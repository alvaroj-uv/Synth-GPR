"""Build a complete gprMax ``.in`` file for an arbitrary N-layer scene.

Consumes a list of :class:`~src.layer_spec.Layer` (bottom -> top) and a
:class:`SceneParams` and emits a valid 2-D gprMax input deck:

  * a self-contained header — provenance (date, git sha, seed), DEFAULTS,
    ``CONFIG_*`` / ``SOURCE_*`` replication keys, and the full TOML config embedded
    verbatim for exact reproduction;
  * parametric ``#domain`` / ``#dx_dy_dz`` / ``#time_window``;
  * one ``#material`` per distinct material;
  * a single monostatic Hertzian-dipole source (co-located TX/RX by default);
  * layer geometry in painter's-algorithm order (air -> strata -> rocks);
  * any passthrough ``raw_commands`` (e.g. ``#geometry_view``, ``#snapshot``).

``packed`` layers are filled with rocks from the existing physics packer, confined
to the layer's y-range, sitting in a contrasting matrix (painter's-algorithm safe).
"""
from __future__ import annotations

import datetime
import math
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Protocol

from .gpr_commands import (
    DomainCommand, DxDyDzCommand, TimeWindowCommand, MaterialCommand,
    BoxCommand, CylinderCommand, WaveformCommand, HertzianDipoleCommand, RxCommand,
)
from .layer_spec import Layer
from .rock_model import PackingBounds
from src.scene_model import SceneModel, LayerSpec

C_LIGHT = 299_792_458.0
_FMAX_FACTOR = 2.5          # ricker fmax ~ 2.5 x centre frequency
_DX_LAMBDA_FRACTION = 10.0  # dx <= lambda_min / 10  (Khosravi Largani 2025)
_DX_ROCK_CAP = 0.005        # m — must resolve smallest stones when packing
_BAR = "## " + "=" * 58


@dataclass
class SceneParams:
    freq_hz: float = 400e6
    domain_x: float = 1.0           # scan width (m)
    dx: Optional[float] = None      # if None, derived from freq + er_max
    antenna_clearance: float = 0.5  # air above the surface for the antenna
    air_buffer: float = 0.1         # extra air above the antenna
    rx_spacing: float = 0.0         # 0 -> monostatic (co-located TX/RX)
    title: str = "N-layer scene"
    time_window: Optional[float] = None  # if None, derived
    seed: Optional[int] = None
    source_waveform: str = "ricker"
    source_amplitude: float = 1.0
    source_polarization: str = "z"
    rock_packing_algorithm: str = "mbubia_ballast"  # packer for packed layers; "mbubia"/"mbubia_ballast" -> pymunk gravity settle


def _git_sha() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], stderr=subprocess.DEVNULL
        ).decode().strip()
    except Exception:
        return "unknown"


def _derive_dx(freq_hz: float, er_max: float, any_packed: bool) -> float:
    lambda_min = C_LIGHT / (_FMAX_FACTOR * freq_hz * math.sqrt(er_max))
    dx = lambda_min / _DX_LAMBDA_FRACTION
    if any_packed:
        dx = min(dx, _DX_ROCK_CAP)
    return max(math.floor(dx / 5e-4) * 5e-4, 5e-4)


def _unique_materials(layers: List[Layer]) -> tuple[list[MaterialCommand], dict]:
    """Collect distinct (eps, sigma) materials; free_space is built-in (skipped)."""
    cmds: list[MaterialCommand] = []
    by_id: dict[str, tuple[float, float]] = {}

    def add(base_id: str, eps: float, sigma: float) -> str:
        if base_id in ("free_space", "air"):
            return "free_space"
        ident = base_id
        n = 2
        while ident in by_id and abs(by_id[ident][0] - eps) > 1e-9:
            ident = f"{base_id}_{n}"
            n += 1
        if ident not in by_id:
            by_id[ident] = (eps, sigma)
            cmds.append(MaterialCommand(eps=eps, sigma=sigma, mu=1.0, mag_loss=0.0, identifier=ident))
        return ident

    id_map: dict = {}
    for i, ly in enumerate(layers):
        if ly.packed:
            id_map[(i, "matrix")] = add(ly.matrix_name, ly.eps, ly.sigma)
            id_map[(i, "rock")] = add(ly.rock_name, ly.rock_eps, ly.rock_sigma)
        else:
            id_map[(i, "box")] = add(ly.name, ly.eps, ly.sigma)
    return cmds, id_map


class PackerProtocol(Protocol):
    """Minimal packer protocol expected by the builder.

    Implementations must provide generate_rocks(bounds, random_seed=None) -> iterable
    of rock-like objects with attributes: x, y, radius, is_polygon, vertices.
    """


def get_default_packer():
    """Lazily import and instantiate the existing MbubiaPymunkSceneGenerator.

    Keeps the heavy dependency (pymunk/pygame) out of the import path until
    actually needed; callers can inject a test/deterministic packer for unit tests.
    """
    try:
        from .pymunk_packing import MbubiaPymunkSceneGenerator
        return MbubiaPymunkSceneGenerator(scene_name="layer_pack", upper_material="clean_ballast", verbose=False)
    except Exception:
        return None


def get_packer(algo: Optional[str]):
    """Resolve a packing-algorithm name to a packer instance.

    Mirrors the dispatch in warehouses.ToolWarehouse so the ``--layers-file``
    pipeline honours ``[sim] rock_packing_algorithm`` exactly like the batch
    pipeline. ``None``/``"mbubia"``/``"mbubia_ballast"`` -> pymunk gravity
    settle (the historical default). Unknown names fall back to the default.
    """
    algo = (algo or "mbubia_ballast").lower()
    if algo in ("mbubia", "mbubia_ballast", "pymunk", "default"):
        return get_default_packer()
    try:
        from . import rock_packing as rp
        _registry = {
            "rsa": rp.RSAPacking,
            "shang_chu": rp.ShangChuPacking,
            "hybris_shang": rp.HybridShangPacking,
            "front_chain": rp.FrontChainPacking,
            "physics": rp.PhysicsPacking,
            "triangle": rp.TrianglePacking,
            "circlify": rp.CirclifyPacking,
            "growth": rp.GrowthPacking,
            "poisson": rp.PoissonDiskPacking,
            "random": rp.RandomPacking,
            "wang": rp.WangTileRockPacking,
            "grid": rp.GridPacking,
        }
        cls = _registry.get(algo)
        if cls is None:
            print(f"[WARN] Unknown rock_packing_algorithm '{algo}'; using default pymunk packer")
            return get_default_packer()
        return cls()
    except Exception as e:
        print(f"[WARN] Could not build packer '{algo}' ({e}); using default pymunk packer")
        return get_default_packer()


def _call_generate_rocks(packer, bounds, seed):
    """Call a packer's generate_rocks, adapting to the two interface families.

    The pymunk packer accepts ``random_seed=`` and self-seeds deterministically.
    The RockPackingStrategy family seeds via the global RNG and requires
    radius_min/radius_max; we seed it explicitly and polygonise the circles so
    the builder draws angular #triangle stones (comparable to the pymunk path).
    """
    import inspect
    sig = inspect.signature(packer.generate_rocks)
    if "random_seed" in sig.parameters:
        return packer.generate_rocks(bounds, random_seed=seed)
    # Strategy family: seed global RNG so the packing is reproducible.
    import random as _random
    if seed is not None:
        _random.seed(seed)
        try:
            import numpy as _np
            _np.random.seed(seed)
        except Exception:
            pass
    rocks = packer.generate_rocks(
        bounds,
        radius_min=0.004,        # 8 mm min stone diameter
        radius_max=0.025,        # 50 mm max stone diameter
        target_fill_ratio=0.85,
    )
    # Give them angular shapes so they read like ballast (not bare circles).
    try:
        import numpy as _np
        rng = _np.random.default_rng(seed)
        packer.polygonize(rocks, rng=rng)
    except Exception:
        pass
    return rocks


def _pack_layer_rocks(y0: float, y1: float, domain_x: float, dz: float,
                      rock_id: str, seed: Optional[int] = None, packer: Optional[PackerProtocol] = None) -> tuple[int, list[str]]:
    """Fill [y0, y1] x [0, domain_x] with gravity-settled rocks using an injected packer.

    If no packer provided, a default packer will be lazily created. This avoids
    importing heavy dependencies at module import time and enables test stubs to be
    injected.
    """
    from .gpr_commands import TriangleCommand
    if packer is None:
        packer = get_default_packer()
    if packer is None:
        # No packer available → no rocks
        return {"n": 0, "r_min": 0.0, "r_max": 0.0, "r_mean": 0.0}, []
    bounds = PackingBounds(x_min=0.0, x_max=domain_x, y_min=y0, y_max=y1)
    cmds: list[str] = []
    radii: list[float] = []
    for r in _call_generate_rocks(packer, bounds, seed):
        if r.radius <= 0:
            continue
        if r.is_polygon and len(r.vertices) >= 3:
            verts = [(min(max(vx, 0.0), domain_x), min(max(vy, y0), y1)) for vx, vy in r.vertices]
            n = len(verts)
            cx = sum(v[0] for v in verts) / n
            cy = sum(v[1] for v in verts) / n
            for i in range(n):
                v1, v2 = verts[i], verts[(i + 1) % n]
                cmds.append(TriangleCommand(cx, cy, 0.0, v1[0], v1[1], 0.0,
                                            v2[0], v2[1], 0.0, dz, rock_id).get_cmd_string())
            radii.append(r.radius)
        else:
            if r.y - r.radius < y0 - 1e-6 or r.y + r.radius > y1 + 1e-6:
                continue
            cmds.append(CylinderCommand(r.x, r.y, 0.0, r.x, r.y, dz, r.radius, rock_id).get_cmd_string())
            radii.append(r.radius)

    stats = {
        "n": len(radii),
        "r_min": min(radii) if radii else 0.0,
        "r_max": max(radii) if radii else 0.0,
        "r_mean": (sum(radii) / len(radii)) if radii else 0.0,
    }
    return stats, cmds


def _run_lab_worker(y0_ballast: float, y1_ballast: float, domain_x: float, domain_y: float,
                     rock_positions: list, geometry_cmds: list) -> dict:
    """Run LabWorker virtual lab test on the scene geometry; return computed lab results.

    Returns dict with FI, FH, qs_mean, etc. for embedding in .in header.
    """
    try:
        from dataclasses import dataclass

        @dataclass
        class MinimalCheckpoint:
            """Minimal checkpoint-like object for LabWorker (no pipeline coupling)."""
            coordinate_system: object = None
            work_order: object = None
            metadata: dict = None
            rock_positions: list = None
            geometry: list = None
            config: object = None

            def __post_init__(self):
                if self.metadata is None:
                    self.metadata = {}
                if self.rock_positions is None:
                    self.rock_positions = []
                if self.geometry is None:
                    self.geometry = []

        @dataclass
        class MinimalConfig:
            domain_x: float = 1.0
            domain_y: float = 1.0
            fouling_psd_type: str = "standard"

        scene = MinimalCheckpoint(
            metadata={'ballast_bottom_y': y0_ballast, 'ballast_top_y': y1_ballast},
            rock_positions=rock_positions,
            geometry=geometry_cmds,
            config=MinimalConfig(domain_x=domain_x, domain_y=domain_y),
        )

        from .lab_worker import LabWorker
        lab = LabWorker()
        lab.execute(scene, keeper=None)  # LabWorker reads only the checkpoint

        # Extract compact results for header
        results = {}
        if 'Lab_FI' in scene.metadata:
            results['FI'] = f"{scene.metadata['Lab_FI']:.1f}"
        if 'Lab_Class' in scene.metadata:
            results['Class'] = scene.metadata['Lab_Class']
        if 'Lab_LDCP_FH' in scene.metadata:
            results['FH'] = f"{scene.metadata['Lab_LDCP_FH']:.1f}%"
        if 'Lab_LDCP_qs_mean' in scene.metadata:
            results['qs_mean'] = f"{scene.metadata['Lab_LDCP_qs_mean']:.1f}"
        if 'Lab_Porosity' in scene.metadata:
            results['porosity'] = f"{scene.metadata['Lab_Porosity']:.3f}"

        return results
    except Exception as e:
        print(f"[WARN] LabWorker failed: {e}")
        return {}


def effective_toml(params: SceneParams, layers: List[Layer]) -> str:
    """Serialize the effective config to TOML (for embedding when run inline)."""
    out = [
        "[sim]",
        f'title = "{params.title}"',
        f"freq_hz = {params.freq_hz:g}",
        f"domain_x = {params.domain_x:g}",
    ]
    if params.dx is not None:
        out.append(f"dx = {params.dx:g}")
    out += [
        f"antenna_clearance = {params.antenna_clearance:g}",
        f"air_buffer = {params.air_buffer:g}",
        f"rx_spacing = {params.rx_spacing:g}",
    ]
    if params.seed is not None:
        out.append(f"seed = {params.seed}")
    out.append(f'rock_packing_algorithm = "{params.rock_packing_algorithm}"')
    for ly in layers:
        out += ["", "[[layer]]", f'name = "{ly.name}"', f"thickness = {ly.thickness:g}"]
        if ly.packed:
            out += ["packed = true", f'matrix = "{ly.matrix_name}"']
        else:
            out += [f"eps = {ly.eps:g}", f"sigma = {ly.sigma:g}"]
    return "\n".join(out)


def _build_header(layers, params, dx, domain_y, subsurface_top, antenna_y,
                  time_window, rock_count, param_sources, scenario=None, computed_lab=None):
    names = ", ".join(f"{ly.name}*" if ly.packed else ly.name for ly in layers)
    mode = "monostatic" if params.rx_spacing == 0 else f"bistatic {params.rx_spacing:g}m"
    seed = params.seed if params.seed is not None else "None"
    ant_label = "TX=RX" if params.rx_spacing == 0 else "TX/RX"

    lines = [
        _BAR,
        "## Generated gprMax Input File (N-layer creator)",
        "## Scenario: Sim",
        f"## Date: {datetime.date.today().isoformat()}",
        f"## Git Version: {_git_sha()}",
        f"## Base Seed: {seed}",
        _BAR,
        "## DEFAULTS",
        f"## Frequency: {params.freq_hz/1e6:.0f} MHz",
        f"## Source: single Hertzian dipole ({mode}), {params.source_waveform}",
        "## Rock geometry: gravity-settled polygons as #triangle fans",
        f"## Layers ({len(layers)}, bottom->top): {names}   (* = packed)",
        f"## Discretisation: dx={dx*1e3:.1f} mm   Domain: {params.domain_x:g} x {domain_y:.3f} m",
        _BAR,
        "## GEOMETRY (per-section stats annotated inline in the deck below)",
        f"## Time window: {time_window:g} s",
        f"## Antenna ({ant_label}): x={params.domain_x/2:g} y={antenna_y:.3f} z={dx/2:g} m",
        f"## Subsurface top: {subsurface_top:.3f} m    Total rocks: {rock_count}",
        _BAR,
    ]
    lines.append(_BAR)

    # Add antenna position to GEOMETRY section
    lines += [f"## Antenna position: y={antenna_y:.3f} m (above surface at {subsurface_top:.3f} m)"]

    # Add ballast layer bounds for visualization
    y_bottom = 0.0
    for ly in layers:
        if ly.packed:
            y_top = y_bottom + ly.thickness
            lines += [f"## Ballast layer: y=[{y_bottom:.3f}, {y_top:.3f}] m  (packed rocks)"]
            break
        y_bottom += ly.thickness

    if scenario:
        lines += ["", "==== SCENARIO (target) ===="]
        for k, v in scenario.items():
            lines.append(f"## {k}: {v}")

    if computed_lab:
        lines += ["", "==== COMPUTED LAB ===="]
        for k, v in computed_lab.items():
            lines.append(f"## {k}: {v}")

    return lines


def build_scene_commands(layers: List[Layer], params: SceneParams,
                         raw_commands: Optional[List[str]] = None,
                         param_sources: Optional[dict] = None,
                         scenario: Optional[dict] = None,
                         computed_lab: Optional[dict] = None,
                         packer: Optional[PackerProtocol] = None,
                         filename: Optional[str] = None) -> List[str]:
    """Build the header + sectioned deck (each section annotated with stats)."""
    raw_commands = raw_commands or []
    param_sources = param_sources or {}

    # Resolve the packer from the configured algorithm unless one was injected
    # (tests inject a deterministic stub). This is what makes
    # [sim] rock_packing_algorithm actually select the packing strategy.
    if packer is None and any(ly.packed for ly in layers):
        packer = get_packer(getattr(params, "rock_packing_algorithm", None))
        print(f"[PACKER] rock_packing_algorithm = "
              f"{getattr(params, 'rock_packing_algorithm', 'mbubia_ballast')} "
              f"-> {type(packer).__name__ if packer else 'None'}")

    er_max = max(max(ly.eps, ly.rock_eps or 0.0) for ly in layers)
    any_packed = any(ly.packed for ly in layers)
    dx = params.dx if params.dx is not None else _derive_dx(params.freq_hz, er_max, any_packed)
    dz = dx

    subsurface_top = sum(ly.thickness for ly in layers)
    domain_y = subsurface_top + params.antenna_clearance + params.air_buffer
    antenna_y = subsurface_top + params.antenna_clearance * 0.5
    tx_x = params.domain_x / 2.0
    rx_x = tx_x + params.rx_spacing

    # Literature guideline check (Khosravi Largani et al. 2025): warn, don't
    # block — small domains are sometimes a deliberate speed/accuracy trade.
    from .physics import check_fdtd_guidelines
    for warning in check_fdtd_guidelines(
        params.freq_hz,
        domain_x=params.domain_x,
        antenna_height=antenna_y - subsurface_top,
        er_max=er_max,
    ):
        print(f"[GUIDELINE] {warning}")

    if params.time_window is not None:
        time_window = params.time_window
    else:
        v_min = C_LIGHT / math.sqrt(er_max)
        time_window = (2.0 * subsurface_top / v_min) * 1.6 + 3e-9

    mat_cmds, id_map = _unique_materials(layers)

    # --- background boxes (painter order, bottom->top) + packed rock layers ---
    box_lines = [BoxCommand(0.0, 0.0, 0.0, params.domain_x, domain_y, dz, "free_space").get_cmd_string()]
    box_info = [("free_space", 0.0, domain_y, "full domain (air voids)")]
    rock_sections = []  # (name, y0, y1, stats, rock_id, rock_eps, matrix_id, cmds)
    rock_count = 0
    y0 = 0.0
    for i, ly in enumerate(layers):
        y1 = y0 + ly.thickness
        if ly.packed:
            matrix_id = id_map[(i, "matrix")]
            if matrix_id != "free_space":
                box_lines.append(BoxCommand(0.0, y0, 0.0, params.domain_x, y1, dz, matrix_id).get_cmd_string())
                box_info.append((matrix_id, y0, y1, f"matrix for packed '{ly.name}'"))
            rock_id = id_map[(i, "rock")]
            stats, cmds = _pack_layer_rocks(y0, y1, params.domain_x, dz, rock_id, params.seed, packer=packer)
            rock_count += stats["n"]
            rock_sections.append((ly.name, y0, y1, stats, rock_id, ly.rock_eps, matrix_id, cmds))
        else:
            box_id = id_map[(i, "box")]
            box_lines.append(BoxCommand(0.0, y0, 0.0, params.domain_x, y1, dz, box_id).get_cmd_string())
            box_info.append((box_id, y0, y1, f"layer '{ly.name}'"))
        y0 = y1

    # Run LabWorker virtual lab test on the packed ballast layer (if any)
    if not computed_lab and any(ly.packed for ly in layers):
        # Collect rock positions from packed layers
        rock_positions = []
        for i, ly in enumerate(layers):
            if ly.packed:
                y0_ballast = sum(layers[j].thickness for j in range(i))
                y1_ballast = y0_ballast + ly.thickness
                # Use the resolved/injected packer to reconstruct rock positions for LabWorker
                packer_to_use = packer or get_packer(getattr(params, "rock_packing_algorithm", None))
                if packer_to_use is not None:
                    from .rock_model import PackingBounds
                    bounds = PackingBounds(x_min=0.0, x_max=params.domain_x, y_min=y0_ballast, y_max=y1_ballast)
                    rock_positions = _call_generate_rocks(packer_to_use, bounds, params.seed)
                break  # Only test first packed layer

        if rock_positions:
            # Collect geometry for LabWorker
            geom_cmds = box_lines  # Background boxes
            computed_lab = _run_lab_worker(y0_ballast, y1_ballast, params.domain_x, domain_y, rock_positions, geom_cmds)

    header = _build_header(layers, params, dx, domain_y, subsurface_top, antenna_y,
                           time_window, rock_count, param_sources, scenario=scenario, computed_lab=computed_lab)

    out: list[str] = list(header)
    out += ["",
            "## === DOMAIN & TIME WINDOW ===",
            f"##   domain: x={params.domain_x:g} m (scan width)  y={domain_y:.3f} m (air+subsurface)  z={dz:g} m (2-D, extruded)",
            f"##   discretization: dx=dy={dx*1e3:.1f} mm  dz={dz*1e3:.1f} mm",
            f"##   time_window: {time_window:g} s ({time_window*1e9:.1f} ns)  for {subsurface_top:.3f} m subsurface depth",
            DomainCommand(params.domain_x, domain_y, dz).get_cmd_string(),
            DxDyDzCommand(dx, dx, dz).get_cmd_string(),
            TimeWindowCommand(time_window).get_cmd_string()]

    # --- MATERIALS section ---
    out += ["", f"## === MATERIALS ({len(mat_cmds)}) ==="]
    for m in mat_cmds:
        out.append(f"##   {m.identifier:18s} eps={m.eps:g}  sigma={m.sigma:g} S/m")
    out += [m.get_cmd_string() for m in mat_cmds]

    # --- SOURCE section ---
    wave_id = "the_wave"
    out += ["", "## === SOURCE (single monostatic Hertzian dipole) ===",
            WaveformCommand(params.source_waveform, params.source_amplitude, params.freq_hz, wave_id).get_cmd_string(),
            HertzianDipoleCommand(params.source_polarization, tx_x, antenna_y, dz / 2.0, wave_id).get_cmd_string(),
            RxCommand(rx_x, antenna_y, dz / 2.0).get_cmd_string()]

    # --- BACKGROUND BOXES section ---
    out += ["", f"## === BACKGROUND BOXES ({len(box_lines)}, painter order bottom->top) ==="]
    for bid, by0, by1, descr in box_info:
        out.append(f"##   {bid:18s} y=[{by0:.3f}, {by1:.3f}] m  ({by1-by0:.3f} m thick)  {descr}")
    out += box_lines

    # --- one section per packed ROCK LAYER (drawn last → rocks contrast over matrix) ---
    for name, ly0, ly1, stats, rock_id, rock_eps, matrix_id, cmds in rock_sections:
        out += ["",
                f"## === ROCK LAYER: {name} (mbubia gravity-settled, #triangle) ===",
                f"##   height: {ly1-ly0:.3f} m    y=[{ly0:.3f}, {ly1:.3f}] m",
                f"##   rocks: {stats['n']}    radius approx: "
                f"min={stats['r_min']*1e3:.1f} mm  max={stats['r_max']*1e3:.1f} mm  mean={stats['r_mean']*1e3:.1f} mm",
                f"##   rock material: {rock_id} (eps={rock_eps:g})    matrix: {matrix_id}",
                f"##   #triangle commands: {len(cmds)}"]
        out += cmds

    # Add #title, #messages, #geometry_view (standard gprMax metadata)
    out += [""]
    if filename:
        out.append(f"#title: {filename}")
    out.append("#messages: n")

    # Add default #geometry_view (commented by default for visualization) if not in raw_commands
    has_geometry_view = any("geometry_view" in (c or "") for c in (raw_commands or []))
    if not has_geometry_view:
        out.append(f"##geometry_view: 0 0 0 {params.domain_x:g} {domain_y:.3f} {dz:g} {dx*1e3:.0f} {dx*1e3:.0f} {dz*1e3:.0f} y n")

    if raw_commands:
        out += ["", "## === PASSTHROUGH COMMANDS ([[command]]) ==="]
        out += raw_commands
    return out


def write_scene(layers: List[Layer], params: SceneParams, out_path: Path,
                raw_commands: Optional[List[str]] = None,
                param_sources: Optional[dict] = None,
                scenario: Optional[dict] = None,
                computed_lab: Optional[dict] = None) -> Path:
    """Build the scene and write it to ``out_path`` (.in)."""
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    filename = out_path.name
    lines = build_scene_commands(layers, params, raw_commands=raw_commands,
                                 param_sources=param_sources, scenario=scenario, computed_lab=computed_lab,
                                 filename=filename)
    out_path.write_text("\n".join(lines) + "\n")
    return out_path


def build_scene_from_model(scene: SceneModel, **kwargs) -> Dict[str, Any]:
    """Build a scene from a SceneModel instance and return a pure-data representation.

    Returns a dict with keys:
      - geometry: list of layer dicts (bottom->top) with name, thickness, permittivity, conductivity
      - targets: list of target descriptors (copied from SceneModel.targets)
      - metadata: scene.metadata

    This function is a thin adapter that can delegate to existing builder internals
    if available; otherwise it returns a conservative representation useful for
    exporters and unit tests.
    """
    # Conservative representation
    geometry = []
    for lyr in scene.layers:
        geometry.append({
            "name": lyr.name,
            "thickness": float(lyr.thickness),
            "permittivity": float(lyr.permittivity),
            "conductivity": float(getattr(lyr, "conductivity", 0.0)),
            "extra": dict(getattr(lyr, "extra", {})),
        })

    targets = [dict(t) for t in getattr(scene, "targets", [])]

    out = {
        "geometry": geometry,
        "targets": targets,
        "metadata": dict(getattr(scene, "metadata", {})),
    }

    # If this module has a richer builder function, attempt to use it for more
    # detailed geometry (silently fall back if not present).
    try:
        # existing function that builds internal scene representation
        detailed = build_scene_from_layers(geometry, targets, **kwargs)  # type: ignore
        # If successful, return the detailed representation
        return detailed
    except Exception:
        return out


def adapt_and_write_scene(scene: SceneModel, writer, output_path: str, **kwargs) -> str:
    """Adapter that accepts a SceneModel and uses an existing writer object
    (e.g. GPRMaxFileWriter) to serialize the scene.

    This function keeps the file-writing responsibility outside the core
    builder; it simply prepares the pure-data scene and calls the provided
    writer.save_scene_checkpoint-like interface.
    """
    pure = build_scene_from_model(scene, **kwargs)

    # The expected interface on writer is save_scene_checkpoint(checkpoint, ...)
    # If the writer expects a 'checkpoint' object, we try to satisfy it by
    # passing the pure-data dict. Callers can adapt as needed.
    try:
        written = writer.save_scene_checkpoint(pure, output_path, **kwargs)
        return written
    except Exception:
        # Fallback: if writer has a plain 'write' or 'export' method
        if hasattr(writer, "export"):
            writer.export(pure, output_path)
            return output_path
        elif hasattr(writer, "write"):
            writer.write(pure, output_path)
            return output_path
        else:
            raise

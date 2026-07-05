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

import numpy as np

from .gpr_commands import (
    DomainCommand, DxDyDzCommand, TimeWindowCommand, MaterialCommand,
    BoxCommand, CylinderCommand, WaveformCommand, HertzianDipoleCommand, RxCommand,
)
from .layer_spec import Layer
from .rock_model import PackingBounds, rip_polygon_vertices
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
    rx_spacing: float = 0.0         # DEPRECATED: use antenna_mode + receiver_spacing
    antenna_mode: str = "monostatic"  # "monostatic" (TX=RX) or "bistatic" (separate TX/RX)
    num_receivers: int = 1          # number of receivers (1=single, >1=array)
    receiver_spacing: float = 0.05  # spacing between TX/RX in bistatic, or spacing between RX in array
    title: str = "N-layer scene"
    time_window: Optional[float] = None  # if None, derived
    seed: Optional[int] = None
    source_waveform: str = "ricker"
    source_amplitude: float = 1.0
    source_polarization: str = "z"
    rock_packing_algorithm: str = "pymunk_ballast"  # packer for packed layers; "pymunk"/"pymunk_ballast" -> pymunk gravity settle
    pymunk_settle_time: Optional[float] = None  # pymunk gravity-settle seconds; None -> packer default (2.0, phi~0.12). ~0.1 -> phi~0.40
    rock_radius_min: Optional[float] = None  # min rock radius (m) for strategy-family packers; None -> 0.004 m (8 mm dia)
    rock_radius_max: Optional[float] = None  # max rock radius (m) for strategy-family packers; None -> 0.025 m (50 mm dia)
    rock_packing_target_fill: Optional[float] = None  # target area fraction covered by rocks (None -> 0.85 hardcoded default); 0.60 -> phi~0.40 per Brancadoro 2D rule
    excitation_file: Optional[str] = None  # path to gprMax #excitation_file; if set, skips #waveform command
    excitation_waveform_id: str = "gssi_420mhz"  # waveform column ID in excitation_file


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

    Implementations expose the UNIFIED entry point
    ``pack(bounds, radius_min, radius_max, target_fill_ratio, *, seed=None)
    -> List[Rock]`` (provided by RockPackingStrategy.pack for every strategy;
    overridden by the pymunk generator). Rocks have x, y, radius, is_polygon,
    vertices. Per-strategy placement still lives in each ``generate_rocks``.
    """


def get_default_packer(settle_time: Optional[float] = None):
    """Lazily import and instantiate the existing MbubiaPymunkSceneGenerator.

    Keeps the heavy dependency (pymunk/pygame) out of the import path until
    actually needed; callers can inject a test/deterministic packer for unit tests.
    ``settle_time`` (s) overrides the gravity-settle duration: None -> packer
    default (2.0, phi~0.12); ~0.1 -> looser phi~0.40.
    """
    try:
        from .pymunk_packing import MbubiaPymunkSceneGenerator
        kw = {} if settle_time is None else {"settle_time": float(settle_time)}
        return MbubiaPymunkSceneGenerator(scene_name="layer_pack", upper_material="clean_ballast", verbose=False, **kw)
    except Exception:
        return None


def get_packer(algo: Optional[str], settle_time: Optional[float] = None):
    """Resolve a packing-algorithm name to a packer instance.

    Mirrors the dispatch in warehouses.ToolWarehouse so the ``--layers-file``
    pipeline honours ``[sim] rock_packing_algorithm`` exactly like the batch
    pipeline. ``None``/``"pymunk"``/``"pymunk_ballast"`` -> pymunk gravity
    settle (the default). ``"mbubia"``/``"mbubia_ballast"`` are kept as
    backward-compatible aliases. Unknown names fall back to the default.
    ``settle_time`` only affects the pymunk packer.
    """
    algo = (algo or "pymunk_ballast").lower()
    if algo in ("pymunk", "pymunk_ballast", "mbubia", "mbubia_ballast", "default"):
        return get_default_packer(settle_time)
    try:
        from . import rock_packing as rp
        if algo == "rip":
            from .rip_packing import RIPPacking
            return RIPPacking()
        if algo == "rcp":
            from .rcp_packing import RCPPacking
            return RCPPacking()
        if algo in ("rcpgen", "rcpgenerator"):
            from .rcpgenerator_packing import RCPGeneratorPacking
            return RCPGeneratorPacking()
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
            return get_default_packer(settle_time)
        return cls()
    except Exception as e:
        print(f"[WARN] Could not build packer '{algo}' ({e}); using default pymunk packer")
        return get_default_packer(settle_time)


def _call_generate_rocks(packer, bounds, seed,
                         radius_min: Optional[float] = None,
                         radius_max: Optional[float] = None,
                         target_fill_ratio: Optional[float] = None):
    """Pack rocks via the unified ``pack()`` entry point shared by every packer.

    Every packer (RockPackingStrategy subclasses, RIP, pymunk) exposes the same
    ``pack(bounds, radius_min, radius_max, target_fill_ratio, *, seed)`` — it
    seeds the RNGs, delegates to that packer's ``generate_rocks``, and
    polygonises bare circles. No more signature sniffing.
    Defaults: 8 mm min / 50 mm max stone diameter, 0.85 area fill.
    """
    return packer.pack(
        bounds,
        radius_min if radius_min is not None else 0.004,
        radius_max if radius_max is not None else 0.025,
        target_fill_ratio if target_fill_ratio is not None else 0.85,
        seed=seed,
    )


def _pack_layer_rocks(y0: float, y1: float, domain_x: float, dz: float,
                      rock_id: str, seed: Optional[int] = None, packer: Optional[PackerProtocol] = None,
                      radius_min: Optional[float] = None, radius_max: Optional[float] = None,
                      target_fill_ratio: Optional[float] = None,
                      matrix_id: Optional[str] = None,
                      invisible_fraction: float = 0.0,
                      rock_shape: str = "polygon") -> tuple[int, list[str]]:
    """Fill [y0, y1] x [0, domain_x] with gravity-settled rocks using an injected packer.

    If no packer provided, a default packer will be lazily created. This avoids
    importing heavy dependencies at module import time and enables test stubs to be
    injected.

    ``invisible_fraction`` (0-1): each rock independently has this probability
    of being stamped with ``matrix_id`` instead of ``rock_id`` -- geometrically
    present (still counted in the physical/porosity packing) but EM-inert
    (zero dielectric contrast with its surrounding matrix). Deterministic for
    a given ``seed`` (uses a RNG stream separate from the packer's own).

    ``rock_shape``: "polygon" (default -- packer's angular triangulated
    output, kept as-is), "circle" (strips the packer's polygon vertices so
    each rock emits as a single #cylinder -- same centre/radius, round
    cross-section instead of angular facets), or "square" (replaces the
    vertices with a 4-corner square inscribed in the packer's original
    bounding circle -- same centre/radius as the other two shapes).
    """
    from .gpr_commands import TriangleCommand
    if packer is None:
        packer = get_default_packer()
    if packer is None:
        # No packer available → no rocks
        return {"n": 0, "r_min": 0.0, "r_max": 0.0, "r_mean": 0.0, "n_invisible": 0}, []
    bounds = PackingBounds(x_min=0.0, x_max=domain_x, y_min=y0, y_max=y1)
    cmds: list[str] = []
    radii: list[float] = []
    n_invisible = 0
    vis_rng = np.random.default_rng(seed if seed is not None else 0)
    # Separate RNG stream (decorrelated from vis_rng) for RIP polygon shape
    # generation, so toggling rock_invisible_fraction doesn't change rock shapes.
    shape_rng = np.random.default_rng((seed if seed is not None else 0) + 1_000_003)
    for r in _call_generate_rocks(packer, bounds, seed, radius_min=radius_min, radius_max=radius_max,
                                   target_fill_ratio=target_fill_ratio):
        if r.radius <= 0:
            continue
        if rock_shape == "circle" and r.vertices is not None:
            r.vertices = None
        elif rock_shape == "square":
            r.vertices = [
                (r.x + r.radius * math.cos(math.pi / 4 + k * math.pi / 2),
                 r.y + r.radius * math.sin(math.pi / 4 + k * math.pi / 2))
                for k in range(4)
            ]
        elif rock_shape == "rip":
            r.vertices = rip_polygon_vertices(r.x, r.y, r.radius, shape_rng)
        is_invisible = (invisible_fraction > 0.0 and matrix_id is not None
                        and vis_rng.random() < invisible_fraction)
        mat_id = matrix_id if is_invisible else rock_id
        if is_invisible:
            n_invisible += 1
        if r.is_polygon and len(r.vertices) >= 3:
            verts = [(min(max(vx, 0.0), domain_x), min(max(vy, y0), y1)) for vx, vy in r.vertices]
            n = len(verts)
            cx = sum(v[0] for v in verts) / n
            cy = sum(v[1] for v in verts) / n
            for i in range(n):
                v1, v2 = verts[i], verts[(i + 1) % n]
                cmds.append(TriangleCommand(cx, cy, 0.0, v1[0], v1[1], 0.0,
                                            v2[0], v2[1], 0.0, dz, mat_id).get_cmd_string())
            radii.append(r.radius)
        else:
            if r.y - r.radius < y0 - 1e-6 or r.y + r.radius > y1 + 1e-6:
                continue
            cmds.append(CylinderCommand(r.x, r.y, 0.0, r.x, r.y, dz, r.radius, mat_id).get_cmd_string())
            radii.append(r.radius)

    stats = {
        "n": len(radii),
        "r_min": min(radii) if radii else 0.0,
        "r_max": max(radii) if radii else 0.0,
        "r_mean": (sum(radii) / len(radii)) if radii else 0.0,
        "n_invisible": n_invisible,
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

        # Full LabWorker metadata for the dataset-format header. Drop the two
        # bookkeeping inputs we seeded; expose FI_class (= measured Lab_Class) so
        # the .in carries the same label key the training pipeline reads.
        full = {k: v for k, v in scene.metadata.items()
                if k not in ("ballast_bottom_y", "ballast_top_y")}
        if 'Lab_Class' in scene.metadata and 'FI_class' not in full:
            full['FI_class'] = scene.metadata['Lab_Class']
        results['_full'] = full
        return results
    except Exception as e:
        print(f"[WARN] LabWorker failed: {e}")
        return {}


def _geometry_fouling_label(layers: List[Layer]) -> dict:
    """Authoritative fouling label derived from the packed-layer stack geometry.

    ``%FH = H_FB / H_BT`` (fouled ballast height / total ballast height) — the
    SAME definition the real pandoscope labels use (Rojas-Vivanco 2025, eq. 8).
    A packed ballast sublayer counts as fouled when its inter-rock matrix is a
    fouling material (i.e. not air/free_space). FI is taken from the medium
    compaction curve so synthetic labels stay definition-consistent with the
    real data (labelled with ``FI_T_Medium`` regardless of packing density;
    the 2-D packer's geometric porosity is an artefact, not the field state).

    Needed because LabWorker's single-column virtual LDCP cannot see the
    fouled/clean *height* split in a two-sublayer scene — it reports FH=0%.

    Returns {} when there is no packed ballast layer.
    """
    packed = [ly for ly in layers if ly.packed]
    if not packed:
        return {}
    total = sum(ly.thickness for ly in packed)
    fouled = sum(ly.thickness for ly in packed
                 if ly.matrix_name not in ("free_space", "air"))
    fh_pct = 100.0 * fouled / total if total > 0 else 0.0
    from .physics import fi_from_fouling_height, classify_fouling_index
    fi = fi_from_fouling_height(fh_pct)          # porosity=None -> medium curve
    return {"FH_pct": fh_pct, "FI": fi, "Class": classify_fouling_index(fi)}


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
    mode = "monostatic" if params.antenna_mode == "monostatic" else f"bistatic {params.receiver_spacing:g}m"
    seed = params.seed if params.seed is not None else "None"
    ant_label = "TX=RX" if params.antenna_mode == "monostatic" else "TX/RX"

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
        f"## Layers ({len(layers)}, bottom->top internally): {names}   (* = packed)",
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

    # Add ballast layer bounds for visualization (full packed stack, internal bottom->top)
    packed_spans = [
        (sum(layers[j].thickness for j in range(i)),
         sum(layers[j].thickness for j in range(i)) + ly.thickness)
        for i, ly in enumerate(layers) if ly.packed
    ]
    if packed_spans:
        lines += [f"## Ballast layer: y=[{packed_spans[0][0]:.3f}, "
                  f"{packed_spans[-1][1]:.3f}] m  (packed rocks)"]

    if scenario:
        lines += ["", "==== SCENARIO (target) ===="]
        for k, v in scenario.items():
            lines.append(f"## {k}: {v}")

    if computed_lab:
        full = computed_lab.get("_full") if isinstance(computed_lab, dict) else None
        lines += ["", "==== COMPUTED LAB ===="]
        for k, v in computed_lab.items():
            if k == "_full":
                continue
            lines.append(f"## {k}: {v}")
        # Full dataset-format label set — same keys (FI_class, Lab_FI, Lab_P4,
        # Lab_P200, Lab_PSD, mc_*, ...) the training/feature pipeline reads from
        # the canonical GPRMaxFileWriter header.
        if full:
            lines += ["", "==== DATASET LABELS (LabWorker) ===="]
            for k, v in full.items():
                lines.append(f"## {k}: {v}")

    # CONFIG_* replication block (mirrors the canonical dataset header keys).
    lines += ["", "==== CONFIG (replication) ===="]
    lines.append(f"## CONFIG_center_freq_hz: {params.freq_hz:g}")
    lines.append(f"## CONFIG_rock_packing_algorithm: {params.rock_packing_algorithm}")
    if params.seed is not None:
        lines.append(f"## CONFIG_base_seed: {params.seed}")
    lines.append(f"## CONFIG_domain_x: {params.domain_x:g}")
    # Per-layer packing overrides (when any packed layer pins its own algorithm).
    per_layer_algos = {ly.name: ly.rock_packing_algorithm
                       for ly in layers if ly.packed and ly.rock_packing_algorithm}
    for nm, algo in per_layer_algos.items():
        lines.append(f"## CONFIG_layer_packing[{nm}]: {algo}")

    return lines


def _print_cross_section(layers: List[Layer], params: SceneParams,
                         subsurface_top: float, antenna_y: float) -> None:
    """Print a visual cross-section of the layer stack to stdout.

    Layers are shown top-to-bottom (as the radar sees them), with y coordinates
    on the left so the user can immediately verify TOML ordering is correct.
    """
    W = 36  # box width in characters
    border = "+" + "-" * W + "+"

    def row(label: str, detail: str = "") -> str:
        content = f"  {label}"
        if detail:
            content += f"  ({detail})"
        return f"|{content:<{W}}|"

    # Ground surface = top of the deepest non-air layer counting from the top.
    # Users sometimes include an explicit air [[layer]] at the top of their stack;
    # the "<-- ground surface" label belongs at the air/ground interface, not at
    # the top of the entire layer stack.
    ground_surface_y = subsurface_top
    for ly in reversed(layers):
        if ly.eps == 1.0 and ly.sigma == 0.0 and not ly.packed:
            ground_surface_y -= ly.thickness
        else:
            break

    print()
    print("  Layer cross-section (antenna at top, y=0 at bottom of domain)")
    print()
    print(f"  y={antenna_y:.3f} m  {border}")
    print(f"           {row('antenna', params.source_waveform + ' ' + params.antenna_mode)}")
    top_suffix = "  <-- ground surface" if abs(ground_surface_y - subsurface_top) < 1e-9 else ""
    print(f"  y={subsurface_top:.3f} m  {border}{top_suffix}")

    y_top = subsurface_top
    for ly in reversed(layers):
        y_bot = y_top - ly.thickness
        if ly.packed:
            detail = f"eps={ly.rock_eps} in {ly.matrix_name}, PACKED"
        else:
            detail = f"eps={ly.eps}, sigma={ly.sigma}"
        print(f"           {row(ly.name, detail)}")
        bot_suffix = "  <-- ground surface" if abs(y_bot - ground_surface_y) < 1e-9 and y_bot < subsurface_top else ""
        print(f"  y={y_bot:.3f} m  {border}{bot_suffix}")
        y_top = y_bot

    print()


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

    # Per-layer packer selection. The scene-level [sim] rock_packing_algorithm /
    # pymunk_settle_time are the DEFAULTs; a packed layer's own
    # rock_packing_algorithm / pymunk_settle_time override them independently. An
    # injected packer (tests) wins for every layer to keep stubs deterministic.
    # Cache key includes BOTH algo and settle so two layers sharing an algo but
    # different settle times don't collide on the same packer instance.
    _injected = packer is not None
    _scene_algo = getattr(params, "rock_packing_algorithm", None) or "pymunk_ballast"
    _scene_settle = getattr(params, "pymunk_settle_time", None) or getattr(params, "mbubia_settle_time", None)
    if not _injected and any(ly.packed for ly in layers):
        print(f"[PACKER] scene default rock_packing_algorithm = {_scene_algo}, "
              f"pymunk_settle_time = {_scene_settle}")

    _packer_cache: dict[tuple, object] = {}

    def _layer_packer(ly: Layer):
        """Packer for one layer: injected (tests) > per-layer algo/settle > scene default."""
        if _injected:
            return packer
        algo = ly.rock_packing_algorithm or _scene_algo
        settle = ly.pymunk_settle_time if ly.pymunk_settle_time is not None else _scene_settle
        key = (algo, settle)
        if key not in _packer_cache:
            p = get_packer(algo, settle)
            _packer_cache[key] = p
            overridden = []
            if ly.rock_packing_algorithm:
                overridden.append(f"algo={algo}")
            if ly.pymunk_settle_time is not None:
                overridden.append(f"settle={settle}")
            if overridden:
                print(f"[PACKER] layer '{ly.name}' override ({', '.join(overridden)}) "
                      f"-> {type(p).__name__ if p else 'None'}")
        return _packer_cache[key]

    def _layer_radius(ly: Layer) -> tuple[Optional[float], Optional[float]]:
        """Rock radius bounds for one layer: per-layer override > scene default."""
        rmin = ly.rock_radius_min if ly.rock_radius_min is not None else params.rock_radius_min
        rmax = ly.rock_radius_max if ly.rock_radius_max is not None else params.rock_radius_max
        if ly.rock_radius_min is not None or ly.rock_radius_max is not None:
            print(f"[PACKER] layer '{ly.name}' rock_radius = [{rmin}, {rmax}] m (per-layer)")
        return rmin, rmax

    def _layer_target_fill(ly: Layer) -> Optional[float]:
        """Target area-fill fraction for one layer: per-layer override > scene default."""
        tf = (ly.rock_packing_target_fill if ly.rock_packing_target_fill is not None
              else getattr(params, "rock_packing_target_fill", None))
        if ly.rock_packing_target_fill is not None:
            print(f"[PACKER] layer '{ly.name}' rock_packing_target_fill = {tf} (per-layer)")
        return tf

    er_max = max(max(ly.eps, ly.rock_eps or 0.0) for ly in layers)
    any_packed = any(ly.packed for ly in layers)
    dx = params.dx if params.dx is not None else _derive_dx(params.freq_hz, er_max, any_packed)
    dz = dx

    subsurface_top = sum(ly.thickness for ly in layers)
    domain_y = subsurface_top + params.antenna_clearance + params.air_buffer
    antenna_y = subsurface_top + params.antenna_clearance * 0.5

    _print_cross_section(layers, params, subsurface_top, antenna_y)

    # Antenna positioning (monostatic vs bistatic)
    tx_x = params.domain_x / 2.0
    if params.antenna_mode == "bistatic":
        # Bistatic: RX offset from TX by receiver_spacing
        rx_x = tx_x + params.receiver_spacing
    else:
        # Monostatic: RX at same position as TX
        rx_x = tx_x

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
            r_min, r_max = _layer_radius(ly)
            inv_frac = ly.rock_invisible_fraction or 0.0
            shape = ly.rock_shape or "polygon"
            stats, cmds = _pack_layer_rocks(y0, y1, params.domain_x, dz, rock_id, params.seed, packer=_layer_packer(ly),
                                             radius_min=r_min, radius_max=r_max,
                                             target_fill_ratio=_layer_target_fill(ly),
                                             matrix_id=matrix_id, invisible_fraction=inv_frac,
                                             rock_shape=shape)
            if inv_frac > 0.0:
                print(f"[PACKER] layer '{ly.name}' rock_invisible_fraction={inv_frac:.2f} "
                      f"-> {stats['n_invisible']}/{stats['n']} rocks stamped with matrix material")
            if shape == "circle":
                print(f"[PACKER] layer '{ly.name}' rock_shape=circle -> {stats['n']} rocks emitted as cylinders")
            rock_count += stats["n"]
            rock_sections.append((ly.name, y0, y1, stats, rock_id, ly.rock_eps, matrix_id, cmds))
        else:
            box_id = id_map[(i, "box")]
            box_lines.append(BoxCommand(0.0, y0, 0.0, params.domain_x, y1, dz, box_id).get_cmd_string())
            box_info.append((box_id, y0, y1, f"layer '{ly.name}'"))
        y0 = y1

    # Run LabWorker virtual lab test over the FULL packed ballast stack (if any).
    # NB: span every packed sublayer (a fouled bottom + clean top are TWO packed
    # layers) so porosity/qs reflect the whole ballast, not just the first layer.
    if not computed_lab and any(ly.packed for ly in layers):
        packed_idx = [i for i, ly in enumerate(layers) if ly.packed]
        y0_ballast = sum(layers[j].thickness for j in range(packed_idx[0]))
        y1_ballast = sum(layers[j].thickness for j in range(packed_idx[-1] + 1))
        rock_positions = []
        for i in packed_idx:
            ly = layers[i]
            packer_to_use = _layer_packer(ly)
            if packer_to_use is not None:
                from .rock_model import PackingBounds
                ly0 = sum(layers[j].thickness for j in range(i))
                ly1 = ly0 + ly.thickness
                bounds = PackingBounds(x_min=0.0, x_max=params.domain_x, y_min=ly0, y_max=ly1)
                r_min, r_max = _layer_radius(ly)
                rock_positions += _call_generate_rocks(packer_to_use, bounds, params.seed,
                                                        radius_min=r_min, radius_max=r_max,
                                                        target_fill_ratio=_layer_target_fill(ly))

        if rock_positions:
            geom_cmds = box_lines  # Background boxes
            computed_lab = _run_lab_worker(y0_ballast, y1_ballast, params.domain_x, domain_y, rock_positions, geom_cmds)

    # Override the fouling label with the geometry-derived truth. LabWorker's
    # single-column LDCP reports FH=0% for two-sublayer scenes; the matrix
    # composition of the packed stack is the authoritative %FH (see
    # _geometry_fouling_label). Keeps LabWorker's porosity/PSD/qs fields intact.
    geo = _geometry_fouling_label(layers)
    if geo:
        if not isinstance(computed_lab, dict):
            computed_lab = {}
        computed_lab["FH"] = f"{geo['FH_pct']:.1f}%"
        computed_lab["FI"] = f"{geo['FI']:.1f}"
        computed_lab["Class"] = geo["Class"]
        full = computed_lab.setdefault("_full", {})
        full["Lab_LDCP_FH"] = round(geo["FH_pct"], 1)
        full["Lab_FI"] = round(geo["FI"], 1)
        full["Lab_Class"] = geo["Class"]
        full["FI_class"] = geo["Class"]

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
    antenna_type = "bistatic" if params.antenna_mode == "bistatic" else "monostatic"
    excit_file = getattr(params, "excitation_file", None)
    if excit_file:
        wf_id = getattr(params, "excitation_waveform_id", "gssi_420mhz")
        out += ["", f"## === SOURCE (single {antenna_type} Hertzian dipole, excitation file) ===",
                f"#excitation_file: {excit_file}",
                HertzianDipoleCommand(params.source_polarization, tx_x, antenna_y, dz / 2.0, wf_id).get_cmd_string()]
    else:
        wave_id = "the_wave"
        out += ["", f"## === SOURCE (single {antenna_type} Hertzian dipole) ===",
                WaveformCommand(params.source_waveform, params.source_amplitude, params.freq_hz, wave_id).get_cmd_string(),
                HertzianDipoleCommand(params.source_polarization, tx_x, antenna_y, dz / 2.0, wave_id).get_cmd_string()]

    # Add receivers (single or array)
    for i in range(params.num_receivers):
        rx_x_i = rx_x + (i * params.receiver_spacing)
        out.append(RxCommand(rx_x_i, antenna_y, dz / 2.0).get_cmd_string())

    # --- BACKGROUND BOXES section ---
    out += ["", f"## === BACKGROUND BOXES ({len(box_lines)}, painter order bottom->top) ==="]
    for bid, by0, by1, descr in box_info:
        out.append(f"##   {bid:18s} y=[{by0:.3f}, {by1:.3f}] m  ({by1-by0:.3f} m thick)  {descr}")
    out += box_lines

    # --- one section per packed ROCK LAYER (drawn last → rocks contrast over matrix) ---
    for name, ly0, ly1, stats, rock_id, rock_eps, matrix_id, cmds in rock_sections:
        out += ["",
                f"## === ROCK LAYER: {name} (pymunk gravity-settled, #triangle) ===",
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
        out.append(f"##geometry_view: 0 0 0 {params.domain_x:g} {domain_y:.3f} {dz:g} {dx:.4f} {dx:.4f} {dz:.4f} geom n")

    if raw_commands:
        out += ["", "## === PASSTHROUGH COMMANDS ([[command]]) ==="]
        out += raw_commands
    return out


def write_scene(layers: List[Layer], params: SceneParams, out_path: Path,
                raw_commands: Optional[List[str]] = None,
                param_sources: Optional[dict] = None,
                scenario: Optional[dict] = None,
                computed_lab: Optional[dict] = None) -> Path:
    """Build the scene and write it to ``out_path`` (.in) using the data access layer."""
    from src.data_access import INFileWriter
    
    out_path = Path(out_path)
    filename = out_path.name
    lines = build_scene_commands(layers, params, raw_commands=raw_commands,
                                 param_sources=param_sources, scenario=scenario, computed_lab=computed_lab,
                                 filename=filename)
    content = "\n".join(lines) + "\n"
    
    # Use INFileWriter to write the file
    writer = INFileWriter()
    return writer.write(out_path, content)


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

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
from typing import List, Optional

from .gpr_commands import (
    DomainCommand, DxDyDzCommand, TimeWindowCommand, MaterialCommand,
    BoxCommand, CylinderCommand, WaveformCommand, HertzianDipoleCommand, RxCommand,
)
from .layer_spec import Layer
from .rock_model import PackingBounds

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


def _pack_layer_rocks(y0: float, y1: float, domain_x: float, dz: float,
                      rock_id: str) -> list[CylinderCommand]:
    """Fill [y0, y1] x [0, domain_x] with rocks from the physics packer."""
    from .pymunk_packing import MbubiaPymunkSceneGenerator
    packer = MbubiaPymunkSceneGenerator(
        scene_name="layer_pack", upper_material="clean_ballast", verbose=False,
    )
    bounds = PackingBounds(x_min=0.0, x_max=domain_x, y_min=y0, y_max=y1)
    cmds: list[CylinderCommand] = []
    for r in packer.generate_rocks(bounds):
        if r.radius <= 0:
            continue
        if r.y - r.radius < y0 - 1e-6 or r.y + r.radius > y1 + 1e-6:
            continue
        cmds.append(CylinderCommand(
            x1=r.x, y1=r.y, z1=0.0, x2=r.x, y2=r.y, z2=dz, radius=r.radius, material=rock_id,
        ))
    return cmds


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
    for ly in layers:
        out += ["", "[[layer]]", f'name = "{ly.name}"', f"thickness = {ly.thickness:g}"]
        if ly.packed:
            out += ["packed = true", f'matrix = "{ly.matrix_name}"']
        else:
            out += [f"eps = {ly.eps:g}", f"sigma = {ly.sigma:g}"]
    return "\n".join(out)


def _build_header(layers: List[Layer], params: SceneParams, dx: float,
                  domain_y: float, param_sources: dict, embed_toml: str) -> list[str]:
    names = ", ".join(f"{ly.name}*" if ly.packed else ly.name for ly in layers)
    mode = "monostatic" if params.rx_spacing == 0 else f"bistatic {params.rx_spacing:g}m"
    seed = params.seed if params.seed is not None else "None"

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
        f"## Layers ({len(layers)}, bottom->top): {names}   (* = packed)",
        f"## Discretisation: dx={dx*1e3:.1f} mm   Domain: {params.domain_x:g} x {domain_y:.3f} m",
        _BAR,
    ]
    cfg = {
        "center_freq_hz": f"{params.freq_hz:g}",
        "domain_x": f"{params.domain_x:g}",
        "dx": f"{dx:g}",
        "antenna_clearance": f"{params.antenna_clearance:g}",
        "air_buffer": f"{params.air_buffer:g}",
        "rx_spacing": f"{params.rx_spacing:g}",
        "num_layers": str(len(layers)),
    }
    for k, v in cfg.items():
        lines.append(f"## CONFIG_{k}: {v}")
        lines.append(f"## SOURCE_{k}: {param_sources.get(k, 'DEFAULT')}")
    lines.append(_BAR)

    if embed_toml:
        lines.append("## --- embedded config (reproducible) ---")
        lines += [f"## {ln}" for ln in embed_toml.splitlines()]
        lines.append(_BAR)
    return lines


def build_scene_commands(layers: List[Layer], params: SceneParams,
                         raw_commands: Optional[List[str]] = None,
                         param_sources: Optional[dict] = None,
                         embed_toml: str = "") -> List[str]:
    """Build the ordered list of rendered gprMax lines (header + deck) for the scene."""
    raw_commands = raw_commands or []
    param_sources = param_sources or {}

    er_max = max(max(ly.eps, ly.rock_eps or 0.0) for ly in layers)
    any_packed = any(ly.packed for ly in layers)
    dx = params.dx if params.dx is not None else _derive_dx(params.freq_hz, er_max, any_packed)
    dz = dx

    subsurface_top = sum(ly.thickness for ly in layers)
    domain_y = subsurface_top + params.antenna_clearance + params.air_buffer
    antenna_y = subsurface_top + params.antenna_clearance * 0.5
    tx_x = params.domain_x / 2.0
    rx_x = tx_x + params.rx_spacing

    if params.time_window is not None:
        time_window = params.time_window
    else:
        v_min = C_LIGHT / math.sqrt(er_max)
        time_window = (2.0 * subsurface_top / v_min) * 1.6 + 3e-9

    if not embed_toml:
        embed_toml = effective_toml(params, layers)
    header = _build_header(layers, params, dx, domain_y, param_sources, embed_toml)

    deck_header = [
        DomainCommand(params.domain_x, domain_y, dz).get_cmd_string(),
        DxDyDzCommand(dx, dx, dz).get_cmd_string(),
        TimeWindowCommand(time_window).get_cmd_string(),
    ]

    mat_cmds, id_map = _unique_materials(layers)
    materials = [m.get_cmd_string() for m in mat_cmds]

    wave_id = "the_wave"
    source = [
        WaveformCommand(params.source_waveform, params.source_amplitude,
                        params.freq_hz, wave_id).get_cmd_string(),
        HertzianDipoleCommand(params.source_polarization, tx_x, antenna_y, dz / 2.0,
                              wave_id).get_cmd_string(),
        RxCommand(rx_x, antenna_y, dz / 2.0).get_cmd_string(),
    ]

    geometry = [BoxCommand(0.0, 0.0, 0.0, params.domain_x, domain_y, dz, "free_space").get_cmd_string()]
    rock_cmds: list[str] = []
    y0 = 0.0
    for i, ly in enumerate(layers):
        y1 = y0 + ly.thickness
        if ly.packed:
            matrix_id = id_map[(i, "matrix")]
            if matrix_id != "free_space":
                geometry.append(BoxCommand(0.0, y0, 0.0, params.domain_x, y1, dz, matrix_id).get_cmd_string())
            rock_id = id_map[(i, "rock")]
            for c in _pack_layer_rocks(y0, y1, params.domain_x, dz, rock_id):
                rock_cmds.append(c.get_cmd_string())
        else:
            geometry.append(BoxCommand(0.0, y0, 0.0, params.domain_x, y1, dz, id_map[(i, "box")]).get_cmd_string())
        y0 = y1

    out = header + [""] + deck_header + [""] + materials + [""] + source + [""] + geometry + rock_cmds
    if raw_commands:
        out += ["", "## --- passthrough commands ([[command]]) ---", *raw_commands]
    return out


def write_scene(layers: List[Layer], params: SceneParams, out_path: Path,
                raw_commands: Optional[List[str]] = None,
                param_sources: Optional[dict] = None,
                embed_toml: str = "") -> Path:
    """Build the scene and write it to ``out_path`` (.in)."""
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    lines = build_scene_commands(layers, params, raw_commands=raw_commands,
                                 param_sources=param_sources, embed_toml=embed_toml)
    out_path.write_text("\n".join(lines) + "\n")
    return out_path

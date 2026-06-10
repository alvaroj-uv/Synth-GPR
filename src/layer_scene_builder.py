"""Build a complete gprMax ``.in`` file for an arbitrary N-layer scene.

Consumes a list of :class:`~src.layer_spec.Layer` (bottom -> top) and emits a valid
2-D gprMax input deck: parametric domain / discretisation / time window, one
``#material`` per distinct material, a monostatic Hertzian-dipole source (single
dipole, co-located TX/RX), and the layer geometry in painter's-algorithm order
(air -> strata bottom->top -> rocks). ``packed`` layers are filled with rocks from
the existing physics packer, confined to the layer's y-range.
"""
from __future__ import annotations

import math
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


@dataclass
class SceneParams:
    freq_hz: float = 400e6
    domain_x: float = 1.0          # scan width (m)
    dx: Optional[float] = None     # if None, derived from freq + er_max
    antenna_clearance: float = 0.5  # air above the surface for the antenna
    air_buffer: float = 0.1         # extra air above the antenna
    rx_spacing: float = 0.0         # 0 -> monostatic (co-located TX/RX)
    title: str = "N-layer scene"


def _derive_dx(freq_hz: float, er_max: float, any_packed: bool) -> float:
    lambda_min = C_LIGHT / (_FMAX_FACTOR * freq_hz * math.sqrt(er_max))
    dx = lambda_min / _DX_LAMBDA_FRACTION
    if any_packed:
        dx = min(dx, _DX_ROCK_CAP)
    # Round down to a clean 0.5 mm step for tidy grids.
    return max(math.floor(dx / 5e-4) * 5e-4, 5e-4)


def _unique_materials(layers: List[Layer]) -> tuple[list[MaterialCommand], dict]:
    """Collect distinct (eps, sigma) materials; free_space is built-in (skipped).

    Returns (#material commands, name->id map keyed by 'flat:<name>' / 'rock:<name>').
    """
    cmds: list[MaterialCommand] = []
    by_id: dict[str, tuple[float, float]] = {}

    def add(base_id: str, eps: float, sigma: float) -> str:
        if base_id in ("free_space", "air"):
            return "free_space"
        ident = base_id
        n = 2
        # Disambiguate a reused name that carries different properties.
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
                      rock_id: str, seed: Optional[int]) -> list[CylinderCommand]:
    """Fill [y0, y1] x [0, domain_x] with rocks from the physics packer."""
    from .pymunk_packing import MbubiaPymunkSceneGenerator
    packer = MbubiaPymunkSceneGenerator(
        scene_name="layer_pack", upper_material="clean_ballast", verbose=False,
    )
    bounds = PackingBounds(x_min=0.0, x_max=domain_x, y_min=y0, y_max=y1)
    rocks = packer.generate_rocks(bounds)
    cmds: list[CylinderCommand] = []
    for r in rocks:
        if r.radius <= 0:
            continue
        # Keep rocks whose body stays inside the layer band.
        if r.y - r.radius < y0 - 1e-6 or r.y + r.radius > y1 + 1e-6:
            continue
        cmds.append(CylinderCommand(
            x1=r.x, y1=r.y, z1=0.0, x2=r.x, y2=r.y, z2=dz, radius=r.radius, material=rock_id,
        ))
    return cmds


def build_scene_commands(layers: List[Layer], params: SceneParams,
                         seed: Optional[int] = None) -> List[str]:
    """Build the ordered list of rendered gprMax command strings for the scene."""
    er_max = max(
        max(ly.eps, ly.rock_eps or 0.0) for ly in layers
    )
    any_packed = any(ly.packed for ly in layers)
    dx = params.dx if params.dx is not None else _derive_dx(params.freq_hz, er_max, any_packed)
    dz = dx

    # Vertical layout (bottom -> top).
    subsurface_top = sum(ly.thickness for ly in layers)
    domain_y = subsurface_top + params.antenna_clearance + params.air_buffer
    antenna_y = subsurface_top + params.antenna_clearance * 0.5
    tx_x = params.domain_x / 2.0
    rx_x = tx_x + params.rx_spacing

    # Two-way travel time to the deepest interface + pulse/settle margin.
    v_min = C_LIGHT / math.sqrt(er_max)
    time_window = (2.0 * subsurface_top / v_min) * 1.6 + 3e-9

    mat_cmds, id_map = _unique_materials(layers)

    header = [
        f"## {params.title}",
        f"## N-layer scene: {len(layers)} layers, {params.freq_hz/1e6:.0f} MHz, "
        f"single monostatic dipole, dx={dx*1e3:.1f}mm",
        DomainCommand(params.domain_x, domain_y, dz).get_cmd_string(),
        DxDyDzCommand(dx, dx, dz).get_cmd_string(),
        TimeWindowCommand(time_window).get_cmd_string(),
    ]

    materials = [m.get_cmd_string() for m in mat_cmds]

    wave_id = "the_wave"
    source = [
        WaveformCommand("ricker", 1.0, params.freq_hz, wave_id).get_cmd_string(),
        HertzianDipoleCommand("z", tx_x, antenna_y, dz / 2.0, wave_id).get_cmd_string(),
        RxCommand(rx_x, antenna_y, dz / 2.0).get_cmd_string(),
    ]

    # Geometry — painter's algorithm: air first, then strata bottom->top, then rocks.
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
            for c in _pack_layer_rocks(y0, y1, params.domain_x, dz, rock_id, seed):
                rock_cmds.append(c.get_cmd_string())
        else:
            box_id = id_map[(i, "box")]
            geometry.append(BoxCommand(0.0, y0, 0.0, params.domain_x, y1, dz, box_id).get_cmd_string())
        y0 = y1

    return header + [""] + materials + [""] + source + [""] + geometry + rock_cmds


def write_scene(layers: List[Layer], params: SceneParams, out_path: Path,
                seed: Optional[int] = None) -> Path:
    """Build the scene and write it to ``out_path`` (.in)."""
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    lines = build_scene_commands(layers, params, seed=seed)
    out_path.write_text("\n".join(lines) + "\n")
    return out_path

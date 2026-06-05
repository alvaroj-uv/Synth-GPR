#!/usr/bin/env python3
"""
Generate Mbubia-style synthetic two-layer gprMax scenes.

This script recreates the synthetic scene family described in
docs/studies/mbubia.md as closely as the paper allows:

- 4.0 x 1.2 x 0.001 m 2D gprMax domain
- 0.80 m structural trackbed height with air above it
- 0.002 m x/y cell size and 0.001 m z cell size
- 1.4 GHz Ricker source, 20 ns recording time
- monostatic source/receiver 0.30 m above the structural surface
- two-layer material pairings with the lower layer having higher permittivity
- random irregular polygon ballast in clean/fouled ballast layers

The original paper does not publish its voxelization code, packing algorithm,
conductivity table, interface curve model, or scan step. Those parts are
therefore explicit approximations, written into the generated metadata headers.

Usage examples:

    python scripts/experiments/generate_mbubia_scene.py output/mbubia.in
    python scripts/experiments/generate_mbubia_scene.py output/mbubia.in --pair fouled_subgrade --seed 12
    python scripts/experiments/generate_mbubia_scene.py output/mbubia_batch --all-pairs -n 5
    python scripts/experiments/generate_mbubia_scene.py output/mbubia_bscan.in --scan bscan --scan-step 0.01
"""

from __future__ import annotations

import argparse
import math
import random
import io
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterable

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

from src.gpr_commands import (  # noqa: E402
    AbsorbingBCCommand,
    BoxCommand,
    DomainCommand,
    DxDyDzCommand,
    Header,
    HertzianDipoleCommand,
    MaterialCommand,
    RawCommand,
    RxCommand,
    TimeWindowCommand,
    TriangleCommand,
    WaveformCommand,
)
from src.visualization.scene import parse_in_file, render_geometry_figure # type: ignore
from src.physics import fmt  # noqa: E402

try:
    import matplotlib.pyplot as plt
except ImportError:
    plt = None


DOMAIN_X = 4.0
DOMAIN_Y = 1.2
DOMAIN_Z = 0.001
STRUCTURE_TOP_Y = 0.8
DX = 0.002
DY = 0.002
DZ = 0.001
CENTER_FREQ_HZ = 1.4e9
TIME_WINDOW_S = 20e-9
ANTENNA_HEIGHT_M = 0.3
DEFAULT_SCAN_MARGIN_M = 0.30

MIN_GRAIN_RADIUS = 0.036 / 2.0
MAX_GRAIN_RADIUS = 0.060 / 2.0


@dataclass(frozen=True)
class MaterialSpec:
    key: str
    label: str
    material_id: str
    eps_range: tuple[float, float]
    rbf_label: str
    sigma: float
    granular: bool


MATERIALS: dict[str, MaterialSpec] = {
    "clean_ballast": MaterialSpec(
        key="clean_ballast",
        label="clean ballast",
        material_id="bal_rock_L1",
        eps_range=(2.5, 5.0),
        rbf_label="<2",
        sigma=0.001,
        granular=True,
    ),
    "fouled_ballast": MaterialSpec(
        key="fouled_ballast",
        label="fouled ballast",
        material_id="bal_foul_granular",
        eps_range=(3.8, 7.5),
        rbf_label="2-18",
        sigma=0.005,
        granular=True,
    ),
    "highly_fouled_ballast": MaterialSpec(
        key="highly_fouled_ballast",
        label="highly fouled ballast",
        material_id="bal_foul",
        eps_range=(15.0, 18.5),
        rbf_label=">=55",
        sigma=0.020,
        granular=False,
    ),
    "wet_subgrade_soil": MaterialSpec(
        key="wet_subgrade_soil",
        label="wet subgrade soil",
        material_id="subgrade",
        eps_range=(20.5, 25.0),
        rbf_label=">=55",
        sigma=0.030,
        granular=False,
    ),
}


PAIR_DEFS: dict[str, tuple[str, str]] = {
    "clean_highly_fouled": ("clean_ballast", "highly_fouled_ballast"),
    "clean_fouled": ("clean_ballast", "fouled_ballast"),
    "clean_subgrade": ("clean_ballast", "wet_subgrade_soil"),
    "fouled_highly_fouled": ("fouled_ballast", "highly_fouled_ballast"),
    "fouled_subgrade": ("fouled_ballast", "wet_subgrade_soil"),
    "highly_fouled_subgrade": ("highly_fouled_ballast", "wet_subgrade_soil"),
}


@dataclass
class SceneParameters:
    pair_key: str
    upper: MaterialSpec
    lower: MaterialSpec
    upper_eps: float
    lower_eps: float
    upper_thickness: float
    interface_kind: str
    interface_amplitude: float
    seed: int | None

    @property
    def interface_base_y(self) -> float:
        return STRUCTURE_TOP_Y - self.upper_thickness


@dataclass
class Circle:
    x: float
    y: float
    radius: float


def _sample_eps(
    rng: random.Random,
    upper: MaterialSpec,
    lower: MaterialSpec,
    eps_gap: float,
    upper_override: float | None,
    lower_override: float | None,
) -> tuple[float, float]:
    if upper_override is None:
        upper_eps = rng.uniform(*upper.eps_range)
    else:
        upper_eps = upper_override

    if lower_override is None:
        lower_min = max(lower.eps_range[0], upper_eps + eps_gap)
        if lower_min > lower.eps_range[1]:
            raise ValueError(
                f"Cannot sample lower eps for {lower.key}: upper eps {upper_eps:.3f} "
                f"plus gap {eps_gap:.3f} exceeds lower range {lower.eps_range}."
            )
        lower_eps = rng.uniform(lower_min, lower.eps_range[1])
    else:
        lower_eps = lower_override

    if lower_eps <= upper_eps:
        raise ValueError(
            f"Paper pair rule violated: lower eps ({lower_eps}) must be greater "
            f"than upper eps ({upper_eps})."
        )
    return upper_eps, lower_eps


def _make_interface(params: SceneParameters) -> Callable[[float], float]:
    base_y = params.interface_base_y
    amp = params.interface_amplitude
    if params.interface_kind == "flat" or amp <= 0:
        return lambda _x: base_y

    rng = random.Random((params.seed or 0) + 7919)
    phase1 = rng.uniform(0.0, 2.0 * math.pi)
    phase2 = rng.uniform(0.0, 2.0 * math.pi)
    phase3 = rng.uniform(0.0, 2.0 * math.pi)
    min_y = 0.02
    max_y = STRUCTURE_TOP_Y - 0.02

    def y_at(x: float) -> float:
        t = x / DOMAIN_X
        y = base_y + amp * (
            0.55 * math.sin(2.0 * math.pi * t + phase1)
            + 0.30 * math.sin(4.0 * math.pi * t + phase2)
            + 0.15 * math.sin(math.pi * t + phase3)
        )
        return max(min_y, min(max_y, y))

    return y_at


def _segment_edges(width: float) -> list[tuple[float, float]]:
    if width <= 0 or width >= DOMAIN_X:
        return [(0.0, DOMAIN_X)]

    n = max(1, int(math.ceil(DOMAIN_X / width)))
    edges = []
    for i in range(n):
        x1 = i * DOMAIN_X / n
        x2 = (i + 1) * DOMAIN_X / n
        edges.append((x1, x2))
    return edges


def _layer_area(
    layer: str,
    interface_y: Callable[[float], float],
    samples: int = 512,
) -> float:
    dx = DOMAIN_X / samples
    area = 0.0
    for i in range(samples):
        x = (i + 0.5) * dx
        iy = interface_y(x)
        if layer == "upper":
            area += max(0.0, STRUCTURE_TOP_Y - iy) * dx
        else:
            area += max(0.0, iy) * dx
    return area


def _point_bounds(
    layer: str,
    x: float,
    radius: float,
    interface_y: Callable[[float], float],
) -> tuple[float, float] | None:
    margin = radius * 1.25
    iy = interface_y(x)
    if layer == "upper":
        y_min = iy + margin
        y_max = STRUCTURE_TOP_Y - margin
    else:
        y_min = margin
        y_max = iy - margin
    if y_max <= y_min:
        return None
    return y_min, y_max


def _generate_circles(
    layer: str,
    interface_y: Callable[[float], float],
    rng: random.Random,
    fill_ratio: float,
    max_attempts: int,
) -> list[Circle]:
    layer_area = _layer_area(layer, interface_y)
    mean_r = 0.5 * (MIN_GRAIN_RADIUS + MAX_GRAIN_RADIUS)
    target = int(layer_area * fill_ratio / (math.pi * mean_r * mean_r))
    if target <= 0:
        return []

    circles: list[Circle] = []
    cell_size = 2.0 * MAX_GRAIN_RADIUS
    grid: dict[tuple[int, int], list[int]] = {}

    def grid_key(x: float, y: float) -> tuple[int, int]:
        return int(x // cell_size), int(y // cell_size)

    def collides(x: float, y: float, r: float) -> bool:
        gx, gy = grid_key(x, y)
        for nx in range(gx - 2, gx + 3):
            for ny in range(gy - 2, gy + 3):
                for idx in grid.get((nx, ny), []):
                    other = circles[idx]
                    min_dist = 1.05 * (r + other.radius)
                    if (x - other.x) ** 2 + (y - other.y) ** 2 < min_dist * min_dist:
                        return True
        return False

    attempts = 0
    max_total_attempts = max_attempts * target
    while len(circles) < target and attempts < max_total_attempts:
        attempts += 1
        r = rng.uniform(MIN_GRAIN_RADIUS, MAX_GRAIN_RADIUS)
        x = rng.uniform(r * 1.25, DOMAIN_X - r * 1.25)
        bounds = _point_bounds(layer, x, r, interface_y)
        if bounds is None:
            continue
        y = rng.uniform(*bounds)
        if collides(x, y, r):
            continue
        circle = Circle(x, y, r)
        circles.append(circle)
        grid.setdefault(grid_key(x, y), []).append(len(circles) - 1)

    return circles


def _polygon_vertices(
    circle: Circle,
    rng: random.Random,
    sides_min: int,
    sides_max: int,
) -> list[tuple[float, float]]:
    sides = rng.randint(sides_min, sides_max)
    offset = rng.uniform(0.0, 2.0 * math.pi)
    delta = 2.0 * math.pi / sides
    raw_radii = []
    for i in range(sides):
        angle = offset + i * delta
        perturb = (
            0.17 * math.cos(3.0 * angle + rng.uniform(-0.6, 0.6))
            + 0.08 * math.cos(7.0 * angle + rng.uniform(-0.6, 0.6))
            + rng.uniform(-0.05, 0.05)
        )
        raw_radii.append(circle.radius * max(0.72, 1.0 + perturb))

    raw_area = 0.5 * math.sin(delta) * sum(
        raw_radii[i] * raw_radii[(i + 1) % sides] for i in range(sides)
    )
    scale = math.sqrt(math.pi * circle.radius**2 / raw_area) if raw_area > 0 else 1.0

    vertices = []
    for i, rr in enumerate(raw_radii):
        angle = offset + i * delta
        r = rr * scale
        x = max(0.0, min(DOMAIN_X, circle.x + r * math.cos(angle)))
        y = max(0.0, min(STRUCTURE_TOP_Y, circle.y + r * math.sin(angle)))
        vertices.append((x, y))
    return vertices


def _triangulate_polygons(
    circles: Iterable[Circle],
    rng: random.Random,
    material: str,
    sides_min: int,
    sides_max: int,
) -> list[TriangleCommand]:
    triangles: list[TriangleCommand] = []
    for circle in circles:
        vertices = _polygon_vertices(circle, rng, sides_min, sides_max)
        for i in range(len(vertices)):
            x1, y1 = vertices[i]
            x2, y2 = vertices[(i + 1) % len(vertices)]
            triangles.append(
                TriangleCommand(
                    circle.x,
                    circle.y,
                    0.0,
                    x1,
                    y1,
                    0.0,
                    x2,
                    y2,
                    0.0,
                    DOMAIN_Z,
                    material,
                )
            )
    return triangles


def _material_commands(params: SceneParameters, grain_eps: float, sigma_scale: float) -> list[MaterialCommand]:
    specs = {params.upper.key: params.upper, params.lower.key: params.lower}
    commands = []
    eps_by_key = {
        params.upper.key: params.upper_eps,
        params.lower.key: params.lower_eps,
    }
    for spec in specs.values():
        commands.append(
            MaterialCommand(
                eps=eps_by_key[spec.key],
                sigma=spec.sigma * sigma_scale,
                mu=1.0,
                mag_loss=0.0,
                identifier=spec.material_id,
            )
        )

    if params.upper.granular or params.lower.granular:
        commands.append(
            MaterialCommand(
                eps=grain_eps,
                sigma=0.001 * sigma_scale,
                mu=1.0,
                mag_loss=0.0,
                identifier="bal_rock",
            )
        )

    return commands


def _layer_boxes(
    params: SceneParameters,
    interface_y: Callable[[float], float],
    segment_width: float,
) -> list[BoxCommand]:
    boxes = [
        BoxCommand(0.0, 0.0, 0.0, DOMAIN_X, DOMAIN_Y, DOMAIN_Z, "free_space")
    ]
    edges = _segment_edges(segment_width if params.interface_kind == "curved" else DOMAIN_X)
    for x1, x2 in edges:
        mid = 0.5 * (x1 + x2)
        iy = interface_y(mid)
        boxes.append(BoxCommand(x1, 0.0, 0.0, x2, iy, DOMAIN_Z, params.lower.material_id))
        boxes.append(
            BoxCommand(x1, iy, 0.0, x2, STRUCTURE_TOP_Y, DOMAIN_Z, params.upper.material_id)
        )
    return boxes


def _headers(
    params: SceneParameters,
    upper_rocks: int,
    lower_rocks: int,
    scan: str,
    scan_step: float,
    gprmax_n: int,
) -> list[str]:
    headers = [
        Header("=" * 60).render(),
        Header("Mbubia-style synthetic two-layer scene").render(),
        Header("Reference: docs/studies/mbubia.md").render(),
        Header("Approximation: true").render(),
        Header("Reason: paper omits voxelization code, conductivities, exact packing, and scan step").render(),
        Header(f"MBUBIA_pair: {params.pair_key}").render(),
        Header(f"MBUBIA_upper_layer: {params.upper.key}").render(),
        Header(f"MBUBIA_lower_layer: {params.lower.key}").render(),
        Header(f"MBUBIA_upper_eps: {fmt(params.upper_eps)}").render(),
        Header(f"MBUBIA_lower_eps: {fmt(params.lower_eps)}").render(),
        Header(f"MBUBIA_upper_Rb_f_percent: {params.upper.rbf_label}").render(),
        Header(f"MBUBIA_lower_Rb_f_percent: {params.lower.rbf_label}").render(),
        Header(f"MBUBIA_upper_thickness_m: {fmt(params.upper_thickness)}").render(),
        Header(f"MBUBIA_interface_base_y_m: {fmt(params.interface_base_y)}").render(),
        Header(f"MBUBIA_interface_kind: {params.interface_kind}").render(),
        Header(f"MBUBIA_interface_amplitude_m: {fmt(params.interface_amplitude)}").render(),
        Header(f"MBUBIA_upper_polygon_count: {upper_rocks}").render(),
        Header(f"MBUBIA_lower_polygon_count: {lower_rocks}").render(),
        Header(f"MBUBIA_scan: {scan}").render(),
        Header(f"MBUBIA_scan_step_m: {fmt(scan_step)}").render(),
        Header(f"MBUBIA_gprmax_n: {gprmax_n}").render(),
    ]
    if params.seed is not None:
        headers.append(Header(f"MBUBIA_seed: {params.seed}").render())
    headers.append(Header("=" * 60).render())
    return headers


def build_scene_text(args: argparse.Namespace, sample_index: int = 0) -> str:
    seed = None if args.seed is None else args.seed + sample_index
    rng = random.Random(seed)
    upper_key, lower_key = PAIR_DEFS[args.pair]
    upper = MATERIALS[upper_key]
    lower = MATERIALS[lower_key]
    upper_eps, lower_eps = _sample_eps(
        rng,
        upper,
        lower,
        args.eps_gap,
        args.upper_eps,
        args.lower_eps,
    )
    upper_thickness = (
        args.upper_thickness
        if args.upper_thickness is not None
        else rng.uniform(0.13, 0.79)
    )
    if not 0.13 <= upper_thickness <= 0.79:
        raise ValueError("upper thickness must be in the paper range [0.13, 0.79] m")

    interface_amplitude = args.interface_amplitude
    max_amp = min(0.10, 0.30 * upper_thickness, 0.30 * (STRUCTURE_TOP_Y - upper_thickness))
    if args.interface == "curved":
        interface_amplitude = min(interface_amplitude, max(0.0, max_amp))
    else:
        interface_amplitude = 0.0

    params = SceneParameters(
        pair_key=args.pair,
        upper=upper,
        lower=lower,
        upper_eps=upper_eps,
        lower_eps=lower_eps,
        upper_thickness=upper_thickness,
        interface_kind=args.interface,
        interface_amplitude=interface_amplitude,
        seed=seed,
    )

    interface_y = _make_interface(params)

    upper_circles: list[Circle] = []
    lower_circles: list[Circle] = []
    if upper.granular:
        upper_circles = _generate_circles(
            "upper", interface_y, rng, args.fill_ratio, args.max_attempts_per_particle
        )
    if lower.granular:
        lower_circles = _generate_circles(
            "lower", interface_y, rng, args.fill_ratio, args.max_attempts_per_particle
        )

    triangles = []
    triangles.extend(
        _triangulate_polygons(
            upper_circles,
            rng,
            "bal_rock",
            args.polygon_sides_min,
            args.polygon_sides_max,
        )
    )
    triangles.extend(
        _triangulate_polygons(
            lower_circles,
            rng,
            "bal_rock",
            args.polygon_sides_min,
            args.polygon_sides_max,
        )
    )

    if args.scan == "bscan":
        tx_x = args.scan_margin
        gprmax_n = int(math.floor((DOMAIN_X - 2.0 * args.scan_margin) / args.scan_step)) + 1
    else:
        tx_x = 0.5  # A-scan over left rail (paper: antenna centered over rail)
        gprmax_n = 1
    tx_y = STRUCTURE_TOP_Y + ANTENNA_HEIGHT_M
    tx_z = DOMAIN_Z / 2.0
    rx_x = tx_x + args.rx_offset

    lines: list[str] = []
    lines.extend(
        _headers(
            params,
            len(upper_circles),
            len(lower_circles),
            args.scan,
            args.scan_step,
            gprmax_n,
        )
    )
    lines.append("#title: Mbubia-style two-layer synthetic scene")
    lines.append("#messages: n")
    lines.append(DomainCommand(DOMAIN_X, DOMAIN_Y, DOMAIN_Z).render())
    lines.append(DxDyDzCommand(DX, DY, DZ).render())
    lines.append(TimeWindowCommand(TIME_WINDOW_S).render())
    lines.append(AbsorbingBCCommand(cells=10, z_cells=0).render())
    lines.append("")
    lines.append(Header("Materials").render())
    for cmd in _material_commands(params, args.grain_eps, args.sigma_scale):
        lines.append(cmd.render())
    lines.append("")
    lines.append(Header("Geometry").render())
    for cmd in _layer_boxes(params, interface_y, args.interface_segment_width):
        lines.append(cmd.render())
    for cmd in triangles:
        lines.append(cmd.render())
    lines.append("")
    lines.append(Header("Sources and Receivers").render())
    lines.append(WaveformCommand("ricker", 1.0, CENTER_FREQ_HZ, "ricker_src").render())
    lines.append(HertzianDipoleCommand("z", tx_x, tx_y, tx_z, "ricker_src").render())
    lines.append(RxCommand(rx_x, tx_y, tx_z).render())
    if args.scan == "bscan":
        lines.append(RawCommand(f"#src_steps: {fmt(args.scan_step)} 0 0").render())
        lines.append(RawCommand(f"#rx_steps: {fmt(args.scan_step)} 0 0").render())
    lines.append("")
    lines.append(Header(f"Run with: gprMax <this-file> -n {gprmax_n}").render())

    return "\n".join(lines) + "\n"


def _output_paths(args: argparse.Namespace) -> list[tuple[str, Path]]:
    pair_keys = list(PAIR_DEFS) if args.all_pairs else [args.pair]
    count = args.num * len(pair_keys)
    output = Path(args.output)

    if count == 1 and output.suffix == ".in":
        return [(pair_keys[0], output)]

    output.mkdir(parents=True, exist_ok=True)
    paths = []
    for pair in pair_keys:
        for i in range(args.num):
            suffix = f"_{i:03d}" if args.num > 1 else ""
            paths.append((pair, output / f"mbubia_{pair}{suffix}.in"))
    return paths


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate Mbubia-style two-layer synthetic gprMax .in scenes."
    )
    parser.add_argument("output", help="Output .in file, or output directory for batch modes.")
    parser.add_argument("--pair", choices=sorted(PAIR_DEFS), default="clean_subgrade")
    parser.add_argument("--all-pairs", action="store_true", help="Generate all six paper pairings.")
    parser.add_argument("-n", "--num", type=int, default=1, help="Scenes per selected pair.")
    parser.add_argument("--seed", type=int, default=None)
    parser.add_argument("--upper-thickness", type=float, default=None)
    parser.add_argument("--upper-eps", type=float, default=None)
    parser.add_argument("--lower-eps", type=float, default=None)
    parser.add_argument("--eps-gap", type=float, default=0.05)
    parser.add_argument("--interface", choices=["flat", "curved"], default="flat")
    parser.add_argument("--interface-amplitude", type=float, default=0.035)
    parser.add_argument("--interface-segment-width", type=float, default=0.02)
    parser.add_argument("--fill-ratio", type=float, default=0.55)
    parser.add_argument("--max-attempts-per-particle", type=int, default=80)
    parser.add_argument("--polygon-sides-min", type=int, default=7)
    parser.add_argument("--polygon-sides-max", type=int, default=12)
    parser.add_argument("--grain-eps", type=float, default=5.5)
    parser.add_argument("--sigma-scale", type=float, default=1.0)
    parser.add_argument("--scan", choices=["ascan", "bscan"], default="ascan")
    parser.add_argument("--scan-step", type=float, default=0.01)
    parser.add_argument("--scan-margin", type=float, default=DEFAULT_SCAN_MARGIN_M)
    parser.add_argument("--render-png", action="store_true", help="Also render a PNG image of the scene.")
    parser.add_argument("--png-dpi", type=int, default=150, help="DPI for the rendered PNG image.")
    parser.add_argument("--rx-offset", type=float, default=0.0)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.num < 1:
        raise ValueError("--num must be >= 1")
    if args.fill_ratio < 0:
        raise ValueError("--fill-ratio must be non-negative")
    if args.polygon_sides_min < 3 or args.polygon_sides_max < args.polygon_sides_min:
        raise ValueError("polygon side bounds must satisfy 3 <= min <= max")
    if args.scan == "bscan" and args.scan_step <= 0:
        raise ValueError("--scan-step must be positive")

    written = []
    paths = _output_paths(args)
    original_pair = args.pair
    for idx, (pair, path) in enumerate(paths):
        args.pair = pair
        text = build_scene_text(args, sample_index=idx)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        written.append(path)
    args.pair = original_pair

    if args.render_png:
        if plt is None:
            print("Warning: matplotlib not available, skipping PNG rendering")
        else:
            print("Rendering PNGs...")
            for path in written:
                try:
                    scene_data = parse_in_file(path)
                    fig, _ = render_geometry_figure(scene_data, title=scene_data.title)
                    png_path = path.with_suffix(".png")
                    fig.savefig(png_path, bbox_inches="tight", dpi=args.png_dpi)
                    plt.close(fig)
                except Exception as e:
                    print(f"Error rendering {path.name}: {e}")

    print(f"Wrote {len(written)} Mbubia-style scene(s):")
    for path in written[:10]:
        print(f"  {path}")
    if len(written) > 10:
        print(f"  ... {len(written) - 10} more")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

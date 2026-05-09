"""
MC Comparison Test: Geometry-based vs Pixel-based Monte Carlo.

Renders a scene two ways and compares phase fraction estimates:
  - Geometry-MC : random (x,y) points classified via painter's algorithm on raw geometry
  - Pixel-MC    : figure rendered to memory array, random pixels classified by color

Usage:
    python scripts/tools/tests/test_mc_comparison.py
    python scripts/tools/tests/test_mc_comparison.py output/test/s_0000.in --n 100000 --dpi 300
"""

import sys
import argparse
import numpy as np
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from src.visualization.scene import parse_in_file, render_geometry_figure, STYLES, SceneData


# ── Color reverse-map ─────────────────────────────────────────────────────────

def _build_color_map() -> dict[tuple[int, int, int], str]:
    """Map (R, G, B) uint8 tuples → material name."""
    result = {}
    for mat, style in STYLES.items():
        try:
            rgb = tuple(int(round(c * 255)) for c in plt.matplotlib.colors.to_rgb(style.color))
            result[rgb] = mat
        except Exception:
            pass
    # Background / air
    try:
        air_style = STYLES.get("free_space")
        if air_style:
            rgb = tuple(int(round(c * 255)) for c in plt.matplotlib.colors.to_rgb(air_style.color))
            result[rgb] = "free_space"
    except Exception:
        pass
    return result


def _nearest_material(pixel_rgb: np.ndarray, color_map: dict, tolerance: int = 18) -> str | None:
    """Return material whose color is closest to pixel_rgb within tolerance, or None."""
    best_mat = None
    best_dist = tolerance * tolerance * 3 + 1  # worse than any match
    for rgb, mat in color_map.items():
        d = sum((int(pixel_rgb[i]) - rgb[i]) ** 2 for i in range(3))
        if d < best_dist:
            best_dist = d
            best_mat = mat
    return best_mat if best_dist <= tolerance * tolerance * 3 else None


# ── Geometry-MC ───────────────────────────────────────────────────────────────

# gprMax painter priority groups (higher = drawn on top / wins)
_ZORDER = {"box": 1, "cylinder": 2}

_MATERIAL_GROUP = {
    "bal_rock": "rock",
    "bal_rock_L1": "rock", "bal_rock_L2": "rock", "bal_rock_L3": "rock",
    "bal_foul": "fouling", "bal_foul_granular": "fouling",
    **{f"bal_foul_g{i}": "fouling" for i in range(1, 10)},
    "subgrade": "subgrade",
    "formation": "formation",
    "free_space": "air",
    "concrete_sleeper": "other",
}


def geometry_mc(scene: SceneData, n_samples: int) -> dict[str, float]:
    """
    Classify random (x,y) points using painter's algorithm on SceneData.

    Boxes are applied first (zorder 1), then cylinders (zorder 2) overwrite.
    Last writer within each zorder group wins — matches gprMax render order.
    """
    rng = np.random.default_rng(42)
    xs = rng.uniform(0, scene.domain_x, n_samples)
    ys = rng.uniform(0, scene.domain_y, n_samples)

    material = np.full(n_samples, "air", dtype=object)

    # Pass 1: boxes (zorder 1) — applied in file order, last wins
    for box in scene.boxes:
        mask = (xs >= box.x1) & (xs <= box.x2) & (ys >= box.y1) & (ys <= box.y2)
        material[mask] = box.material

    # Pass 2: cylinders (zorder 2) — override boxes
    for cyl in scene.cylinders:
        dx = xs - cyl.x
        dy = ys - cyl.y
        mask = dx**2 + dy**2 <= cyl.radius**2
        material[mask] = cyl.material

    counts: dict[str, int] = {}
    for mat in material:
        group = _MATERIAL_GROUP.get(mat, "other")
        counts[group] = counts.get(group, 0) + 1

    return {k: v / n_samples for k, v in counts.items()}


# ── Pixel-MC ──────────────────────────────────────────────────────────────────

def pixel_mc(scene: SceneData, n_samples: int, dpi: int = 300) -> tuple[dict[str, float], int]:
    """
    Render scene to an in-memory numpy array and classify random pixels.

    Samples only within the axes data region (excludes margins, legend, labels).
    Returns (fractions, n_unmatched) — unmatched pixels are border/hatch artifacts.
    """
    fig, ax = render_geometry_figure(scene, dpi=dpi)
    fig.canvas.draw()
    buf = np.frombuffer(fig.canvas.buffer_rgba(), dtype=np.uint8)
    img = buf.reshape(fig.canvas.get_width_height()[::-1] + (4,))[:, :, :3]

    # Crop to axes data area (excludes figure margins, tick labels, legend chrome)
    bbox = ax.get_window_extent(renderer=fig.canvas.get_renderer())
    fig_h_px = fig.canvas.get_width_height()[1]
    # get_window_extent returns (x0, y0, x1, y1) in display coords (y=0 at bottom)
    col0, col1 = int(bbox.x0), int(bbox.x1)
    # flip y: display y0=bottom → image row = fig_h - display_y
    row0, row1 = int(fig_h_px - bbox.y1), int(fig_h_px - bbox.y0)
    row0, row1 = max(0, row0), min(img.shape[0], row1)
    col0, col1 = max(0, col0), min(img.shape[1], col1)
    img_crop = img[row0:row1, col0:col1]
    plt.close(fig)

    color_map = _build_color_map()
    h, w = img_crop.shape[:2]

    rng = np.random.default_rng(42)
    row_idx = rng.integers(0, h, n_samples)
    col_idx = rng.integers(0, w, n_samples)
    pixels = img_crop[row_idx, col_idx]  # (n_samples, 3)

    counts: dict[str, int] = {}
    n_unmatched = 0
    for px in pixels:
        mat = _nearest_material(px, color_map)
        if mat is None:
            n_unmatched += 1
            continue
        group = _MATERIAL_GROUP.get(mat, "other")
        counts[group] = counts.get(group, 0) + 1

    matched = n_samples - n_unmatched
    return ({k: v / matched for k, v in counts.items()} if matched else {}), n_unmatched


# ── Report ────────────────────────────────────────────────────────────────────

def _pct(d: dict, key: str) -> str:
    return f"{d.get(key, 0) * 100:6.2f}%"


def print_report(geo: dict, pix: dict, n_unmatched: int, n_samples: int, dpi: int) -> None:
    groups = sorted(set(geo) | set(pix))
    print()
    print("=" * 58)
    print(f"  MC Comparison  (n={n_samples:,}, pixel DPI={dpi})")
    print("=" * 58)
    print(f"  {'Group':<18} {'Geometry-MC':>12} {'Pixel-MC':>12}  {'Delta':>8}")
    print("-" * 58)
    for g in groups:
        gv = geo.get(g, 0)
        pv = pix.get(g, 0)
        delta = (pv - gv) * 100
        print(f"  {g:<18} {gv*100:>11.2f}% {pv*100:>11.2f}%  {delta:>+7.2f}pp")
    print("-" * 58)
    unmatched_pct = n_unmatched / n_samples * 100
    print(f"  Pixel unmatched (border/hatch): {n_unmatched:,} ({unmatched_pct:.1f}%)")
    print("=" * 58)
    print()
    print("  Interpretation:")
    rock_delta = abs(pix.get("rock", 0) - geo.get("rock", 0)) * 100
    foul_delta = abs(pix.get("fouling", 0) - geo.get("fouling", 0)) * 100
    if rock_delta < 2.0 and foul_delta < 2.0:
        print("  [PASS] Rock and fouling fractions agree within 2 pp.")
        print("         Pixel-MC is a viable cross-check.")
    else:
        print("  [GAP]  Rock and/or fouling differ by >2 pp.")
        if unmatched_pct > 5:
            print(f"         High unmatched rate ({unmatched_pct:.1f}%) — hatches/borders")
            print("         are absorbing pixels that belong to real materials.")
            print("         Try --dpi 600 or increase --tolerance.")
        else:
            print("         Gap is not explained by unmatched pixels.")
            print("         Likely a systematic difference (axis limits, margins).")
    print()


# ── Entry point ───────────────────────────────────────────────────────────────

def main() -> None:
    ap = argparse.ArgumentParser(description="Compare geometry-MC vs pixel-MC")
    ap.add_argument(
        "in_file", nargs="?",
        default="output/test/s_0000.in",
        type=Path,
        help=".in file to analyse (default: output/test/s_0000.in)",
    )
    ap.add_argument("--n",   type=int, default=50_000, help="MC sample count")
    ap.add_argument("--dpi", type=int, default=300,    help="Render DPI for pixel-MC")
    args = ap.parse_args()

    in_path = Path(args.in_file)
    if not in_path.exists():
        print(f"[ERROR] File not found: {in_path}")
        sys.exit(1)

    print(f"Parsing {in_path} ...")
    scene = parse_in_file(in_path)
    print(f"  Domain: {scene.domain_x:.3f} x {scene.domain_y:.3f} m  |  "
          f"{len(scene.boxes)} boxes, {len(scene.cylinders)} cylinders")

    print(f"Running geometry-MC (n={args.n:,}) ...")
    geo_fractions = geometry_mc(scene, args.n)

    print(f"Running pixel-MC (n={args.n:,}, dpi={args.dpi}) ...")
    pix_fractions, n_unmatched = pixel_mc(scene, args.n, dpi=args.dpi)

    print_report(geo_fractions, pix_fractions, n_unmatched, args.n, args.dpi)


if __name__ == "__main__":
    main()

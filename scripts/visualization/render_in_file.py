"""
Render a gprMax .in file as a 2-D cross-section PNG.

Usage:
    python scripts/visualization/render_in_file.py output/test/s_0000.in
    python scripts/visualization/render_in_file.py output/test/s_0000.in --out custom.png --dpi 200
"""

import sys
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from src.visualization.in_parser import parse_in_file
from src.visualization.geometry_render import draw_geometry


def main() -> None:
    ap = argparse.ArgumentParser(description="Render a gprMax .in file as PNG")
    ap.add_argument("in_file", type=Path, help="Path to .in file")
    ap.add_argument("--out",   type=Path, default=None,
                    help="Output PNG path (default: same dir, same stem)")
    ap.add_argument("--dpi",   type=int,  default=150)
    args = ap.parse_args()

    in_path  = args.in_file.resolve()
    out_path = args.out or in_path.with_suffix(".png")

    scene = parse_in_file(in_path)

    aspect = scene.domain_y / max(scene.domain_x, 1e-6)
    fig_w  = 6.0
    fig_h  = min(fig_w * aspect * 0.75, 14)
    fig, ax = plt.subplots(figsize=(fig_w, fig_h), dpi=args.dpi)
    ax.set_title(in_path.stem, fontsize=10, fontweight="bold")

    draw_geometry(ax, scene)

    fig.tight_layout()
    fig.savefig(out_path, dpi=args.dpi, bbox_inches="tight")
    print(f"Saved -> {out_path}")


if __name__ == "__main__":
    main()

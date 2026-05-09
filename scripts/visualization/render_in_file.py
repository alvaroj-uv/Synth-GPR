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

from src.visualization.scene import parse_in_file, render_geometry_figure


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
    fig, _ = render_geometry_figure(scene, title=in_path.stem, dpi=args.dpi)
    fig.savefig(out_path, dpi=args.dpi, bbox_inches="tight")
    print(f"Saved -> {out_path}")


if __name__ == "__main__":
    main()

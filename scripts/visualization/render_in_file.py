"""
Render a gprMax .in file as a 2-D cross-section PNG or full analysis dashboard.

Usage:
    # Geometry only (fast):
    python scripts/visualization/render_in_file.py output/test/s_0000.in
    python scripts/visualization/render_in_file.py output/test/s_0000.in --out custom.png --dpi 200

    # Full 4-panel dashboard (geometry + signals + PSD + stats):
    python scripts/visualization/render_in_file.py output/test/s_0000.in --dashboard
    python scripts/visualization/render_in_file.py s_0000.in -o report.png --no-show --no-dewow --gain power
"""

import sys
import logging
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from src.visualization.scene import parse_in_file, render_geometry_figure
from src.visualization.dashboard import render_dashboard
from src.visualization.panels import SignalPanelConfig

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("Visualizer")


def main() -> None:
    ap = argparse.ArgumentParser(description="Render a gprMax .in file as PNG or dashboard")
    ap.add_argument("in_file", type=Path, help="Path to .in file")
    ap.add_argument("-o", "--output", type=Path, default=None,
                    help="Output PNG path (default: same dir, same stem)")
    ap.add_argument("--dpi", type=int, default=150, help="Output DPI")
    ap.add_argument("--dashboard", action="store_true",
                    help="Render the full 4-panel analysis dashboard")
    ap.add_argument("--no-show", action="store_true", help="Skip interactive window")
    ap.add_argument("--no-dewow", action="store_true", help="Disable dewow processing")
    ap.add_argument("--gain", choices=["power", "exp", "agc"], default=None,
                    help="Gain type for signal processing")
    ap.add_argument("--alpha", type=float, default=1.0, help="Gain exponent")
    ap.add_argument("--components", nargs="+", default=["Ez"],
                    help="Field components to display (e.g. Ez Hx)")
    ap.add_argument("--rx", nargs="+", default=None,
                    help="Receiver names to display (e.g. rx1 rx2)")

    # Legacy compatibility
    ap.add_argument("--full-dashboard", action="store_true",
                    help="Legacy: Use --dashboard instead")

    args = ap.parse_args()

    in_path = args.in_file.resolve()

    # Handle legacy flag
    if args.full_dashboard:
        args.dashboard = True

    if args.dashboard:
        sig_cfg = SignalPanelConfig(
            dewow=not args.no_dewow,
            gain_type=args.gain,
            gain_alpha=args.alpha,
            components=args.components,
            receivers=args.rx,
        )

        fig, out_path = render_dashboard(
            in_path,
            out_path=args.output,
            sig_cfg=sig_cfg,
        )

        if not args.no_show:
            plt.show()
    else:
        out_path = args.output or in_path.with_suffix(".png")
        scene = parse_in_file(in_path)
        fig, _ = render_geometry_figure(scene, title=in_path.stem, dpi=args.dpi)
        fig.savefig(out_path, dpi=args.dpi, bbox_inches="tight")

    print(f"Saved -> {out_path}")


if __name__ == "__main__":
    main()

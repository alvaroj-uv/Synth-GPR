"""
Full dashboard visualizer for a gprMax .in file.

Produces a 4-column figure:
  [raw signals] | [geometry] | [processed signals] | [PSD curve + stats]

If no matching .out file is found, signal columns show a placeholder.

Usage:
    python scripts/tools/visualization/visualize_gprmax_blueprint.py output/test/s_0000.in
    python scripts/tools/visualization/visualize_gprmax_blueprint.py s_0000.in -o report.png --no-show
    python scripts/tools/visualization/visualize_gprmax_blueprint.py s_0000.in --no-dewow --gain power
"""

import sys
import logging
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from src.visualization.scene import parse_in_file
from src.visualization.dashboard import render_dashboard
from src.visualization.panels import SignalPanelConfig

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("Visualizer")


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Visualize a gprMax .in file as a full analysis dashboard."
    )
    ap.add_argument("in_file", type=Path)
    ap.add_argument("-o", "--output", type=Path, default=None,
                    help="Output PNG path (default: same dir, same stem)")
    ap.add_argument("--no-show",  action="store_true", help="Skip interactive window")
    ap.add_argument("--no-dewow", action="store_true", help="Disable dewow processing")
    ap.add_argument("--gain", choices=["power", "exp", "agc"], default=None)
    ap.add_argument("--alpha", type=float, default=1.0, help="Gain exponent")
    ap.add_argument("--components", nargs="+", default=["Ez"],
                    help="Field components to display (e.g. Ez Hx)")
    ap.add_argument("--rx", nargs="+", default=None,
                    help="Receiver names to display (e.g. rx1 rx2)")
    args = ap.parse_args()

    in_path  = args.in_file.resolve()

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


if __name__ == "__main__":
    main()

"""
Render a gprMax .in file as 2-D/3-D geometry PNG or full analysis dashboard.

Automatically detects 2D vs 3D files (3D = contains #sphere commands).

Usage:
    # Geometry only (fast):
    python scripts/visualization/render_in_file.py output/test/s_0000.in
    python scripts/visualization/render_in_file.py input_files_3d_poc/s_0000.in  # Auto-detects 3D

    # Full 4-panel dashboard (2D only):
    python scripts/visualization/render_in_file.py output/test/s_0000.in --dashboard
"""

import sys
import logging
import argparse
import re
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


def detect_3d_file(in_path: Path) -> bool:
    """Detect if .in file is 3D (contains #sphere commands)."""
    with open(in_path, 'r', encoding='utf-8', errors='replace') as f:
        return any('#sphere:' in line for line in f)


def render_3d_file(in_path: Path, out_path: Path, dpi: int = 150):
    """Render 3D .in file using the specialized 3D renderer."""
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "render_3d",
        Path(__file__).parent / "render_3d_in_file.py"
    )
    render_3d = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(render_3d)

    scene_data = render_3d.parse_3d_in_file(in_path)
    title = f"{in_path.stem} - {scene_data['metadata'].get('Lab_Class', '?')} class"
    fig = render_3d.render_3d_views(scene_data, title=title, dpi=dpi)
    fig.savefig(out_path, dpi=dpi, bbox_inches="tight")
    plt.close(fig)


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

    # Detect 2D vs 3D
    is_3d = detect_3d_file(in_path)

    if is_3d and args.dashboard:
        logger.warning("3D files do not support --dashboard mode, rendering geometry only")

    if args.dashboard and not is_3d:
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
        # Render 2D or 3D geometry
        out_path = args.output or in_path.with_suffix(".png")

        if is_3d:
            render_3d_file(in_path, out_path, dpi=args.dpi)
        else:
            scene = parse_in_file(in_path)
            fig, _ = render_geometry_figure(scene, title=in_path.stem, dpi=args.dpi)
            fig.savefig(out_path, dpi=args.dpi, bbox_inches="tight")
            plt.close(fig)

        print(f"Saved -> {out_path}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Unified GPR Visualization Tool

Combines all visualization capabilities in one script:
  - Geometry from .in file
  - A-scans (time-domain signals)
  - Frequency spectrum
  - Feature extraction & analysis
  - 4-panel dashboard

Usage:
    python scripts/visualization/unified_visualizer.py test.in
    python scripts/visualization/unified_visualizer.py test.out
    python scripts/visualization/unified_visualizer.py test --all --gain agc --no-show
"""

import sys
import argparse
import logging
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

from src.visualization.render import detect_3d_file, render_geometry_png
from src.visualization.dashboard import render_dashboard
from src.visualization.panels import SignalPanelConfig
from src.data_loader import read_gprmax_hdf5, read_ascan
from src.feature_extraction import extract_features
from src.signal_processing import preprocess_signal, compute_padded_spectrum

logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)


def find_paired_file(path: Path) -> Path | None:
    """Find the paired .in or .out file."""
    if path.suffix == ".in":
        paired = path.with_suffix(".out")
    else:
        paired = path.with_suffix(".in")
    return paired if paired.exists() else None


# Geometry rendering (2D/3D dispatch, overlays, annotations) lives in
# src.visualization.render so pipelines import it directly instead of
# shelling out to this CLI. This script is a thin CLI over that facade.


def visualize_ascan_only(out_path: Path, out_png: Path, component: str = "Ez", dpi: int = 150) -> None:
    """Visualize A-scan and frequency spectrum from .out file."""
    from scipy.signal import hilbert

    logger.info(f"Reading {out_path.name}...")
    data = read_ascan(out_path, component)
    if data["component"] != component:
        logger.warning(f"Component '{component}' not found. Available: {data['available']}")
    component = data["component"]
    signal    = data["signal"]
    dt        = data["dt"]
    rx_pos    = data["rx_pos"]
    t_ns      = data["t_ns"]

    # Frequency spectrum (shared padded-rFFT + peak)
    freqs, spectrum, peak_hz = compute_padded_spectrum(signal, dt)
    freq_ghz = freqs / 1e9
    peak_ghz = peak_hz / 1e9

    # Envelope
    envelope = np.abs(hilbert(signal))

    # Plot
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))

    # A-scan
    ax1.plot(t_ns, signal, linewidth=0.8, color="blue", label="Signal")
    ax1.plot(t_ns, envelope, linewidth=1.5, color="red", label="Envelope", alpha=0.7)
    ax1.set_xlabel("Time (ns)")
    ax1.set_ylabel("Amplitude")
    ax1.set_title(f"A-scan at RX {rx_pos} | Component: {component}")
    ax1.grid(True, alpha=0.3)
    ax1.legend()

    # Spectrum
    ax2.semilogy(freq_ghz, spectrum, linewidth=1, color="purple")
    ax2.axvline(peak_ghz, color="red", linestyle="--", label=f"Peak: {peak_ghz:.2f} GHz")
    ax2.set_xlabel("Frequency (GHz)")
    ax2.set_ylabel("Magnitude (log)")
    ax2.set_title("Frequency Spectrum")
    ax2.grid(True, alpha=0.3, which="both")
    ax2.legend()

    plt.tight_layout()
    fig.savefig(out_png, dpi=dpi, bbox_inches="tight")
    logger.info(f"✓ Saved: {out_png}")
    plt.close(fig)


def visualize_full_dashboard(in_path: Path, out_path: Path, sig_cfg: SignalPanelConfig, dpi: int = 150) -> None:
    """Render full 4-panel dashboard with geometry + signals."""
    logger.info("Rendering full dashboard...")
    fig, final_path = render_dashboard(
        in_path,
        out_path=out_path,
        sig_cfg=sig_cfg,
        dpi=dpi,
    )
    logger.info(f"✓ Saved: {final_path}")
    plt.close(fig)


def visualize_all_combined(in_path: Path, out_path: Path, out_ascan: Path, sig_cfg: SignalPanelConfig, dpi: int = 150) -> None:
    """Create three visualizations: geometry, A-scan, and dashboard."""
    # 1. Geometry only
    geom_path = out_path.with_stem(f"{out_path.stem}_01_geometry")
    render_geometry_png(in_path, geom_path, dpi)

    # 2. A-scan only
    out_file = in_path.with_suffix(".out")
    if out_file.exists():
        ascan_path = out_path.with_stem(f"{out_path.stem}_02_ascan")
        try:
            visualize_ascan_only(out_file, ascan_path, "Ez", dpi)
        except Exception as e:
            logger.warning(f"Could not visualize A-scan: {e}")

    # 3. Full dashboard
    dashboard_path = out_path.with_stem(f"{out_path.stem}_03_dashboard")
    try:
        visualize_full_dashboard(in_path, dashboard_path, sig_cfg, dpi)
    except Exception as e:
        logger.warning(f"Could not render dashboard: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="Unified GPR Visualization Tool - Combine geometry, signals, and analysis",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Quick geometry view
  python %(prog)s test.in

  # A-scan + spectrum
  python %(prog)s test.out

  # Full dashboard (geometry + signals)
  python %(prog)s test.in --dashboard

  # All three visualizations
  python %(prog)s test.in --all

  # With signal processing
  python %(prog)s test.in --all --gain agc --no-dewow
        """
    )

    parser.add_argument("file", type=Path, help="Path to .in or .out file")
    parser.add_argument("-o", "--output", type=Path, default=None,
                        help="Output PNG path (default: auto-generated)")
    parser.add_argument("--geometry", action="store_true",
                        help="Show geometry only")
    parser.add_argument("--ascan", action="store_true",
                        help="Show A-scan + spectrum only")
    parser.add_argument("--dashboard", action="store_true",
                        help="Show full 4-panel dashboard")
    parser.add_argument("--all", action="store_true",
                        help="Generate all three visualizations")
    parser.add_argument("--component", default="Ez",
                        help="Field component for A-scan (default: Ez)")
    parser.add_argument("--title", default=None,
                        help="Custom plot title for geometry mode (supports \\n)")
    parser.add_argument("--metadata", default=None,
                        help="Annotation text box for geometry mode (supports \\n)")
    parser.add_argument("--no-show", action="store_true",
                        help="Don't display, save only")
    parser.add_argument("--no-dewow", action="store_true",
                        help="Skip dewow processing")
    parser.add_argument("--gain", choices=["power", "exp", "agc"], default=None,
                        help="Gain type for signal processing")
    parser.add_argument("--alpha", type=float, default=1.0,
                        help="Gain exponent (for --gain exp)")
    parser.add_argument("--dpi", type=int, default=150,
                        help="Output DPI")
    args = parser.parse_args()

    # Resolve input file
    in_file = args.file.resolve()
    if not in_file.exists():
        logger.error(f"File not found: {in_file}")
        return 1

    # Determine file type
    is_in_file = in_file.suffix == ".in"
    is_out_file = in_file.suffix == ".out"

    if not (is_in_file or is_out_file):
        logger.error(f"File must be .in or .out, got: {in_file.suffix}")
        return 1

    # Find paired file if needed
    if is_in_file and (args.all or args.dashboard or args.ascan):
        out_file = in_file.with_suffix(".out")
        if not out_file.exists():
            logger.warning(f"No .out file found at {out_file}")
            if args.dashboard or args.ascan:
                logger.error("Cannot proceed without .out file")
                return 1
    else:
        out_file = in_file if is_out_file else None

    if is_out_file:
        in_file = in_file.with_suffix(".in")
        if not in_file.exists():
            logger.warning(f"No .in file found at {in_file}")

    # Determine output path
    out_path = args.output or in_file.with_stem(f"{in_file.stem}_visualization").with_suffix(".png")
    out_path = out_path.resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)

    # Setup signal config
    sig_cfg = SignalPanelConfig(
        dewow=not args.no_dewow,
        gain_type=args.gain,
        gain_alpha=args.alpha,
    )

    logger.info(f"Input file: {in_file.name}")
    logger.info(f"Output dir: {out_path.parent}")

    # Process escape sequences in title/metadata (geometry mode annotations)
    title = args.title.replace("\\n", "\n") if args.title else None
    metadata = args.metadata.replace("\\n", "\n") if args.metadata else None

    # 3D files only support geometry rendering (no dashboard/signal panels).
    is_3d = in_file.suffix == ".in" and in_file.exists() and detect_3d_file(in_file)
    if is_3d and (args.all or args.dashboard):
        logger.warning("3D files do not support dashboard mode — rendering geometry only")

    # Execute visualizations
    if args.all and not is_3d:
        logger.info("Mode: Generate ALL visualizations")
        visualize_all_combined(in_file, out_path, out_path.with_stem(f"{out_path.stem}_ascan"), sig_cfg, args.dpi)
    elif args.dashboard and not is_3d:
        logger.info("Mode: Full Dashboard")
        visualize_full_dashboard(in_file, out_path, sig_cfg, args.dpi)
    elif args.ascan:
        logger.info(f"Mode: A-scan ({args.component})")
        if not out_file or not out_file.exists():
            logger.error("No .out file found")
            return 1
        visualize_ascan_only(out_file, out_path, args.component, args.dpi)
    elif args.geometry or is_3d:
        logger.info("Mode: Geometry only" + (" (3D)" if is_3d else ""))
        render_geometry_png(in_file, out_path, args.dpi, title=title, metadata=metadata)
    else:
        # Auto-detect: if .out exists, show dashboard; otherwise geometry
        if out_file and out_file.exists():
            logger.info("Mode: Full Dashboard (auto-detected .out file)")
            visualize_full_dashboard(in_file, out_path, sig_cfg, args.dpi)
        else:
            logger.info("Mode: Geometry only (no .out file found)")
            render_geometry_png(in_file, out_path, args.dpi, title=title, metadata=metadata)

    if not args.no_show:
        logger.info("Opening visualization...")
        import subprocess
        try:
            subprocess.run(["open" if sys.platform == "darwin" else "xdg-open", str(out_path)])
        except Exception as e:
            logger.warning(f"Could not open file: {e}")

    return 0


if __name__ == "__main__":
    sys.exit(main())

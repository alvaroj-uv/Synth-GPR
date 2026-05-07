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
import matplotlib.gridspec as gridspec
import numpy as np

from src.visualization.in_parser import parse_in_file
from src.visualization.geometry_render import draw_geometry
from src.visualization.signal_panels import (
    SignalPanelConfig,
    filter_signals,
    preprocess_signals,
    strongest_signal,
    draw_ascan,
    draw_envelope,
    draw_spectrogram,
)
from src.visualization.grading_curve import draw_grading_curve

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("Visualizer")


def _load_signals(hdf5_path: Path, cfg: SignalPanelConfig) -> tuple:
    """
    Load, filter, and return (signals, time_ns, dt) from an HDF5 .out file.
    Returns empty values if loading fails or file is absent.
    """
    try:
        from src.data_loader import read_gprmax_hdf5
        df = read_gprmax_hdf5(str(hdf5_path), fields=["E", "H"])
        if df.empty:
            return {}, np.array([]), 1e-10

        time_vec = df["Time"].values if "Time" in df.columns else np.array([])
        dt = float(time_vec[1] - time_vec[0]) if len(time_vec) > 1 else 1e-10

        raw = {col: df[col].values for col in df.columns if col != "Time"}
        return filter_signals(raw, cfg), time_vec * 1e9, dt

    except Exception as exc:
        logger.warning(f"Could not load signals: {exc}")
        return {}, np.array([]), 1e-10


def _blank_signal_column(fig, gs, col: int) -> None:
    for row in range(3):
        ax = fig.add_subplot(gs[row, col])
        ax.text(0.5, 0.5, "No signal data", ha="center", va="center", fontsize=9)
        ax.axis("off")


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
    out_path = args.output or in_path.with_suffix(".png")

    sig_cfg = SignalPanelConfig(
        dewow=not args.no_dewow,
        gain_type=args.gain,
        gain_alpha=args.alpha,
        components=args.components,
        receivers=args.rx,
    )

    logger.info(f"Parsing {in_path.name}...")
    scene = parse_in_file(in_path)

    # Try adjacent .out file, then outputs/ subdirectory
    hdf5_path = in_path.with_suffix(".out")
    if not hdf5_path.exists():
        hdf5_path = in_path.parent / "outputs" / hdf5_path.name

    signals, time_ns, dt = {}, np.array([]), 1e-10
    if hdf5_path.exists():
        logger.info(f"Loading signals from {hdf5_path.name}...")
        signals, time_ns, dt = _load_signals(hdf5_path, sig_cfg)
    else:
        logger.info("No .out file found — signal panels will be blank.")

    # ── Layout ────────────────────────────────────────────────────────────────
    # Col 0: raw signals (3 rows)
    # Col 1: geometry (spans all rows, 2× width)
    # Col 2: processed signals (3 rows)
    # Col 3: PSD curve (row 0) + metadata text (rows 1-2)
    fig = plt.figure(figsize=(24, 10))
    gs  = gridspec.GridSpec(3, 4, width_ratios=[1, 2, 1, 1], figure=fig)

    # Geometry panel
    ax_geo = fig.add_subplot(gs[:, 1])
    ax_geo.set_title(in_path.stem, fontsize=10, fontweight="bold")
    draw_geometry(ax_geo, scene)

    # Signal panels
    if signals:
        proc      = preprocess_signals(signals, dt, sig_cfg)
        best_raw  = strongest_signal(signals)
        best_proc = strongest_signal(proc)

        draw_ascan(     fig.add_subplot(gs[0, 0]), signals, time_ns, "Raw A-scan")
        draw_envelope(  fig.add_subplot(gs[1, 0]), best_raw,  time_ns, dt, "Raw Envelope")
        draw_spectrogram(fig.add_subplot(gs[2, 0]), best_raw,  dt)

        draw_ascan(     fig.add_subplot(gs[0, 2]), proc,     time_ns, "Processed A-scan")
        draw_envelope(  fig.add_subplot(gs[1, 2]), best_proc, time_ns, dt, "Processed Envelope")
        draw_spectrogram(fig.add_subplot(gs[2, 2]), best_proc, dt)
    else:
        _blank_signal_column(fig, gs, col=0)
        _blank_signal_column(fig, gs, col=2)

    # PSD / grading curve
    draw_grading_curve(fig.add_subplot(gs[0, 3]), scene.meta.get("Lab_PSD"))

    # Metadata text panel
    ax_info = fig.add_subplot(gs[1:, 3])
    ax_info.axis("off")
    meta = scene.meta
    lines = ["Geotechnical Stats\n"]
    for key, label in [("FI (%)", "FI"), ("FI_class", "Class"),
                       ("pvc", "PVC"), ("Lab_Class", "Lab class")]:
        if key in meta:
            lines.append(f"{label}: {meta[key]}")
    ax_info.text(0.1, 0.9, "\n".join(lines), fontsize=10, va="top")

    # ── Save ──────────────────────────────────────────────────────────────────
    plt.tight_layout()
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    logger.info(f"Saved -> {out_path}")

    if not args.no_show:
        plt.show()


if __name__ == "__main__":
    main()

"""
Dashboard renderer for gprMax .in files.

Provides a callable render_dashboard() function so that any script can
produce the full 4-panel analysis figure without spawning a subprocess.
"""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

from .drawing import draw_geometry
from .overlays import draw_research_overlays
from .parser import parse_in_file
from .panels import (
    SignalPanelConfig,
    filter_signals,
    preprocess_signals,
    strongest_signal,
    draw_ascan,
    draw_envelope,
    draw_spectrogram,
    draw_grading_curve,
)

logger = logging.getLogger(__name__)


def _load_signals(hdf5_path: Path, cfg: SignalPanelConfig) -> tuple:
    """Load, filter, and return (signals, time_ns, dt) from an HDF5 .out file."""
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


def render_dashboard(
    in_path: Path,
    out_path: Optional[Path] = None,
    dpi: int = 150,
    sig_cfg: Optional[SignalPanelConfig] = None,
) -> tuple:
    """
    Build the full 4-panel analysis dashboard for a gprMax .in file.

    Args:
        in_path:  Resolved path to the .in file.
        out_path: Output PNG path. Defaults to same stem as in_path.
        dpi:      Output resolution.
        sig_cfg:  Signal panel configuration (dewow, gain, etc.).

    Returns:
        (fig, out_path) — the matplotlib figure and the path it was saved to.
    """
    if sig_cfg is None:
        sig_cfg = SignalPanelConfig()

    out_path = out_path or in_path.with_suffix(".png")

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

    # Layout: [raw signals] | [geometry x2] | [processed signals] | [PSD + metadata]
    fig = plt.figure(figsize=(24, 10))
    gs  = gridspec.GridSpec(3, 4, width_ratios=[1, 2, 1, 1], figure=fig)

    ax_geo = fig.add_subplot(gs[:, 1])
    ax_geo.set_title(in_path.stem, fontsize=10, fontweight="bold")
    draw_geometry(ax_geo, scene)
    # Dashboard is an analysis view: opt into the MC/LDCP research overlays
    draw_research_overlays(ax_geo, scene)

    if signals:
        proc      = preprocess_signals(signals, dt, sig_cfg)
        best_raw  = strongest_signal(signals)
        best_proc = strongest_signal(proc)

        draw_ascan(      fig.add_subplot(gs[0, 0]), signals,   time_ns, "Raw A-scan")
        draw_envelope(   fig.add_subplot(gs[1, 0]), best_raw,  time_ns, dt, "Raw Envelope")
        draw_spectrogram(fig.add_subplot(gs[2, 0]), best_raw,  dt)

        draw_ascan(      fig.add_subplot(gs[0, 2]), proc,      time_ns, "Processed A-scan")
        draw_envelope(   fig.add_subplot(gs[1, 2]), best_proc, time_ns, dt, "Processed Envelope")
        draw_spectrogram(fig.add_subplot(gs[2, 2]), best_proc, dt)
    else:
        _blank_signal_column(fig, gs, col=0)
        _blank_signal_column(fig, gs, col=2)

    draw_grading_curve(fig.add_subplot(gs[0, 3]), scene.meta.get("Lab_PSD"))

    ax_info = fig.add_subplot(gs[1:, 3])
    ax_info.axis("off")
    meta = scene.meta
    lines = ["Geotechnical Stats\n"]
    for key, label in [("FI (%)", "FI"), ("FI_class", "Class"),
                       ("pvc", "PVC"), ("Lab_Class", "Lab class")]:
        if key in meta:
            lines.append(f"{label}: {meta[key]}")
    ax_info.text(0.1, 0.9, "\n".join(lines), fontsize=10, va="top")

    plt.tight_layout()
    fig.savefig(out_path, dpi=dpi, bbox_inches="tight")
    logger.info(f"Saved -> {out_path}")

    return fig, out_path

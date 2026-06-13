"""
Dashboard renderer for gprMax .in files.

Provides a callable render_dashboard() function so that any script can
produce the full 4-panel analysis figure without spawning a subprocess.
"""
from __future__ import annotations

import logging
import re
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


def _get_direct_wave_gate_ns(signals: dict, dt: float) -> Optional[float]:
    """Calculate the end of the direct wave based on the start of the peak-relative coda gate from feature extraction."""
    best_raw = strongest_signal(signals)
    if best_raw is None or len(best_raw) == 0:
        return 4.5
    
    try:
        from src.signal_processing import peak_relative_coda_gate
        mask, _ = peak_relative_coda_gate(best_raw, dt, seek_peak=True)
        indices = np.where(mask)[0]
        if len(indices) > 0:
            return float(indices[0] * dt * 1e9)
        return 4.5
    except Exception as e:
        logger.warning(f"Could not calculate peak-relative direct wave gate: {e}")
        return 4.5


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
    logger.info(f"Parsing {in_path.name}...")
    scene = parse_in_file(in_path)

    out_path = out_path or in_path.with_suffix(".png")

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

    gate_ns = _get_direct_wave_gate_ns(signals, dt)
    if sig_cfg is None:
        sig_cfg = SignalPanelConfig(direct_wave_gate_ns=gate_ns)
    else:
        sig_cfg.direct_wave_gate_ns = gate_ns

    # Layout: [raw] | [geometry / coda] | [processed] | [PSD + metadata]
    fig = plt.figure(figsize=(24, 10))
    gs  = gridspec.GridSpec(3, 4, width_ratios=[1, 2, 1, 1], figure=fig)

    # Geometry takes rows 0 and 1 of Column 1
    ax_geo = fig.add_subplot(gs[0:2, 1])
    ax_geo.set_title(in_path.stem, fontsize=10, fontweight="bold")
    draw_geometry(ax_geo, scene)
    # Dashboard is an analysis view: opt into the MC/LDCP research overlays
    draw_research_overlays(ax_geo, scene)

    if signals:
        proc      = preprocess_signals(signals, dt, sig_cfg)
        best_raw  = strongest_signal(signals)
        best_proc = strongest_signal(proc)

        draw_ascan(      fig.add_subplot(gs[0, 0]), signals,   time_ns, "Raw A-scan", direct_wave_gate_ns=gate_ns)
        draw_envelope(   fig.add_subplot(gs[1, 0]), best_raw,  time_ns, dt, "Raw Envelope")
        draw_spectrogram(fig.add_subplot(gs[2, 0]), best_raw,  dt)

        draw_ascan(      fig.add_subplot(gs[0, 2]), proc,      time_ns, "Processed A-scan", direct_wave_gate_ns=None)
        draw_envelope(   fig.add_subplot(gs[1, 2]), best_proc, time_ns, dt, "Processed Envelope")
        draw_spectrogram(fig.add_subplot(gs[2, 2]), best_proc, dt)

        # Extract Coda-aligned signals (raw coda, not normalized, matching the raw A-scan scale)
        from src.signal_processing import peak_relative_coda_gate
        coda_signals = {}
        coda_time_ns = None
        for name, sig in signals.items():
            try:
                mask, _ = peak_relative_coda_gate(sig, dt, seek_peak=True)
                coda_signals[name] = sig[mask]
                if coda_time_ns is None:
                    coda_time_ns = time_ns[mask]
            except Exception as e:
                logger.warning(f"Could not extract coda segment for {name}: {e}")

        if coda_signals and coda_time_ns is not None and len(coda_time_ns) > 0:
            draw_ascan(fig.add_subplot(gs[2, 1]), coda_signals, coda_time_ns, "Raw Coda A-scan", direct_wave_gate_ns=None)
        else:
            ax_blank = fig.add_subplot(gs[2, 1])
            ax_blank.text(0.5, 0.5, "No coda signal", ha="center", va="center", fontsize=9)
            ax_blank.axis("off")
    else:
        _blank_signal_column(fig, gs, col=0)
        _blank_signal_column(fig, gs, col=2)
        # Blank the coda row under geometry
        ax_blank = fig.add_subplot(gs[2, 1])
        ax_blank.text(0.5, 0.5, "No signal data", ha="center", va="center", fontsize=9)
        ax_blank.axis("off")

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

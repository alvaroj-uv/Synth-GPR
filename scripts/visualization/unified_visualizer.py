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
from src.signal_processing import (preprocess_signal, compute_padded_spectrum,
    vivanco_preprocess, vivanco_preprocess_bscan, vivanco_extract_features,
    _VIVANCO_DROP_CELLS, agc_bscan, fk_filter, bandpass_filter)
from src.dzt_io import read_dzt_traces

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


def visualize_ascan_only(out_path: Path, out_png: Path, component: str = "Ez",
                         dpi: int = 150,
                         tmin_ns: float = None, tmax_ns: float = None) -> None:
    """Visualize A-scan and frequency spectrum from .out file.

    Args:
        tmin_ns: Start of time-axis zoom in ns (None = full trace).
        tmax_ns: End   of time-axis zoom in ns (None = full trace).
    """
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
    zoom_label = f"  [{tmin_ns:.1f}–{tmax_ns:.1f} ns]" if (tmin_ns is not None or tmax_ns is not None) else ""
    ax1.set_title(f"A-scan at RX {rx_pos} | Component: {component}{zoom_label}")
    ax1.grid(True, alpha=0.3)
    ax1.legend()
    if tmin_ns is not None or tmax_ns is not None:
        ax1.set_xlim(
            tmin_ns if tmin_ns is not None else t_ns[0],
            tmax_ns if tmax_ns is not None else t_ns[-1],
        )

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


def _overlay_dir_by_filename(dir_path: Path, out_png: Path, component: str = "Ez",
                             dpi: int = 150, tmin_ns: float = None,
                             tmax_ns: float = None) -> None:
    """True-overlay of every *.out in a folder, legend = filename.

    Fallback used by visualize_overlay_dir for non-sweep folders (no
    metadata.csv), e.g. matched-pair A/B experiments. Traces are NOT
    normalised — amplitude differences are usually the point of the
    comparison — and a residual vs the first trace is drawn underneath
    when all traces share the same time base.
    """
    out_files = sorted(dir_path.glob("*.out"))
    if not out_files:
        raise FileNotFoundError(f"No *.out files in {dir_path}")

    traces = []
    for f in out_files:
        data = read_ascan(f, component)
        traces.append((f.stem, data["t_ns"], data["signal"]))

    same_base = all(len(t) == len(traces[0][1]) for _, t, _ in traces)
    n_ax = 2 if (same_base and len(traces) > 1) else 1
    fig, axes = plt.subplots(n_ax, 1, figsize=(14, 4 * n_ax), sharex=True,
                             squeeze=False)
    ax = axes[0][0]
    for name, t_ns, sig in traces:
        ax.plot(t_ns, sig, linewidth=0.8, alpha=0.8, label=name)
    ax.set_ylabel(f"{component} (V/m)")
    ax.set_title(f"A-scan overlay - {dir_path.name} ({len(traces)} traces)")
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.15)

    if n_ax == 2:
        ref_name, t_ns, ref = traces[0]
        ax2 = axes[1][0]
        for name, _, sig in traces[1:]:
            ax2.plot(t_ns, sig - ref, linewidth=0.8, alpha=0.8,
                     label=f"{name} - {ref_name}")
        ax2.set_ylabel(f"residual {component} (V/m)")
        ax2.legend(fontsize=8)
        ax2.grid(True, alpha=0.15)

    axes[-1][0].set_xlabel("Time (ns)")
    if tmin_ns is not None or tmax_ns is not None:
        axes[-1][0].set_xlim(tmin_ns, tmax_ns)
    plt.tight_layout()
    fig.savefig(out_png, dpi=dpi, bbox_inches="tight")
    logger.info(f"Saved: {out_png}")
    plt.close(fig)


def visualize_overlay_dir(dir_path: Path, out_png: Path, component: str = "Ez",
                          dpi: int = 150, color_by: str = "clean_m",
                          tmin_ns: float = None, tmax_ns: float = None,
                          waterfall: bool = True) -> None:
    """Overlay or waterfall plot of all A-scans in an experiment directory.

    Args:
        dir_path:   Experiment folder containing sample_*.out and metadata.csv.
        color_by:   Column in metadata.csv used for the colour axis.
        tmin_ns / tmax_ns: Optional time-axis zoom limits in ns.
        waterfall:  If True (default), stack traces with a vertical offset so
                    each is visible.  If False, draw all traces on the same
                    axes (true overlay); a legend entry per unique color_by
                    value is shown instead of right-hand labels.
    """
    import matplotlib.cm as cm
    import pandas as pd

    meta_path = dir_path / "metadata.csv"
    if not meta_path.exists():
        # Not a sweep folder: fall back to overlaying every *.out labelled by
        # filename (e.g. matched-pair A/B experiment folders).
        _overlay_dir_by_filename(dir_path, out_png, component=component,
                                 dpi=dpi, tmin_ns=tmin_ns, tmax_ns=tmax_ns)
        return
    meta = pd.read_csv(meta_path)

    out_files = sorted(dir_path.glob("sample_*.out"))
    if not out_files:
        raise FileNotFoundError(f"No sample_*.out files in {dir_path}")

    logger.info(f"Loading {len(out_files)} traces from {dir_path.name} ...")

    traces, color_vals, annotations, group_ids = [], [], [], []
    for out_file in out_files:
        sample_id = int(out_file.stem.split("_")[1])
        row = meta[meta["sample_id"] == sample_id]
        if row.empty:
            continue
        data = read_ascan(out_file, component)
        sig = data["signal"]
        t_ns = data["t_ns"]
        peak = np.abs(sig).max()
        sig = sig / peak if peak > 0 else sig
        traces.append((t_ns, sig))
        fouled_m = float(row["fouled_m"].iloc[0])
        clean_m  = float(row["clean_m"].iloc[0])
        eps_f    = float(row["eps_fouled"].iloc[0])
        color_vals.append(float(row[color_by].iloc[0]) if color_by in row.columns else float(sample_id))
        annotations.append(f"F={fouled_m:.2f} C={clean_m:.2f} eps={eps_f:.1f}")
        group_ids.append(fouled_m)

    n = len(traces)
    cmin, cmax = min(color_vals), max(color_vals)
    cmap = cm.plasma
    norm = plt.Normalize(vmin=cmin, vmax=cmax if cmax > cmin else cmin + 1)

    zoom_str = ""
    if tmin_ns is not None or tmax_ns is not None:
        lo = f"{tmin_ns:.1f}" if tmin_ns is not None else "start"
        hi = f"{tmax_ns:.1f}" if tmax_ns is not None else "end"
        zoom_str = f"  [{lo}-{hi} ns]"

    # ── time-axis mask (shared) ───────────────────────────────────────────────
    def _mask(t_ns):
        m = np.ones(len(t_ns), dtype=bool)
        if tmin_ns is not None:
            m &= t_ns >= tmin_ns
        if tmax_ns is not None:
            m &= t_ns <= tmax_ns
        return m

    if waterfall:
        # ── Waterfall: each trace offset vertically ───────────────────────────
        offset_step = 2.2
        fig_h = max(10, n * 0.28)
        fig, ax = plt.subplots(figsize=(14, fig_h))

        prev_group = None
        for i, ((t_ns, sig), cval, ann, grp) in enumerate(
                zip(traces, color_vals, annotations, group_ids)):
            offset = i * offset_step
            color = cmap(norm(cval))
            m = _mask(t_ns)
            ax.plot(t_ns[m], sig[m] + offset, color=color, linewidth=0.55, alpha=0.85)
            t_end = t_ns[m][-1] if m.any() else t_ns[-1]
            ax.text(t_end + 0.3, offset, ann,
                    va="center", ha="left", fontsize=5.5, color=color)
            if prev_group is not None and grp != prev_group:
                ax.axhline(offset - offset_step * 0.5, color="gray",
                           linewidth=0.4, linestyle="--", alpha=0.4)
            prev_group = grp

        ax.set_yticks([])
        ax.set_title(
            f"All {n} synthetic A-scans (waterfall) - {dir_path.name}\n"
            f"Peak-normalised {component} | coloured by {color_by}{zoom_str}"
        )
    else:
        # ── True overlay: all traces on the same axes ─────────────────────────
        fig, ax = plt.subplots(figsize=(14, 6))

        seen_labels = {}
        for (t_ns, sig), cval, ann in zip(traces, color_vals, annotations):
            color = cmap(norm(cval))
            m = _mask(t_ns)
            label = f"{color_by}={cval:.2f}" if cval not in seen_labels else "_nolegend_"
            seen_labels[cval] = True
            ax.plot(t_ns[m], sig[m], color=color, linewidth=0.7,
                    alpha=0.55, label=label)

        ax.set_ylabel(f"Amplitude (peak-normalised)")
        ax.set_title(
            f"All {n} synthetic A-scans (overlay) - {dir_path.name}\n"
            f"Peak-normalised {component} | coloured by {color_by}{zoom_str}"
        )

    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])
    fig.colorbar(sm, ax=ax, label=color_by, fraction=0.02, pad=0.01)

    ax.set_xlabel("Time (ns)")
    ax.grid(True, alpha=0.15, axis="x")
    if tmin_ns is not None or tmax_ns is not None:
        ax.set_xlim(
            tmin_ns if tmin_ns is not None else traces[0][0][0],
            tmax_ns if tmax_ns is not None else traces[0][0][-1],
        )

    plt.tight_layout()
    fig.savefig(out_png, dpi=dpi, bbox_inches="tight")
    logger.info(f"Saved: {out_png}")
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

    parser.add_argument("file", type=Path,
                        help="Path to .in / .out file, or experiment directory (for --overlay)")
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
    parser.add_argument("--tmin", type=float, default=None, metavar="NS",
                        help="Zoom start time in ns (A-scan / overlay mode)")
    parser.add_argument("--tmax", type=float, default=None, metavar="NS",
                        help="Zoom end time in ns (A-scan / overlay mode)")
    parser.add_argument("--overlay", action="store_true",
                        help="Plot all A-scans from an experiment directory")
    parser.add_argument("--no-offset", action="store_true",
                        help="With --overlay: draw all traces on the same axes (true overlay) "
                             "instead of the default waterfall (stacked with vertical offset)")
    parser.add_argument("--color-by", default="clean_m",
                        help="metadata.csv column used for colour in --overlay (default: clean_m)")
    args = parser.parse_args()

    # Resolve input path
    in_file = args.file.resolve()
    if not in_file.exists():
        logger.error(f"File not found: {in_file}")
        return 1

    # ── Overlay / waterfall mode (directory input) ────────────────────────────
    if in_file.is_dir() or args.overlay:
        dir_path = in_file if in_file.is_dir() else in_file.parent
        out_png  = args.output or dir_path / "overlay_all_ascans.png"
        out_png  = Path(out_png).resolve()
        out_png.parent.mkdir(parents=True, exist_ok=True)
        logger.info(f"Mode: Overlay waterfall ({dir_path.name})")
        visualize_overlay_dir(dir_path, out_png,
                              component=args.component, dpi=args.dpi,
                              color_by=args.color_by,
                              tmin_ns=args.tmin, tmax_ns=args.tmax,
                              waterfall=not args.no_offset)
        return 0

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
        visualize_ascan_only(out_file, out_path, args.component, args.dpi,
                             tmin_ns=args.tmin, tmax_ns=args.tmax)
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


def visualize_vivanco_pipeline(dzt_path: Path, out_png: Path,
                               trace_idx: int = 50,
                               n_bscan: int = 200,
                               bgr_window: int = 100,
                               dpi: int = 150) -> None:
    """Plot the Rojas-Vivanco (2025) pipeline applied to a DZT file.

    Four-panel figure:
      Top-left  : raw A-scan vs processed (single trace)
      Top-right : normalized Hilbert envelope before/after pipeline
      Bottom-left : raw B-scan (n_bscan traces, amplitude image)
      Bottom-right: processed envelope B-scan after full pipeline

    Args:
        dzt_path:  Path to a GSSI DZT file (128 KiB header + int32 samples).
        out_png:   Output PNG path.
        trace_idx: Which trace to highlight in the single-trace panels.
        n_bscan:   Number of consecutive traces to load for the B-scan panels.
        bgr_window: BGR rolling-mean window (traces) for vivanco_preprocess_bscan.
        dpi:       Output resolution.
    """
    from scipy.signal import hilbert as _hilbert

    traces, meta = read_dzt_traces(dzt_path, num_traces=n_bscan)
    dt = meta['sample_interval_ns'] * 1e-9
    n_samp = traces.shape[1]
    t_raw = np.arange(n_samp) * meta['sample_interval_ns']          # ns, full trace

    # ── Single-trace Vivanco ──────────────────────────────────────────────────
    r = vivanco_preprocess(traces[trace_idx], dt)
    t_proc = np.arange(len(r['processed'])) * meta['sample_interval_ns']  # ns

    # Raw envelope for comparison
    raw_norm = traces[trace_idx] / (r['peak_amp'] if r['peak_amp'] > 0 else 1.0)
    raw_env  = np.abs(_hilbert(raw_norm))
    raw_env  = raw_env / (raw_env.max() + 1e-12)

    # ── B-scan Vivanco ────────────────────────────────────────────────────────
    bres = vivanco_preprocess_bscan(traces, dt, bgr_window=bgr_window)
    env_bscan = bres['envelopes']           # (n_traces, n_win)
    n_win = env_bscan.shape[1]
    t_win = np.arange(n_win) * meta['sample_interval_ns']

    # ── Plot ─────────────────────────────────────────────────────────────────
    fig = plt.figure(figsize=(14, 9))
    gs  = gridspec.GridSpec(2, 2, figure=fig, hspace=0.38, wspace=0.32)

    # Panel 1: raw vs processed A-scan
    ax1 = fig.add_subplot(gs[0, 0])
    ax1.plot(t_raw, raw_norm, color='#888', lw=0.8, alpha=0.7, label='Raw (norm)')
    ax1.axvline(r['time_zero_idx'] * meta['sample_interval_ns'],
                color='C1', lw=1.2, ls='--', label='New t=0')
    ax1.plot(t_proc + r['time_zero_idx'] * meta['sample_interval_ns'],
             r['processed'], color='C0', lw=1.0, label='Processed')
    ax1.set_xlabel('Time (ns)')
    ax1.set_ylabel('Amplitude (norm)')
    ax1.set_title(f'A-scan trace {trace_idx}  —  raw vs processed')
    ax1.legend(fontsize=7, loc='upper right')
    ax1.set_xlim(0, t_raw[-1])

    # Panel 2: Hilbert envelope before/after
    ax2 = fig.add_subplot(gs[0, 1])
    ax2.plot(t_raw, raw_env, color='#888', lw=0.8, alpha=0.7, label='Raw envelope')
    ax2.axvline(r['time_zero_idx'] * meta['sample_interval_ns'],
                color='C1', lw=1.2, ls='--', label='New t=0')
    ax2.plot(t_win + r['time_zero_idx'] * meta['sample_interval_ns'],
             r['envelope'], color='C3', lw=1.0, label='Vivanco envelope')
    ax2.set_xlabel('Time (ns)')
    ax2.set_ylabel('Normalized envelope')
    ax2.set_title(f'Hilbert envelope  —  trace {trace_idx}')
    ax2.legend(fontsize=7, loc='upper right')
    ax2.set_xlim(0, t_raw[-1])

    # Panel 3: raw B-scan
    ax3 = fig.add_subplot(gs[1, 0])
    raw_img = traces / (np.max(np.abs(traces), axis=1, keepdims=True) + 1e-12)
    im3 = ax3.imshow(raw_img.T, aspect='auto', cmap='seismic',
                     vmin=-0.3, vmax=0.3,
                     extent=[0, n_bscan, t_raw[-1], t_raw[0]])
    ax3.axhline(r['time_zero_idx'] * meta['sample_interval_ns'],
                color='C1', lw=1.0, ls='--', alpha=0.8)
    ax3.set_xlabel('Trace index')
    ax3.set_ylabel('Time (ns)')
    ax3.set_title('Raw B-scan  (norm per trace)')
    plt.colorbar(im3, ax=ax3, shrink=0.7, label='Amplitude')

    # Panel 4: processed envelope B-scan
    ax4 = fig.add_subplot(gs[1, 1])
    t_win_abs = t_win + r['time_zero_idx'] * meta['sample_interval_ns']
    im4 = ax4.imshow(env_bscan.T, aspect='auto', cmap='hot',
                     vmin=0, vmax=0.5,
                     extent=[0, n_bscan, t_win_abs[-1], t_win_abs[0]])
    ax4.set_xlabel('Trace index')
    ax4.set_ylabel('Time (ns)')
    ax4.set_title('Vivanco pipeline  —  envelope B-scan (7 ns window)')
    plt.colorbar(im4, ax=ax4, shrink=0.7, label='Norm. envelope')

    fig.suptitle(
        f'Rojas-Vivanco (2025) preprocessing pipeline\n'
        f'{dzt_path.name}  |  bandpass 150-800 MHz  |  BGR window={bgr_window} traces',
        fontsize=10, y=1.01
    )
    out_png.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_png, dpi=dpi, bbox_inches='tight')
    plt.close(fig)
    logger.info(f'Vivanco pipeline plot saved -> {out_png}')


def visualize_vivanco_pipeline_steps(
    dzt_path: Path,
    out_png: Path,
    trace_idx: int = 50,
    bgr_window: int = 80,
    dpi: int = 150,
) -> None:
    """Step-by-step visual explanation of the Vivanco (2025) preprocessing pipeline.

    Six-panel figure showing what happens to a single GPR A-scan at each stage:
      1. Raw DZT signal (full ~50 ns trace, ADC counts)
      2. Normalized + dewowed, with the 7 ns window highlighted
      3. Pre-BGR windowed signal (direct wave inside window at sample 30)
      4. Post-BGR windowed signal (direct wave removed by background subtraction)
      5. Hilbert envelopes before and after BGR on the same axis
      6. The three feature grids (ST, H, AH) as colour images

    Args:
        dzt_path:  Path to a GSSI DZT file.
        out_png:   Output PNG path.
        trace_idx: Which trace to visualise (index into DZT).
        bgr_window: BGR rolling-window width in traces.
        dpi:       Output resolution.

    Reference:
        Rojas-Vivanco et al. (2025) Transportation Geotechnics 55, 101701.
    """
    from scipy.signal import hilbert as _hilbert, butter, filtfilt

    # ── Load one trace + neighbourhood for BGR ───────────────────────────────
    half = bgr_window // 2
    start = max(0, trace_idx - half)
    bscan_raw, meta = read_dzt_traces(dzt_path, start_trace=start,
                                       num_traces=bgr_window + 1)
    dt = meta['sample_interval_ns'] * 1e-9
    local_idx = trace_idx - start            # position of target trace
    raw_sig = bscan_raw[local_idx].astype(float)
    local_bg = np.mean(bscan_raw, axis=0).astype(float)
    n = len(raw_sig)
    t_full = np.arange(n) * dt * 1e9        # ns

    # ── Step 1: raw signal ────────────────────────────────────────────────────
    step1 = raw_sig.copy()

    # ── Step 2: normalize by raw-signal max in first half ────────────────────
    search_end = max(n // 2, 1)
    peak_amp = float(np.max(np.abs(step1[:search_end])))
    peak_idx  = int(np.argmax(np.abs(_hilbert(step1)[:search_end])))
    step2 = step1 / peak_amp if peak_amp > 0 else step1.copy()
    # dewow
    wow_len = max(3, int(round(20e-9 / dt)) | 1)  # ~20 ns running mean window
    from scipy.ndimage import uniform_filter1d
    step2 = step2 - uniform_filter1d(step2, size=wow_len)

    # ── Step 3: time-zero (backward shift) & window ───────────────────────────
    dt_ns = dt * 1e9
    n_shift = int(round(3.0 / dt_ns))
    time_zero_idx = max(0, peak_idx - n_shift)
    n_win = int(round(7.0 / dt_ns))

    # bandpass 150–800 MHz
    sig_bpass = step2.copy()
    fs, nyq = 1.0 / dt, 0.5 / dt
    lo, hi = 150e6 / nyq, 800e6 / nyq
    if 0 < lo < hi < 1.0 and len(sig_bpass) > 12:
        b, a = butter(4, [lo, hi], btype='band')
        sig_bpass = filtfilt(b, a, sig_bpass)

    pre_bgr_full = sig_bpass[time_zero_idx: time_zero_idx + n_win]
    if len(pre_bgr_full) < n_win:
        pre_bgr_full = np.pad(pre_bgr_full, (0, n_win - len(pre_bgr_full)))

    t_win = np.arange(n_win) * dt_ns        # ns, relative to window start

    # ── Step 4: BGR subtraction ───────────────────────────────────────────────
    bg_peak = float(np.max(np.abs(local_bg[:search_end])))
    bg_norm = local_bg / bg_peak if bg_peak > 0 else local_bg.copy()
    bg_norm = bg_norm - uniform_filter1d(bg_norm, size=wow_len)
    bg_filt = bg_norm.copy()
    if 0 < lo < hi < 1.0 and len(bg_filt) > 12:
        bg_filt = filtfilt(b, a, bg_filt)
    bg_win = bg_filt[time_zero_idx: time_zero_idx + n_win]
    if len(bg_win) < n_win:
        bg_win = np.pad(bg_win, (0, n_win - len(bg_win)))

    post_bgr = pre_bgr_full - bg_win

    # ── Step 5: Hilbert envelopes ─────────────────────────────────────────────
    env_pre  = np.abs(_hilbert(pre_bgr_full))
    env_post = np.abs(_hilbert(post_bgr))

    # ── Step 6: Feature grids (7×10 / 6×10 for H) ────────────────────────────
    n_target = 70
    def resamp(arr):
        x_old = np.linspace(0, 1, len(arr))
        x_new = np.linspace(0, 1, n_target)
        return np.interp(x_new, x_old, arr)

    st_grid = resamp(post_bgr).reshape(7, 10)
    h_grid  = resamp(env_pre)[:60].reshape(6, 10)
    ah_grid = resamp(env_post).reshape(7, 10)

    # ── Figure layout ─────────────────────────────────────────────────────────
    fig = plt.figure(figsize=(16, 14))
    gs = gridspec.GridSpec(3, 2, figure=fig, hspace=0.45, wspace=0.35)

    BLUE, ORANGE, GREEN, RED = '#2196F3', '#FF9800', '#4CAF50', '#F44336'
    t_win_abs = t_win + time_zero_idx * dt_ns   # absolute ns of window

    # ── Panel 1: raw signal ───────────────────────────────────────────────────
    ax1 = fig.add_subplot(gs[0, 0])
    ax1.plot(t_full, step1 / 1e3, color=BLUE, lw=0.8)
    ax1.axvspan(t_win_abs[0], t_win_abs[-1], alpha=0.15, color=ORANGE,
                label='7 ns window')
    ax1.axvline(peak_idx * dt_ns, color=RED, lw=1.2, ls='--',
                label=f'Direct wave peak (t={peak_idx*dt_ns:.1f} ns)')
    ax1.set_xlabel('Time (ns)')
    ax1.set_ylabel('Amplitude (×10³ ADC)')
    ax1.set_title('Step 1 — Raw DZT signal\n(full 50 ns trace, ADC counts)')
    ax1.legend(fontsize=8)

    # ── Panel 2: after normalize + dewow, window shown ───────────────────────
    ax2 = fig.add_subplot(gs[0, 1])
    ax2.plot(t_full, step2, color=BLUE, lw=0.8, label='Norm + dewow + bandpass')
    ax2.axvspan(t_win_abs[0], t_win_abs[-1], alpha=0.20, color=ORANGE)
    ax2.axvline(peak_idx * dt_ns, color=RED, lw=1.2, ls='--', label='Direct wave')
    # arrow showing backward shift
    ax2.annotate('', xy=(t_win_abs[0], 0.5),
                 xytext=(peak_idx * dt_ns, 0.5),
                 arrowprops=dict(arrowstyle='<->', color=GREEN, lw=1.5))
    ax2.text((t_win_abs[0] + peak_idx * dt_ns) / 2, 0.58,
             f'←  {n_shift} samp\n    (3 ns)', ha='center', fontsize=8, color=GREEN)
    ax2.set_xlabel('Time (ns)')
    ax2.set_ylabel('Normalised amplitude')
    ax2.set_title(f'Step 2-3 — Normalize & backward shift\n'
                  f'Window starts {n_shift} samples BEFORE direct wave')
    ax2.legend(fontsize=8)
    ax2.set_ylim(-1.2, 1.2)

    # ── Panel 3: pre-BGR windowed signal ─────────────────────────────────────
    ax3 = fig.add_subplot(gs[1, 0])
    ax3.plot(t_win, pre_bgr_full, color=BLUE, lw=1.0, label='Signal (pre-BGR)')
    ax3.plot(t_win, env_pre, color=RED, lw=1.2, ls='--', label='Hilbert envelope (H source)')
    direct_in_win = (peak_idx - time_zero_idx) * dt_ns
    ax3.axvline(direct_in_win, color=RED, lw=1.0, alpha=0.5, ls=':')
    ax3.text(direct_in_win + 0.1, env_pre.max() * 0.9,
             f'Direct wave\n@ sample {peak_idx - time_zero_idx}',
             fontsize=8, color=RED)
    ax3.set_xlabel('Time in window (ns)')
    ax3.set_ylabel('Normalised amplitude')
    ax3.set_title('Step 3 — Pre-BGR windowed signal (7 ns)\n'
                  'Direct wave is INSIDE the window — source of H grid')
    ax3.legend(fontsize=8)

    # ── Panel 4: post-BGR windowed signal ─────────────────────────────────────
    ax4 = fig.add_subplot(gs[1, 1])
    ax4.plot(t_win, post_bgr, color=ORANGE, lw=1.0, label='Signal (post-BGR)')
    ax4.plot(t_win, env_post, color=GREEN, lw=1.2, ls='--', label='Hilbert envelope (AH source)')
    ax4.axvline(direct_in_win, color=RED, lw=1.0, alpha=0.4, ls=':',
                label='Former direct wave position')
    ax4.set_xlabel('Time in window (ns)')
    ax4.set_ylabel('Normalised amplitude')
    ax4.set_title('Step 4-5 — After BGR + Hilbert envelope (AH)\n'
                  'Direct wave removed; subsurface reflections remain')
    ax4.legend(fontsize=8)

    # ── Panel 5: envelope comparison ─────────────────────────────────────────
    ax5 = fig.add_subplot(gs[2, 0])
    ax5.plot(t_win, env_pre, color=RED, lw=1.2, label='Pre-BGR envelope  →  H grid (rows 0-5)')
    ax5.plot(t_win, env_post, color=GREEN, lw=1.2, label='Post-BGR envelope →  AH grid (rows 0-6)')
    ax5.axvspan(0, 60 * dt_ns, alpha=0.08, color=RED, label='H grid coverage (6 ns)')
    ax5.axvline(direct_in_win, color=RED, lw=1.0, alpha=0.4, ls=':')
    ax5.set_xlabel('Time in window (ns)')
    ax5.set_ylabel('Envelope amplitude')
    ax5.set_title('Envelope comparison\nPre-BGR (H): includes direct wave  |  '
                  'Post-BGR (AH): subsurface only')
    ax5.legend(fontsize=8)
    peak_ratio = env_pre.max() / (env_post.max() + 1e-12)
    ax5.text(0.98, 0.95, f'Pre/post peak ratio: {peak_ratio:.1f}×',
             transform=ax5.transAxes, ha='right', va='top', fontsize=8,
             bbox=dict(boxstyle='round', fc='wheat', alpha=0.7))

    # ── Panel 6: the three feature grids ─────────────────────────────────────
    ax6 = fig.add_subplot(gs[2, 1])
    ax6.axis('off')

    # Draw three small grid images side by side
    gs6 = gridspec.GridSpecFromSubplotSpec(1, 3, subplot_spec=gs[2, 1],
                                           wspace=0.35)
    for gi, (arr, label, cmap, vbounds) in enumerate([
        (st_grid,  'ST  (7×10)\nPost-BGR signal',   'RdBu',  None),
        (h_grid,   'H   (6×10)\nPre-BGR envelope',  'hot',   (0, 1.1)),
        (ah_grid,  'AH  (7×10)\nPost-BGR envelope', 'hot',   (0, 0.5)),
    ]):
        axi = fig.add_subplot(gs6[gi])
        kw = dict(aspect='auto', origin='upper')
        if vbounds:
            kw['vmin'], kw['vmax'] = vbounds
        im = axi.imshow(arr, cmap=cmap, **kw)
        axi.set_title(label, fontsize=8)
        axi.set_xlabel('Col (0-9)', fontsize=7)
        axi.set_ylabel('Row', fontsize=7)
        axi.tick_params(labelsize=7)
        plt.colorbar(im, ax=axi, shrink=0.7, pad=0.02)
        # Cross out removed cells
        for (r, c) in _VIVANCO_DROP_CELLS:
            if r < arr.shape[0]:
                axi.add_patch(plt.Rectangle((c - 0.5, r - 0.5), 1, 1,
                                            fill=False, edgecolor='cyan',
                                            lw=1.5, ls='--'))

    fig.suptitle(
        f'Rojas-Vivanco (2025) pipeline — step-by-step on trace {trace_idx}\n'
        f'{dzt_path.name}  |  dt={dt*1e9:.4f} ns  |  BGR window={bgr_window} traces',
        fontsize=11, y=1.01
    )
    out_png.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_png, dpi=dpi, bbox_inches='tight')
    plt.close(fig)
    logger.info(f'Pipeline step-by-step plot saved -> {out_png}')


def apply_vivanco_model_to_dzt(
    dzt_path: Path,
    model_pkl: Path,
    out_png: Path,
    n_bscan: int = 500,
    bgr_window: int = 100,
    dpi: int = 150,
) -> dict:
    """Apply the Rojas-Vivanco (2025) XGBoost fouling classifier to EFE DZT traces.

    Loads a DZT file, applies the Vivanco preprocessing pipeline, extracts the
    262-feature schema, runs the pre-trained XGBoost model, and produces a
    two-panel figure:
      - Panel 1: processed envelope B-scan (7 ns window)
      - Panel 2: predicted fouling class along the trace index

    Args:
        dzt_path:   Path to EFE DZT file.
        model_pkl:  Path to serialized XGBoost model (.pkl).
        out_png:    Output PNG path.
        n_bscan:    Number of traces to process (first n_bscan traces).
        bgr_window: BGR rolling-window width in traces.
        dpi:        Figure resolution.

    Returns:
        dict with keys ``predictions``, ``labels``, ``feat_matrix``.

    Reference:
        Rojas-Vivanco et al. (2025) Transportation Geotechnics 55, 101701.
    """
    from src.vivanco_pipeline import predict_dzt_fouling

    logger.info(f'Applying Vivanco model to {dzt_path} ...')
    result = predict_dzt_fouling(dzt_path, model_pkl,
                                 n_bscan=n_bscan, bgr_window=bgr_window)
    preds      = result['predictions']
    labels     = result['labels']
    X          = result['feat_matrix']
    processed  = result['processed']
    envelopes  = result['envelopes']
    dt         = result['dt']

    # Plot
    n_tr, n_win = processed.shape
    t_win = np.arange(n_win) * dt * 1e9
    env_bscan = envelopes

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8),
                                   gridspec_kw={'height_ratios': [3, 1]})
    im = ax1.imshow(env_bscan.T, aspect='auto', cmap='hot',
                    vmin=0, vmax=0.5,
                    extent=[0, n_tr, t_win[-1], t_win[0]])
    ax1.set_xlabel('Trace index')
    ax1.set_ylabel('Time (ns)')
    ax1.set_title('Vivanco-processed envelope B-scan (7 ns window)')
    plt.colorbar(im, ax=ax1, shrink=0.8, label='Norm. envelope')

    # Fouling class along track
    fouling_order = ['C', 'MC', 'MF', 'F', 'HF']
    palette = {'C': '#2196F3', 'MC': '#4CAF50', 'MF': '#FFC107', 'F': '#FF5722', 'HF': '#9C27B0'}
    label_y = [fouling_order.index(l) if l in fouling_order else 2 for l in labels]
    colors = [palette.get(l, 'grey') for l in labels]
    ax2.scatter(range(n_tr), label_y, c=colors, s=8, zorder=2)
    ax2.set_yticks(range(len(fouling_order)))
    ax2.set_yticklabels(fouling_order)
    ax2.set_xlabel('Trace index')
    ax2.set_ylabel('Fouling class')
    ax2.set_title('XGBoost prediction (Rojas-Vivanco 2025 model)')
    ax2.grid(axis='y', alpha=0.3)

    fig.suptitle(
        f'Vivanco model applied to {dzt_path.name}\n'
        f'BGR={bgr_window} traces | {n_tr} traces processed',
        fontsize=10
    )
    fig.tight_layout()
    out_png.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_png, dpi=dpi, bbox_inches='tight')
    plt.close(fig)
    logger.info(f'Prediction plot saved -> {out_png}')

    return {'predictions': preds, 'labels': labels, 'feat_matrix': X}


# apply_agc_to_h5 and stitch_dzt_files moved to src.dzt_io (2026-07-02,
# debt D12: processing does not belong in the visualizer). Re-exported here
# so the CLI and existing importers keep working.
from src.dzt_io import apply_agc_to_h5, stitch_dzt_files  # noqa: F401,E402


def plot_bscan_h5(
    h5_path: Path,
    out_png: Path,
    max_time_ns: float = 25.0,
    n_display: int = 3000,
    clip_pct: float = 98.0,
    cmap: str = 'gray',
    contours: bool = False,
    n_contour_levels: int = 4,
    dpi: int = 200,
) -> None:
    """Plot the full EFE B-scan from the stitched HDF5 archive.

    Reads the HDF5 produced by :func:`stitch_dzt_files`, subsamples traces
    to ``n_display`` columns for display efficiency, and saves a radargram
    with x-axis in km and y-axis in two-way travel time (ns).

    Args:
        h5_path:     Path to the stitched HDF5 (output of stitch_dzt_files).
        out_png:     Output PNG path.
        max_time_ns: Depth of the displayed window in ns (default 25 ns).
        n_display:   Number of trace columns to render (downsampled, default 3000).
        clip_pct:    Amplitude percentile used for colour clipping (default 98).
        cmap:        Matplotlib colormap name (default 'gray').
        dpi:         Output resolution.
    """
    import h5py

    logger.info(f'Reading {h5_path} ...')
    with h5py.File(h5_path, 'r') as f:
        dt_ns   = float(f.attrs['dt_ns'])
        n_tr    = int(f.attrs['n_traces'])
        n_samp  = int(f.attrs['n_samples'])
        pk_m    = f['pk_m'][:]          # (n_tr,)
        seg_idx = f['segment_idx'][:]   # (n_tr,)
        seg_names = [s.decode() if isinstance(s, bytes) else s
                     for s in f['segments'][:]]

        # ── Subsample indices for display ─────────────────────────────────────
        step = max(1, n_tr // n_display)
        idx  = np.arange(0, n_tr, step)
        logger.info(f'Loading {len(idx)} / {n_tr} traces (every {step}th) ...')
        bscan_disp = f['traces'][idx, :]   # (n_display, n_samp)

    pk_disp  = pk_m[idx] / 1e3     # km
    seg_disp = seg_idx[idx]

    # ── Clip to time window ────────────────────────────────────────────────────
    n_win = min(n_samp, int(round(max_time_ns / dt_ns)))
    bscan_disp = bscan_disp[:, :n_win]   # (n_display, n_win)

    # ── Amplitude clipping ────────────────────────────────────────────────────
    vmax = float(np.percentile(np.abs(bscan_disp), clip_pct))
    vmin = -vmax

    # ── Segment boundary positions in km ──────────────────────────────────────
    seg_bounds_km = []
    for s in range(1, len(seg_names)):
        first = np.searchsorted(seg_disp, s)
        if first < len(pk_disp):
            seg_bounds_km.append(pk_disp[first])

    # ── Plot ──────────────────────────────────────────────────────────────────
    t_axis = np.arange(n_win) * dt_ns
    extent = [pk_disp[0], pk_disp[-1], t_axis[-1], t_axis[0]]

    fig, ax = plt.subplots(figsize=(20, 6))
    im = ax.imshow(
        bscan_disp.T,
        aspect='auto',
        cmap=cmap,
        vmin=vmin, vmax=vmax,
        extent=extent,
        interpolation='nearest',
    )
    # segment boundaries
    for km in seg_bounds_km:
        ax.axvline(km, color='red', lw=0.8, ls='--', alpha=0.7)
    # segment labels
    seg_label_km = []
    for s, name in enumerate(seg_names):
        mask = seg_disp == s
        if mask.any():
            mid_km = float(np.median(pk_disp[mask]))
            seg_label_km.append((mid_km, name.split('_PKC')[0].split('EFE_V1_')[-1]
                                         .replace('PKC', 'PK').replace('_', '+')))

    for km, label in seg_label_km:
        ax.text(km, t_axis[-1] * 0.05, label, ha='center', va='top',
                fontsize=7, color='red',
                bbox=dict(boxstyle='round,pad=0.2', fc='white', alpha=0.6, ec='none'))

    plt.colorbar(im, ax=ax, shrink=0.6, label='Amplitude (ADC counts)')
    ax.set_xlabel('Position (km)')
    ax.set_ylabel('Two-way travel time (ns)')
    ax.set_title(
        f'EFE Puerto Limache — full radargram  |  {n_tr:,} traces, '
        f'{pk_disp[0]:.2f}–{pk_disp[-1]:.2f} km  |  '
        f'displayed every {step}th trace'
    )
    # ── Contour overlay — peak-picked horizons ────────────────────────────────
    if contours:
        from scipy.signal import hilbert as _hilbert
        from scipy.ndimage import gaussian_filter1d, median_filter

        env = np.abs(np.apply_along_axis(_hilbert, 1, bscan_disp))
        # time axis in ns for each sample
        t_ns_axis = np.arange(n_win) * dt_ns

        # Define time windows to search for each horizon; tune to this dataset
        # Window edges are in ns from t=0
        windows = [
            (3.0,  8.0,  'cyan',   'Surface'),
            (8.0,  15.0, 'lime',   'Ballast base'),
            (15.0, max_time_ns, 'orange', 'Subgrade'),
        ]

        for t_lo, t_hi, colour, label in windows:
            s_lo = int(round(t_lo / dt_ns))
            s_hi = min(n_win, int(round(t_hi / dt_ns)))
            if s_lo >= s_hi:
                continue

            # For each trace find time of maximum envelope in the window
            sub = env[:, s_lo:s_hi]
            peak_sample = np.argmax(sub, axis=1) + s_lo   # (n_display,)
            peak_t = peak_sample * dt_ns                   # ns

            # Smooth the picked horizon spatially (median + gaussian)
            peak_t = median_filter(peak_t, size=15)
            peak_t = gaussian_filter1d(peak_t.astype(float), sigma=10)

            ax.plot(pk_disp, peak_t, color=colour, lw=1.2,
                    alpha=0.85, label=label)

        ax.legend(loc='lower right', fontsize=7, framealpha=0.6)

    out_png = Path(out_png)
    out_png.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_png, dpi=dpi, bbox_inches='tight')
    plt.close(fig)
    logger.info(f'B-scan saved -> {out_png}')


def plot_line_section_map(
    h5_path: Path,
    out_png: Path,
    n_bins: int = 420,
    coda_lo_ns: float = 5.0,
    coda_hi_ns: float = 16.0,
    n_sections: int | None = 12,
    dpi: int = 150,
) -> dict:
    """Map the railway line into quasi-homogeneous sections for per-section inversion.

    Bins the raw stitched line into ``n_bins`` blocks along PK; in each block the
    traces are first-break aligned and stacked into a high-SNR trace, from which
    three section descriptors are extracted vs PK:

        1. Ballast-base two-way time (ns after first break) — the dominant coda
           reflection; steps here mark trackbed structure changes (section edges).
        2. Coda reflectivity (windowed envelope energy / direct-wave energy).
        3. Intra-bin coherence (mean env-corr of traces to the bin stack) — high
           where the section is uniform, dips at transitions.

    Use RAW (non-AGC) input — AGC destroys coda coherence.

    Returns a dict of arrays (pk_km, base_ns, reflectivity, coherence, edges_km).
    """
    import h5py
    from scipy.signal import hilbert as _hilbert
    from src.signal_processing import _first_break_sample

    logger.info(f"Reading {h5_path} for section map ...")
    with h5py.File(h5_path, "r") as f:
        dt_ns = float(f.attrs["dt_ns"])
        n_tr  = int(f.attrs["n_traces"])
        pk    = f["pk_m"][:]
        seg   = f["segment_idx"][:]
        edges = np.linspace(0, n_tr, n_bins + 1).astype(int)

        s_lo = int(round(coda_lo_ns / dt_ns))
        s_hi = int(round(coda_hi_ns / dt_ns))

        pk_km, base_ns, refl, coher = [], [], [], []
        for b in range(n_bins):
            lo, hi = edges[b], edges[b + 1]
            if hi - lo < 5:
                continue
            block = f["traces"][lo:hi, :].astype(float)
            dt_n  = dt_ns
            fbs   = np.array([_first_break_sample(t, dt_n) for t in block])
            ref   = int(np.median(fbs))
            aligned = np.array([np.roll(block[i], ref - fbs[i]) for i in range(len(block))])
            stack = aligned.mean(axis=0)

            env = np.abs(_hilbert(stack))
            dw_peak = env[ref] if env[ref] > 0 else env.max()
            c0, c1 = ref + s_lo, min(len(env), ref + s_hi)
            if c1 <= c0:
                continue
            coda = env[c0:c1]
            base_ns.append((np.argmax(coda)) * dt_ns + coda_lo_ns)
            refl.append(np.sqrt(np.mean(coda ** 2)) / (dw_peak + 1e-30))

            # coherence: each trace's coda env vs stack coda env
            stack_coda = coda / (coda.max() + 1e-30)
            cs = []
            for i in range(0, len(aligned), max(1, len(aligned) // 30)):
                e = np.abs(_hilbert(aligned[i]))[c0:c1]
                e = e / (e.max() + 1e-30)
                if e.std() > 1e-9 and stack_coda.std() > 1e-9:
                    cs.append(np.corrcoef(e, stack_coda)[0, 1])
            coher.append(np.mean(cs) if cs else np.nan)
            pk_km.append(np.mean(pk[lo:hi]) / 1e3)

    pk_km   = np.array(pk_km)
    base_ns = np.array(base_ns)
    refl    = np.array(refl)
    coher   = np.array(coher)

    # ── Unsupervised section detection (contiguity-constrained clustering) ──────
    # Ward linkage on a 1-D chain graph → each cluster is a contiguous stretch of
    # track. No labels needed (none exist) — sections emerge from coda character.
    sect_edges_km, sect_labels = [], None
    if n_sections and len(pk_km) > n_sections:
        from sklearn.cluster import AgglomerativeClustering
        from scipy.sparse import diags
        feats = np.column_stack([base_ns, refl, coher])
        feats = np.nan_to_num(feats, nan=np.nanmedian(feats))
        feats = (feats - feats.mean(0)) / (feats.std(0) + 1e-9)
        m = len(feats)
        conn = diags([np.ones(m - 1), np.ones(m - 1)], [-1, 1])  # chain adjacency
        sect_labels = AgglomerativeClustering(
            n_clusters=n_sections, connectivity=conn, linkage="ward").fit_predict(feats)
        bnd = np.where(np.diff(sect_labels) != 0)[0]
        sect_edges_km = [(pk_km[i] + pk_km[i + 1]) / 2 for i in bnd]

    # segment boundaries (DZT files) in km
    seg_edges = [pk[np.searchsorted(seg, s)] / 1e3 for s in range(1, int(seg.max()) + 1)]

    fig, ax = plt.subplots(3, 1, figsize=(16, 9), sharex=True)
    ax[0].plot(pk_km, base_ns, color="#1f77b4", lw=0.9)
    ax[0].set_ylabel("Ballast-base\nTWT (ns)"); ax[0].grid(True, alpha=0.25)
    ax[0].set_title(f"Line section map — {h5_path.name}  ({n_bins} bins, "
                    f"~{(pk_km[-1]-pk_km[0])*1000/n_bins:.0f} m each)  [RAW stacked]")
    ax[1].plot(pk_km, refl, color="#2ca02c", lw=0.9)
    ax[1].set_ylabel("Coda\nreflectivity"); ax[1].grid(True, alpha=0.25)
    ax[2].plot(pk_km, coher, color="#d62728", lw=0.9)
    ax[2].set_ylabel("Intra-bin\ncoherence"); ax[2].set_ylim(0, 1.02)
    ax[2].set_xlabel("PK (km)"); ax[2].grid(True, alpha=0.25)
    for a in ax:
        for e in seg_edges:                                  # DZT file joins
            a.axvline(e, color="gray", ls="--", lw=0.8, alpha=0.5)
        for e in sect_edges_km:                              # detected sections
            a.axvline(e, color="green", lw=1.0, alpha=0.55)
    ax[0].axvline(20.0, color="orange", lw=1.2, alpha=0.8, label="PK 20 km (worked)")
    ax[0].plot([], [], color="green", lw=1.0, label=f"detected sections ({len(sect_edges_km)+1})")
    ax[0].plot([], [], color="gray", ls="--", lw=0.8, label="DZT joins")
    ax[0].legend(fontsize=8, loc="upper right", ncol=3)

    plt.tight_layout()
    out_png = Path(out_png); out_png.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_png, dpi=dpi, bbox_inches="tight")
    plt.close(fig)
    logger.info(f"Section map saved -> {out_png}")
    return {"pk_km": pk_km, "base_ns": base_ns,
            "reflectivity": refl, "coherence": coher,
            "seg_edges_km": seg_edges, "sect_edges_km": sect_edges_km,
            "sect_labels": sect_labels}


def compare_synthetic_vs_real(
    out_path: Path,
    h5_path: Path,
    out_png: Path,
    pk_m: float = 20000.0,
    max_time_ns: float = 25.0,
    layer_times_ns: list | None = None,
    layer_labels: list | None = None,
    dpi: int = 150,
    flip_synthetic: bool = False,
) -> None:
    """Compare a synthetic gprMax A-scan with the nearest real EFE trace.

    Loads the synthetic signal from a gprMax .out file, finds the real trace
    at the requested PK position in the stitched HDF5, aligns both traces by
    their direct-wave peak, and produces a 3-panel figure:

        1. Raw signals (independent amplitude axes)
        2. Peak-normalised signals overlaid
        3. Hilbert envelopes overlaid

    Args:
        out_path:       Path to the gprMax .out file.
        h5_path:        Path to the stitched EFE HDF5 (from stitch_dzt_files).
        out_png:        Output PNG path.
        pk_m:           Real-line position to extract (metres); nearest trace used.
        max_time_ns:    Time window to display (ns).
        layer_times_ns: Two-way times of layer interfaces for reference lines (ns).
        layer_labels:   Labels for each interface line.
        dpi:            Output resolution.
        flip_synthetic: Multiply the synthetic signal by -1 before plotting/
                        correlating. The real GSSI hardware and simulated Ez
                        have opposite polarity convention (validated in
                        project_validated_420mhz_pipeline: r=-0.005 unflipped
                        vs +0.913 flipped at 420MHz single-layer; reconfirmed
                        2026-06-30 on a 500MHz multi-layer packed-rock trace:
                        raw corr -0.881 unflipped vs +0.881 flipped). Does NOT
                        affect the envelope panel (sign-independent by
                        construction) but does flip panels 1 and 2.
    """
    import h5py
    from scipy.signal import hilbert as _hilbert

    layer_times_ns = layer_times_ns or []
    layer_labels   = layer_labels   or [f"Layer {i+1}" for i in range(len(layer_times_ns))]

    # ── Load synthetic trace ──────────────────────────────────────────────────
    logger.info(f'Reading synthetic .out: {out_path}')
    syn_data   = read_ascan(out_path, 'Ez')
    syn_sig    = syn_data['signal'].astype(float)
    syn_dt_ns  = syn_data['dt'] * 1e9
    syn_t      = syn_data['t_ns']
    if flip_synthetic:
        syn_sig = -syn_sig
        logger.info('  Synthetic signal polarity flipped (flip_synthetic=True)')

    # ── Load real trace ───────────────────────────────────────────────────────
    logger.info(f'Reading real H5: {h5_path} at PK={pk_m} m')
    with h5py.File(h5_path, 'r') as f:
        real_dt_ns  = float(f.attrs['dt_ns'])
        pk_arr      = f['pk_m'][:]
        idx_real    = int(np.argmin(np.abs(pk_arr - pk_m)))
        actual_pk   = pk_arr[idx_real]
        real_sig    = f['traces'][idx_real, :].astype(float)   # (n_samp,)

    n_real = real_sig.shape[0]
    real_t = np.arange(n_real) * real_dt_ns
    logger.info(f'  Nearest trace: PK={actual_pk:.1f} m (idx={idx_real})')

    # ── Clip to time window ───────────────────────────────────────────────────
    syn_n_win  = min(len(syn_t),  int(np.ceil(max_time_ns / syn_dt_ns)))
    real_n_win = min(len(real_t), int(np.ceil(max_time_ns / real_dt_ns)))
    syn_t    = syn_t[:syn_n_win];   syn_sig  = syn_sig[:syn_n_win]
    real_t   = real_t[:real_n_win]; real_sig = real_sig[:real_n_win]

    # ── Align by direct-wave peak ─────────────────────────────────────────────
    # Search for direct wave in first 8 ns; shift so peaks align at t=0
    search_ns = 8.0
    syn_search  = int(min(search_ns / syn_dt_ns,  len(syn_sig) - 1))
    real_search = int(min(search_ns / real_dt_ns, len(real_sig) - 1))

    syn_peak_t  = syn_t[np.argmax(np.abs(syn_sig[:syn_search]))]
    real_peak_t = real_t[np.argmax(np.abs(real_sig[:real_search]))]
    logger.info(f'  Direct-wave peaks: synthetic={syn_peak_t:.2f} ns, real={real_peak_t:.2f} ns')

    # Shift time axes so direct wave at t=0
    syn_t_aligned  = syn_t  - syn_peak_t
    real_t_aligned = real_t - real_peak_t

    # Reference lines relative to aligned axis
    layer_t_aligned = [t - real_peak_t for t in layer_times_ns]

    # ── Normalise ─────────────────────────────────────────────────────────────
    syn_norm  = syn_sig  / (np.max(np.abs(syn_sig))  + 1e-30)
    real_norm = real_sig / (np.max(np.abs(real_sig)) + 1e-30)

    # ── Envelopes ─────────────────────────────────────────────────────────────
    syn_env  = np.abs(_hilbert(syn_norm))
    real_env = np.abs(_hilbert(real_norm))

    # ── Plot ──────────────────────────────────────────────────────────────────
    xlim = (-2.0, max_time_ns - real_peak_t)

    fig, axes = plt.subplots(3, 1, figsize=(13, 12), sharex=False)
    colours = {'syn': '#d62728', 'real': '#1f77b4'}

    def _add_layer_lines(ax):
        for t_ref, lbl in zip(layer_t_aligned, layer_labels):
            ax.axvline(t_ref, color='gray', lw=0.8, ls='--', alpha=0.7)
            ax.text(t_ref + 0.1, ax.get_ylim()[1] * 0.92, lbl,
                    fontsize=7, color='gray', va='top')

    # Panel 1 — raw (dual y-axes)
    syn_label = 'Synthetic (V/m, flipped)' if flip_synthetic else 'Synthetic (V/m)'
    ax1 = axes[0]
    ax1r = ax1.twinx()
    ax1.plot(syn_t_aligned,  syn_sig,  lw=0.9, color=colours['syn'],  label=syn_label)
    ax1r.plot(real_t_aligned, real_sig, lw=0.9, color=colours['real'], alpha=0.8, label='Real (ADC counts)')
    ax1.set_ylabel('Synthetic amplitude (V/m)', color=colours['syn'])
    ax1r.set_ylabel('Real amplitude (ADC counts)', color=colours['real'])
    ax1.tick_params(axis='y', labelcolor=colours['syn'])
    ax1r.tick_params(axis='y', labelcolor=colours['real'])
    ax1.set_title(f'Raw amplitudes | PK={actual_pk/1e3:.2f} km (nearest to {pk_m/1e3:.2f} km)')
    ax1.set_xlim(xlim); ax1.grid(True, alpha=0.25)
    lines1 = ax1.get_lines() + ax1r.get_lines()
    labs1  = [l.get_label() for l in lines1]
    ax1.legend(lines1, labs1, loc='upper right', fontsize=8)

    # Panel 2 — normalised overlay
    ax2 = axes[1]
    syn_norm_label = 'Synthetic (norm., flipped)' if flip_synthetic else 'Synthetic (norm.)'
    ax2.plot(syn_t_aligned,  syn_norm,  lw=0.9, color=colours['syn'],  label=syn_norm_label)
    ax2.plot(real_t_aligned, real_norm, lw=0.9, color=colours['real'], alpha=0.8, label='Real (norm.)')
    ax2.set_ylabel('Normalised amplitude')
    ax2.set_title('Peak-normalised signals (direct wave aligned at t=0)')
    ax2.set_xlim(xlim); ax2.grid(True, alpha=0.25)
    ax2.legend(loc='upper right', fontsize=8)
    _add_layer_lines(ax2)

    # Panel 3 — Hilbert envelopes
    ax3 = axes[2]
    ax3.plot(syn_t_aligned,  syn_env,  lw=1.2, color=colours['syn'],  label='Synthetic envelope')
    ax3.plot(real_t_aligned, real_env, lw=1.2, color=colours['real'], alpha=0.8, label='Real envelope')
    ax3.fill_between(syn_t_aligned,  0, syn_env,  color=colours['syn'],  alpha=0.15)
    ax3.fill_between(real_t_aligned, 0, real_env, color=colours['real'], alpha=0.15)
    ax3.set_ylabel('Envelope amplitude')
    ax3.set_xlabel('Time relative to direct-wave peak (ns)')
    ax3.set_title('Hilbert envelopes')
    ax3.set_xlim(xlim); ax3.grid(True, alpha=0.25)
    ax3.legend(loc='upper right', fontsize=8)
    _add_layer_lines(ax3)

    plt.tight_layout()
    out_png = Path(out_png)
    out_png.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_png, dpi=dpi, bbox_inches='tight')
    plt.close(fig)
    logger.info(f'Comparison saved -> {out_png}')


def _first_break_ns(sig: np.ndarray, t_ns: np.ndarray, frac: float = 0.30,
                    search_ns: float = 8.0) -> float:
    """First-break time: first sample whose |amplitude| exceeds ``frac`` of the
    peak |amplitude| within ``search_ns``. A consistent picking convention that
    avoids the peak-vs-first-break quarter-period bias when comparing two traces.
    """
    dt_ns = t_ns[1] - t_ns[0]
    n = int(min(search_ns / dt_ns, len(sig) - 1))
    seg = np.abs(sig[:n])
    thr = frac * seg.max()
    idx = int(np.argmax(seg >= thr))
    return t_ns[idx]


def compare_synthetic_vs_real_bgsub(
    out_path: Path,
    background_out: Path,
    h5_path: Path,
    out_png: Path,
    pk_m: float = 20000.0,
    max_time_ns: float = 18.0,
    layer_times_ns: list | None = None,
    layer_labels: list | None = None,
    dpi: int = 150,
) -> dict:
    """Compare a synthetic A-scan to the real EFE trace with the direct wave
    removed by background subtraction, using a consistent first-break picking
    convention for both traces.

    The background ``.out`` is an identical-domain homogeneous half-space whose
    direct + surface arrival matches the layered model; subtracting it isolates
    the buried interface reflections (Annan 2003; standard GPR processing).

    Produces a 4-panel figure:
        1. Raw synthetic (norm) — direct wave dominant
        2. Background-subtracted synthetic — interface reflections exposed
        3. Hilbert envelopes: bg-subtracted synthetic vs real
        4. Raw overlay: synthetic vs real (first-break aligned)

    Returns a dict of measured first-break-aligned reflection times.

    Args:
        out_path:       Layered-model gprMax .out file.
        background_out: Homogeneous-reference gprMax .out (same domain/antenna).
        h5_path:        Stitched EFE HDF5 (from stitch_dzt_files).
        out_png:        Output PNG path.
        pk_m:           Real-line position to extract (metres); nearest used.
        max_time_ns:    Display window (ns); 18 ns to include deep formation event.
        layer_times_ns: Raw-B-scan two-way times of picked interfaces (ns).
        layer_labels:   Labels for the reference lines.
        dpi:            Output resolution.
    """
    import h5py
    from scipy.signal import hilbert as _hilbert, find_peaks

    layer_times_ns = layer_times_ns or []
    layer_labels   = layer_labels   or [f"Layer {i+1}" for i in range(len(layer_times_ns))]

    # ── Load synthetic + background ────────────────────────────────────────────
    logger.info(f'Reading synthetic: {out_path}')
    syn   = read_ascan(out_path, 'Ez')
    bg    = read_ascan(background_out, 'Ez')
    syn_sig   = syn['signal'].astype(float)
    bg_sig    = bg['signal'].astype(float)
    syn_dt_ns = syn['dt'] * 1e9
    syn_t     = syn['t_ns']

    # ── Load real trace ────────────────────────────────────────────────────────
    logger.info(f'Reading real H5: {h5_path} at PK={pk_m} m')
    with h5py.File(h5_path, 'r') as f:
        real_dt_ns = float(f.attrs['dt_ns'])
        pk_arr     = f['pk_m'][:]
        idx_real   = int(np.argmin(np.abs(pk_arr - pk_m)))
        actual_pk  = pk_arr[idx_real]
        real_sig   = f['traces'][idx_real, :].astype(float)
    real_t = np.arange(real_sig.shape[0]) * real_dt_ns
    logger.info(f'  Nearest trace: PK={actual_pk:.1f} m (idx={idx_real})')

    # ── Clip to display window ─────────────────────────────────────────────────
    def _clip(t, s, dt_ns):
        n = min(len(t), int(np.ceil(max_time_ns / dt_ns)))
        return t[:n], s[:n]
    syn_t,  syn_sig  = _clip(syn_t, syn_sig, syn_dt_ns)
    _,      bg_sig   = _clip(syn['t_ns'], bg_sig, syn_dt_ns)
    diff_sig = syn_sig - bg_sig[:len(syn_sig)]
    real_t, real_sig = _clip(real_t, real_sig, real_dt_ns)

    # ── Consistent first-break alignment (both traces, same convention) ────────
    sp = _first_break_ns(syn_sig,  syn_t)
    rp = _first_break_ns(real_sig, real_t)
    logger.info(f'  First-break: synthetic={sp:.2f} ns, real={rp:.2f} ns')
    syn_ta   = syn_t  - sp
    real_ta  = real_t - rp
    layer_ta = [t - rp for t in layer_times_ns]   # picks were on raw real DW

    # ── Normalise ──────────────────────────────────────────────────────────────
    norm = lambda s: s / (np.max(np.abs(s)) + 1e-30)
    syn_n, diff_n, real_n = norm(syn_sig), norm(diff_sig), norm(real_sig)
    env = lambda s: np.abs(_hilbert(s))

    # ── Measure reflection times in bg-subtracted synthetic (skip residual DW) ─
    skip = int(1.5 / syn_dt_ns)
    env_diff = env(diff_n)
    pks, _ = find_peaks(env_diff[skip:], height=0.08, distance=int(1.2 / syn_dt_ns))
    refl_times = [float(syn_ta[skip + p]) for p in pks]
    logger.info(f'  Bg-subtracted reflection times (first-break ref): '
                f'{[f"{t:.2f}" for t in refl_times]} ns')

    # ── Plot ───────────────────────────────────────────────────────────────────
    # Upper xlim uses the smaller first-break so BOTH aligned traces stay visible
    # (synthetic's deeper events would be clipped if we used the real first-break).
    xlim = (-2.0, max_time_ns - min(sp, rp))
    lc = {'syn': '#d62728', 'bg': '#2ca02c', 'real': '#1f77b4'}
    fig, ax = plt.subplots(4, 1, figsize=(13, 15))

    def vlines(a):
        for t, lbl in zip(layer_ta, layer_labels):
            a.axvline(t, color='gray', lw=0.8, ls='--', alpha=0.7)
            a.text(t + 0.1, a.get_ylim()[1] * 0.88, lbl, fontsize=7, color='gray')

    ax[0].plot(syn_ta, syn_n, lw=0.9, color=lc['syn'])
    ax[0].set_title('Raw synthetic (norm) — direct wave at t=0')
    ax[0].set_ylabel('Norm. amp'); ax[0].set_xlim(xlim); ax[0].grid(True, alpha=0.25)

    ax[1].plot(syn_ta, diff_n, lw=0.9, color=lc['bg'], label='synthetic − background')
    for t in refl_times:
        ax[1].axvline(t, color=lc['bg'], lw=0.6, ls=':', alpha=0.6)
    ax[1].set_title('Background subtracted — interface reflections exposed')
    ax[1].set_ylabel('Norm. amp'); ax[1].set_xlim(xlim); ax[1].grid(True, alpha=0.25)
    ax[1].legend(loc='upper right', fontsize=8); vlines(ax[1])

    ax[2].plot(syn_ta,  env(diff_n), lw=1.2, color=lc['bg'],   label='synthetic env (bg-sub)')
    ax[2].plot(real_ta, env(real_n), lw=1.2, color=lc['real'], label='real env', alpha=0.8)
    ax[2].fill_between(syn_ta,  0, env(diff_n), color=lc['bg'],   alpha=0.15)
    ax[2].fill_between(real_ta, 0, env(real_n), color=lc['real'], alpha=0.15)
    ax[2].set_title('Hilbert envelopes — bg-subtracted synthetic vs real')
    ax[2].set_ylabel('Envelope'); ax[2].set_xlim(xlim); ax[2].grid(True, alpha=0.25)
    ax[2].legend(loc='upper right', fontsize=8); vlines(ax[2])

    ax[3].plot(syn_ta,  syn_n,  lw=0.9, color=lc['syn'],  label='synthetic raw')
    ax[3].plot(real_ta, real_n, lw=0.9, color=lc['real'], label='real', alpha=0.8)
    ax[3].set_title('Raw overlay (first-break aligned)')
    ax[3].set_xlabel('Time relative to first break (ns)'); ax[3].set_ylabel('Norm. amp')
    ax[3].set_xlim(xlim); ax[3].grid(True, alpha=0.25)
    ax[3].legend(loc='upper right', fontsize=8); vlines(ax[3])

    plt.tight_layout()
    out_png = Path(out_png)
    out_png.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_png, dpi=dpi, bbox_inches='tight')
    plt.close(fig)
    logger.info(f'Bg-subtracted comparison saved -> {out_png}')
    return {'pk_actual': float(actual_pk), 'syn_first_break_ns': float(sp),
            'real_first_break_ns': float(rp), 'reflection_times_ns': refl_times}


def plot_coda_envelope_fit(
    syn_sig: np.ndarray, syn_dt: float,
    real_sig: np.ndarray, real_dt: float,
    out_png: Path,
    coda_lo_ns: float = 4.0,
    coda_hi_ns: float = 18.0,
    title: str = "",
    r: float | None = None,
    dpi: int = 150,
) -> None:
    """Verification plot for envelope-matching inversion: overlay the synthetic
    and real Hilbert envelopes on the coda objective grid (first-break aligned,
    peak-normalised in window) — the exact view the inversion objective scores.

    Args:
        syn_sig, syn_dt:   Best-fit synthetic A-scan + sample step (s).
        real_sig, real_dt: Real (raw, ideally stacked) A-scan + step (s).
        out_png:           Output PNG.
        coda_lo_ns/hi_ns:  Objective window (ns after first break).
        title:             Plot title (e.g. best params).
        r:                 Pearson r to annotate.
        dpi:               Resolution.
    """
    from scipy.signal import hilbert as _hilbert
    from src.signal_processing import _first_break_sample

    sdt, rdt = syn_dt * 1e9, real_dt * 1e9
    s_fb = _first_break_sample(syn_sig,  sdt) * sdt
    r_fb = _first_break_sample(real_sig, rdt) * rdt
    s_t = np.arange(len(syn_sig))  * sdt - s_fb
    r_t = np.arange(len(real_sig)) * rdt - r_fb

    s_env = np.abs(_hilbert(syn_sig));  r_env = np.abs(_hilbert(real_sig))
    grid = np.linspace(coda_lo_ns, coda_hi_ns, 300)
    s_i = np.interp(grid, s_t, s_env, left=0, right=0)
    r_i = np.interp(grid, r_t, r_env, left=0, right=0)
    s_i /= s_i.max() + 1e-30
    r_i /= r_i.max() + 1e-30

    fig, (a0, a1) = plt.subplots(2, 1, figsize=(12, 8))
    # full coda context
    m = (s_t >= -2) & (s_t <= coda_hi_ns + 2)
    a0.plot(s_t[m], s_env[m] / (s_env[m].max() + 1e-30), color="#d62728", lw=1.0, label="synthetic")
    mr = (r_t >= -2) & (r_t <= coda_hi_ns + 2)
    a0.plot(r_t[mr], r_env[mr] / (r_env[mr].max() + 1e-30), color="#1f77b4", lw=1.0, label="real (raw stack)", alpha=0.85)
    a0.axvspan(coda_lo_ns, coda_hi_ns, color="gold", alpha=0.12, label="objective window")
    a0.set_xlabel("Time after first break (ns)"); a0.set_ylabel("Norm. envelope")
    a0.set_title(title); a0.grid(True, alpha=0.25); a0.legend(fontsize=8)

    # objective-window detail (what r scores)
    a1.plot(grid, s_i, color="#d62728", lw=1.4, label="synthetic")
    a1.plot(grid, r_i, color="#1f77b4", lw=1.4, label="real", alpha=0.85)
    a1.fill_between(grid, s_i, r_i, color="gray", alpha=0.2, label="residual")
    rtxt = f"  (Pearson r = {r:+.3f})" if r is not None else ""
    a1.set_title(f"Objective window [{coda_lo_ns:g}, {coda_hi_ns:g}] ns{rtxt}")
    a1.set_xlabel("Time after first break (ns)"); a1.set_ylabel("Norm. envelope (window)")
    a1.grid(True, alpha=0.25); a1.legend(fontsize=8)

    plt.tight_layout()
    out_png = Path(out_png); out_png.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_png, dpi=dpi, bbox_inches="tight")
    plt.close(fig)
    logger.info(f"Coda envelope fit saved -> {out_png}")


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""B-scan (radargram) visualizer for real DZT files.

Applies the Mbubia-paper processing pipeline:
  1. Background removal  -- subtract mean trace per file (removes direct wave + ringing)
  2. Optional bandpass   -- 100-800 MHz Butterworth (GSSI hardware passband)
  3. Optional time gain  -- linear t-gain to compensate geometric spreading
  4. Radargram display   -- imshow with colour clip
  5. Coda RMS profile    -- spatial proxy for damping (related to MPM output)
  6. Optional MPM        -- Matrix Pencil Method on coda window per trace;
                            extracts dominant damping coefficients alpha_k (1/s)

Panoramic mode (multiple DZT files):
  Pass all DZT paths as positional args. Files are concatenated in order after
  per-file background removal. Use --decimate to reduce trace density.

Reference:
  Mbubia et al. 2024, J. Phys. Conf. Ser. 2887:012047

Usage:
    # Single-file B-scan around trace 77000
    python scripts/visualization/visualize_bscan.py D:/Codigo/Data/PKC011.DZT
        --start 74500 --count 5000 --bpf

    # Full Mbubia pipeline with MPM
    python scripts/visualization/visualize_bscan.py D:/Codigo/Data/PKC011.DZT
        --start 74500 --count 5000 --bpf --mpm

    # Panoramic B-scan -- all 3 DZT files, 1:100 decimation
    python scripts/visualization/visualize_bscan.py
        D:/Codigo/Data/PKC000*.DZT D:/Codigo/Data/PKC011*.DZT D:/Codigo/Data/PKC026*.DZT
        --bpf --decimate 100 --out experiments/2026-06-28/bscan_panorama.png
"""

import argparse
import re
import sys
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.signal import butter, filtfilt

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from src.dzt_io import read_dzt_traces
from src.signal_processing import mpm_decompose


_DZT_DEFAULT = (
    "D:/Codigo/Data/"
    "PUERTO-LIMACHE_20230726_EFE_V1_PKC011_020_PKF026_427_CENTRO_BRUTO.DZT"
)


# ── signal processing ─────────────────────────────────────────────────────────

def background_removal(traces: np.ndarray) -> np.ndarray:
    return traces - traces.mean(axis=0)[np.newaxis, :]


def bandpass(traces: np.ndarray, dt_ns: float,
             flo: float = 100e6, fhi: float = 800e6, order: int = 4) -> np.ndarray:
    fs  = 1.0 / (dt_ns * 1e-9)
    nyq = fs / 2.0
    b, a = butter(order, [flo / nyq, min(fhi / nyq, 0.999)], btype="bandpass")
    return filtfilt(b, a, traces, axis=1)


def time_gain(traces: np.ndarray, dt_ns: float) -> np.ndarray:
    t = np.arange(traces.shape[1]) * dt_ns
    return traces * t[np.newaxis, :]


def clip_percentile(img: np.ndarray, pct: float) -> tuple:
    v = np.percentile(np.abs(img), pct)
    return -v, v


def coda_rms(proc: np.ndarray, dt_ns: float,
             t0: float = 8.0, t1: float = 35.0) -> np.ndarray:
    n = proc.shape[1]
    i0 = max(0, int(t0 / dt_ns))
    i1 = min(n, int(t1 / dt_ns))
    return np.sqrt(np.mean(proc[:, i0:i1] ** 2, axis=1))


# ── MPM wrapper for B-scan spatial damping profile ───────────────────────────

def dominant_damping(y: np.ndarray, dt_s: float,
                     coda_start_ns: float = 8.0,
                     coda_end_ns: float = 35.0) -> float:
    """Residue-weighted mean alpha (1/s) for one trace's coda window.
    Delegates to src.signal_processing.mpm_decompose for the math.
    """
    dt_ns = dt_s * 1e9
    n     = len(y)
    i0    = max(0, int(coda_start_ns / dt_ns))
    i1    = min(n, int(coda_end_ns   / dt_ns))
    seg   = y[i0:i1]
    if len(seg) < 10:
        return np.nan

    seg = seg * np.hanning(len(seg))
    dec = mpm_decompose(seg, dt_s)
    valid = dec['valid_mask']
    if not np.any(valid):
        return np.nan

    alphas = dec['poles_s'].real[valid]       # 1/s
    res    = dec['residues'][valid]
    w      = np.abs(alphas)
    return float(np.average(alphas, weights=w)) if w.sum() > 0 else np.nan


# ── kilometre extraction ──────────────────────────────────────────────────────

def _parse_km(p: Path) -> float | None:
    m = re.search(r'PKC(\d+)_(\d+)', p.name, re.IGNORECASE)
    return (int(m.group(1)) + int(m.group(2)) / 1000.0) if m else None


# ── data loading ──────────────────────────────────────────────────────────────

def _process(traces: np.ndarray, dt_ns: float,
             do_bpf: bool, do_gain: bool) -> np.ndarray:
    p = background_removal(traces)
    if do_bpf:  p = bandpass(p, dt_ns)
    if do_gain: p = time_gain(p, dt_ns)
    return p


def load_single(dzt_path: Path, start: int, count: int,
                decimate: int, do_bpf: bool, do_gain: bool):
    print(f"[DZT] Loading {count:,} traces from #{start:,} ...")
    traces, meta = read_dzt_traces(dzt_path, start_trace=start, num_traces=count)
    dt_ns = meta["sample_interval_ns"]
    proc  = _process(traces, dt_ns, do_bpf, do_gain)

    idx = np.arange(0, proc.shape[0], decimate)
    proc = proc[idx]
    trace_idx = np.arange(start, start + len(idx) * decimate, decimate)

    n_tr, n_s = proc.shape
    print(f"      {n_tr:,} traces x {n_s} samples  dt={dt_ns:.4f} ns")
    return proc, trace_idx, dt_ns, None, None


def load_panorama(dzt_paths: list, decimate: int, do_bpf: bool, do_gain: bool):
    all_proc, all_rms_arr = [], []
    file_starts, file_kms = [], []
    offset = 0

    for p in dzt_paths:
        print(f"[DZT] {p.name}")
        traces, meta = read_dzt_traces(p)
        dt_ns = meta["sample_interval_ns"]
        n     = traces.shape[0]
        proc  = _process(traces, dt_ns, do_bpf, do_gain)

        idx   = np.arange(0, n, decimate)
        proc_d = proc[idx]
        print(f"      {n:,} traces -> {len(proc_d):,} decimated (1:{decimate})")

        file_starts.append(offset)
        file_kms.append(_parse_km(p))
        all_proc.append(proc_d)
        offset += len(proc_d)

    proc = np.vstack(all_proc)
    trace_idx = np.arange(proc.shape[0])
    _, meta0 = read_dzt_traces(dzt_paths[0], start_trace=0, num_traces=1)
    dt_ns = meta0["sample_interval_ns"]
    return proc, trace_idx, dt_ns, file_starts, file_kms


# ── plot helpers ──────────────────────────────────────────────────────────────

def _add_file_markers(ax, file_starts, file_kms, color="white", lw=0.8):
    for i, (fs, km) in enumerate(zip(file_starts, file_kms)):
        ax.axvline(fs, color=color, lw=lw, ls="--")
        if km is not None:
            ax.text(fs + 2, ax.get_ylim()[0] * 0.95,
                    f"km {km:.3f}", color=color, fontsize=6, va="bottom")


# ── main ─────────────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("dzt",         nargs="*", default=[_DZT_DEFAULT],
                    help="One or more DZT files (multiple = panoramic mode)")
    ap.add_argument("--start",     type=int,   default=74500,
                    help="First trace index (single-file only, default 74500)")
    ap.add_argument("--count",     type=int,   default=5000,
                    help="Number of traces (single-file only, default 5000)")
    ap.add_argument("--decimate",  type=int,   default=None,
                    help="Keep 1 trace every N (auto: 100 panoramic, 1 single)")
    ap.add_argument("--bpf",       action="store_true",
                    help="Apply 100-800 MHz bandpass filter")
    ap.add_argument("--gain",      action="store_true",
                    help="Apply linear time gain")
    ap.add_argument("--mpm",       action="store_true",
                    help="Run MPM damping analysis on each trace")
    ap.add_argument("--coda-start",type=float, default=8.0,
                    help="Coda window start ns (default 8)")
    ap.add_argument("--coda-end",  type=float, default=35.0,
                    help="Coda window end ns (default 35)")
    ap.add_argument("--clip-pct",  type=float, default=97.0,
                    help="Colour clip percentile (default 97)")
    ap.add_argument("--out",       default=None,
                    help="Output PNG path")
    args = ap.parse_args()

    dzt_paths = [Path(p) for p in args.dzt]
    for p in dzt_paths:
        if not p.exists():
            print(f"[ERR] File not found: {p}", file=sys.stderr)
            sys.exit(1)

    panoramic = len(dzt_paths) > 1
    decimate  = args.decimate if args.decimate is not None else (100 if panoramic else 1)

    steps = ["bg-removed" + ("/file" if panoramic else "")]
    if args.bpf:  steps.append("BPF 100-800 MHz")
    if args.gain: steps.append("t-gain")
    if decimate > 1: steps.append(f"decimate 1:{decimate}")
    proc_label = " + ".join(steps)

    if panoramic:
        print(f"[MODE] Panoramic ({len(dzt_paths)} files) -- {proc_label}")
        proc, trace_idx, dt_ns, file_starts, file_kms = load_panorama(
            dzt_paths, decimate, args.bpf, args.gain)
    else:
        proc, trace_idx, dt_ns, file_starts, file_kms = load_single(
            dzt_paths[0], args.start, args.count, decimate, args.bpf, args.gain)

    n_tr, n_s = proc.shape
    t_ns      = np.arange(n_s) * dt_ns
    rms       = coda_rms(proc, dt_ns, args.coda_start, args.coda_end)
    print(f"[PROC] {proc_label}  -> {n_tr:,} x {n_s}  coda {args.coda_start}-{args.coda_end} ns")

    # ── MPM (optional) ────────────────────────────────────────────────────────
    mpm_alpha = None
    if args.mpm:
        dt_s = dt_ns * 1e-9
        print(f"[MPM]  Running on {n_tr:,} traces ...")
        mpm_alpha = np.array([
            dominant_damping(proc[i], dt_s, args.coda_start, args.coda_end)
            for i in range(n_tr)
        ])
        valid = np.sum(np.isfinite(mpm_alpha)) / n_tr
        mean_a = np.nanmean(mpm_alpha)
        print(f"       Valid: {valid*100:.1f}%  mean alpha = {mean_a:.3e} 1/s")

    # ── figure ────────────────────────────────────────────────────────────────
    n_panels = 3 if args.mpm else 2
    fig_h    = max(8, 4 * n_panels)
    fig_w    = max(14, 20 if panoramic else 14)
    fig = plt.figure(figsize=(fig_w, fig_h))
    gs  = fig.add_gridspec(n_panels, 2, width_ratios=[15, 1],
                           hspace=0.35, wspace=0.05)

    vmin, vmax = clip_percentile(proc, args.clip_pct)
    extent = [trace_idx[0], trace_idx[-1], t_ns[-1], t_ns[0]]

    # ── Panel 1: radargram ────────────────────────────────────────────────────
    ax1 = fig.add_subplot(gs[0, 0])
    im1 = ax1.imshow(proc.T, aspect="auto", cmap="seismic",
                     vmin=vmin, vmax=vmax, extent=extent, interpolation="nearest")
    ax1.set_ylabel("Time (ns)")
    if panoramic:
        names = " | ".join(p.stem[-20:] for p in dzt_paths)
        ax1.set_title(f"Panoramic B-scan -- {names}\n{proc_label}")
        if file_starts:
            for fs, km in zip(file_starts, file_kms):
                ax1.axvline(fs, color="white", lw=0.8, ls="--")
                if km is not None:
                    ax1.text(fs + 1, t_ns[-1] * 0.97,
                             f"km {km:.1f}", color="white", fontsize=6, va="bottom")
    else:
        dzt_name = dzt_paths[0].stem
        ax1.set_title(
            f"B-scan -- {dzt_name}\n"
            f"{proc_label}  |  traces #{trace_idx[0]:,}-#{trace_idx[-1]:,}")
        ax1.axvline(77000, color="lime", lw=0.8, ls="--", label="tr#77000 (ref)")
        ax1.legend(fontsize=7, loc="lower right")
    ax1.axhline(args.coda_start, color="yellow", lw=0.5, ls=":")
    ax1.axhline(args.coda_end,   color="yellow", lw=0.5, ls=":")
    plt.colorbar(im1, cax=fig.add_subplot(gs[0, 1]), label="Amplitude (A/D counts)")

    # ── Panel 2: coda RMS ─────────────────────────────────────────────────────
    ax2 = fig.add_subplot(gs[1, 0])
    ax2.plot(trace_idx, rms, lw=0.5, color="steelblue")
    ax2.set_ylabel("RMS (A/D)")
    ax2.set_title(f"Coda RMS  ({args.coda_start}-{args.coda_end} ns)")
    ax2.grid(alpha=0.3)
    ax2.set_xlim(trace_idx[0], trace_idx[-1])
    if not panoramic:
        ax2.axvline(77000, color="green", lw=0.8, ls="--")
        ax2.set_xlabel("Trace index")
    else:
        if file_starts:
            for fs, km in zip(file_starts, file_kms):
                ax2.axvline(fs, color="gray", lw=0.6, ls="--")
                if km is not None:
                    ax2.text(fs + 1, ax2.get_ylim()[1] * 0.9,
                             f"km {km:.1f}", fontsize=6, color="gray")
        ax2.set_xlabel("Decimated trace index")
    fig.add_subplot(gs[1, 1]).set_visible(False)

    # ── Panel 3: MPM (optional) ───────────────────────────────────────────────
    if args.mpm and mpm_alpha is not None:
        from scipy.ndimage import median_filter
        ax3 = fig.add_subplot(gs[2, 0])
        alpha_us = mpm_alpha * 1e-6   # 1/s -> 1/us for readability
        ax3.scatter(trace_idx, alpha_us, s=1, c="crimson", alpha=0.4)
        med_size = max(11, n_tr // 200) | 1   # odd, ~0.5% of traces
        med = median_filter(
            np.where(np.isfinite(alpha_us), alpha_us, np.nanmedian(alpha_us)),
            size=med_size)
        ax3.plot(trace_idx, med, lw=1.5, color="darkred",
                 label=f"median ({med_size} tr)")
        ax3.axhline(0, color="k", lw=0.4, ls=":")
        ax3.set_ylabel("alpha (1/us)")
        ax3.set_title("MPM dominant damping in coda  (more negative = faster decay)")
        ax3.legend(fontsize=7)
        ax3.grid(alpha=0.3)
        ax3.set_xlim(trace_idx[0], trace_idx[-1])
        if not panoramic:
            ax3.axvline(77000, color="green", lw=0.8, ls="--")
            ax3.set_xlabel("Trace index")
        else:
            if file_starts:
                for fs in file_starts:
                    ax3.axvline(fs, color="gray", lw=0.6, ls="--")
            ax3.set_xlabel("Decimated trace index")
        fig.add_subplot(gs[2, 1]).set_visible(False)

    # ── save ──────────────────────────────────────────────────────────────────
    if args.out:
        out_path = Path(args.out)
    else:
        out_dir = Path("output_test")
        out_dir.mkdir(parents=True, exist_ok=True)
        if panoramic:
            tag = "bscan_panorama"
        else:
            tag = f"bscan_{dzt_paths[0].stem[-20:]}_tr{trace_idx[0]}-{trace_idx[-1]}"
        if args.bpf:  tag += "_bpf"
        if args.gain: tag += "_gain"
        if args.mpm:  tag += "_mpm"
        out_path = out_dir / f"{tag}.png"

    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"[OK]  Saved: {out_path}")


if __name__ == "__main__":
    main()

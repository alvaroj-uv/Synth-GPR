#!/usr/bin/env python3
"""
Compare two A-scans (synthetic vs real) with alignment and treatment.
Integrates aligned signal comparison into visualization pipeline.

Usage:
    python scripts/visualization/compare_scans.py synthetic.out real.DZT --trace 15000
    python scripts/visualization/compare_scans.py output_test/ballast_layer.out D:/Codigo/Data/*.DZT --trace 15000
"""

import sys
import argparse
import struct
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import h5py
from scipy.interpolate import interp1d

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))


def read_synthetic_out(out_path: Path, component: str = "Ez") -> tuple:
    """Read synthetic .out file."""
    with h5py.File(out_path, 'r') as f:
        signal = f[f'rxs/rx1/{component}'][()]
        dt = f.attrs.get('dt', 0.0)
    t_ns = np.arange(len(signal)) * dt * 1e9
    return signal, t_ns, dt * 1e9


def read_real_dzt(dzt_path: Path, trace_idx: int = 50) -> tuple:
    """Read real DZT trace."""
    HEADER_SIZE = 128 * 1024
    SAMPLES_PER_TRACE = 512
    BYTES_PER_SAMPLE = 4
    DT_NS = 50 / 511

    with open(dzt_path, 'rb') as f:
        f.seek(HEADER_SIZE + trace_idx * SAMPLES_PER_TRACE * BYTES_PER_SAMPLE)
        trace_bytes = f.read(SAMPLES_PER_TRACE * BYTES_PER_SAMPLE)
        signal = np.frombuffer(trace_bytes, dtype=np.int32, count=SAMPLES_PER_TRACE)
        signal = signal.astype(np.float64)

    signal = signal[2:]  # Drop indices 0-1
    t_ns = np.arange(len(signal)) * DT_NS
    return signal, t_ns, DT_NS


def normalize_peak(signal):
    """Normalize by peak amplitude."""
    peak = np.max(np.abs(signal))
    if peak == 0:
        return signal
    return signal / peak


def find_direct_wave_peak(signal: np.ndarray, search_end_idx: int = None) -> int:
    """Find the peak index of the direct wave."""
    if search_end_idx is None:
        search_end_idx = len(signal)
    search_region = signal[:search_end_idx]
    return np.argmax(np.abs(search_region))


def align_and_compare(syn_sig: np.ndarray, syn_t: np.ndarray, dt_syn: float,
                     real_sig: np.ndarray, real_t: np.ndarray, dt_real: float) -> dict:
    """
    Align direct waves and compute comparison metrics.

    Returns dict with:
    - peak_time_syn, peak_time_real, time_shift_ns
    - correlation
    - t_common, syn_norm, real_norm (for plotting)
    """

    # Polarity flip synthetic
    syn_flipped = -syn_sig

    # Find direct wave peaks
    search_ns = 20
    search_idx_syn = int(search_ns / dt_syn)
    search_idx_real = int(search_ns / dt_real)

    peak_idx_syn = find_direct_wave_peak(syn_flipped, min(search_idx_syn, len(syn_flipped)))
    peak_idx_real = find_direct_wave_peak(real_sig, min(search_idx_real, len(real_sig)))

    peak_time_syn = syn_t[peak_idx_syn]
    peak_time_real = real_t[peak_idx_real]

    # Align peaks
    time_shift_ns = peak_time_real - peak_time_syn
    syn_t_shifted = syn_t + time_shift_ns

    # Resample to common dt
    t_min = max(syn_t_shifted[0], real_t[0])
    t_max = min(syn_t_shifted[-1], real_t[-1])
    t_common = np.arange(int((t_max - t_min) / dt_real) + 1) * dt_real + t_min

    f_syn = interp1d(syn_t_shifted, syn_flipped, kind='cubic', bounds_error=False, fill_value=0)
    f_real = interp1d(real_t, real_sig, kind='cubic', bounds_error=False, fill_value=0)

    syn_common = f_syn(t_common)
    real_common = f_real(t_common)

    # Normalize
    syn_norm = normalize_peak(syn_common)
    real_norm = normalize_peak(real_common)

    # Correlate
    try:
        corr = np.corrcoef(syn_norm, real_norm)[0, 1]
    except:
        corr = np.nan

    return {
        'peak_time_syn': peak_time_syn,
        'peak_time_real': peak_time_real,
        'time_shift_ns': time_shift_ns,
        'correlation': corr,
        't_common': t_common,
        'syn_norm': syn_norm,
        'real_norm': real_norm,
    }


def main():
    ap = argparse.ArgumentParser(
        description="Compare two A-scans (synthetic vs real) with direct wave alignment and treatment",
        epilog="""
Examples:
  # Compare synthetic and real
  python scripts/visualization/compare_scans.py output_test/ballast_layer.out D:/Codigo/Data/*.DZT --trace 15000

  # Different trace
  python scripts/visualization/compare_scans.py output_test/rocks_420mhz_50cm.out D:/Codigo/Data/*.DZT --trace 5000
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    ap.add_argument("synthetic", type=Path, help="Synthetic .out file")
    ap.add_argument("real", type=Path, help="Real .DZT file")
    ap.add_argument("--trace", type=int, default=15000, help="DZT trace index (default: 15000)")
    ap.add_argument("--component", default="Ez", help="Field component for synthetic (default: Ez)")
    ap.add_argument("-o", "--output", type=Path, default=None, help="Output PNG path")

    args = ap.parse_args()

    # Validate
    if not args.synthetic.exists():
        print(f"[ERR] Synthetic file not found: {args.synthetic}")
        return 1
    if not args.real.exists():
        print(f"[ERR] Real file not found: {args.real}")
        return 1

    # Load
    print(f"[LOAD] Synthetic: {args.synthetic.name}")
    syn_sig, syn_t, dt_syn = read_synthetic_out(args.synthetic, args.component)

    print(f"[LOAD] Real: {args.real.name} (trace #{args.trace})")
    real_sig, real_t, dt_real = read_real_dzt(args.real, trace_idx=args.trace)

    print(f"  Synthetic: {len(syn_sig)} samples @ {dt_syn:.6f} ns/sample")
    print(f"  Real:      {len(real_sig)} samples @ {dt_real:.6f} ns/sample\n")

    # Align and compare
    result = align_and_compare(syn_sig, syn_t, dt_syn, real_sig, real_t, dt_real)

    print(f"[ALIGN] Direct wave peak alignment:")
    print(f"  Synthetic peak: {result['peak_time_syn']:.3f} ns")
    print(f"  Real peak:      {result['peak_time_real']:.3f} ns")
    print(f"  Time shift:     {result['time_shift_ns']:+.3f} ns")
    print(f"  Correlation:    {result['correlation']:+.6f}\n")

    # Plot
    fig = plt.figure(figsize=(16, 8))
    fig.patch.set_facecolor("#0f1117")
    gs = gridspec.GridSpec(2, 1, figure=fig, hspace=0.3, left=0.1, right=0.95, top=0.96, bottom=0.08)

    c_syn = "#00d9ff"
    c_real = "#ff6b35"

    # Top: Individual
    ax1 = fig.add_subplot(gs[0])
    ax1.set_facecolor("#1a1e2b")

    t = result['t_common']
    mask = t <= 50

    ax1.plot(t[mask], result['syn_norm'][mask], color=c_syn, lw=2, alpha=0.85,
            label="Synthetic (aligned, normalized)")
    ax1.plot(t[mask], result['real_norm'][mask], color=c_real, lw=2, alpha=0.85,
            label="Real (normalized)")
    ax1.axhline(0, color='#2a2f42', lw=0.8, linestyle='-', alpha=0.5)
    ax1.set_ylabel("Amplitude (normalized)", fontsize=11, color="#c8d0e0", fontweight='bold')
    ax1.set_title(f"Aligned Comparison (correlation: {result['correlation']:+.6f})",
                 fontsize=12, color="#c8d0e0", fontweight='bold')
    ax1.grid(True, color="#2a2f42", lw=0.5, alpha=0.3)
    ax1.legend(fontsize=10, facecolor='#1a1e2b', labelcolor='#c8d0e0', edgecolor='#2a2f42')
    ax1.tick_params(colors="#c8d0e0", labelsize=9)
    for spine in ax1.spines.values():
        spine.set_color("#2a2f42")

    # Bottom: Difference
    ax2 = fig.add_subplot(gs[1])
    ax2.set_facecolor("#1a1e2b")

    diff = result['syn_norm'][mask] - result['real_norm'][mask]
    ax2.fill_between(t[mask], diff, 0, alpha=0.5, color='yellow', label='Difference')
    ax2.plot(t[mask], diff, color='orange', lw=1.5, alpha=0.8)
    ax2.axhline(0, color='#2a2f42', lw=0.8, linestyle='-', alpha=0.5)
    ax2.set_xlabel("Time (ns)", fontsize=11, color="#c8d0e0", fontweight='bold')
    ax2.set_ylabel("Amplitude (diff)", fontsize=11, color="#c8d0e0", fontweight='bold')
    ax2.set_title("Residual Difference (syn - real)", fontsize=12, color="#c8d0e0", fontweight='bold')
    ax2.grid(True, color="#2a2f42", lw=0.5, alpha=0.3)
    ax2.legend(fontsize=10, facecolor='#1a1e2b', labelcolor='#c8d0e0', edgecolor='#2a2f42')
    ax2.tick_params(colors="#c8d0e0", labelsize=9)
    for spine in ax2.spines.values():
        spine.set_color("#2a2f42")

    # Title
    fig.suptitle(
        f"A-Scan Comparison: {args.synthetic.name} vs {args.real.name}\n"
        f"Time shift: {result['time_shift_ns']:+.2f} ns | Trace: #{args.trace}",
        color="#c8d0e0", fontsize=12, fontweight='bold', y=0.995
    )

    # Save
    if args.output:
        out_png = args.output.with_suffix('.png')
    else:
        out_png = Path('output_test') / f"compare_{args.synthetic.stem}_vs_{args.real.stem}.png"

    out_png.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_png, dpi=150, bbox_inches='tight', facecolor="#0f1117")
    print(f"[SAVE] {out_png}\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""
Compare synthetic (flipped) vs real DZT (optionally trimmed).
Align waveforms by time-shifting and see if they match.
"""

import sys
from pathlib import Path
import struct
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from scipy.interpolate import interp1d

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data_loader import read_ascan


def read_file(file_path: Path, trace_idx: int = 1000, component: str = "Ez") -> tuple:
    """Read A-scan from .out (synthetic) or .DZT (real) file."""
    suffix = file_path.suffix.upper()

    if suffix == ".OUT":
        data = read_ascan(file_path, component)
        signal = data['signal']
        dt = data['dt']
        t_ns = np.arange(len(signal)) * dt * 1e9
        meta_str = f"{file_path.stem}"
        return signal, t_ns, dt * 1e9, meta_str

    elif suffix == ".DZT" or suffix == ".DTZ":
        HEADER_SIZE = 128 * 1024
        SAMPLES_PER_TRACE = 512
        BYTES_PER_SAMPLE = 4
        DT_NS = 50 / 511

        with open(file_path, 'rb') as f:
            f.seek(HEADER_SIZE + trace_idx * SAMPLES_PER_TRACE * BYTES_PER_SAMPLE)
            trace_bytes = f.read(SAMPLES_PER_TRACE * BYTES_PER_SAMPLE)
            signal = np.frombuffer(trace_bytes, dtype=np.int32, count=SAMPLES_PER_TRACE)
            signal = signal.astype(np.float64)

        signal = signal[2:]  # Drop indices 0-1
        t_ns = np.arange(len(signal)) * DT_NS
        meta_str = f"DZT#{trace_idx}"
        return signal, t_ns, DT_NS, meta_str

    else:
        raise ValueError(f"Unsupported file type: {suffix}")


def normalize_peak(signal):
    """Normalize by peak amplitude."""
    peak = np.max(np.abs(signal))
    if peak == 0:
        return signal
    return signal / peak


def find_peak_time(signal, t_ns):
    """Find time of peak amplitude."""
    peak_idx = np.argmax(np.abs(signal))
    return t_ns[peak_idx]


def plot_comparison(syn_sig, syn_t, real_sig, real_t,
                   syn_flipped=False, real_trim_start_ns=None, out_png=None):
    """
    Plot 3 comparisons:
    1. Original vs Real (as-is)
    2. Flipped Synthetic vs Real (peak-aligned)
    3. Flipped Synthetic vs Real (trimmed)
    """

    # Normalize
    syn_norm = normalize_peak(syn_sig)
    real_norm = normalize_peak(real_sig)

    # Flip synthetic if requested
    if syn_flipped:
        syn_norm = syn_norm[::-1]

    # Compute peak times
    syn_peak_time = find_peak_time(syn_sig, syn_t)
    real_peak_time = find_peak_time(real_sig, real_t)

    print(f"\nPeak times:")
    print(f"  Synthetic peak: {syn_peak_time:.2f} ns")
    print(f"  Real DZT peak: {real_peak_time:.2f} ns")

    # Create figure
    fig = plt.figure(figsize=(16, 12))
    fig.patch.set_facecolor("#0f1117")
    gs = gridspec.GridSpec(3, 1, figure=fig, hspace=0.35, left=0.1, right=0.95, top=0.96, bottom=0.06)

    c_syn = "#00d4ff"
    c_real = "#ff6b35"

    # Row 1: Original (unflipped) vs Real
    ax1 = fig.add_subplot(gs[0])
    ax1.set_facecolor("#1a1e2b")
    ax1.plot(syn_t, normalize_peak(syn_sig), color=c_syn, lw=1.5, alpha=0.8, label="Synthetic (original, NOT flipped)")
    ax1.plot(real_t, real_norm, color=c_real, lw=1.5, alpha=0.7, label="Real DZT")
    ax1.axhline(0, color="#2a2f42", lw=0.8, linestyle='-', alpha=0.5)
    ax1.axvline(syn_peak_time, color=c_syn, lw=1.0, linestyle='--', alpha=0.5)
    ax1.axvline(real_peak_time, color=c_real, lw=1.0, linestyle='--', alpha=0.5)
    ax1.set_ylabel("Normalized Amplitude", fontsize=10, color="#c8d0e0", fontweight='bold')
    ax1.set_title("Row 1: Original (Unflipped) Synthetic vs Real", fontsize=11, color="#c8d0e0", fontweight='bold', pad=8)
    ax1.grid(True, color="#2a2f42", lw=0.5, alpha=0.4)
    ax1.legend(loc='upper right', fontsize=9, facecolor='#1a1e2b', labelcolor='#c8d0e0', edgecolor='#2a2f42')
    ax1.tick_params(colors="#c8d0e0", labelsize=9)
    for spine in ax1.spines.values():
        spine.set_color("#2a2f42")

    # Row 2: Flipped Synthetic (time-reversed) vs Real
    ax2 = fig.add_subplot(gs[1])
    ax2.set_facecolor("#1a1e2b")

    # Create time axis for flipped synthetic (mirror around 0)
    syn_t_flipped = -syn_t[::-1] + syn_t[-1]  # Flip time axis

    ax2.plot(syn_t_flipped, syn_norm, color=c_syn, lw=1.5, alpha=0.8, label="Synthetic (FLIPPED on time axis)")
    ax2.plot(real_t, real_norm, color=c_real, lw=1.5, alpha=0.7, label="Real DZT")
    ax2.axhline(0, color="#2a2f42", lw=0.8, linestyle='-', alpha=0.5)
    ax2.axvline(syn_peak_time, color=c_syn, lw=1.0, linestyle='--', alpha=0.5, label=f"Syn peak @ {syn_peak_time:.2f}ns")
    ax2.axvline(real_peak_time, color=c_real, lw=1.0, linestyle='--', alpha=0.5, label=f"Real peak @ {real_peak_time:.2f}ns")
    ax2.set_ylabel("Normalized Amplitude", fontsize=10, color="#c8d0e0", fontweight='bold')
    ax2.set_title("Row 2: Flipped Synthetic (Time-Reversed) vs Real", fontsize=11, color="#c8d0e0", fontweight='bold', pad=8)
    ax2.grid(True, color="#2a2f42", lw=0.5, alpha=0.4)
    ax2.legend(loc='upper right', fontsize=9, facecolor='#1a1e2b', labelcolor='#c8d0e0', edgecolor='#2a2f42')
    ax2.tick_params(colors="#c8d0e0", labelsize=9)
    for spine in ax2.spines.values():
        spine.set_color("#2a2f42")

    # Row 3: Flipped Synthetic vs Real (trimmed start)
    ax3 = fig.add_subplot(gs[2])
    ax3.set_facecolor("#1a1e2b")

    ax3.plot(syn_t_flipped, syn_norm, color=c_syn, lw=1.5, alpha=0.8, label="Synthetic (flipped)")

    if real_trim_start_ns is not None:
        # Trim real data
        trim_idx = np.argmin(np.abs(real_t - real_trim_start_ns))
        real_trimmed = real_sig[trim_idx:]
        real_t_trimmed = real_t[trim_idx:] - real_trim_start_ns  # Shift time to start at 0
        real_norm_trimmed = normalize_peak(real_trimmed)

        ax3.plot(real_t_trimmed, real_norm_trimmed, color=c_real, lw=1.5, alpha=0.7,
                label=f"Real DZT (trimmed from {real_trim_start_ns:.2f} ns)")
        title_suffix = f" [Real trimmed from {real_trim_start_ns:.2f} ns]"

        print(f"\nTrimmed real data:")
        print(f"  Start: {real_trim_start_ns:.2f} ns")
        print(f"  Samples removed: {trim_idx}")
        print(f"  Remaining samples: {len(real_trimmed)}")
    else:
        ax3.plot(real_t, real_norm, color=c_real, lw=1.5, alpha=0.7, label="Real DZT (full, no trim)")
        title_suffix = ""

    ax3.axhline(0, color="#2a2f42", lw=0.8, linestyle='-', alpha=0.5)
    ax3.set_xlabel("Time (ns)", fontsize=10, color="#c8d0e0", fontweight='bold')
    ax3.set_ylabel("Normalized Amplitude", fontsize=10, color="#c8d0e0", fontweight='bold')
    ax3.set_title(f"Row 3: Flipped Synthetic vs Real (Trimmed){title_suffix}", fontsize=11, color="#c8d0e0", fontweight='bold', pad=8)
    ax3.grid(True, color="#2a2f42", lw=0.5, alpha=0.4)
    ax3.legend(loc='upper right', fontsize=9, facecolor='#1a1e2b', labelcolor='#c8d0e0', edgecolor='#2a2f42')
    ax3.tick_params(colors="#c8d0e0", labelsize=9)
    for spine in ax3.spines.values():
        spine.set_color("#2a2f42")

    # Main title
    fig.suptitle(
        "Flipped Synthetic vs Real: Alignment Test",
        color="#c8d0e0", fontsize=13, fontweight='bold', y=0.995
    )

    # Save
    if out_png:
        out_png.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(out_png, dpi=150, bbox_inches='tight', facecolor="#0f1117")
        plt.close(fig)
        print(f"\n[OK] Comparison saved -> {out_png}")


def main():
    import argparse

    ap = argparse.ArgumentParser(
        description="Compare flipped synthetic vs real DZT (test time alignment)")
    ap.add_argument("synth", type=Path, help="Synthetic .out file")
    ap.add_argument("real", type=Path, help="Real .DZT file")
    ap.add_argument("--trace", type=int, default=1000, help="DZT trace index")
    ap.add_argument("--trim-real", type=float, default=None,
                   help="Trim real data starting from this time (ns)")
    ap.add_argument("-o", "--output", type=Path, default=None, help="Output PNG path")
    args = ap.parse_args()

    # Validate
    if not args.synth.exists():
        print(f"[ERR] Synthetic file not found: {args.synth}")
        sys.exit(1)
    if not args.real.exists():
        print(f"[ERR] Real file not found: {args.real}")
        sys.exit(1)

    # Load
    print(f"[READ] Synthetic: {args.synth.name}")
    syn_sig, syn_t, dt_syn, meta_syn = read_file(args.synth)

    print(f"[READ] Real DZT (trace #{args.trace}): {args.real.name}")
    real_sig, real_t, dt_real, meta_real = read_file(args.real, trace_idx=args.trace)

    print(f"\nSynthetic: {len(syn_sig)} samples, dt={dt_syn:.4f} ns, t_range=[{syn_t[0]:.2f}, {syn_t[-1]:.2f}] ns")
    print(f"Real DZT:  {len(real_sig)} samples, dt={dt_real:.4f} ns, t_range=[{real_t[0]:.2f}, {real_t[-1]:.2f}] ns")

    # Plot
    if args.output:
        out_png = args.output.with_suffix('.png')
    else:
        out_png = Path('output_test') / f"flipped_compare_{args.synth.stem}.png"

    plot_comparison(syn_sig, syn_t, real_sig, real_t,
                   syn_flipped=True, real_trim_start_ns=args.trim_real, out_png=out_png)

    print(f"\n{'='*70}")
    print("ANALYSIS")
    print(f"{'='*70}")
    print(f"Question: Does flipped synthetic match real when time-aligned?")
    print(f"\nIf YES:")
    print(f"  [MATCH] Waveforms are phase-opposite (polarity flip)")
    print(f"  [MATCH] Real trim point: {args.trim_real} ns removes the preprocessing artifact")
    print(f"  [MATCH] Synthetic and real measure same underlying physics")
    print(f"\nIf NO:")
    print(f"  [MISMATCH] Spectral/shape difference is fundamental (not just flip)")
    print(f"  [MISMATCH] Check antenna coupling, system response, preprocessing filters")
    print(f"  [MISMATCH] Consider field calibration pulse for reference")


if __name__ == "__main__":
    main()

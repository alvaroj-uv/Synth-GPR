#!/usr/bin/env python3
"""
Pad synthetic waveform with zeros to match real data first zero-crossing timing.
This absorbs the system delay (antenna coupling, propagation, etc.) as a time shift.
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


def find_first_zero_crossing(signal):
    """Find index of first zero-crossing (signal changes sign)."""
    sign_changes = np.diff(np.sign(signal))
    crossings = np.where(sign_changes != 0)[0]
    if len(crossings) > 0:
        return crossings[0]
    return 0


def find_first_significant_point(signal, threshold_pct=10):
    """Find index where signal first exceeds threshold of max amplitude."""
    max_amp = np.max(np.abs(signal))
    threshold = max_amp * (threshold_pct / 100.0)
    above_threshold = np.where(np.abs(signal) > threshold)[0]
    if len(above_threshold) > 0:
        return above_threshold[0]
    return 0


def normalize_peak(signal):
    """Normalize by peak amplitude."""
    peak = np.max(np.abs(signal))
    if peak == 0:
        return signal
    return signal / peak


def pad_synthetic(syn_sig, syn_t, dt_syn_ns, pad_ns):
    """
    Pad synthetic with zeros at the beginning.

    Args:
        syn_sig: signal array
        syn_t: time array
        dt_syn_ns: sampling interval (ns)
        pad_ns: how many nanoseconds to pad (will be rounded to nearest sample)

    Returns:
        padded_sig, padded_t
    """
    # Calculate number of samples to pad
    n_pad_samples = int(np.round(pad_ns / dt_syn_ns))

    # Create zero padding
    pad_array = np.zeros(n_pad_samples)

    # Pad signal
    padded_sig = np.concatenate([pad_array, syn_sig])

    # Create new time array
    t_min = -n_pad_samples * dt_syn_ns
    padded_t = np.arange(len(padded_sig)) * dt_syn_ns + t_min

    return padded_sig, padded_t, n_pad_samples


def plot_comparison(syn_sig, syn_t, real_sig, real_t,
                   pad_ns, n_pad_samples, out_png):
    """Create comparison: original vs padded vs real."""

    # Normalize
    syn_norm = normalize_peak(syn_sig)
    real_norm = normalize_peak(real_sig)

    # Pad synthetic
    syn_padded, syn_t_padded, _ = pad_synthetic(syn_sig, syn_t,
                                                 syn_t[1] - syn_t[0], pad_ns)
    syn_padded_norm = normalize_peak(syn_padded)

    # Find first significant points
    syn_first_idx = find_first_significant_point(syn_sig, threshold_pct=10)
    syn_first_time = syn_t[syn_first_idx]

    real_first_idx = find_first_significant_point(real_sig, threshold_pct=10)
    real_first_time = real_t[real_first_idx]

    syn_padded_first_time = syn_t_padded[n_pad_samples + syn_first_idx]

    # Create figure
    fig = plt.figure(figsize=(16, 12))
    fig.patch.set_facecolor("#0f1117")
    gs = gridspec.GridSpec(3, 1, figure=fig, hspace=0.35, left=0.1, right=0.95, top=0.96, bottom=0.06)

    c_syn = "#00d4ff"
    c_real = "#ff6b35"
    c_pad = "#00ff88"

    # Row 1: Original Synthetic vs Real
    ax1 = fig.add_subplot(gs[0])
    ax1.set_facecolor("#1a1e2b")
    ax1.plot(syn_t, syn_norm, color=c_syn, lw=1.5, alpha=0.8, label="Synthetic (original)")
    ax1.plot(real_t, real_norm, color=c_real, lw=1.5, alpha=0.7, label="Real DZT")
    ax1.axhline(0, color="#2a2f42", lw=0.8, linestyle='-', alpha=0.5)
    ax1.axvline(syn_first_time, color=c_syn, lw=1.2, linestyle='--', alpha=0.6,
               label=f"Syn first @ {syn_first_time:.2f} ns")
    ax1.axvline(real_first_time, color=c_real, lw=1.2, linestyle='--', alpha=0.6,
               label=f"Real first @ {real_first_time:.2f} ns")
    ax1.set_ylabel("Normalized Amplitude", fontsize=10, color="#c8d0e0", fontweight='bold')
    ax1.set_title(f"Row 1: Original Synthetic vs Real (Delay: {real_first_time - syn_first_time:.2f} ns)",
                 fontsize=11, color="#c8d0e0", fontweight='bold', pad=8)
    ax1.grid(True, color="#2a2f42", lw=0.5, alpha=0.4)
    ax1.legend(loc='upper right', fontsize=9, facecolor='#1a1e2b', labelcolor='#c8d0e0', edgecolor='#2a2f42')
    ax1.tick_params(colors="#c8d0e0", labelsize=9)
    for spine in ax1.spines.values():
        spine.set_color("#2a2f42")

    # Row 2: Padded Synthetic vs Real (aligned onset)
    ax2 = fig.add_subplot(gs[1])
    ax2.set_facecolor("#1a1e2b")
    ax2.plot(syn_t_padded, syn_padded_norm, color=c_pad, lw=1.5, alpha=0.85, label="Synthetic (PADDED with zeros)")
    ax2.plot(real_t, real_norm, color=c_real, lw=1.5, alpha=0.7, label="Real DZT")
    ax2.axhline(0, color="#2a2f42", lw=0.8, linestyle='-', alpha=0.5)
    ax2.axvline(syn_padded_first_time, color=c_pad, lw=1.2, linestyle='--', alpha=0.6,
               label=f"Syn padded first @ {syn_padded_first_time:.2f} ns")
    ax2.axvline(real_first_time, color=c_real, lw=1.2, linestyle='--', alpha=0.6,
               label=f"Real first @ {real_first_time:.2f} ns")
    ax2.set_ylabel("Normalized Amplitude", fontsize=10, color="#c8d0e0", fontweight='bold')
    ax2.set_title(f"Row 2: Padded Synthetic vs Real (Aligned Onset)",
                 fontsize=11, color="#c8d0e0", fontweight='bold', pad=8)
    ax2.grid(True, color="#2a2f42", lw=0.5, alpha=0.4)
    ax2.legend(loc='upper right', fontsize=9, facecolor='#1a1e2b', labelcolor='#c8d0e0', edgecolor='#2a2f42')
    ax2.set_xlim([0, 30])  # Zoom to first 30 ns to see alignment
    ax2.tick_params(colors="#c8d0e0", labelsize=9)
    for spine in ax2.spines.values():
        spine.set_color("#2a2f42")

    # Row 3: Overlay on common time grid (zoomed to first 30 ns)
    ax3 = fig.add_subplot(gs[2])
    ax3.set_facecolor("#1a1e2b")

    # Interpolate to common time grid
    t_min = max(syn_t_padded[0], real_t[0])
    t_max = min(syn_t_padded[-1], real_t[-1])
    t_common = np.linspace(t_min, t_max, 500)

    f_syn = interp1d(syn_t_padded, syn_padded_norm, kind='linear', bounds_error=False, fill_value=0)
    f_real = interp1d(real_t, real_norm, kind='linear', bounds_error=False, fill_value=0)

    syn_interp = f_syn(t_common)
    real_interp = f_real(t_common)

    ax3.plot(t_common, syn_interp, color=c_pad, lw=1.5, alpha=0.85, label="Synthetic (padded)")
    ax3.plot(t_common, real_interp, color=c_real, lw=1.5, alpha=0.7, label="Real DZT")
    ax3.fill_between(t_common, syn_interp, real_interp, alpha=0.2, color="orange",
                    label="Waveform difference")
    ax3.axhline(0, color="#2a2f42", lw=0.8, linestyle='-', alpha=0.5)

    ax3.set_xlabel("Time (ns)", fontsize=10, color="#c8d0e0", fontweight='bold')
    ax3.set_ylabel("Normalized Amplitude", fontsize=10, color="#c8d0e0", fontweight='bold')
    ax3.set_title("Row 3: Overlay on Common Time Grid (First 30 ns)",
                 fontsize=11, color="#c8d0e0", fontweight='bold', pad=8)
    ax3.grid(True, color="#2a2f42", lw=0.5, alpha=0.4)
    ax3.legend(loc='upper right', fontsize=9, facecolor='#1a1e2b', labelcolor='#c8d0e0', edgecolor='#2a2f42')
    ax3.set_xlim([0, 30])  # Zoom to first 30 ns
    ax3.tick_params(colors="#c8d0e0", labelsize=9)
    for spine in ax3.spines.values():
        spine.set_color("#2a2f42")

    # Main title
    fig.suptitle(
        f"Synthetic Padded with {pad_ns:.2f} ns of Zeros to Match Real Onset",
        color="#c8d0e0", fontsize=13, fontweight='bold', y=0.995
    )

    # Save
    out_png.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_png, dpi=150, bbox_inches='tight', facecolor="#0f1117")
    plt.close(fig)

    print(f"\n[OK] Padded comparison saved -> {out_png}")

    # Return metrics
    return {
        'delay_ns': real_first_time - syn_first_time,
        'n_pad_samples': n_pad_samples,
        'syn_first_time': syn_first_time,
        'syn_padded_first_time': syn_padded_first_time,
        'real_first_time': real_first_time,
    }


def main():
    import argparse

    ap = argparse.ArgumentParser(
        description="Pad synthetic with zeros to align first zero-crossing with real DZT")
    ap.add_argument("synth", type=Path, help="Synthetic .out file")
    ap.add_argument("real", type=Path, help="Real .DZT file")
    ap.add_argument("--trace", type=int, default=1000, help="DZT trace index")
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

    # Find first significant points
    syn_first_idx = find_first_significant_point(syn_sig, threshold_pct=10)
    real_first_idx = find_first_significant_point(real_sig, threshold_pct=10)

    syn_first_time = syn_t[syn_first_idx]
    real_first_time = real_t[real_first_idx]

    pad_ns = real_first_time - syn_first_time

    print(f"\nFirst significant point (10% of max):")
    print(f"  Synthetic: {syn_first_time:.2f} ns (sample {syn_first_idx})")
    print(f"  Real DZT:  {real_first_time:.2f} ns (sample {real_first_idx})")
    print(f"  Delay:     {pad_ns:.2f} ns")
    print(f"\nPadding synthetic with {pad_ns:.2f} ns ({int(np.round(pad_ns / dt_syn))} samples of zeros)...")

    # Plot
    if args.output:
        out_png = args.output.with_suffix('.png')
    else:
        out_png = Path('output_test') / f"padded_synthetic_{args.synth.stem}.png"

    metrics = plot_comparison(syn_sig, syn_t, real_sig, real_t, pad_ns,
                             int(np.round(pad_ns / dt_syn)), out_png)

    print(f"\n{'='*70}")
    print("PADDING SUMMARY")
    print(f"{'='*70}")
    print(f"Delay absorbed by padding: {metrics['delay_ns']:.2f} ns")
    print(f"Samples padded: {metrics['n_pad_samples']}")
    print(f"\nAfter padding:")
    print(f"  Synthetic first crossing @ {metrics['syn_padded_first_time']:.2f} ns")
    print(f"  Real first crossing      @ {metrics['real_first_time']:.2f} ns")
    print(f"  Alignment error: {abs(metrics['syn_padded_first_time'] - metrics['real_first_time']):.3f} ns")
    print(f"\nInterpretation:")
    print(f"  The {metrics['delay_ns']:.2f} ns delay represents:")
    print(f"    • Antenna coupling time")
    print(f"    • Propagation delay through ballast")
    print(f"    • System group delay")
    print(f"\nNext step: Check if padded waveforms match in shape (normalized overlay)")


if __name__ == "__main__":
    main()

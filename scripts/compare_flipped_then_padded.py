#!/usr/bin/env python3
"""
Complete analysis: Original, Flipped, and Flipped+Padded synthetic vs Real.
Flip FIRST (horizontally), then pad to match real onset time.
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
        return signal, t_ns, dt * 1e9

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
        return signal, t_ns, DT_NS

    else:
        raise ValueError(f"Unsupported file type: {suffix}")


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


def flip_synthetic(syn_sig, syn_t, dt_syn):
    """Flip synthetic horizontally (mirror on time axis)."""
    syn_flipped = syn_sig[::-1]
    # Rebuild time axis with same spacing, starting from 0
    t_flipped = np.arange(len(syn_flipped)) * dt_syn
    return syn_flipped, t_flipped


def pad_synthetic(syn_sig, dt_syn_ns, pad_ns):
    """Pad synthetic with zeros at the beginning (or trim if pad_ns is negative)."""
    n_pad_samples = int(np.round(pad_ns / dt_syn_ns))

    if n_pad_samples > 0:
        # Pad with zeros
        pad_array = np.zeros(n_pad_samples)
        padded_sig = np.concatenate([pad_array, syn_sig])
        t_min = -n_pad_samples * dt_syn_ns
        padded_t = np.arange(len(padded_sig)) * dt_syn_ns + t_min
    elif n_pad_samples < 0:
        # Negative padding: trim from the beginning (remove early samples)
        trim_idx = abs(n_pad_samples)
        padded_sig = syn_sig[trim_idx:]
        t_min = 0
        padded_t = np.arange(len(padded_sig)) * dt_syn_ns + t_min
    else:
        padded_sig = syn_sig
        padded_t = np.arange(len(syn_sig)) * dt_syn_ns

    return padded_sig, padded_t, n_pad_samples


def compute_correlation(sig1, t1, sig2, t2, t_min=0, t_max=30):
    """Compute correlation over time window (handles different time axes)."""
    # Find common time window
    idx1 = (t1 >= t_min) & (t1 <= t_max)
    idx2 = (t2 >= t_min) & (t2 <= t_max)

    if np.sum(idx1) < 2 or np.sum(idx2) < 2:
        return np.nan

    # Interpolate both to common fine grid
    t_common = np.linspace(max(t1[idx1][0], t2[idx2][0]),
                          min(t1[idx1][-1], t2[idx2][-1]), 500)

    f1 = interp1d(t1[idx1], sig1[idx1], kind='linear', bounds_error=False, fill_value=0)
    f2 = interp1d(t2[idx2], sig2[idx2], kind='linear', bounds_error=False, fill_value=0)

    s1 = f1(t_common)
    s2 = f2(t_common)

    # Normalize
    s1_norm = (s1 - np.mean(s1)) / (np.std(s1) + 1e-12)
    s2_norm = (s2 - np.mean(s2)) / (np.std(s2) + 1e-12)
    return np.corrcoef(s1_norm, s2_norm)[0, 1]


def plot_all_comparisons(syn_sig, syn_t, real_sig, real_t, pad_ns, dt_syn, out_png):
    """
    Create 4-row visualization:
    Row 1: Original synthetic vs Real
    Row 2: Flipped synthetic vs Real
    Row 3: Flipped+Padded synthetic vs Real
    Row 4: Overlay all three (flipped+padded, original+padded, real)
    """

    # Flip synthetic
    syn_flipped, syn_t_flipped = flip_synthetic(syn_sig, syn_t, dt_syn)

    # Pad both: original and flipped
    syn_padded, syn_t_padded, n_pad = pad_synthetic(syn_sig, dt_syn, pad_ns)
    syn_flipped_padded, syn_t_flipped_padded, _ = pad_synthetic(syn_flipped, dt_syn, pad_ns)

    # Normalize
    syn_norm = normalize_peak(syn_sig)
    syn_flipped_norm = normalize_peak(syn_flipped)
    syn_padded_norm = normalize_peak(syn_padded)
    syn_flipped_padded_norm = normalize_peak(syn_flipped_padded)
    real_norm = normalize_peak(real_sig)

    # Create figure
    fig = plt.figure(figsize=(16, 15))
    fig.patch.set_facecolor("#0f1117")
    gs = gridspec.GridSpec(4, 1, figure=fig, hspace=0.35, left=0.1, right=0.95, top=0.96, bottom=0.06)

    c_orig = "#00d4ff"
    c_flip = "#ffaa00"
    c_pad = "#00ff88"
    c_real = "#ff6b35"

    # Row 1: Original vs Real
    ax1 = fig.add_subplot(gs[0])
    ax1.set_facecolor("#1a1e2b")
    ax1.plot(syn_t, syn_norm, color=c_orig, lw=1.5, alpha=0.85, label="Synthetic (original)")
    ax1.plot(real_t, real_norm, color=c_real, lw=1.5, alpha=0.7, label="Real DZT")
    ax1.axhline(0, color="#2a2f42", lw=0.8, linestyle='-', alpha=0.5)
    ax1.set_ylabel("Normalized Amplitude", fontsize=10, color="#c8d0e0", fontweight='bold')
    ax1.set_title("Row 1: Original Synthetic vs Real",
                 fontsize=11, color="#c8d0e0", fontweight='bold', pad=8)
    ax1.grid(True, color="#2a2f42", lw=0.5, alpha=0.4)
    ax1.legend(loc='upper right', fontsize=9, facecolor='#1a1e2b', labelcolor='#c8d0e0', edgecolor='#2a2f42')
    ax1.set_xlim([0, 30])
    ax1.tick_params(colors="#c8d0e0", labelsize=9)
    for spine in ax1.spines.values():
        spine.set_color("#2a2f42")

    # Row 2: Flipped vs Real
    ax2 = fig.add_subplot(gs[1])
    ax2.set_facecolor("#1a1e2b")
    ax2.plot(syn_t_flipped, syn_flipped_norm, color=c_flip, lw=1.5, alpha=0.85, label="Synthetic (FLIPPED horizontally)")
    ax2.plot(real_t, real_norm, color=c_real, lw=1.5, alpha=0.7, label="Real DZT")
    ax2.axhline(0, color="#2a2f42", lw=0.8, linestyle='-', alpha=0.5)
    ax2.set_ylabel("Normalized Amplitude", fontsize=10, color="#c8d0e0", fontweight='bold')
    ax2.set_title("Row 2: Flipped Synthetic vs Real",
                 fontsize=11, color="#c8d0e0", fontweight='bold', pad=8)
    ax2.grid(True, color="#2a2f42", lw=0.5, alpha=0.4)
    ax2.legend(loc='upper right', fontsize=9, facecolor='#1a1e2b', labelcolor='#c8d0e0', edgecolor='#2a2f42')
    ax2.set_xlim([0, 30])
    ax2.tick_params(colors="#c8d0e0", labelsize=9)
    for spine in ax2.spines.values():
        spine.set_color("#2a2f42")

    # Row 3: Flipped+Padded vs Real
    ax3 = fig.add_subplot(gs[2])
    ax3.set_facecolor("#1a1e2b")
    ax3.plot(syn_t_flipped_padded, syn_flipped_padded_norm, color=c_pad, lw=1.5, alpha=0.85,
            label=f"Synthetic (flipped + padded +{pad_ns:.2f}ns)")
    ax3.plot(real_t, real_norm, color=c_real, lw=1.5, alpha=0.7, label="Real DZT")
    ax3.axhline(0, color="#2a2f42", lw=0.8, linestyle='-', alpha=0.5)
    ax3.set_ylabel("Normalized Amplitude", fontsize=10, color="#c8d0e0", fontweight='bold')
    ax3.set_title("Row 3: Flipped + Padded Synthetic vs Real (ONSET ALIGNED)",
                 fontsize=11, color="#c8d0e0", fontweight='bold', pad=8)
    ax3.grid(True, color="#2a2f42", lw=0.5, alpha=0.4)
    ax3.legend(loc='upper right', fontsize=9, facecolor='#1a1e2b', labelcolor='#c8d0e0', edgecolor='#2a2f42')
    ax3.set_xlim([0, 30])
    ax3.tick_params(colors="#c8d0e0", labelsize=9)
    for spine in ax3.spines.values():
        spine.set_color("#2a2f42")

    # Row 4: Overlay comparison (flipped+padded vs real)
    ax4 = fig.add_subplot(gs[3])
    ax4.set_facecolor("#1a1e2b")

    # Common time grid
    t_min = max(0, real_t[0])
    t_max = min(np.max(syn_t_flipped_padded), np.max(real_t))
    t_common = np.linspace(t_min, t_max, 1000)

    # Interpolate
    f_flip_pad = interp1d(syn_t_flipped_padded, syn_flipped_padded_norm, kind='linear',
                         bounds_error=False, fill_value=0)
    f_real = interp1d(real_t, real_norm, kind='linear', bounds_error=False, fill_value=0)

    flip_pad_interp = f_flip_pad(t_common)
    real_interp = f_real(t_common)

    # Compute correlation
    corr = compute_correlation(syn_flipped_padded_norm, syn_t_flipped_padded, real_norm, real_t)

    ax4.plot(t_common, flip_pad_interp, color=c_pad, lw=1.8, alpha=0.9, label="Synthetic (flipped+padded)")
    ax4.plot(t_common, real_interp, color=c_real, lw=1.8, alpha=0.8, label="Real DZT")
    ax4.fill_between(t_common, flip_pad_interp, real_interp, alpha=0.25, color="cyan",
                    label="Waveform difference")
    ax4.axhline(0, color="#2a2f42", lw=0.8, linestyle='-', alpha=0.5)

    ax4.set_xlabel("Time (ns)", fontsize=10, color="#c8d0e0", fontweight='bold')
    ax4.set_ylabel("Normalized Amplitude", fontsize=10, color="#c8d0e0", fontweight='bold')
    corr_str = f"{corr:.3f}" if not np.isnan(corr) else "N/A"
    ax4.set_title(f"Row 4: Overlay (Flipped+Padded vs Real) - Correlation: {corr_str}",
                 fontsize=11, color="#c8d0e0", fontweight='bold', pad=8)
    ax4.grid(True, color="#2a2f42", lw=0.5, alpha=0.4)
    ax4.legend(loc='upper right', fontsize=10, facecolor='#1a1e2b', labelcolor='#c8d0e0', edgecolor='#2a2f42')
    ax4.set_xlim([0, 30])
    ax4.tick_params(colors="#c8d0e0", labelsize=9)
    for spine in ax4.spines.values():
        spine.set_color("#2a2f42")

    # Main title
    fig.suptitle(
        f"Complete Analysis: Original, Flipped, and Flipped+Padded Synthetic vs Real",
        color="#c8d0e0", fontsize=13, fontweight='bold', y=0.995
    )

    # Save
    out_png.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_png, dpi=150, bbox_inches='tight', facecolor="#0f1117")
    plt.close(fig)

    print(f"\n[OK] Complete comparison saved -> {out_png}")

    return {
        'correlation': corr,
        'delay_ns': pad_ns,
        'n_pad_samples': n_pad,
    }


def main():
    import argparse

    ap = argparse.ArgumentParser(
        description="Complete analysis: flip synthetic horizontally, then pad, compare all vs real")
    ap.add_argument("synth", type=Path, help="Synthetic .out file")
    ap.add_argument("real", type=Path, help="Real .DZT file")
    ap.add_argument("--trace", type=int, default=1000, help="DZT trace index")
    ap.add_argument("--delay", type=float, default=None,
                   help="Padding delay (ns). If None, auto-detect from flipped signal")
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
    syn_sig, syn_t, dt_syn = read_file(args.synth)

    print(f"[READ] Real DZT (trace #{args.trace}): {args.real.name}")
    real_sig, real_t, dt_real = read_file(args.real, trace_idx=args.trace)

    print(f"\nSynthetic: {len(syn_sig)} samples, dt={dt_syn:.4f} ns, t_range=[{syn_t[0]:.2f}, {syn_t[-1]:.2f}] ns")
    print(f"Real DZT:  {len(real_sig)} samples, dt={dt_real:.4f} ns, t_range=[{real_t[0]:.2f}, {real_t[-1]:.2f}] ns")

    # Determine padding
    if args.delay is None:
        # For flipped synthetic, find first significant point of flipped signal
        syn_flipped, _ = flip_synthetic(syn_sig, syn_t, dt_syn)
        syn_flipped_first_idx = find_first_significant_point(syn_flipped, threshold_pct=10)
        syn_flipped_first_time = syn_t[syn_flipped_first_idx]

        real_first_idx = find_first_significant_point(real_sig, threshold_pct=10)
        real_first_time = real_t[real_first_idx]

        pad_ns = real_first_time - syn_flipped_first_time
        print(f"\n[AUTO] Flipped synthetic first significant point: {syn_flipped_first_time:.2f} ns")
        print(f"[AUTO] Real first significant point: {real_first_time:.2f} ns")
        print(f"[AUTO] Detected delay for padding: {pad_ns:.2f} ns")
    else:
        pad_ns = args.delay
        print(f"\n[USER] Using specified delay: {pad_ns:.2f} ns")

    # Plot
    if args.output:
        out_png = args.output.with_suffix('.png')
    else:
        out_png = Path('output_test') / f"flip_then_pad_{args.synth.stem}.png"

    metrics = plot_all_comparisons(syn_sig, syn_t, real_sig, real_t, pad_ns, dt_syn, out_png)

    print(f"\n{'='*70}")
    print("COMPLETE ANALYSIS SUMMARY")
    print(f"{'='*70}")
    print(f"\nStep 1: FLIP synthetic horizontally (mirror on time axis)")
    print(f"  -> Reverses the waveform in time")
    print(f"\nStep 2: PAD flipped synthetic by {metrics['delay_ns']:.2f} ns")
    print(f"  -> {metrics['n_pad_samples']} samples of zeros added")
    print(f"  -> Aligns onset with real DZT")
    print(f"\nCorrelation (flipped+padded vs real): {metrics['correlation']:.4f}")
    print(f"\nInterpretation:")

    if not np.isnan(metrics['correlation']):
        if metrics['correlation'] > 0.8:
            print(f"  [EXCELLENT] Very high correlation - waveforms match well!")
            print(f"  -> Flipped+padded synthetic represents the real system response")
        elif metrics['correlation'] > 0.6:
            print(f"  [GOOD] Good correlation - reasonable match with some differences")
            print(f"  -> Shapes are similar but have some structural differences")
        elif metrics['correlation'] > 0.4:
            print(f"  [MODERATE] Moderate correlation - partial overlap")
            print(f"  -> Some shape similarities, but also significant differences")
        else:
            print(f"  [LOW] Low correlation - shapes are quite different")
            print(f"  -> Flipping+padding alone can't reconcile the waveforms")
    else:
        print(f"  [ERROR] Could not compute correlation")

    print(f"\nConclusion:")
    print(f"  1. Time alignment (padding): {metrics['delay_ns']:.2f} ns system delay")
    print(f"  2. Polarity (flipping): Check correlation to see if helpful")
    print(f"  3. Shape difference: Remaining mismatch is due to damping/broadening")
    print(f"     -> Real system has more attenuation than free-space synthetic")


if __name__ == "__main__":
    main()

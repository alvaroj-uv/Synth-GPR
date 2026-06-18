#!/usr/bin/env python3
"""
Step 5: Flip extended synthetic horizontally (reverse time axis).
Compare flipped vs real to check if time-reversed waveform matches better.
"""

import sys
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data_loader import read_ascan


def read_extended_synthetic(file_path: Path, component: str = "Ez") -> tuple:
    """Read extended synthetic .out file from gprMax."""
    data = read_ascan(file_path, component)
    signal = data['signal']
    dt = data['dt']
    t_ns = np.arange(len(signal)) * dt * 1e9
    return signal, t_ns, dt * 1e9


def read_real_dzt(file_path: Path, trace_idx: int = 1000) -> tuple:
    """Read real DZT file."""
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


def normalize_peak(signal):
    """Normalize by peak amplitude."""
    peak = np.max(np.abs(signal))
    if peak == 0:
        return signal
    return signal / peak


def flip_horizontal(signal):
    """Flip signal amplitude-wise (multiply by -1)."""
    return signal * -1


def plot_flip_comparison(syn_sig, syn_t, dt_syn, syn_flipped, real_sig, real_t, dt_real, out_png):
    """
    Create 3-row comparison:
    Row 1: Original synthetic vs flipped synthetic
    Row 2: Flipped synthetic vs real (normalized)
    Row 3: Detailed early-time behavior
    """

    # Normalize
    syn_norm = normalize_peak(syn_sig)
    syn_flip_norm = normalize_peak(syn_flipped)
    real_norm = normalize_peak(real_sig)

    fig = plt.figure(figsize=(16, 14))
    fig.patch.set_facecolor("#0f1117")
    gs = gridspec.GridSpec(3, 1, figure=fig, hspace=0.35, left=0.1, right=0.95, top=0.95, bottom=0.08)

    c_syn_orig = "#00ff88"
    c_syn_flip = "#ff00ff"
    c_real = "#ff6b35"

    # Row 1: Original vs Flipped synthetic (raw)
    ax1 = fig.add_subplot(gs[0])
    ax1.set_facecolor("#1a1e2b")

    ax1.plot(syn_t, syn_sig, color=c_syn_orig, lw=2, alpha=0.85, label="Original")
    ax1.plot(syn_t, syn_flipped, color=c_syn_flip, lw=2, alpha=0.75, label="Flipped (time-reversed)")
    ax1.axhline(0, color="#2a2f42", lw=0.8, linestyle='-', alpha=0.5)
    ax1.fill_between(syn_t, syn_sig, 0, alpha=0.1, color=c_syn_orig)
    ax1.fill_between(syn_t, syn_flipped, 0, alpha=0.1, color=c_syn_flip)

    ax1.set_ylabel("Amplitude (V/m)", fontsize=10, color="#c8d0e0", fontweight='bold')
    ax1.set_title("Row 1: Original vs Flipped Synthetic (Raw V/m) - 0-50 ns",
                 fontsize=11, color="#c8d0e0", fontweight='bold', pad=10)
    ax1.grid(True, color="#2a2f42", lw=0.5, alpha=0.4)
    ax1.legend(loc='upper right', fontsize=10, facecolor='#1a1e2b', labelcolor='#c8d0e0', edgecolor='#2a2f42')
    ax1.tick_params(colors="#c8d0e0", labelsize=9)

    for spine in ax1.spines.values():
        spine.set_color("#2a2f42")

    # Row 2: Flipped synthetic vs Real (normalized overlay)
    ax2 = fig.add_subplot(gs[1])
    ax2.set_facecolor("#1a1e2b")

    ax2.plot(syn_t, syn_flip_norm, color=c_syn_flip, lw=2, alpha=0.85, label="Synthetic (flipped, normalized)")
    ax2.plot(real_t, real_norm, color=c_real, lw=2, alpha=0.75, label="Real DZT (normalized)")
    ax2.axhline(0, color="#2a2f42", lw=0.8, linestyle='-', alpha=0.5)

    ax2.set_ylabel("Normalized Amplitude", fontsize=10, color="#c8d0e0", fontweight='bold')
    ax2.set_title("Row 2: Flipped Synthetic vs Real - Shape Comparison (Normalized)",
                 fontsize=11, color="#c8d0e0", fontweight='bold', pad=10)
    ax2.grid(True, color="#2a2f42", lw=0.5, alpha=0.4)
    ax2.legend(loc='upper right', fontsize=10, facecolor='#1a1e2b', labelcolor='#c8d0e0', edgecolor='#2a2f42')
    ax2.tick_params(colors="#c8d0e0", labelsize=9)

    for spine in ax2.spines.values():
        spine.set_color("#2a2f42")

    # Row 3: Early-time detail (0-20 ns)
    ax3 = fig.add_subplot(gs[2])
    ax3.set_facecolor("#1a1e2b")

    t_min, t_max = 0, 20
    idx_syn = (syn_t >= t_min) & (syn_t <= t_max)
    idx_real = (real_t >= t_min) & (real_t <= t_max)

    ax3.plot(syn_t[idx_syn], syn_flip_norm[idx_syn], color=c_syn_flip, lw=2.5, alpha=0.9, label="Synthetic (flipped)")
    ax3.plot(real_t[idx_real], real_norm[idx_real], color=c_real, lw=2.5, alpha=0.85, label="Real")
    ax3.axhline(0, color="#2a2f42", lw=0.8, linestyle='-', alpha=0.5)

    ax3.set_xlabel("Time (ns)", fontsize=10, color="#c8d0e0", fontweight='bold')
    ax3.set_ylabel("Normalized Amplitude", fontsize=10, color="#c8d0e0", fontweight='bold')
    ax3.set_title("Row 3: Early-Time Detail (0-20 ns) - Flipped vs Real",
                 fontsize=11, color="#c8d0e0", fontweight='bold', pad=10)
    ax3.grid(True, color="#2a2f42", lw=0.5, alpha=0.4)
    ax3.legend(loc='upper right', fontsize=10, facecolor='#1a1e2b', labelcolor='#c8d0e0', edgecolor='#2a2f42')
    ax3.set_xlim([t_min, t_max])
    ax3.tick_params(colors="#c8d0e0", labelsize=9)

    for spine in ax3.spines.values():
        spine.set_color("#2a2f42")

    # Main title
    fig.suptitle(
        "Step 5: Flip Synthetic Horizontally (Time-Reversed)",
        color="#c8d0e0", fontsize=13, fontweight='bold', y=0.98
    )

    out_png.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_png, dpi=150, bbox_inches='tight', facecolor="#0f1117")
    plt.close(fig)

    print(f"\n[OK] Flip comparison saved -> {out_png}")


def compute_correlation(sig1, sig2):
    """Compute normalized cross-correlation at lag 0."""
    if len(sig1) != len(sig2):
        # Truncate to shorter length
        min_len = min(len(sig1), len(sig2))
        sig1 = sig1[:min_len]
        sig2 = sig2[:min_len]

    sig1_norm = (sig1 - np.mean(sig1)) / (np.std(sig1) + 1e-10)
    sig2_norm = (sig2 - np.mean(sig2)) / (np.std(sig2) + 1e-10)

    corr = np.mean(sig1_norm * sig2_norm)
    return corr


def main():
    import argparse

    ap = argparse.ArgumentParser(description="Step 5: Flip extended synthetic horizontally")
    ap.add_argument("synth", type=Path, help="Extended synthetic .out file")
    ap.add_argument("real", type=Path, help="Real .DZT file")
    ap.add_argument("--trace", type=int, default=1000, help="DZT trace index")
    ap.add_argument("-o", "--output", type=Path, default=None, help="Output PNG")
    args = ap.parse_args()

    if not args.synth.exists() or not args.real.exists():
        print("[ERR] Input files not found")
        sys.exit(1)

    print("[READ] Extended synthetic from gprMax...")
    syn_sig, syn_t, dt_syn = read_extended_synthetic(args.synth)

    print("[READ] Real DZT...")
    real_sig, real_t, dt_real = read_real_dzt(args.real, trace_idx=args.trace)

    print(f"\nExtended synthetic: {len(syn_sig)} samples, 0-{syn_t[-1]:.1f} ns")
    print(f"Real DZT:          {len(real_sig)} samples, 0-{real_t[-1]:.1f} ns")

    # Flip synthetic
    syn_flipped = flip_horizontal(syn_sig)

    print(f"\n[PROCESS] Flipping synthetic horizontally (time-reversed)...")
    print(f"  Original peak @ {syn_t[np.argmax(np.abs(syn_sig))]:.2f} ns")
    print(f"  Flipped peak @ {syn_t[np.argmax(np.abs(syn_flipped))]:.2f} ns")

    # Compute correlations
    syn_norm = normalize_peak(syn_sig)
    syn_flip_norm = normalize_peak(syn_flipped)
    real_norm = normalize_peak(real_sig)

    corr_orig_vs_real = compute_correlation(syn_norm, real_norm)
    corr_flip_vs_real = compute_correlation(syn_flip_norm, real_norm)

    print(f"\n[CORRELATE] Normalized cross-correlation @ lag=0:")
    print(f"  Original synthetic vs Real: {corr_orig_vs_real:.4f}")
    print(f"  Flipped synthetic vs Real:  {corr_flip_vs_real:.4f}")
    print(f"  Improvement: {corr_flip_vs_real - corr_orig_vs_real:+.4f}")

    if corr_flip_vs_real > corr_orig_vs_real:
        print(f"\n[RESULT] Flipping IMPROVES correlation by {corr_flip_vs_real - corr_orig_vs_real:.4f}")
    else:
        print(f"\n[RESULT] Flipping WORSENS correlation by {corr_orig_vs_real - corr_flip_vs_real:.4f}")
        print(f"         Original orientation is better.")

    # Plot comparison
    out_png = args.output or Path('output_test/05_flip_synthetic_horizontal.png')
    plot_flip_comparison(syn_sig, syn_t, dt_syn, syn_flipped, real_sig, real_t, dt_real, out_png)

    print(f"\n{'='*70}")
    print("FLIP ANALYSIS COMPLETE")
    print(f"{'='*70}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Step 7: Apply BOTH delay AND vertical flip to synthetic.
- Delay: +2.77 ns (to align peaks)
- Flip: multiply by -1 (to match polarity)
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


def apply_time_delay(signal, dt_ns, delay_ns):
    """Apply time delay by shifting signal."""
    delay_samples = int(np.round(delay_ns / dt_ns))

    if delay_samples == 0:
        return signal

    if delay_samples > 0:
        # Shift right: pad left with zeros
        delayed = np.concatenate([np.zeros(delay_samples), signal[:-delay_samples]])
    else:
        # Shift left: pad right with zeros
        delayed = np.concatenate([signal[-delay_samples:], np.zeros(-delay_samples)])

    return delayed


def flip_vertical(signal):
    """Flip signal vertically (multiply by -1)."""
    return signal * -1


def compute_correlation(sig1, sig2):
    """Compute normalized cross-correlation at lag 0."""
    if len(sig1) != len(sig2):
        min_len = min(len(sig1), len(sig2))
        sig1 = sig1[:min_len]
        sig2 = sig2[:min_len]

    sig1_norm = (sig1 - np.mean(sig1)) / (np.std(sig1) + 1e-10)
    sig2_norm = (sig2 - np.mean(sig2)) / (np.std(sig2) + 1e-10)

    corr = np.mean(sig1_norm * sig2_norm)
    return corr


def plot_delay_and_flip(syn_sig, syn_t, dt_syn, syn_modified, real_sig, real_t, dt_real, delay_ns, out_png):
    """
    Create 4-row comparison:
    Row 1: Original synthetic
    Row 2: After delay
    Row 3: After delay + flip
    Row 4: Delayed+flipped vs Real (normalized overlay)
    """

    # Apply modifications step by step
    syn_delayed = apply_time_delay(syn_sig, dt_syn, delay_ns)
    syn_modified_check = flip_vertical(syn_delayed)

    syn_norm = normalize_peak(syn_sig)
    syn_delayed_norm = normalize_peak(syn_delayed)
    syn_modified_norm = normalize_peak(syn_modified)
    real_norm = normalize_peak(real_sig)

    fig = plt.figure(figsize=(16, 16))
    fig.patch.set_facecolor("#0f1117")
    gs = gridspec.GridSpec(4, 1, figure=fig, hspace=0.30, left=0.1, right=0.95, top=0.96, bottom=0.06)

    c_syn_orig = "#00ff88"
    c_syn_delay = "#00d4ff"
    c_syn_modified = "#ff00ff"
    c_real = "#ff6b35"

    # Row 1: Original synthetic
    ax1 = fig.add_subplot(gs[0])
    ax1.set_facecolor("#1a1e2b")
    ax1.plot(syn_t, syn_sig, color=c_syn_orig, lw=2, alpha=0.85)
    ax1.axhline(0, color="#2a2f42", lw=0.8, linestyle='-', alpha=0.5)
    ax1.fill_between(syn_t, syn_sig, 0, alpha=0.15, color=c_syn_orig)

    syn_peak_idx = np.argmax(np.abs(syn_sig))
    ax1.axvline(syn_t[syn_peak_idx], color=c_syn_orig, lw=1.5, linestyle='--', alpha=0.6)

    ax1.set_ylabel("Amplitude (V/m)", fontsize=10, color="#c8d0e0", fontweight='bold')
    ax1.set_title(f"Row 1: ORIGINAL Synthetic (Peak @ {syn_t[syn_peak_idx]:.2f} ns)",
                 fontsize=11, color="#c8d0e0", fontweight='bold', pad=10)
    ax1.grid(True, color="#2a2f42", lw=0.5, alpha=0.4)
    ax1.tick_params(colors="#c8d0e0", labelsize=9)
    for spine in ax1.spines.values():
        spine.set_color("#2a2f42")

    # Row 2: After delay
    ax2 = fig.add_subplot(gs[1])
    ax2.set_facecolor("#1a1e2b")
    ax2.plot(syn_t, syn_delayed, color=c_syn_delay, lw=2, alpha=0.85)
    ax2.axhline(0, color="#2a2f42", lw=0.8, linestyle='-', alpha=0.5)
    ax2.fill_between(syn_t, syn_delayed, 0, alpha=0.15, color=c_syn_delay)

    syn_delayed_peak_idx = np.argmax(np.abs(syn_delayed))
    ax2.axvline(syn_t[syn_delayed_peak_idx], color=c_syn_delay, lw=1.5, linestyle='--', alpha=0.6)

    ax2.set_ylabel("Amplitude (V/m)", fontsize=10, color="#c8d0e0", fontweight='bold')
    ax2.set_title(f"Row 2: After +{delay_ns:.2f} ns DELAY (Peak @ {syn_t[syn_delayed_peak_idx]:.2f} ns)",
                 fontsize=11, color="#c8d0e0", fontweight='bold', pad=10)
    ax2.grid(True, color="#2a2f42", lw=0.5, alpha=0.4)
    ax2.tick_params(colors="#c8d0e0", labelsize=9)
    for spine in ax2.spines.values():
        spine.set_color("#2a2f42")

    # Row 3: After delay + flip
    ax3 = fig.add_subplot(gs[2])
    ax3.set_facecolor("#1a1e2b")
    ax3.plot(syn_t, syn_modified, color=c_syn_modified, lw=2, alpha=0.85)
    ax3.axhline(0, color="#2a2f42", lw=0.8, linestyle='-', alpha=0.5)
    ax3.fill_between(syn_t, syn_modified, 0, alpha=0.15, color=c_syn_modified)

    syn_modified_peak_idx = np.argmax(np.abs(syn_modified))
    ax3.axvline(syn_t[syn_modified_peak_idx], color=c_syn_modified, lw=1.5, linestyle='--', alpha=0.6)

    ax3.set_ylabel("Amplitude (V/m)", fontsize=10, color="#c8d0e0", fontweight='bold')
    ax3.set_title(f"Row 3: After +{delay_ns:.2f} ns DELAY + VERTICAL FLIP (Peak @ {syn_t[syn_modified_peak_idx]:.2f} ns)",
                 fontsize=11, color="#c8d0e0", fontweight='bold', pad=10)
    ax3.grid(True, color="#2a2f42", lw=0.5, alpha=0.4)
    ax3.tick_params(colors="#c8d0e0", labelsize=9)
    for spine in ax3.spines.values():
        spine.set_color("#2a2f42")

    # Row 4: Delayed+flipped vs Real (normalized)
    ax4 = fig.add_subplot(gs[3])
    ax4.set_facecolor("#1a1e2b")

    ax4.plot(syn_t, syn_modified_norm, color=c_syn_modified, lw=2, alpha=0.85, label="Synthetic (delayed + flipped)")
    ax4.plot(real_t, real_norm, color=c_real, lw=2, alpha=0.75, label="Real DZT")
    ax4.axhline(0, color="#2a2f42", lw=0.8, linestyle='-', alpha=0.5)

    ax4.set_xlabel("Time (ns)", fontsize=10, color="#c8d0e0", fontweight='bold')
    ax4.set_ylabel("Normalized Amplitude", fontsize=10, color="#c8d0e0", fontweight='bold')
    ax4.set_title("Row 4: Modified Synthetic vs Real - Shape Comparison (Normalized)",
                 fontsize=11, color="#c8d0e0", fontweight='bold', pad=10)
    ax4.grid(True, color="#2a2f42", lw=0.5, alpha=0.4)
    ax4.legend(loc='upper right', fontsize=10, facecolor='#1a1e2b', labelcolor='#c8d0e0', edgecolor='#2a2f42')
    ax4.tick_params(colors="#c8d0e0", labelsize=9)
    for spine in ax4.spines.values():
        spine.set_color("#2a2f42")

    # Main title
    fig.suptitle(
        f"Step 7: Apply Delay (+{delay_ns:.2f} ns) AND Vertical Flip (×−1)",
        color="#c8d0e0", fontsize=13, fontweight='bold', y=0.98
    )

    out_png.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_png, dpi=150, bbox_inches='tight', facecolor="#0f1117")
    plt.close(fig)

    print(f"\n[OK] Delay + flip comparison saved -> {out_png}")


def main():
    import argparse

    ap = argparse.ArgumentParser(description="Step 7: Apply delay AND vertical flip to synthetic")
    ap.add_argument("synth", type=Path, help="Extended synthetic .out file")
    ap.add_argument("real", type=Path, help="Real .DZT file")
    ap.add_argument("--delay", type=float, default=2.77, help="Time delay in ns")
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

    # Apply modifications
    print(f"\n[MODIFY] Applying transformations...")
    syn_delayed = apply_time_delay(syn_sig, dt_syn, args.delay)
    syn_modified = flip_vertical(syn_delayed)

    print(f"  [OK] Applied +{args.delay:.2f} ns delay")
    print(f"  [OK] Applied vertical flip (x-1)")

    # Compute correlations
    syn_orig_norm = normalize_peak(syn_sig)
    syn_modified_norm = normalize_peak(syn_modified)
    real_norm = normalize_peak(real_sig)

    corr_orig = compute_correlation(syn_orig_norm, real_norm)
    corr_modified = compute_correlation(syn_modified_norm, real_norm)

    print(f"\n[CORRELATE] Normalized cross-correlation @ lag=0:")
    print(f"  Original synthetic vs Real:          {corr_orig:.6f}")
    print(f"  Delayed + flipped synthetic vs Real: {corr_modified:.6f}")
    print(f"  Improvement: {corr_modified - corr_orig:+.6f}")

    if corr_modified > corr_orig:
        improvement_pct = ((corr_modified - corr_orig) / (abs(corr_orig) + 1e-10)) * 100
        print(f"  [GOOD] Modifications IMPROVE match by {improvement_pct:.1f}%")
    else:
        print(f"  [INFO] Modifications do not improve correlation")

    # Peak alignment check
    syn_mod_peak_idx = np.argmax(np.abs(syn_modified))
    real_peak_idx = np.argmax(np.abs(real_sig))
    peak_offset = real_t[real_peak_idx] - syn_t[syn_mod_peak_idx]

    print(f"\n[PEAKS] After modifications:")
    print(f"  Synthetic peak: {syn_t[syn_mod_peak_idx]:.2f} ns")
    print(f"  Real peak:      {real_t[real_peak_idx]:.2f} ns")
    print(f"  Offset:         {peak_offset:+.2f} ns")

    # Plot
    out_png = args.output or Path('output_test/07_delay_and_flip.png')
    plot_delay_and_flip(syn_sig, syn_t, dt_syn, syn_modified, real_sig, real_t, dt_real, args.delay, out_png)

    print(f"\n{'='*70}")
    print("DELAY + FLIP COMPLETE")
    print(f"{'='*70}")

    print(f"\nSummary:")
    print(f"  Delay applied:   +{args.delay:.2f} ns")
    print(f"  Flip applied:    x-1 (vertical)")
    print(f"  Correlation:     {corr_orig:.6f} -> {corr_modified:.6f}")

    if abs(corr_modified) > abs(corr_orig):
        print(f"\n  [SUCCESS] Modifications improve synthetic-real match!")
    else:
        print(f"\n  [NOTE] Still searching for better match...")


if __name__ == "__main__":
    main()

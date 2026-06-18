#!/usr/bin/env python3
"""
Step 6: Apply time delay to synthetic to align peaks with real.
Measured delay: 2.77 ns (real peak is 2.77 ns LATER than synthetic).
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
    """
    Apply time delay by shifting signal.
    delay_ns > 0: shift signal to the right (later in time)
    """
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


def compute_statistics(signal, t_ns, name="Signal"):
    """Compute basic statistics."""
    peak_idx = np.argmax(np.abs(signal))
    peak_time = t_ns[peak_idx]
    peak_amp = signal[peak_idx]

    max_val = np.max(np.abs(signal))
    above_10pct = np.where(np.abs(signal) > 0.1 * max_val)[0]
    if len(above_10pct) > 0:
        pulse_width = (t_ns[above_10pct[-1]] - t_ns[above_10pct[0]])
    else:
        pulse_width = 0

    return {
        'peak_time': peak_time,
        'peak_amp': peak_amp,
        'pulse_width': pulse_width,
        'rms': np.sqrt(np.mean(signal**2)),
    }


def plot_aligned_peaks(syn_sig, syn_t, dt_syn, syn_delayed, real_sig, real_t, dt_real, delay_ns, out_png):
    """
    Create 3-row comparison:
    Row 1: Original synthetic vs delayed synthetic (before/after)
    Row 2: Delayed synthetic vs real (normalized)
    Row 3: Zoomed comparison (0-15 ns)
    """

    syn_norm = normalize_peak(syn_sig)
    syn_delay_norm = normalize_peak(syn_delayed)
    real_norm = normalize_peak(real_sig)

    fig = plt.figure(figsize=(16, 14))
    fig.patch.set_facecolor("#0f1117")
    gs = gridspec.GridSpec(3, 1, figure=fig, hspace=0.35, left=0.1, right=0.95, top=0.95, bottom=0.08)

    c_syn_orig = "#00ff88"
    c_syn_delay = "#00d4ff"
    c_real = "#ff6b35"

    # Row 1: Original vs Delayed synthetic (raw)
    ax1 = fig.add_subplot(gs[0])
    ax1.set_facecolor("#1a1e2b")

    ax1.plot(syn_t, syn_sig, color=c_syn_orig, lw=2, alpha=0.75, label=f"Original (peak @ {syn_t[np.argmax(np.abs(syn_sig))]:.2f} ns)")
    ax1.plot(syn_t, syn_delayed, color=c_syn_delay, lw=2, alpha=0.85, label=f"Delayed +{delay_ns:.2f} ns (peak @ {syn_t[np.argmax(np.abs(syn_delayed))]:.2f} ns)")
    ax1.axhline(0, color="#2a2f42", lw=0.8, linestyle='-', alpha=0.5)

    ax1.set_ylabel("Amplitude (V/m)", fontsize=10, color="#c8d0e0", fontweight='bold')
    ax1.set_title(f"Row 1: Original vs Delayed Synthetic - {delay_ns:+.2f} ns shift",
                 fontsize=11, color="#c8d0e0", fontweight='bold', pad=10)
    ax1.grid(True, color="#2a2f42", lw=0.5, alpha=0.4)
    ax1.legend(loc='upper right', fontsize=9, facecolor='#1a1e2b', labelcolor='#c8d0e0', edgecolor='#2a2f42')
    ax1.tick_params(colors="#c8d0e0", labelsize=9)

    for spine in ax1.spines.values():
        spine.set_color("#2a2f42")

    # Row 2: Delayed synthetic vs Real (normalized)
    ax2 = fig.add_subplot(gs[1])
    ax2.set_facecolor("#1a1e2b")

    syn_peak_time = syn_t[np.argmax(np.abs(syn_delayed))]
    real_peak_time = real_t[np.argmax(np.abs(real_sig))]
    peak_offset = real_peak_time - syn_peak_time

    ax2.plot(syn_t, syn_delay_norm, color=c_syn_delay, lw=2, alpha=0.85, label=f"Synthetic (delayed, normalized)")
    ax2.plot(real_t, real_norm, color=c_real, lw=2, alpha=0.75, label=f"Real DZT (normalized)")
    ax2.axhline(0, color="#2a2f42", lw=0.8, linestyle='-', alpha=0.5)

    # Mark peaks
    ax2.plot(syn_peak_time, 1.0, 'o', color=c_syn_delay, markersize=8, markeredgewidth=2, markeredgecolor='#c8d0e0')
    ax2.plot(real_peak_time, 1.0, 's', color=c_real, markersize=8, markeredgewidth=2, markeredgecolor='#c8d0e0')

    ax2.set_ylabel("Normalized Amplitude", fontsize=10, color="#c8d0e0", fontweight='bold')
    title_msg = f"Row 2: Delayed Synthetic vs Real (Peak Alignment)"
    if abs(peak_offset) < 0.5:
        title_msg += f" [PEAKS ALIGNED]"
    else:
        title_msg += f" [Offset: {peak_offset:+.2f} ns]"
    ax2.set_title(title_msg, fontsize=11, color="#c8d0e0", fontweight='bold', pad=10)
    ax2.grid(True, color="#2a2f42", lw=0.5, alpha=0.4)
    ax2.legend(loc='upper right', fontsize=9, facecolor='#1a1e2b', labelcolor='#c8d0e0', edgecolor='#2a2f42')
    ax2.tick_params(colors="#c8d0e0", labelsize=9)

    for spine in ax2.spines.values():
        spine.set_color("#2a2f42")

    # Row 3: Zoomed early-time detail (0-15 ns)
    ax3 = fig.add_subplot(gs[2])
    ax3.set_facecolor("#1a1e2b")

    t_min, t_max = 0, 15
    idx_syn = (syn_t >= t_min) & (syn_t <= t_max)
    idx_real = (real_t >= t_min) & (real_t <= t_max)

    ax3.plot(syn_t[idx_syn], syn_delay_norm[idx_syn], color=c_syn_delay, lw=2.5, alpha=0.9, label="Synthetic (delayed)")
    ax3.plot(real_t[idx_real], real_norm[idx_real], color=c_real, lw=2.5, alpha=0.85, label="Real")
    ax3.axhline(0, color="#2a2f42", lw=0.8, linestyle='-', alpha=0.5)

    ax3.set_xlabel("Time (ns)", fontsize=10, color="#c8d0e0", fontweight='bold')
    ax3.set_ylabel("Normalized Amplitude", fontsize=10, color="#c8d0e0", fontweight='bold')
    ax3.set_title(f"Row 3: Early-Time Detail (0-15 ns) - Shape Match After Delay",
                 fontsize=11, color="#c8d0e0", fontweight='bold', pad=10)
    ax3.grid(True, color="#2a2f42", lw=0.5, alpha=0.4)
    ax3.legend(loc='upper right', fontsize=9, facecolor='#1a1e2b', labelcolor='#c8d0e0', edgecolor='#2a2f42')
    ax3.set_xlim([t_min, t_max])
    ax3.tick_params(colors="#c8d0e0", labelsize=9)

    for spine in ax3.spines.values():
        spine.set_color("#2a2f42")

    # Main title
    fig.suptitle(
        f"Step 6: Align Peaks - Apply {delay_ns:+.2f} ns Delay to Synthetic",
        color="#c8d0e0", fontsize=13, fontweight='bold', y=0.98
    )

    out_png.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_png, dpi=150, bbox_inches='tight', facecolor="#0f1117")
    plt.close(fig)

    print(f"\n[OK] Aligned peaks comparison saved -> {out_png}")


def main():
    import argparse

    ap = argparse.ArgumentParser(description="Step 6: Apply time delay to align synthetic peak with real peak")
    ap.add_argument("synth", type=Path, help="Extended synthetic .out file")
    ap.add_argument("real", type=Path, help="Real .DZT file")
    ap.add_argument("--delay", type=float, default=2.77, help="Time delay in ns (default: 2.77 ns)")
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

    print(f"\nExtended synthetic: {len(syn_sig)} samples, 0-{syn_t[-1]:.1f} ns, dt={dt_syn:.4f} ns")
    print(f"Real DZT:          {len(real_sig)} samples, 0-{real_t[-1]:.1f} ns, dt={dt_real:.4f} ns")

    # Compute original peaks
    syn_orig_peak_idx = np.argmax(np.abs(syn_sig))
    real_peak_idx = np.argmax(np.abs(real_sig))
    syn_orig_peak_time = syn_t[syn_orig_peak_idx]
    real_peak_time = real_t[real_peak_idx]
    measured_offset = real_peak_time - syn_orig_peak_time

    print(f"\n[MEASURE] Peak positions (BEFORE delay):")
    print(f"  Synthetic peak: {syn_orig_peak_time:.2f} ns")
    print(f"  Real peak:      {real_peak_time:.2f} ns")
    print(f"  Offset:         {measured_offset:+.2f} ns")

    # Apply delay
    delay_ns = args.delay
    print(f"\n[APPLY] Applying {delay_ns:+.2f} ns delay to synthetic...")
    syn_delayed = apply_time_delay(syn_sig, dt_syn, delay_ns)

    # Check new peak position
    syn_delayed_peak_idx = np.argmax(np.abs(syn_delayed))
    syn_delayed_peak_time = syn_t[syn_delayed_peak_idx]
    new_offset = real_peak_time - syn_delayed_peak_time

    print(f"\n[MEASURE] Peak positions (AFTER delay):")
    print(f"  Synthetic peak: {syn_delayed_peak_time:.2f} ns (was {syn_orig_peak_time:.2f})")
    print(f"  Real peak:      {real_peak_time:.2f} ns")
    print(f"  Offset:         {new_offset:+.2f} ns (was {measured_offset:+.2f})")

    # Plot comparison
    out_png = args.output or Path('output_test/06_align_peaks_with_delay.png')
    plot_aligned_peaks(syn_sig, syn_t, dt_syn, syn_delayed, real_sig, real_t, dt_real, delay_ns, out_png)

    print(f"\n{'='*70}")
    print("PEAK ALIGNMENT COMPLETE")
    print(f"{'='*70}")

    print(f"\nDelay Applied: {delay_ns:+.2f} ns")
    print(f"  Samples shifted: {int(np.round(delay_ns / dt_syn))} (out of {len(syn_sig)} total)")
    print(f"\nResult:")
    if abs(new_offset) < 0.5:
        print(f"  [OK] Peaks now aligned! Offset = {new_offset:+.2f} ns")
    else:
        print(f"  [INFO] Offset reduced: {measured_offset:+.2f} ns -> {new_offset:+.2f} ns")

    print(f"\nTo apply this delay in gprMax simulation:")
    print(f"  Set antenna tx_z to account for {delay_ns:.2f} ns propagation")
    print(f"  Or add receiver delay in gprMax receiver definition")


if __name__ == "__main__":
    main()

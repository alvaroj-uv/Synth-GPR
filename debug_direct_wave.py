#!/usr/bin/env python3
"""
Debug direct wave detection in synthetic signal.
"""

import sys
from pathlib import Path
import numpy as np
import h5py
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from scipy.signal import hilbert


def read_synthetic_file(out_path: Path):
    """Read gprMax .out file."""
    with h5py.File(out_path, 'r') as f:
        signal = f['rxs/rx1/Ez'][()]
        dt = f.attrs.get('dt', 0.0)
    return signal, dt * 1e9


def main():
    # Load synthetic data
    out_path = Path("output_test/ballast_eps51_optimized.out")
    signal, dt_ns = read_synthetic_file(out_path)

    t_ns = np.arange(len(signal)) * dt_ns

    print(f"[LOAD] {out_path.name}")
    print(f"  Samples: {len(signal)}")
    print(f"  dt: {dt_ns:.6f} ns")
    print(f"  Total duration: {(len(signal)-1)*dt_ns:.2f} ns\n")

    # ========================================================================
    # Analyze direct wave detection
    # ========================================================================

    print(f"{'='*70}")
    print("DIRECT WAVE DETECTION ANALYSIS")
    print(f"{'='*70}\n")

    # Find peak in first 20 ns
    search_ns = 20
    search_idx = int(search_ns / dt_ns)
    search_region = signal[:search_idx]

    peak_idx = np.argmax(np.abs(search_region))
    peak_time = t_ns[peak_idx]
    peak_value = signal[peak_idx]

    print(f"Search window: 0-{search_ns} ns ({search_idx} samples)")
    print(f"Peak found at:")
    print(f"  Index: {peak_idx}")
    print(f"  Time: {peak_time:.4f} ns")
    print(f"  Value: {peak_value:.2f} V/m")
    print(f"  Amplitude: {abs(peak_value):.2f} V/m\n")

    # Try different search windows
    print("Peak detection with different search windows:")
    print(f"{'Window (ns)':<15} {'Peak idx':<12} {'Peak time (ns)':<18} {'Peak value (V/m)':<20}")
    print("-" * 70)

    for search_ns_test in [5, 10, 15, 20, 25, 30]:
        search_idx_test = int(search_ns_test / dt_ns)
        peak_idx_test = np.argmax(np.abs(signal[:search_idx_test]))
        peak_time_test = t_ns[peak_idx_test]
        peak_value_test = signal[peak_idx_test]
        print(f"{search_ns_test:<15} {peak_idx_test:<12} {peak_time_test:<18.4f} {peak_value_test:<20.2f}")

    print()

    # ========================================================================
    # Visualize
    # ========================================================================

    fig = plt.figure(figsize=(16, 10))
    fig.patch.set_facecolor("#0f1117")
    gs = gridspec.GridSpec(3, 2, figure=fig, hspace=0.4, wspace=0.3,
                          left=0.1, right=0.95, top=0.96, bottom=0.08)

    # Full signal
    ax1 = fig.add_subplot(gs[0, :])
    ax1.set_facecolor("#1a1e2b")
    ax1.plot(t_ns, signal, color="#ff6b35", lw=0.8, alpha=0.8, label="Full signal")
    ax1.scatter([peak_time], [peak_value], color="#ffff00", s=200, marker='*',
               edgecolor='white', linewidth=2, zorder=5, label=f"Peak @ {peak_time:.4f}ns")
    ax1.axvline(peak_time, color="#ffff00", linestyle='--', alpha=0.5, linewidth=2)
    ax1.axhline(0, color='#2a2f42', lw=0.8, alpha=0.5)
    ax1.set_ylabel("Amplitude (V/m)", fontsize=11, color="#c8d0e0", fontweight='bold')
    ax1.set_title("Full Signal (0-50ns) - Direct Wave Detection", fontsize=12,
                 color="#ff6b35", fontweight='bold')
    ax1.grid(True, color="#2a2f42", alpha=0.3)
    ax1.legend(fontsize=10, facecolor='#1a1e2b', labelcolor='#c8d0e0', edgecolor='#2a2f42')
    ax1.tick_params(colors="#c8d0e0", labelsize=9)
    for spine in ax1.spines.values():
        spine.set_color("#2a2f42")

    # Zoomed: first 10 ns
    ax2 = fig.add_subplot(gs[1, 0])
    ax2.set_facecolor("#1a1e2b")
    t_zoom = t_ns[t_ns <= 10]
    mask = t_ns <= 10
    ax2.plot(t_zoom, signal[mask], color="#00d9ff", lw=1.5, alpha=0.8)
    ax2.scatter([peak_time], [peak_value], color="#ffff00", s=150, marker='*',
               edgecolor='white', linewidth=2, zorder=5)
    ax2.axvline(peak_time, color="#ffff00", linestyle='--', alpha=0.5, linewidth=2)
    ax2.axhline(0, color='#2a2f42', lw=0.8, alpha=0.5)
    ax2.set_ylabel("Amplitude (V/m)", fontsize=10, color="#c8d0e0", fontweight='bold')
    ax2.set_title("Zoomed: First 10 ns (Direct Wave Region)", fontsize=11,
                 color="#00d9ff", fontweight='bold')
    ax2.grid(True, color="#2a2f42", alpha=0.3)
    ax2.tick_params(colors="#c8d0e0", labelsize=9)
    for spine in ax2.spines.values():
        spine.set_color("#2a2f42")

    # Absolute value (envelope-like)
    ax3 = fig.add_subplot(gs[1, 1])
    ax3.set_facecolor("#1a1e2b")
    t_zoom = t_ns[t_ns <= 10]
    mask = t_ns <= 10
    abs_signal = np.abs(signal[mask])
    ax3.plot(t_zoom, abs_signal, color="#00ff88", lw=1.5, alpha=0.8, label="|Signal|")
    ax3.scatter([peak_time], [abs(peak_value)], color="#ffff00", s=150, marker='*',
               edgecolor='white', linewidth=2, zorder=5, label="Peak")
    ax3.fill_between(t_zoom, 0, abs_signal, color="#00ff88", alpha=0.15)
    ax3.axvline(peak_time, color="#ffff00", linestyle='--', alpha=0.5, linewidth=2)
    ax3.set_ylabel("Absolute Amplitude (V/m)", fontsize=10, color="#c8d0e0", fontweight='bold')
    ax3.set_title("Absolute Value: First 10 ns", fontsize=11,
                 color="#00ff88", fontweight='bold')
    ax3.grid(True, color="#2a2f42", alpha=0.3)
    ax3.legend(fontsize=9, facecolor='#1a1e2b', labelcolor='#c8d0e0', edgecolor='#2a2f42')
    ax3.tick_params(colors="#c8d0e0", labelsize=9)
    for spine in ax3.spines.values():
        spine.set_color("#2a2f42")

    # After 30-sample shift
    ax4 = fig.add_subplot(gs[2, 0])
    ax4.set_facecolor("#1a1e2b")
    shift_samples = 30
    new_start_idx = peak_idx + shift_samples
    signal_shifted = signal[new_start_idx:]
    t_shifted = np.arange(len(signal_shifted)) * dt_ns
    t_shifted_zoom = t_shifted[t_shifted <= 10]
    mask_shifted = t_shifted <= 10
    ax4.plot(t_shifted_zoom, signal_shifted[mask_shifted], color="#ff00ff", lw=1.5, alpha=0.8,
            label=f"After DW elimination (+{shift_samples} samp)")
    ax4.axhline(0, color='#2a2f42', lw=0.8, alpha=0.5)
    ax4.set_ylabel("Amplitude (V/m)", fontsize=10, color="#c8d0e0", fontweight='bold')
    ax4.set_title(f"After DW Removal: First 10 ns (start idx={new_start_idx})", fontsize=11,
                 color="#ff00ff", fontweight='bold')
    ax4.grid(True, color="#2a2f42", alpha=0.3)
    ax4.legend(fontsize=9, facecolor='#1a1e2b', labelcolor='#c8d0e0', edgecolor='#2a2f42')
    ax4.tick_params(colors="#c8d0e0", labelsize=9)
    for spine in ax4.spines.values():
        spine.set_color("#2a2f42")

    # Analysis text
    ax5 = fig.add_subplot(gs[2, 1])
    ax5.set_facecolor("#1a1e2b")
    ax5.axis('off')

    analysis_text = f"""
    DIRECT WAVE ANALYSIS

    Peak Detection:
    • Index: {peak_idx}
    • Time: {peak_time:.4f} ns
    • Amplitude: {abs(peak_value):.2f} V/m

    After Shift (+30 samples):
    • New start index: {new_start_idx}
    • Samples remaining: {len(signal_shifted)}
    • New duration: {(len(signal_shifted)-1)*dt_ns:.2f} ns

    Issues to Check:
    ✓ Peak correctly identified?
    ✓ Shift amount (30 samples) appropriate?
    ✓ Remaining signal strong enough?
    ✓ Coda region properly isolated?
    """

    ax5.text(0.1, 0.5, analysis_text, transform=ax5.transAxes,
            fontsize=10, verticalalignment='center', fontfamily='monospace',
            color='#c8d0e0', bbox=dict(boxstyle='round', facecolor='#2a2f42',
                                       edgecolor='#00d9ff', linewidth=2, alpha=0.8))

    fig.suptitle(
        "Debug: Direct Wave Detection in Synthetic Signal",
        color="#c8d0e0", fontsize=13, fontweight='bold', y=0.995
    )

    png_path = Path("output_test") / "debug_direct_wave.png"
    fig.savefig(png_path, dpi=150, bbox_inches='tight', facecolor="#0f1117")
    print(f"[SAVE] {png_path}\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())

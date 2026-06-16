#!/usr/bin/env python3
"""
Visualize complete synthetic trace with all cutoff points marked.
Shows the full 50ns window with DW peak and cutoff lines.
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
    # Load synthetic
    out_path = Path("output_test/ballast_eps51_optimized.out")
    signal, dt_ns = read_synthetic_file(out_path)

    t_ns = np.arange(len(signal)) * dt_ns

    print(f"[LOAD] {out_path.name}")
    print(f"  Samples: {len(signal)}")
    print(f"  dt: {dt_ns:.6f} ns")
    print(f"  Duration: {(len(signal)-1)*dt_ns:.2f} ns\n")

    # Apply polarity flip
    signal = -signal
    print("[POLARIZE] Synthetic signal flipped (multiplied by -1)\n")

    # Find DW peak
    search_ns = 20
    search_idx = int(search_ns / dt_ns)
    peak_idx = np.argmax(np.abs(signal[:search_idx]))
    peak_time = t_ns[peak_idx]

    print(f"Direct Wave Peak: {peak_time:.4f} ns (index {peak_idx})\n")

    # ========================================================================
    # Create visualization
    # ========================================================================

    fig = plt.figure(figsize=(20, 12))
    fig.patch.set_facecolor("#0f1117")
    gs = gridspec.GridSpec(2, 1, figure=fig, hspace=0.3,
                          left=0.08, right=0.95, top=0.96, bottom=0.08)

    # ========================================================================
    # Row 1: Full trace with all cutoff lines
    # ========================================================================

    ax1 = fig.add_subplot(gs[0])
    ax1.set_facecolor("#1a1e2b")

    # Plot full signal
    ax1.plot(t_ns, signal, color="#00d9ff", lw=1.5, alpha=0.9, label="Synthetic signal (V/m)")

    # DW peak marker
    ax1.scatter([peak_time], [signal[peak_idx]], color='#ffff00', s=300, marker='*',
               edgecolor='white', linewidth=2.5, zorder=5, label=f"DW Peak @ {peak_time:.3f}ns")
    ax1.axvline(peak_time, color='#ffff00', linestyle='--', linewidth=2.5, alpha=0.7)

    # Cutoff lines with different colors
    cutoff_samples = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
    colors_cutoff = ['#ff0000', '#ff4400', '#ff8800', '#ffcc00', '#00ff00',
                     '#00ffaa', '#00ccff', '#0088ff', '#0044ff', '#4400ff', '#8800ff']

    cutoff_times = []
    for shift_samples, color in zip(cutoff_samples, colors_cutoff):
        cutoff_idx = peak_idx + shift_samples
        if cutoff_idx < len(signal):
            cutoff_time = t_ns[cutoff_idx]
            cutoff_times.append((shift_samples, cutoff_time))

            # Mark with vertical line
            ax1.axvline(cutoff_time, color=color, linestyle=':', linewidth=2, alpha=0.6)

            # Add label at top
            label_text = f"{shift_samples}s\n{cutoff_time:.2f}ns"
            ax1.text(cutoff_time, np.max(signal)*0.95, label_text,
                    rotation=0, fontsize=8, color=color, fontweight='bold',
                    ha='center', va='top',
                    bbox=dict(boxstyle='round,pad=0.3', facecolor='#1a1e2b',
                             edgecolor=color, linewidth=1, alpha=0.7))

    ax1.axhline(0, color='#2a2f42', lw=0.8, alpha=0.5)
    ax1.set_ylabel("Amplitude (V/m)", fontsize=13, color="#c8d0e0", fontweight='bold')
    ax1.set_title("Complete Synthetic Trace (420 MHz Ballast) - All Cutoff Points Marked",
                 fontsize=14, color="#00d9ff", fontweight='bold', pad=15)
    ax1.grid(True, color="#2a2f42", alpha=0.3, linestyle='-', linewidth=0.5)
    ax1.legend(fontsize=11, facecolor='#1a1e2b', labelcolor='#c8d0e0',
              edgecolor='#2a2f42', loc='upper right')
    ax1.tick_params(colors="#c8d0e0", labelsize=11)
    for spine in ax1.spines.values():
        spine.set_color("#2a2f42")

    # ========================================================================
    # Row 2: Zoomed view of first 15ns (DW region) with cutoffs
    # ========================================================================

    ax2 = fig.add_subplot(gs[1])
    ax2.set_facecolor("#1a1e2b")

    # Plot zoomed region
    t_zoom = t_ns[t_ns <= 15]
    mask = t_ns <= 15
    ax2.plot(t_zoom, signal[mask], color="#00d9ff", lw=2, alpha=0.9, label="Signal (first 15ns)")

    # DW peak
    ax2.scatter([peak_time], [signal[peak_idx]], color='#ffff00', s=300, marker='*',
               edgecolor='white', linewidth=2.5, zorder=5)
    ax2.axvline(peak_time, color='#ffff00', linestyle='--', linewidth=2.5, alpha=0.7,
               label=f"DW Peak @ {peak_time:.3f}ns")

    # Cutoff lines in zoom
    for shift_samples, color in zip(cutoff_samples[:7], colors_cutoff[:7]):  # Only first 7
        cutoff_idx = peak_idx + shift_samples
        if cutoff_idx < len(signal):
            cutoff_time = t_ns[cutoff_idx]
            if cutoff_time <= 15:
                ax2.axvline(cutoff_time, color=color, linestyle=':', linewidth=2.5, alpha=0.7)

                # Add label
                label_text = f"{shift_samples}s\n{cutoff_time:.2f}ns"
                ax2.text(cutoff_time, np.max(signal[mask])*0.8, label_text,
                        rotation=0, fontsize=9, color=color, fontweight='bold',
                        ha='center', va='top',
                        bbox=dict(boxstyle='round,pad=0.3', facecolor='#1a1e2b',
                                 edgecolor=color, linewidth=1.5, alpha=0.8))

    # Highlight optimal cutoff (40 samples = ~0.28 ns after peak)
    optimal_idx = peak_idx + 40
    if optimal_idx < len(signal):
        optimal_time = t_ns[optimal_idx]
        ax2.scatter([optimal_time], [signal[optimal_idx]], color='#00ff00', s=400, marker='D',
                   edgecolor='white', linewidth=2.5, zorder=6, label='OPTIMAL: 40 samples')
        ax2.axvline(optimal_time, color='#00ff00', linestyle='-', linewidth=3, alpha=0.8)

    ax2.axhline(0, color='#2a2f42', lw=0.8, alpha=0.5)
    ax2.set_ylabel("Amplitude (V/m)", fontsize=13, color="#c8d0e0", fontweight='bold')
    ax2.set_xlabel("Time (ns)", fontsize=13, color="#c8d0e0", fontweight='bold')
    ax2.set_title("Zoomed: Direct Wave Region (0-15 ns) with Cutoff Points",
                 fontsize=14, color="#00d9ff", fontweight='bold', pad=15)
    ax2.grid(True, color="#2a2f42", alpha=0.3, linestyle='-', linewidth=0.5)
    ax2.legend(fontsize=11, facecolor='#1a1e2b', labelcolor='#c8d0e0',
              edgecolor='#2a2f42', loc='upper right')
    ax2.tick_params(colors="#c8d0e0", labelsize=11)
    for spine in ax2.spines.values():
        spine.set_color("#2a2f42")

    fig.suptitle(
        "Complete Synthetic A-Scan with Direct Wave Cutoff Points\n"
        "Green diamond = OPTIMAL cutoff (40 samples = 0.283 ns)",
        color="#c8d0e0", fontsize=15, fontweight='bold', y=0.98
    )

    png_path = Path("output_test") / "complete_trace_with_cutoffs.png"
    fig.savefig(png_path, dpi=150, bbox_inches='tight', facecolor="#0f1117")
    print(f"[SAVE] {png_path}\n")

    # ========================================================================
    # Print cutoff table
    # ========================================================================

    print(f"{'='*80}")
    print("CUTOFF POINTS TABLE")
    print(f"{'='*80}\n")

    print(f"{'Shift':<15} {'Time':<15} {'Index':<15} {'Description':<30}")
    print(f"{'(samples)':<15} {'(ns)':<15} {'(sample #)':<15} {'':<30}")
    print("-" * 80)

    for shift_samples in cutoff_samples:
        cutoff_idx = peak_idx + shift_samples
        if cutoff_idx < len(signal):
            cutoff_time = t_ns[cutoff_idx]

            if shift_samples == 40:
                desc = "OPTIMAL - Best quality"
            elif shift_samples == 0:
                desc = "No removal (max peak)"
            else:
                desc = ""

            print(f"{shift_samples:<15} {cutoff_time:<15.3f} {cutoff_idx:<15} {desc:<30}")

    print()
    print(f"DW Peak: {peak_time:.4f} ns (index {peak_idx})")
    print(f"Optimal cutoff: 40 samples ({peak_idx + 40} total index)")
    print()

    return 0


if __name__ == "__main__":
    sys.exit(main())

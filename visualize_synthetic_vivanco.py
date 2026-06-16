#!/usr/bin/env python3
"""
Visualize synthetic trace before and after Vivanco processing.
"""

import sys
from pathlib import Path
import numpy as np
import h5py
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from scripts.proceso_senal_vivanco import VivancoPipeline


def read_synthetic_file(out_path: Path):
    """Read gprMax .out file."""
    with h5py.File(out_path, 'r') as f:
        signal = f['rxs/rx1/Ez'][()]
        dt = f.attrs.get('dt', 0.0)
    return signal, dt * 1e9


def main():
    # Load synthetic data
    out_path = Path("output_test/ballast_eps51_optimized.out")
    print(f"[LOAD] {out_path.name}")
    signal, dt_ns = read_synthetic_file(out_path)
    print(f"  Samples: {len(signal)}")
    print(f"  dt: {dt_ns:.6f} ns")
    print(f"  Window: {(len(signal)-1)*dt_ns:.2f} ns\n")

    # Apply polarity flip (synthetic needs inversion)
    signal = -signal
    print("[POLARIZE] Synthetic signal flipped (multiplied by -1)\n")

    # Process with Vivanco pipeline
    pipeline = VivancoPipeline(dt_ns=dt_ns)
    result = pipeline.process_single_trace(signal, window_length_ns=50)

    # Create time axes
    t_original = np.arange(len(signal)) * dt_ns
    t_processed = np.arange(len(result['signal_envelope'])) * dt_ns

    # Create visualization
    fig = plt.figure(figsize=(18, 10))
    fig.patch.set_facecolor("#0f1117")
    gs = gridspec.GridSpec(2, 2, figure=fig, hspace=0.3, wspace=0.3,
                          left=0.08, right=0.95, top=0.96, bottom=0.08)

    # ========================================================================
    # Row 1: Original vs After Direct Wave Elimination
    # ========================================================================

    ax1 = fig.add_subplot(gs[0, 0])
    ax1.set_facecolor("#1a1e2b")

    t_display = t_original[t_original <= 50]
    mask = t_original <= 50
    ax1.plot(t_display, signal[mask], color="#ff6b35", lw=1, alpha=0.8, label="Original")

    dw_peak_idx = result['direct_wave_peak_idx']
    ax1.axvline(t_original[dw_peak_idx], color="#ffff00", linestyle='--', linewidth=2,
               alpha=0.7, label=f"DW Peak: {t_original[dw_peak_idx]:.2f} ns")

    ax1.axhline(0, color='#2a2f42', lw=0.8, alpha=0.5)
    ax1.set_ylabel("Amplitude (V/m)", fontsize=11, color="#c8d0e0", fontweight='bold')
    ax1.set_title("Original Signal (420 MHz Gaussian Ballast)", fontsize=12,
                 color="#ff6b35", fontweight='bold')
    ax1.grid(True, color="#2a2f42", alpha=0.3)
    ax1.legend(fontsize=10, facecolor='#1a1e2b', labelcolor='#c8d0e0',
              edgecolor='#2a2f42', loc='upper right')
    ax1.tick_params(colors="#c8d0e0", labelsize=9)
    for spine in ax1.spines.values():
        spine.set_color("#2a2f42")

    ax2 = fig.add_subplot(gs[0, 1])
    ax2.set_facecolor("#1a1e2b")

    t_dw_removed = np.arange(len(result['signal_no_dw'])) * dt_ns
    t_dw_display = t_dw_removed[t_dw_removed <= 50]
    mask_dw = t_dw_removed <= 50

    ax2.plot(t_dw_display, result['signal_no_dw'][mask_dw], color="#00ff88", lw=1,
            alpha=0.8, label="DW Eliminated (+30 samples)")
    ax2.axhline(0, color='#2a2f42', lw=0.8, alpha=0.5)
    ax2.set_ylabel("Amplitude (V/m)", fontsize=11, color="#c8d0e0", fontweight='bold')
    ax2.set_title("After Direct Wave Elimination", fontsize=12,
                 color="#00ff88", fontweight='bold')
    ax2.grid(True, color="#2a2f42", alpha=0.3)
    ax2.legend(fontsize=10, facecolor='#1a1e2b', labelcolor='#c8d0e0',
              edgecolor='#2a2f42', loc='upper right')
    ax2.tick_params(colors="#c8d0e0", labelsize=9)
    for spine in ax2.spines.values():
        spine.set_color("#2a2f42")

    # ========================================================================
    # Row 2: Filtered vs Final Envelope
    # ========================================================================

    ax3 = fig.add_subplot(gs[1, 0])
    ax3.set_facecolor("#1a1e2b")

    t_filt = np.arange(len(result['signal_filtered'])) * dt_ns
    t_filt_display = t_filt[t_filt <= 50]
    mask_filt = t_filt <= 50

    ax3.plot(t_filt_display, result['signal_filtered'][mask_filt], color="#ff00ff", lw=1,
            alpha=0.8, label="Bandpass 150-800 MHz")
    ax3.axhline(0, color='#2a2f42', lw=0.8, alpha=0.5)
    ax3.set_xlabel("Time (ns)", fontsize=11, color="#c8d0e0", fontweight='bold')
    ax3.set_ylabel("Amplitude (V/m)", fontsize=11, color="#c8d0e0", fontweight='bold')
    ax3.set_title("After Bandpass Filter", fontsize=12,
                 color="#ff00ff", fontweight='bold')
    ax3.grid(True, color="#2a2f42", alpha=0.3)
    ax3.legend(fontsize=10, facecolor='#1a1e2b', labelcolor='#c8d0e0',
              edgecolor='#2a2f42', loc='upper right')
    ax3.tick_params(colors="#c8d0e0", labelsize=9)
    for spine in ax3.spines.values():
        spine.set_color("#2a2f42")

    ax4 = fig.add_subplot(gs[1, 1])
    ax4.set_facecolor("#1a1e2b")

    t_proc_display = t_processed[t_processed <= 50]
    mask_proc = t_processed <= 50

    ax4.plot(t_proc_display, result['signal_envelope'][mask_proc], color="#00d9ff", lw=2.5,
            alpha=0.9, label="Analytic Envelope (Hilbert)")
    ax4.fill_between(t_proc_display, 0, result['signal_envelope'][mask_proc],
                    color="#00d9ff", alpha=0.15)
    ax4.axhline(0, color='#2a2f42', lw=0.8, alpha=0.5)
    ax4.set_xlabel("Time (ns)", fontsize=11, color="#c8d0e0", fontweight='bold')
    ax4.set_ylabel("Envelope Amplitude", fontsize=11, color="#c8d0e0", fontweight='bold')
    ax4.set_title("FINAL: Analytic Envelope (Hilbert Transform)", fontsize=12,
                 color="#00d9ff", fontweight='bold')
    ax4.grid(True, color="#2a2f42", alpha=0.3)
    ax4.legend(fontsize=10, facecolor='#1a1e2b', labelcolor='#c8d0e0',
              edgecolor='#2a2f42', loc='upper right')
    ax4.tick_params(colors="#c8d0e0", labelsize=9)
    for spine in ax4.spines.values():
        spine.set_color("#2a2f42")

    # Title with processing info
    fig.suptitle(
        "Synthetic Signal Processing: Vivanco Pipeline\n"
        "420 MHz Gaussian Bistatic, Clean Ballast (eps=5.1), 50ns Full Coda",
        color="#c8d0e0", fontsize=13, fontweight='bold', y=0.995
    )

    png_path = Path("output_test") / "synthetic_vivanco_processing.png"
    fig.savefig(png_path, dpi=150, bbox_inches='tight', facecolor="#0f1117")
    print(f"[SAVE] {png_path}\n")

    # Print statistics
    print(f"{'='*70}")
    print("PROCESSING STATISTICS")
    print(f"{'='*70}\n")

    print(f"Original signal:")
    print(f"  Samples: {len(signal)}")
    print(f"  Duration: {(len(signal)-1)*dt_ns:.2f} ns")
    print(f"  Peak: {np.max(np.abs(signal)):.2f} V/m")
    print(f"  Mean: {np.mean(signal):.6f} V/m")
    print(f"  Std: {np.std(signal):.2f} V/m\n")

    print(f"After DW elimination:")
    print(f"  Samples: {len(result['signal_no_dw'])}")
    print(f"  Duration: {(len(result['signal_no_dw'])-1)*dt_ns:.2f} ns")
    print(f"  Start idx: {result['dw_eliminated_idx']}\n")

    print(f"Final envelope:")
    print(f"  Samples: {len(result['signal_envelope'])}")
    print(f"  Duration: {(len(result['signal_envelope'])-1)*dt_ns:.2f} ns")
    print(f"  Peak: {np.max(result['signal_envelope']):.4f}")
    print(f"  Mean: {np.mean(result['signal_envelope']):.6f}")
    print(f"  Std: {np.std(result['signal_envelope']):.6f}\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())

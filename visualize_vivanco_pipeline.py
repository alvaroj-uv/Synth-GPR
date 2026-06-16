#!/usr/bin/env python3
"""
Visualize Vivanco signal processing pipeline steps.
Shows original → processed transformation.
"""

import sys
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from scripts.proceso_senal_vivanco import VivancoPipeline, read_dzt_file


def main():
    # Read sample real data
    dzt_path = Path("D:/Codigo/Data/PUERTO-LIMACHE_20230726_EFE_V1_PKC000_588_PKF011_020_CENTRO_BRUTO.DZT")
    signals, dt_ns = read_dzt_file(dzt_path, max_traces=1)
    signal = signals[0, :]

    # Process with detailed steps
    pipeline = VivancoPipeline(dt_ns=dt_ns)
    result = pipeline.process_single_trace(signal, window_length_ns=50)

    # Create visualization
    fig = plt.figure(figsize=(18, 14))
    fig.patch.set_facecolor("#0f1117")
    gs = gridspec.GridSpec(4, 2, figure=fig, hspace=0.4, wspace=0.3,
                          left=0.08, right=0.95, top=0.96, bottom=0.06)

    colors = {
        'original': '#ff6b35',
        'norm': '#00d9ff',
        'dc': '#ffaa00',
        'dw': '#00ff88',
        'filter': '#ff00ff',
        'truncate': '#ffff00',
        'envelope': '#00ffff',
    }

    t_max = 50  # Display window in ns

    # ========================================================================
    # Row 1: Original & Normalization
    # ========================================================================

    ax1 = fig.add_subplot(gs[0, 0])
    ax1.set_facecolor("#1a1e2b")
    t_orig = np.arange(len(result['original'])) * dt_ns
    t_display = t_orig[t_orig <= t_max]
    mask = t_orig <= t_max
    ax1.plot(t_display, result['original'][mask], color=colors['original'], lw=1.5, alpha=0.8)
    ax1.axhline(0, color='#2a2f42', lw=0.8, alpha=0.5)
    ax1.set_ylabel("Amplitude", fontsize=10, color="#c8d0e0", fontweight='bold')
    ax1.set_title("1. Original Signal", fontsize=11, color=colors['original'], fontweight='bold')
    ax1.grid(True, color="#2a2f42", alpha=0.3)
    ax1.tick_params(colors="#c8d0e0", labelsize=9)
    for spine in ax1.spines.values():
        spine.set_color("#2a2f42")

    ax2 = fig.add_subplot(gs[0, 1])
    ax2.set_facecolor("#1a1e2b")
    mask = t_orig <= t_max
    ax2.plot(t_display, result['signal_norm'][mask], color=colors['norm'], lw=1.5, alpha=0.8)
    ax2.axhline(0, color='#2a2f42', lw=0.8, alpha=0.5)
    ax2.set_ylabel("Amplitude (normalized)", fontsize=10, color="#c8d0e0", fontweight='bold')
    ax2.set_title("2. Direct Wave Normalization", fontsize=11, color=colors['norm'], fontweight='bold')
    ax2.grid(True, color="#2a2f42", alpha=0.3)
    ax2.tick_params(colors="#c8d0e0", labelsize=9)
    for spine in ax2.spines.values():
        spine.set_color("#2a2f42")

    # ========================================================================
    # Row 2: DC Removal & DW Elimination
    # ========================================================================

    ax3 = fig.add_subplot(gs[1, 0])
    ax3.set_facecolor("#1a1e2b")
    mask = t_orig <= t_max
    ax3.plot(t_display, result['signal_no_dc'][mask], color=colors['dc'], lw=1.5, alpha=0.8)
    ax3.axhline(0, color='#2a2f42', lw=0.8, alpha=0.5)
    ax3.set_ylabel("Amplitude (zero-mean)", fontsize=10, color="#c8d0e0", fontweight='bold')
    ax3.set_title("3. DC-Shift Removal", fontsize=11, color=colors['dc'], fontweight='bold')
    ax3.grid(True, color="#2a2f42", alpha=0.3)
    ax3.tick_params(colors="#c8d0e0", labelsize=9)
    for spine in ax3.spines.values():
        spine.set_color("#2a2f42")

    ax4 = fig.add_subplot(gs[1, 1])
    ax4.set_facecolor("#1a1e2b")
    t_dw_removed = np.arange(len(result['signal_no_dw'])) * dt_ns
    t_dw_display = t_dw_removed[t_dw_removed <= t_max]
    mask_dw = t_dw_removed <= t_max
    ax4.plot(t_dw_display, result['signal_no_dw'][mask_dw], color=colors['dw'], lw=1.5, alpha=0.8)
    ax4.axhline(0, color='#2a2f42', lw=0.8, alpha=0.5)
    ax4.set_ylabel("Amplitude", fontsize=10, color="#c8d0e0", fontweight='bold')
    ax4.set_title(f"4. Direct Wave Elimination (+30 samples)", fontsize=11, color=colors['dw'], fontweight='bold')
    ax4.grid(True, color="#2a2f42", alpha=0.3)
    ax4.tick_params(colors="#c8d0e0", labelsize=9)
    for spine in ax4.spines.values():
        spine.set_color("#2a2f42")

    # ========================================================================
    # Row 3: Bandpass Filter & Truncation
    # ========================================================================

    ax5 = fig.add_subplot(gs[2, 0])
    ax5.set_facecolor("#1a1e2b")
    t_filt = np.arange(len(result['signal_filtered'])) * dt_ns
    t_filt_display = t_filt[t_filt <= t_max]
    mask_filt = t_filt <= t_max
    ax5.plot(t_filt_display, result['signal_filtered'][mask_filt], color=colors['filter'], lw=1.5, alpha=0.8)
    ax5.axhline(0, color='#2a2f42', lw=0.8, alpha=0.5)
    ax5.set_ylabel("Amplitude", fontsize=10, color="#c8d0e0", fontweight='bold')
    ax5.set_title("5. Bandpass Filter (150-800 MHz)", fontsize=11, color=colors['filter'], fontweight='bold')
    ax5.grid(True, color="#2a2f42", alpha=0.3)
    ax5.tick_params(colors="#c8d0e0", labelsize=9)
    for spine in ax5.spines.values():
        spine.set_color("#2a2f42")

    ax6 = fig.add_subplot(gs[2, 1])
    ax6.set_facecolor("#1a1e2b")
    t_trunc = np.arange(len(result['signal_truncated'])) * dt_ns
    t_trunc_display = t_trunc[t_trunc <= t_max]
    mask_trunc = t_trunc <= t_max
    ax6.plot(t_trunc_display, result['signal_truncated'][mask_trunc], color=colors['truncate'], lw=1.5, alpha=0.8)
    ax6.axhline(0, color='#2a2f42', lw=0.8, alpha=0.5)
    ax6.set_ylabel("Amplitude (normalized)", fontsize=10, color="#c8d0e0", fontweight='bold')
    ax6.set_title("6. Truncation (50 ns window)", fontsize=11, color=colors['truncate'], fontweight='bold')
    ax6.grid(True, color="#2a2f42", alpha=0.3)
    ax6.tick_params(colors="#c8d0e0", labelsize=9)
    for spine in ax6.spines.values():
        spine.set_color("#2a2f42")

    # ========================================================================
    # Row 4: Analytic Envelope (Final)
    # ========================================================================

    ax7 = fig.add_subplot(gs[3, :])
    ax7.set_facecolor("#1a1e2b")

    t_env = np.arange(len(result['signal_envelope'])) * dt_ns
    t_env_display = t_env[t_env <= t_max]
    mask_env = t_env <= t_max

    ax7.plot(t_env_display, result['signal_envelope'][mask_env], color=colors['envelope'], lw=2, alpha=0.9,
            label="Analytic Envelope (Hilbert)")
    ax7.fill_between(t_env_display, 0, result['signal_envelope'][mask_env], color=colors['envelope'], alpha=0.2)
    ax7.axhline(0, color='#2a2f42', lw=0.8, alpha=0.5)
    ax7.set_xlabel("Time (ns)", fontsize=11, color="#c8d0e0", fontweight='bold')
    ax7.set_ylabel("Envelope Amplitude", fontsize=11, color="#c8d0e0", fontweight='bold')
    ax7.set_title("7. Analytic Envelope (Hilbert Transform)", fontsize=12, color=colors['envelope'], fontweight='bold')
    ax7.grid(True, color="#2a2f42", alpha=0.3)
    ax7.legend(fontsize=10, facecolor='#1a1e2b', labelcolor='#c8d0e0', edgecolor='#2a2f42', loc='upper right')
    ax7.tick_params(colors="#c8d0e0", labelsize=10)
    for spine in ax7.spines.values():
        spine.set_color("#2a2f42")

    # Title
    fig.suptitle(
        "Vivanco Signal Processing Pipeline\n"
        "Complete 7-step transformation from raw to envelope",
        color="#c8d0e0", fontsize=13, fontweight='bold', y=0.995
    )

    png_path = Path("output_test") / "vivanco_pipeline_steps.png"
    fig.savefig(png_path, dpi=150, bbox_inches='tight', facecolor="#0f1117")
    print(f"[SAVE] {png_path}\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())

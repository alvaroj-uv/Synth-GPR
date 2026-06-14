"""
Visualization: Raw GPR A-scan vs. processed with 3 first-break methods.

Shows how each first-break picking algorithm performs and the resulting
time-zero corrected traces side-by-side.
"""
import sys
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
import matplotlib

# Use non-interactive backend for headless environments
matplotlib.use('Agg')

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.signal_processing import (
    detect_first_break,
    time_zero_correction,
    dewow,
    remove_direct_wave,
)


def create_realistic_gpr_trace(noise_level=0.2, dt=0.1e-9):
    """
    Create a realistic GPR A-scan with:
    - Direct pulse (antenna + air-ballast coupling)
    - Weak subsurface reflections
    - Field-like noise
    """
    np.random.seed(42)
    n = 400
    t = np.arange(n)

    # White noise baseline (field-like)
    noise = noise_level * np.random.randn(n)

    # === DIRECT PULSE (dominant, early) ===
    # Simulates the strong antenna + air-ballast surface reflection
    # Peaks around t=50 samples
    t_direct = t - 50
    width_direct = 25
    direct_pulse = 3.5 * (1 - 2 * (np.pi * t_direct / width_direct) ** 2) * np.exp(-(np.pi * t_direct / width_direct) ** 2)
    direct_pulse[t < 30] = 0  # causality
    direct_pulse[t > 90] = 0  # decay

    # === FIRST REFLECTION (weak, medium depth) ===
    # Subsurface reflection from ballast-subgrade interface
    # Peaks around t=180
    t_refl1 = t - 180
    width_refl = 20
    reflection1 = 0.6 * (1 - 2 * (np.pi * t_refl1 / width_refl) ** 2) * np.exp(-(np.pi * t_refl1 / width_refl) ** 2)
    reflection1[t < 160] = 0
    reflection1[t > 200] = 0

    # === SECOND REFLECTION (even weaker, deep) ===
    t_refl2 = t - 300
    reflection2 = 0.25 * (1 - 2 * (np.pi * t_refl2 / width_refl) ** 2) * np.exp(-(np.pi * t_refl2 / width_refl) ** 2)
    reflection2[t < 280] = 0
    reflection2[t > 320] = 0

    # Combine all
    raw_signal = noise + direct_pulse + reflection1 + reflection2

    return raw_signal, dt


def main():
    # Create realistic GPR trace
    raw_signal, dt = create_realistic_gpr_trace(noise_level=0.15)
    time_ns = np.arange(len(raw_signal)) * dt * 1e9

    # Remove direct wave for the preprocessed versions
    # (using time gating, which is quick and works for all methods)
    gated_signal = remove_direct_wave(raw_signal, dt, method='time_gate',
                                      center_freq_hz=400e6, air_gap_m=0.3)
    dewowd_gated = dewow(gated_signal, window_size=50)

    # Detect first break with all 3 methods
    print("=" * 70)
    print("FIRST-BREAK PICKING COMPARISON")
    print("=" * 70)

    fb_sta = detect_first_break(dewowd_gated, method='sta_lta', sta_lta_threshold=1.5)
    fb_cop = detect_first_break(dewowd_gated, method='coppens', coppens_threshold=1.0)
    fb_thr = detect_first_break(dewowd_gated, method='threshold', threshold_ratio=0.1)

    print(f"\nRaw signal properties:")
    print(f"  Length:      {len(raw_signal)} samples")
    print(f"  Sampling:    {1/dt*1e-9:.1f} GHz ({dt*1e9:.3f} ns)")
    print(f"  Duration:    {len(raw_signal) * dt * 1e9:.1f} ns")
    print(f"  Amplitude:   [{raw_signal.min():.3f}, {raw_signal.max():.3f}]")

    print(f"\nFirst-break picks (after dewow + time gating):")
    print(f"  STA/LTA:    sample {fb_sta:3d} ({fb_sta * dt * 1e9:.2f} ns) [RECOMMENDED]")
    print(f"  Coppens:    sample {fb_cop:3d} ({fb_cop * dt * 1e9:.2f} ns)")
    print(f"  Threshold:  sample {fb_thr:3d} ({fb_thr * dt * 1e9:.2f} ns)")

    # Time-zero corrected versions
    proc_sta = time_zero_correction(dewowd_gated, fb_sta)
    proc_cop = time_zero_correction(dewowd_gated, fb_cop)
    proc_thr = time_zero_correction(dewowd_gated, fb_thr)

    # =========================================================================
    # VISUALIZATION
    # =========================================================================
    fig = plt.figure(figsize=(16, 10))
    gs = fig.add_gridspec(3, 3, hspace=0.35, wspace=0.3)

    # ─────────────────────────────────────────────────────────────────────────
    # ROW 1: RAW SIGNAL + PICKS
    # ─────────────────────────────────────────────────────────────────────────

    ax = fig.add_subplot(gs[0, :])
    ax.plot(time_ns, raw_signal, 'k-', linewidth=1.5, label='Raw A-scan')
    ax.axvline(fb_sta * dt * 1e9, color='blue', linestyle='--', linewidth=2, label=f'STA/LTA: {fb_sta}')
    ax.axvline(fb_cop * dt * 1e9, color='green', linestyle='--', linewidth=2, label=f'Coppens: {fb_cop}')
    ax.axvline(fb_thr * dt * 1e9, color='red', linestyle='--', linewidth=2, label=f'Threshold: {fb_thr}')

    # Annotate main features
    ax.axvspan(30, 90, alpha=0.1, color='orange', label='Direct pulse region')
    ax.axvspan(160, 200, alpha=0.1, color='cyan', label='1st reflection')
    ax.axvspan(280, 320, alpha=0.1, color='purple', label='2nd reflection')

    ax.set_xlabel('Time (ns)', fontsize=11)
    ax.set_ylabel('Amplitude', fontsize=11)
    ax.set_title('RAW GPR A-SCAN (with first-break picks)', fontsize=12, fontweight='bold')
    ax.legend(loc='upper right', fontsize=9, ncol=3)
    ax.grid(True, alpha=0.3, linestyle=':')
    ax.set_xlim(time_ns[0], time_ns[-1])

    # ─────────────────────────────────────────────────────────────────────────
    # ROW 2: AFTER DIRECT WAVE REMOVAL + DEWOW
    # ─────────────────────────────────────────────────────────────────────────

    ax = fig.add_subplot(gs[1, :])
    ax.plot(time_ns, dewowd_gated, 'purple', linewidth=1.2, label='After time-gate + dewow')
    ax.axvline(fb_sta * dt * 1e9, color='blue', linestyle='--', linewidth=1.5, alpha=0.8)
    ax.axvline(fb_cop * dt * 1e9, color='green', linestyle='--', linewidth=1.5, alpha=0.8)
    ax.axvline(fb_thr * dt * 1e9, color='red', linestyle='--', linewidth=1.5, alpha=0.8)
    ax.fill_between(time_ns, dewowd_gated, alpha=0.2, color='purple')

    ax.set_xlabel('Time (ns)', fontsize=11)
    ax.set_ylabel('Amplitude', fontsize=11)
    ax.set_title('PREPROCESSED (direct wave removed, low-freq removed)', fontsize=12, fontweight='bold')
    ax.grid(True, alpha=0.3, linestyle=':')
    ax.set_xlim(time_ns[0], time_ns[-1])

    # ─────────────────────────────────────────────────────────────────────────
    # ROW 3: TIME-ZERO CORRECTED (3 VERSIONS SIDE BY SIDE)
    # ─────────────────────────────────────────────────────────────────────────

    titles = [
        f'STA/LTA\n(sample {fb_sta} → 0)',
        f'Coppens\n(sample {fb_cop} → 0)',
        f'Threshold\n(sample {fb_thr} → 0)',
    ]
    colors = ['blue', 'green', 'red']
    processed_sigs = [proc_sta, proc_cop, proc_thr]

    for col, (title, color, proc_sig) in enumerate(zip(titles, colors, processed_sigs)):
        ax = fig.add_subplot(gs[2, col])
        ax.plot(time_ns, proc_sig, color=color, linewidth=1.2)
        ax.fill_between(time_ns, proc_sig, alpha=0.2, color=color)
        ax.axvline(0, color='k', linestyle=':', linewidth=1.5, alpha=0.7, label='t=0 (pulse aligned)')

        ax.set_xlabel('Time (ns)', fontsize=10)
        ax.set_ylabel('Amplitude', fontsize=10)
        ax.set_title(title, fontsize=11, fontweight='bold', color=color)
        ax.grid(True, alpha=0.3, linestyle=':')
        ax.set_xlim(time_ns[0], time_ns[-1])

        # Mark reflections
        if col == 0:
            ax.text(0.02, 0.95, 'Pulse at t=0', transform=ax.transAxes,
                   fontsize=9, va='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3))

    # Overall title
    fig.suptitle('GPR A-Scan: Raw vs. 3 First-Break Picking Methods',
                 fontsize=14, fontweight='bold', y=0.995)

    # Save figure
    output_path = 'gpr_ascan_comparison.png'
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"\n[OK] Saved comparison plot to: {output_path}")

    # Print summary table
    print("\n" + "=" * 70)
    print("SUMMARY TABLE")
    print("=" * 70)
    print(f"{'Method':<15} {'Pick (sample)':<15} {'Pick (ns)':<15} {'Comment':<25}")
    print("-" * 70)
    print(f"{'STA/LTA':<15} {fb_sta:<15} {fb_sta * dt * 1e9:<15.2f} {'Recommended':<25}")
    print(f"{'Coppens':<15} {fb_cop:<15} {fb_cop * dt * 1e9:<15.2f} {'Energy-ratio':<25}")
    print(f"{'Threshold':<15} {fb_thr:<15} {fb_thr * dt * 1e9:<15.2f} {'Amplitude-based':<25}")
    print("=" * 70)

    return output_path


if __name__ == '__main__':
    output = main()
    print(f"\nVisualization saved to: {output}")

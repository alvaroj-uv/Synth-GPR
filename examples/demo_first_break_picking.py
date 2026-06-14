"""
Demo: First-break picking with Coppens, STA/LTA, and threshold methods.

This example shows how to use the three first-break detection algorithms
on synthetic GPR traces and compare their performance.
"""
import sys
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt

# Add parent directory to path so we can import src
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.signal_processing import (
    detect_first_break,
    preprocess_signal,
    dewow,
)


def create_demo_trace(noise_level=0.1):
    """Create a synthetic GPR A-scan for demonstration."""
    np.random.seed(42)
    n = 400
    t = np.arange(n)
    dt = 0.1e-9  # 0.1 ns (field data sampling)

    # Noise baseline
    noise = noise_level * np.random.randn(n)

    # Direct pulse (Ricker wavelet, peaks at t≈60)
    t_pulse = t - 60
    pulse_width = 30
    direct = 2.0 * (1 - 2 * (np.pi * t_pulse / pulse_width) ** 2) * np.exp(-(np.pi * t_pulse / pulse_width) ** 2)
    direct[t < 40] = 0

    # Weak reflection (peaks at t≈200)
    t_refl = t - 200
    reflection = 0.4 * (1 - 2 * (np.pi * t_refl / pulse_width) ** 2) * np.exp(-(np.pi * t_refl / pulse_width) ** 2)
    reflection[t < 170] = 0

    return noise + direct + reflection, dt


def main():
    # Generate trace
    signal, dt = create_demo_trace(noise_level=0.15)

    # Detect first break with three methods
    print("=" * 60)
    print("First-Break Picking Comparison")
    print("=" * 60)

    fb_sta_lta = detect_first_break(signal, method='sta_lta', sta_lta_threshold=1.5)
    fb_coppens = detect_first_break(signal, method='coppens', coppens_threshold=1.0)
    fb_threshold = detect_first_break(signal, method='threshold', threshold_ratio=0.1)

    print(f"\nSTA/LTA pick:    sample {fb_sta_lta:3d} ({fb_sta_lta * dt * 1e9:.2f} ns)")
    print(f"Coppens pick:    sample {fb_coppens:3d} ({fb_coppens * dt * 1e9:.2f} ns)")
    print(f"Threshold pick:  sample {fb_threshold:3d} ({fb_threshold * dt * 1e9:.2f} ns)")

    # Preprocess with default (STA/LTA)
    print("\n" + "=" * 60)
    print("Full Preprocessing Chain (default STA/LTA)")
    print("=" * 60)
    processed, start_idx = preprocess_signal(signal, dt)
    print(f"First break detected at sample: {start_idx}")
    print(f"Trace shifted to start at sample: 0")
    print(f"Output range: [{processed.min():.4f}, {processed.max():.4f}]")

    # Visualization
    fig, axes = plt.subplots(2, 2, figsize=(12, 8))

    # Raw signal with picks
    ax = axes[0, 0]
    t_ns = np.arange(len(signal)) * dt * 1e9
    ax.plot(t_ns, signal, 'k-', linewidth=1, label='Raw signal')
    ax.axvline(fb_sta_lta * dt * 1e9, color='blue', linestyle='--', label=f'STA/LTA: {fb_sta_lta}')
    ax.axvline(fb_coppens * dt * 1e9, color='green', linestyle='--', label=f'Coppens: {fb_coppens}')
    ax.axvline(fb_threshold * dt * 1e9, color='red', linestyle='--', label=f'Threshold: {fb_threshold}')
    ax.set_xlabel('Time (ns)')
    ax.set_ylabel('Amplitude')
    ax.set_title('First-Break Picks')
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

    # Dewowd signal
    ax = axes[0, 1]
    dewowd = dewow(signal)
    ax.plot(t_ns, dewowd, 'g-', linewidth=1)
    ax.axvline(fb_sta_lta * dt * 1e9, color='blue', linestyle='--', alpha=0.7)
    ax.set_xlabel('Time (ns)')
    ax.set_ylabel('Amplitude')
    ax.set_title('After Dewow')
    ax.grid(True, alpha=0.3)

    # Energy ratio (Coppens diagnostic)
    ax = axes[1, 0]
    short_win, long_win = 15, 100
    power = signal ** 2
    short_energy = np.convolve(power, np.ones(short_win) / short_win, mode='same')
    long_energy = np.convolve(power, np.ones(long_win) / long_win, mode='same')
    long_energy = np.maximum(long_energy, 1e-12)
    ratio = short_energy / long_energy
    ax.plot(t_ns, ratio, 'purple', linewidth=1, label='Energy ratio')
    ax.axhline(1.0, color='k', linestyle=':', alpha=0.5, label='Threshold = 1.0')
    ax.axvline(fb_coppens * dt * 1e9, color='green', linestyle='--', alpha=0.7)
    ax.set_xlabel('Time (ns)')
    ax.set_ylabel('Short/Long Energy Ratio')
    ax.set_title('Coppens Energy Ratio')
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

    # Preprocessed signal
    ax = axes[1, 1]
    t_proc = np.arange(len(processed)) * dt * 1e9
    ax.plot(t_proc, processed, 'b-', linewidth=1)
    ax.set_xlabel('Time (ns)')
    ax.set_ylabel('Amplitude')
    ax.set_title('After Full Preprocessing')
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('first_break_comparison.png', dpi=150)
    print("\n[OK] Saved visualization to: first_break_comparison.png")
    plt.show()


if __name__ == '__main__':
    main()

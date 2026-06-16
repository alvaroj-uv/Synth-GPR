#!/usr/bin/env python3
"""
Iterate over different direct wave cutoff points to find optimal.
Tests different sample offsets after peak to find best coda isolation.
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


def analyze_cutoff(signal: np.ndarray, peak_idx: int, shift_samples: int, dt_ns: float) -> dict:
    """
    Analyze signal after cutting at peak + shift_samples.

    Returns metrics:
    - dw_energy: Energy still in direct wave region (first 100 samples)
    - coda_energy: Energy in remaining signal
    - coda_peak: Peak amplitude of coda
    - coda_mean: Mean amplitude of coda
    - dw_suppression: How much DW energy is removed (0-1, higher is better)
    - coda_samples: Number of coda samples
    - coda_duration_ns: Duration of coda in ns
    """

    # Cut signal
    new_start_idx = peak_idx + shift_samples
    if new_start_idx >= len(signal):
        return None

    signal_cut = signal[new_start_idx:]

    # Normalize by peak amplitude for comparison
    peak_amp = np.max(np.abs(signal[:peak_idx+50]))  # Peak in DW region

    signal_norm = signal / peak_amp
    signal_cut_norm = signal_cut / peak_amp

    # DW energy: first 100 samples after cut (should be low for good cutoff)
    dw_remnant = np.sum(np.abs(signal_cut_norm[:min(100, len(signal_cut_norm))]))

    # Coda energy: entire remaining signal
    coda_energy = np.sum(np.abs(signal_cut_norm))
    coda_peak = np.max(np.abs(signal_cut_norm))
    coda_mean = np.mean(np.abs(signal_cut_norm))

    # Compute envelope
    analytic = hilbert(signal_cut)
    envelope = np.abs(analytic)
    envelope_norm = envelope / peak_amp
    envelope_peak = np.max(envelope_norm)

    # Metrics
    coda_samples = len(signal_cut)
    coda_duration_ns = (coda_samples - 1) * dt_ns

    # DW suppression: how much of the original DW energy is removed
    # Calculate energy in first 100 samples of cut signal vs original
    dw_original = np.sum(np.abs(signal_norm[:100]))
    dw_suppression = max(0, 1.0 - (dw_remnant / dw_original)) if dw_original > 0 else 1.0

    return {
        'shift_samples': shift_samples,
        'shift_ns': shift_samples * dt_ns,
        'new_start_idx': new_start_idx,
        'coda_samples': coda_samples,
        'coda_duration_ns': coda_duration_ns,
        'dw_suppression': dw_suppression,
        'coda_energy': coda_energy,
        'coda_peak': coda_peak,
        'coda_mean': coda_mean,
        'envelope_peak': envelope_peak,
    }


def main():
    # Load synthetic
    out_path = Path("output_test/ballast_eps51_optimized.out")
    signal, dt_ns = read_synthetic_file(out_path)

    t_ns = np.arange(len(signal)) * dt_ns

    print(f"[LOAD] {out_path.name}")
    print(f"  Samples: {len(signal)}")
    print(f"  dt: {dt_ns:.6f} ns")
    print(f"  Duration: {(len(signal)-1)*dt_ns:.2f} ns\n")

    # Find DW peak
    search_ns = 20
    search_idx = int(search_ns / dt_ns)
    peak_idx = np.argmax(np.abs(signal[:search_idx]))
    peak_time = t_ns[peak_idx]
    peak_value = signal[peak_idx]

    print(f"Direct Wave Peak:")
    print(f"  Index: {peak_idx}")
    print(f"  Time: {peak_time:.4f} ns")
    print(f"  Amplitude: {abs(peak_value):.2f} V/m\n")

    # Iterate over different cutoff points
    shift_samples_range = range(0, 751, 50)  # Test 0, 50, 100, ..., 750 samples

    results = []

    print(f"{'='*90}")
    print("ITERATING OVER CUTOFF POINTS")
    print(f"{'='*90}\n")

    print(f"{'Shift':<12} {'Time':<12} {'Samples':<12} {'Duration':<12} {'DW Supp':<12} {'Coda Peak':<12}")
    print(f"{'(samples)':<12} {'(ns)':<12} {'(remaining)':<12} {'(ns)':<12} {'(0-1)':<12} {'(norm)':<12}")
    print("-" * 90)

    for shift_samples in shift_samples_range:
        result = analyze_cutoff(signal, peak_idx, shift_samples, dt_ns)

        if result is None:
            break

        results.append(result)

        print(f"{shift_samples:<12} {result['shift_ns']:<12.2f} {result['coda_samples']:<12} "
              f"{result['coda_duration_ns']:<12.2f} {result['dw_suppression']:<12.4f} "
              f"{result['coda_peak']:<12.4f}")

    print()

    # Find best by different metrics
    print(f"{'='*90}")
    print("OPTIMIZATION RESULTS")
    print(f"{'='*90}\n")

    best_suppression = max(results, key=lambda x: x['dw_suppression'])
    best_coda_peak = max(results, key=lambda x: x['coda_peak'])
    best_envelope = max(results, key=lambda x: x['envelope_peak'])

    print(f"Best DW Suppression (remove all DW):")
    print(f"  Shift: {best_suppression['shift_samples']} samples ({best_suppression['shift_ns']:.2f} ns)")
    print(f"  Suppression: {best_suppression['dw_suppression']:.4f}")
    print(f"  Coda peak: {best_suppression['coda_peak']:.4f}\n")

    print(f"Best Coda Peak Preservation:")
    print(f"  Shift: {best_coda_peak['shift_samples']} samples ({best_coda_peak['shift_ns']:.2f} ns)")
    print(f"  Coda peak: {best_coda_peak['coda_peak']:.4f}")
    print(f"  DW suppression: {best_coda_peak['dw_suppression']:.4f}\n")

    print(f"Best Envelope Peak:")
    print(f"  Shift: {best_envelope['shift_samples']} samples ({best_envelope['shift_ns']:.2f} ns)")
    print(f"  Envelope peak: {best_envelope['envelope_peak']:.4f}")
    print(f"  Coda peak: {best_envelope['coda_peak']:.4f}\n")

    # ========================================================================
    # Visualization
    # ========================================================================

    fig = plt.figure(figsize=(18, 12))
    fig.patch.set_facecolor("#0f1117")
    gs = gridspec.GridSpec(3, 3, figure=fig, hspace=0.35, wspace=0.35,
                          left=0.08, right=0.95, top=0.96, bottom=0.06)

    # Select key cutoff points to visualize
    selected_indices = [0, 100, 250, 400, 550, 700]
    selected_results = [r for r in results if r['shift_samples'] in selected_indices]

    for plot_idx, result in enumerate(selected_results):
        if plot_idx >= 6:
            break

        ax = fig.add_subplot(gs[plot_idx // 3, plot_idx % 3])
        ax.set_facecolor("#1a1e2b")

        # Cut signal
        new_start_idx = result['new_start_idx']
        signal_cut = signal[new_start_idx:]
        t_cut = np.arange(len(signal_cut)) * dt_ns

        # Plot
        ax.plot(t_cut[t_cut <= 50], signal_cut[t_cut <= 50], color="#00d9ff", lw=1.2, alpha=0.8,
               label="Coda signal")

        # Envelope
        analytic = hilbert(signal_cut)
        envelope = np.abs(analytic)
        ax.plot(t_cut[t_cut <= 50], envelope[t_cut <= 50], color="#00ff88", lw=2, alpha=0.7,
               label="Envelope")

        ax.axhline(0, color='#2a2f42', lw=0.8, alpha=0.5)

        # Title with metrics
        title = (f"Shift: {result['shift_samples']} samp ({result['shift_ns']:.2f} ns)\n"
                f"DW Supp: {result['dw_suppression']:.3f} | Peak: {result['coda_peak']:.4f}")
        ax.set_title(title, fontsize=10, color="#c8d0e0", fontweight='bold')

        ax.set_ylabel("Amplitude (V/m)", fontsize=9, color="#c8d0e0", fontweight='bold')
        ax.set_xlabel("Time (ns)", fontsize=9, color="#c8d0e0", fontweight='bold')
        ax.grid(True, color="#2a2f42", alpha=0.3)
        ax.legend(fontsize=8, facecolor='#1a1e2b', labelcolor='#c8d0e0', edgecolor='#2a2f42')
        ax.tick_params(colors="#c8d0e0", labelsize=8)

        for spine in ax.spines.values():
            spine.set_color("#2a2f42")

    fig.suptitle(
        "Iterate Direct Wave Cutoff Point (Synthetic 420 MHz Ballast)\n"
        "Find optimal sample offset after peak for coda isolation",
        color="#c8d0e0", fontsize=13, fontweight='bold', y=0.995
    )

    png_path = Path("output_test") / "iterate_dw_cutoff.png"
    fig.savefig(png_path, dpi=150, bbox_inches='tight', facecolor="#0f1117")
    print(f"[SAVE] {png_path}\n")

    # ========================================================================
    # Plot metrics vs cutoff
    # ========================================================================

    fig2, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig2.patch.set_facecolor("#0f1117")

    shifts = [r['shift_samples'] for r in results]
    shifts_ns = [r['shift_ns'] for r in results]
    dw_supp = [r['dw_suppression'] for r in results]
    coda_peaks = [r['coda_peak'] for r in results]
    envelope_peaks = [r['envelope_peak'] for r in results]

    # Plot 1: DW Suppression
    ax = axes[0, 0]
    ax.set_facecolor("#1a1e2b")
    ax.plot(shifts, dw_supp, color="#ff6b35", lw=2.5, marker='o', markersize=6, alpha=0.8)
    ax.scatter([best_suppression['shift_samples']], [best_suppression['dw_suppression']],
              color='#ffff00', s=200, marker='*', edgecolor='white', linewidth=2, zorder=5)
    ax.set_xlabel("Shift (samples)", fontsize=11, color="#c8d0e0", fontweight='bold')
    ax.set_ylabel("DW Suppression (0-1)", fontsize=11, color="#c8d0e0", fontweight='bold')
    ax.set_title("Direct Wave Suppression", fontsize=12, color="#ff6b35", fontweight='bold')
    ax.grid(True, color="#2a2f42", alpha=0.3)
    ax.tick_params(colors="#c8d0e0")
    for spine in ax.spines.values():
        spine.set_color("#2a2f42")

    # Plot 2: Coda Peak
    ax = axes[0, 1]
    ax.set_facecolor("#1a1e2b")
    ax.plot(shifts, coda_peaks, color="#00ff88", lw=2.5, marker='o', markersize=6, alpha=0.8)
    ax.scatter([best_coda_peak['shift_samples']], [best_coda_peak['coda_peak']],
              color='#ffff00', s=200, marker='*', edgecolor='white', linewidth=2, zorder=5)
    ax.set_xlabel("Shift (samples)", fontsize=11, color="#c8d0e0", fontweight='bold')
    ax.set_ylabel("Coda Peak Amplitude", fontsize=11, color="#c8d0e0", fontweight='bold')
    ax.set_title("Coda Peak Preservation", fontsize=12, color="#00ff88", fontweight='bold')
    ax.grid(True, color="#2a2f42", alpha=0.3)
    ax.tick_params(colors="#c8d0e0")
    for spine in ax.spines.values():
        spine.set_color("#2a2f42")

    # Plot 3: Envelope Peak
    ax = axes[1, 0]
    ax.set_facecolor("#1a1e2b")
    ax.plot(shifts, envelope_peaks, color="#00d9ff", lw=2.5, marker='o', markersize=6, alpha=0.8)
    ax.scatter([best_envelope['shift_samples']], [best_envelope['envelope_peak']],
              color='#ffff00', s=200, marker='*', edgecolor='white', linewidth=2, zorder=5)
    ax.set_xlabel("Shift (samples)", fontsize=11, color="#c8d0e0", fontweight='bold')
    ax.set_ylabel("Envelope Peak", fontsize=11, color="#c8d0e0", fontweight='bold')
    ax.set_title("Analytic Envelope Peak", fontsize=12, color="#00d9ff", fontweight='bold')
    ax.grid(True, color="#2a2f42", alpha=0.3)
    ax.tick_params(colors="#c8d0e0")
    for spine in ax.spines.values():
        spine.set_color("#2a2f42")

    # Plot 4: Combined score (normalize and combine metrics)
    ax = axes[1, 1]
    ax.set_facecolor("#1a1e2b")

    # Combined score: balance between DW suppression and coda preservation
    dw_supp_norm = np.array(dw_supp)  # Already 0-1
    coda_peaks_norm = np.array(coda_peaks) / max(coda_peaks)
    combined_score = 0.5 * dw_supp_norm + 0.5 * coda_peaks_norm

    best_combined_idx = np.argmax(combined_score)
    best_combined = results[best_combined_idx]

    ax.plot(shifts, combined_score, color="#ff00ff", lw=2.5, marker='o', markersize=6, alpha=0.8,
           label="Combined score")
    ax.scatter([best_combined['shift_samples']], [combined_score[best_combined_idx]],
              color='#ffff00', s=200, marker='*', edgecolor='white', linewidth=2, zorder=5,
              label=f"Best @ {best_combined['shift_samples']} samp")
    ax.set_xlabel("Shift (samples)", fontsize=11, color="#c8d0e0", fontweight='bold')
    ax.set_ylabel("Combined Score", fontsize=11, color="#c8d0e0", fontweight='bold')
    ax.set_title("Combined Score (50% DW Supp + 50% Coda Peak)", fontsize=12,
                color="#ff00ff", fontweight='bold')
    ax.grid(True, color="#2a2f42", alpha=0.3)
    ax.legend(fontsize=10, facecolor='#1a1e2b', labelcolor='#c8d0e0', edgecolor='#2a2f42')
    ax.tick_params(colors="#c8d0e0")
    for spine in ax.spines.values():
        spine.set_color("#2a2f42")

    fig2.suptitle(
        "Cutoff Optimization Metrics vs Sample Offset",
        color="#c8d0e0", fontsize=13, fontweight='bold'
    )

    png_path2 = Path("output_test") / "iterate_dw_metrics.png"
    fig2.savefig(png_path2, dpi=150, bbox_inches='tight', facecolor="#0f1117")
    print(f"[SAVE] {png_path2}\n")

    # Print recommendation
    print(f"{'='*90}")
    print("RECOMMENDATION")
    print(f"{'='*90}\n")

    print(f"For MAXIMUM DW suppression (cleanest coda):")
    print(f"  Use {best_suppression['shift_samples']} samples ({best_suppression['shift_ns']:.2f} ns)\n")

    print(f"For MAXIMUM coda peak (preserve energy):")
    print(f"  Use {best_coda_peak['shift_samples']} samples ({best_coda_peak['shift_ns']:.2f} ns)\n")

    print(f"For BEST BALANCE (recommended):")
    print(f"  Use {best_combined['shift_samples']} samples ({best_combined['shift_ns']:.2f} ns)")
    print(f"  > DW suppression: {best_combined['dw_suppression']:.4f}")
    print(f"  > Coda peak: {best_combined['coda_peak']:.4f}\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())

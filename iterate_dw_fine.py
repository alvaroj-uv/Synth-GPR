#!/usr/bin/env python3
"""
Fine-grained iteration over direct wave cutoff points (10-sample increments).
Focus on 0-150 samples range.
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

    Returns metrics including early/late energy ratio.
    """

    # Cut signal
    new_start_idx = peak_idx + shift_samples
    if new_start_idx >= len(signal):
        return None

    signal_cut = signal[new_start_idx:]

    # Normalize by peak amplitude
    peak_amp = np.max(np.abs(signal[:peak_idx+100]))

    signal_cut_norm = signal_cut / peak_amp

    # Early energy (first 5 ns after cut - should be low if DW well removed)
    early_ns = 5.0
    early_idx = int(early_ns / dt_ns)
    early_idx = min(early_idx, len(signal_cut_norm))
    early_energy = np.sum(np.abs(signal_cut_norm[:early_idx]))

    # Mid energy (5-15 ns after cut)
    mid_start_idx = early_idx
    mid_end_idx = int(15.0 / dt_ns)
    mid_end_idx = min(mid_end_idx, len(signal_cut_norm))
    mid_energy = np.sum(np.abs(signal_cut_norm[mid_start_idx:mid_end_idx]))

    # Late energy (15+ ns after cut)
    late_energy = np.sum(np.abs(signal_cut_norm[mid_end_idx:]))

    # Total coda energy
    coda_energy = early_energy + mid_energy + late_energy

    # Compute envelope
    analytic = hilbert(signal_cut)
    envelope = np.abs(analytic)
    envelope_norm = envelope / peak_amp

    # Metrics
    coda_samples = len(signal_cut)
    coda_duration_ns = (coda_samples - 1) * dt_ns

    # Peak values
    coda_peak = np.max(np.abs(signal_cut_norm))
    early_peak = np.max(np.abs(signal_cut_norm[:early_idx])) if early_idx > 0 else 0
    envelope_peak = np.max(envelope_norm)

    # Ratio: early energy to total (should be LOW if DW well removed)
    early_ratio = early_energy / coda_energy if coda_energy > 0 else 0

    # Quality: how much coda is in mid+late vs early
    quality_score = (mid_energy + late_energy) / coda_energy if coda_energy > 0 else 0

    return {
        'shift_samples': shift_samples,
        'shift_ns': shift_samples * dt_ns,
        'new_start_idx': new_start_idx,
        'coda_samples': coda_samples,
        'coda_duration_ns': coda_duration_ns,
        'early_energy': early_energy,
        'mid_energy': mid_energy,
        'late_energy': late_energy,
        'coda_energy': coda_energy,
        'early_ratio': early_ratio,
        'quality_score': quality_score,
        'coda_peak': coda_peak,
        'early_peak': early_peak,
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

    # Fine iteration: 0-150 samples in steps of 10
    shift_samples_range = range(0, 151, 10)

    results = []

    print(f"{'='*110}")
    print("FINE-GRAINED ITERATION (10-sample steps)")
    print(f"{'='*110}\n")

    print(f"{'Shift':<12} {'Time':<12} {'Early E':<12} {'Mid E':<12} {'Late E':<12} "
          f"{'Early%':<12} {'Quality':<12} {'Coda Peak':<12}")
    print(f"{'(samp)':<12} {'(ns)':<12} {'(norm)':<12} {'(norm)':<12} {'(norm)':<12} "
          f"{'(0-1)':<12} {'(0-1)':<12} {'(norm)':<12}")
    print("-" * 110)

    for shift_samples in shift_samples_range:
        result = analyze_cutoff(signal, peak_idx, shift_samples, dt_ns)

        if result is None:
            break

        results.append(result)

        print(f"{shift_samples:<12} {result['shift_ns']:<12.2f} {result['early_energy']:<12.4f} "
              f"{result['mid_energy']:<12.4f} {result['late_energy']:<12.4f} "
              f"{result['early_ratio']:<12.4f} {result['quality_score']:<12.4f} "
              f"{result['coda_peak']:<12.4f}")

    print()

    # Find best by different criteria
    print(f"{'='*110}")
    print("OPTIMIZATION RESULTS (Fine-grained)")
    print(f"{'='*110}\n")

    best_quality = max(results, key=lambda x: x['quality_score'])
    best_low_early = min(results, key=lambda x: x['early_ratio'])
    best_peak = max(results, key=lambda x: x['coda_peak'])

    print(f"Best QUALITY (max coda in mid+late regions):")
    print(f"  Shift: {best_quality['shift_samples']} samples ({best_quality['shift_ns']:.3f} ns)")
    print(f"  Quality score: {best_quality['quality_score']:.4f}")
    print(f"  Early ratio: {best_quality['early_ratio']:.4f}")
    print(f"  Coda peak: {best_quality['coda_peak']:.4f}\n")

    print(f"Best DW SUPPRESSION (minimize early energy):")
    print(f"  Shift: {best_low_early['shift_samples']} samples ({best_low_early['shift_ns']:.3f} ns)")
    print(f"  Early ratio: {best_low_early['early_ratio']:.4f}")
    print(f"  Quality score: {best_low_early['quality_score']:.4f}")
    print(f"  Coda peak: {best_low_early['coda_peak']:.4f}\n")

    print(f"Best PEAK PRESERVATION (max coda amplitude):")
    print(f"  Shift: {best_peak['shift_samples']} samples ({best_peak['shift_ns']:.3f} ns)")
    print(f"  Coda peak: {best_peak['coda_peak']:.4f}")
    print(f"  Quality score: {best_peak['quality_score']:.4f}\n")

    # ========================================================================
    # Visualization: metrics curves
    # ========================================================================

    fig, axes = plt.subplots(2, 2, figsize=(16, 10))
    fig.patch.set_facecolor("#0f1117")

    shifts = [r['shift_samples'] for r in results]
    shifts_ns = [r['shift_ns'] for r in results]
    early_ratios = [r['early_ratio'] for r in results]
    quality_scores = [r['quality_score'] for r in results]
    coda_peaks = [r['coda_peak'] for r in results]
    envelope_peaks = [r['envelope_peak'] for r in results]

    # Plot 1: Early Energy Ratio (should be LOW)
    ax = axes[0, 0]
    ax.set_facecolor("#1a1e2b")
    ax.plot(shifts, early_ratios, color="#ff6b35", lw=2.5, marker='o', markersize=8, alpha=0.8)
    ax.scatter([best_low_early['shift_samples']], [best_low_early['early_ratio']],
              color='#ffff00', s=250, marker='*', edgecolor='white', linewidth=2, zorder=5)
    ax.axhline(0.2, color='#2a2f42', linestyle=':', linewidth=1.5, alpha=0.5, label='Threshold 20%')
    ax.set_xlabel("Shift (samples)", fontsize=12, color="#c8d0e0", fontweight='bold')
    ax.set_ylabel("Early Energy Ratio (0-1)", fontsize=12, color="#c8d0e0", fontweight='bold')
    ax.set_title("Early Energy Suppression (lower is better)", fontsize=12, color="#ff6b35", fontweight='bold')
    ax.grid(True, color="#2a2f42", alpha=0.3)
    ax.legend(fontsize=10, facecolor='#1a1e2b', labelcolor='#c8d0e0', edgecolor='#2a2f42')
    ax.tick_params(colors="#c8d0e0", labelsize=11)
    for spine in ax.spines.values():
        spine.set_color("#2a2f42")

    # Plot 2: Quality Score (high = good coda in mid+late)
    ax = axes[0, 1]
    ax.set_facecolor("#1a1e2b")
    ax.plot(shifts, quality_scores, color="#00ff88", lw=2.5, marker='s', markersize=8, alpha=0.8)
    ax.scatter([best_quality['shift_samples']], [best_quality['quality_score']],
              color='#ffff00', s=250, marker='*', edgecolor='white', linewidth=2, zorder=5)
    ax.set_xlabel("Shift (samples)", fontsize=12, color="#c8d0e0", fontweight='bold')
    ax.set_ylabel("Quality Score (0-1)", fontsize=12, color="#c8d0e0", fontweight='bold')
    ax.set_title("Coda Quality (mid+late energy ratio)", fontsize=12, color="#00ff88", fontweight='bold')
    ax.grid(True, color="#2a2f42", alpha=0.3)
    ax.tick_params(colors="#c8d0e0", labelsize=11)
    for spine in ax.spines.values():
        spine.set_color("#2a2f42")

    # Plot 3: Coda Peak
    ax = axes[1, 0]
    ax.set_facecolor("#1a1e2b")
    ax.plot(shifts, coda_peaks, color="#00d9ff", lw=2.5, marker='^', markersize=8, alpha=0.8)
    ax.scatter([best_peak['shift_samples']], [best_peak['coda_peak']],
              color='#ffff00', s=250, marker='*', edgecolor='white', linewidth=2, zorder=5)
    ax.set_xlabel("Shift (samples)", fontsize=12, color="#c8d0e0", fontweight='bold')
    ax.set_ylabel("Coda Peak Amplitude", fontsize=12, color="#c8d0e0", fontweight='bold')
    ax.set_title("Peak Preservation", fontsize=12, color="#00d9ff", fontweight='bold')
    ax.grid(True, color="#2a2f42", alpha=0.3)
    ax.tick_params(colors="#c8d0e0", labelsize=11)
    for spine in ax.spines.values():
        spine.set_color("#2a2f42")

    # Plot 4: Envelope Peak
    ax = axes[1, 1]
    ax.set_facecolor("#1a1e2b")
    ax.plot(shifts, envelope_peaks, color="#ff00ff", lw=2.5, marker='d', markersize=8, alpha=0.8)
    best_envelope_idx = np.argmax(envelope_peaks)
    ax.scatter([results[best_envelope_idx]['shift_samples']], [results[best_envelope_idx]['envelope_peak']],
              color='#ffff00', s=250, marker='*', edgecolor='white', linewidth=2, zorder=5)
    ax.set_xlabel("Shift (samples)", fontsize=12, color="#c8d0e0", fontweight='bold')
    ax.set_ylabel("Envelope Peak", fontsize=12, color="#c8d0e0", fontweight='bold')
    ax.set_title("Hilbert Envelope Peak", fontsize=12, color="#ff00ff", fontweight='bold')
    ax.grid(True, color="#2a2f42", alpha=0.3)
    ax.tick_params(colors="#c8d0e0", labelsize=11)
    for spine in ax.spines.values():
        spine.set_color("#2a2f42")

    fig.suptitle(
        "Fine-Grained Direct Wave Cutoff Optimization (0-150 samples)",
        color="#c8d0e0", fontsize=14, fontweight='bold'
    )

    png_path = Path("output_test") / "iterate_dw_fine_metrics.png"
    fig.savefig(png_path, dpi=150, bbox_inches='tight', facecolor="#0f1117")
    print(f"[SAVE] {png_path}\n")

    # ========================================================================
    # Visualization: sample waveforms at key points
    # ========================================================================

    key_shifts = [0, 10, 20, 30, 40, 50]
    key_results = [r for r in results if r['shift_samples'] in key_shifts]

    fig = plt.figure(figsize=(18, 10))
    fig.patch.set_facecolor("#0f1117")
    gs = gridspec.GridSpec(2, 3, figure=fig, hspace=0.3, wspace=0.35,
                          left=0.08, right=0.95, top=0.94, bottom=0.08)

    for plot_idx, result in enumerate(key_results):
        ax = fig.add_subplot(gs[plot_idx // 3, plot_idx % 3])
        ax.set_facecolor("#1a1e2b")

        # Cut signal
        new_start_idx = result['new_start_idx']
        signal_cut = signal[new_start_idx:]
        t_cut = np.arange(len(signal_cut)) * dt_ns

        # Plot signal
        mask = t_cut <= 30
        ax.plot(t_cut[mask], signal_cut[mask], color="#00d9ff", lw=1.2, alpha=0.8,
               label="Coda signal")

        # Envelope
        analytic = hilbert(signal_cut)
        envelope = np.abs(analytic)
        ax.plot(t_cut[mask], envelope[mask], color="#00ff88", lw=2.5, alpha=0.7,
               label="Envelope")

        # Mark energy regions
        early_ns = 5.0
        ax.axvline(early_ns, color='#ff6b35', linestyle='--', linewidth=2, alpha=0.5, label='Early end')
        ax.axvline(15.0, color='#ffaa00', linestyle='--', linewidth=2, alpha=0.5, label='Mid end')

        ax.axhline(0, color='#2a2f42', lw=0.8, alpha=0.5)

        # Title with metrics
        title = (f"Shift: {result['shift_samples']} samp ({result['shift_ns']:.2f} ns)\n"
                f"Quality: {result['quality_score']:.3f} | Early%: {result['early_ratio']:.3f} | "
                f"Peak: {result['coda_peak']:.3f}")
        ax.set_title(title, fontsize=10, color="#c8d0e0", fontweight='bold')

        ax.set_ylabel("Amplitude (V/m)", fontsize=9, color="#c8d0e0", fontweight='bold')
        ax.set_xlabel("Time (ns)", fontsize=9, color="#c8d0e0", fontweight='bold')
        ax.grid(True, color="#2a2f42", alpha=0.3)
        if plot_idx == 0:
            ax.legend(fontsize=8, facecolor='#1a1e2b', labelcolor='#c8d0e0', edgecolor='#2a2f42', loc='upper right')
        ax.tick_params(colors="#c8d0e0", labelsize=8)

        for spine in ax.spines.values():
            spine.set_color("#2a2f42")

    fig.suptitle(
        "Waveforms at Different Cutoff Points (0-50 samples)",
        color="#c8d0e0", fontsize=13, fontweight='bold'
    )

    png_path2 = Path("output_test") / "iterate_dw_fine_waveforms.png"
    fig.savefig(png_path2, dpi=150, bbox_inches='tight', facecolor="#0f1117")
    print(f"[SAVE] {png_path2}\n")

    # ========================================================================
    # Final recommendation
    # ========================================================================

    print(f"{'='*110}")
    print("FINAL RECOMMENDATION FOR SYNTHETIC DATA")
    print(f"{'='*110}\n")

    print(f"OPTION A: Maximum Quality (preserve coda in mid+late regions)")
    print(f"  Shift: {best_quality['shift_samples']} samples ({best_quality['shift_ns']:.3f} ns)")
    print(f"  Rationale: Best preservation of coda structure")
    print(f"  Use this for: Feature extraction, analysis\n")

    print(f"OPTION B: Best DW Suppression (minimal early energy)")
    print(f"  Shift: {best_low_early['shift_samples']} samples ({best_low_early['shift_ns']:.3f} ns)")
    print(f"  Rationale: Cleanest coda isolation")
    print(f"  Use this for: Extreme noise sensitivity\n")

    print(f"OPTION C: Maximum Peak Preservation")
    print(f"  Shift: {best_peak['shift_samples']} samples ({best_peak['shift_ns']:.3f} ns)")
    print(f"  Rationale: Maintain maximum signal energy")
    print(f"  Use this for: Energy-sensitive analysis\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())

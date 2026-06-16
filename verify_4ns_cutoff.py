#!/usr/bin/env python3
"""
Verify cutoff at 4 ns on the time axis.
Fine iteration around the visual optimum suggested by user.
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


def analyze_cutoff(signal: np.ndarray, cutoff_time_ns: float, dt_ns: float) -> dict:
    """
    Analyze signal after cutting at specific time point.
    """
    cutoff_idx = int(round(cutoff_time_ns / dt_ns))

    if cutoff_idx >= len(signal) or cutoff_idx < 0:
        return None

    signal_cut = signal[cutoff_idx:]

    # Normalize by peak amplitude
    peak_amp = np.max(np.abs(signal))
    signal_cut_norm = signal_cut / peak_amp

    # Compute metrics
    early_ns = 5.0
    early_idx = int(early_ns / dt_ns)
    early_idx = min(early_idx, len(signal_cut_norm))
    early_energy = np.sum(np.abs(signal_cut_norm[:early_idx]))

    mid_start_idx = early_idx
    mid_end_idx = int(15.0 / dt_ns)
    mid_end_idx = min(mid_end_idx, len(signal_cut_norm))
    mid_energy = np.sum(np.abs(signal_cut_norm[mid_start_idx:mid_end_idx]))

    late_energy = np.sum(np.abs(signal_cut_norm[mid_end_idx:]))

    coda_energy = early_energy + mid_energy + late_energy

    # Envelope
    analytic = hilbert(signal_cut)
    envelope = np.abs(analytic)
    envelope_norm = envelope / peak_amp

    # Metrics
    coda_samples = len(signal_cut)
    coda_duration_ns = (coda_samples - 1) * dt_ns

    coda_peak = np.max(np.abs(signal_cut_norm))
    early_peak = np.max(np.abs(signal_cut_norm[:early_idx])) if early_idx > 0 else 0
    envelope_peak = np.max(envelope_norm)

    early_ratio = early_energy / coda_energy if coda_energy > 0 else 0
    quality_score = (mid_energy + late_energy) / coda_energy if coda_energy > 0 else 0

    return {
        'cutoff_time_ns': cutoff_time_ns,
        'cutoff_idx': cutoff_idx,
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
    print(f"  dt: {dt_ns:.6f} ns\n")

    # Find DW peak
    search_ns = 20
    search_idx = int(search_ns / dt_ns)
    peak_idx = np.argmax(np.abs(signal[:search_idx]))
    peak_time = t_ns[peak_idx]

    print(f"Direct Wave Peak: {peak_time:.4f} ns (index {peak_idx})\n")

    # Iterate around 4 ns on time axis (0.1 ns increments)
    cutoff_times = np.arange(1.0, 7.0, 0.1)  # 1 to 7 ns in 0.1 ns steps

    results = []

    print(f"{'='*100}")
    print("FINE ITERATION AROUND 4 NS (time-axis cutoff)")
    print(f"{'='*100}\n")

    print(f"{'Time':<12} {'Index':<12} {'Early E':<12} {'Mid E':<12} {'Late E':<12} "
          f"{'Early%':<12} {'Quality':<12} {'Coda Peak':<12} {'Envelope':<12}")
    print(f"{'(ns)':<12} {'(sample#)':<12} {'(norm)':<12} {'(norm)':<12} {'(norm)':<12} "
          f"{'(0-1)':<12} {'(0-1)':<12} {'(norm)':<12} {'(norm)':<12}")
    print("-" * 100)

    for cutoff_time in cutoff_times:
        result = analyze_cutoff(signal, cutoff_time, dt_ns)

        if result is None:
            continue

        results.append(result)

        marker = " <-- 4.0 NS" if abs(cutoff_time - 4.0) < 0.01 else ""
        print(f"{cutoff_time:<12.1f} {result['cutoff_idx']:<12} {result['early_energy']:<12.4f} "
              f"{result['mid_energy']:<12.4f} {result['late_energy']:<12.4f} "
              f"{result['early_ratio']:<12.4f} {result['quality_score']:<12.4f} "
              f"{result['coda_peak']:<12.4f} {result['envelope_peak']:<12.4f}{marker}")

    print()

    # Find best
    best_quality = max(results, key=lambda x: x['quality_score'])
    best_low_early = min(results, key=lambda x: x['early_ratio'])

    print(f"{'='*100}")
    print("RESULTS AROUND 4 NS")
    print(f"{'='*100}\n")

    # Find result closest to 4 ns
    result_4ns = min(results, key=lambda x: abs(x['cutoff_time_ns'] - 4.0))

    print(f"AT 4.0 NS (user suggestion):")
    print(f"  Time: {result_4ns['cutoff_time_ns']:.1f} ns")
    print(f"  Index: {result_4ns['cutoff_idx']}")
    print(f"  Quality score: {result_4ns['quality_score']:.4f}")
    print(f"  Early ratio: {result_4ns['early_ratio']:.4f}")
    print(f"  Coda peak: {result_4ns['coda_peak']:.4f}")
    print(f"  Envelope peak: {result_4ns['envelope_peak']:.4f}\n")

    print(f"BEST QUALITY (overall):")
    print(f"  Time: {best_quality['cutoff_time_ns']:.1f} ns")
    print(f"  Quality score: {best_quality['quality_score']:.4f}")
    print(f"  Early ratio: {best_quality['early_ratio']:.4f}\n")

    print(f"BEST DW SUPPRESSION (overall):")
    print(f"  Time: {best_low_early['cutoff_time_ns']:.1f} ns")
    print(f"  Early ratio: {best_low_early['early_ratio']:.4f}")
    print(f"  Quality score: {best_low_early['quality_score']:.4f}\n")

    # ========================================================================
    # Visualization
    # ========================================================================

    fig, axes = plt.subplots(2, 2, figsize=(16, 10))
    fig.patch.set_facecolor("#0f1117")

    times = [r['cutoff_time_ns'] for r in results]
    quality_scores = [r['quality_score'] for r in results]
    early_ratios = [r['early_ratio'] for r in results]
    coda_peaks = [r['coda_peak'] for r in results]
    envelope_peaks = [r['envelope_peak'] for r in results]

    # Plot 1: Quality Score
    ax = axes[0, 0]
    ax.set_facecolor("#1a1e2b")
    ax.plot(times, quality_scores, color="#00ff88", lw=2.5, marker='o', markersize=8, alpha=0.8)
    ax.axvline(4.0, color='#ffff00', linestyle='--', linewidth=3, alpha=0.7, label='4.0 ns (suggested)')
    ax.scatter([result_4ns['cutoff_time_ns']], [result_4ns['quality_score']],
              color='#ffff00', s=250, marker='s', edgecolor='white', linewidth=2, zorder=5)
    ax.scatter([best_quality['cutoff_time_ns']], [best_quality['quality_score']],
              color='#00ff00', s=250, marker='*', edgecolor='white', linewidth=2, zorder=6)
    ax.set_xlabel("Cutoff Time (ns)", fontsize=12, color="#c8d0e0", fontweight='bold')
    ax.set_ylabel("Quality Score (0-1)", fontsize=12, color="#c8d0e0", fontweight='bold')
    ax.set_title("Coda Quality vs Cutoff Time", fontsize=12, color="#00ff88", fontweight='bold')
    ax.grid(True, color="#2a2f42", alpha=0.3)
    ax.legend(fontsize=10, facecolor='#1a1e2b', labelcolor='#c8d0e0', edgecolor='#2a2f42')
    ax.tick_params(colors="#c8d0e0", labelsize=10)
    for spine in ax.spines.values():
        spine.set_color("#2a2f42")

    # Plot 2: Early Ratio
    ax = axes[0, 1]
    ax.set_facecolor("#1a1e2b")
    ax.plot(times, early_ratios, color="#ff6b35", lw=2.5, marker='o', markersize=8, alpha=0.8)
    ax.axvline(4.0, color='#ffff00', linestyle='--', linewidth=3, alpha=0.7, label='4.0 ns (suggested)')
    ax.scatter([result_4ns['cutoff_time_ns']], [result_4ns['early_ratio']],
              color='#ffff00', s=250, marker='s', edgecolor='white', linewidth=2, zorder=5)
    ax.scatter([best_low_early['cutoff_time_ns']], [best_low_early['early_ratio']],
              color='#00ff00', s=250, marker='*', edgecolor='white', linewidth=2, zorder=6)
    ax.set_xlabel("Cutoff Time (ns)", fontsize=12, color="#c8d0e0", fontweight='bold')
    ax.set_ylabel("Early Energy Ratio (0-1)", fontsize=12, color="#c8d0e0", fontweight='bold')
    ax.set_title("DW Suppression vs Cutoff Time", fontsize=12, color="#ff6b35", fontweight='bold')
    ax.grid(True, color="#2a2f42", alpha=0.3)
    ax.legend(fontsize=10, facecolor='#1a1e2b', labelcolor='#c8d0e0', edgecolor='#2a2f42')
    ax.tick_params(colors="#c8d0e0", labelsize=10)
    for spine in ax.spines.values():
        spine.set_color("#2a2f42")

    # Plot 3: Coda Peak
    ax = axes[1, 0]
    ax.set_facecolor("#1a1e2b")
    ax.plot(times, coda_peaks, color="#00d9ff", lw=2.5, marker='o', markersize=8, alpha=0.8)
    ax.axvline(4.0, color='#ffff00', linestyle='--', linewidth=3, alpha=0.7, label='4.0 ns (suggested)')
    ax.scatter([result_4ns['cutoff_time_ns']], [result_4ns['coda_peak']],
              color='#ffff00', s=250, marker='s', edgecolor='white', linewidth=2, zorder=5)
    ax.set_xlabel("Cutoff Time (ns)", fontsize=12, color="#c8d0e0", fontweight='bold')
    ax.set_ylabel("Coda Peak", fontsize=12, color="#c8d0e0", fontweight='bold')
    ax.set_title("Peak Preservation vs Cutoff Time", fontsize=12, color="#00d9ff", fontweight='bold')
    ax.grid(True, color="#2a2f42", alpha=0.3)
    ax.legend(fontsize=10, facecolor='#1a1e2b', labelcolor='#c8d0e0', edgecolor='#2a2f42')
    ax.tick_params(colors="#c8d0e0", labelsize=10)
    for spine in ax.spines.values():
        spine.set_color("#2a2f42")

    # Plot 4: Envelope Peak
    ax = axes[1, 1]
    ax.set_facecolor("#1a1e2b")
    ax.plot(times, envelope_peaks, color="#ff00ff", lw=2.5, marker='o', markersize=8, alpha=0.8)
    ax.axvline(4.0, color='#ffff00', linestyle='--', linewidth=3, alpha=0.7, label='4.0 ns (suggested)')
    ax.scatter([result_4ns['cutoff_time_ns']], [result_4ns['envelope_peak']],
              color='#ffff00', s=250, marker='s', edgecolor='white', linewidth=2, zorder=5)
    ax.set_xlabel("Cutoff Time (ns)", fontsize=12, color="#c8d0e0", fontweight='bold')
    ax.set_ylabel("Envelope Peak", fontsize=12, color="#c8d0e0", fontweight='bold')
    ax.set_title("Hilbert Envelope Peak vs Cutoff Time", fontsize=12, color="#ff00ff", fontweight='bold')
    ax.grid(True, color="#2a2f42", alpha=0.3)
    ax.legend(fontsize=10, facecolor='#1a1e2b', labelcolor='#c8d0e0', edgecolor='#2a2f42')
    ax.tick_params(colors="#c8d0e0", labelsize=10)
    for spine in ax.spines.values():
        spine.set_color("#2a2f42")

    fig.suptitle(
        "Fine Analysis: Cutoff Time Around 4 ns (User Visual Suggestion)\n"
        "Yellow square = 4.0 ns | Green star = overall best",
        color="#c8d0e0", fontsize=14, fontweight='bold'
    )

    png_path = Path("output_test") / "verify_4ns_cutoff.png"
    fig.savefig(png_path, dpi=150, bbox_inches='tight', facecolor="#0f1117")
    print(f"[SAVE] {png_path}\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())

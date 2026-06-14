"""
Apply first-break picking to real EFE GPR signals from DZT files.

Uses the canonical read_dzt_traces function from dzt_io.py
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib

matplotlib.use('Agg')

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.signal_processing import (
    detect_first_break,
    dewow,
    remove_direct_wave,
)
from src.dzt_io import read_dzt_traces


def analyze_single_trace(trace: np.ndarray, dt: float, trace_idx: int):
    """
    Apply all 3 first-break methods to a single trace.

    Returns:
        results (dict): {'sta_lta': idx, 'coppens': idx, 'threshold': idx}
        preprocessed (ndarray): dewowd trace
    """
    # Preprocess: time gating + dewow
    gated = remove_direct_wave(trace, dt, method='time_gate',
                               center_freq_hz=400e6, air_gap_m=0.3)
    dewowd = dewow(gated, window_size=50)

    # Detect with all 3 methods
    fb_sta = detect_first_break(dewowd, method='sta_lta', sta_lta_threshold=1.5)
    fb_cop = detect_first_break(dewowd, method='coppens', coppens_threshold=1.0)
    fb_thr = detect_first_break(dewowd, method='threshold', threshold_ratio=0.1)

    results = {
        'trace_idx': trace_idx,
        'sta_lta': fb_sta,
        'coppens': fb_cop,
        'threshold': fb_thr,
    }

    return results, dewowd


def main():
    # ─────────────────────────────────────────────────────────────────────────
    # LOAD DATA
    # ─────────────────────────────────────────────────────────────────────────
    dzt_files = list(Path("d:/Codigo/Data").glob("*.dzt"))

    if not dzt_files:
        print("ERROR: No DZT files found in d:/Codigo/Data")
        return

    dzt_path = dzt_files[0]  # Use first file
    print(f"Using: {dzt_path.name}\n")

    # Use the canonical reader from dzt_io
    print("Loading with read_dzt_traces from dzt_io.py...")
    traces, metadata = read_dzt_traces(dzt_path, num_traces=100)

    print(f"  Loaded: {traces.shape[0]} traces, {traces.shape[1]} samples per trace")
    print(f"  Data type: {traces.dtype}")
    print(f"  Sample interval: {metadata['sample_interval_ns']:.4f} ns")
    print(f"  Antenna: {metadata['antenna_name']}")

    # Time step from metadata
    dt = metadata['sample_interval_ns'] * 1e-9  # Convert ns to seconds

    print(f"  Time step: {dt*1e9:.4f} ns")
    print(f"  Sampling: {1.0/dt/1e9:.2f} GHz\n")

    # ─────────────────────────────────────────────────────────────────────────
    # PROCESS TRACES
    # ─────────────────────────────────────────────────────────────────────────
    print("Processing traces with all 3 methods...\n")

    results_list = []
    sample_traces = {}  # Store a few preprocessed traces for visualization

    for i in range(len(traces)):
        results, dewowd = analyze_single_trace(traces[i], dt, i)
        results_list.append(results)

        # Store first 5 traces for visualization
        if i < 5:
            sample_traces[i] = {
                'raw': traces[i],
                'preprocessed': dewowd,
                'results': results,
            }

        if (i + 1) % 10 == 0:
            print(f"  {i+1:3d}/{len(traces)}")

    # Convert to DataFrame
    results_df = pd.DataFrame(results_list)
    print(f"\nProcessed {len(results_df)} traces")

    # ─────────────────────────────────────────────────────────────────────────
    # STATISTICS
    # ─────────────────────────────────────────────────────────────────────────
    print("\n" + "=" * 70)
    print("FIRST-BREAK PICK STATISTICS (Real EFE Field Data)")
    print("=" * 70)

    for method in ['sta_lta', 'coppens', 'threshold']:
        picks = results_df[method].values
        picks_ns = picks * dt * 1e9

        print(f"\n{method.upper()}:")
        print(f"  Mean:     {picks.mean():.1f} samples ({picks_ns.mean():.2f} ns)")
        print(f"  Median:   {np.median(picks):.1f} samples ({np.median(picks_ns):.2f} ns)")
        print(f"  Std:      {picks.std():.1f} samples ({picks_ns.std():.2f} ns)")
        print(f"  Range:    [{picks.min():.0f}, {picks.max():.0f}] samples")
        print(f"  % Non-zero: {(picks > 0).sum() / len(picks) * 100:.1f}%")

    # ─────────────────────────────────────────────────────────────────────────
    # VISUALIZATION: RAW TRACES + PICKS
    # ─────────────────────────────────────────────────────────────────────────
    time_ns = np.arange(traces.shape[1]) * dt * 1e9

    fig, axes = plt.subplots(5, 1, figsize=(14, 12))

    for row, (trace_idx, data) in enumerate(sample_traces.items()):
        ax = axes[row]
        raw = data['raw']
        results = data['results']

        # Plot raw trace
        ax.plot(time_ns, raw, 'k-', linewidth=0.8, alpha=0.7, label='Raw field trace')

        # Mark picks
        fb_sta = results['sta_lta']
        fb_cop = results['coppens']
        fb_thr = results['threshold']

        colors = ['blue', 'green', 'red']
        labels = ['STA/LTA', 'Coppens', 'Threshold']
        picks = [fb_sta, fb_cop, fb_thr]

        for color, label, pick in zip(colors, labels, picks):
            if pick > 0:
                ax.axvline(pick * dt * 1e9, color=color, linestyle='--', linewidth=1.5, alpha=0.8,
                          label=f'{label}: {pick}')

        ax.set_ylabel(f'Trace {trace_idx}', fontsize=10)
        ax.set_xlim(time_ns[0], min(30, time_ns[-1]))  # First 30 ns
        ax.grid(True, alpha=0.3, linestyle=':')
        ax.legend(loc='upper right', fontsize=8, ncol=3)

        if row == 0:
            ax.set_title('EFE Real Field Data: First-Break Picks (First 5 Traces)',
                        fontsize=12, fontweight='bold')
        if row == 4:
            ax.set_xlabel('Time (ns)', fontsize=10)

    plt.tight_layout()
    plt.savefig('efe_real_data_first_breaks.png', dpi=150, bbox_inches='tight')
    print("\n[OK] Saved visualization to: efe_real_data_first_breaks.png")

    # ─────────────────────────────────────────────────────────────────────────
    # VISUALIZATION: STATISTICS HISTOGRAMS
    # ─────────────────────────────────────────────────────────────────────────
    fig, axes = plt.subplots(1, 3, figsize=(14, 4))

    for col, method in enumerate(['sta_lta', 'coppens', 'threshold']):
        ax = axes[col]
        picks = results_df[method].values
        picks_ns = picks * dt * 1e9

        ax.hist(picks, bins=30, color=['blue', 'green', 'red'][col], alpha=0.7, edgecolor='black')
        ax.axvline(picks.mean(), color='red', linestyle='--', linewidth=2, label=f'Mean: {picks.mean():.1f}')
        ax.axvline(np.median(picks), color='orange', linestyle='--', linewidth=2, label=f'Median: {np.median(picks):.1f}')

        ax.set_xlabel(f'First-Break Sample Index', fontsize=10)
        ax.set_ylabel('Frequency', fontsize=10)
        ax.set_title(f'{method.upper()}\n({picks_ns.mean():.2f} ± {picks_ns.std():.2f} ns)', fontsize=11, fontweight='bold')
        ax.legend(fontsize=9)
        ax.grid(True, alpha=0.3, linestyle=':')

    plt.suptitle(f'Distribution of First-Break Picks ({len(traces)} traces)', fontsize=12, fontweight='bold')
    plt.tight_layout()
    plt.savefig('efe_first_breaks_distribution.png', dpi=150, bbox_inches='tight')
    print("[OK] Saved histogram to: efe_first_breaks_distribution.png")

    # ─────────────────────────────────────────────────────────────────────────
    # SAVE RESULTS
    # ─────────────────────────────────────────────────────────────────────────
    csv_path = 'efe_first_breaks_results.csv'
    results_df.to_csv(csv_path, index=False)
    print(f"[OK] Saved results to: {csv_path}")

    print("\n" + "=" * 70)
    print(f"Analysis complete: {len(traces)} traces processed")
    print("=" * 70)


if __name__ == '__main__':
    main()

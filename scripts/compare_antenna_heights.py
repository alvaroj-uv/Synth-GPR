#!/usr/bin/env python3
"""
Compare multiple antenna heights against real field data.
Loads .out files from antenna_heights directory and computes correlations.
"""

import sys
from pathlib import Path
import numpy as np
import h5py
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d


def read_real_dzt(dzt_path: Path, trace_idx: int = 1000) -> tuple:
    """Read real DZT trace."""
    HEADER_SIZE = 128 * 1024
    SAMPLES_PER_TRACE = 512
    BYTES_PER_SAMPLE = 4
    DT_NS = 50 / 511

    with open(dzt_path, 'rb') as f:
        f.seek(HEADER_SIZE + trace_idx * SAMPLES_PER_TRACE * BYTES_PER_SAMPLE)
        trace_bytes = f.read(SAMPLES_PER_TRACE * BYTES_PER_SAMPLE)
        signal = np.frombuffer(trace_bytes, dtype=np.int32, count=SAMPLES_PER_TRACE)
        signal = signal.astype(np.float64)

    signal = signal[2:]  # Drop indices 0-1
    t_ns = np.arange(len(signal)) * DT_NS
    return signal, t_ns, DT_NS


def read_synthetic_out(out_path: Path) -> tuple:
    """Read synthetic .out file."""
    with h5py.File(out_path, 'r') as f:
        signal = f['rxs/rx1/Ez'][()]
        dt = f.attrs.get('dt', 0.0)
    t_ns = np.arange(len(signal)) * dt * 1e9
    return signal, t_ns, dt * 1e9


def normalize_peak(signal):
    """Normalize by peak amplitude."""
    peak = np.max(np.abs(signal))
    if peak == 0:
        return signal
    return signal / peak


def compute_correlation(syn_sig: np.ndarray, syn_t: np.ndarray, dt_syn: float,
                       real_sig: np.ndarray, real_t: np.ndarray, dt_real: float) -> float:
    """Resample and compute correlation."""
    # Polarity flip
    syn_flipped = -syn_sig

    # Resample to real's dt
    t_min = 0
    t_max = min(syn_t[-1], real_t[-1])
    t_common = np.arange(int(t_max / dt_real) + 1) * dt_real

    f_syn = interp1d(syn_t, syn_flipped, kind='cubic', bounds_error=False, fill_value=0)
    f_real = interp1d(real_t, real_sig, kind='cubic', bounds_error=False, fill_value=0)

    syn_rs = f_syn(t_common)
    real_rs = f_real(t_common)

    # Normalize
    syn_norm = normalize_peak(syn_rs)
    real_norm = normalize_peak(real_rs)

    # Compute correlation
    try:
        corr = np.corrcoef(syn_norm, real_norm)[0, 1]
        return float(corr)
    except:
        return np.nan


def main():
    # Load real data
    dzt_path = Path("D:/Codigo/Data/PUERTO-LIMACHE_20230726_EFE_V1_PKC000_588_PKF011_020_CENTRO_BRUTO.DZT")
    print(f"[READ] Real DZT: {dzt_path.name}")
    real_sig, real_t, dt_real = read_real_dzt(dzt_path, trace_idx=15000)

    # Find all .out files
    out_dir = Path("output_test/antenna_heights")
    out_files = sorted(out_dir.glob("*.out"))

    if not out_files:
        print("[ERR] No .out files found in output_test/antenna_heights/")
        return 1

    print(f"[FOUND] {len(out_files)} synthetic outputs\n")

    results = []

    print(f"{'Height':<12} {'File':<30} {'Correlation':<15} {'Status'}")
    print("-" * 70)

    for out_file in out_files:
        # Extract height from filename
        height_str = out_file.stem.replace("height_", "").replace("cm", "")
        try:
            height_cm = float(height_str)
        except:
            height_cm = 0

        try:
            syn_sig, syn_t, dt_syn = read_synthetic_out(out_file)
            corr = compute_correlation(syn_sig, syn_t, dt_syn, real_sig, real_t, dt_real)

            if np.isnan(corr):
                status = "[ERR corr]"
            else:
                status = "[OK]"
                results.append({'height': height_cm, 'file': out_file, 'corr': corr})

            print(f"{height_cm:>6.1f} cm    {out_file.name:<30} {corr:>+10.6f}    {status}")

        except Exception as e:
            print(f"{height_cm:>6.1f} cm    {out_file.name:<30} {'ERR':<15} [FAIL] {str(e)[:30]}")

    if not results:
        print("\n[ERR] No valid correlations computed")
        return 1

    # Sort and display
    results_sorted = sorted(results, key=lambda x: x['corr'], reverse=True)

    print(f"\n{'='*70}")
    print("RESULTS (sorted by correlation)")
    print(f"{'='*70}\n")

    print(f"{'Height':<12} {'Correlation':<15} {'Status'}")
    print("-" * 70)

    best_height = results_sorted[0]['height']
    best_corr = results_sorted[0]['corr']

    for r in results_sorted:
        marker = "*** BEST ***" if abs(r['height'] - best_height) < 0.1 else ""
        print(f"{r['height']:>6.1f} cm    {r['corr']:>+10.6f}          {marker}")

    print(f"\n{'='*70}")
    print(f"OPTIMAL HEIGHT: {best_height:.1f} cm")
    print(f"CORRELATION: {best_corr:.6f}")
    print(f"{'='*70}\n")

    # Plot
    fig, ax = plt.subplots(figsize=(12, 6))
    fig.patch.set_facecolor("#0f1117")
    ax.set_facecolor("#1a1e2b")

    heights = [r['height'] for r in results_sorted]
    corrs = [r['corr'] for r in results_sorted]

    # Plot scatter with color gradient
    scatter = ax.scatter(heights, corrs, s=150, c=corrs, cmap='RdYlGn',
                        edgecolors='#c8d0e0', linewidth=2, alpha=0.8, vmin=-0.1, vmax=0.1)

    # Mark best
    ax.scatter([best_height], [best_corr], s=400, marker='*', color='gold',
              edgecolors='white', linewidth=2, label=f'Best: {best_height:.1f}cm', zorder=5)

    # Connect with line
    ax.plot(heights, corrs, 'c--', alpha=0.3, linewidth=1.5)

    # Reference lines
    ax.axhline(0, color='#2a2f42', linestyle='-', linewidth=1, alpha=0.5)
    ax.axvline(5, color='#666', linestyle=':', linewidth=1, alpha=0.5, label='Current: 5cm')

    ax.set_xlabel("Antenna Height (cm)", fontsize=12, color="#c8d0e0", fontweight='bold')
    ax.set_ylabel("Correlation with Real Field GPR", fontsize=12, color="#c8d0e0", fontweight='bold')
    ax.set_title("Antenna Height Optimization (420 MHz Gaussian Bistatic 30mm)",
                fontsize=13, color="#c8d0e0", fontweight='bold')

    ax.grid(True, color="#2a2f42", alpha=0.3)
    ax.legend(fontsize=11, facecolor='#1a1e2b', labelcolor='#c8d0e0', edgecolor='#2a2f42', loc='best')
    ax.tick_params(colors="#c8d0e0", labelsize=10)

    for spine in ax.spines.values():
        spine.set_color("#2a2f42")
        spine.set_linewidth(1.5)

    cbar = plt.colorbar(scatter, ax=ax, label='Correlation')
    cbar.set_label("Correlation", color="#c8d0e0", fontsize=10)
    cbar.ax.tick_params(colors="#c8d0e0")

    png_path = Path("output_test") / "17_antenna_height_sweep.png"
    fig.savefig(png_path, dpi=150, bbox_inches='tight', facecolor="#0f1117")
    print(f"[SAVE] Plot: {png_path}\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())

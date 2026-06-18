#!/usr/bin/env python3
"""
Analyze fouled ballast epsilon sweep: compare each with real data.
Calculate correlation for each epsilon value.
"""

import sys
from pathlib import Path
import numpy as np
import h5py
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d

sys.path.insert(0, str(Path(__file__).parent))


def read_synthetic_out(out_path: Path):
    """Read gprMax .out file."""
    if not out_path.exists():
        return None, None
    try:
        with h5py.File(out_path, 'r') as f:
            signal = f['rxs/rx1/Ez'][()]
            dt = f.attrs.get('dt', 0.0)
        return signal, dt * 1e9
    except:
        return None, None


def read_real_dzt(dzt_path: Path, trace_idx: int = 15000):
    """Read GSSI DZT file."""
    HEADER_SIZE = 128 * 1024
    SAMPLES_PER_TRACE = 512
    BYTES_PER_SAMPLE = 4
    DT_NS = 50 / 511

    try:
        with open(dzt_path, 'rb') as f:
            f.seek(HEADER_SIZE + trace_idx * SAMPLES_PER_TRACE * BYTES_PER_SAMPLE)
            trace_bytes = f.read(SAMPLES_PER_TRACE * BYTES_PER_SAMPLE)
            signal = np.frombuffer(trace_bytes, dtype=np.int32, count=SAMPLES_PER_TRACE)
            signal = signal[2:].astype(np.float64)
        return signal, DT_NS
    except:
        return None, None


def find_dw_peak(signal: np.ndarray, dt_ns: float, search_ns: float = 20):
    """Find direct wave peak."""
    search_idx = int(search_ns / dt_ns)
    search_idx = min(search_idx, len(signal))
    peak_idx = np.argmax(np.abs(signal[:search_idx]))
    peak_time = peak_idx * dt_ns
    return peak_idx, peak_time


def apply_cutoff(signal: np.ndarray, peak_idx: int, cutoff_ns: float, dt_ns: float):
    """Apply cutoff at peak + cutoff_ns."""
    cutoff_samples = int(round(cutoff_ns / dt_ns))
    cutoff_idx = peak_idx + cutoff_samples
    if cutoff_idx >= len(signal):
        return signal, 0
    return signal[cutoff_idx:], cutoff_idx


def normalize_peak(signal: np.ndarray):
    """Normalize by peak amplitude."""
    peak = np.max(np.abs(signal))
    if peak == 0:
        return signal
    return signal / peak


def compute_correlation(syn_path: Path, real_sig: np.ndarray, real_dt: float):
    """Compute correlation between synthetic and real."""
    syn_sig, syn_dt = read_synthetic_out(syn_path)
    if syn_sig is None:
        return None

    # Flip polarity
    syn_sig = -syn_sig

    # Find peaks
    syn_peak_idx, _ = find_dw_peak(syn_sig, syn_dt)
    real_peak_idx, _ = find_dw_peak(real_sig, real_dt)

    # Apply cutoff
    cutoff_ns = 4.0
    syn_cut, _ = apply_cutoff(syn_sig, syn_peak_idx, cutoff_ns, syn_dt)
    real_cut, _ = apply_cutoff(real_sig, real_peak_idx, cutoff_ns, real_dt)

    if len(syn_cut) == 0 or len(real_cut) == 0:
        return None

    # Interpolate
    syn_t_cut = np.arange(len(syn_cut)) * syn_dt
    real_t_cut = np.arange(len(real_cut)) * real_dt

    common_dt = real_dt
    t_max = min(syn_t_cut[-1], real_t_cut[-1])
    t_common = np.arange(0, t_max + common_dt, common_dt)

    f_syn = interp1d(syn_t_cut, syn_cut, kind='cubic', bounds_error=False, fill_value=0)
    f_real = interp1d(real_t_cut, real_cut, kind='cubic', bounds_error=False, fill_value=0)

    syn_interp = f_syn(t_common)
    real_interp = f_real(t_common)

    # Normalize and compute correlation
    syn_norm = normalize_peak(syn_interp)
    real_norm = normalize_peak(real_interp)

    corr = np.corrcoef(syn_norm, real_norm)[0, 1]
    return corr


def main():
    print("\n" + "="*80)
    print("FOULED BALLAST EPSILON SWEEP ANALYSIS")
    print("="*80 + "\n")

    # Load real data
    real_path = Path("D:/Codigo/Data/PUERTO-LIMACHE_20230726_EFE_V1_PKC000_588_PKF011_020_CENTRO_BRUTO.DZT")
    real_sig, real_dt = read_real_dzt(real_path, trace_idx=15000)

    if real_sig is None:
        print("ERROR: Could not load real data")
        return 1

    # Scan epsilon sweep directory
    sweep_dir = Path("epsilon_sweep_fouled")
    out_files = sorted(sweep_dir.glob("*.out"))

    print(f"Found {len(out_files)} simulation outputs\n")
    print(f"{'Epsilon':<10} {'File':<40} {'Correlation':<15}")
    print("-" * 65)

    results = []

    for out_file in out_files:
        # Extract epsilon from filename
        name = out_file.stem
        try:
            eps_str = name.split("_")[-1]
            eps = float(eps_str)
        except:
            eps = None

        # Compute correlation
        corr = compute_correlation(out_file, real_sig, real_dt)

        if corr is not None:
            results.append((eps, corr, out_file.name))
            print(f"{eps:<10.1f} {out_file.name:<40} {corr:+.6f}")
        else:
            print(f"{'?':<10} {out_file.name:<40} [FAILED]")

    if not results:
        print("\nNo valid results to analyze")
        return 1

    # Find best
    best_eps, best_corr, best_file = max(results, key=lambda x: x[1])

    print(f"\n{'='*80}")
    print("RESULTS")
    print(f"{'='*80}\n")

    print(f"Optimal epsilon: {best_eps:.1f}")
    print(f"Best correlation: {best_corr:+.6f}")
    print(f"File: {best_file}\n")

    if best_corr > 0.237:
        improvement = ((best_corr - 0.237) / 0.237) * 100
        print(f"Improvement over eps=5.1: +{improvement:.1f}%")
    else:
        improvement = ((0.237 - best_corr) / 0.237) * 100
        print(f"Degradation from eps=5.1: {improvement:.1f}%")

    # Create visualization
    fig, ax = plt.subplots(figsize=(12, 6))
    fig.patch.set_facecolor("#0f1117")
    ax.set_facecolor("#1a1e2b")

    eps_vals = [r[0] for r in results]
    corr_vals = [r[1] for r in results]

    ax.plot(eps_vals, corr_vals, color="#00d9ff", lw=2.5, marker='o', markersize=10, alpha=0.8)
    ax.scatter([best_eps], [best_corr], s=400, color='#00ff00', marker='*',
              edgecolor='white', linewidth=2, zorder=5, label=f'Best: eps={best_eps:.1f}')

    # Mark reference point
    ax.axhline(0.237, color='#ff6b35', linestyle='--', linewidth=2, alpha=0.7,
              label='Reference: eps=5.1 (r=0.237)')

    ax.set_xlabel("Epsilon", fontsize=12, color="#c8d0e0", fontweight='bold')
    ax.set_ylabel("Pearson Correlation", fontsize=12, color="#c8d0e0", fontweight='bold')
    ax.set_title("Fouled Ballast Epsilon Sweep: Correlation with Real Data",
                fontsize=13, color="#00d9ff", fontweight='bold', pad=15)

    ax.grid(True, color="#2a2f42", alpha=0.3, linestyle='--')
    ax.tick_params(colors="#c8d0e0", labelsize=10)
    for spine in ax.spines.values():
        spine.set_color("#2a2f42")

    ax.legend(fontsize=11, facecolor='#1a1e2b', labelcolor='#c8d0e0',
             edgecolor='#2a2f42', loc='best')

    png_path = Path("output_test") / "fouled_epsilon_sweep_results.png"
    fig.savefig(png_path, dpi=150, bbox_inches='tight', facecolor="#0f1117")
    print(f"[SAVE] {png_path}\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""
Compare three configurations:
1. Freespace (no material)
2. Ballast layer (homogeneous)
3. Rocks layer (heterogeneous packing)
All at 420 MHz Gaussian bistatic 30mm.
"""

import sys
from pathlib import Path
import numpy as np
import h5py
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from scipy.interpolate import interp1d


def read_synthetic_out(out_path: Path) -> tuple:
    """Read synthetic .out file."""
    with h5py.File(out_path, 'r') as f:
        signal = f['rxs/rx1/Ez'][()]
        dt = f.attrs.get('dt', 0.0)
    t_ns = np.arange(len(signal)) * dt * 1e9
    return signal, t_ns, dt * 1e9


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


def normalize_peak(signal):
    """Normalize by peak amplitude."""
    peak = np.max(np.abs(signal))
    if peak == 0:
        return signal
    return signal / peak


def compute_correlation(syn_sig: np.ndarray, syn_t: np.ndarray, dt_syn: float,
                       real_sig: np.ndarray, real_t: np.ndarray, dt_real: float) -> float:
    """Resample and compute correlation."""
    syn_flipped = -syn_sig

    t_min = 0
    t_max = min(syn_t[-1], real_t[-1])
    t_common = np.arange(int(t_max / dt_real) + 1) * dt_real

    f_syn = interp1d(syn_t, syn_flipped, kind='cubic', bounds_error=False, fill_value=0)
    f_real = interp1d(real_t, real_sig, kind='cubic', bounds_error=False, fill_value=0)

    syn_rs = f_syn(t_common)
    real_rs = f_real(t_common)

    syn_norm = normalize_peak(syn_rs)
    real_norm = normalize_peak(real_rs)

    try:
        corr = np.corrcoef(syn_norm, real_norm)[0, 1]
        return float(corr), t_common, syn_norm, real_norm
    except:
        return np.nan, None, None, None


def main():
    # Load real data
    dzt_path = Path("D:/Codigo/Data/PUERTO-LIMACHE_20230726_EFE_V1_PKC000_588_PKF011_020_CENTRO_BRUTO.DZT")
    print(f"[READ] Real DZT: {dzt_path.name} (trace #15000)")
    real_sig, real_t, dt_real = read_real_dzt(dzt_path, trace_idx=15000)
    real_norm = normalize_peak(real_sig)

    # Load three configurations
    configs = [
        ("Freespace (No material)", "output_test/freespace_420mhz_optimized.out", "#00d9ff"),
        ("Ballast layer (eps=3.45)", "output_test/ballast_layer.out", "#00ff88"),
        ("Rocks layer (mbubia)", "output_test/rocks_420mhz_50cm.out", "#ff9500"),
    ]

    results = []

    print(f"\n{'='*70}")
    print("MATERIAL COMPARISON: Freespace vs Ballast vs Rocks")
    print(f"{'='*70}\n")

    print(f"{'Configuration':<30} {'Correlation':<15} {'Status'}")
    print("-" * 70)

    for name, out_path, color in configs:
        try:
            out_p = Path(out_path)
            if not out_p.exists():
                print(f"{name:<30} {'N/A':<15} [FILE NOT FOUND]")
                continue

            syn_sig, syn_t, dt_syn = read_synthetic_out(out_p)
            corr, t_common, syn_norm, real_norm_rs = compute_correlation(
                syn_sig, syn_t, dt_syn, real_sig, real_t, dt_real
            )

            if np.isnan(corr):
                status = "[ERR]"
            else:
                status = "[OK]"
                results.append({
                    'name': name,
                    'path': out_path,
                    'color': color,
                    'corr': corr,
                    't_common': t_common,
                    'syn_norm': syn_norm,
                    'real_norm': real_norm_rs
                })

            print(f"{name:<30} {corr:>+10.6f}      {status}")

        except Exception as e:
            print(f"{name:<30} {'ERR':<15} {str(e)[:40]}")

    if not results:
        print("[ERR] No valid results")
        return 1

    # Sort by correlation
    results_sorted = sorted(results, key=lambda x: x['corr'], reverse=True)

    print(f"\n{'='*70}")
    print("RANKED BY CORRELATION")
    print(f"{'='*70}\n")

    for i, r in enumerate(results_sorted, 1):
        marker = "[BEST]" if i == 1 else ""
        print(f"{i}. {r['name']:<28} {r['corr']:>+10.6f}  {marker}")

    # Plot
    fig = plt.figure(figsize=(16, 10))
    fig.patch.set_facecolor("#0f1117")
    gs = gridspec.GridSpec(len(results) + 1, 1, figure=fig, hspace=0.35,
                          left=0.1, right=0.95, top=0.96, bottom=0.06)

    display_max = min(50, results[0]['t_common'][-1])

    # Plot each synthetic vs real
    for i, r in enumerate(results_sorted):
        ax = fig.add_subplot(gs[i])
        ax.set_facecolor("#1a1e2b")

        t = r['t_common']
        mask = t <= display_max

        ax.plot(t[mask], r['syn_norm'][mask], color=r['color'], lw=1.5, alpha=0.85,
               label=r['name'])
        ax.plot(t[mask], r['real_norm'][mask], color='#ff6b35', lw=1.5, alpha=0.7,
               label='Real field GPR')

        ax.axhline(0, color='#2a2f42', lw=0.8, linestyle='-', alpha=0.5)
        ax.set_ylabel("Amplitude (norm)", fontsize=10, color="#c8d0e0", fontweight='bold')
        ax.set_title(f"Row {i+1}: {r['name']} (corr: {r['corr']:+.6f})",
                    fontsize=11, color="#c8d0e0", fontweight='bold', pad=8)
        ax.grid(True, color="#2a2f42", lw=0.5, alpha=0.4)
        ax.legend(loc='upper right', fontsize=9, facecolor='#1a1e2b', labelcolor='#c8d0e0',
                 edgecolor='#2a2f42')
        ax.tick_params(colors="#c8d0e0", labelsize=9)
        for spine in ax.spines.values():
            spine.set_color("#2a2f42")

    # Final comparison row
    ax_final = fig.add_subplot(gs[-1])
    ax_final.set_facecolor("#1a1e2b")

    for r in results_sorted:
        t = r['t_common']
        mask = t <= display_max
        ax_final.plot(t[mask], r['syn_norm'][mask], color=r['color'], lw=2, alpha=0.85,
                     label=f"{r['name']} ({r['corr']:+.4f})")

    # Real data on its own time grid
    real_t_display = real_t[real_t <= display_max]
    real_norm_display = real_norm[:len(real_t_display)]
    ax_final.plot(real_t_display, real_norm_display, color='#ff6b35', lw=2, alpha=0.85,
                 label='Real (reference)', linestyle='--')
    ax_final.axhline(0, color='#2a2f42', lw=0.8, linestyle='-', alpha=0.5)
    ax_final.set_xlabel("Time (ns)", fontsize=10, color="#c8d0e0", fontweight='bold')
    ax_final.set_ylabel("Amplitude (norm)", fontsize=10, color="#c8d0e0", fontweight='bold')
    ax_final.set_title("All Configurations Overlaid",
                      fontsize=11, color="#c8d0e0", fontweight='bold', pad=8)
    ax_final.grid(True, color="#2a2f42", lw=0.5, alpha=0.4)
    ax_final.legend(loc='upper right', fontsize=10, facecolor='#1a1e2b', labelcolor='#c8d0e0',
                   edgecolor='#2a2f42')
    ax_final.tick_params(colors="#c8d0e0", labelsize=9)
    for spine in ax_final.spines.values():
        spine.set_color("#2a2f42")

    fig.suptitle(
        "Material Comparison: Freespace vs Ballast vs Rocks\n"
        "420 MHz Gaussian Bistatic 30mm",
        color="#c8d0e0", fontsize=13, fontweight='bold', y=0.995
    )

    png_path = Path("output_test") / "18_material_comparison.png"
    fig.savefig(png_path, dpi=150, bbox_inches='tight', facecolor="#0f1117")
    print(f"\n[SAVE] {png_path}\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""
Compare resampled 10layer_eps_sweep_50ns.out with real DZT sample.
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


def read_synthetic_out(out_path: Path):
    """Read gprMax .out file."""
    with h5py.File(out_path, 'r') as f:
        signal = f['rxs/rx1/Ez'][()]
        dt = f.attrs.get('dt', 0.0)
    return signal, dt * 1e9


def read_dzt_sample(dzt_path: Path, trace_idx: int = 15000):
    """Extract DZT sample."""
    HEADER_SIZE = 128 * 1024
    SAMPLES_PER_TRACE = 512
    BYTES_PER_SAMPLE = 4
    DT_NS = 50 / 511

    with open(dzt_path, 'rb') as f:
        f.seek(HEADER_SIZE + trace_idx * SAMPLES_PER_TRACE * BYTES_PER_SAMPLE)
        trace_bytes = f.read(SAMPLES_PER_TRACE * BYTES_PER_SAMPLE)
        signal = np.frombuffer(trace_bytes, dtype=np.int32, count=SAMPLES_PER_TRACE)
        signal = signal[2:].astype(np.float64)

    return signal, DT_NS


def find_dw_peak(signal: np.ndarray, dt_ns: float, search_ns: float = 20):
    """Find direct wave peak."""
    search_idx = int(search_ns / dt_ns)
    search_idx = min(search_idx, len(signal))
    peak_idx = np.argmax(np.abs(signal[:search_idx]))
    return peak_idx, peak_idx * dt_ns


def normalize_peak(signal: np.ndarray):
    """Normalize by peak amplitude."""
    peak = np.max(np.abs(signal))
    if peak == 0:
        return signal
    return signal / peak


def main():
    print("\n" + "="*90)
    print("RESAMPLED 10LAYER vs DZT SAMPLE COMPARISON")
    print("="*90 + "\n")

    # Load synthetic (resampled)
    out_path = Path("10layer_eps_sweep_50ns.out")
    syn_sig, syn_dt = read_synthetic_out(out_path)
    syn_t = np.arange(len(syn_sig)) * syn_dt

    print(f"[SYNTHETIC - RESAMPLED 10LAYER]")
    print(f"  File: {out_path.name}")
    print(f"  Samples: {len(syn_sig)}")
    print(f"  dt: {syn_dt:.6f} ns")
    print(f"  Duration: {(len(syn_sig)-1)*syn_dt:.2f} ns\n")

    # Load DZT
    dzt_path = Path("D:/Codigo/Data/PUERTO-LIMACHE_20230726_EFE_V1_PKC000_588_PKF011_020_CENTRO_BRUTO.DZT")
    real_sig, real_dt = read_dzt_sample(dzt_path, trace_idx=15000)
    real_t = np.arange(len(real_sig)) * real_dt

    print(f"[REAL - DZT SAMPLE]")
    print(f"  Trace index: 15000")
    print(f"  Samples: {len(real_sig)}")
    print(f"  dt: {real_dt:.6f} ns")
    print(f"  Duration: {(len(real_sig)-1)*real_dt:.2f} ns\n")

    # Apply polarity flip
    syn_sig_flip = -syn_sig

    # Find peaks
    syn_peak_idx, syn_peak_t = find_dw_peak(syn_sig_flip, syn_dt)
    real_peak_idx, real_peak_t = find_dw_peak(real_sig, real_dt)

    print(f"DW Peak (synthetic): {syn_peak_t:.4f} ns")
    print(f"DW Peak (real): {real_peak_t:.4f} ns\n")

    # Interpolate to common grid
    common_dt = real_dt
    t_max = min(syn_t[-1], real_t[-1])
    t_common = np.arange(0, t_max + common_dt, common_dt)

    f_syn = interp1d(syn_t, syn_sig_flip, kind='cubic', bounds_error=False, fill_value=0)
    f_real = interp1d(real_t, real_sig, kind='cubic', bounds_error=False, fill_value=0)

    syn_interp = f_syn(t_common)
    real_interp = f_real(t_common)

    # Normalize
    syn_norm = normalize_peak(syn_interp)
    real_norm = normalize_peak(real_interp)

    # Correlation
    corr = np.corrcoef(syn_norm, real_norm)[0, 1]

    print(f"Pearson Correlation: {corr:+.6f}\n")

    # Visualization
    fig = plt.figure(figsize=(16, 10))
    fig.patch.set_facecolor("#0f1117")
    gs = gridspec.GridSpec(3, 2, figure=fig, hspace=0.35, wspace=0.3,
                          left=0.08, right=0.95, top=0.96, bottom=0.08)

    # Row 1: Full traces
    ax1 = fig.add_subplot(gs[0, 0])
    ax1.set_facecolor("#1a1e2b")
    ax1.plot(syn_t, syn_sig_flip, color="#00d9ff", lw=1, alpha=0.8, label="Synthetic (resampled)")
    ax1.scatter([syn_peak_t], [syn_sig_flip[syn_peak_idx]], color='#ffff00', s=150,
               marker='*', edgecolor='white', linewidth=2, zorder=5)
    ax1.axhline(0, color='#2a2f42', lw=0.8, alpha=0.5)
    ax1.set_ylabel("Amplitude (V/m)", fontsize=10, color="#c8d0e0", fontweight='bold')
    ax1.set_title("Synthetic 10-Layer Resampled to 50ns", fontsize=11, color="#00d9ff", fontweight='bold')
    ax1.grid(True, color="#2a2f42", alpha=0.3)
    ax1.legend(fontsize=9, facecolor='#1a1e2b', labelcolor='#c8d0e0', edgecolor='#2a2f42')
    ax1.tick_params(colors="#c8d0e0", labelsize=9)
    for spine in ax1.spines.values():
        spine.set_color("#2a2f42")

    ax2 = fig.add_subplot(gs[0, 1])
    ax2.set_facecolor("#1a1e2b")
    ax2.plot(real_t, real_sig, color="#ff6b35", lw=1, alpha=0.8, label="Real DZT Trace #15000")
    ax2.scatter([real_peak_t], [real_sig[real_peak_idx]], color='#ffff00', s=150,
               marker='*', edgecolor='white', linewidth=2, zorder=5)
    ax2.axhline(0, color='#2a2f42', lw=0.8, alpha=0.5)
    ax2.set_ylabel("Amplitude (A/D counts)", fontsize=10, color="#c8d0e0", fontweight='bold')
    ax2.set_title("Real DZT Sample (Full 50ns)", fontsize=11, color="#ff6b35", fontweight='bold')
    ax2.grid(True, color="#2a2f42", alpha=0.3)
    ax2.legend(fontsize=9, facecolor='#1a1e2b', labelcolor='#c8d0e0', edgecolor='#2a2f42')
    ax2.tick_params(colors="#c8d0e0", labelsize=9)
    for spine in ax2.spines.values():
        spine.set_color("#2a2f42")

    # Row 2: Zoomed to 40ns
    ax3 = fig.add_subplot(gs[1, 0])
    ax3.set_facecolor("#1a1e2b")
    mask_syn = syn_t <= 40
    ax3.plot(syn_t[mask_syn], syn_sig_flip[mask_syn], color="#00d9ff", lw=1.5, alpha=0.8)
    ax3.axhline(0, color='#2a2f42', lw=0.8, alpha=0.5)
    ax3.set_ylabel("Amplitude (V/m)", fontsize=10, color="#c8d0e0", fontweight='bold')
    ax3.set_title("Synthetic (0-40ns)", fontsize=11, color="#00d9ff", fontweight='bold')
    ax3.grid(True, color="#2a2f42", alpha=0.3)
    ax3.tick_params(colors="#c8d0e0", labelsize=9)
    for spine in ax3.spines.values():
        spine.set_color("#2a2f42")

    ax4 = fig.add_subplot(gs[1, 1])
    ax4.set_facecolor("#1a1e2b")
    mask_real = real_t <= 40
    ax4.plot(real_t[mask_real], real_sig[mask_real], color="#ff6b35", lw=1.5, alpha=0.8)
    ax4.axhline(0, color='#2a2f42', lw=0.8, alpha=0.5)
    ax4.set_ylabel("Amplitude (A/D counts)", fontsize=10, color="#c8d0e0", fontweight='bold')
    ax4.set_title("Real (0-40ns)", fontsize=11, color="#ff6b35", fontweight='bold')
    ax4.grid(True, color="#2a2f42", alpha=0.3)
    ax4.tick_params(colors="#c8d0e0", labelsize=9)
    for spine in ax4.spines.values():
        spine.set_color("#2a2f42")

    # Row 3: Normalized comparison
    ax5 = fig.add_subplot(gs[2, :])
    ax5.set_facecolor("#1a1e2b")

    mask = t_common <= 40
    ax5.plot(t_common[mask], syn_norm[mask], color="#00d9ff", lw=2.5, alpha=0.85,
            label="Synthetic (normalized)")
    ax5.plot(t_common[mask], real_norm[mask], color="#ff6b35", lw=2.5, alpha=0.85,
            label="Real (normalized)")
    ax5.fill_between(t_common[mask], syn_norm[mask], real_norm[mask], alpha=0.15, color='yellow',
                    label="Difference")
    ax5.axhline(0, color='#2a2f42', lw=0.8, alpha=0.5)

    ax5.set_xlabel("Time (ns)", fontsize=11, color="#c8d0e0", fontweight='bold')
    ax5.set_ylabel("Normalized Amplitude", fontsize=11, color="#c8d0e0", fontweight='bold')
    ax5.set_title(f"Aligned Comparison (Pearson r = {corr:+.4f})", fontsize=12,
                 color="#c8d0e0", fontweight='bold', pad=12)
    ax5.grid(True, color="#2a2f42", alpha=0.3)
    ax5.legend(fontsize=11, facecolor='#1a1e2b', labelcolor='#c8d0e0', edgecolor='#2a2f42',
              loc='upper right')
    ax5.tick_params(colors="#c8d0e0", labelsize=10)
    for spine in ax5.spines.values():
        spine.set_color("#2a2f42")

    fig.suptitle(
        "10-Layer Resampled to 50ns vs Real DZT\n" +
        "Polarity Corrected, Common Time Grid",
        color="#c8d0e0", fontsize=13, fontweight='bold', y=0.995
    )

    png_path = Path("output_test") / "compare_resampled_10layer_dzt.png"
    fig.savefig(png_path, dpi=150, bbox_inches='tight', facecolor="#0f1117")
    print(f"[SAVE] {png_path}\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())

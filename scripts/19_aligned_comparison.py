#!/usr/bin/env python3
"""
Improved material comparison with direct wave alignment.
Steps:
1. Detect direct wave peak in both synthetic and real
2. Align peaks (time-shift one to match the other)
3. Resample to common dt
4. Normalize and compare
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


def find_direct_wave_peak(signal: np.ndarray, search_start_idx: int = 0,
                         search_end_idx: int = None) -> int:
    """Find the peak index of the direct wave (first major peak)."""
    if search_end_idx is None:
        search_end_idx = len(signal)

    search_region = signal[search_start_idx:search_end_idx]
    peak_idx_local = np.argmax(np.abs(search_region))
    return search_start_idx + peak_idx_local


def align_and_correlate(syn_sig: np.ndarray, syn_t: np.ndarray, dt_syn: float,
                       real_sig: np.ndarray, real_t: np.ndarray, dt_real: float,
                       label: str = "") -> dict:
    """
    Align direct waves and compute correlation.

    Steps:
    1. Polarity flip synthetic
    2. Find direct wave peaks
    3. Align peaks
    4. Resample to common dt
    5. Compute correlation
    """

    # Step 1: Polarity flip
    syn_flipped = -syn_sig

    # Step 2: Find direct wave peaks (search first 20ns)
    search_ns = 20
    search_idx_syn = int(search_ns / dt_syn)
    search_idx_real = int(search_ns / dt_real)

    peak_idx_syn = find_direct_wave_peak(syn_flipped, 0, min(search_idx_syn, len(syn_flipped)))
    peak_idx_real = find_direct_wave_peak(real_sig, 0, min(search_idx_real, len(real_sig)))

    peak_time_syn = syn_t[peak_idx_syn]
    peak_time_real = real_t[peak_idx_real]

    # Step 3: Calculate time shift to align peaks
    time_shift_ns = peak_time_real - peak_time_syn
    shift_samples_syn = int(round(time_shift_ns / dt_syn))

    # Apply shift to synthetic time axis (don't modify signal, just shift time reference)
    syn_t_shifted = syn_t + time_shift_ns

    # Step 4: Resample to common dt (use real's dt)
    t_min = max(syn_t_shifted[0], real_t[0])
    t_max = min(syn_t_shifted[-1], real_t[-1])
    t_common = np.arange(int((t_max - t_min) / dt_real) + 1) * dt_real + t_min

    # Interpolate both to common time grid
    f_syn = interp1d(syn_t_shifted, syn_flipped, kind='cubic', bounds_error=False, fill_value=0)
    f_real = interp1d(real_t, real_sig, kind='cubic', bounds_error=False, fill_value=0)

    syn_common = f_syn(t_common)
    real_common = f_real(t_common)

    # Step 5: Normalize and correlate
    syn_norm = normalize_peak(syn_common)
    real_norm = normalize_peak(real_common)

    try:
        corr = np.corrcoef(syn_norm, real_norm)[0, 1]
    except:
        corr = np.nan

    return {
        'label': label,
        'peak_time_syn': peak_time_syn,
        'peak_time_real': peak_time_real,
        'time_shift_ns': time_shift_ns,
        'correlation': corr,
        't_common': t_common,
        'syn_norm': syn_norm,
        'real_norm': real_norm,
    }


def main():
    # Load real data
    dzt_path = Path("D:/Codigo/Data/PUERTO-LIMACHE_20230726_EFE_V1_PKC000_588_PKF011_020_CENTRO_BRUTO.DZT")
    print(f"[READ] Real DZT: {dzt_path.name} (trace #15000)")
    real_sig, real_t, dt_real = read_real_dzt(dzt_path, trace_idx=15000)

    # Three configurations
    configs = [
        ("Freespace", "output_test/freespace_420mhz_optimized.out", "#00d9ff"),
        ("Ballast (eps=3.45)", "output_test/ballast_layer.out", "#00ff88"),
        ("Rocks (mbubia)", "output_test/rocks_420mhz_50cm.out", "#ff9500"),
    ]

    results = []

    print(f"\n{'='*80}")
    print("ALIGNED DIRECT WAVE COMPARISON")
    print(f"{'='*80}\n")

    print(f"{'Configuration':<25} {'Peak Syn':<12} {'Peak Real':<12} {'Shift (ns)':<12} {'Corr':<12}")
    print("-" * 80)

    for name, out_path, color in configs:
        try:
            out_p = Path(out_path)
            if not out_p.exists():
                print(f"{name:<25} {'FILE NOT FOUND':<50}")
                continue

            syn_sig, syn_t, dt_syn = read_synthetic_out(out_p)

            result = align_and_correlate(syn_sig, syn_t, dt_syn, real_sig, real_t, dt_real, name)
            result['color'] = color
            result['path'] = out_path
            results.append(result)

            print(f"{name:<25} {result['peak_time_syn']:>7.2f} ns  {result['peak_time_real']:>7.2f} ns  "
                  f"{result['time_shift_ns']:>7.2f} ns  {result['correlation']:>+8.6f}")

        except Exception as e:
            print(f"{name:<25} ERROR: {str(e)[:50]}")

    if not results:
        print("[ERR] No valid results")
        return 1

    # Sort by correlation
    results_sorted = sorted(results, key=lambda x: x['correlation'], reverse=True)

    print(f"\n{'='*80}")
    print("RANKED BY CORRELATION (Direct Wave Aligned)")
    print(f"{'='*80}\n")

    for i, r in enumerate(results_sorted, 1):
        marker = "[BEST]" if i == 1 else ""
        print(f"{i}. {r['label']:<28} {r['correlation']:>+10.6f}  {marker}")

    # Plot
    fig = plt.figure(figsize=(16, 12))
    fig.patch.set_facecolor("#0f1117")
    gs = gridspec.GridSpec(len(results) + 1, 1, figure=fig, hspace=0.4,
                          left=0.1, right=0.95, top=0.96, bottom=0.06)

    display_max = 50  # First 50 ns

    # Plot each configuration
    for i, r in enumerate(results_sorted):
        ax = fig.add_subplot(gs[i])
        ax.set_facecolor("#1a1e2b")

        t = r['t_common']
        mask = t <= display_max

        ax.plot(t[mask], r['syn_norm'][mask], color=r['color'], lw=2, alpha=0.85,
               label=f"{r['label']} (syn, shift={r['time_shift_ns']:+.2f}ns)")
        ax.plot(t[mask], r['real_norm'][mask], color='#ff6b35', lw=2, alpha=0.7,
               label='Real field GPR')

        # Mark aligned direct wave peaks
        ax.axvline(r['peak_time_syn'], color=r['color'], linestyle='--', alpha=0.5, linewidth=1)
        ax.axvline(r['peak_time_real'], color='#ff6b35', linestyle='--', alpha=0.5, linewidth=1)

        ax.axhline(0, color='#2a2f42', lw=0.8, linestyle='-', alpha=0.5)
        ax.set_ylabel("Amplitude (norm)", fontsize=10, color="#c8d0e0", fontweight='bold')
        ax.set_title(f"Row {i+1}: {r['label']} (corr: {r['correlation']:+.6f}, "
                    f"syn_peak:{r['peak_time_syn']:.2f}ns, real_peak:{r['peak_time_real']:.2f}ns)",
                    fontsize=11, color="#c8d0e0", fontweight='bold', pad=8)
        ax.grid(True, color="#2a2f42", lw=0.5, alpha=0.4)
        ax.legend(loc='upper right', fontsize=9, facecolor='#1a1e2b', labelcolor='#c8d0e0',
                 edgecolor='#2a2f42')
        ax.tick_params(colors="#c8d0e0", labelsize=9)
        for spine in ax.spines.values():
            spine.set_color("#2a2f42")

    # Overlay plot
    ax_overlay = fig.add_subplot(gs[-1])
    ax_overlay.set_facecolor("#1a1e2b")

    for r in results_sorted:
        t = r['t_common']
        mask = t <= display_max
        ax_overlay.plot(t[mask], r['syn_norm'][mask], color=r['color'], lw=2, alpha=0.85,
                       label=f"{r['label']} ({r['correlation']:+.4f})")

    # Real on its own axis (for reference)
    real_t_display = real_t[real_t <= display_max]
    real_norm = normalize_peak(real_sig)
    real_norm_display = real_norm[:len(real_t_display)]
    ax_overlay.plot(real_t_display, real_norm_display, color='#ff6b35', lw=2.5, alpha=0.85,
                   label='Real (reference)', linestyle='-')

    ax_overlay.axhline(0, color='#2a2f42', lw=0.8, linestyle='-', alpha=0.5)
    ax_overlay.set_xlabel("Time (ns)", fontsize=10, color="#c8d0e0", fontweight='bold')
    ax_overlay.set_ylabel("Amplitude (norm)", fontsize=10, color="#c8d0e0", fontweight='bold')
    ax_overlay.set_title("All Configurations (Direct Waves Aligned)",
                        fontsize=11, color="#c8d0e0", fontweight='bold', pad=8)
    ax_overlay.grid(True, color="#2a2f42", lw=0.5, alpha=0.4)
    ax_overlay.legend(loc='upper right', fontsize=10, facecolor='#1a1e2b', labelcolor='#c8d0e0',
                     edgecolor='#2a2f42')
    ax_overlay.tick_params(colors="#c8d0e0", labelsize=9)
    for spine in ax_overlay.spines.values():
        spine.set_color("#2a2f42")

    fig.suptitle(
        "Direct Wave Aligned Comparison: Freespace vs Ballast vs Rocks\n"
        "Direct waves aligned to same peak time, then correlated",
        color="#c8d0e0", fontsize=13, fontweight='bold', y=0.995
    )

    png_path = Path("output_test") / "19_aligned_comparison.png"
    fig.savefig(png_path, dpi=150, bbox_inches='tight', facecolor="#0f1117")
    print(f"\n[SAVE] {png_path}\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())

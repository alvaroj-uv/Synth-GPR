#!/usr/bin/env python3
"""
Final comparison: Optimized ballast (eps=5.1) vs real field GPR.
Shows before/after optimization improvement.
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


def read_real_dzt(dzt_path: Path, trace_idx: int = 15000) -> tuple:
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


def find_direct_wave_peak(signal: np.ndarray, search_end_idx: int = None) -> int:
    """Find the peak index of the direct wave."""
    if search_end_idx is None:
        search_end_idx = len(signal)
    search_region = signal[:search_end_idx]
    return np.argmax(np.abs(search_region))


def align_and_correlate(syn_sig: np.ndarray, syn_t: np.ndarray, dt_syn: float,
                       real_sig: np.ndarray, real_t: np.ndarray, dt_real: float,
                       label: str = "") -> dict:
    """Align direct waves and compute correlation."""

    # Polarity flip
    syn_flipped = -syn_sig

    # Find direct wave peaks
    search_ns = 20
    search_idx_syn = int(search_ns / dt_syn)
    search_idx_real = int(search_ns / dt_real)

    peak_idx_syn = find_direct_wave_peak(syn_flipped, min(search_idx_syn, len(syn_flipped)))
    peak_idx_real = find_direct_wave_peak(real_sig, min(search_idx_real, len(real_sig)))

    peak_time_syn = syn_t[peak_idx_syn]
    peak_time_real = real_t[peak_idx_real]

    # Align peaks
    time_shift_ns = peak_time_real - peak_time_syn
    syn_t_shifted = syn_t + time_shift_ns

    # Resample to common dt
    t_min = max(syn_t_shifted[0], real_t[0])
    t_max = min(syn_t_shifted[-1], real_t[-1])
    t_common = np.arange(int((t_max - t_min) / dt_real) + 1) * dt_real + t_min

    f_syn = interp1d(syn_t_shifted, syn_flipped, kind='cubic', bounds_error=False, fill_value=0)
    f_real = interp1d(real_t, real_sig, kind='cubic', bounds_error=False, fill_value=0)

    syn_common = f_syn(t_common)
    real_common = f_real(t_common)

    # Normalize
    syn_norm = normalize_peak(syn_common)
    real_norm = normalize_peak(real_common)

    try:
        corr = np.corrcoef(syn_norm, real_norm)[0, 1]
    except:
        corr = np.nan

    return {
        'label': label,
        'correlation': corr,
        't_common': t_common,
        'syn_norm': syn_norm,
        'real_norm': real_norm,
    }


def main():
    # Load real data
    dzt_path = Path("D:/Codigo/Data/PUERTO-LIMACHE_20230726_EFE_V1_PKC000_588_PKF011_020_CENTRO_BRUTO.DZT")
    print(f"[LOAD] Real DZT: {dzt_path.name} (trace #15000)")
    real_sig, real_t, dt_real = read_real_dzt(dzt_path, trace_idx=15000)

    # Before and after optimization
    configs = [
        ("Ballast (eps=3.45, OLD 10ns)", "output_test/ballast_layer.out", "#ff9999"),
        ("Ballast (eps=5.1, OPTIMIZED 50ns)", "output_test/ballast_eps51_optimized.out", "#00ff88"),
    ]

    results = []

    print(f"\n{'='*80}")
    print("BALLAST OPTIMIZATION COMPARISON")
    print(f"{'='*80}\n")

    print(f"{'Configuration':<40} {'Correlation':<20}")
    print("-" * 80)

    for name, out_path, color in configs:
        try:
            out_p = Path(out_path)
            if not out_p.exists():
                print(f"{name:<40} FILE NOT FOUND")
                continue

            syn_sig, syn_t, dt_syn = read_synthetic_out(out_p)
            result = align_and_correlate(syn_sig, syn_t, dt_syn, real_sig, real_t, dt_real, name)
            result['color'] = color
            result['path'] = out_path
            results.append(result)

            print(f"{name:<40} {result['correlation']:>+10.6f}")

        except Exception as e:
            print(f"{name:<40} ERROR: {str(e)[:50]}")

    if len(results) < 2:
        print("[ERR] Need both before and after results")
        return 1

    # Calculate improvement
    old_corr = results[0]['correlation']
    new_corr = results[1]['correlation']
    improvement = new_corr - old_corr
    improvement_pct = (improvement / old_corr) * 100

    print(f"\n{'='*80}")
    print(f"IMPROVEMENT: {improvement:+.6f} ({improvement_pct:+.2f}%)")
    print(f"{'='*80}\n")

    # Plot
    fig = plt.figure(figsize=(16, 10))
    fig.patch.set_facecolor("#0f1117")
    gs = gridspec.GridSpec(3, 1, figure=fig, hspace=0.35,
                          left=0.1, right=0.95, top=0.96, bottom=0.08)

    display_max = 50  # Full 50 ns window

    # Row 1: Old ballast
    ax1 = fig.add_subplot(gs[0])
    ax1.set_facecolor("#1a1e2b")

    r = results[0]
    t = r['t_common']
    mask = t <= display_max

    ax1.plot(t[mask], r['syn_norm'][mask], color=r['color'], lw=2.5, alpha=0.85,
            label=f"Synthetic (eps=3.45)")
    ax1.plot(t[mask], r['real_norm'][mask], color='#ff6b35', lw=2.5, alpha=0.7,
            label='Real field GPR')
    ax1.axhline(0, color='#2a2f42', lw=0.8, linestyle='-', alpha=0.5)
    ax1.set_ylabel("Amplitude (norm)", fontsize=11, color="#c8d0e0", fontweight='bold')
    ax1.set_title(f"BEFORE: Ballast eps=3.45, 10ns window | Correlation: {r['correlation']:+.6f}",
                 fontsize=12, color="#ff9999", fontweight='bold', pad=10)
    ax1.grid(True, color="#2a2f42", lw=0.5, alpha=0.4)
    ax1.legend(loc='upper right', fontsize=10, facecolor='#1a1e2b', labelcolor='#c8d0e0',
              edgecolor='#2a2f42')
    ax1.tick_params(colors="#c8d0e0", labelsize=10)
    for spine in ax1.spines.values():
        spine.set_color("#2a2f42")

    # Row 2: New optimized ballast
    ax2 = fig.add_subplot(gs[1])
    ax2.set_facecolor("#1a1e2b")

    r = results[1]
    t = r['t_common']
    mask = t <= display_max

    ax2.plot(t[mask], r['syn_norm'][mask], color=r['color'], lw=2.5, alpha=0.85,
            label=f"Synthetic (eps=5.1)")
    ax2.plot(t[mask], r['real_norm'][mask], color='#ff6b35', lw=2.5, alpha=0.7,
            label='Real field GPR')
    ax2.axhline(0, color='#2a2f42', lw=0.8, linestyle='-', alpha=0.5)
    ax2.set_ylabel("Amplitude (norm)", fontsize=11, color="#c8d0e0", fontweight='bold')
    ax2.set_title(f"AFTER: Ballast eps=5.1, 50ns window (OPTIMIZED) | Correlation: {r['correlation']:+.6f}",
                 fontsize=12, color="#00ff88", fontweight='bold', pad=10)
    ax2.grid(True, color="#2a2f42", lw=0.5, alpha=0.4)
    ax2.legend(loc='upper right', fontsize=10, facecolor='#1a1e2b', labelcolor='#c8d0e0',
              edgecolor='#2a2f42')
    ax2.tick_params(colors="#c8d0e0", labelsize=10)
    for spine in ax2.spines.values():
        spine.set_color("#2a2f42")

    # Row 3: Improvement metrics
    ax3 = fig.add_subplot(gs[2])
    ax3.set_facecolor("#1a1e2b")
    ax3.axis('off')

    # Text box with improvements
    text_content = f"""
    OPTIMIZATION SUMMARY

    Before:    eps = 3.45  |  window = 10 ns   |  correlation = {old_corr:+.6f}
    After:     eps = 5.1   |  window = 50 ns   |  correlation = {new_corr:+.6f}

    Improvement:  {improvement:+.6f}  ({improvement_pct:+.2f}%)

    Key Changes:
    • Epsilon optimized from 3.45 to 5.1 (48% increase)
    • Time window extended from 10ns to 50ns (5x more coda data)
    • Full waveform now captured and compared
    • Cleaner ballast baseline established for fouling discrimination
    """

    ax3.text(0.1, 0.5, text_content, transform=ax3.transAxes,
            fontsize=11, verticalalignment='center', fontfamily='monospace',
            color='#c8d0e0', bbox=dict(boxstyle='round', facecolor='#2a2f42',
                                       edgecolor='#00ff88', linewidth=2, alpha=0.8))

    fig.suptitle(
        "Ballast Optimization: eps=3.45 (10ns) → eps=5.1 (50ns Full Coda)",
        color="#c8d0e0", fontsize=13, fontweight='bold', y=0.995
    )

    png_path = Path("output_test") / "ballast_optimization_before_after.png"
    fig.savefig(png_path, dpi=150, bbox_inches='tight', facecolor="#0f1117")
    print(f"[SAVE] {png_path}\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())

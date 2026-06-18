#!/usr/bin/env python3
"""
Show final aligned and treated real vs synthetic signals.
Clean visualization of preprocessed waveforms ready for analysis.
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


def main():
    # Load data
    dzt_path = Path("D:/Codigo/Data/PUERTO-LIMACHE_20230726_EFE_V1_PKC000_588_PKF011_020_CENTRO_BRUTO.DZT")
    out_path = Path("output_test/ballast_layer.out")  # Use optimized ballast

    print(f"[LOAD] Real DZT: {dzt_path.name}")
    real_sig_raw, real_t, dt_real = read_real_dzt(dzt_path, trace_idx=15000)

    print(f"[LOAD] Synthetic: {out_path.name}")
    syn_sig_raw, syn_t, dt_syn = read_synthetic_out(out_path)

    # ========================================================================
    # TREATMENT STEPS
    # ========================================================================

    # Step 1: Polarity flip synthetic
    print("\n[TREAT] Applying preprocessing:")
    print(f"  1. Polarity flip synthetic (multiply by -1)")
    syn_sig = -syn_sig_raw

    # Step 2: Find direct wave peaks
    search_ns = 20
    search_idx_syn = int(search_ns / dt_syn)
    search_idx_real = int(search_ns / dt_real)

    peak_idx_syn = find_direct_wave_peak(syn_sig, min(search_idx_syn, len(syn_sig)))
    peak_idx_real = find_direct_wave_peak(real_sig_raw, min(search_idx_real, len(real_sig_raw)))

    peak_time_syn = syn_t[peak_idx_syn]
    peak_time_real = real_t[peak_idx_real]

    print(f"  2. Find direct wave peaks")
    print(f"     - Synthetic peak: {peak_time_syn:.3f} ns (idx={peak_idx_syn})")
    print(f"     - Real peak:      {peak_time_real:.3f} ns (idx={peak_idx_real})")

    # Step 3: Align peaks
    time_shift_ns = peak_time_real - peak_time_syn
    print(f"  3. Align peaks (shift synthetic by {time_shift_ns:+.3f} ns)")
    syn_t_shifted = syn_t + time_shift_ns

    # Step 4: Resample to common dt
    print(f"  4. Resample to common dt (real's dt = {dt_real:.6f} ns)")
    t_min = max(syn_t_shifted[0], real_t[0])
    t_max = min(syn_t_shifted[-1], real_t[-1])
    t_common = np.arange(int((t_max - t_min) / dt_real) + 1) * dt_real + t_min

    f_syn = interp1d(syn_t_shifted, syn_sig, kind='cubic', bounds_error=False, fill_value=0)
    f_real = interp1d(real_t, real_sig_raw, kind='cubic', bounds_error=False, fill_value=0)

    syn_rs = f_syn(t_common)
    real_rs = f_real(t_common)

    # Step 5: Normalize
    print(f"  5. Normalize (peak normalization)")
    syn_norm = normalize_peak(syn_rs)
    real_norm = normalize_peak(real_rs)

    # Correlation
    corr = np.corrcoef(syn_norm, real_norm)[0, 1]
    print(f"  6. Compute correlation: {corr:+.6f}")

    # ========================================================================
    # VISUALIZATION
    # ========================================================================

    fig = plt.figure(figsize=(16, 12))
    fig.patch.set_facecolor("#0f1117")
    gs = gridspec.GridSpec(3, 2, figure=fig, hspace=0.4, wspace=0.3,
                          left=0.1, right=0.95, top=0.96, bottom=0.06)

    # Colors
    c_syn = "#00d9ff"  # Cyan
    c_real = "#ff6b35"  # Orange-red

    # ========================================================================
    # Row 1: Raw signals (original)
    # ========================================================================

    ax1a = fig.add_subplot(gs[0, 0])
    ax1a.set_facecolor("#1a1e2b")
    ax1a.plot(syn_t, syn_sig_raw, color=c_syn, lw=1, alpha=0.7, label="Synthetic (raw)")
    ax1a.axvline(peak_time_syn, color=c_syn, linestyle='--', alpha=0.5, linewidth=1.5, label=f"Peak: {peak_time_syn:.2f}ns")
    ax1a.axhline(0, color='#2a2f42', lw=0.8, linestyle='-', alpha=0.5)
    ax1a.set_ylabel("Amplitude (V/m)", fontsize=10, color="#c8d0e0", fontweight='bold')
    ax1a.set_title("Raw Synthetic (before treatment)", fontsize=11, color="#c8d0e0", fontweight='bold')
    ax1a.grid(True, color="#2a2f42", lw=0.5, alpha=0.3)
    ax1a.legend(fontsize=9, facecolor='#1a1e2b', labelcolor='#c8d0e0', edgecolor='#2a2f42', loc='upper right')
    ax1a.tick_params(colors="#c8d0e0", labelsize=9)
    for spine in ax1a.spines.values():
        spine.set_color("#2a2f42")

    ax1b = fig.add_subplot(gs[0, 1])
    ax1b.set_facecolor("#1a1e2b")
    ax1b.plot(real_t, real_sig_raw, color=c_real, lw=1, alpha=0.7, label="Real (raw)")
    ax1b.axvline(peak_time_real, color=c_real, linestyle='--', alpha=0.5, linewidth=1.5, label=f"Peak: {peak_time_real:.2f}ns")
    ax1b.axhline(0, color='#2a2f42', lw=0.8, linestyle='-', alpha=0.5)
    ax1b.set_ylabel("Amplitude (A/D counts)", fontsize=10, color="#c8d0e0", fontweight='bold')
    ax1b.set_title("Raw Real (before treatment)", fontsize=11, color="#c8d0e0", fontweight='bold')
    ax1b.grid(True, color="#2a2f42", lw=0.5, alpha=0.3)
    ax1b.legend(fontsize=9, facecolor='#1a1e2b', labelcolor='#c8d0e0', edgecolor='#2a2f42', loc='upper right')
    ax1b.tick_params(colors="#c8d0e0", labelsize=9)
    for spine in ax1b.spines.values():
        spine.set_color("#2a2f42")

    # ========================================================================
    # Row 2: After polarity flip & alignment (on original time grids)
    # ========================================================================

    ax2a = fig.add_subplot(gs[1, 0])
    ax2a.set_facecolor("#1a1e2b")
    ax2a.plot(syn_t_shifted, syn_sig, color=c_syn, lw=1, alpha=0.7, label="Synthetic (flipped, shifted)")
    ax2a.axvline(peak_time_syn, color=c_syn, linestyle='--', alpha=0.5, linewidth=1.5, label="Peak aligned")
    ax2a.axhline(0, color='#2a2f42', lw=0.8, linestyle='-', alpha=0.5)
    ax2a.set_ylabel("Amplitude (V/m)", fontsize=10, color="#c8d0e0", fontweight='bold')
    ax2a.set_title(f"After Polarity Flip & Peak Alignment (shift={time_shift_ns:+.2f}ns)",
                  fontsize=11, color="#c8d0e0", fontweight='bold')
    ax2a.set_xlim([0, 50])
    ax2a.grid(True, color="#2a2f42", lw=0.5, alpha=0.3)
    ax2a.legend(fontsize=9, facecolor='#1a1e2b', labelcolor='#c8d0e0', edgecolor='#2a2f42', loc='upper right')
    ax2a.tick_params(colors="#c8d0e0", labelsize=9)
    for spine in ax2a.spines.values():
        spine.set_color("#2a2f42")

    ax2b = fig.add_subplot(gs[1, 1])
    ax2b.set_facecolor("#1a1e2b")
    ax2b.plot(real_t, real_sig_raw, color=c_real, lw=1, alpha=0.7, label="Real (reference)")
    ax2b.axvline(peak_time_real, color=c_real, linestyle='--', alpha=0.5, linewidth=1.5, label="Peak reference")
    ax2b.axhline(0, color='#2a2f42', lw=0.8, linestyle='-', alpha=0.5)
    ax2b.set_ylabel("Amplitude (A/D counts)", fontsize=10, color="#c8d0e0", fontweight='bold')
    ax2b.set_title("Real (reference time grid)", fontsize=11, color="#c8d0e0", fontweight='bold')
    ax2b.set_xlim([0, 50])
    ax2b.grid(True, color="#2a2f42", lw=0.5, alpha=0.3)
    ax2b.legend(fontsize=9, facecolor='#1a1e2b', labelcolor='#c8d0e0', edgecolor='#2a2f42', loc='upper right')
    ax2b.tick_params(colors="#c8d0e0", labelsize=9)
    for spine in ax2b.spines.values():
        spine.set_color("#2a2f42")

    # ========================================================================
    # Row 3: Final normalized & resampled (common grid)
    # ========================================================================

    ax3 = fig.add_subplot(gs[2, :])
    ax3.set_facecolor("#1a1e2b")

    mask = t_common <= 50
    ax3.plot(t_common[mask], syn_norm[mask], color=c_syn, lw=2, alpha=0.85,
            label=f"Synthetic (treated, normalized)")
    ax3.plot(t_common[mask], real_norm[mask], color=c_real, lw=2, alpha=0.85,
            label=f"Real (normalized)")
    ax3.fill_between(t_common[mask], syn_norm[mask], real_norm[mask], alpha=0.15, color='yellow')

    ax3.axhline(0, color='#2a2f42', lw=0.8, linestyle='-', alpha=0.5)
    ax3.set_xlabel("Time (ns)", fontsize=11, color="#c8d0e0", fontweight='bold')
    ax3.set_ylabel("Normalized Amplitude", fontsize=11, color="#c8d0e0", fontweight='bold')
    ax3.set_title(f"FINAL: Aligned & Normalized Signals (Correlation: {corr:+.6f})",
                 fontsize=12, color="#c8d0e0", fontweight='bold', pad=12)
    ax3.grid(True, color="#2a2f42", lw=0.5, alpha=0.3)
    ax3.legend(fontsize=11, facecolor='#1a1e2b', labelcolor='#c8d0e0', edgecolor='#2a2f42',
              loc='upper right', ncol=2)
    ax3.tick_params(colors="#c8d0e0", labelsize=10)
    for spine in ax3.spines.values():
        spine.set_color("#2a2f42")
        spine.set_linewidth(1.5)

    # Main title
    fig.suptitle(
        "Signal Treatment Pipeline: Raw → Aligned → Normalized\n"
        "420 MHz Gaussian Ballast Layer vs Puerto-Limache Field Data",
        color="#c8d0e0", fontsize=13, fontweight='bold', y=0.995
    )

    # Save
    png_path = Path("output_test") / "21_aligned_treated_signals.png"
    fig.savefig(png_path, dpi=150, bbox_inches='tight', facecolor="#0f1117")
    print(f"\n[SAVE] {png_path}\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())

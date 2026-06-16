#!/usr/bin/env python3
"""Overlay free space synthetic (.out) over real DZT trace for direct wave comparison."""

import sys
from pathlib import Path
import struct
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from scipy.signal import hilbert, spectrogram
from scipy.interpolate import interp1d

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data_loader import read_ascan
from src.signal_processing import (
    compute_padded_spectrum,
    calculate_instantaneous_attributes,
    remove_direct_wave,
)
from src.constants import SC

# Waveform scaling factor (computed 2026-06-16)
SCALE_FACTOR = 2592.594444  # synthetic V/m → real A/D counts


def read_dzt_single_trace(dzt_path: Path, trace_idx: int = 1000) -> tuple:
    """Read one DZT trace (128KiB header, int32 samples)."""
    HEADER_SIZE = 128 * 1024
    SAMPLES_PER_TRACE = 512
    BYTES_PER_SAMPLE = 4
    DT_NS = 50 / 511

    with open(dzt_path, 'rb') as f:
        f.seek(HEADER_SIZE + trace_idx * SAMPLES_PER_TRACE * BYTES_PER_SAMPLE)
        trace_bytes = f.read(SAMPLES_PER_TRACE * BYTES_PER_SAMPLE)
        trace = np.frombuffer(trace_bytes, dtype=np.int32, count=SAMPLES_PER_TRACE)
        trace = trace.astype(np.float64)

    # Drop indices 0-1
    trace = trace[2:]
    t_ns = np.arange(len(trace)) * DT_NS

    return trace, t_ns, DT_NS


def read_synthetic_out(out_path: Path) -> tuple:
    """Read synthetic free space .out file."""
    data = read_ascan(out_path, 'Ez')
    signal = data['signal']
    dt = data['dt']

    # Time axis in ns
    t_ns = np.arange(len(signal)) * dt * 1e9

    return signal, t_ns, dt


def align_waveforms(syn_signal, syn_t, real_signal, real_t):
    """
    Align synthetic to real by matching peak times.
    Interpolate synthetic to real time grid.
    """
    # Find peaks
    syn_peak_idx = np.argmax(np.abs(syn_signal))
    syn_peak_time = syn_t[syn_peak_idx]

    real_peak_idx = np.argmax(np.abs(real_signal))
    real_peak_time = real_t[real_peak_idx]

    # Time offset
    dt_peak = real_peak_time - syn_peak_time

    # Shift synthetic time axis
    syn_t_shifted = syn_t + dt_peak

    # Interpolate synthetic to real time grid
    f_interp = interp1d(
        syn_t_shifted, syn_signal,
        kind='linear',
        bounds_error=False,
        fill_value=0.0
    )
    syn_interp = f_interp(real_t)

    return syn_interp, real_peak_time, syn_peak_time


def main():
    # Paths
    out_file = Path('output_test/freespace_400mhz.out')
    dzt_file = Path('D:/Codigo/Data/PUERTO-LIMACHE_20230726_EFE_V1_PKC000_588_PKF011_020_CENTRO_BRUTO.DZT')

    if not out_file.exists():
        print(f"[ERR] Synthetic file not found: {out_file}")
        sys.exit(1)
    if not dzt_file.exists():
        print(f"[ERR] DZT file not found: {dzt_file}")
        sys.exit(1)

    print(f"[READ] Synthetic: {out_file.name}")
    syn_raw, syn_t, syn_dt = read_synthetic_out(out_file)

    # Scale synthetic to real amplitude
    syn_scaled = np.abs(syn_raw) * SCALE_FACTOR

    print(f"[READ] Real DZT trace #1000: {dzt_file.name}")
    real_raw, real_t, real_dt = read_dzt_single_trace(dzt_file, trace_idx=1000)

    # Align peaks
    print(f"[ALIGN] Matching peak times...")
    syn_aligned, real_peak_t, syn_peak_t = align_waveforms(syn_scaled, syn_t, real_raw, real_t)

    print(f"  Synthetic peak: {syn_peak_t:.4f} ns")
    print(f"  Real peak:      {real_peak_t:.4f} ns")
    print(f"  Time offset:    {real_peak_t - syn_peak_t:.4f} ns")

    # Direct wave end (for gating)
    dw_end_syn = syn_peak_t + SC.CODA_GATE_START_AFTER_PEAK_NS
    dw_end_real = real_peak_t + SC.CODA_GATE_START_AFTER_PEAK_NS

    # Gate both signals (use real_t for both since syn_aligned is interpolated to real_t)
    syn_gated = syn_aligned.copy()
    syn_gated[real_t < dw_end_syn] = 0
    real_gated = real_raw.copy()
    real_gated[real_t < dw_end_real] = 0

    # Frequency spectra
    freqs_syn, spec_syn, peak_hz_syn = compute_padded_spectrum(syn_scaled, syn_dt)
    freqs_real, spec_real, peak_hz_real = compute_padded_spectrum(real_raw, real_dt)

    # --- Figure: 6-panel overlay comparison ---
    fig = plt.figure(figsize=(20, 12))
    fig.patch.set_facecolor("#0f1117")
    gs = gridspec.GridSpec(3, 4, figure=fig, hspace=0.4, wspace=0.35,
                           left=0.05, right=0.98, top=0.92, bottom=0.08)

    dark_bg = "#0f1117"
    panel_bg = "#1a1e2b"
    accent_syn = "#00d4ff"  # cyan (synthetic)
    accent_real = "#ff6b35"  # orange (real)
    accent_overlay = "#00ff00"  # green (overlay)
    grid_col = "#2a2f42"
    text_col = "#c8d0e0"

    # Panel 1: Full overlay - raw signals
    ax1 = fig.add_subplot(gs[0, :2])
    ax1.set_facecolor(panel_bg)
    ax1.plot(syn_t, syn_scaled, color=accent_syn, lw=1.2, alpha=0.8, label='Synthetic (scaled)')
    ax1.plot(real_t, real_raw, color=accent_real, lw=1.0, alpha=0.7, label='Real DZT trace #1000')
    ax1.axvline(dw_end_syn, color=accent_syn, linestyle='--', lw=1, alpha=0.5)
    ax1.axvline(dw_end_real, color=accent_real, linestyle='--', lw=1, alpha=0.5)
    ax1.axhline(0, color=grid_col, lw=0.5)
    ax1.set_xlabel("Time (ns)", color=text_col, fontsize=9)
    ax1.set_ylabel("Amplitude (A/D counts)", color=text_col, fontsize=9)
    ax1.set_title("Full Overlay (Raw Signals)", color=text_col, fontsize=10, fontweight='bold')
    ax1.tick_params(colors=text_col, labelsize=8)
    ax1.legend(fontsize=8, facecolor=panel_bg, labelcolor=text_col, edgecolor=grid_col)
    ax1.grid(True, color=grid_col, lw=0.4, alpha=0.5)
    for spine in ax1.spines.values():
        spine.set_edgecolor(grid_col)

    # Panel 2: Zoomed early-time (direct pulse only)
    ax2 = fig.add_subplot(gs[0, 2:])
    ax2.set_facecolor(panel_bg)
    idx_early_syn = syn_t <= 10.0
    idx_early_real = real_t <= 10.0
    ax2.plot(syn_t[idx_early_syn], syn_scaled[idx_early_syn], color=accent_syn, lw=1.5,
             alpha=0.8, label=f'Synthetic (peak={np.max(syn_scaled[idx_early_syn]):.2e})')
    ax2.plot(real_t[idx_early_real], real_raw[idx_early_real], color=accent_real, lw=1.2,
             alpha=0.7, label=f'Real (peak={np.max(real_raw[idx_early_real]):.2e})')
    ax2.axvline(syn_peak_t, color=accent_syn, linestyle='--', lw=1.5, alpha=0.6)
    ax2.axvline(real_peak_t, color=accent_real, linestyle='--', lw=1.5, alpha=0.6)
    ax2.axhline(0, color=grid_col, lw=0.5)
    ax2.set_xlabel("Time (ns)", color=text_col, fontsize=9)
    ax2.set_ylabel("Amplitude (A/D counts)", color=text_col, fontsize=9)
    ax2.set_title("Early-time Zoom (Direct Pulse)", color=text_col, fontsize=10, fontweight='bold')
    ax2.tick_params(colors=text_col, labelsize=8)
    ax2.legend(fontsize=8, facecolor=panel_bg, labelcolor=text_col, edgecolor=grid_col)
    ax2.grid(True, color=grid_col, lw=0.4, alpha=0.5)
    for spine in ax2.spines.values():
        spine.set_edgecolor(grid_col)

    # Panel 3: Overlay after interpolation
    ax3 = fig.add_subplot(gs[1, 0])
    ax3.set_facecolor(panel_bg)
    ax3.plot(real_t, real_raw, color=accent_real, lw=1.2, alpha=0.8, label='Real (original)')
    ax3.plot(real_t, syn_aligned, color=accent_syn, lw=1.0, alpha=0.7, label='Synthetic (aligned)')
    ax3.axhline(0, color=grid_col, lw=0.5)
    ax3.set_xlabel("Time (ns)", color=text_col, fontsize=8)
    ax3.set_ylabel("Amplitude (A/D counts)", color=text_col, fontsize=8)
    ax3.set_title("Aligned (shared time grid)", color=text_col, fontsize=9, fontweight='bold')
    ax3.tick_params(colors=text_col, labelsize=7)
    ax3.legend(fontsize=7, facecolor=panel_bg, labelcolor=text_col, edgecolor=grid_col)
    ax3.grid(True, color=grid_col, lw=0.4, alpha=0.5)
    for spine in ax3.spines.values():
        spine.set_edgecolor(grid_col)

    # Panel 4: Direct wave gated
    ax4 = fig.add_subplot(gs[1, 1])
    ax4.set_facecolor(panel_bg)
    ax4.plot(real_t, real_gated, color=accent_real, lw=1.2, alpha=0.8, label='Real (gated)')
    ax4.plot(real_t, syn_gated, color=accent_syn, lw=1.0, alpha=0.7, label='Synthetic (gated)')
    ax4.axvspan(0, dw_end_real, alpha=0.1, color=accent_real)
    ax4.axhline(0, color=grid_col, lw=0.5)
    ax4.set_xlabel("Time (ns)", color=text_col, fontsize=8)
    ax4.set_ylabel("Amplitude (A/D counts)", color=text_col, fontsize=8)
    ax4.set_title(f"After DW Removal (gate>{dw_end_real:.1f}ns)", color=text_col, fontsize=9)
    ax4.tick_params(colors=text_col, labelsize=7)
    ax4.legend(fontsize=7, facecolor=panel_bg, labelcolor=text_col, edgecolor=grid_col)
    ax4.grid(True, color=grid_col, lw=0.4, alpha=0.5)
    for spine in ax4.spines.values():
        spine.set_edgecolor(grid_col)

    # Panel 5: Hilbert envelopes
    ax5 = fig.add_subplot(gs[1, 2:])
    ax5.set_facecolor(panel_bg)

    # Normalize for envelope comparison
    syn_norm = syn_scaled / np.max(np.abs(syn_scaled))
    real_norm = real_raw / np.max(np.abs(real_raw))

    attrs_syn = calculate_instantaneous_attributes(syn_norm, syn_dt)
    attrs_real = calculate_instantaneous_attributes(real_norm, real_dt)

    env_syn = attrs_syn['envelope']
    env_real = attrs_real['envelope']

    ax5.plot(syn_t, syn_norm, color=accent_syn, lw=0.5, alpha=0.4, label='Synthetic (normalized)')
    ax5.plot(syn_t, env_syn, color=accent_syn, lw=1.5, label='Synthetic envelope')

    ax5.plot(real_t, real_norm, color=accent_real, lw=0.5, alpha=0.4, label='Real (normalized)')
    ax5.plot(real_t, env_real, color=accent_real, lw=1.5, label='Real envelope')

    ax5.set_xlabel("Time (ns)", color=text_col, fontsize=8)
    ax5.set_ylabel("Amplitude (normalized)", color=text_col, fontsize=8)
    ax5.set_title("Hilbert Envelopes Comparison", color=text_col, fontsize=9, fontweight='bold')
    ax5.tick_params(colors=text_col, labelsize=7)
    ax5.legend(fontsize=7, facecolor=panel_bg, labelcolor=text_col, edgecolor=grid_col, loc='upper right')
    ax5.grid(True, color=grid_col, lw=0.4, alpha=0.5)
    for spine in ax5.spines.values():
        spine.set_edgecolor(grid_col)

    # Panel 6: Frequency spectra
    ax6 = fig.add_subplot(gs[2, 0:2])
    ax6.set_facecolor(panel_bg)
    freq_ghz_syn = freqs_syn / 1e9
    freq_ghz_real = freqs_real / 1e9
    ax6.semilogy(freq_ghz_syn, spec_syn, color=accent_syn, lw=1.5, alpha=0.8, label='Synthetic')
    ax6.semilogy(freq_ghz_real, spec_real, color=accent_real, lw=1.2, alpha=0.7, label='Real')
    ax6.axvline(peak_hz_syn/1e9, color=accent_syn, linestyle='--', lw=1.2, alpha=0.6)
    ax6.axvline(peak_hz_real/1e9, color=accent_real, linestyle='--', lw=1.2, alpha=0.6)
    ax6.set_xlabel("Frequency (GHz)", color=text_col, fontsize=8)
    ax6.set_ylabel("Magnitude (log)", color=text_col, fontsize=8)
    ax6.set_title("Frequency Spectra", color=text_col, fontsize=9, fontweight='bold')
    ax6.set_xlim([0, 2.0])
    ax6.tick_params(colors=text_col, labelsize=7)
    ax6.legend(fontsize=7, facecolor=panel_bg, labelcolor=text_col, edgecolor=grid_col)
    ax6.grid(True, color=grid_col, lw=0.4, alpha=0.5, which='both')
    for spine in ax6.spines.values():
        spine.set_edgecolor(grid_col)

    # Panel 7: Spectrograms (synthetic)
    ax7 = fig.add_subplot(gs[2, 2])
    ax7.set_facecolor(panel_bg)
    f_syn, t_syn_spec, Sxx_syn = spectrogram(syn_scaled, fs=1/syn_dt, nperseg=64, noverlap=32)
    pcm7 = ax7.pcolormesh(t_syn_spec*1e9, f_syn/1e9, 10*np.log10(Sxx_syn+1e-12),
                          shading='auto', cmap='viridis')
    ax7.set_xlabel("Time (ns)", color=text_col, fontsize=7)
    ax7.set_ylabel("Frequency (GHz)", color=text_col, fontsize=7)
    ax7.set_title("Synthetic STFT", color=accent_syn, fontsize=8, fontweight='bold')
    ax7.set_ylim([0, 1.5])
    ax7.tick_params(colors=text_col, labelsize=6)
    for spine in ax7.spines.values():
        spine.set_edgecolor(grid_col)

    # Panel 8: Spectrograms (real)
    ax8 = fig.add_subplot(gs[2, 3])
    ax8.set_facecolor(panel_bg)
    f_real, t_real_spec, Sxx_real = spectrogram(real_raw, fs=1/real_dt, nperseg=64, noverlap=32)
    pcm8 = ax8.pcolormesh(t_real_spec*1e9, f_real/1e9, 10*np.log10(Sxx_real+1e-12),
                          shading='auto', cmap='viridis')
    ax8.set_xlabel("Time (ns)", color=text_col, fontsize=7)
    ax8.set_ylabel("Frequency (GHz)", color=text_col, fontsize=7)
    ax8.set_title("Real STFT", color=accent_real, fontsize=8, fontweight='bold')
    ax8.set_ylim([0, 1.5])
    ax8.tick_params(colors=text_col, labelsize=6)
    for spine in ax8.spines.values():
        spine.set_edgecolor(grid_col)

    # Main title
    fig.suptitle(
        f"Synthetic-Real Direct Wave Overlay — Free Space 400MHz vs Puerto-Limache DZT (Trace #1000)  |  Scale: ×{SCALE_FACTOR:.2f}",
        color=text_col, fontsize=13, fontweight='bold', y=0.97,
    )

    # Save
    out_png = Path('output_test/overlay_synthetic_real_directwave.png')
    fig.savefig(out_png, dpi=150, bbox_inches='tight', facecolor=dark_bg)
    plt.close(fig)

    print(f"\n[OK] Overlay visualization saved -> {out_png}")
    print(f"\n{'='*70}")
    print("COMPARISON SUMMARY")
    print(f"{'='*70}")
    print(f"Synthetic peak (V/m):      {np.max(syn_raw):.4e}")
    print(f"Synthetic peak (scaled):   {np.max(syn_scaled):.4e} A/D counts")
    print(f"Real peak:                 {np.max(real_raw):.4e} A/D counts")
    print(f"Scale factor applied:      {SCALE_FACTOR:.2f}x")
    print(f"Synthetic peak time:       {syn_peak_t:.4f} ns")
    print(f"Real peak time:            {real_peak_t:.4f} ns")
    print(f"Time alignment offset:     {real_peak_t - syn_peak_t:.4f} ns")
    print(f"Synthetic dominant freq:   {peak_hz_syn/1e9:.3f} GHz")
    print(f"Real dominant freq:        {peak_hz_real/1e9:.3f} GHz")
    print(f"\nSynthetic samples:         {len(syn_scaled)}")
    print(f"Real samples:              {len(real_raw)}")
    print(f"Synthetic dt:              {syn_dt*1e9:.4f} ns")
    print(f"Real dt:                   {real_dt:.4f} ns")


if __name__ == "__main__":
    main()

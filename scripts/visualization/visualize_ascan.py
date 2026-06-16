"""
Visualize A-scans with frequency spectrum.

Supports:
- Synthetic: gprMax .out files (V/m physical units)
- Real field: DZT files (A/D converter counts) - .DZT or .dzt
- Extracted traces: .npy files (from binary DZT extraction)

Usage:
    # Synthetic gprMax output
    python scripts/visualization/visualize_ascan.py output_test/angular_rocks_400MHz.out
    python scripts/visualization/visualize_ascan.py output_test/angular_rocks_400MHz.out --component Ez

    # Real DZT field data (auto-detected)
    python scripts/visualization/visualize_ascan.py D:/Codigo/Data/PUERTO-LIMACHE_*.DZT --trace 50

    # Extracted numpy trace
    python scripts/visualization/visualize_ascan.py output_test/dzt_trace_1000.npy
"""
import sys
import argparse
import struct
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from scipy.signal import hilbert, find_peaks, spectrogram
from scipy.stats import skew, kurtosis

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from src.data_loader import read_ascan
from src.signal_processing import (
    compute_padded_spectrum,
    calculate_instantaneous_attributes,
    detect_first_break,
    dewow,
    remove_direct_wave,
)
from src.file_reader import parse_metadata_file
from src.dzt_io import get_dzt_metadata
from src.constants import SC


def read_dzt_trace(dzt_path: Path, trace_idx: int = 50) -> tuple:
    """
    Read a single A-scan from DZT file (drop first 2 samples).
    Extracts antenna metadata from DZT header.

    Returns:
        (signal, dt_ns, metadata)
    """
    HEADER_SIZE = 128 * 1024
    SAMPLES_PER_TRACE = 512
    BYTES_PER_SAMPLE = 4
    DT_NS = 50 / 511  # nanoseconds per sample

    with open(dzt_path, 'rb') as f:
        header = f.read(HEADER_SIZE)
        data = f.read()
        data_size_aligned = (len(data) // BYTES_PER_SAMPLE) * BYTES_PER_SAMPLE
        data_aligned = data[:data_size_aligned]
        num_samples_total = data_size_aligned // BYTES_PER_SAMPLE
        fmt = f'<{num_samples_total}i'
        all_samples = struct.unpack(fmt, data_aligned)
        all_samples = np.array(all_samples, dtype=np.float32)
        num_complete_traces = len(all_samples) // SAMPLES_PER_TRACE
        all_samples = all_samples[:num_complete_traces * SAMPLES_PER_TRACE]
        traces_raw = all_samples.reshape(-1, SAMPLES_PER_TRACE)

    # Drop first 2 samples (indices 0-1: timing markers)
    trace = traces_raw[min(trace_idx, traces_raw.shape[0]-1), 2:]

    # GSSI antenna specs (from Data/README.md: GSSI 400 MHz, ground-coupled)
    # Extracted from filename or use defaults
    antenna_name = 'GSSI 400 MHz'
    antenna_freq_hz = 400e6
    system = 'GSSI SIR-3000'

    metadata = {
        'file': dzt_path.name,
        'trace_idx': trace_idx,
        'total_traces': traces_raw.shape[0],
        'samples_per_trace': len(trace),
        'dt_ns': DT_NS,
        'time_window_ns': len(trace) * DT_NS,
        'antenna_name': antenna_name,
        'antenna_freq_hz': antenna_freq_hz,
        'antenna_freq_mhz': antenna_freq_hz / 1e6,
        'system': system,
    }

    return trace, DT_NS, metadata


def read_npy_trace(npy_path: Path) -> tuple:
    """
    Read a single A-scan from numpy .npy file.

    Assumes:
    - Signal is 1D float64 array
    - dt = 50/511 ns (standard DZT sampling) unless specified in filename
    - Already cleaned (indices 0-1 dropped if applicable)

    Returns:
        (signal, dt_ns, metadata)
    """
    # Load numpy array
    signal = np.load(npy_path).astype(np.float64)

    # Default: DZT sampling rate (50/511 ns per sample)
    DT_NS = 50 / 511

    # Try to extract dt from filename if it contains "dt_" or similar
    filename = npy_path.stem
    # For now, use standard DZT dt

    metadata = {
        'file': npy_path.name,
        'source': 'numpy_extraction',
        'samples_per_trace': len(signal),
        'dt_ns': DT_NS,
        'time_window_ns': len(signal) * DT_NS,
        'antenna_name': 'GSSI 400 MHz (extracted)',
        'antenna_freq_hz': 400e6,
        'antenna_freq_mhz': 400.0,
        'system': 'Extracted from DZT',
    }

    return signal, DT_NS, metadata


def read_header_meta(in_path: Path) -> dict:
    """Extract ## comment metadata from the companion .in file (shared parser)."""
    if not in_path.exists():
        return {}
    return parse_metadata_file(in_path)


def visualize_simple_wave(signal, t_ns, file_path: Path, title: str = "A-scan", unit: str = "V/m") -> Path:
    """
    Generate a simple, clean single-wave visualization.

    Args:
        signal: 1D waveform array
        t_ns: Time axis in nanoseconds
        file_path: Output PNG path
        title: Plot title
        unit: Y-axis unit label
    """
    fig, ax = plt.subplots(figsize=(14, 6))
    fig.patch.set_facecolor("#0f1117")
    ax.set_facecolor("#1a1e2b")

    # Plot signal
    ax.plot(t_ns, signal, color="#00d4ff", lw=1.5, alpha=0.95)
    ax.axhline(0, color="#2a2f42", lw=1.0, linestyle='-', alpha=0.7)
    ax.fill_between(t_ns, signal, 0, alpha=0.15, color="#00d4ff")

    # Find and mark peak
    peak_idx = np.argmax(np.abs(signal))
    peak_time = t_ns[peak_idx]
    peak_amp = signal[peak_idx]
    ax.plot(peak_time, peak_amp, color="#ff6b35", marker='o', markersize=10,
            markeredgewidth=2, markerfacecolor='none', zorder=5)
    ax.annotate(f'Peak: {peak_amp:.2e}\n@ {peak_time:.2f} ns',
                xy=(peak_time, peak_amp),
                xytext=(peak_time + 2, peak_amp * 0.7),
                fontsize=10, color="#ff6b35",
                bbox=dict(boxstyle='round,pad=0.5', facecolor='#1a1e2b', edgecolor='#ff6b35', linewidth=1.5),
                arrowprops=dict(arrowstyle='->', color='#ff6b35', lw=1.5))

    # Labels and title
    ax.set_xlabel("Time (ns)", fontsize=12, color="#c8d0e0", fontweight='bold')
    ax.set_ylabel(f"Amplitude ({unit})", fontsize=12, color="#c8d0e0", fontweight='bold')
    ax.set_title(title, fontsize=14, color="#c8d0e0", fontweight='bold', pad=20)

    # Grid
    ax.grid(True, color="#2a2f42", lw=0.5, alpha=0.6, linestyle='-')
    ax.set_axisbelow(True)

    # Spines
    for spine in ax.spines.values():
        spine.set_color("#2a2f42")
        spine.set_linewidth(1.5)

    # Ticks
    ax.tick_params(colors="#c8d0e0", labelsize=10, width=1.5, length=6)

    # Statistics text
    rms = np.sqrt(np.mean(signal**2))
    stats_text = (
        f"Samples: {len(signal):,}\n"
        f"Peak: {np.max(signal):.2e}\n"
        f"Min: {np.min(signal):.2e}\n"
        f"RMS: {rms:.2e}\n"
        f"Δt: {t_ns[-1] - t_ns[0]:.2f} ns"
    )
    ax.text(0.98, 0.97, stats_text, transform=ax.transAxes,
            fontsize=9, verticalalignment='top', horizontalalignment='right',
            bbox=dict(boxstyle='round', facecolor='#1a1e2b', edgecolor='#00d4ff',
                     linewidth=1.5, alpha=0.9),
            fontfamily='monospace', color="#c8d0e0")

    plt.tight_layout()
    plt.savefig(file_path, dpi=150, bbox_inches='tight', facecolor="#0f1117")
    plt.close(fig)

    return file_path


def visualize_npy_ascan(npy_path: Path) -> Path:
    """Visualize a numpy-extracted A-scan (typically from DZT binary extraction)."""
    npy_path = npy_path.resolve()

    # Read NPY trace
    signal, dt_ns, meta = read_npy_trace(npy_path)
    t_ns = np.arange(len(signal)) * dt_ns

    # Auto-detect direct wave end using peak-relative gating
    idx_early = t_ns <= 20.0
    if idx_early.any():
        signal_early = signal[idx_early]
        t_early = t_ns[idx_early]

        # Find the direct pulse peak
        peak_idx = np.argmax(np.abs(signal_early))
        peak_time = t_early[peak_idx]

        # Direct wave ends at: peak_time + CODA_GATE_START_AFTER_PEAK_NS (4.5 ns)
        direct_wave_end = peak_time + SC.CODA_GATE_START_AFTER_PEAK_NS
    else:
        direct_wave_end = 5.0  # fallback

    # Apply time gating to remove direct wave
    signal_gated = remove_direct_wave(signal, dt_ns * 1e-9, method='time_gate', gate_ns=direct_wave_end)

    # Frequency spectrum
    idx_after_dw = t_ns >= direct_wave_end
    if idx_after_dw.any():
        signal_spectrum = signal_gated[idx_after_dw]
    else:
        signal_spectrum = signal_gated
    freqs, spectrum, peak_hz = compute_padded_spectrum(signal_spectrum, dt_ns * 1e-9)
    freq_ghz = freqs / 1e9
    peak_ghz = peak_hz / 1e9

    # --- Figure layout: 6-panel (same style as DZT) ---
    fig = plt.figure(figsize=(18, 10))
    fig.patch.set_facecolor("#0f1117")
    gs = gridspec.GridSpec(3, 4, figure=fig, hspace=0.35, wspace=0.3,
                           left=0.06, right=0.98, top=0.92, bottom=0.08)

    dark_bg   = "#0f1117"
    panel_bg  = "#1a1e2b"
    accent    = "#00d4ff"
    accent2   = "#ff6b35"
    accent3   = "#80e080"
    grid_col  = "#2a2f42"
    text_col  = "#c8d0e0"

    # Panel 1: Full A-scan with direct wave removed
    ax1 = fig.add_subplot(gs[0, :])
    ax1.set_facecolor(panel_bg)

    ax1.plot(t_ns, signal_gated, color=accent, lw=0.8, alpha=0.92, label='Signal (direct wave removed)')
    ax1.axhline(0, color=grid_col, lw=0.5)

    # Mark direct wave region that was removed
    ax1.axvspan(0, direct_wave_end, alpha=0.1, color=accent2, label=f'Removed direct wave (0–{direct_wave_end:.1f} ns)')

    for spine in ax1.spines.values():
        spine.set_edgecolor(grid_col)
    ax1.set_xlabel("Time (ns)", color=text_col, fontsize=9)
    ax1.set_ylabel("Amplitude (A/D counts)", color=text_col, fontsize=9)
    ax1.set_title(f"Numpy-Extracted A-scan (Trace) — Full window {t_ns[-1]:.1f} ns",
                  color=text_col, fontsize=10, fontweight='bold')
    ax1.tick_params(colors=text_col, labelsize=8)
    ax1.grid(True, color=grid_col, lw=0.5, alpha=0.6)
    ax1.legend(fontsize=8, facecolor=panel_bg, labelcolor=text_col, edgecolor=grid_col, loc='upper right')

    # Panel 2: Zoom early-time (direct air wave)
    ax2 = fig.add_subplot(gs[1, 0])
    ax2.set_facecolor(panel_bg)
    idx_early = t_ns <= 5.0
    if idx_early.any():
        ax2.plot(t_ns[idx_early], signal[idx_early], color=accent, lw=1.0, marker='o', markersize=3)
    for spine in ax2.spines.values():
        spine.set_edgecolor(grid_col)
    ax2.set_xlabel("Time (ns)", color=text_col, fontsize=8)
    ax2.set_ylabel("Amplitude (A/D counts)", color=text_col, fontsize=8)
    ax2.set_title("Early-time (Direct Pulse)", color=text_col, fontsize=9)
    ax2.tick_params(colors=text_col, labelsize=7)
    ax2.grid(True, color=grid_col, lw=0.4, alpha=0.5)

    # Panel 2b: Mid-time (coda)
    ax2b = fig.add_subplot(gs[1, 2])
    ax2b.set_facecolor(panel_bg)
    idx_mid = (t_ns >= 5.0) & (t_ns <= 25.0)
    if idx_mid.any():
        ax2b.plot(t_ns[idx_mid], signal[idx_mid], color=accent, lw=1.0)
        peaks, _ = find_peaks(np.abs(signal[idx_mid]), height=np.std(signal)*0.5)
        if len(peaks) > 0:
            ax2b.plot(t_ns[idx_mid][peaks], signal[idx_mid][peaks], color=accent2, marker='o', markersize=5, linestyle='none')
    for spine in ax2b.spines.values():
        spine.set_edgecolor(grid_col)
    ax2b.set_xlabel("Time (ns)", color=text_col, fontsize=8)
    ax2b.set_ylabel("Amplitude (A/D counts)", color=text_col, fontsize=8)
    ax2b.set_title("Mid-time (Coda Zone)", color=accent2, fontsize=9, fontweight='bold')
    ax2b.tick_params(colors=text_col, labelsize=7)
    ax2b.grid(True, color=grid_col, lw=0.4, alpha=0.5)

    # Panel 3: Hilbert envelope
    ax3 = fig.add_subplot(gs[1, 1])
    ax3.set_facecolor(panel_bg)
    signal_max = np.max(np.abs(signal))
    if signal_max > 0:
        signal_normalized = signal / signal_max
    else:
        signal_normalized = signal.copy()
    attrs = calculate_instantaneous_attributes(signal_normalized, dt_ns * 1e-9)
    envelope = attrs['envelope']
    ax3.plot(t_ns, signal_normalized, color=accent, lw=0.5, alpha=0.6, label='Signal (normalized)')
    ax3.plot(t_ns, envelope, color=accent2, lw=1.2, label='Envelope (Hilbert)')
    ax3.plot(t_ns, -envelope, color=accent2, lw=0.8, linestyle='--', alpha=0.5)
    for spine in ax3.spines.values():
        spine.set_edgecolor(grid_col)
    ax3.set_xlabel("Time (ns)", color=text_col, fontsize=8)
    ax3.set_ylabel("Amplitude (normalized)", color=text_col, fontsize=8)
    ax3.set_title(f"Hilbert Envelope ({len(signal)} samples)", color=text_col, fontsize=9)
    ax3.tick_params(colors=text_col, labelsize=7)
    ax3.legend(fontsize=7, facecolor=panel_bg, labelcolor=text_col, edgecolor=grid_col, loc='upper right')
    ax3.grid(True, color=grid_col, lw=0.4, alpha=0.5)

    # Panel 4: Frequency spectrum
    ax4 = fig.add_subplot(gs[1, 3])
    ax4.set_facecolor(panel_bg)
    fmax = min(3.0, freq_ghz[-1])
    mask = freq_ghz <= fmax
    ax4.semilogy(freq_ghz[mask], spectrum[mask], color=accent, lw=1.0)
    ax4.fill_between(freq_ghz[mask], spectrum[mask], alpha=0.2, color=accent)
    ax4.axvline(peak_ghz, color=accent2, lw=1.2, ls='--', label=f'{peak_ghz:.2f} GHz')
    for spine in ax4.spines.values():
        spine.set_edgecolor(grid_col)
    ax4.set_xlabel("Frequency (GHz)", color=text_col, fontsize=8)
    ax4.set_ylabel("Magnitude", color=text_col, fontsize=8)
    ax4.set_title("Frequency Spectrum (log)", color=text_col, fontsize=9)
    ax4.tick_params(colors=text_col, labelsize=7)
    ax4.legend(fontsize=7, facecolor=panel_bg, labelcolor=text_col, edgecolor=grid_col)
    ax4.grid(True, color=grid_col, lw=0.4, alpha=0.5, which='both')

    # Panel 5: Spectrogram
    ax5 = fig.add_subplot(gs[2, :3])
    ax5.set_facecolor(panel_bg)
    f, t_spec, Sxx = spectrogram(signal, fs=1/(dt_ns*1e-9), nperseg=128, noverlap=64)
    t_spec_ns = t_spec * 1e9
    f_ghz = f / 1e9
    pcm = ax5.pcolormesh(t_spec_ns, f_ghz, 10*np.log10(Sxx+1e-12), shading='auto', cmap='viridis')
    ax5.set_ylabel("Frequency (GHz)", color=text_col, fontsize=8)
    ax5.set_xlabel("Time (ns)", color=text_col, fontsize=8)
    ax5.set_title("Spectrogram (Time-Frequency)", color=text_col, fontsize=9)
    ax5.tick_params(colors=text_col, labelsize=7)
    ax5.set_ylim([0, 3])
    cbar = plt.colorbar(pcm, ax=ax5, label='Power (dB)')
    cbar.set_label('Power (dB)', color=text_col, fontsize=8)
    cbar.ax.tick_params(colors=text_col, labelsize=7)

    # Panel 6: Statistics
    ax6 = fig.add_subplot(gs[2, 3])
    ax6.set_facecolor(panel_bg)
    ax6.axis("off")
    for spine in ax6.spines.values():
        spine.set_edgecolor(grid_col)

    peaks_all, _ = find_peaks(np.abs(signal), height=np.std(signal)*2)
    n_peaks = len(peaks_all)

    stats_lines = [
        ("SIGNAL METRICS", ""),
        ("Duration", f"{t_ns[-1]:.2f} ns"),
        ("Samples", f"{len(signal):,}"),
        ("Peak amplitude", f"{np.max(signal):.2e}"),
        ("RMS", f"{np.sqrt(np.mean(signal**2)):.2e}"),
        ("Peaks found", f"{n_peaks}"),
        ("─" * 25, ""),
        ("FREQUENCY", ""),
        ("Dom. Freq", f"{peak_ghz:.2f} GHz"),
        ("─" * 25, ""),
        ("FILE INFO", ""),
        ("File", meta['file'][:20]),
        ("Source", meta['source']),
        ("dt", f"{dt_ns:.4f} ns"),
    ]

    y = 0.98
    for key, val in stats_lines:
        if key.startswith("─"):
            y -= 0.035
            continue
        if key.isupper() and val == "":
            ax6.text(0.05, y, key, transform=ax6.transAxes,
                    color=accent2, fontsize=8, fontweight='bold', va="top", fontfamily="monospace")
            y -= 0.055
            continue
        ax6.text(0.05, y, f"{key}", transform=ax6.transAxes,
                color="#80a0c0", fontsize=7.5, va="top", fontfamily="monospace")
        ax6.text(0.95, y, val, transform=ax6.transAxes,
                color=text_col, fontsize=7.5, va="top", fontfamily="monospace", ha="right")
        y -= 0.052

    # Main title with antenna info
    antenna_info = f"{meta.get('antenna_name', 'Unknown')}"
    fig.suptitle(
        f"Numpy A-scan Analysis — {antenna_info}",
        color=text_col, fontsize=12, fontweight='bold', y=0.965,
    )

    out_png = npy_path.with_name(npy_path.stem + "_ascan_analysis.png")
    fig.savefig(out_png, dpi=150, bbox_inches="tight", facecolor=dark_bg)
    plt.close(fig)
    print(f"[OK] Numpy A-scan analysis saved -> {out_png}")

    # Also generate simple view
    out_simple = npy_path.with_name(npy_path.stem + "_ascan_simple.png")
    visualize_simple_wave(signal, t_ns, out_simple,
                         title=f"Extracted Trace — {npy_path.stem}",
                         unit="A/D counts")
    print(f"[OK] Simple waveform view saved -> {out_simple}")

    return out_png


def visualize_dzt_ascan(dzt_path: Path, trace_idx: int = 50) -> Path:
    """Visualize a real DZT A-scan (field data from Puerto-Limache)."""
    dzt_path = dzt_path.resolve()

    # Read DZT trace
    signal, dt_ns, meta = read_dzt_trace(dzt_path, trace_idx)
    t_ns = np.arange(len(signal)) * dt_ns

    # Auto-detect direct wave end using peak-relative gating (SC.CODA_GATE_START_AFTER_PEAK_NS)
    # Direct wave ends ~4.5 ns after the direct pulse peak (one 400MHz Ricker period)
    # This matches the feature extraction pipeline (peak_relative_coda_gate)
    idx_early = t_ns <= 20.0
    if idx_early.any():
        signal_early = signal[idx_early]
        t_early = t_ns[idx_early]

        # Find the direct pulse peak (max amplitude in early window)
        peak_idx = np.argmax(np.abs(signal_early))
        peak_time = t_early[peak_idx]

        # Direct wave ends at: peak_time + CODA_GATE_START_AFTER_PEAK_NS (4.5 ns)
        direct_wave_end = peak_time + SC.CODA_GATE_START_AFTER_PEAK_NS
    else:
        direct_wave_end = 5.0  # fallback

    # Apply time gating to remove direct wave (Wang §2.2)
    # Gate time = peak + CODA_GATE_START_AFTER_PEAK_NS (4.5 ns for 400 MHz)
    signal_gated = remove_direct_wave(signal, dt_ns * 1e-9, method='time_gate', gate_ns=direct_wave_end)

    # Frequency spectrum (computed from gated signal after direct wave)
    idx_after_dw = t_ns >= direct_wave_end
    if idx_after_dw.any():
        signal_spectrum = signal_gated[idx_after_dw]
    else:
        signal_spectrum = signal_gated
    freqs, spectrum, peak_hz = compute_padded_spectrum(signal_spectrum, dt_ns * 1e-9)
    freq_ghz = freqs / 1e9
    peak_ghz = peak_hz / 1e9

    # --- Figure layout: 6-panel (same style as synthetic) ---
    fig = plt.figure(figsize=(18, 10))
    fig.patch.set_facecolor("#0f1117")
    gs = gridspec.GridSpec(3, 4, figure=fig, hspace=0.35, wspace=0.3,
                           left=0.06, right=0.98, top=0.92, bottom=0.08)

    dark_bg   = "#0f1117"
    panel_bg  = "#1a1e2b"
    accent    = "#00d4ff"
    accent2   = "#ff6b35"
    accent3   = "#80e080"
    grid_col  = "#2a2f42"
    text_col  = "#c8d0e0"

    # Panel 1: Full A-scan with direct wave removed (time gating)
    ax1 = fig.add_subplot(gs[0, :])
    ax1.set_facecolor(panel_bg)

    ax1.plot(t_ns, signal_gated, color=accent, lw=0.8, alpha=0.92, label='Signal (direct wave removed)')
    ax1.axhline(0, color=grid_col, lw=0.5)

    # Mark direct air wave region that was removed
    ax1.axvspan(0, direct_wave_end, alpha=0.1, color=accent2, label=f'Removed direct wave (0–{direct_wave_end:.1f} ns)')

    for spine in ax1.spines.values():
        spine.set_edgecolor(grid_col)
    ax1.set_xlabel("Time (ns)", color=text_col, fontsize=9)
    ax1.set_ylabel("Amplitude (A/D counts)", color=text_col, fontsize=9)
    ax1.set_title(f"Real DZT A-scan (Field Data) — Trace {trace_idx}/{meta['total_traces']}  |  Full window {t_ns[-1]:.1f} ns",
                  color=text_col, fontsize=10, fontweight='bold')
    ax1.tick_params(colors=text_col, labelsize=8)
    ax1.grid(True, color=grid_col, lw=0.5, alpha=0.6)
    ax1.legend(fontsize=8, facecolor=panel_bg, labelcolor=text_col, edgecolor=grid_col, loc='upper right')

    # Panel 2: Zoom early-time (direct air wave)
    ax2 = fig.add_subplot(gs[1, 0])
    ax2.set_facecolor(panel_bg)
    idx_early = t_ns <= 5.0
    if idx_early.any():
        ax2.plot(t_ns[idx_early], signal[idx_early], color=accent, lw=1.0, marker='o', markersize=3)
    for spine in ax2.spines.values():
        spine.set_edgecolor(grid_col)
    ax2.set_xlabel("Time (ns)", color=text_col, fontsize=8)
    ax2.set_ylabel("Amplitude (A/D counts)", color=text_col, fontsize=8)
    ax2.set_title("Early-time (Direct Air Wave)", color=text_col, fontsize=9)
    ax2.tick_params(colors=text_col, labelsize=7)
    ax2.grid(True, color=grid_col, lw=0.4, alpha=0.5)

    # Panel 2b: Mid-time (coda/reflections)
    ax2b = fig.add_subplot(gs[1, 2])
    ax2b.set_facecolor(panel_bg)
    idx_mid = (t_ns >= 5.0) & (t_ns <= 25.0)
    if idx_mid.any():
        ax2b.plot(t_ns[idx_mid], signal[idx_mid], color=accent, lw=1.0)
        # Mark peaks
        peaks, _ = find_peaks(np.abs(signal[idx_mid]), height=np.std(signal)*0.5)
        if len(peaks) > 0:
            ax2b.plot(t_ns[idx_mid][peaks], signal[idx_mid][peaks], color=accent2, marker='o', markersize=5, linestyle='none')
    for spine in ax2b.spines.values():
        spine.set_edgecolor(grid_col)
    ax2b.set_xlabel("Time (ns)", color=text_col, fontsize=8)
    ax2b.set_ylabel("Amplitude (A/D counts)", color=text_col, fontsize=8)
    ax2b.set_title("Mid-time (Coda Zone)", color=accent2, fontsize=9, fontweight='bold')
    ax2b.tick_params(colors=text_col, labelsize=7)
    ax2b.grid(True, color=grid_col, lw=0.4, alpha=0.5)

    # Panel 3: Hilbert envelope (using existing signal_processing function)
    ax3 = fig.add_subplot(gs[1, 1])
    ax3.set_facecolor(panel_bg)
    signal_max = np.max(np.abs(signal))
    if signal_max > 0:
        signal_normalized = signal / signal_max
    else:
        signal_normalized = signal.copy()
    # Use existing calculate_instantaneous_attributes function
    attrs = calculate_instantaneous_attributes(signal_normalized, dt_ns * 1e-9)
    envelope = attrs['envelope']
    ax3.plot(t_ns, signal_normalized, color=accent, lw=0.5, alpha=0.6, label='Signal (normalized)')
    ax3.plot(t_ns, envelope, color=accent2, lw=1.2, label='Envelope (Hilbert)')
    ax3.plot(t_ns, -envelope, color=accent2, lw=0.8, linestyle='--', alpha=0.5)
    for spine in ax3.spines.values():
        spine.set_edgecolor(grid_col)
    ax3.set_xlabel("Time (ns)", color=text_col, fontsize=8)
    ax3.set_ylabel("Amplitude (normalized)", color=text_col, fontsize=8)
    ax3.set_title(f"Hilbert Envelope ({len(signal)} samples)", color=text_col, fontsize=9)
    ax3.tick_params(colors=text_col, labelsize=7)
    ax3.legend(fontsize=7, facecolor=panel_bg, labelcolor=text_col, edgecolor=grid_col, loc='upper right')
    ax3.grid(True, color=grid_col, lw=0.4, alpha=0.5)

    # Panel 4: Frequency spectrum
    ax4 = fig.add_subplot(gs[1, 3])
    ax4.set_facecolor(panel_bg)
    fmax = min(3.0, freq_ghz[-1])
    mask = freq_ghz <= fmax
    ax4.semilogy(freq_ghz[mask], spectrum[mask], color=accent, lw=1.0)
    ax4.fill_between(freq_ghz[mask], spectrum[mask], alpha=0.2, color=accent)
    ax4.axvline(peak_ghz, color=accent2, lw=1.2, ls='--', label=f'{peak_ghz:.2f} GHz')
    for spine in ax4.spines.values():
        spine.set_edgecolor(grid_col)
    ax4.set_xlabel("Frequency (GHz)", color=text_col, fontsize=8)
    ax4.set_ylabel("Magnitude", color=text_col, fontsize=8)
    ax4.set_title("Frequency Spectrum (log)", color=text_col, fontsize=9)
    ax4.tick_params(colors=text_col, labelsize=7)
    ax4.legend(fontsize=7, facecolor=panel_bg, labelcolor=text_col, edgecolor=grid_col)
    ax4.grid(True, color=grid_col, lw=0.4, alpha=0.5, which='both')

    # Panel 5: Spectrogram
    ax5 = fig.add_subplot(gs[2, :3])
    ax5.set_facecolor(panel_bg)
    f, t_spec, Sxx = spectrogram(signal, fs=1/(dt_ns*1e-9), nperseg=128, noverlap=64)
    # Convert time to ns and frequency to GHz
    t_spec_ns = t_spec * 1e9
    f_ghz = f / 1e9
    pcm = ax5.pcolormesh(t_spec_ns, f_ghz, 10*np.log10(Sxx+1e-12), shading='auto', cmap='viridis')
    ax5.set_ylabel("Frequency (GHz)", color=text_col, fontsize=8)
    ax5.set_xlabel("Time (ns)", color=text_col, fontsize=8)
    ax5.set_title("Spectrogram (Time-Frequency)", color=text_col, fontsize=9)
    ax5.tick_params(colors=text_col, labelsize=7)
    ax5.set_ylim([0, 3])
    cbar = plt.colorbar(pcm, ax=ax5, label='Power (dB)')
    cbar.set_label('Power (dB)', color=text_col, fontsize=8)
    cbar.ax.tick_params(colors=text_col, labelsize=7)

    # Panel 6: Statistics
    ax6 = fig.add_subplot(gs[2, 3])
    ax6.set_facecolor(panel_bg)
    ax6.axis("off")
    for spine in ax6.spines.values():
        spine.set_edgecolor(grid_col)

    peaks_all, _ = find_peaks(np.abs(signal), height=np.std(signal)*2)
    n_peaks = len(peaks_all)

    stats_lines = [
        ("SIGNAL METRICS", ""),
        ("Duration", f"{t_ns[-1]:.2f} ns"),
        ("Samples", f"{len(signal):,}"),
        ("Peak amplitude", f"{np.max(signal):.2e}"),
        ("RMS", f"{np.sqrt(np.mean(signal**2)):.2e}"),
        ("Peaks found", f"{n_peaks}"),
        ("─" * 25, ""),
        ("FREQUENCY", ""),
        ("Dom. Freq", f"{peak_ghz:.2f} GHz"),
        ("─" * 25, ""),
        ("FILE INFO", ""),
        ("File", meta['file'][:20]),
        ("Trace", f"{trace_idx} / {meta['total_traces']}"),
        ("dt", f"{dt_ns:.4f} ns"),
    ]

    y = 0.98
    for key, val in stats_lines:
        if key.startswith("─"):
            y -= 0.035
            continue
        if key.isupper() and val == "":
            ax6.text(0.05, y, key, transform=ax6.transAxes,
                    color=accent2, fontsize=8, fontweight='bold', va="top", fontfamily="monospace")
            y -= 0.055
            continue
        ax6.text(0.05, y, f"{key}", transform=ax6.transAxes,
                color="#80a0c0", fontsize=7.5, va="top", fontfamily="monospace")
        ax6.text(0.95, y, val, transform=ax6.transAxes,
                color=text_col, fontsize=7.5, va="top", fontfamily="monospace", ha="right")
        y -= 0.052

    # Main title with antenna info
    antenna_info = f"{meta.get('antenna_name', 'Unknown')} ({meta.get('system', 'Unknown')})"
    fig.suptitle(
        f"Real DZT A-scan Analysis — {antenna_info} — Trace {trace_idx}",
        color=text_col, fontsize=12, fontweight='bold', y=0.965,
    )

    out_png = dzt_path.with_name(dzt_path.stem + f"_trace{trace_idx}_ascan_analysis.png")
    fig.savefig(out_png, dpi=150, bbox_inches="tight", facecolor=dark_bg)
    plt.close(fig)
    print(f"[OK] DZT A-scan analysis saved -> {out_png}")

    # Also generate simple view
    out_simple = dzt_path.with_name(dzt_path.stem + f"_trace{trace_idx}_ascan_simple.png")
    visualize_simple_wave(signal, t_ns, out_simple,
                         title=f"Real DZT Trace #{trace_idx} — {dzt_path.stem[:30]}...",
                         unit="A/D counts")
    print(f"[OK] Simple waveform view saved -> {out_simple}")

    return out_png


def visualize_ascan(out_path: Path, component: str = "Ez") -> Path:
    out_path = out_path.resolve()
    in_path  = out_path.with_suffix(".in")

    # --- Read A-scan trace (shared reader; handles B-scan trace selection) ---
    data = read_ascan(out_path, component)
    if data["component"] != component:
        print(f"[!] Component '{component}' not found. Available: {data['available']}")
    component  = data["component"]
    signal     = data["signal"]
    dt         = data["dt"]
    iterations = data["iterations"]
    rx_pos     = data["rx_pos"]
    ascan_idx  = data["ascan_idx"]
    t_ns       = data["t_ns"]    # time axis in nanoseconds

    # --- Frequency spectrum (computed from gated signal, after direct wave) ---
    # Will be computed after gating below

    # --- Metadata from .in ---
    meta = read_header_meta(in_path)
    pvc       = meta.get("pvc", "?")
    fi_class  = meta.get("FI_class", "?")
    lab_class = meta.get("Lab_Class", "?")
    lab_fi    = meta.get("Lab_FI", "?")
    moisture  = meta.get("moisture", "?")
    bal_bot   = float(meta.get("ballast_bottom_y", 0))
    bal_top   = float(meta.get("ballast_top_y",   0))
    bulk_eps  = meta.get("Lab_bulk_eps", "?")
    surface_R = meta.get("Lab_surface_R", "?")
    clean_mm  = meta.get("Lab_clean_ballast_mm", "?")

    # two-way travel time to ballast interfaces (ns)
    c = 3e8
    eps_approx = 3.3   # typical dry ballast
    v = c / np.sqrt(eps_approx)
    tt_top = 2 * bal_top / v * 1e9
    tt_bot = 2 * bal_bot / v * 1e9

    # Extract antenna position and ballast bounds from metadata
    import re
    antenna_y = None
    subsurface_top = None
    ballast_top_y = None

    # Parse "Antenna position" = "y=0.800 m (above surface at 0.550 m)"
    antenna_line = meta.get("Antenna position", None)
    if antenna_line:
        try:
            match = re.search(r'y=([\d.]+)', antenna_line)
            if match:
                antenna_y = float(match.group(1))
        except:
            pass

    # Parse "Subsurface top" = "0.550 m    Total rocks: 216"
    subsurface_line = meta.get("Subsurface top", None)
    if subsurface_line:
        try:
            match = re.search(r'^([\d.]+)', subsurface_line)
            if match:
                subsurface_top = float(match.group(1))
        except:
            pass

    # Parse "Ballast layer" = "y=[0.300, 0.550] m  (packed rocks)"
    ballast_line = meta.get("Ballast layer", None)
    if ballast_line:
        try:
            match = re.search(r'y=\[([\d.]+),\s*([\d.]+)\]', ballast_line)
            if match:
                ballast_bottom_y = float(match.group(1))
                ballast_top_y = float(match.group(2))
        except:
            pass

    # Calculate direct wave arrival time
    if antenna_y and subsurface_top:
        antenna_height_above_surface = antenna_y - subsurface_top
        if antenna_height_above_surface > 0:
            direct_wave_time_ns = 2 * antenna_height_above_surface / c * 1e9
        else:
            direct_wave_time_ns = 1.5  # fallback
    else:
        direct_wave_time_ns = 1.5  # fallback to 1.5 ns

    # Surface reflection arrives at ballast top (use extracted ballast_top_y if available)
    if ballast_top_y:
        v = c / np.sqrt(eps_approx)
        surface_reflection_time_ns = 2 * ballast_top_y / v * 1e9
    else:
        surface_reflection_time_ns = tt_top if bal_top > 0 else 1.5

    # --- Figure layout: 6-panel comprehensive analysis ---
    fig = plt.figure(figsize=(18, 10))
    fig.patch.set_facecolor("#0f1117")
    gs = gridspec.GridSpec(3, 4, figure=fig, hspace=0.35, wspace=0.3,
                           left=0.06, right=0.98, top=0.92, bottom=0.08)

    dark_bg   = "#0f1117"
    panel_bg  = "#1a1e2b"
    accent    = "#00d4ff"
    accent2   = "#ff6b35"
    accent3   = "#80e080"
    grid_col  = "#2a2f42"
    text_col  = "#c8d0e0"

    # Gate signal to start after surface reflection (per Rojas-Vivanco: direct wave + 30 samples = surface)
    idx_after_surface = t_ns >= surface_reflection_time_ns
    signal_gated = signal.copy()
    signal_gated[~idx_after_surface] = 0  # Zero out pre-surface region
    t_ns_gated = t_ns[idx_after_surface]
    signal_gated_trimmed = signal_gated[idx_after_surface]

    # Coda/ballast gate window
    coda_win_ns = SC.CODA_WINDOW_NS  # (6.0, 16.0)

    # Approximate direct wave pulse width
    direct_wave_width = max(0.2, direct_wave_time_ns * 0.3)

    # --- Panel 1: Full A-scan (raw trace incl. direct pulse, top row) ---
    # Shows the whole trace so the coda callout below magnifies the small
    # subsurface coda out of the dominant direct pulse. Direct-wave-gated
    # detail lives in panels 2/2b/3.
    ax1 = fig.add_subplot(gs[0, :])
    ax1.set_facecolor(panel_bg)
    ax1.plot(t_ns, signal, color=accent, lw=0.8, alpha=0.92)
    ax1.axhline(0, color=grid_col, lw=0.5)

    # Annotate physical features (relative to gated time axis)
    ax1.axvline(surface_reflection_time_ns, color=accent2, lw=2.0, linestyle='--', alpha=0.8, label=f'Surface reflection ({surface_reflection_time_ns:.2f}ns)')
    ax1.axvline(coda_win_ns[0], color='#ffd700', lw=1.5, linestyle=':', alpha=0.6, label=f'Ballast gate ({coda_win_ns[0]:.1f}-{coda_win_ns[1]:.1f}ns)')
    ax1.axvline(coda_win_ns[1], color='#ffd700', lw=1.5, linestyle=':', alpha=0.6)
    ax1.text(surface_reflection_time_ns+0.2, ax1.get_ylim()[1]*0.85, 'Surface', color=accent2, fontsize=8, fontweight='bold')
    ax1.text((coda_win_ns[0]+coda_win_ns[1])/2, ax1.get_ylim()[1]*0.75, 'Ballast\nGate', color='#ffd700', fontsize=7, fontweight='bold', ha='center')

    for spine in ax1.spines.values():
        spine.set_edgecolor(grid_col)
    ax1.set_xlabel("Time (ns)", color=text_col, fontsize=9)
    ax1.set_ylabel(f"{component} (V/m)", color=text_col, fontsize=9)
    ax1.set_title(f"Full A-scan with coda callout — {component}  [Surface reflection {surface_reflection_time_ns:.2f}ns | Ballast gate {coda_win_ns[0]:.1f}-{coda_win_ns[1]:.1f}ns]",
                  color=text_col, fontsize=10, fontweight='bold')
    ax1.tick_params(colors=text_col, labelsize=8)
    ax1.grid(True, color=grid_col, lw=0.5, alpha=0.6)
    ax1.legend(fontsize=8, facecolor=panel_bg, labelcolor=text_col, edgecolor=grid_col, loc='upper right')

    # --- Coda callout: a box outlines the ballast/coda window on the full
    # A-scan and connector lines link it to a magnified inset. The fouling
    # signature is a small modulation deep in the coda, invisible at full scale.
    idx_coda1 = (t_ns >= coda_win_ns[0]) & (t_ns <= coda_win_ns[1])
    if idx_coda1.any():
        coda_amp = float(np.max(np.abs(signal[idx_coda1]))) or 1.0
        full_amp = float(np.max(np.abs(signal))) or coda_amp
        axins = ax1.inset_axes([0.60, 0.10, 0.37, 0.52], facecolor=panel_bg)
        axins.plot(t_ns, signal, color=accent, lw=1.1)
        axins.axhline(0, color=grid_col, lw=0.5)
        axins.set_xlim(coda_win_ns[0], coda_win_ns[1])
        axins.set_ylim(-1.3 * coda_amp, 1.3 * coda_amp)
        axins.set_title(f"CODA magnified ~{full_amp / coda_amp:.0f}x", color='#ffd700', fontsize=8)
        axins.tick_params(colors=text_col, labelsize=6)
        for sp in axins.spines.values():
            sp.set_edgecolor('#ffd700')
        ax1.indicate_inset_zoom(axins, edgecolor='#ffd700', lw=1.3, alpha=0.7)

    # --- Panel 2: Zoom on surface-to-ballast gate transition (post-DW) ---
    ax2 = fig.add_subplot(gs[1, 0])
    ax2.set_facecolor(panel_bg)
    # Show region from surface reflection to mid-ballast gate
    idx_zoom = (t_ns_gated >= surface_reflection_time_ns) & (t_ns_gated <= (coda_win_ns[0] + coda_win_ns[1])/2)
    if idx_zoom.any():
        ax2.plot(t_ns_gated[idx_zoom], signal_gated_trimmed[idx_zoom], color=accent, lw=1.0)

    # Mark surface reflection and ballast gate regions
    ax2.axvline(surface_reflection_time_ns, color=accent2, lw=1.5, linestyle='--', alpha=0.7)
    ax2.axvline(coda_win_ns[0], color='#ffd700', lw=1.5, linestyle=':', alpha=0.6)
    ax2.text(surface_reflection_time_ns+0.05, ax2.get_ylim()[1]*0.8, 'Surface', color=accent2, fontsize=7, fontweight='bold')
    ax2.text(coda_win_ns[0]+0.1, ax2.get_ylim()[1]*0.6, 'Ballast\ngate', color='#ffd700', fontsize=7, fontweight='bold')

    # Mark peaks in this window
    if idx_zoom.any():
        peaks, props = find_peaks(np.abs(signal_gated_trimmed[idx_zoom]), height=np.std(signal_gated_trimmed)*1.5)
        if len(peaks) > 0:
            peak_times = t_ns_gated[idx_zoom][peaks]
            peak_vals = signal_gated_trimmed[idx_zoom][peaks]
            ax2.plot(peak_times, peak_vals, color=accent2, marker='*', markersize=10, linestyle='none')
    for spine in ax2.spines.values():
        spine.set_edgecolor(grid_col)
    ax2.set_xlabel("Time (ns)", color=text_col, fontsize=8)
    ax2.set_ylabel(f"{component} (V/m)", color=text_col, fontsize=8)
    ax2.set_title(f"Transition Zone ({surface_reflection_time_ns:.2f}-{coda_win_ns[0]:.1f} ns)", color=text_col, fontsize=9)
    ax2.tick_params(colors=text_col, labelsize=7)
    ax2.grid(True, color=grid_col, lw=0.4, alpha=0.5)

    # --- Panel 2b: Ballast/Coda Window (6-16 ns, fouling-sensitive) ---
    ax2b = fig.add_subplot(gs[1, 2])
    ax2b.set_facecolor(panel_bg)
    idx_coda = (t_ns >= coda_win_ns[0]) & (t_ns <= coda_win_ns[1])
    if idx_coda.any():
        ax2b.plot(t_ns[idx_coda], signal[idx_coda], color=accent, lw=1.5)
        # Mark peaks in coda window
        peaks_coda, _ = find_peaks(np.abs(signal[idx_coda]), height=np.std(signal)*1.5)
        if len(peaks_coda) > 0:
            peak_times_coda = t_ns[idx_coda][peaks_coda]
            peak_vals_coda = signal[idx_coda][peaks_coda]
            ax2b.plot(peak_times_coda, peak_vals_coda, color=accent2, marker='o', markersize=6, linestyle='none')
    for spine in ax2b.spines.values():
        spine.set_edgecolor(grid_col)
    ax2b.set_xlabel("Time (ns)", color=text_col, fontsize=8)
    ax2b.set_ylabel(f"{component} (V/m)", color=text_col, fontsize=8)
    ax2b.set_title(f"Ballast/Coda Gate ({coda_win_ns[0]:.1f}-{coda_win_ns[1]:.1f} ns)", color=accent2, fontsize=9, fontweight='bold')
    ax2b.tick_params(colors=text_col, labelsize=7)
    ax2b.grid(True, color=grid_col, lw=0.4, alpha=0.5)

    # --- Frequency spectrum (computed from gated signal, after direct wave) ---
    freqs, spectrum, peak_hz = compute_padded_spectrum(signal_gated_trimmed, dt)
    freq_ghz = freqs / 1e9
    peak_ghz = peak_hz / 1e9

    # --- Panel 3: Hilbert envelope (Rojas-Vivanco methodology) ---
    ax3 = fig.add_subplot(gs[1, 1])
    ax3.set_facecolor(panel_bg)
    # Per Rojas-Vivanco: normalize post-DW signal to max value THEN compute Hilbert
    signal_max = np.max(np.abs(signal_gated_trimmed))
    if signal_max > 0:
        signal_normalized = signal_gated_trimmed / signal_max  # Normalize to [0, 1]
    else:
        signal_normalized = signal_gated_trimmed.copy()
    # Compute Hilbert transform on CLEAN, NORMALIZED, post-DW-only signal
    analytic = hilbert(signal_normalized)
    envelope = np.abs(analytic)
    # Plot normalized signal with envelope
    ax3.plot(t_ns_gated, signal_normalized, color=accent, lw=0.5, alpha=0.6, label='Signal (normalized)')
    ax3.plot(t_ns_gated, envelope, color=accent2, lw=1.2, label='Envelope (Hilbert)')
    ax3.plot(t_ns_gated, -envelope, color=accent2, lw=0.8, linestyle='--', alpha=0.5)
    for spine in ax3.spines.values():
        spine.set_edgecolor(grid_col)
    ax3.set_xlabel(f"Time (ns, from {direct_wave_time_ns:.2f}ns)", color=text_col, fontsize=8)
    ax3.set_ylabel("Amplitude (V/m)", color=text_col, fontsize=8)
    ax3.set_title(f"Hilbert Envelope (post-DW only, {len(signal_gated_trimmed)} samples)", color=text_col, fontsize=9)
    # Set x-axis limits to match actual data (post-DW only)
    if len(t_ns_gated) > 0:
        ax3.set_xlim(t_ns_gated[0], t_ns_gated[-1])
    ax3.tick_params(colors=text_col, labelsize=7)
    ax3.legend(fontsize=7, facecolor=panel_bg, labelcolor=text_col, edgecolor=grid_col, loc='upper right')
    ax3.grid(True, color=grid_col, lw=0.4, alpha=0.5)

    # --- Panel 4: Frequency spectrum (log scale) ---
    ax4 = fig.add_subplot(gs[1, 3])
    ax4.set_facecolor(panel_bg)
    fmax = min(3.0, freq_ghz[-1])
    mask = freq_ghz <= fmax
    ax4.semilogy(freq_ghz[mask], spectrum[mask], color=accent, lw=1.0)
    ax4.fill_between(freq_ghz[mask], spectrum[mask], alpha=0.2, color=accent)
    ax4.axvline(peak_ghz, color=accent2, lw=1.2, ls='--', label=f'{peak_ghz:.2f} GHz')
    for spine in ax4.spines.values():
        spine.set_edgecolor(grid_col)
    ax4.set_xlabel("Frequency (GHz)", color=text_col, fontsize=8)
    ax4.set_ylabel("Magnitude", color=text_col, fontsize=8)
    ax4.set_title("Frequency Spectrum (log)", color=text_col, fontsize=9)
    ax4.tick_params(colors=text_col, labelsize=7)
    ax4.legend(fontsize=7, facecolor=panel_bg, labelcolor=text_col, edgecolor=grid_col)
    ax4.grid(True, color=grid_col, lw=0.4, alpha=0.5, which='both')

    # --- Panel 5: Spectrogram (from gated signal, after direct wave) ---
    ax5 = fig.add_subplot(gs[2, :3])
    ax5.set_facecolor(panel_bg)
    f, t_spec, Sxx = spectrogram(signal_gated_trimmed, fs=1/dt, nperseg=512, noverlap=256)
    t_spec = t_spec + direct_wave_time_ns  # Shift time axis to match gated window
    pcm = ax5.pcolormesh(t_spec*1e9, f/1e9, 10*np.log10(Sxx+1e-12), shading='auto', cmap='viridis')
    ax5.set_ylabel("Frequency (GHz)", color=text_col, fontsize=8)
    ax5.set_xlabel("Time (ns)", color=text_col, fontsize=8)
    ax5.set_title("Spectrogram (Time-Frequency)", color=text_col, fontsize=9)
    ax5.tick_params(colors=text_col, labelsize=7)
    ax5.set_ylim([0, 3])
    cbar = plt.colorbar(pcm, ax=ax5, label='Power (dB)')
    cbar.set_label('Power (dB)', color=text_col, fontsize=8)
    cbar.ax.tick_params(colors=text_col, labelsize=7)

    # --- Panel 6: Statistics & Metadata ---
    ax6 = fig.add_subplot(gs[2, 3])
    ax6.set_facecolor(panel_bg)
    ax6.axis("off")
    for spine in ax6.spines.values():
        spine.set_edgecolor(grid_col)

    # Build statistics text (from gated signal, after direct wave)
    rms = np.sqrt(np.mean(signal_gated_trimmed**2))
    peaks_gated, _ = find_peaks(np.abs(signal_gated_trimmed), height=np.std(signal_gated_trimmed)*2)
    n_peaks = len(peaks_gated)

    if rx_pos[0] is not None and rx_pos[1] is not None:
        rx_str = f"({rx_pos[0]:.3f}, {rx_pos[1]:.3f}) m"
    else:
        rx_str = "n/a"

    stats_lines = [
        ("TIMING (computed)", ""),
        ("Direct wave", f"0.0-{direct_wave_time_ns:.2f} ns"),
        ("Surface hit", f"~{surface_reflection_time_ns:.2f} ns"),
        ("Ballast gate", f"{coda_win_ns[0]:.1f}-{coda_win_ns[1]:.1f} ns"),
        ("─" * 25, ""),
        ("SIGNAL METRICS (post-DW)", ""),
        ("Duration", f"{t_ns_gated[-1]:.2f} ns"),
        ("Samples", f"{len(signal_gated_trimmed):,}"),
        ("Peak", f"{np.max(signal_gated_trimmed):.0f} V/m"),
        ("RMS", f"{rms:.0f} V/m"),
        ("Peaks found", f"{n_peaks}"),
        ("─" * 25, ""),
        ("FREQUENCY", ""),
        ("Dom. Freq", f"{peak_ghz:.2f} GHz"),
        ("BW est.", "~1-2 GHz"),
        ("─" * 25, ""),
        ("METADATA", ""),
        ("File", out_path.stem[:15]),
        ("PVC", f"{pvc}%"),
        ("Lab FI", f"{lab_fi}% [{lab_class}]"),
    ]

    y = 0.98
    for key, val in stats_lines:
        if key.startswith("SIGNAL") or key.startswith("─"):
            if key.startswith("SIGNAL"):
                ax6.text(0.05, y, key, transform=ax6.transAxes,
                        color=accent2, fontsize=8, fontweight='bold', va="top", fontfamily="monospace")
            y -= 0.05
            continue
        ax6.text(0.05, y, f"{key}", transform=ax6.transAxes,
                color="#80a0c0", fontsize=7.5, va="top", fontfamily="monospace")
        ax6.text(0.65, y, val, transform=ax6.transAxes,
                color=text_col, fontsize=7.5, va="top", fontfamily="monospace", ha="right")
        y -= 0.052

    # --- Main title ---
    fig.suptitle(
        f"gprMax A-scan — Comprehensive Analysis  |  {out_path.stem}  |  PVC={pvc}%  FI={lab_fi}% [{lab_class}]",
        color=text_col, fontsize=12, fontweight='bold', y=0.965,
    )

    out_png = out_path.with_name(out_path.stem + "_ascan_analysis.png")
    fig.savefig(out_png, dpi=150, bbox_inches="tight", facecolor=dark_bg)
    plt.close(fig)
    print(f"[OK] Comprehensive A-scan analysis saved -> {out_png}")

    # Also generate simple view
    out_simple = out_path.with_name(out_path.stem + "_ascan_simple.png")
    visualize_simple_wave(signal, t_ns, out_simple,
                         title=f"Synthetic A-scan — {out_path.stem}  |  {component}",
                         unit="V/m")
    print(f"[OK] Simple waveform view saved -> {out_simple}")

    return out_png


def main():
    ap = argparse.ArgumentParser(description="Visualize A-scans (synthetic .out, real DZT, or numpy-extracted)")
    ap.add_argument("ascan_file", type=Path, help="Path to .out (synthetic), .DZT/.dzt (real), or .npy (extracted) file")
    ap.add_argument("--component", default="Ez",
                    help="Field component to plot (synthetic only; default: Ez)")
    ap.add_argument("--trace", type=int, default=50,
                    help="Trace index for DZT files (default: 50)")
    args = ap.parse_args()

    file_path = args.ascan_file.resolve()

    # Auto-detect file type
    suffix = file_path.suffix.upper()

    if suffix == ".OUT":
        print(f"[AUTO] Detected synthetic gprMax .out file")
        visualize_ascan(file_path, component=args.component)
    elif suffix == ".DZT" or suffix == ".DTZ":
        print(f"[AUTO] Detected real field DZT file")
        visualize_dzt_ascan(file_path, trace_idx=args.trace)
    elif suffix == ".NPY":
        print(f"[AUTO] Detected numpy-extracted A-scan file")
        visualize_npy_ascan(file_path)
    else:
        print(f"[ERR] Unsupported file type: {file_path.suffix}")
        print(f"      Supported: .out (synthetic), .DZT/.dzt (real), .npy (extracted)")
        sys.exit(1)


if __name__ == "__main__":
    main()

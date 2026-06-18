#!/usr/bin/env python3
"""Visualize a single DZT trace from Puerto-Limache dataset."""

import sys
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.signal_processing import calculate_instantaneous_attributes, remove_direct_wave

# Load the trace
trace_file = Path('output_test/dzt_trace_1000.npy')
signal = np.load(trace_file).astype(np.float64)

# DZT parameters (from memory)
dt = 50 / 511e9  # ~0.0978 ns
time_axis = np.arange(len(signal)) * dt * 1e9  # ns

# Drop indices 0-1 (DZT artifacts)
signal_clean = signal[2:]
time_axis_clean = time_axis[2:]

# Calculate signal attributes
attrs = calculate_instantaneous_attributes(signal_clean, dt)
envelope = attrs['envelope']
inst_freq = attrs['frequency']  # Instantaneous frequency in Hz

# Direct wave end (from SC.CODA_GATE_START_AFTER_PEAK_NS)
peak_idx = np.argmax(np.abs(signal_clean))
dw_end_time = time_axis_clean[peak_idx] + 4.5  # 4.5 ns after peak

# Remove direct wave for coda analysis
gate_ns = dw_end_time + 2.0  # Add 2ns after peak for safety
signal_gated = remove_direct_wave(signal_clean, dt, method='time_gate', gate_ns=gate_ns)

# Time-frequency analysis (STFT)
from scipy.signal import spectrogram
f, t_stft, Sxx = spectrogram(signal_clean, fs=1/dt, nperseg=64, noverlap=32)
f_mhz = f / 1e6

# Frequency spectrum
from scipy.fft import fft, fftfreq
sig_detrended = signal_clean - np.mean(signal_clean)
fft_vals = np.abs(fft(sig_detrended))
fft_freq = fftfreq(len(sig_detrended), dt)
fft_pos_mask = fft_freq > 0
fft_freq_pos = fft_freq[fft_pos_mask] / 1e6  # MHz
fft_mag_pos = fft_vals[fft_pos_mask] / len(sig_detrended)

# Create comprehensive 6-panel visualization
fig = plt.figure(figsize=(16, 12))
fig.suptitle(f'Real GPR A-scan - Puerto-Limache DZT Trace #1000', fontsize=14, fontweight='bold')

# Panel 1: Raw waveform with direct wave removal
ax1 = plt.subplot(2, 3, 1)
ax1.plot(time_axis_clean, signal_clean, 'b-', linewidth=1, label='Raw signal')
ax1.axvline(dw_end_time, color='r', linestyle='--', linewidth=2, label=f'DW end ({dw_end_time:.2f} ns)')
ax1.set_xlabel('Time (ns)')
ax1.set_ylabel('Amplitude (A/D counts)')
ax1.set_title('Raw Waveform + Direct Wave Gate')
ax1.legend()
ax1.grid(True, alpha=0.3)

# Panel 2: Hilbert envelope
ax2 = plt.subplot(2, 3, 2)
ax2.plot(time_axis_clean, signal_clean, 'b-', linewidth=0.5, alpha=0.6, label='Signal')
ax2.plot(time_axis_clean, envelope, 'r-', linewidth=2, label='Hilbert envelope')
ax2.set_xlabel('Time (ns)')
ax2.set_ylabel('Amplitude (A/D counts)')
ax2.set_title('Instantaneous Envelope')
ax2.legend()
ax2.grid(True, alpha=0.3)

# Panel 3: Instantaneous frequency
ax3 = plt.subplot(2, 3, 3)
inst_freq_valid = inst_freq[~np.isnan(inst_freq) & ~np.isinf(inst_freq)] / 1e6  # MHz
if len(inst_freq_valid) > 0:
    ax3.plot(time_axis_clean[:len(inst_freq_valid)], inst_freq_valid, 'g-', linewidth=1)
    ax3.set_ylabel('Frequency (MHz)')
else:
    ax3.text(0.5, 0.5, 'Inst. freq: NaN', ha='center', va='center', transform=ax3.transAxes)
ax3.set_xlabel('Time (ns)')
ax3.set_title('Instantaneous Frequency')
ax3.grid(True, alpha=0.3)

# Panel 4: Gated signal (coda only)
ax4 = plt.subplot(2, 3, 4)
ax4.plot(time_axis_clean, signal_gated, 'c-', linewidth=1, label='Gated signal (coda)')
ax4.set_xlabel('Time (ns)')
ax4.set_ylabel('Amplitude (A/D counts)')
ax4.set_title(f'Direct Wave Removed (gate>{dw_end_time:.2f}ns)')
ax4.legend()
ax4.grid(True, alpha=0.3)

# Panel 5: Frequency spectrum
ax5 = plt.subplot(2, 3, 5)
ax5.semilogy(fft_freq_pos, fft_mag_pos, 'b-', linewidth=1)
ax5.set_xlabel('Frequency (MHz)')
ax5.set_ylabel('Magnitude')
ax5.set_title('Frequency Spectrum')
ax5.set_xlim([0, 1000])
ax5.grid(True, alpha=0.3, which='both')

# Panel 6: STFT spectrogram
ax6 = plt.subplot(2, 3, 6)
im = ax6.pcolormesh(t_stft * 1e9, f_mhz, 10 * np.log10(Sxx + 1e-12), shading='auto', cmap='viridis')
ax6.set_xlabel('Time (ns)')
ax6.set_ylabel('Frequency (MHz)')
ax6.set_ylim([0, 600])
ax6.set_title('Time-Frequency (STFT)')
cbar = plt.colorbar(im, ax=ax6)
cbar.set_label('Power (dB)')

plt.tight_layout()
output_file = Path('output_test/dzt_trace_1000_analysis.png')
plt.savefig(output_file, dpi=150, bbox_inches='tight')
print(f'[OK] Saved visualization: {output_file}')

# Print statistics
print(f'\n{"="*70}')
print(f'DZT TRACE STATISTICS (Trace #1000)')
print(f'{"="*70}')
print(f'Peak amplitude: {np.max(np.abs(signal_clean)):.4e} A/D counts')
print(f'Peak time: {time_axis_clean[peak_idx]:.4f} ns')
print(f'Mean amplitude: {np.mean(np.abs(signal_clean)):.4e}')
print(f'RMS amplitude: {np.sqrt(np.mean(signal_clean**2)):.4e}')
print(f'Envelope peak: {np.max(envelope):.4e}')
print(f'Direct wave end (4.5ns after peak): {dw_end_time:.4f} ns')
print(f'Coda samples (after DW gate): {np.sum(time_axis_clean > dw_end_time)}')
print(f'Sampling rate: {1/dt:.2e} Hz ({1/dt/1e9:.2f} GHz)')
print(f'Time window: {time_axis_clean[-1]:.2f} ns')

plt.close()

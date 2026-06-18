#!/usr/bin/env python3
"""Waveform scaling with direct binary DZT reading (GSSI format)."""

import sys
from pathlib import Path
import struct
import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data_loader import read_ascan

print('='*70)
print('WAVEFORM SCALING: Synthetic vs Real')
print('='*70)

# Read synthetic free space .out file
print('\n[1] SYNTHETIC (Free Space 400 MHz)')
syn_data = read_ascan('output_test/freespace_400mhz.out', 'Ez')
syn_signal = syn_data['signal']
syn_dt = syn_data['dt']

# Find peak amplitude
syn_peak_idx = np.argmax(np.abs(syn_signal))
syn_peak_amp = syn_signal[syn_peak_idx]
syn_peak_time = syn_peak_idx * syn_dt * 1e9

print(f'  Peak amplitude: {syn_peak_amp:.4e} V/m')
print(f'  Peak time: {syn_peak_time:.4f} ns')
print(f'  Total samples: {len(syn_signal)}')

# Direct binary read DZT (GSSI Puerto-Limache format)
print('\n[2] REAL (Puerto-Limache DZT - direct binary)')
dzt_files = sorted(Path('D:/Codigo/Data').glob('*.DZT'))
if dzt_files:
    dzt_file = dzt_files[0]
    print(f'  File: {dzt_file.name}')

    file_size = dzt_file.stat().st_size
    print(f'  File size: {file_size} bytes')

    # GSSI DZT format (from memory):
    # Header: 128 KiB (131,072 bytes)
    # Data: int32 samples, 512 samples per trace
    # Total traces: (file_size - 131072) / (512 * 4) = (file_size - 131072) / 2048

    HEADER_SIZE = 128 * 1024  # 131,072 bytes
    SAMPLES_PER_TRACE = 512
    BYTES_PER_SAMPLE = 4  # int32

    data_size = file_size - HEADER_SIZE
    num_traces = data_size // (SAMPLES_PER_TRACE * BYTES_PER_SAMPLE)

    print(f'  Header size: {HEADER_SIZE} bytes')
    print(f'  Samples per trace: {SAMPLES_PER_TRACE}')
    print(f'  Bytes per sample: {BYTES_PER_SAMPLE}')
    print(f'  Calculated traces: {num_traces}')

    # Read header to verify
    with open(dzt_file, 'rb') as f:
        header_data = f.read(HEADER_SIZE)

        # Extract antenna info from header (if available at known offsets)
        # For now, just proceed to trace reading

        # Seek to trace 1000 and read it
        trace_idx = min(1000, num_traces - 1)
        byte_offset = HEADER_SIZE + (trace_idx * SAMPLES_PER_TRACE * BYTES_PER_SAMPLE)

        print(f'  Reading trace #{trace_idx}...')
        f.seek(byte_offset)

        # Read one trace (SAMPLES_PER_TRACE int32 samples)
        trace_bytes = f.read(SAMPLES_PER_TRACE * BYTES_PER_SAMPLE)
        real_trace = np.frombuffer(trace_bytes, dtype=np.int32, count=SAMPLES_PER_TRACE)
        real_trace = real_trace.astype(np.float64)

        print(f'  Raw samples read: {len(real_trace)}')

    # Drop indices 0-1 as per memory
    real_trace_clean = real_trace[2:]

    # Find peak
    real_peak_idx = np.argmax(np.abs(real_trace_clean))
    real_peak_amp = real_trace_clean[real_peak_idx]

    print(f'  Peak amplitude (cleaned): {real_peak_amp:.4e} A/D counts')
    print(f'  Peak index (after drop 0-1): {real_peak_idx}')
    print(f'  Samples (after cleaning): {len(real_trace_clean)}')

    # Calculate scale factor
    scale_factor = real_peak_amp / syn_peak_amp
    print('\n' + '='*70)
    print('SCALE FACTOR')
    print('='*70)
    print(f'  Synthetic peak: {syn_peak_amp:.4e} V/m')
    print(f'  Real peak:      {real_peak_amp:.4e} A/D counts')
    print(f'  scale_factor = {scale_factor:.6e}')
    print(f'  scale_factor magnitude = {abs(scale_factor):.6f}')

    print('\n' + '='*70)
    print('APPLICATION')
    print('='*70)
    print(f'  To scale all synthetic waveforms:')
    print(f'    scale_factor = {abs(scale_factor):.6e}')
    print(f'    traces_scaled = np.abs(traces_synthetic) * {abs(scale_factor):.6e}')

else:
    print('  ERROR: No DZT files found in D:/Codigo/Data')

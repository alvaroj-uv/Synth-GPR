#!/usr/bin/env python3
"""Fast waveform scaling: extract peak from synthetic .out and one DZT trace."""

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

# Fast DZT read: one trace only
print('\n[2] REAL (Puerto-Limache DZT - one trace)')
dzt_files = sorted(Path('D:/Codigo/Data').glob('*.DZT'))
if dzt_files:
    dzt_file = dzt_files[0]
    print(f'  File: {dzt_file.name}')

    with open(dzt_file, 'rb') as f:
        # GSSI DZT format: 1024-byte header + int16 samples
        header = f.read(1024)

        # Per dzt_io.py: correct offsets for GSSI header
        rh_nsamp = struct.unpack('<H', header[8:10])[0]  # offset 8: samples per A-scan

        # If rh_nsamp is wrong (=1), try standard 512
        if rh_nsamp < 10:
            print(f'  [WARN] Header says {rh_nsamp} samples, using standard 512')
            rh_nsamp = 512

        # Get file size to calculate traces
        file_size = dzt_file.stat().st_size
        data_size = file_size - 1024  # Subtract 1KiB header
        ntraces = data_size // (rh_nsamp * 2)  # int16 = 2 bytes

        print(f'  Samples per trace: {rh_nsamp}')
        print(f'  Total traces: {ntraces}')

        # Seek to trace 1000 and read it
        trace_idx = min(1000, ntraces - 1)
        byte_offset = 1024 + (trace_idx * rh_nsamp * 2)
        f.seek(byte_offset)

        # Read one trace (rh_nsamp int16 samples)
        trace_bytes = f.read(rh_nsamp * 2)
        real_trace = np.frombuffer(trace_bytes, dtype=np.int16, count=rh_nsamp)

        # Drop indices 0-1 as per memory
        real_trace_clean = real_trace[2:].astype(np.float64)

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
        print(f'  scale_factor = real_peak / synthetic_peak')
        print(f'  {real_peak_amp:.4e} / {syn_peak_amp:.4e}')
        print(f'  scale_factor = {scale_factor:.6e}')
        print(f'  scale_factor ~= {abs(scale_factor):.2f} (magnitude)')

        print('\n' + '='*70)
        print('USAGE')
        print('='*70)
        print(f'  Apply to synthetic dataset:')
        print(f'    traces_synthetic_scaled = np.abs(traces_synthetic) * {abs(scale_factor):.6e}')
else:
    print('  ERROR: No DZT files found in D:/Codigo/Data')

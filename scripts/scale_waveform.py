#!/usr/bin/env python3
"""Extract peak amplitudes from synthetic and real data, compute scaling factor."""

import sys
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data_loader import read_ascan
from src.dzt_io import read_dzt_traces

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
print(f'  Sample rate: {1/syn_dt:.2e} Hz')
print(f'  Total samples: {len(syn_signal)}')

# Read ONE trace from real Puerto-Limache DZT
print('\n[2] REAL (Puerto-Limache DZT - one trace)')
dzt_files = sorted(Path('D:/Codigo/Data').glob('*.DZT'))
if dzt_files:
    dzt_file = dzt_files[0]
    print(f'  File: {dzt_file.name}')

    # Read just 1 trace, starting from middle of file
    traces, metadata = read_dzt_traces(dzt_file, start_trace=1000, num_traces=1)
    real_trace = traces[0]

    antenna = metadata.get('antenna_name', '?')
    print(f'  Antenna: {antenna}')
    print(f'  Samples per trace: {len(real_trace)}')

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
    print(f'  scale_factor = real_peak / synthetic_peak')
    print(f'  scale_factor = {real_peak_amp:.4e} / {syn_peak_amp:.4e}')
    print(f'  scale_factor = {scale_factor:.6e}')
    print(f'  scale_factor ≈ {scale_factor:.2f}')

    # Show application
    print('\n' + '='*70)
    print('APPLICATION')
    print('='*70)
    print(f'  To scale synthetic waveforms:')
    print(f'    traces_synthetic_scaled = traces_synthetic * {scale_factor:.6e}')
    print(f'  ')
    print(f'  This converts V/m → A/D counts for matching real hardware amplitude')
else:
    print('  ERROR: No DZT files found in D:/Codigo/Data')

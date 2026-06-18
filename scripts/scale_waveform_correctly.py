#!/usr/bin/env python3
"""Waveform scaling with correct GSSI DZT reading via readgssi."""

import sys
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data_loader import read_ascan
from src.dzt_io import get_dzt_metadata, read_dzt_traces

print('='*70)
print('WAVEFORM SCALING: Synthetic vs Real (GSSI Correct)')
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

# Read DZT via readgssi (correct GSSI handling)
print('\n[2] REAL (Puerto-Limache DZT - via readgssi)')
dzt_files = sorted(Path('D:/Codigo/Data').glob('*.DZT'))
if dzt_files:
    dzt_file = dzt_files[0]
    print(f'  File: {dzt_file.name}')

    # Get metadata via readgssi
    try:
        metadata = get_dzt_metadata(dzt_file)
        print(f'  Antenna: {metadata.get("antenna_name", "?")}')
        print(f'  Frequency: {metadata.get("antenna_freq", "?")/1e6:.0f} MHz')
        print(f'  Samples per trace: {metadata.get("samples_per_trace", "?")}')
        print(f'  Total traces: {metadata.get("num_traces", "?")}')
        print(f'  Bits per sample: {metadata.get("bits_per_sample", "?")}')
        print(f'  Sampling rate: {metadata.get("sampling_rate", "?")/1e9:.2f} GHz')

        # Read one trace via readgssi
        traces, _ = read_dzt_traces(dzt_file, start_trace=1000, num_traces=1)
        real_trace = traces[0]

        print(f'  Trace length (raw): {len(real_trace)}')

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
        print(f'  {real_peak_amp:.4e} / {syn_peak_amp:.4e}')
        print(f'  scale_factor = {scale_factor:.6e}')
        print(f'  scale_factor magnitude = {abs(scale_factor):.6f}')

        print('\n' + '='*70)
        print('USAGE')
        print('='*70)
        print(f'  Apply to synthetic dataset:')
        print(f'    traces_synthetic_scaled = np.abs(traces_synthetic) * {abs(scale_factor):.6e}')
    except Exception as e:
        print(f'  ERROR reading DZT: {e}')
        import traceback
        traceback.print_exc()
else:
    print('  ERROR: No DZT files found in D:/Codigo/Data')

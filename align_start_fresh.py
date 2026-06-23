#!/usr/bin/env python3
"""
Align start_fresh.out with real data by iterating time shifts.
"""

import numpy as np
import h5py
from scipy.interpolate import interp1d

# Read synthetic
with h5py.File("start_fresh.out", 'r') as f:
    syn_sig = f['rxs/rx1/Ez'][()]
    syn_dt = f.attrs.get('dt', 0.0) * 1e9

# Read real DZT
HEADER_SIZE = 128 * 1024
with open("D:/Codigo/Data/PUERTO-LIMACHE_20230726_EFE_V1_PKC000_588_PKF011_020_CENTRO_BRUTO.DZT", 'rb') as f:
    f.seek(HEADER_SIZE + 15000 * 512 * 4)
    real_sig = np.frombuffer(f.read(512 * 4), dtype=np.int32)[2:].astype(float)

real_dt = 50 / 511

# Flip polarity
syn_sig = -syn_sig

# Time arrays
syn_t = np.arange(len(syn_sig)) * syn_dt
real_t = np.arange(len(real_sig)) * real_dt

print("\n" + "="*70)
print("Time-Shift Alignment: start_fresh.out vs Real DZT")
print("="*70 + "\n")

results = []

for shift_ns in np.arange(0, 7, 0.5):
    # Shift synthetic time array
    syn_t_shifted = syn_t + shift_ns

    # Interpolate to common grid
    common_dt = real_dt
    t_max = min(syn_t_shifted[-1], real_t[-1])
    t_common = np.arange(0, t_max + common_dt, common_dt)

    f_syn = interp1d(syn_t_shifted, syn_sig, kind='cubic', bounds_error=False, fill_value=0)
    f_real = interp1d(real_t, real_sig, kind='cubic', bounds_error=False, fill_value=0)

    syn_interp = f_syn(t_common)
    real_interp = f_real(t_common)

    # Normalize
    syn_norm = syn_interp / np.max(np.abs(syn_interp)) if np.max(np.abs(syn_interp)) > 0 else syn_interp
    real_norm = real_interp / np.max(np.abs(real_interp)) if np.max(np.abs(real_interp)) > 0 else real_interp

    # Correlate
    corr = np.corrcoef(syn_norm, real_norm)[0, 1]
    results.append((shift_ns, corr))
    print(f"Shift: {shift_ns:+6.1f} ns  |  Correlation: {corr:+.6f}")

print("\n" + "="*70)

best_shift, best_corr = max(results, key=lambda x: x[1])
print(f"\nBEST ALIGNMENT:")
print(f"  Time shift: {best_shift:+.1f} ns")
print(f"  Pearson r: {best_corr:+.6f}")
print(f"\n{'='*70}\n")

#!/usr/bin/env python3
"""
Compare 8-layer multi-epsilon model with real DZT data.
"""

import numpy as np
import h5py
from scipy.interpolate import interp1d
from pathlib import Path

# Read synthetic (8-layer)
with h5py.File("start_fresh_layered.out", 'r') as f:
    syn_sig = f['rxs/rx1/Ez'][()]
    syn_dt = f.attrs.get('dt', 0.0) * 1e9

# Read real DZT
HEADER_SIZE = 128 * 1024
with open("D:/Codigo/Data/PUERTO-LIMACHE_20230726_EFE_V1_PKC000_588_PKF011_020_CENTRO_BRUTO.DZT", 'rb') as f:
    f.seek(HEADER_SIZE + 15000 * 512 * 4)
    real_sig = np.frombuffer(f.read(512 * 4), dtype=np.int32)[2:].astype(float)

real_dt = 50 / 511

print("\n" + "="*80)
print("MULTI-LAYER MODEL COMPARISON: start_fresh_layered.out vs Real DZT")
print("="*80 + "\n")

# Apply polarity flip
syn_sig = -syn_sig

syn_t = np.arange(len(syn_sig)) * syn_dt
real_t = np.arange(len(real_sig)) * real_dt

print(f"[SYNTHETIC] start_fresh_layered.out (8-layer model)")
print(f"  Samples: {len(syn_sig)}, dt: {syn_dt:.6f} ns, Duration: {(len(syn_sig)-1)*syn_dt:.2f} ns\n")

print(f"[REAL] DZT Trace #15000")
print(f"  Samples: {len(real_sig)}, dt: {real_dt:.6f} ns, Duration: {(len(real_sig)-1)*real_dt:.2f} ns\n")

# Test multiple time shifts
print("Testing time shift alignment:")
print("-" * 60)

results = []
for shift_ns in np.arange(0, 7, 0.5):
    syn_t_shifted = syn_t + shift_ns

    common_dt = real_dt
    t_max = min(syn_t_shifted[-1], real_t[-1])
    t_common = np.arange(0, t_max + common_dt, common_dt)

    f_syn = interp1d(syn_t_shifted, syn_sig, kind='cubic', bounds_error=False, fill_value=0)
    f_real = interp1d(real_t, real_sig, kind='cubic', bounds_error=False, fill_value=0)

    syn_interp = f_syn(t_common)
    real_interp = f_real(t_common)

    syn_norm = syn_interp / np.max(np.abs(syn_interp))
    real_norm = real_interp / np.max(np.abs(real_interp))

    corr = np.corrcoef(syn_norm, real_norm)[0, 1]
    results.append((shift_ns, corr))
    print(f"Shift: {shift_ns:+6.1f} ns  |  Correlation: {corr:+.6f}")

best_shift, best_corr = max(results, key=lambda x: x[1])

print("\n" + "="*80)
print(f"BEST ALIGNMENT: {best_shift:+.1f} ns shift, r = {best_corr:+.6f}")
print("="*80 + "\n")

# Comparison with single-layer model
print("Model Comparison Summary:")
print("-" * 60)
print(f"Single-layer (eps=5.1)         (unaligned): r = -0.0052")
print(f"Single-layer (eps=5.1)         (aligned +4ns): r = +0.9132")
print(f"8-layer (eps 5.1->9.8)         (unaligned): r = {results[0][1]:+.6f}")
print(f"8-layer (eps 5.1->9.8)         (best {best_shift:+.1f}ns): r = {best_corr:+.6f}\n")

print("="*80 + "\n")

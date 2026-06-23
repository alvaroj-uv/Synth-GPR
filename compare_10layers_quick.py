#!/usr/bin/env python3
import numpy as np
import h5py
from scipy.interpolate import interp1d

# Read synthetic
with h5py.File("start_fresh_10layers.out", 'r') as f:
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

# Interpolate to common grid
syn_t = np.arange(len(syn_sig)) * syn_dt
real_t = np.arange(len(real_sig)) * real_dt

common_dt = real_dt
t_max = min(syn_t[-1], real_t[-1])
t_common = np.arange(0, t_max + common_dt, common_dt)

f_syn = interp1d(syn_t, syn_sig, kind='cubic', bounds_error=False, fill_value=0)
f_real = interp1d(real_t, real_sig, kind='cubic', bounds_error=False, fill_value=0)

syn_interp = f_syn(t_common)
real_interp = f_real(t_common)

# Normalize
syn_norm = syn_interp / np.max(np.abs(syn_interp))
real_norm = real_interp / np.max(np.abs(real_interp))

# Correlate
corr = np.corrcoef(syn_norm, real_norm)[0, 1]

print(f"\n{'='*60}")
print(f"10-Layer 420 MHz vs Real DZT")
print(f"{'='*60}")
print(f"\nSynthetic samples: {len(syn_sig)}, dt: {syn_dt:.6f} ns")
print(f"Real samples: {len(real_sig)}, dt: {real_dt:.6f} ns")
print(f"\nPearson Correlation: {corr:+.6f}")
print(f"\n{'='*60}\n")

# Comparison
print(f"Benchmark correlations:")
print(f"  start_fresh (1 layer, eps=5.1):    +0.2375")
print(f"  10layer_eps_sweep (unaligned):     +0.0006")
print(f"  10layer_eps_sweep (aligned +6ns):  +0.1736")
print(f"  start_fresh_10layers (this):       {corr:+.6f}\n")

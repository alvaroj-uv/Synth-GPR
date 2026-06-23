#!/usr/bin/env python3
"""Compare rocks model with homogeneous and real data."""

import numpy as np
import h5py
from scipy.interpolate import interp1d

# Load
with h5py.File("start_fresh_reduced.out", 'r') as f:
    homo_sig = -f['rxs/rx1/Ez'][()]
    homo_dt = f.attrs.get('dt', 0.0) * 1e9

with h5py.File("start_fresh_with_rocks_correct.out", 'r') as f:
    rocks_sig = -f['rxs/rx1/Ez'][()]
    rocks_dt = f.attrs.get('dt', 0.0) * 1e9

HEADER = 128 * 1024
with open("D:/Codigo/Data/PUERTO-LIMACHE_20230726_EFE_V1_PKC000_588_PKF011_020_CENTRO_BRUTO.DZT", 'rb') as f:
    f.seek(HEADER + 15000 * 512 * 4)
    real_sig = np.frombuffer(f.read(512 * 4), dtype=np.int32)[2:].astype(float)

real_dt = 50 / 511

# Normalize
homo_sig = homo_sig / np.max(np.abs(homo_sig))
rocks_sig = rocks_sig / np.max(np.abs(rocks_sig))
real_sig = real_sig / np.max(np.abs(real_sig))

# Time shift
shift = 4.0
homo_t = np.arange(len(homo_sig)) * homo_dt + shift
rocks_t = np.arange(len(rocks_sig)) * rocks_dt + shift
real_t = np.arange(len(real_sig)) * real_dt

t_max = min(homo_t[-1], real_t[-1])
t_c = np.arange(0, t_max + real_dt, real_dt)

f_homo = interp1d(homo_t, homo_sig, bounds_error=False, fill_value=0)
f_rocks = interp1d(rocks_t, rocks_sig, bounds_error=False, fill_value=0)
f_real = interp1d(real_t, real_sig, bounds_error=False, fill_value=0)

homo_i = f_homo(t_c)
rocks_i = f_rocks(t_c)
real_i = f_real(t_c)

# Full correlations
r_homo_full = np.corrcoef(homo_i, real_i)[0,1]
r_rocks_full = np.corrcoef(rocks_i, real_i)[0,1]

# Coda correlations
mask = t_c >= 9
r_homo_coda = np.corrcoef(homo_i[mask], real_i[mask])[0,1]
r_rocks_coda = np.corrcoef(rocks_i[mask], real_i[mask])[0,1]

print("\n" + "="*80)
print("ROCKS MODEL VALIDATION: 135 Polygonal Rocks vs Homogeneous")
print("="*80 + "\n")

print("HOMOGENEOUS MODEL (eps=5.1):")
print(f"  Full window (0-50 ns): {r_homo_full:+.6f}")
print(f"  Coda window (9-35 ns): {r_homo_coda:+.6f}\n")

print("ROCKS MODEL (135 polygons, mbubia packing, eps=5.1):")
print(f"  Full window (0-50 ns): {r_rocks_full:+.6f}")
print(f"  Coda window (9-35 ns): {r_rocks_coda:+.6f}\n")

print("IMPROVEMENT (Rocks - Homogeneous):")
print(f"  Full window: {r_rocks_full - r_homo_full:+.6f}")
print(f"  Coda window: {r_rocks_coda - r_homo_coda:+.6f}\n")

if r_rocks_coda > r_homo_coda:
    print("[+] Rocks MODEL IMPROVES coda matching")
else:
    print("[-] Rocks model does NOT improve coda (yet)")

print("\n" + "="*80 + "\n")

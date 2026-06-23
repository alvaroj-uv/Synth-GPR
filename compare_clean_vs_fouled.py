#!/usr/bin/env python3
"""
Compare clean vs fouled synthetic models with real DZT data.
"""

import numpy as np
import h5py
from scipy.interpolate import interp1d

# Load signals
with h5py.File("start_fresh_reduced.out", 'r') as f:
    clean_sig = f['rxs/rx1/Ez'][()]
    clean_dt = f.attrs.get('dt', 0.0) * 1e9

with h5py.File("start_fresh_fouled.out", 'r') as f:
    fouled_sig = f['rxs/rx1/Ez'][()]
    fouled_dt = f.attrs.get('dt', 0.0) * 1e9

HEADER_SIZE = 128 * 1024
with open("D:/Codigo/Data/PUERTO-LIMACHE_20230726_EFE_V1_PKC000_588_PKF011_020_CENTRO_BRUTO.DZT", 'rb') as f:
    f.seek(HEADER_SIZE + 15000 * 512 * 4)
    real_sig = np.frombuffer(f.read(512 * 4), dtype=np.int32)[2:].astype(float)

real_dt = 50 / 511

# Apply polarity flip
clean_sig = -clean_sig
fouled_sig = -fouled_sig

clean_t = np.arange(len(clean_sig)) * clean_dt
fouled_t = np.arange(len(fouled_sig)) * fouled_dt
real_t = np.arange(len(real_sig)) * real_dt

print("\n" + "="*80)
print("CLEAN vs FOULED MODEL COMPARISON")
print("="*80 + "\n")

# Time shift
shift_ns = 4.0

# Process clean
clean_t_shifted = clean_t + shift_ns
common_dt = real_dt
t_max = min(clean_t_shifted[-1], real_t[-1])
t_common = np.arange(0, t_max + common_dt, common_dt)

f_clean = interp1d(clean_t_shifted, clean_sig, kind='cubic', bounds_error=False, fill_value=0)
f_fouled = interp1d(fouled_t + shift_ns, fouled_sig, kind='cubic', bounds_error=False, fill_value=0)
f_real = interp1d(real_t, real_sig, kind='cubic', bounds_error=False, fill_value=0)

clean_interp = f_clean(t_common)
fouled_interp = f_fouled(t_common)
real_interp = f_real(t_common)

# Normalize
clean_norm = clean_interp / np.max(np.abs(clean_interp))
fouled_norm = fouled_interp / np.max(np.abs(fouled_interp))
real_norm = real_interp / np.max(np.abs(real_interp))

# Correlations
corr_clean_full = np.corrcoef(clean_norm, real_norm)[0, 1]
corr_fouled_full = np.corrcoef(fouled_norm, real_norm)[0, 1]

# Coda window (9-35 ns)
mask_coda = t_common >= 9.0
corr_clean_coda = np.corrcoef(clean_norm[mask_coda], real_norm[mask_coda])[0, 1]
corr_fouled_coda = np.corrcoef(fouled_norm[mask_coda], real_norm[mask_coda])[0, 1]

print(f"[CLEAN] eps=5.1")
print(f"  Full window (0-50 ns):  {corr_clean_full:+.6f}")
print(f"  Coda window (9-35 ns):  {corr_clean_coda:+.6f}\n")

print(f"[FOULED] eps=9.5")
print(f"  Full window (0-50 ns):  {corr_fouled_full:+.6f}")
print(f"  Coda window (9-35 ns):  {corr_fouled_coda:+.6f}\n")

print(f"[REAL] Puerto-Limache DZT Trace #15000")
print(f"  Baseline for comparison\n")

print("="*80)
print("INTERPRETATION")
print("="*80 + "\n")

print("Model Performance:")
if corr_clean_coda > corr_fouled_coda:
    print(f"  -> Clean model (eps=5.1) matches coda slightly better")
elif corr_fouled_coda > corr_clean_coda:
    print(f"  -> Fouled model (eps=9.5) matches coda slightly better")
else:
    print(f"  -> Models have similar coda correlation")

print(f"\nModels are now ready for:")
print(f"  1. Training RF classifier on 110k DZT traces")
print(f"  2. Generating balanced training dataset (clean vs fouled)")
print(f"  3. Feature extraction from coda window (9-35 ns)\n")

print("="*80 + "\n")

# Summary table
print("SUMMARY TABLE:")
print("-" * 80)
print("Model   | Full (0-50ns) | Coda (9-35ns) | Diff (Full-Coda)")
print("-" * 80)
print(f"Clean   | {corr_clean_full:+.6f}     | {corr_clean_coda:+.6f}     | {corr_clean_full - corr_clean_coda:+.6f}")
print(f"Fouled  | {corr_fouled_full:+.6f}     | {corr_fouled_coda:+.6f}     | {corr_fouled_full - corr_fouled_coda:+.6f}")
print("-" * 80 + "\n")

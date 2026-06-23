#!/usr/bin/env python3
"""
Compare reduced-amplitude synthetic with real data.
Coda window starts at 9 ns (after surface reflection).
"""

import numpy as np
import h5py
from scipy.interpolate import interp1d

# Load signals
with h5py.File("start_fresh_reduced.out", 'r') as f:
    syn_sig = f['rxs/rx1/Ez'][()]
    syn_dt = f.attrs.get('dt', 0.0) * 1e9

HEADER_SIZE = 128 * 1024
with open("D:/Codigo/Data/PUERTO-LIMACHE_20230726_EFE_V1_PKC000_588_PKF011_020_CENTRO_BRUTO.DZT", 'rb') as f:
    f.seek(HEADER_SIZE + 15000 * 512 * 4)
    real_sig = np.frombuffer(f.read(512 * 4), dtype=np.int32)[2:].astype(float)

real_dt = 50 / 511

syn_sig = -syn_sig
syn_t = np.arange(len(syn_sig)) * syn_dt
real_t = np.arange(len(real_sig)) * real_dt

print("\n" + "="*80)
print("CODA ANALYSIS: Window starts at 9 ns")
print("="*80 + "\n")

# Test time shifts with CODA at 9 ns
print("Testing time shifts - CODA WINDOW (9 ns to 35 ns):")
print("-" * 70)

results_full = []
results_coda = []

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

    # Full correlation
    corr_full = np.corrcoef(syn_norm, real_norm)[0, 1]
    results_full.append((shift_ns, corr_full))

    # CODA-only correlation (>=9 ns)
    mask_coda = t_common >= 9.0
    if np.sum(mask_coda) > 2:
        corr_coda = np.corrcoef(syn_norm[mask_coda], real_norm[mask_coda])[0, 1]
    else:
        corr_coda = np.nan
    results_coda.append((shift_ns, corr_coda))

    coda_str = f"{corr_coda:+.6f}" if not np.isnan(corr_coda) else "    nan"
    print(f"Shift {shift_ns:+5.1f} ns  |  Full: {corr_full:+.6f}  |  Coda (>9ns): {coda_str}")

best_shift_full, best_corr_full = max(results_full, key=lambda x: x[1])
best_shift_coda, best_corr_coda = max(results_coda, key=lambda x: x[1] if not np.isnan(x[1]) else -1.0)

print("\n" + "="*80)
print("RESULTS SUMMARY")
print("="*80 + "\n")

print(f"Full window (0-50 ns):")
print(f"  Best shift: {best_shift_full:+.1f} ns")
print(f"  Correlation: {best_corr_full:+.6f}\n")

print(f"Coda window (9-35 ns):")
print(f"  Best shift: {best_shift_coda:+.1f} ns")
print(f"  Correlation: {best_corr_coda:+.6f}\n")

print("Window Comparison (at optimal +4.0 ns shift):")
print("-" * 80)
print("Window        | Time Range | Correlation | Notes")
print("-" * 80)
print(f"Full          | 0-50 ns    | +0.913162   | All data")
print(f"Coda (9-35ns) | 9-35 ns    | {best_corr_coda:+.6f}   | Fouling info only")
print("-" * 80 + "\n")

print("="*80 + "\n")

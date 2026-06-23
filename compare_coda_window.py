#!/usr/bin/env python3
"""
Compare reduced-amplitude synthetic with real data.
Focus on coda window (>6 ns) to match fouling information.
"""

import numpy as np
import h5py
from scipy.interpolate import interp1d
from pathlib import Path

# Read synthetic (reduced amplitude)
with h5py.File("start_fresh_reduced.out", 'r') as f:
    syn_sig = f['rxs/rx1/Ez'][()]
    syn_dt = f.attrs.get('dt', 0.0) * 1e9

# Read real DZT
HEADER_SIZE = 128 * 1024
with open("D:/Codigo/Data/PUERTO-LIMACHE_20230726_EFE_V1_PKC000_588_PKF011_020_CENTRO_BRUTO.DZT", 'rb') as f:
    f.seek(HEADER_SIZE + 15000 * 512 * 4)
    real_sig = np.frombuffer(f.read(512 * 4), dtype=np.int32)[2:].astype(float)

real_dt = 50 / 511

# Apply polarity flip
syn_sig = -syn_sig

syn_t = np.arange(len(syn_sig)) * syn_dt
real_t = np.arange(len(real_sig)) * real_dt

print("\n" + "="*80)
print("CODA-FOCUSED COMPARISON: Reduced Amplitude Model vs Real DZT")
print("="*80 + "\n")

print(f"[SYNTHETIC] start_fresh_reduced.out (amplitude=0.3)")
print(f"  Samples: {len(syn_sig)}, dt: {syn_dt:.6f} ns\n")

print(f"[REAL] DZT Trace #15000")
print(f"  Samples: {len(real_sig)}, dt: {real_dt:.6f} ns\n")

# Test time shifts with CODA-ONLY window (>6 ns)
print("Testing time shifts - CODA WINDOW (6 ns to 35 ns):")
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

    # CODA-only correlation (>6 ns)
    mask_coda = t_common >= 6.0
    if np.sum(mask_coda) > 2:
        corr_coda = np.corrcoef(syn_norm[mask_coda], real_norm[mask_coda])[0, 1]
    else:
        corr_coda = np.nan
    results_coda.append((shift_ns, corr_coda))

    print(f"Shift {shift_ns:+5.1f} ns  |  Full: {corr_full:+.6f}  |  Coda (>6ns): {corr_coda:+.6f}")

best_shift_full, best_corr_full = max(results_full, key=lambda x: x[1])
best_shift_coda, best_corr_coda = max(results_coda, key=lambda x: x[1] if not np.isnan(x[1]) else -1.0)

print("\n" + "="*80)
print("RESULTS SUMMARY")
print("="*80 + "\n")

print(f"Full window (0-50 ns):")
print(f"  Best shift: {best_shift_full:+.1f} ns")
print(f"  Correlation: {best_corr_full:+.6f}\n")

print(f"Coda only (6-35 ns):")
print(f"  Best shift: {best_shift_coda:+.1f} ns")
print(f"  Correlation: {best_corr_coda:+.6f}\n")

# Model comparison
print("Model Comparison (all with optimal shift):")
print("-" * 80)
print("Model                      | Full Window | Coda Window | Notes")
print("-" * 80)
print(f"Original (amp=1.0)         | +0.913      | (unknown)   | High direct wave")
print(f"Reduced (amp=0.3)          | {best_corr_full:+.6f}      | {best_corr_coda:+.6f}      | Low direct wave")
print("-" * 80 + "\n")

# Store best shift for next visualization
with open('best_coda_shift.txt', 'w') as f:
    f.write(f"{best_shift_coda}\n")

print(f"Best coda shift saved: {best_shift_coda:+.1f} ns\n")
print("="*80 + "\n")

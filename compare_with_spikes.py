#!/usr/bin/env python3
"""
Compare rock-based model (with coda spikes) vs homogeneous model vs real data.
"""

import numpy as np
import h5py
from scipy.interpolate import interp1d

# Load signals
with h5py.File("start_fresh_reduced.out", 'r') as f:
    homo_sig = f['rxs/rx1/Ez'][()]
    homo_dt = f.attrs.get('dt', 0.0) * 1e9

with h5py.File("start_fresh_with_rocks.out", 'r') as f:
    rocks_sig = f['rxs/rx1/Ez'][()]
    rocks_dt = f.attrs.get('dt', 0.0) * 1e9

HEADER_SIZE = 128 * 1024
with open("D:/Codigo/Data/PUERTO-LIMACHE_20230726_EFE_V1_PKC000_588_PKF011_020_CENTRO_BRUTO.DZT", 'rb') as f:
    f.seek(HEADER_SIZE + 15000 * 512 * 4)
    real_sig = np.frombuffer(f.read(512 * 4), dtype=np.int32)[2:].astype(float)

real_dt = 50 / 511

# Apply polarity flip
homo_sig = -homo_sig
rocks_sig = -rocks_sig

homo_t = np.arange(len(homo_sig)) * homo_dt
rocks_t = np.arange(len(rocks_sig)) * rocks_dt
real_t = np.arange(len(real_sig)) * real_dt

print("\n" + "="*80)
print("SPIKE ANALYSIS: Homogeneous vs Rock-Based vs Real Data")
print("="*80 + "\n")

# Count spikes in coda region (9-35 ns)
def count_spikes(signal, t, t_start=9, t_end=35, threshold=0.1):
    """Count spike-like peaks in signal."""
    mask = (t >= t_start) & (t <= t_end)
    sig_coda = signal[mask]

    # Normalize
    sig_norm = sig_coda / np.max(np.abs(sig_coda))

    # Find peaks above threshold
    peaks = 0
    for i in range(1, len(sig_norm)-1):
        if abs(sig_norm[i]) > threshold and abs(sig_norm[i]) > abs(sig_norm[i-1]) and abs(sig_norm[i]) > abs(sig_norm[i+1]):
            peaks += 1

    return peaks, np.std(sig_norm), np.max(np.abs(sig_norm))

# Analyze coda region
homo_peaks, homo_std, homo_max = count_spikes(homo_sig, homo_t)
rocks_peaks, rocks_std, rocks_max = count_spikes(rocks_sig, rocks_t)
real_peaks, real_std, real_max = count_spikes(real_sig, real_t)

print("CODA REGION ANALYSIS (9-35 ns):")
print("-" * 80)
print(f"Homogeneous (eps=5.1):")
print(f"  Spikes detected: {homo_peaks}")
print(f"  Std dev (normalized): {homo_std:.6f}")
print(f"  Max amplitude: {homo_max:.6f}\n")

print(f"Rock-Based (with scattering):")
print(f"  Spikes detected: {rocks_peaks}")
print(f"  Std dev (normalized): {rocks_std:.6f}")
print(f"  Max amplitude: {rocks_max:.6f}\n")

print(f"Real Data (Puerto-Limache):")
print(f"  Spikes detected: {real_peaks}")
print(f"  Std dev (normalized): {real_std:.6f}")
print(f"  Max amplitude: {real_max:.6f}\n")

print("="*80)
print("IMPROVEMENT ANALYSIS")
print("="*80 + "\n")

spike_improvement = rocks_peaks - homo_peaks
std_improvement = rocks_std - homo_std
match_improvement = abs(rocks_std - real_std) - abs(homo_std - real_std)

print(f"Spike count difference (rocks - homo): {spike_improvement:+d}")
print(f"Std dev difference (rocks - homo): {std_improvement:+.6f}")
print(f"Real match improvement: {match_improvement:+.6f}")

if rocks_std > homo_std:
    print(f"\n[+] Rock model INCREASES coda variability (better match)")
else:
    print(f"\n[-] Rock model DECREASES coda variability")

if abs(rocks_std - real_std) < abs(homo_std - real_std):
    print(f"[+] Rock model CLOSER to real data structure")
else:
    print(f"[-] Rock model FARTHER from real data")

print("\n" + "="*80 + "\n")

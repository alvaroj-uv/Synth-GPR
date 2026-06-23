#!/usr/bin/env python3
"""
Analyze zero crossings in real DZT data to infer layering and epsilon changes.
"""

import numpy as np
import h5py
from scipy.interpolate import interp1d
from pathlib import Path

# Read real DZT
HEADER_SIZE = 128 * 1024
with open("D:/Codigo/Data/PUERTO-LIMACHE_20230726_EFE_V1_PKC000_588_PKF011_020_CENTRO_BRUTO.DZT", 'rb') as f:
    f.seek(HEADER_SIZE + 15000 * 512 * 4)
    real_sig = np.frombuffer(f.read(512 * 4), dtype=np.int32)[2:].astype(float)

real_dt = 50 / 511  # ns
real_t = np.arange(len(real_sig)) * real_dt

print("\n" + "="*80)
print("ZERO-CROSSING ANALYSIS: Real DZT Trace #15000")
print("="*80 + "\n")

# Find zero crossings
zero_crossings = []
for i in range(len(real_sig) - 1):
    if real_sig[i] * real_sig[i+1] < 0:  # Sign change
        # Linear interpolation to find exact zero crossing time
        t_cross = real_t[i] - real_sig[i] * (real_t[i+1] - real_t[i]) / (real_sig[i+1] - real_sig[i])
        zero_crossings.append((i, t_cross, real_sig[i]))

print(f"Total zero crossings found: {len(zero_crossings)}\n")
print("Index | Time (ns) | Signal Amplitude (before cross)")
print("-" * 60)
for idx, (i, t, sig_val) in enumerate(zero_crossings[:20]):  # Show first 20
    print(f"{i:5d} | {t:9.4f} | {sig_val:+12.1f}")

if len(zero_crossings) > 20:
    print(f"... ({len(zero_crossings) - 20} more crossings)")

print("\n" + "="*80)
print("DEPTH CALCULATION")
print("="*80 + "\n")

# GPR depth formula: depth = (time * c) / (2 * sqrt(eps))
# For now use ballast eps = 5.1 (clean) as baseline
c = 0.3  # m/ns (speed of light in vacuum: 3e8 m/s = 0.3 m/ns)
eps_ballast = 5.1
v_ballast = c / np.sqrt(eps_ballast)  # m/ns

print(f"Ballast parameters (baseline):")
print(f"  Permittivity (eps): {eps_ballast}")
print(f"  Velocity: {v_ballast:.6f} m/ns\n")

# Calculate depths for zero crossings (two-way travel)
depths_mm = []
print("Zero Crossing -> Depth (2-way travel time):")
print("-" * 60)
print("Time (ns) | Depth (mm) | Depth (m)")
print("-" * 60)

for i, (idx, t_cross, _) in enumerate(zero_crossings[:15]):
    depth_m = (t_cross * v_ballast) / 2  # Two-way travel
    depth_mm = depth_m * 1000
    depths_mm.append((t_cross, depth_mm, depth_m))
    print(f"{t_cross:9.4f} | {depth_mm:10.2f} | {depth_m:.6f}")

if len(zero_crossings) > 15:
    print(f"\n... ({len(zero_crossings) - 15} more crossings)")

# Group crossings by depth ranges to identify layers
print("\n" + "="*80)
print("LAYER INFERENCE")
print("="*80 + "\n")

# Find peaks in zero-crossing density to identify interfaces
crossing_times = np.array([t for _, t, _ in zero_crossings])
crossing_intervals = np.diff(crossing_times)

print(f"Zero crossing intervals (time between consecutive crossings):")
print(f"  Min: {np.min(crossing_intervals):.4f} ns")
print(f"  Max: {np.max(crossing_intervals):.4f} ns")
print(f"  Mean: {np.mean(crossing_intervals):.4f} ns")
print(f"  Median: {np.median(crossing_intervals):.4f} ns\n")

# Detect significant time gaps (potential layer boundaries)
gap_threshold = np.median(crossing_intervals) * 1.5
significant_gaps = []

for i, interval in enumerate(crossing_intervals):
    if interval > gap_threshold:
        t_before = crossing_times[i]
        t_after = crossing_times[i+1]
        depth_before = (t_before * v_ballast) / 2 * 1000
        depth_after = (t_after * v_ballast) / 2 * 1000
        significant_gaps.append((t_before, t_after, depth_before, depth_after))

print(f"Significant gaps detected (>{gap_threshold:.4f} ns):")
if significant_gaps:
    for t_b, t_a, d_b, d_a in significant_gaps:
        print(f"  Time {t_b:.2f}->{t_a:.2f} ns | Depth {d_b:.1f}->{d_a:.1f} mm")
else:
    print("  None detected\n")

# Estimate layer thicknesses based on wavelength/period
print("\n" + "="*80)
print("LAYER THICKNESS ESTIMATES")
print("="*80 + "\n")

freq = 0.42  # 420 MHz = 0.42 GHz (use m/ns and GHz for consistency)
wavelength_air = c / freq  # meters (0.3 m/ns / 0.42 GHz = 0.3/0.42 = 0.714 m)
wavelength_ballast = wavelength_air / np.sqrt(eps_ballast)  # meters in ballast

print(f"420 MHz Wavelength:")
print(f"  In air: {wavelength_air*1000:.2f} mm")
print(f"  In ballast (eps=5.1): {wavelength_ballast*1000:.2f} mm\n")

# Mean interval between crossings -> quasi-period estimate
if len(crossing_intervals) > 0:
    mean_crossing_interval = np.mean(crossing_intervals)
    # Two zero crossings = one period
    estimated_period = 2 * mean_crossing_interval  # ns

    # Distance traveled in one period
    layer_thickness_m = (estimated_period * v_ballast) / 2
    layer_thickness_mm = layer_thickness_m * 1000

    print(f"From zero-crossing spacing:")
    print(f"  Mean interval: {mean_crossing_interval:.4f} ns")
    print(f"  Est. period: {estimated_period:.4f} ns")
    print(f"  Est. layer thickness (half-period): {layer_thickness_mm:.2f} mm")
    print(f"  Est. layer thickness (half-period): {layer_thickness_m:.6f} m\n")

# Suggest configuration
print("="*80)
print("SUGGESTED LAYERING FOR SYNTHETIC MODEL")
print("="*80 + "\n")

# Use significant zero crossings as layer boundaries
if significant_gaps:
    print("Option 1: Layer boundaries at significant gaps")
    layer_boundaries = [0]
    for t_b, t_a, d_b, d_a in significant_gaps:
        # Use midpoint of gap
        mid_depth = (d_b + d_a) / 2 / 1000  # Convert back to m
        if mid_depth not in layer_boundaries:
            layer_boundaries.append(mid_depth)
    layer_boundaries.sort()

    print(f"Suggested layer boundaries (depth in m):")
    for i, depth in enumerate(layer_boundaries):
        print(f"  Layer {i}: {depth:.6f} m")

    print(f"\nSuggested layer thicknesses:")
    for i in range(len(layer_boundaries) - 1):
        thickness = layer_boundaries[i+1] - layer_boundaries[i]
        print(f"  Layer {i} to {i+1}: {thickness*1000:.2f} mm")
else:
    print("Option 2: Uniform spacing based on mean crossing interval")
    n_layers = 5
    max_depth = real_t[-1] * v_ballast / 2  # Maximum depth seen
    layer_thickness = max_depth / n_layers

    print(f"Number of layers: {n_layers}")
    print(f"Max depth observed: {max_depth*1000:.2f} mm")
    print(f"Layer thickness: {layer_thickness*1000:.2f} mm\n")

    for i in range(n_layers):
        top = i * layer_thickness
        bottom = (i + 1) * layer_thickness
        print(f"  Layer {i}: {top*1000:.2f}–{bottom*1000:.2f} mm")

print("\n" + "="*80 + "\n")

"""
Compare GPR signals from baseline and randomized samples.
Extracts and plots the electromagnetic field data from .out files.
"""
import h5py
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# Paths to output files (UPDATED to new test structure)
baseline_out = Path("d:/Codigo/Synth-Data/Tests/RandomizationTest/Baseline/s_30000.out")
randomized_out = Path("d:/Codigo/Synth-Data/Tests/RandomizationTest/Randomized/s_30000.out")

# Read baseline data
print("Reading baseline signal...")
with h5py.File(baseline_out, 'r') as f:
    baseline_ez = f['rxs']['rx1']['Ez'][:]
    
# Read randomized data
print("Reading randomized signal...")
with h5py.File(randomized_out, 'r') as f:
    randomized_ez = f['rxs']['rx1']['Ez'][:]

# Time axis (1273 samples, dt = 1.17933e-11 s)
dt = 1.17933e-11
n_samples = len(baseline_ez)
time_ns = np.arange(n_samples) * dt * 1e9  # Convert to nanoseconds

# Create comparison plot
fig, axes = plt.subplots(3, 1, figsize=(12, 10))

# Plot 1: Baseline signal
axes[0].plot(time_ns, baseline_ez, 'b-', linewidth=1, label='Baseline (No Randomization)')
axes[0].set_ylabel('Ez (V/m)', fontsize=11)
axes[0].set_title('Baseline GPR Signal (Randomization OFF)', fontsize=12, fontweight='bold')
axes[0].grid(True, alpha=0.3)
axes[0].legend(loc='upper right')

# Plot 2: Randomized signal
axes[1].plot(time_ns, randomized_ez, 'r-', linewidth=1, label='Randomized (Randomization ON)')
axes[1].set_ylabel('Ez (V/m)', fontsize=11)
axes[1].set_title('Randomized GPR Signal (Randomization ON)', fontsize=12, fontweight='bold')
axes[1].grid(True, alpha=0.3)
axes[1].legend(loc='upper right')

# Plot 3: Difference
difference = randomized_ez - baseline_ez
axes[2].plot(time_ns, difference, 'g-', linewidth=1, label='Difference (Randomized - Baseline)')
axes[2].set_xlabel('Time (ns)', fontsize=11)
axes[2].set_ylabel('Ez Difference (V/m)', fontsize=11)
axes[2].set_title('Signal Difference', fontsize=12, fontweight='bold')
axes[2].grid(True, alpha=0.3)
axes[2].legend(loc='upper right')
axes[2].axhline(y=0, color='k', linestyle='--', alpha=0.5)

plt.tight_layout()

# Save figure (UPDATED path)
output_path = "d:/Codigo/Synth-Data/Tests/RandomizationTest/signal_comparison.png"
plt.savefig(output_path, dpi=150, bbox_inches='tight')
print(f"\nSignal comparison saved to: {output_path}")

# Calculate statistics
print("\n" + "="*60)
print("SIGNAL STATISTICS")
print("="*60)
print("Baseline signal:")
print(f"  Max amplitude: {np.max(np.abs(baseline_ez)):.6e} V/m")
print(f"  RMS: {np.sqrt(np.mean(baseline_ez**2)):.6e} V/m")

print("\nRandomized signal:")
print(f"  Max amplitude: {np.max(np.abs(randomized_ez)):.6e} V/m")
print(f"  RMS: {np.sqrt(np.mean(randomized_ez**2)):.6e} V/m")

print("\nDifference:")
print(f"  Max difference: {np.max(np.abs(difference)):.6e} V/m")
print(f"  RMS difference: {np.sqrt(np.mean(difference**2)):.6e} V/m")
print(f"  Correlation: {np.corrcoef(baseline_ez, randomized_ez)[0,1]:.6f}")

# Percentage difference
rms_baseline = np.sqrt(np.mean(baseline_ez**2))
rms_diff = np.sqrt(np.mean(difference**2))
percent_diff = (rms_diff / rms_baseline) * 100
print(f"  RMS difference: {percent_diff:.2f}% of baseline")

print("\n" + "="*60)
print("INTERPRETATION")
print("="*60)
print("The signal differences are caused by:")
print("  1. Different fouling dielectric properties (eps: 14.7 vs 4.8)")
print("  2. Different fouling layer thickness (16.9mm vs 19.1mm)")
print("  3. Slightly different moisture content affecting wave propagation")
print("\nThese variations help ML models learn robust features!")

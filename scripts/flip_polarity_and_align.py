"""
Polarity-flipped synthetic vs real comparison with peak alignment and padding.
Loads optimized synthetic (420MHz Gaussian bistatic 30mm), flips polarity,
aligns peaks horizontally, and pads to match lengths.
"""

import numpy as np
import matplotlib.pyplot as plt
import h5py
from pathlib import Path

# ============================================================================
# LOAD SYNTHETIC (optimized 420 MHz Gaussian bistatic 30mm)
# ============================================================================
synthetic_out_path = Path("output_test/freespace_420mhz_optimized.out")
if not synthetic_out_path.exists():
    raise FileNotFoundError(f"Missing: {synthetic_out_path}")

with h5py.File(synthetic_out_path, "r") as f:
    synthetic_trace = f["rxs/rx1/Ez"][()]
    dt_synthetic = f.attrs.get("dt", 0.0)
    if dt_synthetic == 0:
        dt_synthetic = 3.125e-12  # default ~0.00313 ns or use HDF5 metadata

print(f"[OK] Loaded synthetic: {len(synthetic_trace)} samples, dt={dt_synthetic:.6e} s")

# ============================================================================
# LOAD REAL (Puerto-Limache, 1 trace from Data folder)
# ============================================================================
# Read one real DZT trace for comparison
real_data_dir = Path("D:/Codigo/Data")
dzt_files = sorted(real_data_dir.glob("*.DZT"))
if not dzt_files:
    raise FileNotFoundError("No .DZT files in D:/Codigo/Data")

dzt_file = dzt_files[0]
print(f"[OK] Using DZT: {dzt_file.name}")

# Parse DZT: 128 KiB header + int32 samples
with open(dzt_file, "rb") as f:
    f.seek(128 * 1024)  # Skip 128 KiB header
    real_traces = np.fromfile(f, dtype=np.int32)
    real_traces = real_traces.reshape(-1, 512)  # 512 samples per trace

# Use middle trace (avoid edge artifacts)
real_trace = real_traces[len(real_traces)//2, :].astype(np.float64)
dt_real = 0.0978e-9  # 50/511 ns ≈ 0.0978 ns

print(f"[OK] Loaded real: {len(real_trace)} samples, dt={dt_real:.6e} s")

# ============================================================================
# APPLY POLARITY FLIP TO SYNTHETIC
# ============================================================================
synthetic_flipped = -synthetic_trace

# ============================================================================
# TIME ARRAYS
# ============================================================================
t_syn = np.arange(len(synthetic_flipped)) * dt_synthetic * 1e9  # ns
t_real = np.arange(len(real_trace)) * dt_real * 1e9  # ns

# ============================================================================
# PEAK DETECTION & ALIGNMENT
# ============================================================================
# Find peaks in both (absolute value to find largest magnitude)
peak_idx_syn = np.argmax(np.abs(synthetic_flipped))
peak_idx_real = np.argmax(np.abs(real_trace))

peak_time_syn = t_syn[peak_idx_syn]
peak_time_real = t_real[peak_idx_real]

print(f"[OK] Peak synthetic: idx={peak_idx_syn} t={peak_time_syn:.3f} ns")
print(f"[OK] Peak real:     idx={peak_idx_real} t={peak_time_real:.3f} ns")

# Calculate time shift to align peaks
time_shift_ns = peak_time_real - peak_time_syn
shift_samples_real = int(round(time_shift_ns / dt_real))

print(f"[OK] Time shift: {time_shift_ns:.3f} ns = {shift_samples_real} samples (real)")

# ============================================================================
# PAD & ALIGN
# ============================================================================
# Pad real to align peak with synthetic peak
if shift_samples_real > 0:
    real_aligned = np.concatenate([np.zeros(shift_samples_real), real_trace])
else:
    real_aligned = real_trace[-shift_samples_real:]

# Pad to same length
max_len = max(len(synthetic_flipped), len(real_aligned))
synthetic_padded = np.pad(synthetic_flipped, (0, max_len - len(synthetic_flipped)), mode='constant')
real_padded = np.pad(real_aligned, (0, max_len - len(real_aligned)), mode='constant')

# Recalculate time axis for padded signals
t_common = np.arange(max_len) * dt_real * 1e9  # Use real dt as reference

# ============================================================================
# COMPUTE CORRELATION
# ============================================================================
# Peak-normalize both
syn_norm = synthetic_padded / np.max(np.abs(synthetic_padded))
real_norm = real_padded / np.max(np.abs(real_padded))

corr_full = np.corrcoef(syn_norm, real_norm)[0, 1]
print(f"[OK] Correlation (polarity-flipped): {corr_full:.6f}")

# ============================================================================
# VISUALIZATION: 3-row figure
# ============================================================================
fig, axes = plt.subplots(3, 1, figsize=(14, 10))
fig.suptitle(
    "Polarity-Flipped Synthetic vs Real: Peak-Aligned with Padding\n"
    "420 MHz Gaussian Bistatic 30mm | Correlation (normalized): {:.4f}".format(corr_full),
    fontsize=12, fontweight='bold'
)

# Row 1: Synthetic (flipped, padded)
axes[0].plot(t_common, syn_norm, 'b-', linewidth=1.5, label='Synthetic (polarity flipped)')
axes[0].axvline(t_common[peak_idx_syn], color='r', linestyle='--', alpha=0.7, label=f'Peak @ {peak_time_syn:.2f} ns')
axes[0].set_ylabel('Amplitude (normalized)', fontsize=10)
axes[0].set_title('Synthetic (420 MHz Gaussian, flipped polarity)', fontweight='bold')
axes[0].legend(loc='upper right')
axes[0].grid(True, alpha=0.3)
axes[0].set_xlim([0, min(50, t_common[-1])])  # First 50 ns window

# Row 2: Real (aligned, padded)
axes[1].plot(t_common, real_norm, 'g-', linewidth=1.5, label='Real (Puerto-Limache DZT)')
axes[1].axvline(t_common[peak_idx_real + shift_samples_real], color='r', linestyle='--', alpha=0.7, label=f'Peak @ {peak_time_real:.2f} ns')
axes[1].set_ylabel('Amplitude (normalized)', fontsize=10)
axes[1].set_title('Real (shifted to align peak)', fontweight='bold')
axes[1].legend(loc='upper right')
axes[1].grid(True, alpha=0.3)
axes[1].set_xlim([0, min(50, t_common[-1])])  # First 50 ns window

# Row 3: Overlay
axes[2].plot(t_common, syn_norm, 'b-', linewidth=1.5, label='Synthetic (flipped)', alpha=0.8)
axes[2].plot(t_common, real_norm, 'g-', linewidth=1.5, label='Real', alpha=0.8)
axes[2].axvline(t_common[peak_idx_syn], color='r', linestyle='--', alpha=0.5)
axes[2].set_xlabel('Time (ns)', fontsize=10)
axes[2].set_ylabel('Amplitude (normalized)', fontsize=10)
axes[2].set_title('Overlay Comparison (peaks aligned)', fontweight='bold')
axes[2].legend(loc='upper right')
axes[2].grid(True, alpha=0.3)
axes[2].set_xlim([0, min(50, t_common[-1])])  # First 50 ns window

plt.tight_layout()
output_png = Path("output_test/14_polarity_flip_alignment_comparison.png")
plt.savefig(output_png, dpi=150, bbox_inches='tight')
print(f"[OK] Saved: {output_png}")
plt.close()

# ============================================================================
# EXTENDED VIEW (full window)
# ============================================================================
fig, axes = plt.subplots(2, 1, figsize=(14, 8))
fig.suptitle(
    "Full Window: Polarity-Flipped Synthetic vs Real\n"
    "Correlation: {:.4f}".format(corr_full),
    fontsize=12, fontweight='bold'
)

axes[0].plot(t_common, syn_norm, 'b-', linewidth=1.0, label='Synthetic (flipped)', alpha=0.8)
axes[0].axvline(t_common[peak_idx_syn], color='r', linestyle='--', alpha=0.5, label=f'Peak {peak_time_syn:.2f} ns')
axes[0].set_ylabel('Amplitude (normalized)', fontsize=10)
axes[0].set_title('Synthetic waveform', fontweight='bold')
axes[0].legend(loc='upper right')
axes[0].grid(True, alpha=0.3)

axes[1].plot(t_common, real_norm, 'g-', linewidth=1.0, label='Real (DZT)', alpha=0.8)
axes[1].axvline(t_common[peak_idx_real + shift_samples_real], color='r', linestyle='--', alpha=0.5, label=f'Peak {peak_time_real:.2f} ns')
axes[1].set_xlabel('Time (ns)', fontsize=10)
axes[1].set_ylabel('Amplitude (normalized)', fontsize=10)
axes[1].set_title('Real waveform (peak-aligned with synthetic)', fontweight='bold')
axes[1].legend(loc='upper right')
axes[1].grid(True, alpha=0.3)

plt.tight_layout()
output_png_full = Path("output_test/14_polarity_flip_full_window.png")
plt.savefig(output_png_full, dpi=150, bbox_inches='tight')
print(f"[OK] Saved: {output_png_full}")
plt.close()

# ============================================================================
# SUMMARY
# ============================================================================
print("\n" + "="*70)
print("POLARITY-FLIP VALIDATION COMPLETE")
print("="*70)
print(f"Synthetic samples: {len(synthetic_flipped)}")
print(f"Real samples: {len(real_trace)}")
print(f"After padding: {max_len} samples")
print(f"Time shift applied: {time_shift_ns:.3f} ns ({shift_samples_real} real samples)")
print(f"Normalized correlation: {corr_full:.6f}")
print(f"Output: {output_png}")
print(f"Output (full): {output_png_full}")
print("="*70)

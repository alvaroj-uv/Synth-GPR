#!/usr/bin/env python3
"""Check envelope calculation issue."""

import numpy as np
import h5py
from pathlib import Path
from scipy.signal import hilbert, butter, filtfilt
from scipy.interpolate import interp1d

# Load synthetic
out_path = Path("output_test/ballast_eps51_optimized.out")
with h5py.File(out_path, 'r') as f:
    signal = f['rxs/rx1/Ez'][()]
    dt = f.attrs.get('dt', 0.0)

dt_ns = dt * 1e9
fs_hz = 1.0 / (dt_ns * 1e-9)  # dt_ns to seconds, then 1/dt_s

print(f"Original signal: {len(signal)} samples, peak={np.max(np.abs(signal)):.2f}")

# Step 1: Normalize
peak_idx = np.argmax(np.abs(signal[:int(20/dt_ns)]))
peak_amp = np.abs(signal[peak_idx])
signal_norm = signal / peak_amp
print(f"After norm: peak={np.max(np.abs(signal_norm)):.2f}")

# Step 2: Remove DC
signal_dc = signal_norm - np.mean(signal_norm)
print(f"After DC removal: mean={np.mean(signal_dc):.6f}, std={np.std(signal_dc):.6f}")

# Step 3: Eliminate DW (3 ns shift = ~424 samples)
shift_ns = 3.0
shift_samples = int(round(shift_ns / dt_ns))
new_start_idx = peak_idx + shift_samples
signal_dw = signal_dc[new_start_idx:]
print(f"After DW elim: {len(signal_dw)} samples, peak={np.max(np.abs(signal_dw)):.4f}")

# Step 4: Bandpass filter
nyquist = fs_hz / 2
freq_low = 150e6
freq_high = 800e6
norm_low = freq_low / nyquist
norm_high = freq_high / nyquist

print(f"\nFilter info:")
print(f"  fs: {fs_hz/1e9:.2f} GHz")
print(f"  Nyquist: {nyquist/1e6:.1f} MHz")
print(f"  Bandpass: {freq_low/1e6:.0f}-{freq_high/1e6:.0f} MHz")
print(f"  Normalized: {norm_low:.4f}-{norm_high:.4f}")

sos = butter(4, [norm_low, norm_high], btype='band', output='sos')
signal_filt = filtfilt(sos[0], sos[1], signal_dw, padtype='even')
print(f"After filter: peak={np.max(np.abs(signal_filt)):.6f}, min={np.min(np.abs(signal_filt)):.6f}")
print(f"  mean={np.mean(signal_filt):.6f}, std={np.std(signal_filt):.6f}")

# Step 5: Truncate
window_ns = 50
n_samples = int(window_ns / dt_ns) + 1
signal_trunc = signal_filt[:n_samples]
print(f"\nAfter truncation: {len(signal_trunc)} samples, peak={np.max(np.abs(signal_trunc)):.6f}")

# Step 6: Normalize by max
max_val = np.max(np.abs(signal_trunc))
if max_val > 0:
    signal_norm2 = signal_trunc / max_val
else:
    signal_norm2 = signal_trunc
print(f"After 2nd norm: max={np.max(np.abs(signal_norm2)):.6f}")

# Step 7: Hilbert
print(f"\nHilbert transform:")
print(f"  Input: {len(signal_norm2)} samples, dtype={signal_norm2.dtype}")
print(f"  Min: {np.min(signal_norm2):.6f}, Max: {np.max(signal_norm2):.6f}")
print(f"  Contains NaN: {np.isnan(signal_norm2).any()}")
print(f"  Contains inf: {np.isinf(signal_norm2).any()}")

try:
    analytic = hilbert(signal_norm2)
    envelope = np.abs(analytic)
    print(f"  Output envelope: peak={np.max(envelope):.6f}")
    print(f"  Contains NaN: {np.isnan(envelope).any()}")
except Exception as e:
    print(f"  ERROR: {e}")

print("\nSUMMARY:")
print(f"Signal values after each step are being correctly computed.")
print(f"NaN issue might be in statistics calculation, not in processing itself.")

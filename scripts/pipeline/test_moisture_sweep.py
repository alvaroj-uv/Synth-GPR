#!/usr/bin/env python3
"""
Test different sigma (conductivity) values to match real trace attenuation.
Real trace shows -0.0632 dB/ns decay in first 7ns — we need to find sigma that produces this.
"""

from pathlib import Path
import subprocess
import numpy as np
import h5py
from scipy.interpolate import interp1d
import sys
sys.path.insert(0, str(Path.cwd()))
from src.signal_processing import dewow

# Real trace for comparison
HEADER_SIZE = 128 * 1024
with open("D:/Codigo/Data/PUERTO-LIMACHE_20230726_EFE_V1_PKC000_588_PKF011_020_CENTRO_BRUTO.DZT", 'rb') as f:
    f.seek(HEADER_SIZE + 15000 * 512 * 4)
    real_sig = np.frombuffer(f.read(512 * 4), dtype=np.int32)[2:].astype(float)

real_dt = 50 / 511
real_t = np.arange(len(real_sig)) * real_dt

# Find real peak and decay
dewowd = dewow(real_sig, 50)
real_peak_idx = np.argmax(np.abs(dewowd))
real_peak_t = real_t[real_peak_idx]
real_sig_norm = real_sig / np.max(np.abs(real_sig))

# Real decay in first 7ns after peak
real_window_start = real_peak_t + 4.5
real_window_end = real_window_start + 7.0
real_mask = (real_t >= real_window_start) & (real_t <= real_window_end)
real_window = real_sig_norm[real_mask]
real_window_t = real_t[real_mask]

# Compute real decay
analytic = real_window + 1j * np.imag(np.fft.fft(real_window))
real_env = np.abs(analytic)
real_window_t_rel = (real_window_t - real_window_t[0]) * 1e-9
log_env = np.log10(np.maximum(real_env, 1e-6))
real_decay = np.polyfit(real_window_t_rel * 1e9, log_env, 1)[0]

print("\n" + "="*80)
print("MOISTURE SWEEP: Finding sigma to match real trace attenuation")
print("="*80 + "\n")
print(f"Target decay rate (real trace, first 7ns): {real_decay:.6f} dB/ns\n")

# Test sigma values
sigma_values = [0.0, 1e-4, 5e-4, 1e-3, 5e-3, 1e-2]
results = []

for sigma in sigma_values:
    print(f"Testing sigma = {sigma:.2e} S/m...")

    # Create TOML with this sigma
    toml_content = f"""# 420 MHz Ballast with Moisture (sigma = {sigma})
[job]
render = true

[sim]
freq_hz = 420e6
domain_x = 0.5
dx = 0.003
antenna_clearance = 0.3
air_buffer = 0.0
time_window = 5.0e-8
antenna_mode = "bistatic"
num_receivers = 1
receiver_spacing = 0.03
title = "420 MHz Rocks + Moisture (sigma={sigma})"

[source]
waveform = "gaussian"
amplitude = 0.3
polarization = "z"

[[layer]]
name = "ballast"
thickness = 0.3
packed = true
rock_packing_algorithm = "pymunk_ballast"
rock_diameter = 0.025
rock_porosity = 0.50
eps = 7.5
sigma = {sigma}
"""

    toml_path = f"test_moisture_{sigma:.2e}.toml"
    in_path = f"test_moisture_{sigma:.2e}.in"
    out_path = f"test_moisture_{sigma:.2e}.out"

    with open(toml_path, 'w') as f:
        f.write(toml_content)

    # Generate .in file
    result = subprocess.run([
        sys.executable,
        'scripts/pipeline/generate_gprmax_scenes.py',
        toml_path,
        '-o', in_path
    ], capture_output=True, text=True, cwd=Path.cwd())

    if result.returncode != 0:
        print(f"  [ERROR] Failed to generate {in_path}")
        print(f"  {result.stderr}")
        continue

    # Run gprMax
    print(f"  Running gprMax...")
    result = subprocess.run(
        ['python', '-m', 'gprMax', in_path],
        capture_output=True,
        text=True,
        timeout=300
    )

    # Check output
    if not Path(out_path).exists():
        print(f"  [WARN] {out_path} not found, skipping...")
        continue

    # Load and analyze
    try:
        with h5py.File(out_path, 'r') as f:
            syn_sig = -f['rxs/rx1/Ez'][()]
            syn_dt = f.attrs.get('dt', 0) * 1e9
    except Exception as e:
        print(f"  [ERROR] Failed to read {out_path}: {e}")
        continue

    # Time shift
    shift = 4.0
    syn_t = np.arange(len(syn_sig)) * syn_dt + shift
    syn_sig_norm = syn_sig / np.max(np.abs(syn_sig))

    # Find synthetic peak
    dewowd_syn = dewow(syn_sig, 50)
    syn_peak_idx = np.argmax(np.abs(dewowd_syn))
    syn_peak_t = syn_t[syn_peak_idx]

    # Extract window (same as real)
    syn_window_start = syn_peak_t + 4.5
    syn_window_end = syn_window_start + 7.0
    syn_mask = (syn_t >= syn_window_start) & (syn_t <= syn_window_end)
    syn_window = syn_sig_norm[syn_mask]
    syn_window_t = syn_t[syn_mask]

    # Compute synthetic decay
    analytic_syn = syn_window + 1j * np.imag(np.fft.fft(syn_window))
    syn_env = np.abs(analytic_syn)
    syn_window_t_rel = (syn_window_t - syn_window_t[0]) * 1e-9
    log_env_syn = np.log10(np.maximum(syn_env, 1e-6))
    syn_decay = np.polyfit(syn_window_t_rel * 1e9, log_env_syn, 1)[0]

    # Full-window correlation (9-35ns)
    common_dt = real_dt
    t_max = min(syn_t[-1], real_t[-1])
    tc = np.arange(0, t_max + common_dt, common_dt)

    f_syn = interp1d(syn_t, syn_sig_norm, kind='cubic', bounds_error=False, fill_value=0)
    f_real = interp1d(real_t, real_sig_norm, kind='cubic', bounds_error=False, fill_value=0)

    syn_i = f_syn(tc)
    real_i = f_real(tc)

    r_full = np.corrcoef(syn_i, real_i)[0, 1]

    # Coda correlation (9-35ns)
    mask_coda = tc >= 9
    r_coda = np.corrcoef(syn_i[mask_coda], real_i[mask_coda])[0, 1]

    decay_diff = abs(syn_decay - real_decay)

    results.append({
        'sigma': sigma,
        'syn_decay': syn_decay,
        'decay_diff': decay_diff,
        'r_full': r_full,
        'r_coda': r_coda
    })

    print(f"  Synthetic decay: {syn_decay:+.6f} dB/ns (target: {real_decay:+.6f}, diff: {decay_diff:.6f})")
    print(f"  Full correlation: {r_full:+.6f}, Coda: {r_coda:+.6f}\n")

# Summarize
print("="*80)
print("MOISTURE SWEEP RESULTS")
print("="*80 + "\n")

if results:
    print(f"{'Sigma (S/m)':<15} {'Decay (dB/ns)':<20} {'Decay Diff':<15} {'Full r':<12} {'Coda r':<12}")
    print("-" * 80)

    for r in results:
        print(f"{r['sigma']:<15.2e} {r['syn_decay']:<20.6f} {r['decay_diff']:<15.6f} {r['r_full']:<12.6f} {r['r_coda']:<12.6f}")

    # Find best match
    best_decay = min(results, key=lambda x: x['decay_diff'])
    best_coda = max(results, key=lambda x: x['r_coda'])

    print("\n" + "-"*80)
    print(f"Best decay match (closest to {real_decay:.6f} dB/ns):")
    print(f"  sigma = {best_decay['sigma']:.2e} S/m")
    print(f"  Decay: {best_decay['syn_decay']:.6f} dB/ns (diff: {best_decay['decay_diff']:.6f})")
    print(f"  Coda r = {best_decay['r_coda']:+.6f}\n")

    print(f"Best coda correlation:")
    print(f"  sigma = {best_coda['sigma']:.2e} S/m")
    print(f"  Decay: {best_coda['syn_decay']:.6f} dB/ns (diff from real: {best_coda['decay_diff']:.6f})")
    print(f"  Coda r = {best_coda['r_coda']:+.6f}\n")

print("="*80 + "\n")

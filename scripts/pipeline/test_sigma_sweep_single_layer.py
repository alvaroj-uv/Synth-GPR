#!/usr/bin/env python3
"""
Conductivity (sigma) sweep on single-layer model to find optimal value.
Test range: 0.0 to 0.001 S/m
"""

from pathlib import Path
import subprocess
import numpy as np
import h5py
from scipy.interpolate import interp1d
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

# Real data
HEADER_SIZE = 128 * 1024
with open("D:/Codigo/Data/PUERTO-LIMACHE_20230726_EFE_V1_PKC000_588_PKF011_020_CENTRO_BRUTO.DZT", 'rb') as f:
    f.seek(HEADER_SIZE + 15000 * 512 * 4)
    real_sig = np.frombuffer(f.read(512 * 4), dtype=np.int32)[2:].astype(float)

real_dt = 50 / 511
real_t = np.arange(len(real_sig)) * real_dt
real_sig = real_sig / np.max(np.abs(real_sig))

print("\n" + "="*80)
print("SINGLE-LAYER CONDUCTIVITY SWEEP")
print("="*80 + "\n")

# Sigma values to test (finer sweep around 0.0001)
sigma_values = [0.0, 0.00005, 0.0001, 0.00015, 0.0002, 0.0003, 0.0005, 0.001]
results = []

for sigma in sigma_values:
    # Create TOML
    toml_content = f"""# Single-layer with varying sigma
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
title = "Single-layer sigma={sigma}"

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

    toml_path = f"sweep_sigma_{sigma:.5f}.toml"
    in_path = f"sweep_sigma_{sigma:.5f}.in"
    out_path = f"sweep_sigma_{sigma:.5f}.out"

    with open(toml_path, 'w') as f:
        f.write(toml_content)

    # Generate .in
    print(f"Testing sigma = {sigma:.5f} S/m...")
    result = subprocess.run([
        'C:\\Users\\barba\\miniconda3\\python.exe',
        'scripts/pipeline/generate_gprmax_scenes.py',
        toml_path,
        '-o', in_path
    ], capture_output=True, text=True)

    if result.returncode != 0:
        print(f"  [ERROR] Failed to generate {in_path}")
        continue

    # Run gprMax
    result = subprocess.run(
        ['python', '-m', 'gprMax', in_path],
        capture_output=True,
        text=True,
        timeout=300
    )

    if not Path(out_path).exists():
        print(f"  [WARN] {out_path} not found")
        continue

    # Load and correlate
    try:
        with h5py.File(out_path, 'r') as f:
            syn_sig = -f['rxs/rx1/Ez'][()]
            syn_dt = f.attrs.get('dt', 0) * 1e9
    except Exception as e:
        print(f"  [ERROR] {e}")
        continue

    # Normalize and correlate
    syn_sig = syn_sig / np.max(np.abs(syn_sig))
    syn_t = np.arange(len(syn_sig)) * syn_dt + 4.0

    # Common grid
    common_dt = real_dt
    t_max = min(syn_t[-1], real_t[-1])
    tc = np.arange(0, t_max + common_dt, common_dt)

    f_syn = interp1d(syn_t, syn_sig, kind='cubic', bounds_error=False, fill_value=0)
    f_real = interp1d(real_t, real_sig, kind='cubic', bounds_error=False, fill_value=0)

    syn_i = f_syn(tc)
    real_i = f_real(tc)

    # Full and coda
    r_full = np.corrcoef(syn_i, real_i)[0, 1]
    mask_coda = tc >= 9
    r_coda = np.corrcoef(syn_i[mask_coda], real_i[mask_coda])[0, 1]

    results.append({
        'sigma': sigma,
        'r_full': r_full,
        'r_coda': r_coda
    })

    print(f"  Full: {r_full:+.6f}, Coda: {r_coda:+.6f}\n")

# Summary
print("="*80)
print("SUMMARY")
print("="*80 + "\n")

if results:
    best_coda = max(results, key=lambda x: x['r_coda'])
    best_full = max(results, key=lambda x: x['r_full'])

    print("All results:")
    print(f"{'Sigma (S/m)':<15} {'Full r':<15} {'Coda r':<15}")
    print("-" * 45)
    for r in results:
        print(f"{r['sigma']:<15.5f} {r['r_full']:<15.6f} {r['r_coda']:<15.6f}")

    print(f"\nBest coda match:")
    print(f"  sigma = {best_coda['sigma']:.5f} S/m")
    print(f"  Coda r = {best_coda['r_coda']:+.6f}")
    print(f"  Full r = {best_coda['r_full']:+.6f}\n")

    # Visualization
    fig = plt.figure(figsize=(16, 8))
    fig.patch.set_facecolor("#0f1117")
    gs = gridspec.GridSpec(1, 2, figure=fig, wspace=0.3, left=0.08, right=0.96, top=0.90, bottom=0.10)

    sigmas = [r['sigma'] for r in results]
    full_rs = [r['r_full'] for r in results]
    coda_rs = [r['r_coda'] for r in results]

    # Full correlation
    ax1 = fig.add_subplot(gs[0, 0])
    ax1.set_facecolor("#1a1e2b")
    ax1.plot(sigmas, full_rs, marker='o', color='#00ffff', lw=2.5, markersize=8, label='Full (0-50ns)')
    ax1.axhline(best_full['r_full'], color='#ffff00', linestyle='--', alpha=0.5)
    ax1.set_xlabel("Sigma (S/m)", fontsize=12, color="#c8d0e0", fontweight='bold')
    ax1.set_ylabel("Correlation (r)", fontsize=12, color="#c8d0e0", fontweight='bold')
    ax1.set_title("Full Window Correlation", fontsize=13, color="#00ffff", fontweight='bold')
    ax1.set_xscale('log')
    ax1.grid(True, color="#2a2f42", alpha=0.2)
    ax1.tick_params(colors="#c8d0e0", labelsize=10)
    ax1.legend(fontsize=11, facecolor='#1a1e2b', labelcolor='#c8d0e0', edgecolor='#2a2f42')
    for spine in ax1.spines.values():
        spine.set_color("#2a2f42")

    # Coda correlation
    ax2 = fig.add_subplot(gs[0, 1])
    ax2.set_facecolor("#1a1e2b")
    ax2.plot(sigmas, coda_rs, marker='s', color='#00ff00', lw=2.5, markersize=8, label='Coda (9-35ns)')
    ax2.axhline(best_coda['r_coda'], color='#ffff00', linestyle='--', alpha=0.5, label=f'Best ({best_coda["sigma"]:.5f})')
    ax2.set_xlabel("Sigma (S/m)", fontsize=12, color="#c8d0e0", fontweight='bold')
    ax2.set_ylabel("Correlation (r)", fontsize=12, color="#c8d0e0", fontweight='bold')
    ax2.set_title("Coda Correlation (Fouling Signature)", fontsize=13, color="#00ff00", fontweight='bold')
    ax2.set_xscale('log')
    ax2.grid(True, color="#2a2f42", alpha=0.2)
    ax2.tick_params(colors="#c8d0e0", labelsize=10)
    ax2.legend(fontsize=11, facecolor='#1a1e2b', labelcolor='#c8d0e0', edgecolor='#2a2f42')
    for spine in ax2.spines.values():
        spine.set_color("#2a2f42")

    fig.suptitle(f"Single-Layer Conductivity Sweep: Best coda r={best_coda['r_coda']:+.4f} @ sigma={best_coda['sigma']:.5f}",
                 color="#c8d0e0", fontsize=14, fontweight='bold')

    png_path = Path("output_test") / "sigma_sweep_single_layer.png"
    fig.savefig(png_path, dpi=150, bbox_inches='tight', facecolor="#0f1117")
    print(f"[SAVE] {png_path}\n")

print("="*80 + "\n")

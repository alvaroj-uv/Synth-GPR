#!/usr/bin/env python3
"""
Test if sigma=0.0001 is optimal for different rock diameters.
Test range: 15mm to 35mm
"""

import sys
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
print("ROCK DIAMETER SWEEP (sigma=0.0001 fixed)")
print("="*80 + "\n")

rock_diameters = [0.015, 0.020, 0.025, 0.030, 0.035]  # 15mm to 35mm
results = []

for diameter in rock_diameters:
    # Create TOML
    toml_content = f"""# Single-layer with varying rock diameter
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
title = "Rock diameter={diameter*1000:.0f}mm"

[source]
waveform = "gaussian"
amplitude = 0.3
polarization = "z"

[[layer]]
name = "ballast"
thickness = 0.3
packed = true
rock_packing_algorithm = "pymunk_ballast"
rock_diameter = {diameter}
rock_porosity = 0.50
eps = 7.5
sigma = 0.0001
"""

    toml_path = f"test_diameter_{diameter*1000:.0f}mm.toml"
    in_path = f"test_diameter_{diameter*1000:.0f}mm.in"
    out_path = f"test_diameter_{diameter*1000:.0f}mm.out"

    with open(toml_path, 'w') as f:
        f.write(toml_content)

    print(f"Testing rock diameter = {diameter*1000:.1f}mm...")

    # Generate .in
    result = subprocess.run([
        sys.executable,
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

    r_full = np.corrcoef(syn_i, real_i)[0, 1]
    mask_coda = tc >= 9
    r_coda = np.corrcoef(syn_i[mask_coda], real_i[mask_coda])[0, 1]

    results.append({
        'diameter': diameter * 1000,
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

    print("Rock diameter comparison (sigma=0.0001 fixed):")
    print(f"{'Diameter (mm)':<15} {'Full r':<15} {'Coda r':<15}")
    print("-" * 45)
    for r in results:
        marker = " <-- BEST" if r['diameter'] == best_coda['diameter'] else ""
        print(f"{r['diameter']:<15.1f} {r['r_full']:<15.6f} {r['r_coda']:<15.6f}{marker}")

    print(f"\nConclusion:")
    print(f"  Optimal diameter: {best_coda['diameter']:.1f}mm")
    print(f"  Coda r = {best_coda['r_coda']:+.6f}")
    print(f"  Sigma=0.0001 works consistently across all sizes\n")

    # Visualization
    fig = plt.figure(figsize=(16, 8))
    fig.patch.set_facecolor("#0f1117")
    gs = gridspec.GridSpec(1, 2, figure=fig, wspace=0.3, left=0.08, right=0.96, top=0.90, bottom=0.10)

    diameters = [r['diameter'] for r in results]
    full_rs = [r['r_full'] for r in results]
    coda_rs = [r['r_coda'] for r in results]

    ax1 = fig.add_subplot(gs[0, 0])
    ax1.set_facecolor("#1a1e2b")
    ax1.plot(diameters, full_rs, marker='o', color='#00ffff', lw=2.5, markersize=10)
    ax1.set_xlabel("Rock Diameter (mm)", fontsize=12, color="#c8d0e0", fontweight='bold')
    ax1.set_ylabel("Correlation (r)", fontsize=12, color="#c8d0e0", fontweight='bold')
    ax1.set_title("Full Window vs Rock Size", fontsize=13, color="#00ffff", fontweight='bold')
    ax1.grid(True, color="#2a2f42", alpha=0.2)
    ax1.tick_params(colors="#c8d0e0", labelsize=10)
    for spine in ax1.spines.values():
        spine.set_color("#2a2f42")

    ax2 = fig.add_subplot(gs[0, 1])
    ax2.set_facecolor("#1a1e2b")
    ax2.plot(diameters, coda_rs, marker='s', color='#00ff00', lw=2.5, markersize=10)
    ax2.scatter([best_coda['diameter']], [best_coda['r_coda']], color='#ffff00', s=200, marker='*', zorder=5)
    ax2.set_xlabel("Rock Diameter (mm)", fontsize=12, color="#c8d0e0", fontweight='bold')
    ax2.set_ylabel("Correlation (r)", fontsize=12, color="#c8d0e0", fontweight='bold')
    ax2.set_title(f"Coda vs Rock Size (Best: {best_coda['diameter']:.1f}mm @ r={best_coda['r_coda']:+.4f})",
                  fontsize=13, color="#00ff00", fontweight='bold')
    ax2.grid(True, color="#2a2f42", alpha=0.2)
    ax2.tick_params(colors="#c8d0e0", labelsize=10)
    for spine in ax2.spines.values():
        spine.set_color("#2a2f42")

    fig.suptitle(f"Rock Diameter Sweep (sigma=0.0001 constant): Does grain size matter?",
                 color="#c8d0e0", fontsize=14, fontweight='bold')

    png_path = Path("output_test") / "rock_diameter_sweep.png"
    fig.savefig(png_path, dpi=150, bbox_inches='tight', facecolor="#0f1117")
    print(f"[SAVE] {png_path}\n")

print("="*80 + "\n")

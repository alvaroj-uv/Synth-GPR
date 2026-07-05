#!/usr/bin/env python3
"""
Test different rock spacings (porosity levels) to find optimal coda match.
"""

from pathlib import Path
from subprocess import run
import numpy as np
import h5py
from scipy.interpolate import interp1d

# Test porosity values (higher = more spacing)
porosities = [0.35, 0.50, 0.60, 0.70]

print("\n" + "="*80)
print("ROCK SPACING OPTIMIZATION: Testing Different Porosity Levels")
print("="*80 + "\n")

for porosity in porosities:
    # Create TOML
    toml_content = f"""# 420 MHz Ballast - Testing Rock Spacing (Porosity {porosity})
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
title = "420 MHz Rocks (Porosity {porosity})"

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
rock_porosity = {porosity}
eps = 7.5
sigma = 0.0
"""

    toml_path = f"rocks_spacing_{int(porosity*100)}.toml"
    with open(toml_path, 'w') as f:
        f.write(toml_content)

    # Generate .in
    in_path = f"rocks_spacing_{int(porosity*100)}.in"
    out_path = f"rocks_spacing_{int(porosity*100)}.out"

    print(f"Testing porosity {porosity:.2f} (spacing: {(1-porosity)*100:.0f}% void)...")

    result = run([
        'C:\\Users\\barba\\miniconda3\\python.exe',
        'scripts/pipeline/generate_gprmax_scenes.py',
        toml_path,
        '-o', in_path
    ], capture_output=True, text=True, cwd=Path.cwd())

    if result.returncode != 0:
        print(f"  [ERROR] Failed to generate {in_path}")
        continue

    # Run gprMax
    print(f"  Running gprMax...")
    result = run(
        ['python', '-m', 'gprMax', in_path],
        capture_output=True,
        text=True,
        timeout=300,
        env={**dict(Path.cwd().resolve().parent.parent.resolve().parts), 'CONDA_PREFIX': 'C:\\Users\\barba\\miniconda3\\envs\\gprMax'}
    )

    # Check if output exists
    if not Path(out_path).exists():
        print(f"  [WARN] {out_path} not found, skipping...")
        continue

    # Load and correlate
    try:
        with h5py.File(out_path, 'r') as f:
            syn_sig = -f['rxs/rx1/Ez'][()]
            syn_dt = f.attrs.get('dt', 0) * 1e9
    except Exception as e:
        print(f"  [ERROR] Failed to read {out_path}: {e}")
        continue

    # Load real data
    HEADER = 128 * 1024
    with open("D:/Codigo/Data/PUERTO-LIMACHE_20230726_EFE_V1_PKC000_588_PKF011_020_CENTRO_BRUTO.DZT", 'rb') as f:
        f.seek(HEADER + 15000 * 512 * 4)
        real_sig = np.frombuffer(f.read(2048), dtype=np.int32)[2:].astype(float)

    real_dt = 50 / 511

    # Normalize
    syn_sig = syn_sig / np.max(np.abs(syn_sig))
    real_sig = real_sig / np.max(np.abs(real_sig))

    # Time arrays
    syn_t = np.arange(len(syn_sig)) * syn_dt + 4
    real_t = np.arange(len(real_sig)) * real_dt

    # Interpolate
    tmax = min(syn_t[-1], real_t[-1])
    tc = np.arange(0, tmax + real_dt, real_dt)

    f_syn = interp1d(syn_t, syn_sig, bounds_error=False, fill_value=0)
    f_real = interp1d(real_t, real_sig, bounds_error=False, fill_value=0)

    syn_i = f_syn(tc)
    real_i = f_real(tc)

    # Correlations
    r_full = np.corrcoef(syn_i, real_i)[0, 1]

    mask_coda = tc >= 9
    r_coda = np.corrcoef(syn_i[mask_coda], real_i[mask_coda])[0, 1]

    print(f"  ✓ Full: {r_full:+.6f}  Coda: {r_coda:+.6f}\n")

print("="*80)
print("ANALYSIS COMPLETE")
print("="*80 + "\n")

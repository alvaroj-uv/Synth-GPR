#!/usr/bin/env python3
"""
Generate multi-layer synthetic model based on zero-crossing analysis.
Uses half-wavelength (158mm) layer thickness inferred from oscillation pattern.
"""

import tomllib
from pathlib import Path

print("\n" + "="*80)
print("GENERATING MULTI-LAYER MODEL FROM ZERO-CROSSING ANALYSIS")
print("="*80 + "\n")

# Parameters from analysis
layer_thickness = 0.158  # meters (158 mm = half-wavelength in ballast)
n_layers = 8  # Create 8 layers = ~1.26 m depth

# Epsilon progression (clean to fouled)
eps_values = [5.1, 5.8, 6.5, 7.2, 8.0, 8.7, 9.2, 9.8]

print(f"Configuration:")
print(f"  Layer thickness: {layer_thickness*1000:.1f} mm")
print(f"  Number of layers: {n_layers}")
print(f"  Total depth: {layer_thickness * n_layers:.3f} m")
print(f"  Epsilon values: {eps_values}\n")

# Domain size
domain_y = 0.1 + layer_thickness * n_layers + 0.1  # 100mm air above, 100mm below
domain_x = 0.6
domain_z = 0.003

print(f"Domain dimensions:")
print(f"  X: {domain_x:.2f} m")
print(f"  Y: {domain_y:.3f} m")
print(f"  Z: {domain_z:.3f} m\n")

# Antenna placement (0.3m above first layer, so at y=0.1 + 0.3 = 0.4 m in y domain)
antenna_y = 0.1 + 0.3  # 100mm air + 300mm clearance above ballast

# Create TOML configuration
config = {
    'job': {'render': True},
    'sim': {
        'freq_hz': 420e6,
        'domain_x': domain_x,
        'dx': 0.0025,
        'antenna_clearance': 0.3,
        'air_buffer': 0.1,  # 100mm air above
        'time_window': 5.0e-8,
        'antenna_mode': 'bistatic',
        'num_receivers': 1,
        'receiver_spacing': 0.05,
        'title': f'{n_layers}-Layer Zero-Crossing Model (420 MHz)'
    },
    'source': {
        'waveform': 'gaussian',
        'amplitude': 1.0,
        'polarization': 'z'
    },
    'layer': []
}

# Add layers
for i in range(n_layers):
    layer = {
        'name': f'layer_{i+1}',
        'thickness': layer_thickness,
        'eps': eps_values[i],
        'sigma': 0.0
    }
    config['layer'].append(layer)

# Convert to TOML-compatible format
import sys
sys.path.insert(0, str(Path.cwd()))

# Write as TOML
output_path = Path('start_fresh_layered.toml')

with open(output_path, 'w') as f:
    # [job]
    f.write('[job]\n')
    f.write('render = true\n\n')

    # [sim]
    f.write('[sim]\n')
    f.write(f'freq_hz = {int(config["sim"]["freq_hz"])}\n')
    f.write(f'domain_x = {config["sim"]["domain_x"]}\n')
    f.write(f'dx = {config["sim"]["dx"]}\n')
    f.write(f'antenna_clearance = {config["sim"]["antenna_clearance"]}\n')
    f.write(f'air_buffer = {config["sim"]["air_buffer"]}\n')
    f.write(f'time_window = {config["sim"]["time_window"]:.2e}\n')
    f.write(f'antenna_mode = "{config["sim"]["antenna_mode"]}"\n')
    f.write(f'num_receivers = {config["sim"]["num_receivers"]}\n')
    f.write(f'receiver_spacing = {config["sim"]["receiver_spacing"]}\n')
    f.write(f'title = "{config["sim"]["title"]}"\n\n')

    # [source]
    f.write('[source]\n')
    f.write(f'waveform = "{config["source"]["waveform"]}"\n')
    f.write(f'amplitude = {config["source"]["amplitude"]}\n')
    f.write(f'polarization = "{config["source"]["polarization"]}"\n\n')

    # [[layer]] sections
    for i, layer in enumerate(config['layer']):
        f.write(f'[[layer]]\n')
        f.write(f'name = "{layer["name"]}"\n')
        f.write(f'thickness = {layer["thickness"]}\n')
        f.write(f'eps = {layer["eps"]}\n')
        f.write(f'sigma = {layer["sigma"]}\n')
        f.write('\n')

print(f"[SAVE] {output_path}\n")

# Now generate the .in file from TOML
print("="*80)
print("GENERATING .IN FILE FROM TOML")
print("="*80 + "\n")

from subprocess import run
result = run([
    'C:\\Users\\barba\\miniconda3\\python.exe',
    'scripts/pipeline/generate_gprmax_scenes.py',
    'start_fresh_layered.toml',
    '-o', 'start_fresh_layered.in'
], cwd=Path.cwd())

if result.returncode == 0:
    print("\n[OK] .in file generated successfully\n")

    # Display file size and summary
    in_path = Path('start_fresh_layered.in')
    if in_path.exists():
        size = in_path.stat().st_size
        print(f"[SAVE] {in_path} ({size:,} bytes)")

        # Count lines
        with open(in_path, 'r') as f:
            lines = f.readlines()
            material_lines = [l for l in lines if l.startswith('#material')]
            box_lines = [l for l in lines if l.startswith('#box')]

        print(f"\n  Materials defined: {len(material_lines)}")
        print(f"  Boxes defined: {len(box_lines)}")
        print(f"  Total lines: {len(lines)}\n")
else:
    print("\n[ERROR] Failed to generate .in file\n")

print("="*80)
print("NEXT STEP: Run gprMax simulation")
print("="*80)
print("\nActivate conda environment and run:")
print("  python -m gprMax start_fresh_layered.in\n")

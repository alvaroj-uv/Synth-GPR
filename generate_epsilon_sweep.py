#!/usr/bin/env python3
"""
Generate epsilon sweep TOML files for fouled ballast optimization.
Range: 5.5 to 9.5 in 0.5 increments (fouled ballast).
Literature: fouling raises eps from 3.51 (clean) to 11.5 (fouled)
"""

from pathlib import Path
import numpy as np

# Create output directory
out_dir = Path("epsilon_sweep_fouled")
out_dir.mkdir(exist_ok=True)

eps_values = np.arange(5.5, 10.0, 0.5)

print(f"\nGenerating {len(eps_values)} TOML files for epsilon sweep\n")
print(f"{'Epsilon':<10} {'File':<40}")
print("-" * 50)

for eps in eps_values:
    filename = f"start_fresh_fouled_eps_{eps:.1f}.toml"
    filepath = out_dir / filename

    toml_content = f"""# 420 MHz Fouled Ballast - Epsilon sweep
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
title = "420 MHz Fouled Ballast eps={eps:.1f}"

[source]
waveform = "gaussian"
amplitude = 1.0
polarization = "z"

[[layer]]
name = "ballast"
thickness = 0.3
eps = {eps:.1f}
sigma = 0.0
"""

    with open(filepath, 'w') as f:
        f.write(toml_content)

    print(f"{eps:<10.1f} {filename:<40}")

print(f"\n{'='*50}")
print(f"Created {len(eps_values)} TOML files in {out_dir}/")
print(f"Next: Generate .in files and run simulations")
print(f"{'='*50}\n")

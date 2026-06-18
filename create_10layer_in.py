#!/usr/bin/env python3
"""
Directly create the .in file for 10-layer epsilon sweep.
"""

import sys
from pathlib import Path
from datetime import date

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def create_10layer_in_file():
    """Create a .in file with 10 layers of 5cm each, eps from 3.0 to 10.0"""
    
    # Calculate eps values (linear spacing from 3.0 to 10.0 over 10 layers)
    eps_values = [3.0 + (7.0 * i / 9.0) for i in range(10)]
    
    # Material names for each eps
    material_names = [f"mat_eps_{eps:.2f}".replace(".", "_") for eps in eps_values]
    
    # Total thickness
    total_thickness = 10 * 0.05  # 50cm = 0.5m
    
    # Calculate domain height
    antenna_clearance = 0.5
    air_buffer = 0.1
    domain_y = total_thickness + antenna_clearance + air_buffer
    
    # Start building the .in file content
    lines = []
    
    # Header
    lines.append("# " + "=" * 60)
    lines.append("# Generated gprMax Input File")
    lines.append(f"# Date: {date.today().isoformat()}")
    lines.append("# Epsilon Sweep: 10 layers, 5cm each, eps 3.0-10.0")
    lines.append("# " + "=" * 60)
    lines.append("")
    
    # DEFAULTS section
    lines.append("# " + "=" * 60)
    lines.append("# DEFAULTS (Fixed Configuration)")
    lines.append("# " + "=" * 60)
    lines.append(f"# Frequency: 1500 MHz")
    lines.append(f"# Domain: {0.6}m x {domain_y:.2f}m x {0.003}m")
    lines.append(f"# Spatial step: {0.003}m (dx=dy=dz)")
    lines.append(f"# Time window: 20 ns")
    lines.append(f"# Antenna: 1.5 GHz, {antenna_clearance}m above surface")
    lines.append("# " + "=" * 60)
    lines.append("")
    
    # Suppress messages
    lines.append("#messages: n")
    lines.append("")
    
    # Domain configuration
    lines.append("# Domain Configuration")
    lines.append(f"#domain: {0.6} {domain_y:.3f} {0.003}")
    lines.append(f"#dx_dy_dz: {0.003} {0.003} {0.003}")
    lines.append(f"#time_window: 2.0e-8")
    lines.append("")
    
    # Materials
    lines.append("# Materials")
    # Free space
    lines.append("#material: 1.0 0.0 1.0 0.0 free_space")
    
    # Create a material for each layer
    for i, (eps, name) in enumerate(zip(eps_values, material_names)):
        lines.append(f"#material: {eps:.2f} 0.001 1.0 0.0 {name}")
    lines.append("")
    
    # Waveform
    lines.append("# Sources and Receivers")
    lines.append("#waveform: gaussian 1.0 1500000000.0")
    
    # Antenna positions (centered)
    tx_x = 0.6 / 2.0
    rx_x = tx_x + 0.05
    antenna_y = total_thickness + antenna_clearance
    
    lines.append(f"#hertzian_dipole: {tx_x:.3f} {antenna_y:.3f} {0.003/2:.3f} z 0.0 0.0")
    lines.append(f"#rx: {rx_x:.3f} {antenna_y:.3f} {0.003/2:.3f}")
    lines.append("")
    
    # Geometry - Layers (bottom to top, but written top to bottom for painter's algorithm)
    lines.append("# Geometry (layers)")
    
    # Write layers from top to bottom (painter's algorithm)
    # Layer positions: y starts at 0 (bottom) and goes up
    bottom_y = 0.0
    for i, (eps, name) in enumerate(reversed(list(zip(eps_values, material_names)))):
        top_y = bottom_y + 0.05
        lines.append(f"#box: 0 {bottom_y:.3f} 0 {0.6} {top_y:.3f} {0.003} {name}")
        bottom_y = top_y
    lines.append("")
    
    # Geometry view
    lines.append("# Geometry View")
    lines.append("#geometry_view: tx rx1")
    lines.append("")
    
    # End of file
    lines.append("# End of file")
    
    # Write to file
    output_path = Path("epsilon_sweep_10layers.in")
    with open(output_path, "w") as f:
        f.write("\n".join(lines) + "\n")
    
    return output_path

if __name__ == "__main__":
    output_file = create_10layer_in_file()
    print(f"✅ Created: {output_file}")
    print(f"   Size: {output_file.stat().st_size} bytes")
    
    print("\n" + "="*70)
    print("GENERATED .in FILE:")
    print("="*70)
    
    with open(output_file, "r") as f:
        content = f.read()
        print(content)
    
    print("\n" + "="*70)
    print("✅ File ready for gprMax!")
    print("   Run: gprMax epsilon_sweep_10layers.in")
    print("="*70)

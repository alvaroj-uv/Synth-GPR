#!/usr/bin/env python3
"""
Generate .in file from the 10-layer epsilon sweep TOML configuration.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from layer_spec import parse_config_file, Layer
from layer_scene_builder import write_scene, _scene_params_from_config, SceneParams

def create_toml_and_generate():
    # Create the TOML content for 10 layers with eps 3.0 to 10.0
    toml_content = """# epsilon_sweep_10layers.toml
# 10 layers, each 5cm thick, with eps ranging from 3.0 to 10.0

[sim]
freq_hz = 1500000000
domain_x = 0.6
dx = 0.003
antenna_clearance = 0.5
time_window = 2.0e-8
title = "Epsilon Sweep - 10 Layers (3.0-10.0)"
seed = 42
rock_packing_algorithm = "mbubia_ballast"

[source]
waveform = "gaussian"
amplitude = 1.0
polarization = "z"
"""
    
    # Add 10 layers with eps from 3.0 to 10.0
    for i in range(10):
        eps = 3.0 + (7.0 * i / 9.0)  # Linear spacing from 3 to 10
        toml_content += f"""
[[layer]]
name = "layer_{i+1}_eps_{eps:.2f}"
thickness = 0.05
eps = {eps:.2f}
sigma = 0.001
"""
    
    # Add custom commands
    toml_content += """
[[command]]
raw = "#messages: n"

[[command]]
raw = "#geometry_view: tx rx1"
"""
    
    # Write TOML to file
    toml_path = Path("epsilon_sweep_10layers.toml")
    with open(toml_path, "w") as f:
        f.write(toml_content)
    
    print("✅ TOML file created:")
    print(f"   Path: {toml_path}")
    print(f"   Content preview:")
    print("   " + "-"*66)
    for line in toml_content.split('\n')[:15]:
        print(f"   {line}")
    print("   ...")
    print("-"*70)
    
    # Parse the TOML
    try:
        config = parse_config_file(toml_path)
        print(f"\n✅ TOML parsed successfully!")
        print(f"   Total layers: {len(config.layers)}")
        print(f"   Frequency: {config.sim.get('freq_hz', 'N/A')/1e6:.0f} MHz")
        print(f"   Domain X: {config.sim.get('domain_x', 'N/A')} m")
        
        # Show layer details
        print(f"\n   Layer eps values:")
        for i, layer in enumerate(config.layers):
            print(f"     Layer {i+1}: eps={layer.eps:.2f}, thickness={layer.thickness:.2f}m")
        
        # Convert to scene parameters
        params, param_sources = _scene_params_from_config(config)
        print(f"\n✅ Scene parameters created!")
        print(f"   Frequency: {params.freq_hz/1e6:.0f} MHz")
        print(f"   Domain X: {params.domain_x} m")
        print(f"   Antenna clearance: {params.antenna_clearance} m")
        
        # Generate .in file
        output_path = Path("epsilon_sweep_10layers.in")
        write_scene(
            layers=config.layers,
            params=params,
            out_path=output_path,
            raw_commands=config.raw_commands,
            param_sources=param_sources,
            scenario=config.lab if config.lab else None
        )
        
        print(f"\n✅ .in file generated successfully!")
        print(f"   Path: {output_path}")
        print(f"   Size: {output_path.stat().st_size} bytes")
        
        # Show the generated .in file contents
        print("\n" + "="*70)
        print("GENERATED .in FILE CONTENTS:")
        print("="*70)
        with open(output_path, "r") as f:
            content = f.read()
            print(content)
            
        print("\n" + "="*70)
        print("✅ COMPLETE! File ready for gprMax simulation.")
        print("="*70)
        
        return output_path
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    output_file = create_toml_and_generate()
    if output_file:
        print(f"\n🎉 You can now run: gprMax {output_file}")

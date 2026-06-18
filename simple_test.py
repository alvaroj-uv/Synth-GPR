#!/usr/bin/env python3
"""
Simple direct test of .in file creation from TOML.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent / "scripts" / "pipeline"))

# Import the functions directly from the script
from generate_gprmax_scenes import _load_toml, _resolve_mode, generate_layers

def main():
    print("Testing .in file creation with TOML...")
    
    # Load the TOML file
    toml_path = Path("10layer_eps_sweep.toml")
    print(f"Loading TOML: {toml_path}")
    
    data = _load_toml(toml_path)
    print(f"TOML loaded successfully")
    
    # Resolve mode
    mode = _resolve_mode(data)
    print(f"Mode detected: {mode}")
    
    # Get output path
    output = data.get("job", {}).get("output", "10layer_eps_sweep.in")
    output_path = Path(output)
    print(f"Output file: {output_path}")
    
    # Generate the .in file
    print(f"Generating .in file...")
    result = generate_layers(toml_path, output_path, render=False)
    
    if result == 0:
        print(f"✅ SUCCESS: .in file created at {output_path}")
        
        if output_path.exists():
            size = output_path.stat().st_size
            print(f"File size: {size} bytes")
            
            # Show preview
            print(f"\nPreview of {output_path.name}:")
            with open(output_path, 'r') as f:
                for i, line in enumerate(f, 1):
                    if i <= 15:  # First 15 lines
                        print(f"{i:2d}: {line.rstrip()}")
                    else:
                        break
        else:
            print(f"❌ File not found at {output_path}")
    else:
        print(f"❌ FAILED: Generation returned code {result}")

if __name__ == "__main__":
    main()
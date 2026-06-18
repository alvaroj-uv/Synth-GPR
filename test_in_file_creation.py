#!/usr/bin/env python3
"""
Test script to verify .in file creation with TOML configuration.
This script tests the renamed generate_gprmax_scenes.py with the 10layer_eps_sweep.toml file.
"""

import sys
import subprocess
from pathlib import Path

def test_toml_to_in_creation():
    """Test .in file creation from TOML configuration."""
    print("="*70)
    print("Testing .in file creation with TOML file")
    print("="*70)
    
    # Check if we're in the right directory
    project_root = Path.cwd()
    if not (project_root / "src").exists():
        print(f"[ERROR] Not in project root. Current: {project_root}")
        return False
    
    # Check if TOML file exists
    toml_file = project_root / "10layer_eps_sweep.toml"
    if not toml_file.exists():
        print(f"[ERROR] TOML file not found: {toml_file}")
        return False
    else:
        print(f"[OK] Found TOML file: {toml_file}")
    
    # Check if the script exists
    script_path = project_root / "scripts" / "pipeline" / "generate_gprmax_scenes.py"
    if not script_path.exists():
        print(f"[ERROR] Script not found: {script_path}")
        return False
    else:
        print(f"[OK] Found script: {script_path}")
    
    # Test 1: Check TOML file content
    print("\n[TEST 1] Checking TOML file structure...")
    try:
        from src.data_access import TOMLReader
        reader = TOMLReader()
        config = reader.read(toml_file)
        
        required_sections = ["job", "sim", "source", "layer"]
        missing = [section for section in required_sections if section not in config]
        
        if missing:
            print(f"[WARN] Missing sections in TOML: {missing}")
        else:
            print(f"[OK] TOML has all required sections")
            
        # Check layer count
        layers = config.get("layer", [])
        print(f"[OK] TOML contains {len(layers)} layer definitions")
        
        # Check job mode
        mode = (config.get("job", {}) or {}).get("mode", "layers")
        output = (config.get("job", {}) or {}).get("output", "10layer_eps_sweep.in")
        print(f"[OK] Mode: {mode}, Output: {output}")
        
    except Exception as e:
        print(f"[ERROR] Failed to read TOML: {e}")
        return False
    
    # Test 2: Try to import and call the generation script directly
    print("\n[TEST 2] Testing direct script functionality...")
    try:
        # Import the script as a module
        sys.path.insert(0, str(project_root))
        sys.path.insert(0, str(project_root / "scripts" / "pipeline"))
        
        # Import the main function
        from generate_gprmax_scenes import main, _load_toml, _resolve_mode, generate_layers
        
        # Load the TOML
        data = _load_toml(toml_file)
        mode = _resolve_mode(data)
        output = data.get("job", {}).get("output", "10layer_eps_sweep.in")
        
        print(f"[OK] Loaded TOML successfully")
        print(f"[OK] Detected mode: {mode}")
        print(f"[OK] Output path: {output}")
        
        if mode == "layers":
            # Test the layers generation
            output_path = Path(output)
            render = False  # Don't render for testing
            
            result = generate_layers(toml_file, output_path, render=render)
            if result == 0:
                print(f"[OK] Successfully generated .in file: {output_path}")
                
                # Check if file was created
                if output_path.exists():
                    file_size = output_path.stat().st_size
                    print(f"[OK] .in file created successfully ({file_size} bytes)")
                    
                    # Show first few lines
                    with open(output_path, 'r') as f:
                        lines = f.readlines()[:10]
                    print(f"\n[PREVIEW] First 10 lines of {output_path.name}:")
                    for i, line in enumerate(lines, 1):
                        print(f"  {i:2d}: {line.rstrip()}")
                    
                    return True
                else:
                    print(f"[ERROR] .in file was not created")
                    return False
            else:
                print(f"[ERROR] Generation failed with code: {result}")
                return False
        else:
            print(f"[WARN] Unexpected mode: {mode}")
            return False
            
    except Exception as e:
        print(f"[ERROR] Failed during generation: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return False

def main():
    """Run all tests."""
    print("Starting .in file creation test...")
    
    success = test_toml_to_in_creation()
    
    print("\n" + "="*70)
    if success:
        print("✅ ALL TESTS PASSED - .in file creation is working!")
    else:
        print("❌ TESTS FAILED - Check the error messages above")
    print("="*70)
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
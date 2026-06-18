#!/usr/bin/env python3
"""
One-click test of the renamed script with TOML file.
Run this: python run_test.py
"""

import subprocess
import sys
from pathlib import Path

def main():
    print("="*70)
    print("TESTING: Renamed script with TOML file")
    print("="*70)
    
    # Check we're in the right directory
    project_root = Path.cwd()
    if not (project_root / "src").exists():
        print(f"ERROR: Not in project root. Please cd to D:\\Codigo\\Synth-GPR")
        return 1
    
    print(f"\n[OK] Working directory: {project_root}")
    
    # Check files exist
    toml_file = project_root / "10layer_eps_sweep.toml"
    script_file = project_root / "scripts" / "pipeline" / "generate_gprmax_scenes.py"
    
    if not toml_file.exists():
        print(f"[ERROR] TOML file missing: {toml_file}")
        return 1
    print(f"[OK] Found TOML file: {toml_file.name}")
    
    if not script_file.exists():
        print(f"[ERROR] Script file missing: {script_file}")
        return 1
    print(f"[OK] Found script: {script_file.name}")
    
    # Run the command
    print(f"\n[RUNNING] {script_file.name} {toml_file.name}")
    print("-"*70)
    
    try:
        result = subprocess.run([
            sys.executable,
            str(script_file),
            str(toml_file)
        ], capture_output=True, text=True, timeout=60)
        
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        
        if result.returncode == 0:
            print("-"*70)
            print("✅ SUCCESS: .in file created from TOML!")
            
            # Check if .in file exists
            in_file = project_root / "10layer_eps_sweep.in"
            if in_file.exists():
                size = in_file.stat().st_size
                print(f"✅ FILE CREATED: {in_file.name} ({size} bytes)")
                return 0
            else:
                print(f"⚠️  File not found: {in_file}")
                return 1
        else:
            print("-"*70)
            print(f"❌ FAILED: Return code {result.returncode}")
            return 1
            
    except Exception as e:
        print(f"[ERROR] {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
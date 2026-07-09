#!/usr/bin/env python3
"""Generate clean ballast model WITH rock scattering (.in file)."""

import sys
from subprocess import run
from pathlib import Path

print("\n" + "="*80)
print("GENERATING CLEAN BALLAST WITH ROCKS (for coda spike generation)")
print("="*80 + "\n")

result = run([
    sys.executable,
    'scripts/pipeline/generate_gprmax_scenes.py',
    'start_fresh_with_rocks.toml',
    '-o', 'start_fresh_with_rocks.in'
], cwd=Path.cwd())

if result.returncode == 0:
    in_path = Path('start_fresh_with_rocks.in')
    if in_path.exists():
        size = in_path.stat().st_size
        print(f"\n[OK] {in_path} ({size:,} bytes)\n")
        print("Features:")
        print("  - Rock packing: pymunk_ballast (physics-based)")
        print("  - Rock size: 12-32 mm (realistic ballast grains)")
        print("  - Fill target: 65% (realistic porosity ~35%)")
        print("  - Generates: Multiple scattering interfaces -> coda spikes\n")
else:
    print("\n[ERROR] Failed to generate .in file\n")

print("="*80 + "\n")

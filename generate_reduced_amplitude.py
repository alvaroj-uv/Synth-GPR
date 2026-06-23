#!/usr/bin/env python3
"""Generate .in file from modified TOML with reduced amplitude."""

from subprocess import run
from pathlib import Path

print("\n" + "="*80)
print("GENERATING .IN FILE: Reduced Amplitude (0.3 vs 1.0)")
print("="*80 + "\n")

result = run([
    'C:\\Users\\barba\\miniconda3\\python.exe',
    'scripts/pipeline/generate_gprmax_scenes.py',
    'start_fresh.toml',
    '-o', 'start_fresh_reduced.in'
], cwd=Path.cwd())

if result.returncode == 0:
    in_path = Path('start_fresh_reduced.in')
    if in_path.exists():
        size = in_path.stat().st_size
        print(f"\n[OK] {in_path} ({size:,} bytes)")
        print("\nNext: Run gprMax simulation\n")
else:
    print("\n[ERROR] Failed to generate .in file\n")

print("="*80 + "\n")

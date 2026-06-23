#!/usr/bin/env python3
"""Generate fouled ballast model (.in file) from TOML."""

from subprocess import run
from pathlib import Path

print("\n" + "="*80)
print("GENERATING FOULED BALLAST MODEL")
print("="*80 + "\n")

result = run([
    'C:\\Users\\barba\\miniconda3\\python.exe',
    'scripts/pipeline/generate_gprmax_scenes.py',
    'start_fresh_fouled.toml',
    '-o', 'start_fresh_fouled.in'
], cwd=Path.cwd())

if result.returncode == 0:
    in_path = Path('start_fresh_fouled.in')
    if in_path.exists():
        size = in_path.stat().st_size
        print(f"\n[OK] {in_path} ({size:,} bytes)\n")
else:
    print("\n[ERROR] Failed to generate .in file\n")

print("="*80 + "\n")

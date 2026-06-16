#!/usr/bin/env python3
"""
Render all .in files from epsilon sweep (visualize geometries).
"""

import sys
from pathlib import Path
import subprocess

def render_in_file(in_path: Path) -> bool:
    """Render a .in file to PNG."""
    result = subprocess.run(
        [sys.executable, 'scripts/pipeline/render_in_files.py', str(in_path)],
        capture_output=True, text=True, timeout=30
    )
    return result.returncode == 0


def main():
    sweep_dir = Path("output_test/ballast_epsilon_sweep_50ns")
    in_files = sorted(sweep_dir.glob("ballast_eps_*.in"))

    if not in_files:
        print("[ERR] No .in files found in epsilon sweep directory")
        return 1

    print(f"Found {len(in_files)} .in files to render\n")
    print("="*70)
    print("RENDERING EPSILON SWEEP GEOMETRIES")
    print("="*70 + "\n")

    success = 0
    failed = 0

    for in_file in in_files:
        eps = in_file.stem.replace("ballast_eps_", "").replace(".in", "")
        print(f"Rendering eps={eps}... ", end="", flush=True)

        if render_in_file(in_file):
            png_file = in_file.with_suffix(".png")
            if png_file.exists():
                size_kb = png_file.stat().st_size / 1024
                print(f"[OK] ({size_kb:.1f} KB)")
                success += 1
            else:
                print("[ERR] PNG not created")
                failed += 1
        else:
            print("[FAIL]")
            failed += 1

    print(f"\n{'='*70}")
    print(f"RESULTS: {success} OK, {failed} FAILED")
    print(f"{'='*70}\n")

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())

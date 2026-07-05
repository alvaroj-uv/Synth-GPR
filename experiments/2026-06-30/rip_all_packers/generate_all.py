#!/usr/bin/env python3
"""Test rock_shape="rip" against every packer reachable via
[sim].rock_packing_algorithm in the layers-mode pipeline (see
src/layer_scene_builder.py get_packer() for the authoritative dispatch list).
Generates + renders one .in per algo, tolerating failures (some algos may be
slow, unimplemented for this geometry, or missing optional deps).
"""
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PY = r"C:\Users\barba\miniconda3\python.exe"

ALGOS = [
    # pymunk_ballast, circlify, rip, rcp, rcpgen, rsa, shang_chu, hybris_shang
    # already completed in the first run -- resuming with the rest.
    "front_chain", "physics", "triangle",
    "growth", "poisson", "random", "wang", "grid",
]

TOML_TEMPLATE = """# RIP shape + {algo} placement
[job]
mode = "layers"
render = true

[sim]
freq_hz = 420e6
domain_x = 0.5
dx = 0.002
antenna_clearance = 0.1
air_buffer = 0.1
time_window = 12e-9
antenna_mode = "bistatic"
num_receivers = 1
receiver_spacing = 0.03
rock_packing_algorithm = "{algo}"
seed = 42
title = "RIP shape + {algo} placement"

[source]
waveform = "gaussian"
amplitude = 1.0
polarization = "z"

[[layer]]
name = "ballast"
thickness = 0.45
packed = true
eps = 6.1
sigma = 0.001
matrix_eps = 3.0
matrix_sigma = 1e-5
rock_shape = "rip"

[[layer]]
name = "formation"
thickness = 0.10
eps = 10.0
sigma = 0.03

[[layer]]
name = "subgrade"
thickness = 0.20
eps = 8.0
sigma = 0.020
"""


def main():
    results = []
    for algo in ALGOS:
        toml_path = HERE / f"rip_{algo}.toml"
        in_path = HERE / f"rip_{algo}.in"
        png_path = HERE / f"rip_{algo}.png"

        toml_path.write_text(TOML_TEMPLATE.format(algo=algo))

        print(f"\n=== {algo} ===", flush=True)
        t0 = time.time()
        try:
            gen = subprocess.run(
                [PY, "scripts/pipeline/generate_gprmax_scenes.py", str(toml_path), "-o", str(in_path)],
                cwd=ROOT, capture_output=True, text=True, timeout=90,
            )
            elapsed = time.time() - t0
            ok = gen.returncode == 0 and png_path.exists()
            if ok:
                print(f"  [OK] {elapsed:.1f}s", flush=True)
            else:
                print(f"  [FAIL] {elapsed:.1f}s\n{gen.stdout[-800:]}\n{gen.stderr[-800:]}", flush=True)
        except subprocess.TimeoutExpired:
            elapsed = time.time() - t0
            ok = False
            print(f"  [TIMEOUT] {elapsed:.1f}s (>90s, likely a slow/degenerate packer for this geometry)", flush=True)
        results.append((algo, ok, elapsed))

    print("\n" + "=" * 50)
    print("SUMMARY")
    print("=" * 50)
    for algo, ok, elapsed in results:
        print(f"  {algo:15s} {'OK' if ok else 'FAIL':5s} {elapsed:.1f}s")


if __name__ == "__main__":
    main()

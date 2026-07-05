#!/usr/bin/env python3
"""Frequency sweep (100-2000 MHz, step 100) over the three-layer trackbed
(ballast-in-air / subballast / subgrade) geometry, to see at what frequency
the formation/subgrade interface separates from the ballast/formation
interface in the A-scan (merged at 420 MHz -- see
experiments/2026-06-30/README.md Run 3).

For each frequency: writes a TOML (dx omitted -> auto-derived per freq so the
mesh stays dispersion-stable across the whole sweep), generates the .in via
generate_gprmax_scenes.py, runs gprMax, and reports runtime. Only .in/.out are
kept (render=false, no #geometry_view) -- the geometry is identical across
the sweep, only the timing/resolution in the A-scan is of interest here.
"""
import subprocess
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]   # repo root
OUT_DIR = Path(__file__).resolve().parent     # freq_sweep/
PY_GEN = r"C:\Users\barba\miniconda3\python.exe"
PY_GPRMAX = r"C:\Users\barba\.conda\envs\gprMax\python.exe"

TOML_TEMPLATE = """# Three-layer trackbed frequency sweep step: {freq_mhz:.0f} MHz
[job]
mode = "layers"
render = false

[sim]
freq_hz = {freq_hz:.0f}
domain_x = 0.5
antenna_clearance = 0.1
air_buffer = 0.1
antenna_mode = "bistatic"
num_receivers = 1
receiver_spacing = 0.03
rock_packing_algorithm = "pymunk_ballast"
seed = 42
title = "Freq sweep {freq_mhz:.0f} MHz: ballast(air)/subballast/subgrade"

[source]
waveform = "gaussian"
amplitude = 1.0
polarization = "z"

[[layer]]
name = "ballast"
thickness = 0.45
packed = true
eps = 4.0
sigma = 0.001
matrix = "free_space"

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
    freqs_mhz = list(range(100, 2001, 100))
    results = []
    for fm in freqs_mhz:
        tag = f"{fm:04d}mhz"
        toml_path = OUT_DIR / f"three_layer_{tag}.toml"
        in_path = OUT_DIR / f"three_layer_{tag}.in"
        out_path = OUT_DIR / f"three_layer_{tag}.out"

        toml_path.write_text(TOML_TEMPLATE.format(freq_mhz=fm, freq_hz=fm * 1e6))

        print(f"\n=== {fm} MHz ===", flush=True)
        t0 = time.time()
        gen = subprocess.run(
            [PY_GEN, "scripts/pipeline/generate_gprmax_scenes.py", str(toml_path), "-o", str(in_path)],
            cwd=ROOT, capture_output=True, text=True,
        )
        if gen.returncode != 0:
            print(f"  [FAIL generate]\n{gen.stderr[-2000:]}", flush=True)
            results.append((fm, "generate_failed", None))
            continue

        run = subprocess.run(
            [PY_GPRMAX, "-m", "gprMax", in_path.name],
            cwd=OUT_DIR, capture_output=True, text=True, timeout=600,
        )
        elapsed = time.time() - t0
        if run.returncode != 0 or not out_path.exists():
            print(f"  [FAIL gprmax] rc={run.returncode}\n{run.stdout[-1500:]}\n{run.stderr[-1500:]}", flush=True)
            results.append((fm, "gprmax_failed", elapsed))
            continue

        print(f"  [OK] {out_path.name} written in {elapsed:.1f}s", flush=True)
        results.append((fm, "ok", elapsed))

    print("\n" + "=" * 60)
    print("SWEEP SUMMARY")
    print("=" * 60)
    for fm, status, elapsed in results:
        e = f"{elapsed:.1f}s" if elapsed is not None else "-"
        print(f"  {fm:5d} MHz  {status:16s} {e}")


if __name__ == "__main__":
    main()

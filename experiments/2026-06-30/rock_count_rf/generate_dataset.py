#!/usr/bin/env python3
"""Generate a small synthetic dataset varying rock_packing_target_fill (+ seed)
to test whether an RF can predict the NUMBER OF PACKED ROCKS from waveform
features alone.

Geometry: single ballast layer (rock=6.1 Brancadoro / matrix=3 Mbubia-Clean,
420 MHz -- the session's best-so-far config), rock_shape="circle" so each
rock emits exactly one #cylinder command -- ground-truth rock count is just
`grep -c "#cylinder"` on the generated .in, no separate bookkeeping needed.

IMPORTANT: uses rock_packing_algorithm="circlify", NOT the project default
"pymunk_ballast". Verified empirically that pymunk_ballast IGNORES both
target_fill_ratio and rock_radius_min/max for its generate_rocks() path (uses
a hardcoded internal grading curve, self._get_radii_for(self.upper_material))
-- rock count there depends only on `seed`, giving near-identical geometry
across every target_fill value (confirmed via `diff` on two .in files -- 0
differing lines). circlify actually respects target_fill_ratio (81 rocks at
fill=0.4 vs 111 at fill=0.8, same seed) so it's used here instead.

Sweep: target_fill in {0.4, 0.5, 0.6, 0.7, 0.8, 0.9} x 6 seeds each = 36 samples.
"""
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PY_GEN = r"C:\Users\barba\miniconda3\python.exe"
PY_GPRMAX = r"C:\Users\barba\.conda\envs\gprMax\python.exe"

TOML_TEMPLATE = """# rock-count RF dataset: target_fill={fill:.2f}, seed={seed}
[job]
mode = "layers"
render = false

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
rock_packing_algorithm = "circlify"
seed = {seed}
title = "rock-count dataset: fill={fill:.2f} seed={seed}"

[[layer]]
name = "ballast"
thickness = 0.45
packed = true
eps = 6.1
sigma = 0.001
matrix_eps = 3.0
matrix_sigma = 1e-5
rock_shape = "circle"
rock_packing_target_fill = {fill:.2f}
"""


def main():
    fills = [0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
    seeds = list(range(1, 7))  # 6 seeds per fill
    total = len(fills) * len(seeds)
    done = 0
    results = []

    for fill in fills:
        for seed in seeds:
            done += 1
            tag = f"f{int(fill*100):03d}_s{seed:02d}"
            toml_path = HERE / f"sample_{tag}.toml"
            in_path = HERE / f"sample_{tag}.in"
            out_path = HERE / f"sample_{tag}.out"

            toml_path.write_text(TOML_TEMPLATE.format(fill=fill, seed=seed))

            print(f"\n=== [{done}/{total}] fill={fill:.2f} seed={seed} ===", flush=True)
            t0 = time.time()
            gen = subprocess.run(
                [PY_GEN, "scripts/pipeline/generate_gprmax_scenes.py", str(toml_path), "-o", str(in_path)],
                cwd=ROOT, capture_output=True, text=True,
            )
            if gen.returncode != 0:
                print(f"  [FAIL generate]\n{gen.stderr[-1500:]}", flush=True)
                results.append((fill, seed, None, None))
                continue

            n_rocks = in_path.read_text().count("#cylinder")

            run = subprocess.run(
                [PY_GPRMAX, "-m", "gprMax", in_path.name],
                cwd=HERE, capture_output=True, text=True, timeout=300,
            )
            elapsed = time.time() - t0
            if run.returncode != 0 or not out_path.exists():
                print(f"  [FAIL gprmax] rc={run.returncode}\n{run.stdout[-1000:]}\n{run.stderr[-1000:]}", flush=True)
                results.append((fill, seed, n_rocks, None))
                continue

            print(f"  [OK] {elapsed:.1f}s  n_rocks={n_rocks}", flush=True)
            results.append((fill, seed, n_rocks, elapsed))

    print("\n" + "=" * 60)
    print("DATASET GENERATION SUMMARY")
    print("=" * 60)
    print(f"{'fill':>6s} {'seed':>5s} {'n_rocks':>8s} {'time_s':>8s}")
    for fill, seed, n_rocks, elapsed in results:
        nr = str(n_rocks) if n_rocks is not None else "FAIL"
        t = f"{elapsed:.1f}" if elapsed is not None else "-"
        print(f"{fill:6.2f} {seed:5d} {nr:>8s} {t:>8s}")


if __name__ == "__main__":
    main()

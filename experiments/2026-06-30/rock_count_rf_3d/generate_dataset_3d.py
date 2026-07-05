#!/usr/bin/env python3
"""3-D rock-count RF dataset: N=20 (target_phi in {0.30,0.45,0.60,0.75,0.90} x
4 seeds each), using the project's proper TOML-driven pipeline
(scripts/pipeline/generate_3d_scene.py --config ..., NOT a hand-rolled
generator -- see this session's earlier correction). GSSI 400MHz antenna,
granite spheres via RCPGeneratorPacking (respects target_phi correctly).

~6 min/sample measured (11M cells, full GSSI antenna model) -> N=20 ~ 2 hours.

Ground truth rock count parsed from generate_3d_scene.py's own stdout
("[gen] N spheres ..." line) -- no separate bookkeeping needed.
"""
import re
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PY_GEN = r"C:\Users\barba\miniconda3\python.exe"
PY_GPRMAX = r"C:\Users\barba\.conda\envs\gprMax\python.exe"

TOML_TEMPLATE = (HERE / "sample_template.toml").read_text()

N_ROCKS_RE = re.compile(r"\[gen\]\s+(\d+)\s+spheres")


def main():
    fills = [0.30, 0.45, 0.60, 0.75, 0.90]
    seeds = list(range(1, 5))  # 4 seeds per fill -> 20 total
    total = len(fills) * len(seeds)
    done = 0
    results = []

    for fill in fills:
        for seed in seeds:
            done += 1
            tag = f"f{int(fill*100):03d}_s{seed:02d}"
            toml_path = HERE / f"sample3d_{tag}.toml"
            in_path = HERE / f"sample3d_{tag}.in"
            out_path = HERE / f"sample3d_{tag}.out"

            toml_path.write_text(TOML_TEMPLATE.format(fill=fill, seed=seed))

            print(f"\n=== [{done}/{total}] fill={fill:.2f} seed={seed} ===", flush=True)
            t0 = time.time()
            gen = subprocess.run(
                [PY_GEN, "scripts/pipeline/generate_3d_scene.py",
                 "--config", str(toml_path), "--out", str(in_path)],
                cwd=ROOT, capture_output=True, text=True,
            )
            if gen.returncode != 0 or not in_path.exists():
                print(f"  [FAIL generate]\n{gen.stderr[-1500:]}", flush=True)
                results.append((fill, seed, None, None))
                continue

            m = N_ROCKS_RE.search(gen.stdout)
            n_rocks = int(m.group(1)) if m else None

            run = subprocess.run(
                [PY_GPRMAX, "-m", "gprMax", in_path.name],
                cwd=HERE, capture_output=True, text=True, timeout=900,
            )
            elapsed = time.time() - t0
            if run.returncode != 0 or not out_path.exists():
                print(f"  [FAIL gprmax] rc={run.returncode}\n{run.stdout[-1000:]}\n{run.stderr[-1000:]}", flush=True)
                results.append((fill, seed, n_rocks, None))
                continue

            print(f"  [OK] {elapsed:.1f}s  n_rocks={n_rocks}", flush=True)
            results.append((fill, seed, n_rocks, elapsed))

    print("\n" + "=" * 60)
    print("3-D DATASET GENERATION SUMMARY (N=20)")
    print("=" * 60)
    print(f"{'fill':>6s} {'seed':>5s} {'n_rocks':>8s} {'time_s':>8s}")
    for fill, seed, n_rocks, elapsed in results:
        nr = str(n_rocks) if n_rocks is not None else "FAIL"
        t = f"{elapsed:.1f}" if elapsed is not None else "-"
        print(f"{fill:6.2f} {seed:5d} {nr:>8s} {t:>8s}")


if __name__ == "__main__":
    main()

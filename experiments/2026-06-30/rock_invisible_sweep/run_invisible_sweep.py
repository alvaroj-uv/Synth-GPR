#!/usr/bin/env python3
"""Sweep rock_invisible_fraction 0.0 -> 1.0 in steps of 0.1 on the best-so-far
config (rock=6.1 Brancadoro / matrix=3 Mbubia-Clean / 420 MHz), re-evaluating
the EFE real-data correlation at each step.

For each fraction: writes a TOML, generates the .in, runs gprMax, then
computes Hilbert-envelope and flipped-raw-signal correlation against the real
EFE Puerto-Limache trace nearest PK=20 km (D:/Codigo/Data/efe_full.h5, RAW not
AGC). See experiments/2026-06-30/README.md Run 7 for invisible_fraction=0.3
(single-point result: 0.9789 envelope / 0.9470 raw) -- this sweep fills in
the rest of the curve.
"""
import subprocess
import sys
import time
from pathlib import Path

import h5py
import numpy as np
from scipy.signal import hilbert
from scipy.interpolate import interp1d
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT))

from src.data_loader import read_ascan  # noqa: E402

PY_GEN = r"C:\Users\barba\miniconda3\python.exe"
PY_GPRMAX = r"C:\Users\barba\.conda\envs\gprMax\python.exe"
EFE_H5 = Path("D:/Codigo/Data/efe_full.h5")
PK_M = 20000.0

TOML_TEMPLATE = """# rock_invisible_fraction sweep step: {frac_pct:.0f}%
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
rock_packing_algorithm = "pymunk_ballast"
seed = 42
title = "420 MHz, rock eps=6.1, matrix eps=3, {frac_pct:.0f}% rocks invisible"

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
rock_invisible_fraction = {frac:.2f}

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


def compute_correlations(out_path: Path):
    syn = read_ascan(out_path, "Ez")
    syn_sig = -syn["signal"].astype(float)  # flipped, per established convention
    syn_t = syn["t_ns"]

    with h5py.File(EFE_H5, "r") as f:
        pk_arr = f["pk_m"][:]
        idx = int(np.argmin(np.abs(pk_arr - PK_M)))
        real_sig = f["traces"][idx, :].astype(float)
        real_dt_ns = float(f.attrs["dt_ns"])
    real_t = np.arange(len(real_sig)) * real_dt_ns

    syn_peak_idx = int(np.argmax(np.abs(hilbert(syn_sig)[: len(syn_sig) // 2])))
    real_peak_idx = int(np.argmax(np.abs(hilbert(real_sig)[: len(real_sig) // 2])))
    syn_t0 = syn_t - syn_t[syn_peak_idx]
    real_t0 = real_t - real_t[real_peak_idx]

    syn_env = np.abs(hilbert(syn_sig)); syn_env /= syn_env.max()
    real_env = np.abs(hilbert(real_sig)); real_env /= real_env.max()

    tc = np.arange(-2, 6, 0.05)
    f_syn_env = interp1d(syn_t0, syn_env, bounds_error=False, fill_value=0)
    f_real_env = interp1d(real_t0, real_env, bounds_error=False, fill_value=0)
    env_corr = float(np.corrcoef(f_syn_env(tc), f_real_env(tc))[0, 1])

    f_syn_raw = interp1d(syn_t0, syn_sig / np.abs(syn_sig).max(), bounds_error=False, fill_value=0)
    f_real_raw = interp1d(real_t0, real_sig / np.abs(real_sig).max(), bounds_error=False, fill_value=0)
    raw_corr = float(np.corrcoef(f_syn_raw(tc), f_real_raw(tc))[0, 1])

    return env_corr, raw_corr


def main():
    fractions = [round(x * 0.1, 1) for x in range(0, 11)]  # 0.0 .. 1.0
    results = []

    for frac in fractions:
        pct = frac * 100
        tag = f"inv{int(pct):03d}"
        toml_path = HERE / f"three_layer_420mhz_{tag}.toml"
        in_path = HERE / f"three_layer_420mhz_{tag}.in"
        out_path = HERE / f"three_layer_420mhz_{tag}.out"

        toml_path.write_text(TOML_TEMPLATE.format(frac=frac, frac_pct=pct))

        print(f"\n=== invisible_fraction={frac:.1f} ({pct:.0f}%) ===", flush=True)
        t0 = time.time()
        gen = subprocess.run(
            [PY_GEN, "scripts/pipeline/generate_gprmax_scenes.py", str(toml_path), "-o", str(in_path)],
            cwd=ROOT, capture_output=True, text=True,
        )
        if gen.returncode != 0:
            print(f"  [FAIL generate]\n{gen.stderr[-1500:]}", flush=True)
            results.append((frac, None, None, None))
            continue

        run = subprocess.run(
            [PY_GPRMAX, "-m", "gprMax", in_path.name],
            cwd=HERE, capture_output=True, text=True, timeout=300,
        )
        elapsed = time.time() - t0
        if run.returncode != 0 or not out_path.exists():
            print(f"  [FAIL gprmax] rc={run.returncode}\n{run.stdout[-1000:]}\n{run.stderr[-1000:]}", flush=True)
            results.append((frac, None, None, elapsed))
            continue

        env_corr, raw_corr = compute_correlations(out_path)
        print(f"  [OK] {elapsed:.1f}s  envelope_corr={env_corr:.4f}  raw_corr_flipped={raw_corr:.4f}", flush=True)
        results.append((frac, env_corr, raw_corr, elapsed))

    print("\n" + "=" * 60)
    print("SWEEP SUMMARY")
    print("=" * 60)
    print(f"{'frac':>6s} {'env_corr':>10s} {'raw_corr':>10s} {'time_s':>8s}")
    for frac, env_corr, raw_corr, elapsed in results:
        e = f"{env_corr:.4f}" if env_corr is not None else "FAIL"
        r = f"{raw_corr:.4f}" if raw_corr is not None else "FAIL"
        t = f"{elapsed:.1f}" if elapsed is not None else "-"
        print(f"{frac:6.1f} {e:>10s} {r:>10s} {t:>8s}")

    # Plot
    fracs_ok = [f for f, e, r, t in results if e is not None]
    env_ok = [e for f, e, r, t in results if e is not None]
    raw_ok = [r for f, e, r, t in results if e is not None]
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(fracs_ok, env_ok, "o-", label="Envelope correlation")
    ax.plot(fracs_ok, raw_ok, "s-", label="Raw correlation (flipped)")
    ax.set_xlabel("rock_invisible_fraction")
    ax.set_ylabel("Correlation vs real EFE trace (PK=20km)")
    ax.set_title("EFE correlation vs fraction of invisible rocks\n(rock=6.1, matrix=3, 420 MHz)")
    ax.legend()
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    out_png = HERE / "invisible_fraction_sweep_correlation.png"
    fig.savefig(out_png, dpi=150)
    print(f"\nSaved {out_png}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Domain-width A/B experiment (Khosravi Largani et al. 2025 guideline check).

Question: does widening the 400 MHz domain from the current 1.0 m to the
recommended 1.5*lambda_max (~2.25 m) materially change the extracted waveform
features? If yes, the guideline violation biases the research features and the
baselines need regeneration; if no, the 1.0 m trade is empirically justified.

Per (width, seed): build a 3-layer fouled scene -> run gprMax -> extract the
waveform features from the Ez A-scan. Then compare the two arms per-feature
with Cohen's d.

Usage:
    python scripts/experiments/domain_width_ab.py                # default run
    python scripts/experiments/domain_width_ab.py --seeds 8      # quick look
    python scripts/experiments/domain_width_ab.py \
        --widths 1.0 2.248 --freq 400e6 --out-dir test_output/domain_width_ab
"""

import argparse
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import numpy as np
import pandas as pd

from src.data_loader import read_ascan
from src.feature_extraction import extract_features_from_signal
from src.layer_scene_builder import SceneParams, write_scene
from src.layer_spec import _layers_from_table

GPRMAX_PYTHON_DEFAULT = "/opt/miniconda3/envs/gprMax/bin/python"

# Fixed 3-layer fouled scene (matches examples/scenes/three_layer_400mhz_fouled.toml)
LAYER_TABLE = [
    {"name": "subgrade", "thickness": 0.20},
    {"name": "formation", "thickness": 0.10},
    {"name": "ballast", "thickness": 0.25, "packed": True, "matrix": "fouling"},
]


def build_scene(width: float, seed: int, freq: float, out_dir: Path) -> Path:
    layers = _layers_from_table(LAYER_TABLE)
    params = SceneParams(
        freq_hz=freq,
        domain_x=width,
        antenna_clearance=0.5,  # held constant: isolate the width effect
        air_buffer=0.1,
        rx_spacing=0.0,
        seed=seed,
        title=f"domain-width A/B w={width} s={seed}",
    )
    in_path = out_dir / f"w{width:g}_s{seed:03d}.in"
    return Path(write_scene(layers, params, in_path))


def build_centered_scene(w_inner: float, w_outer: float, seed: int, out_dir: Path) -> Path:
    """Third arm: the EXACT rock field of the w_inner scene, centered in a
    w_outer domain. Layer boxes are stretched to the new width, rocks and
    antenna are shifted to the middle. Isolates boundary distance (vs the
    w_outer arm, which also has more rocks)."""
    src = out_dir / f"w{w_inner:g}_s{seed:03d}.in"
    if not src.exists():
        raise FileNotFoundError(f"build the {w_inner} m arm first: {src}")
    offset = (w_outer - w_inner) / 2.0
    out_lines = []
    for line in src.read_text().splitlines():
        tokens = line.split()
        cmd = tokens[0] if tokens else ""
        if cmd == "#domain:":
            tokens[1] = f"{w_outer:g}"
        elif cmd == "#box:":
            x1, x2 = float(tokens[1]), float(tokens[4])
            if abs(x1) < 1e-9 and abs(x2 - w_inner) < 1e-9:
                tokens[4] = f"{w_outer:g}"   # full-width layer box: stretch
            else:                             # localized box: shift
                tokens[1] = f"{x1 + offset:.6g}"
                tokens[4] = f"{x2 + offset:.6g}"
        elif cmd == "#triangle:":
            for i in (1, 4, 7):
                tokens[i] = f"{float(tokens[i]) + offset:.6g}"
        elif cmd == "#cylinder:":
            for i in (1, 4):
                tokens[i] = f"{float(tokens[i]) + offset:.6g}"
        elif cmd == "#hertzian_dipole:":
            tokens[2] = f"{float(tokens[2]) + offset:.6g}"
        elif cmd == "#rx:":
            tokens[1] = f"{float(tokens[1]) + offset:.6g}"
        else:
            out_lines.append(line)
            continue
        out_lines.append(" ".join(tokens))
    dst = out_dir / f"centered_s{seed:03d}.in"
    dst.write_text("\n".join(out_lines) + "\n")
    return dst


def run_gprmax(in_path: Path, gprmax_python: str) -> Path:
    out_path = in_path.with_suffix(".out")
    if out_path.exists():            # resumable: skip finished sims
        return out_path
    result = subprocess.run(
        [gprmax_python, "-m", "gprMax", str(in_path), "-n", "1"],
        capture_output=True, text=True,
    )
    if result.returncode != 0 or not out_path.exists():
        raise RuntimeError(f"gprMax failed for {in_path.name}:\n{result.stderr[-2000:]}")
    return out_path


def features_for(out_path: Path) -> pd.Series:
    data = read_ascan(out_path, "Ez")
    df = extract_features_from_signal(data["signal"], dt=data["dt"], signal_name="Ez")
    row = df.select_dtypes(include=[np.number]).iloc[0]
    return row


def cohens_d(a: np.ndarray, b: np.ndarray) -> float:
    na, nb = len(a), len(b)
    va, vb = a.var(ddof=1), b.var(ddof=1)
    pooled = ((na - 1) * va + (nb - 1) * vb) / (na + nb - 2)
    if pooled <= 0:
        return 0.0
    return float((a.mean() - b.mean()) / np.sqrt(pooled))


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    ap.add_argument("--widths", type=float, nargs=2, default=[1.0, 2.248],
                    help="the two domain widths to compare (m)")
    ap.add_argument("--seeds", type=int, default=16, help="seeds per arm")
    ap.add_argument("--freq", type=float, default=400e6, help="center frequency (Hz)")
    ap.add_argument("--out-dir", type=Path, default=Path("test_output/domain_width_ab"))
    ap.add_argument("--gprmax-python", default=GPRMAX_PYTHON_DEFAULT)
    ap.add_argument("--center-arm", action="store_true",
                    help="add a third arm: the narrow arm's rock field centered "
                         "in the wide domain (isolates boundary distance)")
    args = ap.parse_args()

    args.out_dir.mkdir(parents=True, exist_ok=True)
    w_lo, w_hi = sorted(args.widths)
    rows = []
    t0 = time.time()
    for width in args.widths:
        for seed in range(1, args.seeds + 1):
            tag = f"w={width:g} seed={seed}"
            t1 = time.time()
            in_path = build_scene(width, seed, args.freq, args.out_dir)
            out_path = run_gprmax(in_path, args.gprmax_python)
            feats = features_for(out_path)
            feats["_arm"] = f"{width:g}"
            feats["_seed"] = seed
            rows.append(feats)
            print(f"[{tag}] done in {time.time()-t1:.1f}s ({len(feats)-2} features)")

    if args.center_arm:
        for seed in range(1, args.seeds + 1):
            t1 = time.time()
            in_path = build_centered_scene(w_lo, w_hi, seed, args.out_dir)
            out_path = run_gprmax(in_path, args.gprmax_python)
            feats = features_for(out_path)
            feats["_arm"] = "centered"
            feats["_seed"] = seed
            rows.append(feats)
            print(f"[centered seed={seed}] done in {time.time()-t1:.1f}s")

    df = pd.DataFrame(rows)
    csv_path = args.out_dir / "features.csv"
    df.to_csv(csv_path, index=False)

    def arm(name):
        return df[df["_arm"] == name].drop(columns=["_arm", "_seed"])

    def compare(a, b):
        cols = arm(a).columns
        d = pd.Series({c: cohens_d(arm(a)[c].to_numpy(float), arm(b)[c].to_numpy(float))
                       for c in cols}).replace([np.inf, -np.inf], np.nan).dropna()
        return d

    pairs = [(f"{w_lo:g}", f"{w_hi:g}", "width effect (boundary + content)")]
    if args.center_arm:
        pairs += [
            (f"{w_lo:g}", "centered", "boundary distance only (same rocks)"),
            ("centered", f"{w_hi:g}", "scene content only (same boundary)"),
        ]

    summary = [f"Domain-width A/B/C @ {args.freq/1e6:.0f} MHz — "
               f"{w_lo} m vs {w_hi} m, n={args.seeds}/arm"]
    for a, b, label in pairs:
        d = compare(a, b)
        d_abs = d.abs().sort_values(ascending=False)
        summary += [
            "",
            f"── {a} vs {b}  [{label}] ──",
            f"median |d| = {d_abs.median():.3f}   "
            f"|d|>=0.5: {(d_abs >= 0.5).sum()} ({100*(d_abs >= 0.5).mean():.0f}%)   "
            f"|d|>=0.8: {(d_abs >= 0.8).sum()} ({100*(d_abs >= 0.8).mean():.0f}%)",
            "top 10:",
        ]
        for name in d_abs.head(10).index:
            summary.append(f"  {d[name]:+7.2f}  {name}")
    text = "\n".join(summary)
    (args.out_dir / "summary.txt").write_text(text + "\n")
    print("\n" + text)
    print(f"\nFeatures CSV: {csv_path}")
    print(f"Total runtime: {(time.time()-t0)/60:.1f} min")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Peplinski-model test: does gprMax's physically-validated #soil_peplinski mixing
model (+ #fractal_box heterogeneity) produce a frequency-vs-FI slope closer to
the real ~3.6 MHz/FI than CRIM+Debye (which ceilinged at ~0.42)?

The ballast layer is modeled as a fouled soil whose VOLUMETRIC WATER FRACTION
rises with fouling (PVC-driven capillary retention: more fouling fines -> more
retained water -> stronger dielectric dispersion). water_frac correlates ~0.93
with FI by design, so the signature should track FI.

#soil_peplinski: sand clay bulk_density sand_part_density water_lo water_hi name
#fractal_box: x1 y1 z1 x2 y2 z2 frac_dim weight_x weight_y weight_z n_materials soil box_id

10 scenes spanning FI 0-50. Metric: spectral centroid; compare slope vs FI.

Usage:
    python scripts/experiments/peplinski_slope.py --generate
    python scripts/experiments/peplinski_slope.py --analyze
"""
import re, sys, argparse
from pathlib import Path
import numpy as np, pandas as pd

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))
from src.dataset_io import load_features

DATA_DIR = ROOT / "output" / "gpr_synth_dataset_80k"
OUT_DIR  = Path(r"D:\gprMax\user_models\peplinski")
PARQUET  = ROOT / "output" / "dataset_80k_features.parquet"

# Peplinski fixed params (clay-dominated fouling fines, per config notes)
SAND_FRAC, CLAY_FRAC = 0.3, 0.7
BULK_DENSITY = 1.9          # g/cm3
SAND_PART_DENSITY = 2.66    # g/cm3
N_MATERIALS = 10            # fractal_box water-fraction variants
FRAC_DIM = 1.5
FI_BINS = [(0,5),(15,20),(25,30),(35,42),(45,55)]
N_PER_BIN = 2
SEED = 11


def water_frac(pvc):
    """Volumetric water fraction driven by fouling (PVC capillary retention)."""
    return float(np.clip(0.02 + 0.20 * (pvc / 100.0), 0.001, 0.25))


def parse(c, k):
    m = re.search(rf"^## {k}:\s*([-\d.eE+]+)", c, re.MULTILINE)
    return float(m.group(1)) if m else None


def build(content, pvc):
    bb = parse(content, "ballast_bottom_y"); bt = parse(content, "ballast_top_y")
    dom = re.search(r"#domain:\s*([\d.eE+-]+) [\d.eE+-]+ ([\d.eE+-]+)", content)
    dxx, dz = float(dom.group(1)), dom.group(2)

    wlo = max(0.001, water_frac(pvc) - 0.02)
    whi = water_frac(pvc) + 0.02

    kept = [l for l in content.splitlines()
            if not l.startswith(("#box:", "#cylinder:", "#triangle:", "#edge:", "#plate:"))]
    body = "\n".join(kept).rstrip()

    soil = (f"#soil_peplinski: {SAND_FRAC} {CLAY_FRAC} {BULK_DENSITY} "
            f"{SAND_PART_DENSITY} {wlo:.4f} {whi:.4f} foul_soil")
    # subgrade + formation as plain boxes; ballast layer as fractal_box of soil
    geom = (
        f"\n{soil}\n"
        f"#box: 0.0 0.0 0.0 {dxx} 0.2 {dz} subgrade\n"
        f"#box: 0.0 0.2 0.0 {dxx} {bb} {dz} formation\n"
        f"#fractal_box: 0.0 {bb} 0.0 {dxx} {bt} {dz} {FRAC_DIM} 1 1 1 "
        f"{N_MATERIALS} foul_soil ballast_fb\n"
    )
    return body + geom


def generate():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    syn = load_features(PARQUET, columns=["sample_id", "Lab_FI", "pvc"])
    rng = np.random.default_rng(SEED); picks = []
    for lo, hi in FI_BINS:
        pool = syn[(syn.Lab_FI >= lo) & (syn.Lab_FI < hi)].sample_id.values
        if len(pool): picks.extend(rng.choice(pool, min(N_PER_BIN, len(pool)), replace=False))
    man = []
    for sid in picks:
        src = DATA_DIR / f"s_{int(sid):05d}.in"
        if not src.exists(): continue
        row = syn[syn.sample_id == sid].iloc[0]
        txt = build(src.read_text(encoding="utf-8", errors="ignore"), row.pvc)
        (OUT_DIR / f"s_{int(sid):05d}_pep.in").write_text(txt, encoding="utf-8")
        man.append({"sample_id": int(sid), "Lab_FI": float(row.Lab_FI),
                    "pvc": float(row.pvc), "water_frac": water_frac(row.pvc)})
    pd.DataFrame(man).to_csv(OUT_DIR / "manifest.csv", index=False)
    print(f"Generated {len(man)} Peplinski .in in {OUT_DIR}")
    print(f"FI range: {min(m['Lab_FI'] for m in man):.0f}-{max(m['Lab_FI'] for m in man):.0f}")
    print("Run run_all.bat, then --analyze")


def metric(ez, dt):
    from scipy.signal import welch, butter, filtfilt
    pk = int(np.argmax(np.abs(ez))); coda = ez[pk + 20:]
    if len(coda) < 64: return np.nan
    sig = coda - coda.mean(); fs = 1 / dt
    b, a = butter(4, [150e6/(fs/2), 800e6/(fs/2)], btype="band"); sig = filtfilt(b, a, sig)
    f, p = welch(sig, fs=fs, nperseg=min(len(sig), 256), nfft=4096)
    band = (f >= 150e6) & (f <= 800e6); f, p = f[band], p[band]
    return np.sum(f*p)/np.sum(p)/1e6 if p.sum() > 0 else np.nan


def analyze():
    from scipy.stats import linregress
    man = pd.read_csv(OUT_DIR / "manifest.csv")
    from src.data_loader import read_ascan

    def load(p):
        d = read_ascan(p)
        return d["signal"].astype(float), d["dt"]
    rows = []
    for _, r in man.iterrows():
        op = OUT_DIR / f"s_{int(r['sample_id']):05d}_pep.out"
        if op.exists():
            rows.append({"FI": r["Lab_FI"], "c": metric(*load(op))})
    d = pd.DataFrame(rows).dropna()
    print(f"Analyzed {len(d)} scenes, FI {d.FI.min():.0f}-{d.FI.max():.0f}\n")
    if len(d) > 2:
        s = linregress(d["FI"], d["c"])
        print(f"  Peplinski+fractal: centroid-vs-FI slope = {s.slope:+.3f} MHz/FI "
              f"(r={s.rvalue:+.2f}, p={s.pvalue:.2g}, n={len(d)})")
    print(f"\n  Reference: homog={0.17}, Debye-max={0.42}, REAL={3.6} MHz/FI")
    print("  Peplinski is the answer only if slope >> 0.42 and approaches 3.6.")
    d.to_csv(OUT_DIR / "results.csv", index=False)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--generate", action="store_true")
    ap.add_argument("--analyze", action="store_true")
    a = ap.parse_args()
    if a.generate: generate()
    elif a.analyze: analyze()
    else: print("--generate or --analyze")


if __name__ == "__main__":
    main()

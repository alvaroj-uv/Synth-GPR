#!/usr/bin/env python3
"""
Rigorous rock-vs-homogeneous experiment (replication + proper spectral metric).

Tests the hypothesis that explicit rocks invert the fouling frequency-signature
sign vs an effective medium — properly this time:
  - N scenes per class (C and HF extremes), not n=1.
  - WITH-rocks traces reuse the existing 80k .out (already simulated).
  - WITHOUT-rocks: generate homogeneous-medium .in (one CRIM ballast box) to run.
  - Compare the DISTRIBUTION of spectral CENTROID (stable) + peak, with Welch +
    zero-padding for fine frequency resolution.

Step 1 (this script, --generate): sample scenes, write homogeneous .in files.
Step 2: run the homogeneous .in through gprMax (run_all.bat).
Step 3 (--analyze): compare centroid distributions rocks vs homogeneous.

Usage:
    python scripts/analysis/rock_vs_homog_rigorous.py --generate
    python scripts/analysis/rock_vs_homog_rigorous.py --analyze
"""

import re
import sys
import glob
import argparse
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))
from src.dataset_io import load_features
from src.physics import crim_bulk_eps

DATA_DIR = ROOT / "output" / "gpr_synth_dataset_80k"
HOMOG_DIR = Path(r"D:\gprMax\user_models\rock_vs_homog")
PARQUET = ROOT / "output" / "dataset_80k_features.parquet"

N_PER_CLASS = 20
SEED = 42
EPS_ROCK, SIG_ROCK = 5.0, 0.001


# ---------- spectral metric ----------
def spectral_metrics(ez, dt):
    """Centroid (stable) and peak freq of the coda, Welch + zero-pad, 150-800 MHz."""
    from scipy.signal import welch, butter, filtfilt
    pk = int(np.argmax(np.abs(ez)))
    coda = ez[pk + 20:]
    if len(coda) < 64:
        return np.nan, np.nan
    sig = coda - coda.mean()
    fs = 1.0 / dt
    b, a = butter(4, [150e6 / (fs / 2), 800e6 / (fs / 2)], btype="band")
    sig = filtfilt(b, a, sig)
    # Welch PSD with zero-padding (nfft) for fine resolution
    nper = min(len(sig), 256)
    f, p = welch(sig, fs=fs, nperseg=nper, nfft=4096)
    band = (f >= 150e6) & (f <= 800e6)
    f, p = f[band], p[band]
    if p.sum() <= 0:
        return np.nan, np.nan
    centroid = np.sum(f * p) / np.sum(p) / 1e6
    peak = f[np.argmax(p)] / 1e6
    return centroid, peak


# ---------- generation ----------
def parse(content, key):
    m = re.search(rf"^## {key}:\s*([-\d.eE+]+)", content, re.MULTILINE)
    return float(m.group(1)) if m else None


def fouling_props(content):
    m = re.search(r"^#material:\s*([\d.eE+-]+)\s+([\d.eE+-]+).*bal_foul", content, re.MULTILINE)
    return (float(m.group(1)), float(m.group(2))) if m else (5.0, 0.01)


def make_homogeneous(content):
    fr = parse(content, "mc_rock_fraction") or 0.0
    ff = parse(content, "mc_fouling_fraction") or 0.0
    fv = parse(content, "mc_void_fraction") or 0.0
    tot = fr + ff + fv
    if tot <= 0:
        return None
    vr, vf, va = fr / tot, ff / tot, fv / tot
    eps_f, sig_f = fouling_props(content)
    eps_eff = round(crim_bulk_eps(vr, EPS_ROCK, vf, eps_f, 0.0, 1.0, va), 4)
    sig_eff = round(vr * SIG_ROCK + vf * sig_f, 6)

    bb = parse(content, "ballast_bottom_y")
    bt = parse(content, "ballast_top_y")
    dom = re.search(r"#domain:\s*([\d.eE+-]+) [\d.eE+-]+ ([\d.eE+-]+)", content)
    dx_x, dz = dom.group(1), dom.group(2)

    kept = [ln for ln in content.splitlines()
            if not ln.startswith(("#box:", "#cylinder:", "#triangle:", "#edge:", "#plate:"))]
    body = "\n".join(kept).rstrip()
    geom = (f"\n#material: {eps_eff} {sig_eff} 1 0.0 ballast_eff\n"
            f"#box: 0.0 0.0 0.0 {dx_x} 0.2 {dz} subgrade\n"
            f"#box: 0.0 0.2 0.0 {dx_x} {bb} {dz} formation\n"
            f"#box: 0.0 {bb} 0.0 {dx_x} {bt} {dz} ballast_eff\n")
    return body + geom, eps_eff, sig_eff


def generate():
    HOMOG_DIR.mkdir(parents=True, exist_ok=True)
    syn = load_features(PARQUET, columns=["sample_id", "Lab_FI"])
    syn["cls"] = syn["Lab_FI"].apply(lambda v: "C" if v < 10 else "HF" if v >= 40 else "mid")
    rng = np.random.default_rng(SEED)

    manifest = []
    for cls in ["C", "HF"]:
        pool = syn[syn["cls"] == cls]["sample_id"].values
        pick = rng.choice(pool, size=min(N_PER_CLASS, len(pool)), replace=False)
        for sid in pick:
            src = DATA_DIR / f"s_{int(sid):05d}.in"
            outr = DATA_DIR / f"s_{int(sid):05d}.out"
            if not src.exists() or not outr.exists():
                continue
            res = make_homogeneous(src.read_text(encoding="utf-8", errors="ignore"))
            if res is None:
                continue
            text, eps_eff, _ = res
            hpath = HOMOG_DIR / f"s_{int(sid):05d}_{cls}_homog.in"
            hpath.write_text(text, encoding="utf-8")
            manifest.append({"sample_id": int(sid), "cls": cls,
                             "rocks_out": str(outr), "homog_in": str(hpath),
                             "eps_eff": eps_eff})
    pd.DataFrame(manifest).to_csv(HOMOG_DIR / "manifest.csv", index=False)
    print(f"Generated {len(manifest)} homogeneous .in in {HOMOG_DIR}")
    print(f"Class counts: {pd.DataFrame(manifest)['cls'].value_counts().to_dict()}")
    print(f"\nNow run the homogeneous .in through gprMax (run_all.bat in that dir),")
    print(f"then: python {Path(__file__).name} --analyze")


# ---------- analysis ----------
def analyze():
    from src.data_loader import read_ascan
    man = pd.read_csv(HOMOG_DIR / "manifest.csv")

    def load(p):
        d = read_ascan(p)
        return d["signal"].astype(float), d["dt"]

    rows = []
    for _, r in man.iterrows():
        homog_out = Path(r["homog_in"]).with_suffix(".out")
        rec = {"cls": r["cls"], "sample_id": r["sample_id"]}
        if Path(r["rocks_out"]).exists():
            rec["rocks_centroid"], rec["rocks_peak"] = spectral_metrics(*load(r["rocks_out"]))
        if homog_out.exists():
            rec["homog_centroid"], rec["homog_peak"] = spectral_metrics(*load(homog_out))
        rows.append(rec)
    df = pd.DataFrame(rows)

    def summ(col):
        c = df[df.cls == "C"][col].dropna()
        h = df[df.cls == "HF"][col].dropna()
        return c.mean(), c.std(), h.mean(), h.std(), h.mean() - c.mean()

    print(f"Analyzed {len(df)} scenes "
          f"(C={sum(df.cls=='C')}, HF={sum(df.cls=='HF')})\n")
    from scipy.stats import mannwhitneyu
    for metric in ["centroid", "peak"]:
        print(f"=== {metric.upper()} FREQ (MHz) ===")
        for kind in ["rocks", "homog"]:
            col = f"{kind}_{metric}"
            if col not in df:
                continue
            cm, cs, hm, hs, d = summ(col)
            cvals = df[df.cls == "C"][col].dropna()
            hvals = df[df.cls == "HF"][col].dropna()
            try:
                _, pval = mannwhitneyu(cvals, hvals)
            except ValueError:
                pval = np.nan
            sign = "+" if d > 0 else "-"
            print(f"  {kind:6s}: C={cm:6.1f}±{cs:4.1f}  HF={hm:6.1f}±{hs:4.1f}  "
                  f"HF-C={d:+6.1f} [{sign}]  p={pval:.3g}")
        print()
    print("REAL: fouling RAISES freq (+). Hypothesis: rocks give (-), homog gives (+).")
    print("Trust only if the difference is large vs the ± std AND p<0.05.")
    df.to_csv(HOMOG_DIR / "results.csv", index=False)
    print(f"\nSaved {HOMOG_DIR / 'results.csv'}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--generate", action="store_true")
    ap.add_argument("--analyze", action="store_true")
    args = ap.parse_args()
    if args.generate:
        generate()
    elif args.analyze:
        analyze()
    else:
        print("Use --generate (then run gprMax) or --analyze.")


if __name__ == "__main__":
    main()

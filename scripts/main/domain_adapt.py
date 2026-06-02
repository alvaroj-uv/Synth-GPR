#!/usr/bin/env python3
"""
Option 2 + 3: notebook bins + domain adaptation (synthetic + a few reals).

Compares three training regimes, all evaluated on held-out REAL traces via
StratifiedKFold so a real test fold is NEVER seen in training:

  A) SYNTH-ONLY      : train on synthetic, predict real test fold (the gap)
  B) SYNTH + REAL    : train on synthetic + the OTHER real folds, predict fold
  C) REAL-ONLY       : train on the other real folds only (reference)

Labels: notebook bins (0/10/20/30/40) from continuous FI on both sides.
Because C has only 1 real sample (coda CSV drops placeholders), the headline
is BINARY LOW (FI<20) vs HIGH (FI>=20); 4-class (drop C) reported as secondary.

Usage:
    python scripts/main/domain_adapt.py
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import balanced_accuracy_score, accuracy_score

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

SYN_PARQUET = ROOT / "output" / "dataset_coda_features.parquet"
FI_PARQUET = ROOT / "output" / "dataset_80k_features.parquet"
REAL_CSV = ROOT / "docs" / "input" / "feature_dataset_real.csv"
REPORT = ROOT / "output" / "domain_adapt.txt"


def notebook_bins(fi):
    fi = np.asarray(fi, float)
    o = np.empty(len(fi), object)
    o[fi < 10] = "C"; o[(fi >= 10) & (fi < 20)] = "MC"
    o[(fi >= 20) & (fi < 30)] = "MF"; o[(fi >= 30) & (fi < 40)] = "F"
    o[fi >= 40] = "HF"
    return o


def binary(fi):
    return np.where(np.asarray(fi, float) >= 20, "HIGH", "LOW")


def rf():
    return RandomForestClassifier(
        n_estimators=300, max_features="sqrt", min_samples_leaf=2,
        class_weight="balanced", random_state=42, n_jobs=-1)


def run(label_fn, Xs, ys_syn, Xr, yr, name, log):
    """5-fold over reals; A/B/C regimes; report mean balanced acc + acc."""
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    res = {k: {"bal": [], "acc": []} for k in ("A_synth", "B_synth+real", "C_real")}
    for tr, te in skf.split(Xr, yr):
        Xr_tr, Xr_te = Xr[tr], Xr[te]
        yr_tr, yr_te = yr[tr], yr[te]

        # A) synthetic only
        m = rf().fit(Xs, ys_syn)
        p = m.predict(Xr_te)
        res["A_synth"]["bal"].append(balanced_accuracy_score(yr_te, p))
        res["A_synth"]["acc"].append(accuracy_score(yr_te, p))

        # B) synthetic + real-train
        Xb = np.vstack([Xs, Xr_tr]); yb = np.concatenate([ys_syn, yr_tr])
        m = rf().fit(Xb, yb)
        p = m.predict(Xr_te)
        res["B_synth+real"]["bal"].append(balanced_accuracy_score(yr_te, p))
        res["B_synth+real"]["acc"].append(accuracy_score(yr_te, p))

        # C) real only
        m = rf().fit(Xr_tr, yr_tr)
        p = m.predict(Xr_te)
        res["C_real"]["bal"].append(balanced_accuracy_score(yr_te, p))
        res["C_real"]["acc"].append(accuracy_score(yr_te, p))

    log(f"\n[{name}]  (5-fold over reals, mean ± std)")
    log(f"  {'regime':<16}{'bal_acc':>16}{'accuracy':>16}")
    for k, v in res.items():
        b = np.array(v["bal"]); a = np.array(v["acc"])
        log(f"  {k:<16}{b.mean():>8.3f}±{b.std():.3f}{a.mean():>8.3f}±{a.std():.3f}")


def main():
    lines = []
    def log(m=""):
        print(m); lines.append(m)

    real = pd.read_csv(REAL_CSV)
    feat = [c for c in real.columns if c not in ("ID", "FI", "FI_class")]

    syn = pd.read_parquet(SYN_PARQUET)
    fi_map = pd.read_parquet(FI_PARQUET, columns=["sample_id", "Lab_FI"])
    syn = syn.merge(fi_map, on="sample_id", how="inner")
    feat = [c for c in feat if c in syn.columns]

    Xs = syn[feat].values.astype("float32")
    Xr = real[feat].values.astype("float32")
    fi_syn = syn["Lab_FI"].values
    fi_real = real["FI"].values

    log("=" * 60)
    log("DOMAIN ADAPTATION — notebook bins, synthetic + reals")
    log("=" * 60)
    log(f"Synthetic: {len(Xs)} | Real: {len(Xr)} | Features: {len(feat)}")

    # Binary (robust headline)
    run(binary, Xs, binary(fi_syn), Xr, binary(fi_real),
        "BINARY  LOW(FI<20) vs HIGH(FI>=20)", log)

    # 4-class (drop C: only 1 real sample)
    yr4 = notebook_bins(fi_real)
    keep = yr4 != "C"
    ys4 = notebook_bins(fi_syn)
    run(notebook_bins, Xs[ys4 != "C"], ys4[ys4 != "C"],
        Xr[keep], yr4[keep], "4-CLASS  MC/MF/F/HF (C dropped, 1 real)", log)

    log("\nInterpretation:")
    log("  B > A  => a few real traces rescue the synthetic model (adaptation works)")
    log("  B ~ A  => synthetic dominates; few reals can't shift it")
    log("  C high => real features ARE separable; gap is purely sim->real")

    REPORT.write_text("\n".join(lines), encoding="utf-8")
    print(f"\nReport saved -> {REPORT}")


if __name__ == "__main__":
    main()

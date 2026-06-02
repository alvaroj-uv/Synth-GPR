#!/usr/bin/env python3
"""
DIAGNOSTIC: is the fouling signal present in the REAL traces themselves?

Trains/evaluates a Random Forest using ONLY the 101 real field traces
(feature_dataset_real.csv) via cross-validation -- no synthetic data involved.

Interpretation:
  - If real-only CV balanced accuracy is clearly > chance  -> the fouling
    signature IS in the real waveform features; the sim->real collapse is a
    DOMAIN-SHIFT problem (simulator must be calibrated / domain-adapted).
  - If real-only CV is ~chance -> either the real FI labels are too noisy or
    the 572 features don't capture field fouling; calibrating the sim won't help.

Two label granularities (small, imbalanced set -> report both):
  - 4-class : MC / MF / F / HF  (as-is)
  - binary  : LOW (MC+MF, FI<20) vs HIGH (F+HF, FI>=20)  -- robust headline

Usage:
    python scripts/main/diagnose_real.py
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.dummy import DummyClassifier
from sklearn.metrics import (
    balanced_accuracy_score, accuracy_score,
    classification_report, confusion_matrix,
)

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

REAL_CSV = ROOT / "docs" / "input" / "feature_dataset_real.csv"
REPORT_PATH = ROOT / "output" / "rf_diagnose_real.txt"
RANDOM_SEED = 42


def rf():
    return RandomForestClassifier(
        n_estimators=300, max_features="sqrt", min_samples_leaf=2,
        class_weight="balanced", random_state=RANDOM_SEED, n_jobs=-1,
    )


def cv_eval(X, y, n_splits, log):
    """Stratified CV out-of-fold predictions -> honest small-sample estimate."""
    skf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=RANDOM_SEED)
    y_pred = cross_val_predict(rf(), X, y, cv=skf, n_jobs=-1)

    # Chance baselines
    dummy_strat = cross_val_predict(
        DummyClassifier(strategy="stratified", random_state=RANDOM_SEED),
        X, y, cv=skf)
    dummy_freq = cross_val_predict(
        DummyClassifier(strategy="most_frequent"), X, y, cv=skf)

    bal = balanced_accuracy_score(y, y_pred)
    acc = accuracy_score(y, y_pred)
    log(f"  RF        : balanced_acc={bal:.4f}  acc={acc:.4f}")
    log(f"  Dummy(MF) : balanced_acc={balanced_accuracy_score(y, dummy_freq):.4f}"
        f"  acc={accuracy_score(y, dummy_freq):.4f}  (predict majority)")
    log(f"  Dummy(str): balanced_acc={balanced_accuracy_score(y, dummy_strat):.4f}"
        f"  acc={accuracy_score(y, dummy_strat):.4f}  (random stratified)")
    labels = sorted(set(y))
    log("  Classification report (out-of-fold):")
    log(classification_report(y, y_pred, labels=labels, target_names=labels,
                              zero_division=0))
    log("  Confusion (rows=true, cols=pred): " + str(labels))
    cm = confusion_matrix(y, y_pred, labels=labels)
    for rl, row in zip(labels, cm):
        log(f"    {rl:>4}: {row}")
    return bal


def main():
    real = pd.read_csv(REAL_CSV)
    feat_cols = [c for c in real.columns if c not in ("ID", "FI", "FI_class")]
    X = real[feat_cols].values.astype("float32")
    y4 = real["FI_class"].values

    # Binary grouping by FI threshold 20 (F/HF = HIGH, MC/MF = LOW)
    ybin = np.where(real["FI"].values >= 20, "HIGH", "LOW")

    lines = []

    def log(m=""):
        print(m)
        lines.append(m)

    log("=" * 60)
    log("DIAGNOSTIC — RF trained on REAL traces ONLY (no synthetic)")
    log("=" * 60)
    log(f"Samples : {len(real)}   Features: {len(feat_cols)}")
    log(f"4-class dist : {pd.Series(y4).value_counts().sort_index().to_dict()}")
    log(f"binary  dist : {pd.Series(ybin).value_counts().to_dict()}")
    log()

    # 4-class: drop the singleton MC class (1 sample) so StratifiedKFold works,
    # OR fold it; with 1 sample CV is impossible -> report on >=2 classes.
    counts = pd.Series(y4).value_counts()
    keep = counts[counts >= 5].index  # need enough per fold
    mask = np.isin(y4, keep)
    log(f"[4-class CV] using classes with >=5 samples: {sorted(keep)} "
        f"({mask.sum()}/{len(y4)} samples)")
    n_splits4 = int(counts[keep].min())
    n_splits4 = max(2, min(5, n_splits4))
    log(f"  StratifiedKFold n_splits={n_splits4}")
    cv_eval(X[mask], y4[mask], n_splits4, log)
    log()

    log("[Binary CV] LOW (FI<20) vs HIGH (FI>=20)")
    log("  StratifiedKFold n_splits=5")
    bal_bin = cv_eval(X, ybin, 5, log)
    log()

    # Verdict
    log("=" * 60)
    log("VERDICT")
    log("=" * 60)
    chance_bin = 0.5
    if bal_bin > chance_bin + 0.10:
        log(f"Binary balanced_acc={bal_bin:.3f} >> chance (0.5):")
        log("  -> Fouling signature IS present in the real waveform features.")
        log("  -> sim->real collapse is a DOMAIN-SHIFT problem (calibrate sim /")
        log("     domain-adapt). The real data is learnable.")
    else:
        log(f"Binary balanced_acc={bal_bin:.3f} ~ chance (0.5):")
        log("  -> Real features do NOT separate fouling on their own.")
        log("  -> Either FI labels are too noisy or the 572 features miss field")
        log("     fouling. Calibrating the simulator alone won't fix it.")

    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")
    print(f"\nReport saved -> {REPORT_PATH}")


if __name__ == "__main__":
    main()

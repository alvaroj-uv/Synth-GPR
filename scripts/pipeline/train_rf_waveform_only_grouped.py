#!/usr/bin/env python3
"""
Leakage-controlled variant of train_rf_waveform_only.py.

Motivation
----------
The original experiment (output/rf_results_waveform_only.txt) used a RANDOM
stratified train/test split and reported balanced accuracy ~0.8868.

Inspection of output/dataset_80k_features.parquet revealed that, although every
row has a unique sample_id and unique scene metadata, **13,408 of 80,000 rows
(16.76%) are EXACT duplicates on the full 572-feature waveform vector**
(68,317 distinct vectors; largest duplicate group = 493 identical class-C
"clean" A-scans). A random split scatters these identical waveforms across
train and test, leaking information and inflating the metric.

This script keeps EVERYTHING identical to the original (same 572 features, same
RF hyper-parameters, same seed) but replaces the split with a GROUP-AWARE,
class-stratified scheme where the group id is the full-feature-vector hash, so
identical waveforms can never appear in both train and test.

It also re-runs the original RANDOM split inside this same process (same seed)
so the reported delta is exact and per-class comparable.

Outputs (new file, nothing existing is overwritten):
    output/rf_results_waveform_only_grouped.txt
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import (
    train_test_split, StratifiedKFold, cross_val_score,
    StratifiedGroupKFold, GroupShuffleSplit,
)
from sklearn.metrics import (
    classification_report, confusion_matrix, accuracy_score,
    balanced_accuracy_score, f1_score,
)

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

# ---- Kept identical to the original script -----------------------------------
METADATA_FIELDS = {
    "pvc", "moisture", "achieved_density", "porosity",
    "Lab_FI", "Lab_FI_local", "Lab_FR",
    "Lab_er_bulk_leng", "Lab_bulk_eps",
    "Lab_alpha_400MHz_npm", "Lab_alpha_2GHz_npm", "Lab_surface_R",
    "Lab_LDCP_FI_est", "Lab_LDCP_FH", "Lab_LDCP_qs_mean",
    "Lab_clean_ballast_mm",
    "mc_rock_fraction", "mc_fouling_fraction", "mc_subgrade_fraction",
    "mc_formation_fraction", "mc_void_fraction", "mc_pvc_measured",
    "ballast_top_y", "ballast_bottom_y",
    "mc_y_max", "mc_y_min", "mc_y_local_max",
    "ldcp_x",
    "Lab_P4", "Lab_P200", "Lab_Porosity",
}
LABEL_ORDER = ["C", "MC", "MF", "F", "HF"]
TEST_SIZE = 0.2
RANDOM_SEED = 42

PARQUET = Path("output/dataset_80k_features.parquet")
REPORT = Path("output/rf_results_waveform_only_grouped.txt")


def make_rf():
    """Identical hyper-parameters to the original experiment."""
    return RandomForestClassifier(
        n_estimators=300,
        max_features="sqrt",
        min_samples_leaf=2,
        class_weight="balanced",
        random_state=RANDOM_SEED,
        n_jobs=-1,
    )


def load():
    df = pd.read_parquet(PARQUET)
    exclude = {"sample_id", "source", "label"} | METADATA_FIELDS
    feat_cols = [c for c in df.columns if c not in exclude]
    X = df[feat_cols].values.astype("float32")
    y = df["label"].values
    # group id = hash of the full (rounded) feature vector -> identical
    # waveforms share a group and cannot straddle train/test.
    gid = pd.util.hash_pandas_object(df[feat_cols].round(6), index=False).values
    return X, y, gid, feat_cols


def per_class_f1(y_true, y_pred):
    f1 = f1_score(y_true, y_pred, labels=LABEL_ORDER, average=None, zero_division=0)
    return dict(zip(LABEL_ORDER, f1))


def fmt_cm(cm):
    lines = [f"{'':>6}" + "".join(f"{c:>7}" for c in LABEL_ORDER)]
    for i, lab in enumerate(LABEL_ORDER):
        lines.append(f"{lab:>6}" + "".join(f"{v:>7}" for v in cm[i]))
    return "\n".join(lines)


def main():
    print(f"Loading {PARQUET} ...")
    X, y, gid, feat_cols = load()
    n = len(y)
    n_groups = len(np.unique(gid))
    classes, counts = np.unique(y, return_counts=True)

    print(f"  A-scans (rows)        : {n}")
    print(f"  Features              : {len(feat_cols)} (waveform only)")
    print(f"  Unique feature-vector groups : {n_groups}")
    print(f"  Duplicate-collapsed rows     : {n - n_groups} "
          f"({100*(n-n_groups)/n:.2f}%)")
    print(f"  Classes               : {dict(zip(classes, counts))}\n")

    lines = []

    def log(msg=""):
        print(msg)
        lines.append(msg)

    log("=" * 70)
    log("RANDOM FOREST — Waveform Only — LEAKAGE-CONTROLLED (grouped split)")
    log("=" * 70)
    log("Group id = hash of the full 572-feature waveform vector.")
    log("Identical waveforms are forced into the SAME split side.")
    log()
    log(f"Dataset : {PARQUET}")
    log(f"A-scans : {n}")
    log(f"Unique feature-vector groups : {n_groups} "
        f"({n - n_groups} duplicate rows, {100*(n-n_groups)/n:.2f}%)")
    log(f"Features: {len(feat_cols)} (metadata excluded)")
    log(f"Classes : {dict(zip(classes, counts))}")
    log(f"RF      : 300 trees, max_features=sqrt, min_samples_leaf=2, "
        f"class_weight=balanced, seed={RANDOM_SEED}")
    log()

    # ==================================================================
    # (A) BASELINE — reproduce the ORIGINAL random split (same seed)
    # ==================================================================
    log("-" * 70)
    log("(A) BASELINE: random stratified split (reproduces the original)")
    log("-" * 70)
    Xtr_r, Xte_r, ytr_r, yte_r = train_test_split(
        X, y, test_size=TEST_SIZE, random_state=RANDOM_SEED, stratify=y
    )
    rf_r = make_rf()
    print("  training baseline RF ...")
    rf_r.fit(Xtr_r, ytr_r)
    yp_r = rf_r.predict(Xte_r)
    acc_r = accuracy_score(yte_r, yp_r)
    bal_r = balanced_accuracy_score(yte_r, yp_r)
    cv_r = cross_val_score(
        make_rf(), Xtr_r, ytr_r,
        cv=StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_SEED),
        scoring="balanced_accuracy", n_jobs=-1,
    )
    f1_r = per_class_f1(yte_r, yp_r)
    log(f"  Test Accuracy          : {acc_r:.4f}")
    log(f"  Test Balanced Accuracy : {bal_r:.4f}")
    log(f"  CV Balanced Accuracy   : {cv_r.mean():.4f} +/- {cv_r.std():.4f}")
    log()

    # ==================================================================
    # (B) GROUPED — group-aware, stratified-by-class split
    # ==================================================================
    log("-" * 70)
    log("(B) LEAKAGE-CONTROLLED: group-aware split (no shared waveform)")
    log("-" * 70)

    # Held-out test via GroupShuffleSplit (disjoint groups, ~20%)
    gss = GroupShuffleSplit(n_splits=1, test_size=TEST_SIZE, random_state=RANDOM_SEED)
    tr_idx, te_idx = next(gss.split(X, y, groups=gid))
    Xtr, Xte = X[tr_idx], X[te_idx]
    ytr, yte = y[tr_idx], y[te_idx]
    gtr, gte = gid[tr_idx], gid[te_idx]

    # Hard assertion: no group leaks across the train/test boundary
    inter = set(np.unique(gtr)) & set(np.unique(gte))
    log(f"  Train rows={len(tr_idx)}  Test rows={len(te_idx)}")
    log(f"  Train groups={len(np.unique(gtr))}  Test groups={len(np.unique(gte))}")
    log(f"  Groups appearing in BOTH train and test: {len(inter)}")
    assert len(inter) == 0, "LEAKAGE: a group appears in both train and test!"
    log("  ASSERT OK: train/test group intersection is empty.")
    log(f"  Test class distribution: "
        f"{dict(zip(*np.unique(yte, return_counts=True)))}")
    log()

    rf_g = make_rf()
    print("  training grouped RF ...")
    rf_g.fit(Xtr, ytr)
    yp_g = rf_g.predict(Xte)
    acc_g = accuracy_score(yte, yp_g)
    bal_g = balanced_accuracy_score(yte, yp_g)

    # CV: StratifiedGroupKFold on the TRAIN portion only
    sgkf = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=RANDOM_SEED)
    cv_scores = []
    for k, (cv_tr, cv_va) in enumerate(sgkf.split(Xtr, ytr, groups=gtr), 1):
        # verify no group leak in each CV fold
        leak = set(np.unique(gtr[cv_tr])) & set(np.unique(gtr[cv_va]))
        assert len(leak) == 0, f"LEAKAGE in CV fold {k}"
        m = make_rf()
        m.fit(Xtr[cv_tr], ytr[cv_tr])
        s = balanced_accuracy_score(ytr[cv_va], m.predict(Xtr[cv_va]))
        cv_scores.append(s)
        print(f"    CV fold {k}: balanced_acc={s:.4f} (no group leak)")
    cv_scores = np.array(cv_scores)
    f1_g = per_class_f1(yte, yp_g)

    log(f"  Test Accuracy          : {acc_g:.4f}")
    log(f"  Test Balanced Accuracy : {bal_g:.4f}")
    log(f"  CV Balanced Accuracy   : {cv_scores.mean():.4f} +/- {cv_scores.std():.4f}")
    log("  (CV via StratifiedGroupKFold, every fold asserted leak-free)")
    log()
    log("  Classification report (grouped test set):")
    log(classification_report(yte, yp_g, target_names=LABEL_ORDER,
                              labels=LABEL_ORDER, zero_division=0))
    log("  Confusion matrix (rows=true, cols=pred):")
    log(fmt_cm(confusion_matrix(yte, yp_g, labels=LABEL_ORDER)))
    log()

    # ==================================================================
    # (C) DELTA TABLE
    # ==================================================================
    log("=" * 70)
    log("(C) DELTA — random (leaky) vs grouped (leak-free)")
    log("=" * 70)
    log(f"{'Metric':<26}{'Random':>10}{'Grouped':>10}{'Delta':>10}")
    log("-" * 56)
    log(f"{'Balanced accuracy':<26}{bal_r:>10.4f}{bal_g:>10.4f}{bal_g-bal_r:>+10.4f}")
    log(f"{'Accuracy':<26}{acc_r:>10.4f}{acc_g:>10.4f}{acc_g-acc_r:>+10.4f}")
    log(f"{'CV balanced acc (mean)':<26}{cv_r.mean():>10.4f}{cv_scores.mean():>10.4f}"
        f"{cv_scores.mean()-cv_r.mean():>+10.4f}")
    log()
    log(f"{'F1 by class':<26}{'Random':>10}{'Grouped':>10}{'Delta':>10}")
    log("-" * 56)
    for c in LABEL_ORDER:
        log(f"{c:<26}{f1_r[c]:>10.4f}{f1_g[c]:>10.4f}{f1_g[c]-f1_r[c]:>+10.4f}")
    log()

    # ==================================================================
    # (D) CONCLUSION
    # ==================================================================
    drop = bal_r - bal_g
    worst = min(LABEL_ORDER, key=lambda c: f1_g[c] - f1_r[c])
    log("=" * 70)
    log("(D) CONCLUSION")
    log("=" * 70)
    log(f"Removing the duplicate-waveform leakage drops balanced accuracy by "
        f"{drop:+.4f} ({bal_r:.4f} -> {bal_g:.4f}).")
    log(f"Largest per-class F1 degradation: class '{worst}' "
        f"(Delta={f1_g[worst]-f1_r[worst]:+.4f}).")
    if drop > 0.01:
        log(f"=> The original random-split result was OPTIMISTIC by ~"
            f"{drop:.4f} balanced-accuracy points due to 16.76% duplicate "
            f"waveforms scattered across train/test.")
    else:
        log("=> The grouped split is within ~0.01 of the random split; "
            "leakage impact on this metric is minor.")
    log()

    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text("\n".join(lines), encoding="utf-8")
    print(f"\nReport saved -> {REPORT}")


if __name__ == "__main__":
    main()

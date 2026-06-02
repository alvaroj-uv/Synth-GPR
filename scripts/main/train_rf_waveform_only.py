#!/usr/bin/env python3
"""
Train Random Forest using waveform features ONLY (no metadata).

This implements the core novelty: predicting fouling class from GPR Ez
waveform features alone, without relying on lab metadata.

Usage:
    python scripts/main/train_rf_waveform_only.py [--parquet PATH] [--model-out PATH] [--report PATH]

Output:
    Model file     — trained Random Forest (waveform features only)
    Report file    — metrics and feature importances
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.metrics import (
    classification_report, confusion_matrix, accuracy_score, balanced_accuracy_score
)
import argparse

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

# Metadata columns to EXCLUDE (keep only waveform features)
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


def parse_args():
    p = argparse.ArgumentParser(description="Train RF on waveform features only")
    p.add_argument("--parquet", type=Path, default=Path("output/dataset_80k_features.parquet"),
                  help="Input parquet path")
    p.add_argument("--model-out", type=Path, default=Path("output/rf_model_waveform_only.joblib"),
                  help="Output model path")
    p.add_argument("--report", type=Path, default=Path("output/rf_results_waveform_only.txt"),
                  help="Output report path")
    return p.parse_args()


def load_data_waveform_only(parquet_path):
    """Load parquet and select only waveform features (exclude metadata)."""
    df = pd.read_parquet(parquet_path)

    # Exclude: sample_id, source, label, and all metadata fields
    exclude_cols = {"sample_id", "source", "label"} | METADATA_FIELDS

    feat_cols = [c for c in df.columns if c not in exclude_cols]

    print(f"Excluding {len(METADATA_FIELDS)} metadata fields")
    print(f"Using {len(feat_cols)} waveform features")

    X = df[feat_cols].values.astype("float32")
    y = df["label"].values

    return X, y, feat_cols


def print_and_log(msg, fh):
    print(msg)
    fh.write(msg + "\n")


def main():
    args = parse_args()

    print(f"Loading {args.parquet} ...")
    X, y, feat_cols = load_data_waveform_only(args.parquet)

    print(f"  Samples   : {X.shape[0]}")
    print(f"  Features  : {X.shape[1]} (waveform only, metadata excluded)")

    classes, counts = np.unique(y, return_counts=True)
    print(f"  Classes   : {dict(zip(classes, counts))}")
    print()

    # Train / test split (stratified)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=TEST_SIZE, random_state=RANDOM_SEED, stratify=y
    )

    # Random Forest with balanced weights
    rf = RandomForestClassifier(
        n_estimators=300,
        max_features="sqrt",
        min_samples_leaf=2,
        class_weight="balanced",
        random_state=RANDOM_SEED,
        n_jobs=-1,
    )

    print("Training Random Forest (300 trees, balanced weights) ...")
    print("  Using WAVEFORM FEATURES ONLY (no metadata)")
    print()
    rf.fit(X_train, y_train)
    print("Training complete.\n")

    # Evaluation
    y_pred = rf.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    bal_acc = balanced_accuracy_score(y_test, y_pred)

    # Cross-validation
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_SEED)
    cv_scores = cross_val_score(rf, X_train, y_train,
                                cv=cv, scoring="balanced_accuracy", n_jobs=-1)

    # Feature importances
    importances = pd.Series(rf.feature_importances_, index=feat_cols)
    top20 = importances.nlargest(20)

    # Write report
    args.report.parent.mkdir(parents=True, exist_ok=True)
    with open(args.report, "w") as fh:
        def log(msg=""):
            print_and_log(msg, fh)

        log("=" * 60)
        log("RANDOM FOREST — Waveform Features Only")
        log("=" * 60)
        log("CORE NOVELTY: Predicting fouling class from GPR Ez waveform")
        log("features ALONE, without metadata")
        log()
        log(f"Dataset       : {args.parquet}")
        log(f"Samples       : {X.shape[0]}  (train={len(X_train)}, test={len(X_test)})")
        log(f"Features      : {X.shape[1]} (WAVEFORM ONLY)")
        log(f"Metadata excl.: {len(METADATA_FIELDS)} fields")
        log(f"Classes       : {dict(zip(classes, counts))}")
        log()
        log(f"Test Accuracy          : {acc:.4f}")
        log(f"Test Balanced Accuracy : {bal_acc:.4f}")
        log(f"CV Balanced Accuracy   : {cv_scores.mean():.4f} +/- {cv_scores.std():.4f}")
        log()
        log("Classification Report (test set):")
        log(classification_report(y_test, y_pred, target_names=LABEL_ORDER,
                                  labels=LABEL_ORDER, zero_division=0))
        log("Confusion Matrix (rows=true, cols=pred):")
        cm = confusion_matrix(y_test, y_pred, labels=LABEL_ORDER)
        header = f"{'':>6}" + "".join(f"{c:>6}" for c in LABEL_ORDER)
        log(header)
        for i, row_label in enumerate(LABEL_ORDER):
            row = f"{row_label:>6}" + "".join(f"{v:>6}" for v in cm[i])
            log(row)
        log()
        log("Top-20 Feature Importances:")
        for feat, imp in top20.items():
            log(f"  {imp:.4f}  {feat}")
        log()
        log(f"Model saved : {args.model_out}")

    # Save model
    args.model_out.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(rf, args.model_out)
    print(f"Model saved -> {args.model_out}")
    print(f"Report saved -> {args.report}")


if __name__ == "__main__":
    main()

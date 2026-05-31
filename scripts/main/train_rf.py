#!/usr/bin/env python3
"""
Train a Random Forest classifier on the dataset_1k feature parquet.

Usage:
    python scripts/main/train_rf.py

Output:
    output/rf_model.joblib     — trained model
    output/rf_results.txt      — metrics report
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
from sklearn.preprocessing import LabelEncoder

PARQUET   = Path("output/dataset_1k_features.parquet")
MODEL_OUT = Path("output/rf_model.joblib")
REPORT    = Path("output/rf_results.txt")

import argparse as _ap
def _parse_args():
    p = _ap.ArgumentParser()
    p.add_argument("--parquet",     default=None)
    p.add_argument("--model-out",   default=None)
    p.add_argument("--report",      default=None)
    return p.parse_args()

LABEL_ORDER = ["C", "MC", "MF", "F", "HF"]   # ascending fouling severity
TEST_SIZE   = 0.2
RANDOM_SEED = 42


def load_data(parquet_path):
    df = pd.read_parquet(parquet_path)
    feat_cols = [c for c in df.columns if c not in ("sample_id", "label", "source")]
    X = df[feat_cols].values.astype("float32")
    y = df["label"].values
    return X, y, feat_cols


def print_and_log(msg, fh):
    print(msg)
    fh.write(msg + "\n")


def main():
    args      = _parse_args()
    parquet   = Path(args.parquet)   if args.parquet   else PARQUET
    model_out = Path(args.model_out) if args.model_out else MODEL_OUT
    report    = Path(args.report)    if args.report    else REPORT
    print(f"Loading {parquet} ...")
    X, y, feat_cols = load_data(parquet)
    print(f"  Samples  : {X.shape[0]}")
    print(f"  Features : {X.shape[1]}")
    print(f"  (includes metadata + signal features)")

    classes, counts = np.unique(y, return_counts=True)
    print(f"  Classes  : {dict(zip(classes, counts))}")
    print()

    # Train / test split (stratified to preserve class ratios)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=TEST_SIZE, random_state=RANDOM_SEED, stratify=y
    )

    # Random Forest with class_weight='balanced' to handle imbalance
    rf = RandomForestClassifier(
        n_estimators=300,
        max_features="sqrt",
        min_samples_leaf=2,
        class_weight="balanced",
        random_state=RANDOM_SEED,
        n_jobs=-1,
    )

    print("Training Random Forest (300 trees, balanced weights) ...")
    rf.fit(X_train, y_train)
    print("Training complete.\n")

    # --- Evaluation ---
    y_pred = rf.predict(X_test)
    acc      = accuracy_score(y_test, y_pred)
    bal_acc  = balanced_accuracy_score(y_test, y_pred)

    # Cross-validation on training set (5-fold stratified)
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_SEED)
    cv_scores = cross_val_score(rf, X_train, y_train,
                                cv=cv, scoring="balanced_accuracy", n_jobs=-1)

    # Top feature importances
    importances = pd.Series(rf.feature_importances_, index=feat_cols)
    top20 = importances.nlargest(20)

    with open(report, "w") as fh:
        def log(msg=""): print_and_log(msg, fh)

        log("=" * 60)
        log("RANDOM FOREST — GPR Fouling Classification")
        log("=" * 60)
        log(f"Dataset   : {parquet}")
        log(f"Samples   : {X.shape[0]}  (train={len(X_train)}, test={len(X_test)})")
        log(f"Features  : {X.shape[1]}")
        log(f"Classes   : {dict(zip(classes, counts))}")
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
        log(f"Model saved : {model_out}")

    # Save model
    model_out.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(rf, model_out)
    print(f"Model saved -> {model_out}")
    print(f"Report saved -> {report}")


if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
    main()

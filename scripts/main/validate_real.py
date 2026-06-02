#!/usr/bin/env python3
"""
Field Validation: synthetic-trained RF vs REAL GPR traces.

Loads the waveform-only Random Forest trained on the synthetic dataset and
evaluates it on the 101 real field traces (feature_dataset_real.csv), measuring
the simulation -> real domain gap.

Key points:
  - Uses the EXACT feat_cols order from train_rf_waveform_only (572 features).
  - Real features were produced by the identical extract_features pipeline.
  - Reports global + balanced accuracy, per-class report, confusion matrix.
  - Because the real set is heavily imbalanced (71% 'F'), balanced accuracy
    is the honest headline metric.

Usage:
    python scripts/main/validate_real.py
"""

import sys
import argparse
import importlib.util
from pathlib import Path

import numpy as np
import pandas as pd
import joblib
from sklearn.metrics import (
    classification_report, confusion_matrix,
    accuracy_score, balanced_accuracy_score,
)

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

LABEL_ORDER = ["C", "MC", "MF", "F", "HF"]


def parse_args():
    p = argparse.ArgumentParser(description="Validate synthetic RF on real traces")
    p.add_argument("--model", type=Path,
                   default=ROOT / "output" / "rf_model_waveform_only.joblib")
    p.add_argument("--parquet", type=Path,
                   default=ROOT / "output" / "dataset_80k_features.parquet",
                   help="Parquet the model was trained on (for feat_cols order)")
    p.add_argument("--real", type=Path,
                   default=ROOT / "docs" / "input" / "feature_dataset_real.csv")
    p.add_argument("--report", type=Path,
                   default=ROOT / "output" / "rf_validation_real.txt")
    return p.parse_args()


def get_feat_cols(parquet_path):
    """Reconstruct the exact waveform feat_cols used at training time."""
    spec = importlib.util.spec_from_file_location(
        "trainmod", ROOT / "scripts" / "main" / "train_rf_waveform_only.py"
    )
    t = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(t)
    df = pd.read_parquet(parquet_path, columns=None)
    exclude = {"sample_id", "source", "label"} | t.METADATA_FIELDS
    return [c for c in df.columns if c not in exclude]


def main():
    args = parse_args()
    global MODEL_PATH, REAL_CSV, REPORT_PATH
    MODEL_PATH, REAL_CSV, REPORT_PATH = args.model, args.real, args.report

    print(f"Loading model: {MODEL_PATH.name}")
    rf = joblib.load(MODEL_PATH)

    feat_cols = get_feat_cols(args.parquet)
    assert len(feat_cols) == rf.n_features_in_, "feature count mismatch"

    print(f"Loading real traces: {REAL_CSV.name}")
    real = pd.read_csv(REAL_CSV)

    # Order columns EXACTLY as the model expects
    X = real[feat_cols].values.astype("float32")
    y_true = real["FI_class"].values

    y_pred = rf.predict(X)

    acc = accuracy_score(y_true, y_pred)
    bal_acc = balanced_accuracy_score(y_true, y_pred)

    # Labels actually present in the real set (for honest reporting)
    present = [c for c in LABEL_ORDER if c in set(y_true)]

    lines = []

    def log(msg=""):
        print(msg)
        lines.append(msg)

    log("=" * 60)
    log("FIELD VALIDATION — Synthetic-trained RF on REAL traces")
    log("=" * 60)
    log(f"Model        : {MODEL_PATH.name}")
    log(f"Real samples : {len(real)}")
    log(f"Features     : {X.shape[1]} (waveform only, identical pipeline)")
    log(f"Model classes: {list(rf.classes_)}")
    log()
    log(f"Real class distribution:")
    for c in present:
        log(f"   {c:>3}: {(y_true == c).sum()}")
    log()
    log(f"Global Accuracy        : {acc:.4f}")
    log(f"Balanced Accuracy      : {bal_acc:.4f}   <-- headline (imbalanced set)")
    log(f"(synthetic test baseline: 0.7083 balanced acc)")
    log()
    log("Classification Report:")
    log(classification_report(y_true, y_pred, labels=present,
                              target_names=present, zero_division=0))
    log("Confusion Matrix (rows=true, cols=pred):")
    cm = confusion_matrix(y_true, y_pred, labels=LABEL_ORDER)
    header = f"{'':>6}" + "".join(f"{c:>6}" for c in LABEL_ORDER)
    log(header)
    for i, rl in enumerate(LABEL_ORDER):
        log(f"{rl:>6}" + "".join(f"{v:>6}" for v in cm[i]))
    log()

    # Adjacent-class accuracy (off-by-one on the ordinal FI scale)
    idx = {c: i for i, c in enumerate(LABEL_ORDER)}
    dist = np.abs([idx[a] - idx[b] for a, b in zip(y_true, y_pred)])
    log(f"Exact class accuracy   : {(dist == 0).mean():.4f}")
    log(f"Within +/-1 class       : {(dist <= 1).mean():.4f}")

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")
    print(f"\nReport saved -> {REPORT_PATH}")


if __name__ == "__main__":
    main()

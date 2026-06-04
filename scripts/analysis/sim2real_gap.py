#!/usr/bin/env python3
"""
SIM -> REAL DOMAIN GAP — the core thesis experiment.

Question: does a waveform-only classifier trained on SYNTHETIC GPR data
recognize fouling in REAL field traces?

Method (with every correction learned this session):
  - Labels use the NOTEBOOK bins (0/10/20/30/40), NOT Selig (1/10/20/40),
    on BOTH sides. Synthetic FI = Lab_FI; real FI = pandoscope estimate.
  - Real features come from the coda-aligned, peak-normalized pipeline
    (feature_dataset_rojas.csv) so amplitude/window match training.
  - Train RF (waveform-only) on synthetic, test on the 108 real Site-1 traces.
  - Report honest metrics: balanced accuracy, within-±1-class (ordinal),
    confusion matrix. Per-trace scoring (block regularization needs Pk, TODO).

Caveat: the real set is the paper's Site 1 — its WORST site (~50%, antenna at
10 cm vs 50 cm). A poor score conflates sim->real gap with atypical acquisition.

Usage:
    python scripts/analysis/sim2real_gap.py
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    balanced_accuracy_score, accuracy_score,
    classification_report, confusion_matrix,
)

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

# Coda-aligned synthetic parquet: SAME 250-sample coda time-support as the real
# traces, SAME 572 extract_features columns. This is the only fair training set.
SYN_PARQUET = ROOT / "output" / "dataset_coda_features.parquet"
# 80k parquet only used to fetch continuous Lab_FI (for notebook-bin relabeling).
FI_PARQUET = ROOT / "output" / "dataset_80k_features.parquet"
# Real traces: coda-aligned, extract_features (572 cols) — matches SYN_PARQUET.
REAL_CSV = ROOT / "docs" / "input" / "feature_dataset_real.csv"
REPORT = ROOT / "output" / "sim2real_gap.txt"
ORDER = ["C", "MC", "MF", "F", "HF"]

# Metadata columns to exclude (waveform-only); same set as train_rf_waveform_only
META = {
    "pvc", "moisture", "achieved_density", "porosity",
    "Lab_FI", "Lab_FI_local", "Lab_FR", "Lab_er_bulk_leng", "Lab_bulk_eps",
    "Lab_alpha_400MHz_npm", "Lab_alpha_2GHz_npm", "Lab_surface_R",
    "Lab_LDCP_FI_est", "Lab_LDCP_FH", "Lab_LDCP_qs_mean", "Lab_clean_ballast_mm",
    "mc_rock_fraction", "mc_fouling_fraction", "mc_subgrade_fraction",
    "mc_formation_fraction", "mc_void_fraction", "mc_pvc_measured",
    "ballast_top_y", "ballast_bottom_y", "mc_y_max", "mc_y_min",
    "mc_y_local_max", "ldcp_x", "Lab_P4", "Lab_P200", "Lab_Porosity",
}


def notebook_bins(fi):
    """Rojas notebook classification (cell 12): 0/10/20/30/40."""
    out = np.empty(len(fi), dtype=object)
    out[fi < 10] = "C"
    out[(fi >= 10) & (fi < 20)] = "MC"
    out[(fi >= 20) & (fi < 30)] = "MF"
    out[(fi >= 30) & (fi < 40)] = "F"
    out[fi >= 40] = "HF"
    return out


def main():
    log_lines = []

    def log(m=""):
        print(m)
        log_lines.append(m)

    # ---- real features define the COMMON feature space ----
    real = pd.read_csv(REAL_CSV)
    real_feats = [c for c in real.columns if c not in ("ID", "FI", "FI_class")]

    # ---- synthetic: coda-aligned features + continuous Lab_FI (from 80k parquet)
    syn = pd.read_parquet(SYN_PARQUET)
    fi_map = pd.read_parquet(FI_PARQUET, columns=["sample_id", "Lab_FI"])
    syn = syn.merge(fi_map, on="sample_id", how="inner")
    common = [c for c in real_feats if c in syn.columns]
    missing = [c for c in real_feats if c not in syn.columns]

    log("=" * 64)
    log("SIM -> REAL DOMAIN GAP  (notebook bins, waveform-only)")
    log("=" * 64)
    log(f"Real features            : {len(real_feats)}")
    log(f"Shared with synthetic    : {len(common)}")
    log(f"Real-only (no synth twin): {len(missing)}  -> dropped from experiment")
    if missing:
        log(f"  e.g. {missing[:8]}")
    log()

    X_train = syn[common].values.astype("float32")
    y_train = notebook_bins(syn["Lab_FI"].values)
    X_real = real[common].values.astype("float32")
    y_real = notebook_bins(real["FI"].values)

    log(f"Synthetic train: {X_train.shape[0]} samples, "
        f"dist={pd.Series(y_train).value_counts().reindex(ORDER).to_dict()}")
    log(f"Real test      : {X_real.shape[0]} samples (Site 1), "
        f"dist={pd.Series(y_real).value_counts().reindex(ORDER).to_dict()}")
    log()

    rf = RandomForestClassifier(
        n_estimators=300, max_features="sqrt", min_samples_leaf=2,
        class_weight="balanced", random_state=42, n_jobs=-1,
    )
    log("Training RF on synthetic (waveform-only, notebook bins)...")
    rf.fit(X_train, y_train)

    y_pred = rf.predict(X_real)
    bal = balanced_accuracy_score(y_real, y_pred)
    acc = accuracy_score(y_real, y_pred)

    idx = {c: i for i, c in enumerate(ORDER)}
    dist = np.abs([idx[a] - idx[b] for a, b in zip(y_real, y_pred)])

    log()
    log(f"Balanced accuracy  : {bal:.4f}")
    log(f"Global accuracy    : {acc:.4f}")
    log(f"Exact-class        : {(dist == 0).mean():.4f}")
    log(f"Within +/-1 class  : {(dist <= 1).mean():.4f}")
    log()
    present = [c for c in ORDER if c in set(y_real)]
    log("Classification report:")
    log(classification_report(y_real, y_pred, labels=present,
                              target_names=present, zero_division=0))
    log("Confusion (rows=true, cols=pred): " + str(ORDER))
    cm = confusion_matrix(y_real, y_pred, labels=ORDER)
    for rl, row in zip(ORDER, cm):
        log(f"  {rl:>3}: {row}")
    log()
    log("CAVEAT: real set = paper Site 1 (worst site, antenna 10 cm). A poor")
    log("score mixes the sim->real gap with atypical acquisition conditions.")
    log("TODO: block-regularize per 20 m along Pk for paper-comparable metric")
    log("      (needs each trace's Pk position, not present in current CSVs).")

    REPORT.write_text("\n".join(log_lines), encoding="utf-8")
    print(f"\nReport saved -> {REPORT}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
SIM -> REAL gap with BLOCK REGULARIZATION along the track (paper method).

The Rojas-Vivanco field-validation notebook (Application_ML_2025) never scores
per-trace. It orders predictions spatially along the track (Pk) and applies
`regularizar_bloques`: the mode class within each fixed-size block (5 m, 20 m),
ties broken toward the higher class. We reproduce that here.

We have no Pk in metres, but df_GPR_match_filtrado carries `n_traza` — the
trace's index in the continuous GPR sweep, i.e. a spatial-order proxy. We sort
by n_traza and regularize by blocks of K traces.

Pipeline (all session corrections applied):
  - Train RF (waveform-only) on the coda-aligned synthetic parquet.
  - Labels: notebook bins (0/10/20/30/40) on both sides, from continuous FI.
  - Predict on the 101 real Site-1 traces, order by n_traza, regularize.
  - Report per-trace vs per-block (K=5, K=20) balanced acc + within-±1.

Usage:
    python scripts/main/sim2real_regularized.py
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import balanced_accuracy_score, accuracy_score, confusion_matrix

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

SYN_PARQUET = ROOT / "output" / "dataset_coda_features.parquet"
FI_PARQUET = ROOT / "output" / "dataset_80k_features.parquet"
REAL_CSV = ROOT / "docs" / "input" / "feature_dataset_real.csv"
RAW_GPR = ROOT / "docs" / "input" / "Señales_Brutas" / "df_GPR_match_filtrado.pkl"
REPORT = ROOT / "output" / "sim2real_regularized.txt"

ORDER = ["C", "MC", "MF", "F", "HF"]
RANK = {c: i for i, c in enumerate(ORDER)}


def notebook_bins(fi):
    out = np.empty(len(fi), dtype=object)
    fi = np.asarray(fi, dtype=float)
    out[fi < 10] = "C"
    out[(fi >= 10) & (fi < 20)] = "MC"
    out[(fi >= 20) & (fi < 30)] = "MF"
    out[(fi >= 30) & (fi < 40)] = "F"
    out[fi >= 40] = "HF"
    return out


def regularizar_bloques(labels, block):
    """Mode per fixed-size block; ties -> higher (more-fouled) class.
    Faithful port of the notebook's regularizar_bloques."""
    out = []
    for i in range(0, len(labels), block):
        chunk = list(labels[i:i + block])
        counts = {c: chunk.count(c) for c in set(chunk)}
        mx = max(counts.values())
        winners = [c for c, n in counts.items() if n == mx]
        # tie-break: keep the higher-ranked (more fouled) class
        keep = max(winners, key=lambda c: RANK[c])
        out.extend([keep] * len(chunk))
    return np.array(out, dtype=object)


def metrics(y_true, y_pred):
    bal = balanced_accuracy_score(y_true, y_pred)
    acc = accuracy_score(y_true, y_pred)
    d = np.abs([RANK[a] - RANK[b] for a, b in zip(y_true, y_pred)])
    return bal, acc, (d == 0).mean(), (d <= 1).mean()


def main():
    lines = []

    def log(m=""):
        print(m); lines.append(m)

    # --- train RF on synthetic (coda-aligned, notebook bins) ---
    syn = pd.read_parquet(SYN_PARQUET)
    fi_map = pd.read_parquet(FI_PARQUET, columns=["sample_id", "Lab_FI"])
    syn = syn.merge(fi_map, on="sample_id", how="inner")

    real = pd.read_csv(REAL_CSV)
    feat = [c for c in real.columns if c not in ("ID", "FI", "FI_class")]
    feat = [c for c in feat if c in syn.columns]

    X_train = syn[feat].values.astype("float32")
    y_train = notebook_bins(syn["Lab_FI"].values)

    rf = RandomForestClassifier(
        n_estimators=300, max_features="sqrt", min_samples_leaf=2,
        class_weight="balanced", random_state=42, n_jobs=-1)
    log("Training RF on coda-aligned synthetic (notebook bins)...")
    rf.fit(X_train, y_train)

    # --- predict on real, attach spatial order n_traza ---
    raw = pd.read_pickle(RAW_GPR)[["ID", "n_traza"]]
    real = real.merge(raw, on="ID", how="left").sort_values("n_traza").reset_index(drop=True)

    X_real = real[feat].values.astype("float32")
    y_true = notebook_bins(real["FI"].values)
    y_pred = rf.predict(X_real)

    log("=" * 64)
    log("SIM -> REAL with block regularization along n_traza (Site 1)")
    log("=" * 64)
    log(f"Train: {X_train.shape[0]} synth | Test: {len(real)} real")
    log(f"Real dist: {pd.Series(y_true).value_counts().reindex(ORDER).to_dict()}")
    log()

    log(f"{'method':<22}{'bal_acc':>9}{'acc':>8}{'exact':>8}{'±1':>8}")
    for name, yp in [
        ("per-trace (raw)", y_pred),
        ("regularized K=5", regularizar_bloques(y_pred, 5)),
        ("regularized K=20", regularizar_bloques(y_pred, 20)),
    ]:
        bal, acc, ex, w1 = metrics(y_true, yp)
        log(f"{name:<22}{bal:>9.3f}{acc:>8.3f}{ex:>8.3f}{w1:>8.3f}")
    log()

    # confusion for K=20 (paper's headline regularization)
    yp20 = regularizar_bloques(y_pred, 20)
    log("Confusion K=20 (rows=true, cols=pred): " + str(ORDER))
    cm = confusion_matrix(y_true, yp20, labels=ORDER)
    for rl, row in zip(ORDER, cm):
        log(f"  {rl:>3}: {row}")
    log()
    log("NOTE: n_traza is a spatial-ORDER proxy (no metres), so block size K is")
    log("in traces, not 20 m. Direction of effect (regularization helps) is what")
    log("matters; absolute K is not metric-comparable to the paper's 20 m.")

    REPORT.write_text("\n".join(lines), encoding="utf-8")
    print(f"\nReport saved -> {REPORT}")


if __name__ == "__main__":
    main()

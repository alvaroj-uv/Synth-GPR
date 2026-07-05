#!/usr/bin/env python3
"""Train RF on the 3D rock-count dataset. Ey component (not Ez -- the GSSI
antenna model uses that orientation), raw signal (no preprocess_signal, per
this session's 2D finding that it hurts synthetic-only tasks).

CAVEAT: n_rocks is deterministic per target_phi with RCPGeneratorPacking (the
engine computes N analytically from phi -- see generate_dataset_3d.py log),
so this N=20 set really has only 5 distinct target values (4 seed-repeats
each, varying only rock POSITIONS). Different structure from the 2D N=100 run
(circlify gave genuinely continuous per-seed count variation).
"""
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import h5py

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT))

from src.feature_extraction import extract_features  # noqa: E402

N_ROCKS_RE = re.compile(r"##\s*\[gen\]|CONFIG_target_phi:\s*([\d.]+)")


def n_rocks_for_fill(fill: float) -> int:
    # From generate_log_3d.txt (deterministic per-phi count, rcpgen)
    table = {0.30: 91, 0.45: 137, 0.60: 182, 0.75: 228, 0.90: 273}
    return table[round(fill, 2)]


def main():
    out_files = sorted(HERE.glob("sample3d_*.out"))
    print(f"Found {len(out_files)} .out files")

    signals = {}
    n_rocks = {}
    dt = None
    t_ns = None

    for out_path in out_files:
        tag = out_path.stem
        m = re.match(r"sample3d_f(\d+)_s(\d+)", tag)
        fill = int(m.group(1)) / 100.0
        n_rocks[tag] = n_rocks_for_fill(fill)

        with h5py.File(out_path, "r") as f:
            sig = f["rxs/rx1/Ey"][()]
            this_dt = float(f.attrs["dt"])
        signals[tag] = sig
        if dt is None:
            dt = this_dt
            t_ns = np.arange(len(sig)) * dt * 1e9

    tags = sorted(signals.keys())
    print(f"Loaded {len(tags)} traces, dt={dt*1e9:.5f} ns, n_samples={len(t_ns)}")

    df = pd.DataFrame({"Time": t_ns})
    for tag in tags:
        df[tag] = signals[tag]

    print("Extracting waveform features (raw Ey, no preprocessing)...")
    feat_df = extract_features(df, dt=dt, center_freq_hz=400e6)
    feat_df = feat_df.set_index("Signal").loc[tags]

    drop_cols = [c for c in feat_df.columns if c.startswith("meta_")]
    X = feat_df.drop(columns=drop_cols).select_dtypes(include=[np.number])
    y = np.array([n_rocks[t] for t in tags])

    print(f"\nFeature matrix: {X.shape[0]} samples x {X.shape[1]} features")
    print(f"Target (rock count): distinct values = {sorted(set(y.tolist()))}")

    from sklearn.ensemble import RandomForestRegressor
    from sklearn.model_selection import GroupKFold, cross_val_score

    rf = RandomForestRegressor(n_estimators=300, random_state=0, n_jobs=-1)
    # GroupKFold by fill level: with only 5 distinct targets x 4 seed-repeats,
    # a random KFold could leak (train and test seeing the same target value
    # trivially). GroupKFold keeps each fill-level's 4 repeats together,
    # giving an honest "generalize to an unseen density" test with 5 folds.
    fills = np.array([int(t.split("_")[1][1:]) for t in tags])
    gkf = GroupKFold(n_splits=5)

    r2_scores = cross_val_score(rf, X, y, cv=gkf, groups=fills, scoring="r2")
    mae_scores = -cross_val_score(rf, X, y, cv=gkf, groups=fills, scoring="neg_mean_absolute_error")

    print("\n" + "=" * 60)
    print(f"GROUP-5-FOLD CV RESULTS (N={len(tags)}, grouped by fill level)")
    print("=" * 60)
    print(f"R^2:  {r2_scores.mean():.3f} +/- {r2_scores.std():.3f}  (per-fold: {np.round(r2_scores, 3)})")
    print(f"MAE:  {mae_scores.mean():.1f} +/- {mae_scores.std():.1f} rocks")
    print(f"Target range: {y.min()}-{y.max()} rocks (span={y.max()-y.min()})")
    print("\n(compare: 2D N=100, ordinary 5-fold CV -> R^2 = 0.264 +/- 0.188)")

    rf.fit(X, y)
    importances = pd.Series(rf.feature_importances_, index=X.columns).sort_values(ascending=False)
    print("\nTop 15 features by importance (fit on full data, NOT held-out):")
    print(importances.head(15).to_string())


if __name__ == "__main__":
    main()

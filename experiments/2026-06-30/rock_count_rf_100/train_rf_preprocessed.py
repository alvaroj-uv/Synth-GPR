#!/usr/bin/env python3
"""Same as train_rf.py but applies src.signal_processing.preprocess_signal()
to each raw trace BEFORE extract_features(), matching the project's
established convention for synthetic .out files
(src/data_loader.py::load_batch_dataset calls preprocess_signal(raw, dt) on
every trace before any downstream analysis -- see
feedback_real_feature_pipeline memory: "Real traces MUST go through
preprocess_signal before extract_features, exactly like the synthetic
build" -- the earlier train_rf.py run skipped this step entirely).

direct_wave_kwargs matched to THIS geometry's actual antenna setup
(center_freq_hz=420e6, air_gap_m=0.1 -- our antenna_clearance), not the
function's 400MHz/0.3m defaults (tuned for a different real-antenna setup).
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT))

from src.data_loader import read_ascan  # noqa: E402
from src.feature_extraction import extract_features  # noqa: E402
from src.signal_processing import preprocess_signal  # noqa: E402


def main():
    out_files = sorted(HERE.glob("sample_*.out"))
    print(f"Found {len(out_files)} .out files")

    signals_raw = {}
    signals_pre = {}
    n_rocks = {}
    dt = None
    t_ns = None

    for out_path in out_files:
        tag = out_path.stem
        in_path = out_path.with_suffix(".in")
        if not in_path.exists():
            continue
        n_rocks[tag] = in_path.read_text().count("#cylinder")

        data = read_ascan(out_path, "Ez")
        signals_raw[tag] = data["signal"]
        if dt is None:
            dt = data["dt"]
            t_ns = data["t_ns"]

    tags = sorted(signals_raw.keys())
    print(f"Loaded {len(tags)} traces, dt={dt*1e9:.4f} ns, n_samples={len(t_ns)}")

    print("Applying preprocess_signal (dewow + time-gate direct-wave removal "
          "@420MHz/0.1m air gap + time-zero + bandpass 150-800MHz + peak-normalize)...")
    for tag in tags:
        treated, _ = preprocess_signal(
            signals_raw[tag], dt,
            direct_wave_kwargs={"center_freq_hz": 420e6, "air_gap_m": 0.1},
        )
        signals_pre[tag] = treated

    df = pd.DataFrame({"Time": t_ns})
    for tag in tags:
        df[tag] = signals_pre[tag]

    print("Extracting waveform features on PREPROCESSED signals...")
    feat_df = extract_features(df, dt=dt, center_freq_hz=420e6)
    feat_df = feat_df.set_index("Signal").loc[tags]

    drop_cols = [c for c in feat_df.columns if c.startswith("meta_")]
    X = feat_df.drop(columns=drop_cols).select_dtypes(include=[np.number])
    y = np.array([n_rocks[t] for t in tags])

    print(f"\nFeature matrix: {X.shape[0]} samples x {X.shape[1]} features")
    print(f"Target (rock count): min={y.min()} max={y.max()} mean={y.mean():.1f} std={y.std():.1f}")

    from sklearn.ensemble import RandomForestRegressor
    from sklearn.model_selection import KFold, cross_val_score

    rf = RandomForestRegressor(n_estimators=300, random_state=0, n_jobs=-1)
    kf = KFold(n_splits=5, shuffle=True, random_state=0)

    r2_scores = cross_val_score(rf, X, y, cv=kf, scoring="r2")
    mae_scores = -cross_val_score(rf, X, y, cv=kf, scoring="neg_mean_absolute_error")

    print("\n" + "=" * 60)
    print(f"5-FOLD CV RESULTS, PREPROCESSED (N={len(tags)})")
    print("=" * 60)
    print(f"R^2:  {r2_scores.mean():.3f} +/- {r2_scores.std():.3f}  (per-fold: {np.round(r2_scores, 3)})")
    print(f"MAE:  {mae_scores.mean():.1f} +/- {mae_scores.std():.1f} rocks  "
          f"(per-fold: {np.round(mae_scores, 1)})")
    print(f"Target range: {y.min()}-{y.max()} rocks (span={y.max()-y.min()}), "
          f"MAE/span = {mae_scores.mean()/(y.max()-y.min())*100:.1f}%")
    print("\n(compare: RAW signal, no preprocessing -> R^2 = 0.264 +/- 0.188, MAE=21.4)")

    rf.fit(X, y)
    importances = pd.Series(rf.feature_importances_, index=X.columns).sort_values(ascending=False)
    print("\nTop 15 features by importance (fit on full data, NOT held-out):")
    print(importances.head(15).to_string())

    out_csv = HERE / "rf_feature_importances_preprocessed.csv"
    importances.to_csv(out_csv, header=["importance"])
    print(f"\nSaved {out_csv}")

    results_txt = HERE / "rf_results_preprocessed.txt"
    with open(results_txt, "w") as f:
        f.write(f"N samples: {len(tags)}\n")
        f.write(f"N features: {X.shape[1]}\n")
        f.write(f"Target range: {y.min()}-{y.max()} rocks\n")
        f.write(f"R^2 (5-fold CV, preprocessed): {r2_scores.mean():.3f} +/- {r2_scores.std():.3f}\n")
        f.write(f"Per-fold R^2: {list(np.round(r2_scores, 3))}\n")
        f.write(f"MAE (5-fold CV): {mae_scores.mean():.1f} +/- {mae_scores.std():.1f} rocks\n")
        f.write("\n(compare: RAW signal, no preprocessing -> R^2 = 0.264 +/- 0.188, MAE=21.4)\n")
        f.write("\nTop 15 features:\n")
        f.write(importances.head(15).to_string())
    print(f"Saved {results_txt}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Evaluate the synthetic-trained layer-depth regressor on 112 real labeled traces.

Training: RF/XGBoost on synthetic gprMax data (clean_m, total_m labels)
Test:     112 real DZT traces with pandoscope labels (Prof_BS, Prof_BC)

Domain gap is handled by peak-normalizing BOTH synthetic and real signals
before feature extraction, so amplitude differences (V/m vs A/D counts)
don't dominate.

Usage:
    python scripts/pipeline/eval_layer_height_real.py \\
        experiments/2026-06-29/layer_height_v1/
"""

import sys
import argparse
import warnings
from pathlib import Path
import time as _time

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.model_selection import LeaveOneOut, cross_val_predict
from sklearn.metrics import mean_absolute_error, r2_score
from scipy.stats import spearmanr
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

try:
    from xgboost import XGBRegressor
    HAS_XGB = True
except ImportError:
    HAS_XGB = False

from src.feature_extraction import extract_features_from_signal
from src.data_loader import read_gprmax_hdf5

# ── Real data constants ───────────────────────────────────────────────────────
DATA_LABELED   = Path("D:/Codigo/Data_Labled")
FI_PKL         = DATA_LABELED / "Mediciones_FI/df_pandoscope_med.pkl"
TRACES_PKL     = DATA_LABELED / "Señales_Brutas/df_GPR_match_filtrado.pkl"
DT_REAL_S      = 50e-9 / 511          # ≈ 9.784e-11 s  (GSSI 400 MHz, 512 samp)
CENTER_FREQ_HZ = 420e6

# ── Synthetic constants ───────────────────────────────────────────────────────
EXCLUDE_COLS = {"sample_id", "fouled_m", "clean_m", "total_m", "eps_fouled"}

TARGET_PAIRS = [
    ("clean_m",  "Prof_BS", "Clean ballast thickness"),
    ("total_m",  "Prof_BC", "Total ballast depth"),
]


# ─────────────────────────────────────────────────────────────────────────────
# Real data loading
# ─────────────────────────────────────────────────────────────────────────────

def load_real_labeled() -> pd.DataFrame:
    df_fi     = pd.read_pickle(FI_PKL)
    df_traces = pd.read_pickle(TRACES_PKL)
    df = df_traces.merge(df_fi[["ID", "Prof_BS", "Prof_BC"]], on="ID")
    print(f"Loaded {len(df)} labeled traces")
    return df


def extract_real_features(df: pd.DataFrame) -> pd.DataFrame:
    """Extract waveform features from real DZT traces with peak normalization."""
    sample_cols = [str(i) for i in range(512) if str(i) in df.columns]
    if not sample_cols:
        sample_cols = [c for c in df.columns if isinstance(c, int)]

    rows = []
    n = len(df)
    t0 = _time.time()
    for i, (_, row) in enumerate(df.iterrows()):
        sig = row[sample_cols].values.astype(float)
        sig = sig[2:]                                   # drop DZT marker samples 0-1
        sig = sig / (np.abs(sig).max() + 1e-12)        # peak-normalize to [-1, 1]
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            feat = extract_features_from_signal(
                sig, dt=DT_REAL_S, signal_name="trace",
                center_freq_hz=CENTER_FREQ_HZ,
            )
        rows.append(feat.iloc[0].to_dict())
        if (i + 1) % 20 == 0 or (i + 1) == n:
            elapsed = _time.time() - t0
            eta = elapsed / (i + 1) * (n - i - 1)
            print(f"  {i+1:3d}/{n}  {elapsed:.0f}s elapsed  ~{eta:.0f}s remaining")
    return pd.DataFrame(rows)


# ─────────────────────────────────────────────────────────────────────────────
# Synthetic feature loading + re-extraction with normalization
# ─────────────────────────────────────────────────────────────────────────────

def extract_synth_features_normalized(exp_dir: Path, meta: pd.DataFrame) -> pd.DataFrame:
    """Re-extract synthetic features WITH peak normalization, to match real pipeline."""
    rows = []
    for _, row in meta.iterrows():
        sample_id = int(row["sample_id"])
        out_file = exp_dir / f"sample_{sample_id:04d}.out"
        df_raw = read_gprmax_hdf5(str(out_file), fields=["Ez"])
        if df_raw.empty:
            rows.append(None)
            continue
        time_arr = df_raw["Time"].values
        dt = float(time_arr[1] - time_arr[0]) if len(time_arr) > 1 else None
        ez = df_raw["rx1_Ez"].values
        ez = ez / (np.abs(ez).max() + 1e-12)          # peak-normalize
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            feat = extract_features_from_signal(
                ez, dt=dt, signal_name="rx1_Ez",
                center_freq_hz=CENTER_FREQ_HZ,
            )
        d = feat.iloc[0].to_dict()
        d["sample_id"] = sample_id
        rows.append(d)
    good = [r for r in rows if r is not None]
    return pd.DataFrame(good)


# ─────────────────────────────────────────────────────────────────────────────
# Model training + evaluation
# ─────────────────────────────────────────────────────────────────────────────

def align_columns(X_train: pd.DataFrame, X_test: pd.DataFrame):
    """Keep only columns present in both; fill missing in test with 0."""
    common = [c for c in X_train.columns if c in X_test.columns]
    missing = [c for c in X_train.columns if c not in X_test.columns]
    if missing:
        print(f"  WARNING: {len(missing)} train columns missing in test — filling with 0")
    X_test_aligned = X_test.reindex(columns=X_train.columns, fill_value=0.0)
    return X_train[common], X_test_aligned[common]


def evaluate(exp_dir: Path, feat_csv: Path, use_cached_synth: bool):
    meta = pd.read_csv(exp_dir / "metadata.csv")

    # ── Synthetic features ────────────────────────────────────────────────────
    if use_cached_synth:
        print("Loading cached synthetic features (raw Ez, not normalized)…")
        synth_df = pd.read_csv(feat_csv)
    else:
        print("Re-extracting synthetic features WITH peak normalization…")
        synth_feat = extract_synth_features_normalized(exp_dir, meta)
        synth_df = meta[["sample_id","fouled_m","clean_m","total_m","eps_fouled"]].merge(
            synth_feat, on="sample_id", how="inner"
        )

    feat_cols = [c for c in synth_df.columns
                 if c not in EXCLUDE_COLS and not c.startswith("meta_")]
    X_synth_all = (synth_df[feat_cols]
                   .select_dtypes(include=[np.number])
                   .replace([np.inf, -np.inf], np.nan)
                   .dropna(axis=1))

    # ── Real features ─────────────────────────────────────────────────────────
    print("\nLoading real labeled traces…")
    df_real = load_real_labeled()
    print("Extracting real features…")
    real_feat = extract_real_features(df_real)
    real_feat_num = (real_feat
                     .select_dtypes(include=[np.number])
                     .replace([np.inf, -np.inf], np.nan))

    # Join real features with pandoscope labels
    df_fi = pd.read_pickle(FI_PKL)
    real_feat["ID"] = df_real["ID"].values
    real_labeled = real_feat.merge(df_fi[["ID","Prof_BS","Prof_BC"]], on="ID")

    # ── Per-target evaluation ─────────────────────────────────────────────────
    models = {
        "RandomForest":    RandomForestRegressor(n_estimators=300, random_state=42, n_jobs=-1),
        "GradBoosting":    GradientBoostingRegressor(n_estimators=200, random_state=42),
    }
    if HAS_XGB:
        models["XGBoost"] = XGBRegressor(n_estimators=200, random_state=42,
                                          verbosity=0, n_jobs=-1)

    all_results = {}
    for synth_col, real_col, label in TARGET_PAIRS:
        print(f"\n{'='*60}")
        print(f"Target: {label}  ({synth_col} -> {real_col})")
        print(f"{'='*60}")

        y_synth = synth_df[synth_col].values

        # Subset real to non-NaN labels
        mask = real_labeled[real_col].notna()
        real_sub   = real_labeled[mask].reset_index(drop=True)
        y_real     = real_sub[real_col].values
        print(f"  Synthetic train n={len(y_synth)},  Real test n={len(y_real)}")

        real_feat_sub = real_sub[[c for c in real_feat_num.columns
                                   if c in real_sub.columns]]
        X_real_all = real_sub[feat_cols].select_dtypes(include=[np.number]).replace([np.inf,-np.inf],np.nan)

        # Align columns
        common = sorted(set(X_synth_all.columns) & set(X_real_all.columns))
        X_tr = X_synth_all[common].fillna(0)
        X_te = X_real_all[common].fillna(0)
        print(f"  Shared features: {len(common)}")

        results_this = {}
        for name, model in models.items():
            model.fit(X_tr, y_synth)
            y_pred = model.predict(X_te)
            mae  = mean_absolute_error(y_real, y_pred)
            r2   = r2_score(y_real, y_pred)
            rho, pval = spearmanr(y_real, y_pred)
            print(f"  {name:20s}  MAE={mae*100:.1f} cm  R²={r2:.3f}  rho={rho:+.3f} (p={pval:.3e})")
            results_this[name] = (y_real, y_pred, mae, r2, rho)

        # LOO on synthetic (sanity check that training works)
        rf_loo = RandomForestRegressor(n_estimators=300, random_state=42, n_jobs=-1)
        y_loo = cross_val_predict(rf_loo, X_tr, y_synth, cv=LeaveOneOut())
        rho_loo, _ = spearmanr(y_synth, y_loo)
        mae_loo = mean_absolute_error(y_synth, y_loo)
        print(f"  {'LOO-synth (RF)':20s}  MAE={mae_loo*100:.1f} cm  rho={rho_loo:+.3f}  (sanity)")

        all_results[(synth_col, real_col)] = results_this

        # Plot best model (RF)
        y_real_p, y_pred_p, mae_p, r2_p, rho_p = results_this["RandomForest"]
        fig, ax = plt.subplots(figsize=(5, 4))
        ax.scatter(y_real_p * 100, y_pred_p * 100, alpha=0.7, s=40, edgecolors="k", linewidths=0.3)
        lims = [min(y_real_p.min(), y_pred_p.min()) * 100 - 3,
                max(y_real_p.max(), y_pred_p.max()) * 100 + 3]
        ax.plot(lims, lims, "k--", linewidth=1)
        ax.set_xlabel(f"Pandoscope {real_col} (cm)")
        ax.set_ylabel("RF prediction (cm)")
        ax.set_title(f"Sim→Real  |  {label}\nMAE={mae_p*100:.1f}cm  R²={r2_p:.3f}  rho={rho_p:+.3f}")
        ax.grid(True, alpha=0.3)
        plt.tight_layout()
        plot_path = exp_dir / f"sim2real_{synth_col}.png"
        fig.savefig(plot_path, dpi=150, bbox_inches="tight")
        plt.close(fig)
        print(f"  Plot -> {plot_path}")

    return all_results


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("experiment_dir", type=Path,
                        help="Experiment folder with metadata.csv and sample_*.out files")
    parser.add_argument("--no-renorm", action="store_true",
                        help="Use cached feature_dataset.csv (raw Ez) instead of re-extracting "
                             "with peak normalization. Faster but may hurt sim→real transfer.")
    args = parser.parse_args()

    exp_dir  = args.experiment_dir.resolve()
    feat_csv = exp_dir / "feature_dataset.csv"

    if args.no_renorm and not feat_csv.exists():
        print("ERROR: --no-renorm requires feature_dataset.csv to exist.")
        sys.exit(1)

    evaluate(exp_dir, feat_csv, use_cached_synth=args.no_renorm)
    print("\nDone.")


if __name__ == "__main__":
    main()

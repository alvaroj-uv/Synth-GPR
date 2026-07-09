#!/usr/bin/env python3
"""
Train RF and XGBoost regressors to predict ballast layer depths from waveform features.

Target variables:
  clean_m   — clean ballast thickness (analogous to Prof_BS in pandoscope)
  total_m   — total ballast depth    (analogous to Prof_BC in pandoscope)

Training data: synthetic gprMax simulations from layer_height_v1 (99 samples)
Features: 734 waveform features (time-domain, Hilbert, freq, STFT, coda, MPM)
          Excludes meta_* and non-numeric columns.

Evaluation: leave-one-out cross-validation (small dataset) + feature importance.

Usage:
    python scripts/pipeline/train_layer_height_regressor.py \\
        experiments/2026-06-29/layer_height_v1/feature_dataset.csv
"""

import sys
import argparse
from pathlib import Path

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


TARGETS = ["clean_m", "total_m"]
LABEL_MAP = {
    "clean_m": "Clean ballast thickness (m)",
    "total_m": "Total ballast depth (m)",
}

EXCLUDE_COLS = {"sample_id", "fouled_m", "clean_m", "total_m", "eps_fouled"}


def load_dataset(csv_path: Path):
    df = pd.read_csv(csv_path)
    feat_cols = [c for c in df.columns
                 if c not in EXCLUDE_COLS and not c.startswith("meta_")]
    X = df[feat_cols].select_dtypes(include=[np.number])
    # Drop columns with any NaN or infinite values
    X = X.replace([np.inf, -np.inf], np.nan).dropna(axis=1)
    print(f"Loaded {len(df)} samples, {X.shape[1]} usable features")
    return df, X


def evaluate_model(name, model, X, y, target_label):
    loo = LeaveOneOut()
    y_pred = cross_val_predict(model, X, y, cv=loo)
    mae = mean_absolute_error(y, y_pred)
    r2 = r2_score(y, y_pred)
    rho, pval = spearmanr(y, y_pred)
    print(f"  {name:30s}  MAE={mae*100:.1f} cm   R2={r2:.3f}   rho={rho:.3f} (p={pval:.3e})")
    return y_pred, mae, r2, rho


def plot_predictions(results: dict, target: str, out_path: Path):
    fig, axes = plt.subplots(1, len(results), figsize=(5 * len(results), 4), squeeze=False)
    for ax, (name, (y_true, y_pred, mae, r2)) in zip(axes[0], results.items()):
        ax.scatter(y_true * 100, y_pred * 100, alpha=0.7, s=40)
        lims = [min(y_true.min(), y_pred.min()) * 100 - 2,
                max(y_true.max(), y_pred.max()) * 100 + 2]
        ax.plot(lims, lims, "k--", linewidth=1)
        ax.set_xlabel(f"True {LABEL_MAP[target]} (cm)")
        ax.set_ylabel("Predicted (cm)")
        ax.set_title(f"{name}\nMAE={mae*100:.1f}cm  R²={r2:.3f}")
        ax.grid(True, alpha=0.3)
    plt.tight_layout()
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  Plot -> {out_path}")


def plot_feature_importance(model, feature_names, target, out_path: Path, top_n=20):
    if not hasattr(model, "feature_importances_"):
        return
    imp = model.feature_importances_
    idx = np.argsort(imp)[::-1][:top_n]
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.barh(range(top_n), imp[idx][::-1])
    ax.set_yticks(range(top_n))
    ax.set_yticklabels([feature_names[i] for i in idx[::-1]], fontsize=7)
    ax.set_xlabel("Feature importance")
    ax.set_title(f"Top {top_n} features — {LABEL_MAP[target]}")
    plt.tight_layout()
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  Importance -> {out_path}")


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("dataset_csv", type=Path,
                        help="Path to feature_dataset.csv from extract_features_layer_height.py")
    args = parser.parse_args()

    csv_path = args.dataset_csv.resolve()
    out_dir = csv_path.parent
    df, X = load_dataset(csv_path)

    models = {
        "RandomForest": RandomForestRegressor(n_estimators=200, random_state=42, n_jobs=-1),
        "GradientBoosting": GradientBoostingRegressor(n_estimators=200, random_state=42),
    }
    if HAS_XGB:
        models["XGBoost"] = XGBRegressor(n_estimators=200, random_state=42,
                                         verbosity=0, n_jobs=-1)

    for target in TARGETS:
        y = df[target].values
        print(f"\n--- Target: {LABEL_MAP[target]} ---")
        pred_results = {}
        for name, model in models.items():
            y_pred, mae, r2, rho = evaluate_model(name, model, X, y, target)
            pred_results[name] = (y, y_pred, mae, r2)

        # Plot predictions (use RF for importance)
        plot_predictions(pred_results, target,
                         out_dir / f"predictions_{target}.png")

        # Feature importance from RF (fit on full data)
        rf = RandomForestRegressor(n_estimators=200, random_state=42, n_jobs=-1)
        rf.fit(X, y)
        plot_feature_importance(rf, list(X.columns), target,
                                out_dir / f"importance_{target}.png")

    print("\nDone.")


if __name__ == "__main__":
    main()

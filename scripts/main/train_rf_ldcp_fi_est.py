#!/usr/bin/env python3
"""
Train Random Forest to estimate Lab_LDCP_FI_est from waveform features.

Uses 10-fold stratified cross-validation on 80k samples.
Predicts Lab_LDCP_FI_est (Fouling Index from LDCP measurement).

Pipeline:
  1. Load dataset_80k_features_complete.parquet
  2. Exclude metadata except sample_id, source, label
  3. Use only 572 waveform features as predictors
  4. Target: Lab_LDCP_FI_est (regression)
  5. Train RF with 10-fold CV
  6. Report MAE, RMSE, R² per fold
"""

import sys
from pathlib import Path
from datetime import datetime

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import KFold, cross_validate
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from tqdm import tqdm

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from src.constants import PC

PARQUET_PATH = Path("output/dataset_80k_features_complete.parquet")
OUTPUT_REPORT = Path("output/rf_ldcp_fi_est_10fold.txt")

# Metadata columns to exclude (keep only waveform features)
EXCLUDE_COLS = {
    "sample_id", "source", "label",
    # Metadata (all variations)
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

def main():
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Loading parquet...")
    df = pd.read_parquet(PARQUET_PATH)
    print(f"  Shape: {df.shape}")

    # Check target variable
    target = "Lab_LDCP_FI_est"
    if target not in df.columns:
        print(f"ERROR: {target} not found in parquet")
        return

    missing_target = df[target].isna().sum()
    if missing_target > 0:
        print(f"WARNING: {missing_target} missing values in {target}, removing rows...")
        df = df.dropna(subset=[target])
        print(f"  After removal: {df.shape[0]} rows")

    # Extract features (waveform only)
    feature_cols = [c for c in df.columns if c not in EXCLUDE_COLS]
    X = df[feature_cols].copy()
    y = df[target].copy()

    print(f"  Features: {X.shape[1]} waveform features")
    print(f"  Target: {target} (regression)")
    print(f"  Samples: {X.shape[0]}")
    print(f"  Target range: [{y.min():.2f}, {y.max():.2f}]")
    print(f"  Target mean ± std: {y.mean():.2f} ± {y.std():.2f}")

    # Handle NaN in features (impute with column median)
    nan_mask = X.isna().any(axis=1)
    if nan_mask.any():
        print(f"  Imputing {nan_mask.sum()} rows with NaN features...")
        for col in X.columns:
            if X[col].isna().any():
                X[col].fillna(X[col].median(), inplace=True)

    # 10-fold cross-validation
    print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Training RF with 10-fold CV...")

    rf = RandomForestRegressor(
        n_estimators=300,
        max_features="sqrt",
        min_samples_leaf=2,
        n_jobs=-1,
        random_state=42,
        verbose=0
    )

    kf = KFold(n_splits=10, shuffle=True, random_state=42)

    # Custom scoring for detailed output
    scoring = {
        'r2': 'r2',
        'neg_mae': 'neg_mean_absolute_error',
        'neg_rmse': 'neg_mean_squared_error',
    }

    cv_results = cross_validate(
        rf, X, y,
        cv=kf,
        scoring=scoring,
        return_train_score=True,
        n_jobs=1  # Sequential to avoid multiprocessing issues
    )

    # Extract metrics
    test_r2 = cv_results['test_r2']
    test_mae = -cv_results['test_neg_mae']
    test_rmse = np.sqrt(-cv_results['test_neg_rmse'])

    train_r2 = cv_results['train_r2']
    train_mae = -cv_results['train_neg_mae']
    train_rmse = np.sqrt(-cv_results['train_neg_rmse'])

    # Train final model on full dataset for feature importance
    print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Training final model on all data...")
    rf.fit(X, y)

    # Feature importance
    importance_df = pd.DataFrame({
        'feature': feature_cols,
        'importance': rf.feature_importances_
    }).sort_values('importance', ascending=False)

    # Report
    report = f"""
=== Random Forest: Lab_LDCP_FI_est Estimation (10-Fold CV) ===

Dataset:     {PARQUET_PATH.name}
Samples:     {X.shape[0]}
Features:    {X.shape[1]} (waveform only, no metadata)
Target:      {target}

Model:
  Algorithm:    Random Forest (regression)
  Trees:        300
  Max features: sqrt
  Min samples:  2
  Random state: 42

Target Statistics:
  Mean:    {y.mean():.4f}
  Std:     {y.std():.4f}
  Range:   [{y.min():.4f}, {y.max():.4f}]

Cross-Validation Results (10 folds):
  Fold  | Train R²  | Test R²   | Train MAE | Test MAE  | Train RMSE | Test RMSE
  ------|-----------|-----------|-----------|-----------|------------|----------
"""
    for i in range(10):
        report += f"  {i+1:2d}   | {train_r2[i]:8.4f}  | {test_r2[i]:8.4f}  | {train_mae[i]:8.4f}  | {test_mae[i]:8.4f}  | {train_rmse[i]:9.4f}  | {test_rmse[i]:9.4f}\n"

    report += f"""
  ------|-----------|-----------|-----------|-----------|------------|----------
  Mean  | {train_r2.mean():8.4f}  | {test_r2.mean():8.4f}  | {train_mae.mean():8.4f}  | {test_mae.mean():8.4f}  | {train_rmse.mean():9.4f}  | {test_rmse.mean():9.4f}
  Std   | {train_r2.std():8.4f}  | {test_r2.std():8.4f}  | {train_mae.std():8.4f}  | {test_mae.std():8.4f}  | {train_rmse.std():9.4f}  | {test_rmse.std():9.4f}

Interpretation:
  - R²: Coefficient of determination (1.0 = perfect, 0.0 = mean baseline)
  - MAE: Mean absolute error (same units as target)
  - RMSE: Root mean squared error (penalizes large errors)

Top 20 Features by Importance:
"""
    for idx, row in importance_df.head(20).iterrows():
        report += f"  {row['feature']:40s} {row['importance']:6.4f} ({row['importance']*100:5.2f}%)\n"

    report += f"""
Model Performance Summary:
  Test R²:   {test_r2.mean():.4f} ± {test_r2.std():.4f}
  Test MAE:  {test_mae.mean():.4f} ± {test_mae.std():.4f}
  Test RMSE: {test_rmse.mean():.4f} ± {test_rmse.std():.4f}

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

    # Save report
    with open(OUTPUT_REPORT, 'w') as f:
        f.write(report)

    print(report)
    print(f"\n✓ Report saved to {OUTPUT_REPORT}")

    # Summary stats
    print(f"\n=== Summary ===")
    print(f"Test R²:   {test_r2.mean():.4f} ± {test_r2.std():.4f}")
    print(f"Test MAE:  {test_mae.mean():.4f} ± {test_mae.std():.4f}")
    print(f"Test RMSE: {test_rmse.mean():.4f} ± {test_rmse.std():.4f}")

if __name__ == "__main__":
    main()

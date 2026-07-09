#!/usr/bin/env python3
"""
Correlation of MPM coda features vs pandoscope FI labels.

Loads the 112 labeled real GPR traces from D:/Codigo/Data_Labled,
extracts the full waveform feature set (including MPM pole features),
and reports Spearman correlation with FI_Estimado_Medio_JRO_Final.

Usage:
    python scripts/calibration/mpm_fi_correlation.py
    python scripts/calibration/mpm_fi_correlation.py --top 30
    python scripts/calibration/mpm_fi_correlation.py --out experiments/2026-06-28/mpm_fi_corr.csv
"""

import argparse
import sys
import time
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

# --- project root on sys.path -----------------------------------------------
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from src.feature_extraction import extract_features_from_signal

DATA_LABELED = Path("D:/Codigo/Data_Labled")
# Real GPR dt: GSSI 400 MHz, 512 samp, 50 ns window
DT_REAL_S = 50e-9 / 511          # ≈ 9.784e-11 s


def load_labeled_set() -> pd.DataFrame:
    fi_path    = DATA_LABELED / "Mediciones_FI/df_pandoscope_med.pkl"
    trace_path = DATA_LABELED / "Señales_Brutas/df_GPR_match_filtrado.pkl"
    df_fi     = pd.read_pickle(fi_path)
    df_traces = pd.read_pickle(trace_path)
    df = df_traces.merge(df_fi[["ID", "FI_Estimado_Medio_JRO_Final"]], on="ID")
    print(f"Loaded {len(df)} labeled traces  (FI range {df['FI_Estimado_Medio_JRO_Final'].min():.1f}"
          f"–{df['FI_Estimado_Medio_JRO_Final'].max():.1f})")
    return df


def extract_all(df: pd.DataFrame) -> pd.DataFrame:
    """Extract waveform features from every trace. Returns rows aligned with df."""
    sample_cols = [str(i) for i in range(512) if str(i) in df.columns]
    if not sample_cols:
        # columns may be integer-typed
        sample_cols = [c for c in df.columns if isinstance(c, int)]
    rows = []
    n = len(df)
    t0 = time.time()
    for idx, row in df.iterrows():
        sig = row[sample_cols].values.astype(float)
        # Drop indices 0-1 (marker artifacts in DZT format)
        sig = sig[2:]
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            feat = extract_features_from_signal(sig, dt=DT_REAL_S, signal_name="trace")
        # feat is a 1-row DataFrame; convert to dict
        rows.append(feat.iloc[0].to_dict())
        if (idx + 1) % 10 == 0 or (idx + 1) == n:
            elapsed = time.time() - t0
            eta = elapsed / (idx + 1) * (n - idx - 1)
            print(f"  {idx+1:3d}/{n}  {elapsed:.0f}s elapsed  ~{eta:.0f}s remaining")
    return pd.DataFrame(rows)


def correlate_with_fi(feat_df: pd.DataFrame, fi_series: pd.Series,
                      top: int) -> pd.DataFrame:
    fi = fi_series.values
    results = []
    for col in feat_df.columns:
        x = feat_df[col].values
        if not np.isfinite(x).all():
            x_clean = x.copy()
            x_clean[~np.isfinite(x_clean)] = np.nanmedian(x_clean)
        else:
            x_clean = x
        try:
            rho, pval = spearmanr(x_clean, fi)
        except Exception:
            rho, pval = np.nan, np.nan
        results.append({"feature": col, "spearman_rho": rho, "pval": pval})
    corr_df = pd.DataFrame(results)
    corr_df["abs_rho"] = corr_df["spearman_rho"].abs()
    corr_df = corr_df.sort_values("abs_rho", ascending=False).reset_index(drop=True)
    return corr_df.head(top)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--top",  type=int, default=30,
                    help="Show top-N features by |rho|")
    ap.add_argument("--out",  default=None,
                    help="Save full correlation table to CSV (optional)")
    args = ap.parse_args()

    df_labeled = load_labeled_set()
    fi = df_labeled["FI_Estimado_Medio_JRO_Final"]

    print(f"\nExtracting features (dt={DT_REAL_S*1e9:.4f} ns) ...")
    feat_df = extract_all(df_labeled)
    print(f"Feature matrix: {feat_df.shape[0]} traces x {feat_df.shape[1]} features")

    if args.out:
        feat_df.to_csv(args.out.replace(".csv", "_features.csv"), index=False)

    # Drop non-numeric columns before correlating
    feat_numeric = feat_df.select_dtypes(include=[np.number])
    print(f"Numeric features: {feat_numeric.shape[1]}")

    # Full correlation table
    all_results = []
    fi_vals = fi.values
    for col in feat_numeric.columns:
        x = feat_numeric[col].values.astype(float)
        x[~np.isfinite(x)] = np.nanmedian(x) if np.isfinite(x).any() else 0.0
        try:
            rho, pval = spearmanr(x, fi_vals)
        except Exception:
            rho, pval = np.nan, np.nan
        all_results.append({"feature": col, "spearman_rho": rho, "pval": pval})
    corr_df = pd.DataFrame(all_results)
    corr_df["abs_rho"] = corr_df["spearman_rho"].abs()
    corr_df = corr_df.sort_values("abs_rho", ascending=False).reset_index(drop=True)

    if args.out:
        corr_df.to_csv(args.out, index=False)
        print(f"\nSaved full table to {args.out}")

    # Print top-N
    top_df = corr_df.head(args.top)
    print(f"\n--- Top {args.top} features by |rho| ---")
    print(f"{'rank':>4}  {'feature':<40}  {'rho':>7}  {'pval':>9}")
    print("-" * 65)
    for i, row in top_df.iterrows():
        star = "*" if row["pval"] < 0.05 else " "
        print(f"{i+1:4d}  {row['feature']:<40}  {row['spearman_rho']:+7.4f}  {row['pval']:9.4f} {star}")

    # Focused MPM summary
    mpm_feats = corr_df[corr_df["feature"].str.startswith("mpm_")].copy()
    print(f"\n--- MPM features only ({len(mpm_feats)} total) ---")
    for _, r in mpm_feats.head(10).iterrows():
        star = "*" if r["pval"] < 0.05 else " "
        print(f"  {r['feature']:<40}  rho={r['spearman_rho']:+.4f}  p={r['pval']:.4f} {star}")

    # Baseline: att_env_decay_rate
    baseline = corr_df[corr_df["feature"] == "att_env_decay_rate"]
    if not baseline.empty:
        r = baseline.iloc[0]
        print(f"\nBaseline att_env_decay_rate: rho={r['spearman_rho']:+.4f}  p={r['pval']:.4f}"
              f"  rank #{baseline.index[0]+1}/{len(corr_df)}")

    print("\nDone.")


if __name__ == "__main__":
    main()

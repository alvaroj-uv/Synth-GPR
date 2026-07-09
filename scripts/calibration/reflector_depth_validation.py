#!/usr/bin/env python3
"""
Validate physics-based reflector travel-time depth estimation.

Tests pick_reflector() + reflector_to_depth() on:
  1. All 99 synthetic layer_height_v1 .out files  → compare with clean_m
  2. 112 real labeled DZT traces                  → compare with Prof_BS

This is the Sussmann (2000) Eq.1 approach:
    d = c * t_oneway / sqrt(eps_clean)

Usage:
    python scripts/calibration/reflector_depth_validation.py \\
        experiments/2026-06-29/layer_height_v1/
"""

import sys
import argparse
import warnings
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from sklearn.metrics import mean_absolute_error
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from src.signal_processing import pick_reflector, reflector_to_depth
from src.data_loader import read_gprmax_hdf5

# ── constants ─────────────────────────────────────────────────────────────────
DATA_LABELED   = Path("D:/Codigo/Data_Labled")
FI_PKL         = DATA_LABELED / "Mediciones_FI/df_pandoscope_med.pkl"
TRACES_PKL     = DATA_LABELED / "Señales_Brutas/df_GPR_match_filtrado.pkl"
DT_REAL_S      = 50e-9 / 511
EPS_CLEAN      = 3.45
SKIP_NS        = 2.5     # ns to skip after direct wave (avoids ringing)
MIN_PROM       = 0.04    # reflector must be >=4% of direct wave amplitude


# ─────────────────────────────────────────────────────────────────────────────
# Synthetic
# ─────────────────────────────────────────────────────────────────────────────

def run_synthetic(exp_dir: Path, skip_ns: float = SKIP_NS,
                  min_prom: float = MIN_PROM) -> pd.DataFrame:
    meta = pd.read_csv(exp_dir / "metadata.csv")
    rows = []
    for _, row in meta.iterrows():
        sid  = int(row["sample_id"])
        path = exp_dir / f"sample_{sid:04d}.out"
        df   = read_gprmax_hdf5(str(path), fields=["Ez"])
        if df.empty:
            continue
        dt   = float(df["Time"].iloc[1] - df["Time"].iloc[0])
        sig  = df["rx1_Ez"].values
        res  = pick_reflector(sig, dt, skip_after_direct_ns=skip_ns,
                              min_prominence=min_prom)
        depth_est = reflector_to_depth(res["dt_twoway_ns"], eps=EPS_CLEAN)
        rows.append({
            "sample_id":   sid,
            "fouled_m":    row["fouled_m"],
            "clean_m":     row["clean_m"],
            "total_m":     row["total_m"],
            "eps_fouled":  row["eps_fouled"],
            "t_direct_ns": res["t_direct_ns"],
            "t_refl_ns":   res["t_reflector_ns"],
            "dt_twoway_ns":res["dt_twoway_ns"],
            "depth_est_m": depth_est,
            "peak_ratio":  res["peak_ratio"],
            "found":       res["found"],
        })
    return pd.DataFrame(rows)


# ─────────────────────────────────────────────────────────────────────────────
# Real
# ─────────────────────────────────────────────────────────────────────────────

def run_real(skip_ns: float = SKIP_NS, min_prom: float = MIN_PROM) -> pd.DataFrame:
    df_fi     = pd.read_pickle(FI_PKL)
    df_traces = pd.read_pickle(TRACES_PKL)
    df = df_traces.merge(df_fi[["ID", "Prof_BS", "Prof_BC"]], on="ID")

    sample_cols = [str(i) for i in range(512) if str(i) in df.columns]
    if not sample_cols:
        sample_cols = [c for c in df.columns if isinstance(c, int)]

    rows = []
    for _, row in df.iterrows():
        sig = row[sample_cols].values.astype(float)[2:]   # drop DZT markers
        res = pick_reflector(sig, DT_REAL_S,
                             skip_after_direct_ns=skip_ns,
                             min_prominence=min_prom)
        depth_est = reflector_to_depth(res["dt_twoway_ns"], eps=EPS_CLEAN)
        rows.append({
            "ID":          row["ID"],
            "Prof_BS":     row["Prof_BS"],
            "Prof_BC":     row["Prof_BC"],
            "t_direct_ns": res["t_direct_ns"],
            "t_refl_ns":   res["t_reflector_ns"],
            "dt_twoway_ns":res["dt_twoway_ns"],
            "depth_est_m": depth_est,
            "peak_ratio":  res["peak_ratio"],
            "found":       res["found"],
        })
    return pd.DataFrame(rows)


# ─────────────────────────────────────────────────────────────────────────────
# Metrics + plots
# ─────────────────────────────────────────────────────────────────────────────

def report(df, true_col, est_col, label, out_png):
    sub = df[[true_col, est_col]].dropna()
    if len(sub) == 0:
        print(f"  {label}: no valid pairs")
        return

    found_rate = df["found"].mean()
    mae = mean_absolute_error(sub[true_col], sub[est_col])
    rho, pval = spearmanr(sub[true_col], sub[est_col])
    print(f"  {label}")
    print(f"    n={len(sub)}  found={found_rate:.0%}")
    print(f"    MAE={mae*100:.1f} cm   rho={rho:+.3f}  p={pval:.3e}")

    fig, ax = plt.subplots(figsize=(5, 4))
    ax.scatter(sub[true_col] * 100, sub[est_col] * 100, s=25, alpha=0.7,
               edgecolors="k", linewidths=0.3)
    lims = [min(sub[true_col].min(), sub[est_col].min()) * 100 - 3,
            max(sub[true_col].max(), sub[est_col].max()) * 100 + 3]
    ax.plot(lims, lims, "k--", linewidth=1)
    ax.set_xlabel(f"True {true_col} (cm)")
    ax.set_ylabel("Physics estimate (cm)")
    ax.set_title(f"{label}\nMAE={mae*100:.1f}cm  rho={rho:+.3f}  n={len(sub)}")
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    fig.savefig(out_png, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"    Plot -> {out_png}")


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("experiment_dir", type=Path,
                        help="layer_height_v1 experiment folder")
    parser.add_argument("--skip-ns", type=float, default=SKIP_NS,
                        help=f"ns to skip after direct wave (default {SKIP_NS})")
    parser.add_argument("--min-prom", type=float, default=MIN_PROM,
                        help=f"min reflector prominence fraction (default {MIN_PROM})")
    args = parser.parse_args()

    skip_ns  = args.skip_ns
    min_prom = args.min_prom
    exp_dir  = args.experiment_dir.resolve()

    # ── Synthetic ────────────────────────────────────────────────────────────
    print("\n=== SYNTHETIC (layer_height_v1) ===")
    synth = run_synthetic(exp_dir, skip_ns=skip_ns, min_prom=min_prom)
    synth.to_csv(exp_dir / "reflector_synth.csv", index=False)
    print(f"Detector found reflector in {synth['found'].sum()}/{len(synth)} traces")
    valid_synth = synth[synth["found"]]
    print(f"  t_direct range:  {synth.t_direct_ns.min():.2f} - {synth.t_direct_ns.max():.2f} ns")
    if len(valid_synth):
        print(f"  dt_twoway range: {valid_synth.dt_twoway_ns.min():.2f} - {valid_synth.dt_twoway_ns.max():.2f} ns")

    report(synth, "clean_m", "depth_est_m", "Synth: depth_est vs clean_m",
           exp_dir / "reflector_synth_clean.png")

    # Sub-analysis: traces with fouled_m=0 (clean only, 1-reflector)
    clean_only = synth[synth["fouled_m"] == 0].copy()
    report(clean_only, "clean_m", "depth_est_m", "Synth (fouled=0): depth_est vs clean_m",
           exp_dir / "reflector_synth_cleanonly.png")

    # ── Real ─────────────────────────────────────────────────────────────────
    print("\n=== REAL (112 labeled traces) ===")
    real = run_real(skip_ns=skip_ns, min_prom=min_prom)
    real.to_csv(exp_dir / "reflector_real.csv", index=False)
    print(f"Detector found reflector in {real['found'].sum()}/{len(real)} traces")
    print(f"  t_direct range: {real.t_direct_ns.min():.2f} – {real.t_direct_ns.max():.2f} ns")

    real_valid = real[real["found"]].copy()
    if len(real_valid):
        print(f"  dt_twoway range: {real_valid.dt_twoway_ns.min():.2f} – "
              f"{real_valid.dt_twoway_ns.max():.2f} ns")
        print(f"  depth_est range: {real_valid.depth_est_m.min()*100:.1f} – "
              f"{real_valid.depth_est_m.max()*100:.1f} cm")

    report(real, "Prof_BS", "depth_est_m", "Real: depth_est vs Prof_BS",
           exp_dir / "reflector_real_profbs.png")

    print("\nDone.")


if __name__ == "__main__":
    main()

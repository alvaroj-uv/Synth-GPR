#!/usr/bin/env python3
"""
Rojas-Vivanco (2025)-style feature extraction for the REAL traces.

Key difference vs our extract_features: the dominant predictor in the paper
(SHAP group 3, 60-65%) is the ANALYTIC (Hilbert) signal sampled POINT-BY-POINT
in time -- not global envelope statistics. We reproduce that here.

Per the paper (Table 4) features are organized as:
  G3 (analytic signal) : envelope sampled every 0.1 ns + envelope statistics
  G2 (processed signal): signal sampled every 0.1 ns + signal statistics
                         + signal area, zero-crossings, inflection pts, peaks
  G1 (prior-study)     : area under Hilbert curve, area under Fourier + dominant
                         frequency  (small SHAP, kept for completeness)

We also keep the frequency-domain features that already showed real signal
(median/mean frequency, spectral flatness; rho~0.45 in spearman_real).

Labels: the 10 rows with FI==0.4933 are CLEAN (class C), the FH=0 intercept of
the medium-ballast equation -- NOT missing data. They are kept and labeled C.

Output: docs/input/feature_dataset_rojas.csv  [ID, FI, FI_class, <features>]

Usage:
    python scripts/pipeline/extract_features_rojas.py
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.signal import hilbert, find_peaks
from scipy.stats import skew, kurtosis

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

from src.physics import classify_fouling_index

SIGNALS_CSV = ROOT / "docs" / "input" / "df_Signaux_traitees_S1.csv"
MED_CSV = ROOT / "docs" / "input" / "df_pandoscope_med.csv"
OUTPUT_CSV = ROOT / "docs" / "input" / "feature_dataset_rojas.csv"

DT = 0.1e-9            # 0.1 ns
CLEAN_INTERCEPT = 0.4933  # medium-ballast FH=0 intercept => CLEAN


def distribution_stats(x, prefix):
    """Selig-style distribution descriptors used by the paper."""
    rms = np.sqrt(np.mean(x ** 2))
    d = {
        f"{prefix}_mean": np.mean(x),
        f"{prefix}_rms": rms,
        f"{prefix}_std": np.std(x),
        f"{prefix}_median": np.median(x),
        f"{prefix}_skew": skew(x),
        f"{prefix}_kurt": kurtosis(x),
        f"{prefix}_min": np.min(x),
        f"{prefix}_max": np.max(x),
    }
    for q in (25, 50, 75):
        d[f"{prefix}_q{q}"] = np.percentile(x, q)
    for i, dec in enumerate(np.percentile(x, np.arange(10, 100, 10))):
        d[f"{prefix}_dec{(i + 1) * 10}"] = dec
    return d


def signal_shape_feats(sig):
    """G2 processed-signal shape: area, zero-crossings, inflections, peaks."""
    zero_cross = int(np.sum(np.diff(np.signbit(sig)) != 0))
    inflections = int(np.sum(np.diff(np.signbit(np.diff(sig, 2))) != 0))
    peaks, props = find_peaks(sig, height=np.std(sig) * 0.5)
    return {
        "sig_area": np.sum(np.abs(sig)),
        "sig_zero_crossings": zero_cross,
        "sig_inflections": inflections,
        "sig_peak_count": len(peaks),
        "sig_peak_mean_height": float(np.mean(props["peak_heights"])) if len(peaks) else 0.0,
    }


def frequency_feats(sig):
    """G1 + the frequency features that showed real correlation."""
    fft = np.abs(np.fft.rfft(sig))
    freqs = np.fft.rfftfreq(len(sig), d=DT)
    area = np.sum(fft)
    if area > 0:
        mean_f = np.sum(freqs * fft) / area
        cum = np.cumsum(fft)
        med_f = freqs[min(np.searchsorted(cum, area / 2), len(freqs) - 1)]
    else:
        mean_f = med_f = 0.0
    g = np.exp(np.mean(np.log(fft + 1e-12)))
    a = np.mean(fft)
    flatness = g / a if a > 0 else 0.0
    return {
        "fourier_area": area,
        "dominant_frequency": freqs[int(np.argmax(fft))],
        "mean_frequency": mean_f,
        "median_frequency": med_f,
        "spectral_flatness": flatness,
    }


def extract_one(sig):
    """All paper-style features for one processed coda trace."""
    analytic = hilbert(sig)
    env = np.abs(analytic)          # analytic-signal envelope (G3)
    feats = {}

    # G3: point-by-point analytic envelope (the 60-65% SHAP driver)
    for i, v in enumerate(env):
        feats[f"env_t{i}"] = v
    feats.update(distribution_stats(env, "env"))
    feats["area_hilbert"] = np.sum(env)   # G1: area under Hilbert curve

    # G2: point-by-point processed signal + stats + shape
    for i, v in enumerate(sig):
        feats[f"sig_t{i}"] = v
    feats.update(distribution_stats(sig, "sig"))
    feats.update(signal_shape_feats(sig))

    # G1 + frequency
    feats.update(frequency_feats(sig))
    return feats


def main():
    long = pd.read_csv(SIGNALS_CSV)
    wide = long.pivot(index="Time", columns="ID", values="GPR").sort_index()

    rows = []
    for trace_id in wide.columns:
        sig = wide[trace_id].values.astype(float)
        m = np.max(np.abs(sig))
        if m > 0:
            sig = sig / m  # normalize to max (paper: envelope normalized to max)
        feats = extract_one(sig)
        feats["ID"] = int(trace_id)
        rows.append(feats)

    feats_df = pd.DataFrame(rows)

    med = pd.read_csv(MED_CSV)[["ID", "FI_Estimado_Medio_JRO_Final"]]
    med = med.rename(columns={"FI_Estimado_Medio_JRO_Final": "FI"})
    df = feats_df.merge(med, on="ID", how="inner")

    # FI==0.4933 -> CLEAN (FH=0 intercept), classify the rest by Selig & Waters
    is_clean = df["FI"].round(4) == CLEAN_INTERCEPT
    df["FI_class"] = df["FI"].apply(classify_fouling_index)
    df.loc[is_clean, "FI_class"] = "C"

    feat_cols = [c for c in df.columns if c not in ("ID", "FI", "FI_class")]
    df = df[["ID", "FI", "FI_class"] + feat_cols].sort_values("ID").reset_index(drop=True)
    df.to_csv(OUTPUT_CSV, index=False)

    print("=" * 60)
    print("Rojas-style feature extraction complete")
    print("=" * 60)
    print(f"Samples : {len(df)}   Features: {len(feat_cols)}")
    print(f"  point-by-point envelope: {sum(c.startswith('env_t') for c in feat_cols)}")
    print(f"  point-by-point signal  : {sum(c.startswith('sig_t') for c in feat_cols)}")
    print(f"FI clean (C) rows        : {int(is_clean.sum())}")
    print(f"Class dist:\n{df['FI_class'].value_counts().sort_index().to_string()}")
    print(f"Output: {OUTPUT_CSV}")


if __name__ == "__main__":
    main()

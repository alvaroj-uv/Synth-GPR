#!/usr/bin/env python3
"""
Build a CODA-ALIGNED synthetic feature parquet for fair real-trace validation.

Problem
-------
Synthetic .out traces are 644 samples and INCLUDE the direct pulse (at sample
~112). The real processed traces (df_Signaux_traitees_S1) are 250 samples of
*post-direct-pulse coda only* (raw samples 61..310, starting at the direct
pulse peak). Extracting the 572 features over these incompatible time supports
makes length/position-sensitive features (grid_signal_time_*, slices, freq)
non-comparable -> ~483/572 features showed |drift|>2 IQR, a measurement
artifact, not a true domain gap.

Fix
---
Window BOTH sides identically: take 250 samples starting at the direct-pulse
peak (argmax|dewow(signal)|), then run the SAME extract_features. This mirrors
exactly what was done to produce the real coda window.

Output
------
    output/dataset_coda_features.parquet  (synthetic, coda-aligned, 572 feats)

Usage
-----
    python scripts/pipeline/build_parquet_coda_aligned.py
"""

import sys
import glob
from pathlib import Path

import numpy as np
import pandas as pd
from tqdm import tqdm

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

from src.data_loader import read_gprmax_hdf5
from src.signal_processing import dewow
from src.feature_extraction import extract_features_from_signal
from src.constants import PC
from src.dataset_io import load_features, save_dataset

DATASET_DIR = ROOT / "output" / "dataset_variants"
OUTPUT_PATH = ROOT / "output" / "dataset_coda_features.parquet"
SRC_PARQUET = ROOT / "output" / "dataset_80k_features.parquet"  # for labels

CODA_LEN = 250  # match real _S1 window length


def _class_from_id(sample_id: int) -> str:
    if sample_id < 1000: return "C"
    if sample_id < 2000: return "MC"
    if sample_id < 3000: return "MF"
    if sample_id < 4000: return "F"
    return "HF"


def coda_window(signal: np.ndarray) -> np.ndarray:
    """Return CODA_LEN samples starting at the direct-pulse peak, peak-normalized.

    Mirrors the real window: raw sample 61 (direct-pulse peak) .. 310.
    Steps (identical on synthetic and real): dewow -> cut coda -> normalize
    to peak |amplitude| = 1 (so amplitude scale matches across domains).
    """
    dw = dewow(signal, 50)
    peak = int(np.argmax(np.abs(dw)))
    end = peak + CODA_LEN
    if end > len(dw):  # safety; all synthetic traces have >=250 after peak
        peak = len(dw) - CODA_LEN
        end = len(dw)
    coda = dw[peak:end]
    m = np.max(np.abs(coda))
    if m > 0:
        coda = coda / m
    return coda


def main():
    outs = sorted(glob.glob(str(DATASET_DIR / "*.out")))
    print(f"Found {len(outs)} synthetic .out files")

    # Build sample_id -> label map from existing parquet (authoritative labels)
    labels = {}
    try:
        lab_df = load_features(SRC_PARQUET, columns=["sample_id", "label"])
        labels = dict(zip(lab_df["sample_id"], lab_df["label"]))
    except Exception:
        print("  (no source parquet labels; falling back to id-range classes)")

    rows = []
    for o in tqdm(outs, desc="Coda-aligned features"):
        df = read_gprmax_hdf5(o, fields=["E"])
        if df.empty:
            continue
        ez = next((c for c in df.columns if c.endswith("Ez")), None)
        if ez is None:
            continue

        coda = coda_window(df[ez].values)

        # True dt of this .out (≈0.031 ns) so freq features are correctly scaled.
        t = df["Time"].values
        dt = float(t[1] - t[0]) if len(t) > 1 else None
        # NOTE for sim↔real comparison: real traces are sampled at 0.1 ns; these
        # synthetic ones at ~0.031 ns. For a fully clean comparison, resample the
        # coda to 0.1 ns before feature extraction. TODO when rebuilding full set.
        feat_df = extract_features_from_signal(coda, dt=dt, signal_name="sig") if dt else extract_features_from_signal(coda, signal_name="sig")
        if feat_df.empty:
            continue
        row = feat_df.iloc[0].drop(labels=["Signal"], errors="ignore").to_dict()

        sample_id = int(Path(o).stem.split("_")[-1])
        row["sample_id"] = sample_id
        row["label"] = labels.get(sample_id, _class_from_id(sample_id))
        rows.append(row)

    out = pd.DataFrame(rows)
    save_dataset(out, OUTPUT_PATH)
    print(f"\nSaved {len(out)} rows -> {OUTPUT_PATH}")
    print(f"Class dist:\n{out['label'].value_counts().sort_index().to_string()}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Build training parquet from dataset_1k.

Pipeline per sample:
  .out (HDF5)  ->  preprocess_signal  ->  extract_features  ->  row
  .in (header) ->  FI_class label

Output: output/dataset_1k_features.parquet
  Columns: sample_id | label | <573 feature columns>
"""

import sys
import re
from pathlib import Path

import numpy as np
import pandas as pd
from tqdm import tqdm

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from src.data_loader import read_gprmax_hdf5
from src.feature_extraction import extract_features
from src.signal_processing import preprocess_signal
from src.constants import PC

DATASET_DIR = Path("output/dataset_1k")
OUTPUT_PATH = Path("output/dataset_1k_features.parquet")


import argparse as _ap
def _parse_args():
    p = _ap.ArgumentParser()
    p.add_argument("--dataset-dir", default=None)
    p.add_argument("--output",      default=None)
    return p.parse_args()


def _label_from_header(in_path: Path) -> str | None:
    """Read FI_class from .in header (## FI_class: XX)."""
    try:
        with open(in_path, encoding="utf-8", errors="ignore") as f:
            for line in f:
                if not line.startswith("##"):
                    break
                if line.startswith("## FI_class:"):
                    return line.split(":", 1)[1].strip()
    except OSError:
        pass
    return None


def _label_from_id(sample_id: int) -> str:
    """Fallback: derive class from sample ID range (batch generation order)."""
    if sample_id < 1000: return "CL"
    if sample_id < 2000: return "MC"
    if sample_id < 3000: return "MF"
    if sample_id < 4000: return "F"
    return "HF"


def _process(out_path: Path) -> dict | None:
    """Load Ez, preprocess, and extract features from one .out file."""
    df = read_gprmax_hdf5(str(out_path), fields=["E"])
    if df.empty or "Time" not in df.columns:
        return None

    # Find the Ez column (primary component for 2-D TMz simulation)
    ez_col = next((c for c in df.columns if c.endswith("Ez")), None)
    if ez_col is None:
        return None

    time = df["Time"].values
    dt = float(time[1] - time[0]) if len(time) > 1 else PC.DEFAULT_DT

    sig, _ = preprocess_signal(df[ez_col].values, dt,
                               use_dewow=True,
                               use_gain=False,
                               use_time_zero=True)

    feat_df = extract_features(pd.DataFrame({"Time": time, ez_col: sig}))
    if feat_df.empty:
        return None

    # Drop the non-numeric 'Signal' column before returning
    row = feat_df.iloc[0].drop(labels=["Signal"], errors="ignore")
    return row.to_dict()


def main():
    args = _parse_args()
    dataset_dir = Path(args.dataset_dir) if args.dataset_dir else DATASET_DIR
    output_path = Path(args.output)      if args.output      else OUTPUT_PATH

    out_files = sorted(dataset_dir.glob("s_*.out"))
    print(f"Dataset : {dataset_dir}")
    print(f"Samples : {len(out_files)}")
    print(f"Output  : {output_path}")
    print()

    rows = []
    errors = 0

    for out_path in tqdm(out_files, desc="Processing", unit="file"):
        m = re.search(r"s_(\d+)\.out$", out_path.name)
        if not m:
            continue
        sample_id = int(m.group(1))
        in_path = out_path.with_suffix(".in")

        label = _label_from_header(in_path) or _label_from_id(sample_id)


        try:
            feats = _process(out_path)
            if feats is None:
                errors += 1
                continue
            rows.append({"sample_id": sample_id, "label": label, **feats})
        except Exception as e:
            tqdm.write(f"[WARN] {out_path.name}: {e}")
            errors += 1

    if not rows:
        print("ERROR: no features extracted — check .out files")
        sys.exit(1)

    df = pd.DataFrame(rows)

    # Cast feature columns to float32 to halve file size
    feat_cols = [c for c in df.columns if c not in ("sample_id", "label")]
    df[feat_cols] = df[feat_cols].astype("float32")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(output_path, index=False, engine="pyarrow", compression="snappy")

    print(f"\nDone")
    print(f"  Rows      : {len(df)}")
    print(f"  Features  : {len(feat_cols)}")
    print(f"  Errors    : {errors}")
    print(f"  File size : {output_path.stat().st_size / 1e6:.1f} MB")
    print(f"\nLabel distribution:")
    print(df["label"].value_counts().sort_index().to_string())


if __name__ == "__main__":
    main()

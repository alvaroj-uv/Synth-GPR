#!/usr/bin/env python3
"""
Build training parquet from multiple datasets with metadata + signal features.

Pipeline per sample:
  .out (HDF5)  ->  preprocess_signal  ->  extract_features  ->  row
  .in (header) ->  Lab_Class label + metadata features

Merges gpr_dataset_10k and dataset_variants (default), producing:
  output/dataset_80k_features.parquet
    Columns: sample_id | source | label | <metadata cols> | <572 feature cols>
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

DEFAULT_DIRS = [
    Path("output/gpr_dataset_10k"),
    Path("output/dataset_variants"),
]
OUTPUT_PATH = Path("output/dataset_80k_features.parquet")

# Metadata fields to extract from .in headers (float-like and common across datasets)
METADATA_FIELDS = [
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
    # dataset_variants only
    "Lab_P4", "Lab_P200", "Lab_Porosity",
]


import argparse as _ap
def _parse_args():
    p = _ap.ArgumentParser(description="Build parquet from multiple dataset directories")
    p.add_argument("--dirs", nargs="+", default=None,
                  help="Dataset directories (default: gpr_dataset_10k dataset_variants)")
    p.add_argument("--output", default=None, help="Output parquet path")
    return p.parse_args()


def _parse_metadata(in_path: Path) -> dict:
    """Extract metadata fields from .in header comments."""
    meta = {}
    try:
        with open(in_path, encoding="utf-8", errors="ignore") as f:
            for line in f:
                if not line.startswith("##"):
                    break
                if ":" not in line:
                    continue
                key, val = line[2:].split(":", 1)
                key, val = key.strip(), val.strip()
                if key in METADATA_FIELDS:
                    try:
                        meta[key] = float(val)
                    except ValueError:
                        pass
    except OSError:
        pass
    return meta


def _label_from_header(in_path: Path) -> str | None:
    """Read Lab_Class from .in header (## Lab_Class: XX)."""
    try:
        with open(in_path, encoding="utf-8", errors="ignore") as f:
            for line in f:
                if not line.startswith("##"):
                    break
                if line.startswith("## Lab_Class:"):
                    return line.split(":", 1)[1].strip()
    except OSError:
        pass
    return None


def _process(out_path: Path) -> dict | None:
    """Load Ez, preprocess, and extract 572 features from one .out file."""
    df = read_gprmax_hdf5(str(out_path), fields=["E"])
    if df.empty or "Time" not in df.columns:
        return None

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

    row = feat_df.iloc[0].drop(labels=["Signal"], errors="ignore")
    return row.to_dict()


def main():
    args = _parse_args()
    dirs = [Path(d) for d in args.dirs] if args.dirs else DEFAULT_DIRS
    output_path = Path(args.output) if args.output else OUTPUT_PATH

    print(f"Datasets :")
    for d in dirs:
        print(f"  {d}")
    print(f"Output   : {output_path}")
    print()

    rows = []
    errors = 0
    total_files = 0

    for dataset_dir in dirs:
        if not dataset_dir.exists():
            print(f"[WARN] {dataset_dir} not found, skipping")
            continue

        out_files = sorted(dataset_dir.glob("s_*.out"))
        print(f"\n{dataset_dir.name}: {len(out_files)} files")

        source_name = dataset_dir.name

        for out_path in tqdm(out_files, desc=source_name, unit="file"):
            total_files += 1
            m = re.search(r"s_(\d+)\.out$", out_path.name)
            if not m:
                continue
            sample_id = int(m.group(1))
            in_path = out_path.with_suffix(".in")

            label = _label_from_header(in_path)
            if label is None:
                errors += 1
                continue

            try:
                feats = _process(out_path)
                if feats is None:
                    errors += 1
                    continue

                meta = _parse_metadata(in_path)

                row = {
                    "sample_id": sample_id,
                    "source": source_name,
                    "label": label,
                }
                # Add metadata fields (missing ones will be NaN)
                for field in METADATA_FIELDS:
                    row[field] = meta.get(field, np.nan)
                # Add signal features
                row.update(feats)

                rows.append(row)
            except Exception as e:
                tqdm.write(f"[WARN] {out_path.name}: {e}")
                errors += 1

    if not rows:
        print("ERROR: no features extracted — check .out files")
        sys.exit(1)

    df = pd.DataFrame(rows)

    # Fill NaN metadata with column median
    for field in METADATA_FIELDS:
        if field in df.columns and df[field].isna().any():
            df[field].fillna(df[field].median(), inplace=True)

    # Cast feature columns to float32
    feat_cols = [c for c in df.columns
                 if c not in ("sample_id", "source", "label")]
    df[feat_cols] = df[feat_cols].astype("float32")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(output_path, index=False, engine="pyarrow", compression="snappy")

    print(f"\nDone")
    print(f"  Total files  : {total_files}")
    print(f"  Rows saved   : {len(df)}")
    print(f"  Metadata cols: {len(METADATA_FIELDS)}")
    print(f"  Signal feats : {len([c for c in df.columns if c not in METADATA_FIELDS + ['sample_id', 'source', 'label']])}")
    print(f"  Total cols   : {len(df.columns)}")
    print(f"  Errors       : {errors}")
    print(f"  File size    : {output_path.stat().st_size / 1e6:.1f} MB")
    print(f"\nSource distribution:")
    print(df["source"].value_counts().to_string())
    print(f"\nLabel distribution:")
    print(df["label"].value_counts().sort_index().to_string())


if __name__ == "__main__":
    main()

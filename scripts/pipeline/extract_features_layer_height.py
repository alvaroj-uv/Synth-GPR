#!/usr/bin/env python3
"""
Extract waveform features from the layer-height gprMax dataset.

Reads every sample_NNNN.out from the experiment directory, extracts features
via src.feature_extraction.extract_features (using the correct synthetic dt
read from each HDF5 file), and joins with metadata.csv labels
(fouled_m, clean_m, total_m, eps_fouled).

Output: feature_dataset.csv  (same directory as input metadata.csv)
  Columns: sample_id, fouled_m, clean_m, total_m, eps_fouled, <waveform features...>
  Excludes: meta_* and Signal columns (provenance, not features).

Usage:
    python scripts/pipeline/extract_features_layer_height.py \\
        experiments/2026-06-29/layer_height_v1/
"""

import sys
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import pandas as pd
from tqdm import tqdm

from src.feature_extraction import extract_features
from src.data_loader import read_gprmax_hdf5


CENTER_FREQ_HZ = 420e6


def extract_from_out(out_path: Path) -> dict:
    """Read Ez component and extract waveform features."""
    # Use fields=['Ez'] so the DataFrame has only Time + rx1_Ez;
    # fields=['E'] returns Ex/Ey/Ez and iloc[0] would give near-zero Ex features.
    df = read_gprmax_hdf5(str(out_path), fields=["Ez"])
    if df.empty:
        raise ValueError(f"Empty DataFrame from {out_path.name}")
    time = df["Time"].values
    dt = float(time[1] - time[0]) if len(time) > 1 else None
    if dt is None:
        raise ValueError(f"Cannot determine dt from {out_path.name}")
    feat_df = extract_features(df, dt=dt, center_freq_hz=CENTER_FREQ_HZ)
    if feat_df.empty:
        raise ValueError(f"No features extracted from {out_path.name}")
    row = feat_df.iloc[0].to_dict()
    # Drop provenance / non-waveform columns
    return {k: v for k, v in row.items()
            if not k.startswith("meta_") and k != "Signal"}


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("experiment_dir", type=Path,
                        help="Experiment folder containing sample_*.out and metadata.csv")
    parser.add_argument("--output", type=Path, default=None,
                        help="Output CSV path (default: <experiment_dir>/feature_dataset.csv)")
    args = parser.parse_args()

    exp_dir = args.experiment_dir.resolve()
    meta_path = exp_dir / "metadata.csv"
    if not meta_path.exists():
        print(f"ERROR: metadata.csv not found in {exp_dir}", file=sys.stderr)
        sys.exit(1)

    out_path = args.output or exp_dir / "feature_dataset.csv"
    out_path = out_path.resolve()

    meta = pd.read_csv(meta_path)
    print(f"Loaded {len(meta)} samples from metadata.csv")

    rows = []
    errors = []
    for _, row in tqdm(meta.iterrows(), total=len(meta), desc="Extracting features"):
        sample_id = int(row["sample_id"])
        out_file = exp_dir / f"sample_{sample_id:04d}.out"
        if not out_file.exists():
            errors.append(sample_id)
            continue
        try:
            feats = extract_from_out(out_file)
            feats["sample_id"] = sample_id
            rows.append(feats)
        except Exception as e:
            print(f"\nWARN: {out_file.name}: {e}")
            errors.append(sample_id)

    if errors:
        print(f"\nSkipped {len(errors)} samples: {errors}")

    feat_df = pd.DataFrame(rows)
    # Join labels from metadata
    labels = meta[["sample_id", "fouled_m", "clean_m", "total_m", "eps_fouled"]]
    result = labels.merge(feat_df, on="sample_id", how="inner")

    # Put label columns first
    label_cols = ["sample_id", "fouled_m", "clean_m", "total_m", "eps_fouled"]
    feature_cols = [c for c in result.columns if c not in label_cols]
    result = result[label_cols + feature_cols]

    result.to_csv(out_path, index=False)
    print(f"\nSaved {len(result)} rows x {len(result.columns)} columns -> {out_path}")
    print(f"  Label columns : {label_cols}")
    print(f"  Feature count : {len(feature_cols)}")


if __name__ == "__main__":
    main()

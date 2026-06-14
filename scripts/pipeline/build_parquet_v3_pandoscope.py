#!/usr/bin/env python3
"""
Build parquet dataset from v3 .in/.out files with Pandoscope FI conversion.

Workflow:
1. Read v3 .in files (metadata with pvc, FI_class)
2. Extract waveform features from .out files
3. Convert Selig FI_class -> Pandoscope FI using Rojas equation
4. Write gpr_synth_dataset_v3_pandoscope_features.parquet

This bridges the synthetic/real label gap by converting synthetic Selig labels
to Pandoscope (empirical layer-height) labels that match real Site-1 data.

CONVERSION FORMULA (Rojas-Vivanco, medium ballast compaction):
    FI_pandoscope = -0.0017*pvc^2 + 0.6311*pvc + 0.4933
    where pvc is porosity void content percentage
"""

import sys
from pathlib import Path
import numpy as np
import pandas as pd
import warnings

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.file_reader import parse_metadata_file
from src.signal_processing import extract_features_from_traces

warnings.filterwarnings('ignore')


def rojas_pandoscope_fi(pvc: float) -> float:
    """Convert PVC to Pandoscope FI using Rojas quadratic equation (medium ballast)."""
    return -0.0017 * pvc**2 + 0.6311 * pvc + 0.4933


def fi_to_selig_class(fi: float) -> str:
    """Bin FI value to Selig class."""
    if fi <= 2:
        return 'C'
    elif fi <= 8:
        return 'MC'
    elif fi <= 20:
        return 'MF'
    elif fi <= 50:
        return 'F'
    else:
        return 'HF'


def main():
    print("=" * 70)
    print("BUILD PARQUET V3: Pandoscope FI Conversion")
    print("=" * 70)

    data_dir = Path('D:/Codigo/gpr_synth_dataset_v3')
    out_parquet = Path('output/gpr_synth_dataset_v3_pandoscope_features.parquet')

    if not data_dir.exists():
        print(f"ERROR: Dataset directory not found: {data_dir}")
        return 1

    # Find all .in files
    in_files = sorted(list(data_dir.glob('s_*.in')))
    out_files = sorted(list(data_dir.glob('s_*.out')))

    if not in_files:
        print(f"ERROR: No .in files found in {data_dir}")
        return 1

    print(f"\nFound {len(in_files)} .in files")
    print(f"Found {len(out_files)} .out files")

    if len(in_files) != len(out_files):
        print(f"WARNING: Mismatch between .in and .out file counts")

    # Build dataset
    records = []
    metadata_cols = []

    for idx, in_path in enumerate(in_files):
        if idx % 2500 == 0:
            print(f"  Processing {idx}/{len(in_files)}...")

        # Parse metadata
        try:
            meta = parse_metadata_file(in_path)
        except Exception as e:
            print(f"  WARN: Could not parse {in_path.name}: {e}")
            continue

        # Get matching .out file
        out_path = in_path.with_suffix('.out')
        if not out_path.exists():
            print(f"  WARN: No .out file for {in_path.name}")
            continue

        # Extract features
        try:
            features, trace = extract_features_from_traces(str(out_path))
        except Exception as e:
            print(f"  WARN: Could not extract features from {out_path.name}: {e}")
            continue

        # Extract metadata
        sample_id = meta.get('sample_id')
        pvc = meta.get('pvc')
        porosity = meta.get('porosity')
        fi_selig_class = meta.get('FI_class')

        if any(v is None for v in [sample_id, pvc, porosity, fi_selig_class]):
            print(f"  WARN: Missing metadata in {in_path.name}")
            continue

        # Convert Selig FI -> Pandoscope FI
        fi_pandoscope = rojas_pandoscope_fi(float(pvc))
        fi_pandoscope_class = fi_to_selig_class(fi_pandoscope)

        # Build record
        record = {
            'sample_id': sample_id,
            'label_selig': fi_selig_class,
            'label_pandoscope': fi_pandoscope_class,
            'pvc': pvc,
            'porosity': porosity,
            'FI_pandoscope': fi_pandoscope,
        }

        # Add features
        for feat_name, feat_val in features.items():
            record[feat_name] = feat_val

        records.append(record)

        if idx == 0:
            metadata_cols = [k for k in record.keys() if k not in features]

    print(f"\nProcessed {len(records)} samples successfully")

    # Convert to DataFrame
    df = pd.DataFrame(records)

    print(f"\nDataFrame shape: {df.shape}")
    print(f"Columns: {len(df.columns)}")
    print(f"  Metadata: {len(metadata_cols)}")
    print(f"  Features: {len(df.columns) - len(metadata_cols)}")

    # Check label distributions
    print(f"\nLabel distributions:")
    print(f"\nSelig (original synthetic):")
    print(df['label_selig'].value_counts().sort_index())
    print(f"\nPandoscope (converted):")
    print(df['label_pandoscope'].value_counts().sort_index())

    print(f"\nConversion statistics:")
    print(f"  Mean Pandoscope FI: {df['FI_pandoscope'].mean():.2f}")
    print(f"  Min/Max: {df['FI_pandoscope'].min():.2f} / {df['FI_pandoscope'].max():.2f}")

    # Write parquet
    out_parquet.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(out_parquet, index=False)

    print(f"\nDataset saved: {out_parquet}")
    print(f"Size: {out_parquet.stat().st_size / 1e9:.2f} GB")

    print("\n" + "=" * 70)
    print("SUCCESS")
    print("=" * 70)

    return 0


if __name__ == '__main__':
    sys.exit(main())

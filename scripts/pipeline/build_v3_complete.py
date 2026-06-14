#!/usr/bin/env python3
"""
Complete v3 pipeline: Phase 2-3 generation + feature extraction + label conversion.

Run AFTER Phase 1 completes (2225 C-class samples generated).

Workflow:
1. Phase 2: Generate 4025 MF samples (start_id 2226)
2. Phase 3: Generate 18750 F samples (start_id 6251)
3. Extract features from all 25k .out files
4. Convert Selig FI -> Pandoscope FI using Rojas equation
5. Train RF model on v3 with Pandoscope labels
6. Test on real Site-1 data
"""

import subprocess
import sys
from pathlib import Path
import numpy as np
import pandas as pd
import warnings

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.file_reader import parse_metadata_file
from src.signal_processing import extract_features_from_traces

warnings.filterwarnings('ignore')


def run_phase(phase_num: int, label: str, n_samples: int, start_id: int) -> bool:
    """Generate N samples for a given label."""
    print(f"\n{'='*70}")
    print(f"PHASE {phase_num}/3: {label} CLASS ({n_samples} samples, IDs {start_id}–{start_id+n_samples-1})")
    print(f"{'='*70}\n")

    cmd = [
        sys.executable,
        "scripts/pipeline/generate_in_files.py",
        "D:/Codigo/gpr_synth_dataset_v3",
        "--mode", "batch",
        "--labels", label,
        "-n", str(n_samples),
        "--freq", "400e6",
        "--start-id", str(start_id),
    ]

    result = subprocess.run(cmd, cwd="D:/Codigo/Synth-GPR/Synth-GPR")
    return result.returncode == 0


def extract_all_features() -> pd.DataFrame:
    """Extract features from all 25k .out files."""
    print(f"\n{'='*70}")
    print("FEATURE EXTRACTION: All 25000 samples")
    print(f"{'='*70}\n")

    data_dir = Path('D:/Codigo/gpr_synth_dataset_v3')
    in_files = sorted(list(data_dir.glob('s_*.in')))

    print(f"Found {len(in_files)} .in files")

    records = []
    metadata_cols = None

    for idx, in_path in enumerate(in_files):
        if idx % 2500 == 0:
            print(f"  Processing {idx}/{len(in_files)}...")

        # Parse metadata
        try:
            meta = parse_metadata_file(in_path)
        except Exception:
            continue

        out_path = in_path.with_suffix('.out')
        if not out_path.exists():
            continue

        # Extract features
        try:
            features, _ = extract_features_from_traces(str(out_path))
        except Exception:
            continue

        # Extract metadata
        sample_id = meta.get('sample_id')
        pvc = meta.get('pvc')
        porosity = meta.get('porosity')
        fi_selig = meta.get('FI_class')

        if any(v is None for v in [sample_id, pvc, porosity, fi_selig]):
            continue

        record = {
            'sample_id': sample_id,
            'label_selig': fi_selig,
            'pvc': pvc,
            'porosity': porosity,
        }
        record.update(features)

        records.append(record)

        if metadata_cols is None:
            metadata_cols = [k for k in record.keys() if k not in features]

    df = pd.DataFrame(records)
    print(f"\nExtracted features from {len(df)} samples")
    return df, metadata_cols


def rojas_pandoscope_fi(pvc: float) -> float:
    """Convert PVC to Pandoscope FI."""
    return -0.0017 * pvc**2 + 0.6311 * pvc + 0.4933


def fi_to_class(fi: float) -> str:
    """Bin FI to Selig class."""
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


def convert_labels(df: pd.DataFrame) -> pd.DataFrame:
    """Add Pandoscope labels."""
    print(f"\n{'='*70}")
    print("LABEL CONVERSION: Selig -> Pandoscope")
    print(f"{'='*70}\n")

    df['FI_pandoscope'] = df['pvc'].apply(rojas_pandoscope_fi)
    df['label_pandoscope'] = df['FI_pandoscope'].apply(fi_to_class)

    print(f"Selig distribution (original):")
    print(df['label_selig'].value_counts().sort_index())

    print(f"\nPandoscope distribution (converted):")
    print(df['label_pandoscope'].value_counts().sort_index())

    print(f"\nConversion statistics:")
    print(f"  Mean FI_pandoscope: {df['FI_pandoscope'].mean():.2f}")
    print(f"  Min/Max: {df['FI_pandoscope'].min():.2f} / {df['FI_pandoscope'].max():.2f}")

    return df


def main():
    print("=" * 70)
    print("V3 DATASET: COMPLETE PIPELINE")
    print("=" * 70)

    # Phase 2: MF (2226–6250)
    if not run_phase(2, 'MF', 4025, 2226):
        print("ERROR: Phase 2 failed")
        return 1

    # Phase 3: F (6251–25000)
    if not run_phase(3, 'F', 18750, 6251):
        print("ERROR: Phase 3 failed")
        return 1

    # Extract features
    df, metadata_cols = extract_all_features()
    if df is None or len(df) == 0:
        print("ERROR: Feature extraction failed")
        return 1

    # Convert labels
    df = convert_labels(df)

    # Save parquet
    out_parquet = Path('output/gpr_synth_dataset_v3_pandoscope_features.parquet')
    out_parquet.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(out_parquet, index=False)

    print(f"\nDataset saved: {out_parquet}")
    print(f"Shape: {df.shape}")
    print(f"Size: {out_parquet.stat().st_size / 1e9:.2f} GB")

    print("\n" + "=" * 70)
    print("SUCCESS: V3 dataset ready for training")
    print("=" * 70)

    return 0


if __name__ == '__main__':
    sys.exit(main())

#!/usr/bin/env python3
"""
Extract Features from GPR Simulation Results

Reads .in files and their corresponding .out files from a directory,
extracts features from signals, and consolidates into a feature dataset CSV
with FI_class labels for ML training.

Usage:
    python scripts/pipeline/extract_features.py <data_dir> [options]

Arguments:
    data_dir: Directory containing .in and .out files + metadata.csv
    --output: Output CSV filename (default: feature_dataset.csv)

Example:
    python scripts/pipeline/extract_features.py output/production --output features.csv

Output:
    feature_dataset.csv with columns: [sample_id, FI_class, feature_1, ..., feature_N]
"""

import sys
from pathlib import Path
import argparse
import pandas as pd
from tqdm import tqdm

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.feature_extraction import extract_features
from src.data_loader import read_gprmax_hdf5


def extract_features_from_out_file(out_file_path: str) -> dict:
    """
    Read .out file and extract features using existing implementation.
    
    Args:
        out_file_path: Path to .out file (HDF5 format)
        
    Returns:
        Dictionary of features (500+ features)
    """
    # Load A-scan data from .out file (HDF5)
    df = read_gprmax_hdf5(out_file_path, fields=['E'])

    # Use the TRUE dt from the Time axis (synthetic .out dt ≈ 0.031 ns) so freq
    # features aren't computed with the 0.1 ns default. See build_parquet.py.
    time = df["Time"].values
    dt = float(time[1] - time[0]) if len(time) > 1 else None
    features_df = extract_features(df, dt=dt) if dt else extract_features(df)
    
    # Return first row as dictionary (one signal per file)
    if len(features_df) == 0:
        raise ValueError(f"No features extracted from {out_file_path}")
    
    return features_df.iloc[0].to_dict()


def extract_dataset_features(
    data_dir: Path,
    output_filename: str = "feature_dataset.csv"
) -> pd.DataFrame:
    """
    Extract features from all .out files and merge with labels.
    
    Args:
        data_dir: Directory with .in, .out files and metadata.csv
        output_filename: Name for output feature CSV
        
    Returns:
        DataFrame with [sample_id, FI_class, feature_1, ..., feature_N]
    """
    data_dir = Path(data_dir)
    
    # 1. Load metadata (contains FI_class labels)
    metadata_csv = data_dir / 'metadata.csv'
    if not metadata_csv.exists():
        raise FileNotFoundError(f"Metadata not found: {metadata_csv}")
    
    metadata = pd.read_csv(metadata_csv)
    print(f"Found {len(metadata)} samples in metadata.csv")
    
    # 2. Extract features from each .out file
    feature_rows = []
    skipped = 0
    
    for idx, row in tqdm(metadata.iterrows(), total=len(metadata), desc="Extracting features"):
        sample_id = row['sample_id']
        
        # Find corresponding .out file
        # Try different naming patterns
        out_file_patterns = [
            data_dir / f"s{sample_id:04d}.out",
            data_dir / f"s_{sample_id:04d}.out",
            data_dir / f"{sample_id}.out"
        ]
        
        out_file = None
        for pattern in out_file_patterns:
            if pattern.exists():
                out_file = pattern
                break
        
        if out_file is None:
            print(f"\n⚠️  Warning: .out file not found for sample {sample_id}, skipping")
            skipped += 1
            continue
        
        try:
            # Extract features using existing implementation
            features = extract_features_from_out_file(str(out_file))
            
            # Combine with label and metadata
            feature_row = {
                'sample_id': sample_id,
                'FI_class': row['FI_class'],
                **features
            }
            feature_rows.append(feature_row)
            
        except Exception as e:
            print(f"\n❌ Error processing {out_file}: {e}")
            skipped += 1
            continue
    
    # 3. Consolidate into DataFrame
    if not feature_rows:
        raise ValueError("No features extracted! Check .out files.")
    
    feature_dataset = pd.DataFrame(feature_rows)
    
    # 4. Save to CSV
    output_path = data_dir / output_filename
    feature_dataset.to_csv(output_path, index=False)
    
    print(f"\n{'='*60}")
    print("Feature Extraction Complete!")
    print(f"{'='*60}")
    print(f"Processed:  {len(feature_rows)} samples")
    print(f"Skipped:    {skipped} samples")
    print(f"Features:   {len(feature_dataset.columns) - 2}")  # Exclude sample_id, FI_class
    print(f"Output:     {output_path}")
    print(f"{'='*60}")
    
    return feature_dataset


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Extract features from GPR simulation results (.out files)",
        epilog="Requires metadata.csv with FI_class labels in the same directory"
    )
    
    parser.add_argument(
        "data_dir",
        help="Directory containing .in, .out files and metadata.csv"
    )
    
    parser.add_argument(
        "--output",
        default="feature_dataset.csv",
        help="Output CSV filename (default: feature_dataset.csv)"
    )
    
    args = parser.parse_args()
    
    # Run feature extraction
    try:
        dataset = extract_dataset_features(args.data_dir, args.output)
        
        # Display sample
        print("\nSample rows:")
        print(dataset.head())
        
        print("\nColumn summary:")
        print("  - sample_id: integer")
        print(f"  - FI_class: {dataset['FI_class'].unique().tolist()}")
        print(f"  - Features: {len(dataset.columns) - 2} columns")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)

#!/usr/bin/env python3
"""
Script to create a feature dataset CSV file from a folder of gprMax output files.

Usage:
    python create_feature_dataset.py <input_folder> [options]
    
Examples:
    # Basic usage - process all .out files in samples/ folder
    python create_feature_dataset.py ../samples
    
    # Specify output file name
    python create_feature_dataset.py ../samples -o my_features.csv
    
    # Use metadata file for labeling
    python create_feature_dataset.py ../output -o features.csv -m metadata.csv
    
    # Process specific fields
    python create_feature_dataset.py ../samples --fields Ez Ey
"""

import os
import sys
import glob
import argparse
import pandas as pd
import h5py
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data_loader import read_gprmax_hdf5
from src.feature_extraction import extract_features


def get_label_from_filename(filename):
    """
    Extracts the classification label from the filename.
    Assumes format like 'A_Cle-A_0000.out', where 'Cle' is the label.
    """
    basename = os.path.basename(filename)
    # Extract character at index 6 (after 'A_Cle-')
    if len(basename) > 6:
        return basename[6]
    return "Unknown"


def load_metadata(metadata_path):
    """
    Loads metadata from CSV and returns a dictionary mapping filename to label.
    Expected CSV columns: 'filename', 'FI_class' (or 'Label')
    """
    try:
        df = pd.read_csv(metadata_path)
        
        # Check for various column name formats
        filename_col = None
        label_col = None
        
        for col in df.columns:
            if col.lower() in ['filename', 'file', 'name']:
                filename_col = col
            if col.lower() in ['fi_class', 'label', 'class', 'classification']:
                label_col = col
        
        if not filename_col or not label_col:
            print(f"Warning: Could not find required columns in {metadata_path}")
            print(f"  Found columns: {list(df.columns)}")
            print(f"  Expected: 'filename' and 'FI_class' (or similar)")
            return {}
        
        # Create mapping: filename -> label
        mapping = pd.Series(df[label_col].values, index=df[filename_col]).to_dict()
        print(f"Loaded {len(mapping)} labels from metadata file")
        return mapping
        
    except Exception as e:
        print(f"Error loading metadata from {metadata_path}: {e}")
        return {}


def process_single_file(filepath, label_mapping=None, fields=['Ez']):
    """
    Extracts features for a single gprMax output file.
    
    Args:
        filepath: Path to .out file
        label_mapping: Optional dict mapping filename to label
        fields: List of fields to extract (e.g., ['Ez', 'Ey', 'Hx'])
    
    Returns:
        List of feature dictionaries (one per signal)
    """
    filename = os.path.basename(filepath)
    
    # Determine Label - priority order:
    # 1. Read from HDF5 Title attribute (preferred)
    # 2. Metadata lookup
    # 3. Filename parsing (fallback)
    label = "Unknown"
    
    # Try reading from HDF5 Title attribute first
    try:
        with h5py.File(filepath, 'r') as f:
            if 'Title' in f.attrs:
                title = f.attrs['Title']
                if isinstance(title, bytes):
                    title = title.decode('utf-8')
                # Use Title if it looks like a label (CL, MF, F, HF)
                if title in ['CL', 'MF', 'F', 'HF']:
                    label = title
    except Exception:
        pass  # Silently continue to other methods
    
    # Try metadata lookup if label not found
    if label == "Unknown" and label_mapping:
        # Try both .in and .out extensions
        for ext in ['.in', '.out']:
            lookup_name = filename.replace('.out', ext)
            if lookup_name in label_mapping:
                label = label_mapping[lookup_name]
                break
    
    # Try parsing corresponding .in file
    if label == "Unknown":
        in_filepath = os.path.splitext(filepath)[0] + '.in'
        if os.path.exists(in_filepath):
            try:
                with open(in_filepath, 'r', encoding='utf-8') as f:
                    for line in f:
                        if "## FI class:" in line:
                            # Extract value after colon and strip whitespace
                            label = line.split(":", 1)[1].strip()
                            break
            except Exception:
                pass

    # Fallback to filename parsing
    if label == "Unknown" and len(filename) > 6:
        label = get_label_from_filename(filename)
    
    try:
        # Read HDF5 file
        df = read_gprmax_hdf5(filepath, fields=fields)
        
        if df.empty:
            print(f"  Warning: No data found in {filename}")
            return []
        
        # Determine time step
        dt = 1e-10  # Default value
        if 'Time' in df.columns and len(df) > 1:
            dt = df['Time'].iloc[1] - df['Time'].iloc[0]
        
        # Extract features
        features_df = extract_features(df, dt=dt)
        
        if features_df.empty:
            print(f"  Warning: No features extracted from {filename}")
            return []
        
        # Convert to list of dicts and add metadata
        features_list = features_df.to_dict('records')
        for feat in features_list:
            feat['Filename'] = filename
            feat['Label'] = label
        
        return features_list
        
    except Exception as e:
        print(f"  Error processing {filename}: {e}")
        return []


def create_feature_dataset(input_folder, output_csv='features_dataset.csv', 
                          metadata_file=None, fields=['Ez'], verbose=True):
    """
    Create a feature dataset CSV from all .out files in a folder.
    
    Args:
        input_folder: Path to folder containing .out files
        output_csv: Output CSV filename
        metadata_file: Optional CSV file with filename-to-label mapping
        fields: List of fields to extract
        verbose: Print progress messages
    
    Returns:
        pandas.DataFrame with extracted features
    """
    # Convert to absolute path
    input_folder = os.path.abspath(input_folder)
    
    if not os.path.exists(input_folder):
        print(f"Error: Input folder does not exist: {input_folder}")
        return None
    
    if verbose:
        print(f"\n{'='*60}")
        print(f"Creating Feature Dataset")
        print(f"{'='*60}")
        print(f"Input folder: {input_folder}")
        print(f"Output file:  {output_csv}")
        print(f"Fields:       {fields}")
    
    # Find all .out files
    pattern = os.path.join(input_folder, '*.out')
    files = sorted(glob.glob(pattern))
    
    if not files:
        print(f"\nError: No .out files found in {input_folder}")
        return None
    
    if verbose:
        print(f"\nFound {len(files)} .out files")
    
    # Load metadata if provided
    label_mapping = {}
    if metadata_file:
        if os.path.exists(metadata_file):
            label_mapping = load_metadata(metadata_file)
        else:
            print(f"Warning: Metadata file not found: {metadata_file}")
    
    # Process all files
    all_features = []
    
    if verbose:
        print(f"\n{'='*60}")
        print("Processing files...")
        print(f"{'='*60}")
    
    for i, filepath in enumerate(files, 1):
        if verbose:
            print(f"[{i}/{len(files)}] {os.path.basename(filepath)}")
        
        file_features = process_single_file(filepath, label_mapping, fields)
        all_features.extend(file_features)
    
    # Create DataFrame
    if not all_features:
        print("\nError: No features were extracted from any files")
        return None
    
    df_features = pd.DataFrame(all_features)
    
    # Reorder columns: Filename, Label, Signal first, then features
    priority_cols = ['Filename', 'Label', 'Signal']
    existing_priority = [c for c in priority_cols if c in df_features.columns]
    other_cols = [c for c in df_features.columns if c not in existing_priority]
    df_features = df_features[existing_priority + other_cols]
    
    # Save to CSV
    df_features.to_csv(output_csv, index=False)
    
    if verbose:
        print(f"\n{'='*60}")
        print("Results")
        print(f"{'='*60}")
        print(f"Total features extracted: {len(df_features)}")
        print(f"Unique signals:          {df_features['Signal'].nunique() if 'Signal' in df_features.columns else 'N/A'}")
        print(f"Unique labels:           {df_features['Label'].nunique() if 'Label' in df_features.columns else 'N/A'}")
        print(f"Feature columns:         {len(df_features.columns) - len(existing_priority)}")
        print(f"\nSaved to: {output_csv}")
        print(f"{'='*60}\n")
    
    return df_features


def main():
    parser = argparse.ArgumentParser(
        description='Create a feature dataset CSV from gprMax output files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s samples/
  %(prog)s output/ -o features.csv
  %(prog)s samples/ -m metadata.csv --fields Ez Ey Hx
        """
    )
    
    parser.add_argument(
        'input_folder',
        help='Folder containing .out files to process'
    )
    
    parser.add_argument(
        '-o', '--output',
        default='features_dataset.csv',
        help='Output CSV filename (default: features_dataset.csv)'
    )
    
    parser.add_argument(
        '-m', '--metadata',
        help='Optional metadata CSV file for labeling (should have "filename" and "FI_class" columns)'
    )
    
    parser.add_argument(
        '--fields',
        nargs='+',
        default=['Ez'],
        help='Fields to extract from HDF5 files (default: Ez)'
    )
    
    parser.add_argument(
        '-q', '--quiet',
        action='store_true',
        help='Suppress progress messages'
    )
    
    args = parser.parse_args()
    
    # Create feature dataset
    result = create_feature_dataset(
        input_folder=args.input_folder,
        output_csv=args.output,
        metadata_file=args.metadata,
        fields=args.fields,
        verbose=not args.quiet
    )
    
    # Exit with appropriate code
    sys.exit(0 if result is not None else 1)


if __name__ == "__main__":
    main()

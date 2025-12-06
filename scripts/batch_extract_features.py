import os
import glob
import pandas as pd
import numpy as np
import sys
# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.data_loader import read_gprmax_hdf5
from src.feature_extraction import extract_features

def get_label_from_filename(filename):
    """
    Extracts the classification label from the filename.
    Assumes format like 'A_Cle-A_0000.out', where 'Cle' is the label.
    Specifically, takes characters at indices 2:5.
    """
    basename = os.path.basename(filename)
    # Based on user request: "classify by the tree letters of the filename after the two first letters"
    # Example: A_Cle... -> indices 0,1 are 'A_', then 'Cle' are indices 2,3,4.
    # So slice [2:5] seems correct.
    return basename[6]

def load_metadata(metadata_path):
    """
    Loads metadata from CSV and returns a dictionary mapping filename (.in) to label (FI_class).
    """
    try:
        df = pd.read_csv(metadata_path)
        # Ensure filename and FI_class columns exist
        if 'filename' not in df.columns or 'FI_class' not in df.columns:
            print(f"Error: metadata.csv must contain 'filename' and 'FI_class' columns.")
            return {}
        
        # Create mapping: filename -> FI_class
        return pd.Series(df.FI_class.values, index=df.filename).to_dict()
    except Exception as e:
        print(f"Error loading metadata from {metadata_path}: {e}")
        return {}

def process_single_file_features(filepath, label_mapping=None):
    """
    Extracts features for a single file.
    Returns a list of feature dictionaries (one per signal).
    """
    filename = os.path.basename(filepath)
    
    # Determine Label
    label = "Unknown"
    
    # Try metadata lookup first
    if label_mapping:
        in_filename = filename.replace('.out', '.in')
        if in_filename in label_mapping:
            label = label_mapping[in_filename]
    
    # Fallback to legacy filename parsing
    if label == "Unknown" and filename.startswith('A_') and len(filename) > 5:
         label = get_label_from_filename(filename)
    
    try:
        # Read only Ez field as requested (or make configurable)
        df = read_gprmax_hdf5(filepath, fields=['Ez'])
        
        if df.empty:
            print(f"  Warning: DataFrame empty for {filename}")
            return []
            
        # Extract features
        dt = 1e-10
        if 'Time' in df.columns and len(df) > 1:
            dt = df['Time'].iloc[1] - df['Time'].iloc[0]
            
        features_df = extract_features(df, dt=dt)
        
        if features_df.empty:
            return []
            
        # Add Filename and Label to features
        features_list = features_df.to_dict('records')
        for feat in features_list:
            feat['Filename'] = filename
            feat['Label'] = label
            
        return features_list
        
    except Exception as e:
        print(f"Error processing {filename}: {e}")
        return []

def process_files(input_dir, output_csv='features_dataset.csv', metadata_file=None):
    """
    Iterates over .out files in input_dir, extracts features, and saves to CSV.
    """
    print(f"Searching for .out files in {input_dir}...")
    files = glob.glob(os.path.join(input_dir, '*.out'))
    
    if not files:
        print("No .out files found.")
        return

    print(f"Found {len(files)} files. Starting processing...")
    
    # Load metadata if available
    label_mapping = {}
    if metadata_file and os.path.exists(metadata_file):
        print(f"Loading metadata from {metadata_file}...")
        label_mapping = load_metadata(metadata_file)
    
    all_features = []
    
    for i, filepath in enumerate(files):
        print(f"[{i+1}/{len(files)}] Processing {os.path.basename(filepath)}...")
        file_features = process_single_file_features(filepath, label_mapping)
        all_features.extend(file_features)
        
    if all_features:
        df_out = pd.DataFrame(all_features)
        
        # Reorder columns to have Filename, Label, Signal first
        cols = ['Filename', 'Label', 'Signal']
        existing_cols = [c for c in cols if c in df_out.columns]
        remaining_cols = [c for c in df_out.columns if c not in existing_cols]
        df_out = df_out[existing_cols + remaining_cols]
        
        df_out.to_csv(output_csv, index=False)
        print(f"Saved features to {output_csv}")
    else:
        print("No features extracted.")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Extract GPR features from .out files.")
    parser.add_argument("--input_dir", type=str, default=r'd:\Codigo\Synth-Data\400MHz', help="Directory containing .out files")
    parser.add_argument("--output_csv", type=str, default='features_dataset.csv', help="Output CSV filename")
    parser.add_argument("--metadata", type=str, help="Path to metadata.csv. Defaults to input_dir/metadata.csv")
    
    args = parser.parse_args()
    
    input_dir = args.input_dir
    output_csv = args.output_csv
    
    if args.metadata:
        metadata_file = args.metadata
    else:
        metadata_file = os.path.join(input_dir, 'metadata.csv')
    
    print(f"Input Directory: {input_dir}")
    print(f"Metadata File: {metadata_file}")
    
    if not os.path.exists(input_dir):
        print(f"Error: Input directory {input_dir} does not exist.")
    else:
        process_files(input_dir, output_csv=output_csv, metadata_file=metadata_file)

import os
import glob
import pandas as pd
from src.data_loader import read_gprmax_hdf5
from src.feature_extraction import extract_features
from visualization.plot_utils import save_feature_summary_plot
from scripts.main.batch_extract_features import process_single_file_features, load_metadata

def process_file(filepath, output_dir=None, fields=['Ez'], generate_images=False):
    """
    Runs the pipeline for a single file: Load -> Extract -> Visualize.
    """
    if not os.path.exists(filepath):
        print(f"Error: File {filepath} not found.")
        return

    print(f"--- Processing {filepath} ---")
    
    # 1. Load Data
    df = read_gprmax_hdf5(filepath, fields=fields)
    if df.empty:
        print(f"Warning: No data found in {filepath}")
        return

    # 2. Extract Features
    # Determine dt
    dt = 1e-10
    if 'Time' in df.columns and len(df) > 1:
        dt = df['Time'].iloc[1] - df['Time'].iloc[0]
        
    features_df = extract_features(df, dt=dt)
    
    if features_df.empty:
        print(f"Warning: No features extracted for {filepath}")
        return

    # 3. Visualize
    if generate_images:
        # Save plots to output_dir if specified, else same as input
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
            base_dir = output_dir
        else:
            base_dir = os.path.dirname(filepath)
            
        base_name = os.path.basename(filepath).replace('.out', '')
        
        for index, row in features_df.iterrows():
            signal_name = row['Signal']
            output_filename = os.path.join(base_dir, f"{base_name}_{signal_name}_features.png")
            
            print(f"  Plotting {signal_name} -> {output_filename}")
            save_feature_summary_plot(features_df, df, signal_name, output_filename=output_filename)
    else:
        print("  Skipping image generation.")

def process_directory(input_dir, output_dir=None, fields=['E', 'H'], generate_images=False, output_csv='features_dataset.csv', metadata_file=None):
    """
    Iterates over all .out files in the directory, processes them, and saves features to a CSV.
    """
    files = glob.glob(os.path.join(input_dir, "*.out"))
    if not files:
        print(f"No .out files found in directory: {input_dir}")
        return
        
    print(f"Found {len(files)} files in {input_dir}")
    
    # Load metadata if available
    label_mapping = {}
    if metadata_file and os.path.exists(metadata_file):
        print(f"Loading metadata from {metadata_file}...")
        label_mapping = load_metadata(metadata_file)
    
    all_features = []
    
    for i, filepath in enumerate(files):
        print(f"[{i+1}/{len(files)}] Processing {os.path.basename(filepath)}...")
        
        # 1. Process for Visualization (if enabled)
        # We call process_file mainly for visualization side effects if enabled.
        # However, process_file re-reads and re-extracts. Ideally we avoid double work.
        # But for now, let's keep them separate or refactor process_file to return features.
        # Refactoring process_file to return features is better, but to minimize changes let's just use process_single_file_features for CSV.
        
        if generate_images:
             process_file(filepath, output_dir=output_dir, fields=fields, generate_images=True)
        
        # 2. Extract Features for CSV
        # Using the batch extraction logic which handles labeling
        file_features = process_single_file_features(filepath, label_mapping)
        all_features.extend(file_features)

    # Save CSV
    if all_features:
        df_out = pd.DataFrame(all_features)
        
        # Reorder columns
        cols = ['Filename', 'Label', 'Signal']
        existing_cols = [c for c in cols if c in df_out.columns]
        remaining_cols = [c for c in df_out.columns if c not in existing_cols]
        df_out = df_out[existing_cols + remaining_cols]
        
        # Save to output_dir if specified, else current dir
        if output_dir:
            csv_path = os.path.join(output_dir, output_csv)
        else:
            csv_path = output_csv
            
        df_out.to_csv(csv_path, index=False)
        print(f"\nSaved accumulated features to {csv_path}")
    else:
        print("\nNo features extracted.")

def main():
    # --- Configuration ---
    # Path to a single .out file or a directory containing .out files
    input_path = "samples" 
    # input_path = "samples/A_Cle-A_0001.out" 
    
    # Directory to save outputs (optional, set to None to save in same directory as input)
    output_dir = None 
    
    # Fields to extract
    fields = ['Ez']
    
    # Image Generation Toggle
    generate_images = False
    
    # CSV Output (for directory processing)
    output_csv = 'features_dataset.csv'
    metadata_file = 'synthetic_inputs/metadata.csv' # Adjust path as needed
    # ---------------------

    print(f"Input Path: {input_path}")
    print(f"Output Directory: {output_dir if output_dir else 'Same as input'}")
    print(f"Fields: {fields}")
    print(f"Generate Images: {generate_images}")
    
    if os.path.isfile(input_path):
        process_file(input_path, output_dir=output_dir, fields=fields, generate_images=generate_images)
    elif os.path.isdir(input_path):
        process_directory(input_path, output_dir=output_dir, fields=fields, generate_images=generate_images, output_csv=output_csv, metadata_file=metadata_file)
    else:
        print(f"Error: Invalid path {input_path}")

if __name__ == "__main__":
    main()

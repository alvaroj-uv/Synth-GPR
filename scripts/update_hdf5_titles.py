import pandas as pd
import h5py
import os
import argparse
from tqdm import tqdm

def update_titles(csv_path, folder_path):
    print(f"Reading labels from: {csv_path}")
    try:
        df = pd.read_csv(csv_path)
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return

    if 'Filename' not in df.columns or 'Label' not in df.columns:
        print("Error: CSV must contain 'Filename' and 'Label' columns.")
        return

    # Create a mapping dictionary to handle potential duplicates (though distinct filenames shouldn't duplicate)
    # If multiple signals exist for one file, just take the first label found (should be same for the file)
    file_label_map = dict(zip(df['Filename'], df['Label']))
    
    print(f"Found {len(file_label_map)} unique files in CSV.")
    print(f"Target folder: {folder_path}")

    updated_count = 0
    error_count = 0
    skipped_count = 0

    files_in_folder = os.listdir(folder_path)
    # Filter for .out files to match against map
    
    # We iterate through the map to ensure we process known files
    for filename, label in tqdm(file_label_map.items(), desc="Updating HDF5 Titles"):
        filepath = os.path.join(folder_path, filename)
        
        if not os.path.exists(filepath):
            # It might be that the CSV has filenames that are not in the folder? 
            # Or vice versa.
            # print(f"File not found: {filepath}")
            skipped_count += 1
            continue

        try:
            with h5py.File(filepath, 'r+') as f:
                # Update Title attribute
                # HDF5 attributes can be bytes or string. gprMax usually uses string/bytes.
                # Let's write as string (utf-8)
                f.attrs['Title'] = str(label)
                updated_count += 1
        except Exception as e:
            print(f"Failed to update {filename}: {e}")
            error_count += 1

    print("\nUpdate Complete.")
    print(f"Updated: {updated_count}")
    print(f"Skipped (not found): {skipped_count}")
    print(f"Errors: {error_count}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Update HDF5 Title attributes based on a CSV mapping.")
    parser.add_argument("folder", help="Folder containing .out files")
    parser.add_argument("csv", help="Path to features_dataset.csv containing Filename and Label")
    
    args = parser.parse_args()
    
    update_titles(args.csv, args.folder)

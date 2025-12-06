import pandas as pd
import argparse
import sys
from pathlib import Path

def merge_datasets(file_paths, output_path, deduplicate=False):
    dfs = []
    print(f"Merging {len(file_paths)} files...")
    
    for p in file_paths:
        p = Path(p)
        if not p.exists():
            print(f"Error: File not found: {p}")
            return False
            
        try:
            print(f"Reading {p}...")
            df = pd.read_csv(p)
            print(f"  - shape: {df.shape}")
            dfs.append(df)
        except Exception as e:
            print(f"Error reading {p}: {e}")
            return False
            
    if not dfs:
        print("No dataframes to merge.")
        return False
        
    combined_df = pd.concat(dfs, ignore_index=True)
    
    if deduplicate:
        initial_count = len(combined_df)
        combined_df.drop_duplicates(inplace=True)
        final_count = len(combined_df)
        if initial_count > final_count:
             print(f"Removed {initial_count - final_count} duplicate rows.")
        else:
             print("No duplicate rows found.")
    
    print(f"Combined shape: {combined_df.shape}")
    
    try:
        combined_df.to_csv(output_path, index=False)
        print(f"Saved merged dataset to: {output_path}")
        return True
    except Exception as e:
        print(f"Error saving to {output_path}: {e}")
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Merge multiple CSV feature datasets.")
    parser.add_argument("files", nargs="+", help="Input CSV files to merge")
    parser.add_argument("-o", "--output", required=True, help="Output CSV file path")
    parser.add_argument("--dedup", action="store_true", help="Remove duplicate rows")
    
    args = parser.parse_args()
    
    success = merge_datasets(args.files, args.output, deduplicate=args.dedup)
    sys.exit(0 if success else 1)

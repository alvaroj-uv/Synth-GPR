#!/usr/bin/env python3
"""
Consolidate datasets from multiple folders into a single canonical directory.
Renames files sequentially (s_0000, s_0001, ...) and creates a master metadata index.

Usage:
    python scripts/pipeline/consolidate_dataset.py

Configuration:
    Edit the 'folders' list in the main block of this script to specify source directories.

Verification:
    1. Check the target folder (e.g. d:/Codigo/Synth-Data/Consolidated) for rename files.
    2. Check 'master_index.csv' in the target folder for the mapping of Old Name -> New Name.
"""

import shutil
import pandas as pd
from pathlib import Path
from tqdm import tqdm

def consolidate_data(source_folders, output_folder):
    """
    Consolidate datasets from multiple folders into one, renumbering files.
    """
    output_folder = Path(output_folder)
    output_folder.mkdir(parents=True, exist_ok=True)
    
    mapping_data = []
    current_id = 0
    
    print(f"Consolidating to {output_folder}...")
    
    # Determine start ID
    existing_files = list(output_folder.glob("s_*.in"))
    if existing_files:
        current_id = len(existing_files)
        print(f"Appending to existing folder. Start ID: {current_id}")
    else:
        current_id = 0

    for folder in source_folders:
        folder = Path(folder)
        if not folder.exists():
            print(f"Warning: Folder not found: {folder}")
            continue
            
        # Find all .in files
        in_files = sorted(list(folder.glob("*.in")))
        print(f"Processing {folder.name} ({len(in_files)} files)...")
        
        for in_file in tqdm(in_files):
            # Check for corresponding .out file
            out_file = in_file.with_suffix('.out')
            
            if not out_file.exists():
                # print(f"Skipping {in_file.name}: No corresponding .out file")
                continue
                
            # New base name
            new_base = f"s_{current_id:05d}"
            new_in = output_folder / f"{new_base}.in"
            new_out = output_folder / f"{new_base}.out"
            
            # Copy files
            shutil.copy2(in_file, new_in)
            shutil.copy2(out_file, new_out)
            
            # Record mapping
            mapping_data.append({
                "original_folder": str(folder),
                "original_filename": in_file.name,
                "new_filename": new_in.name,
                "id": current_id
            })
            
            current_id += 1
            
    # Save mapping (append if exists)
    mapping_csv = output_folder / "filename_mapping.csv"
    mode = 'a' if mapping_csv.exists() else 'w'
    header = not mapping_csv.exists()
    pd.DataFrame(mapping_data).to_csv(mapping_csv, index=False, mode=mode, header=header)
    print(f"\nConsolidation complete. {current_id} total samples.")

if __name__ == "__main__":
    
    # Append mode example:
    sources = [
        r"d:\Codigo\Synth-Data\400MHz\Extra_Stratified"
    ]
    
    target = r"d:\Codigo\Synth-Data\Merged_400MHz"
    
    consolidate_data(sources, target)

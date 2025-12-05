#!/usr/bin/env python3
"""
Script to update HDF5 output file titles to match the FI_class from corresponding input files.

Reads FI_class from either:
1. The #title field (for new files generated with updated generator)
2. The ## FI class: comment line (for old files)

Usage:
    python update_hdf5_titles.py <folder_path>
    
Example:
    python update_hdf5_titles.py synthetic_inputs/
"""

import os
import sys
import h5py
import argparse
import re
from pathlib import Path


def extract_fi_class_code(fi_class_full):
    """
    Extract the short code from FI_class string.
    Examples:
        "Moderately Fouled (MF)" -> "MF"
        "Clean (CL)" -> "CL"
        "MF" -> "MF"
    """
    # Check if already in short form
    if fi_class_full in ['CL', 'MF', 'F', 'HF']:
        return fi_class_full
    
    # Extract code from parentheses
    match = re.search(r'\(([A-Z]+)\)', fi_class_full)
    if match:
        return match.group(1)
    
    return fi_class_full


def read_fi_class_from_input_file(input_file_path):
    """
    Read the FI_class from a gprMax input file.
    
    Tries two methods:
    1. Read from #title field (new format)
    2. Read from ## FI class: comment (old format)
    
    Args:
        input_file_path: Path to the .in file
        
    Returns:
        The FI_class code (e.g., "CL", "MF", "F", "HF"), or None if not found
    """
    try:
        title_value = None
        fi_class_comment = None
        
        with open(input_file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line_stripped = line.strip()
                
                # Check for #title field
                if line_stripped.startswith('#title:'):
                    title_value = line_stripped.split(':', 1)[1].strip()
                
                # Check for ## FI class: comment
                if line_stripped.startswith('## FI class:'):
                    fi_class_comment = line_stripped.split(':', 1)[1].strip()
        
        # Prefer #title if it looks like a class code
        if title_value and title_value in ['CL', 'MF', 'F', 'HF']:
            return title_value
        
        # Otherwise, extract from comment
        if fi_class_comment:
            return extract_fi_class_code(fi_class_comment)
        
        # Fallback: if #title exists but isn't a class code, use it as-is
        if title_value:
            return title_value
            
        return None
        
    except Exception as e:
        print(f"  Error reading {input_file_path}: {e}")
        return None


def update_hdf5_title(hdf5_file_path, new_title):
    """
    Update the Title attribute in an HDF5 file.
    
    Args:
        hdf5_file_path: Path to the .out (HDF5) file
        new_title: New title string to set
        
    Returns:
        True if successful, False otherwise
    """
    try:
        with h5py.File(hdf5_file_path, 'r+') as f:
            # Update or create the Title attribute (note: capital T)
            if 'Title' in f.attrs:
                old_title = f.attrs['Title']
                if isinstance(old_title, bytes):
                    old_title = old_title.decode('utf-8')
                print(f"    Old Title: '{old_title}'")
            else:
                print(f"    No previous Title attribute")
            
            # Set the new Title
            f.attrs['Title'] = new_title
            print(f"    New Title: '{new_title}'")
            
        return True
    except Exception as e:
        print(f"  Error updating {hdf5_file_path}: {e}")
        return False


def process_folder(folder_path, dry_run=False):
    """
    Process all .out files in a folder, updating their titles from corresponding .in files.
    
    Args:
        folder_path: Path to folder containing .in and .out files
        dry_run: If True, only show what would be done without making changes
    """
    folder_path = Path(folder_path).resolve()
    
    if not folder_path.exists():
        print(f"Error: Folder does not exist: {folder_path}")
        return
    
    print(f"\n{'='*70}")
    print(f"Updating HDF5 Titles with FI_class from Input Files")
    print(f"{'='*70}")
    print(f"Folder: {folder_path}")
    print(f"Mode: {'DRY RUN (no changes)' if dry_run else 'LIVE (making changes)'}")
    print(f"{'='*70}\n")
    
    # Find all .out files
    out_files = sorted(folder_path.glob('*.out'))
    
    if not out_files:
        print(f"No .out files found in {folder_path}")
        return
    
    print(f"Found {len(out_files)} .out files\n")
    
    success_count = 0
    skip_count = 0
    error_count = 0
    
    for out_file in out_files:
        # Find corresponding .in file
        in_file = out_file.with_suffix('.in')
        
        print(f"[{success_count + skip_count + error_count + 1}/{len(out_files)}] {out_file.name}")
        
        if not in_file.exists():
            print(f"  WARNING: No matching .in file found: {in_file.name}")
            skip_count += 1
            continue
        
        # Read FI_class from input file
        fi_class = read_fi_class_from_input_file(in_file)
        
        if fi_class is None:
            print(f"  WARNING: No FI_class found in {in_file.name}")
            skip_count += 1
            continue
        
        print(f"  Found FI_class in {in_file.name}: '{fi_class}'")
        
        # Update HDF5 file
        if not dry_run:
            if update_hdf5_title(out_file, fi_class):
                success_count += 1
            else:
                error_count += 1
        else:
            print(f"  [DRY RUN] Would update title to: '{fi_class}'")
            success_count += 1
        
        print()
    
    # Summary
    print(f"{'='*70}")
    print(f"Summary")
    print(f"{'='*70}")
    print(f"Total processed: {len(out_files)}")
    print(f"Successfully updated: {success_count}")
    print(f"Skipped: {skip_count}")
    print(f"Errors: {error_count}")
    print(f"{'='*70}\n")


def main():
    parser = argparse.ArgumentParser(
        description='Update HDF5 output file titles with FI_class from corresponding input files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s synthetic_inputs/
  %(prog)s output/ --dry-run
        """
    )
    
    parser.add_argument(
        'folder',
        help='Folder containing .in and .out file pairs'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be done without making changes'
    )
    
    args = parser.parse_args()
    
    process_folder(args.folder, dry_run=args.dry_run)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Quick analysis of dataset structure - samples only."""

import sys
from pathlib import Path
from collections import defaultdict
import h5py

def parse_in_file(in_path):
    """Extract metadata from .in file header."""
    metadata = {}
    with open(in_path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line.startswith('##'):
                break
            if ':' in line:
                parts = line[2:].split(':', 1)
                if len(parts) == 2:
                    key = parts[0].strip()
                    val = parts[1].strip()
                    metadata[key] = val
    return metadata


def main():
    datasets = {
        'gpr_dataset_10k': Path('output/gpr_dataset_10k'),
        'dataset_variants': Path('output/dataset_variants'),
    }

    print("\n" + "="*80)
    print("DATASET STRUCTURE ANALYSIS - .IN FILES (INDEPENDENT VARIABLES)")
    print("="*80)

    for dataset_name, dataset_dir in datasets.items():
        print(f"\n{dataset_name}:")
        print("-" * 80)

        # Sample 5 files
        sample_files = sorted(dataset_dir.glob("*.in"))[:5]
        all_attrs = defaultdict(set)

        for in_file in sample_files:
            metadata = parse_in_file(in_file)
            for key, val in metadata.items():
                all_attrs[key].add(val)

        # Print all attributes found
        print(f"\nAttributes found in .in file headers:")
        for i, attr_name in enumerate(sorted(all_attrs.keys()), 1):
            values = list(all_attrs[attr_name])
            print(f"  {i:2d}. {attr_name:<30} | Sample values: {values[0]}")

    print("\n" + "="*80)
    print("DATASET STRUCTURE ANALYSIS - .OUT FILES (HDF5 FORMAT)")
    print("="*80)

    for dataset_name, dataset_dir in datasets.items():
        out_file = list(dataset_dir.glob("*.out"))[0]
        print(f"\n{dataset_name}:")
        print(f"  File: {out_file.name}")
        print("-" * 80)

        try:
            with h5py.File(out_file, 'r') as f:
                def show_keys(name, obj, indent=2):
                    if isinstance(obj, h5py.Group):
                        print(" " * indent + f"[Group] {name}")
                    else:
                        dtype_str = str(obj.dtype)
                        shape_str = str(obj.shape)
                        print(" " * indent + f"[Dataset] {name}: shape={shape_str}, dtype={dtype_str}")

                # Show first level only
                print("\n  Top-level structure:")
                for key in f.keys():
                    if isinstance(f[key], h5py.Group):
                        print(f"    [Group] {key}/")
                        # Show subkeys
                        for subkey in f[key].keys():
                            print(f"      └─ {subkey}")
                    else:
                        obj = f[key]
                        print(f"    [Dataset] {key}: shape={obj.shape}, dtype={obj.dtype}")

        except Exception as e:
            print(f"  Error reading file: {e}")

    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print(f"""
Dataset Overview:
  • gpr_dataset_10k: 50,000 samples
  • dataset_variants: 30,000 samples
  • Total: 80,000 samples

Structure:
  • Each sample consists of:
    - .in file: Text file with metadata (independent variables/parameters)
    - .out file: HDF5 binary file with simulation output (Ez field data)

Next Step:
  • Create a feature extraction and RF training pipeline that:
    1. Loads .in file headers as features
    2. Extracts Ez field data from .out HDF5 files
    3. Combines features for each sample
    4. Trains RF classifier with Lab_Class as target
""")


if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
    main()

#!/usr/bin/env python3
"""
Analyze .in and .out files to understand their structure before training RF.
Extract metadata from .in files and verify .out file structure.

I/O note: this is a low-level HDF5 *introspection* diagnostic — it walks raw
groups/datasets to report file structure, which is its whole purpose. It is the
sanctioned exception to the "no raw h5py in scripts" rule (see
docs/architecture/IO_CONSOLIDATION_PLAN.md); signal reads go through
src.data_loader.
"""

import sys
from pathlib import Path
from collections import defaultdict, Counter
import h5py

def parse_in_file(in_path):
    """Extract metadata from .in file header comments."""
    metadata = {}
    with open(in_path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line.startswith('##'):
                break
            # Parse "## key: value" format
            if ':' in line:
                parts = line[2:].split(':', 1)
                if len(parts) == 2:
                    key = parts[0].strip()
                    val = parts[1].strip()
                    metadata[key] = val
    return metadata


def analyze_out_file(out_path):
    """Check structure of .out file (HDF5 format)."""
    try:
        with h5py.File(out_path, 'r') as f:
            keys = list(f.keys())
            return {'format': 'HDF5', 'keys': keys}
    except Exception as e:
        return {'format': 'unknown', 'error': str(e)}


def main():
    datasets = {
        'gpr_dataset_10k': Path('output/gpr_dataset_10k'),
        'dataset_variants': Path('output/dataset_variants'),
    }

    all_metadata = {}

    for dataset_name, dataset_dir in datasets.items():
        print(f"\n{'='*70}")
        print(f"Analyzing: {dataset_name}")
        print(f"{'='*70}")

        in_files = sorted(dataset_dir.glob("*.in"))[:5]  # Sample first 5

        if not in_files:
            print(f"No .in files found in {dataset_dir}")
            continue

        print(f"\nSampling {len(in_files)} .in files...")
        all_keys = Counter()

        for in_file in in_files:
            metadata = parse_in_file(in_file)
            for key in metadata.keys():
                all_keys[key] += 1

        # Analyze full dataset for key distribution
        all_in_files = sorted(dataset_dir.glob("*.in"))
        unique_attrs = defaultdict(set)

        print(f"Scanning all {len(all_in_files)} files for attribute values...")
        for i, in_file in enumerate(all_in_files):
            if (i + 1) % 10000 == 0:
                print(f"  Processed {i + 1}/{len(all_in_files)}")

            metadata = parse_in_file(in_file)
            for key, val in metadata.items():
                unique_attrs[key].add(val)

        print(f"\n{'INDEPENDENT VARIABLES (from .in file headers)':^70}")
        print(f"{'-'*70}")

        for attr in sorted(unique_attrs.keys()):
            values = unique_attrs[attr]
            n_unique = len(values)
            sample_vals = list(values)[:3]
            print(f"  {attr:<30} : {n_unique:>5} unique values")
            if n_unique <= 10:
                print(f"    Values: {', '.join(map(str, sorted(values)))}")
            else:
                print(f"    Sample: {', '.join(map(str, sample_vals))}")

        all_metadata[dataset_name] = unique_attrs

    # Analyze .out file structure
    print(f"\n{'='*70}")
    print(f"Analyzing .out files (HDF5 structure)")
    print(f"{'='*70}")

    for dataset_name, dataset_dir in datasets.items():
        out_files = sorted(dataset_dir.glob("*.out"))[:1]
        if out_files:
            out_path = out_files[0]
            print(f"\n{dataset_name}:")
            print(f"  File: {out_path.name}")

            analysis = analyze_out_file(out_path)
            if analysis['format'] == 'HDF5':
                print(f"  Format: HDF5")
                print(f"  Top-level keys: {analysis['keys']}")

                # Detailed structure
                with h5py.File(out_path, 'r') as f:
                    print(f"\n  Detailed structure:")

                    def print_structure(name, obj, indent=4):
                        prefix = " " * indent
                        if isinstance(obj, h5py.Group):
                            print(f"{prefix}[Group] {name}/")
                        else:
                            shape = obj.shape
                            dtype = obj.dtype
                            print(f"{prefix}[Dataset] {name}")
                            print(f"{prefix}  shape: {shape}, dtype: {dtype}")

                    f.visititems(lambda name, obj: print_structure(name, obj) if '/' not in name or name.count('/') <= 1 else None)
            else:
                print(f"  Error: {analysis.get('error', 'Unknown format')}")

    # Summary
    print(f"\n{'='*70}")
    print(f"SUMMARY")
    print(f"{'='*70}")
    print(f"\nDataset Comparison:")
    print(f"  gpr_dataset_10k    : 50,000 samples")
    print(f"  dataset_variants   : 30,000 samples")
    print(f"  Total              : 80,000 samples")

    print(f"\nDEPENDENT VARIABLE (Classification Target):")
    print(f"  Source: Lab_Class from .in file headers")
    print(f"  Classes: {sorted(all_metadata['gpr_dataset_10k'].get('Lab_Class', set()))}")

    print(f"\nINDEPENDENT VARIABLES:")
    print(f"  Numerical features from .in file headers (input parameters)")
    print(f"  Features from Ez field data in .out HDF5 files")


if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
    main()

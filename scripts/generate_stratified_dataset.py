#!/usr/bin/env python3
"""
Script to generate stratified synthetic GPR data (specific classes).
"""

import sys
import argparse
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.synthetic_data_generator import GeneratorConfig, BallastScenarioGenerator

def generate_stratified(output_dir, labels, n_per_label=50, start_id=10000):
    """
    Generates n samples for each requested label.
    Labels: CL, MC, MF, F, HF
    """
    print(f"Generating {n_per_label} samples for each: {labels}")
    print(f"Output directory: {output_dir}")
    
    # Define PVC ranges for each class
    # CL: 0-5, MC: 5-20, MF: 20-40, F: 40-60, HF: >60 (say 60-100)
    pvc_ranges = {
        'CL': (0.0, 5.0),
        'MC': (5.0, 20.0),
        'MF': (20.0, 40.0),
        'F':  (40.0, 60.0),
        'HF': (60.0, 100.0)
    }
    
    current_id = start_id
    total_generated = 0
    all_dfs = []
    
    for label in labels:
        if label not in pvc_ranges:
            print(f"Unknown label: {label}, skipping.")
            continue
            
        pmin, pmax = pvc_ranges[label]
        print(f"  Generating {label} (PVC {pmin}-{pmax}%)...")
        
        cfg = GeneratorConfig(
            base_seed=current_id,
            add_waveform=True,
            add_source=True,
            granular_mode=True,
            pvc_min=pmin,
            pvc_max=pmax,
            moisture_min=0.0, 
            moisture_max=0.15, # Slight variation
        )
        
        gen = BallastScenarioGenerator(cfg)
        
        # Generate batch
        df = gen.generate_dataset(
            out_dir=output_dir,
            n_samples=n_per_label,
            csv_name=f"metadata_{label}.csv",
            start_id=current_id
        )
        
        current_id += n_per_label
        total_generated += len(df)
        all_dfs.append(df)
        
    print(f"Successfully generated {total_generated} samples.")
    
    return total_generated

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate Stratified synthetic samples.")
    parser.add_argument("output_dir", help="Directory to save output files")
    parser.add_argument("--labels", nargs="+", default=['CL', 'MC', 'MF', 'F'], help="Labels to generate (CL MC MF F HF)")
    parser.add_argument("-n", "--num", type=int, default=50, help="Samples per label")
    parser.add_argument("--start_id", type=int, default=10000, help="Starting ID")
    
    args = parser.parse_args()
    
    generate_stratified(args.output_dir, args.labels, args.num, args.start_id)

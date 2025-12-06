#!/usr/bin/env python3
"""
Script to generate 'Clean' scenario (PVC <= 5%) synthetic GPR data.
"""

import sys
import argparse
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.synthetic_data_generator import GeneratorConfig, BallastScenarioGenerator

def generate_clean_data(output_dir, n_samples=50, start_id=3000):
    """
    Generates Clean samples.
    """
    print(f"Generating {n_samples} Clean samples (PVC 0-5%)...")
    print(f"Output directory: {output_dir}")
    
    # Configure for Clean Ballast (Granular Mode)
    cfg = GeneratorConfig(
        # Simulation
        base_seed=start_id, # Use start_id as seed base for reproducibility
        add_waveform=True,
        add_source=True,
        add_geometry_view=False,
        
        # Granular Mode
        granular_mode=True,
        
        # Class Definition: Clean (PVC <= 5%)
        pvc_min=0.0,
        pvc_max=5.0,
        
        # Moisture (Clean ballast drains well, but some moisture is possible)
        moisture_min=0.0,
        moisture_max=0.10, 
        
        # Geometry constraints (keep consistent with other datasets)
        min_ballast_thickness=0.25,
        max_ballast_thickness=0.45,
    )
    
    gen = BallastScenarioGenerator(cfg)
    
    # Generate
    df = gen.generate_dataset(
        out_dir=output_dir,
        n_samples=n_samples,
        csv_name="metadata.csv",
        start_id=start_id
    )
    
    print(f"Successfully generated {len(df)} samples.")
    print(f"Metadata saved to {output_dir}/metadata.csv")
    
    return df

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate Clean synthetic blocks.")
    parser.add_argument("output_dir", help="Directory to save output files")
    parser.add_argument("-n", "--num", type=int, default=50, help="Number of samples to generate")
    parser.add_argument("--start_id", type=int, default=3000, help="Starting ID for filenames")
    
    args = parser.parse_args()
    
    generate_clean_data(args.output_dir, args.num, args.start_id)

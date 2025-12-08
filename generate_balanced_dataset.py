import os
import random
import shutil
import sys
from pathlib import Path
from src.dataset_generator import DatasetGenerator
from src.config import GeneratorConfig
from src.physics import inverse_convert_fi_to_pvc

OUT_DIR = "output/balanced_dataset"
SAMPLES_PER_CLASS = 2  # Small number for verification, user can increase

# Selig & Waters Ranges (FI)
CLASSES = {
    "C": (0.0, 1.0),
    "MC": (1.0, 10.0),
    "MF": (10.0, 20.0),
    "F": (20.0, 40.0),
    "HF": (40.0, 50.0) # Cap at 50 for realistic max fouling
}


import time

def scale_pvc_for_classes(n_samples: int, base_output_dir: str):
    # Create timestamped run folder
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    output_dir = os.path.join(base_output_dir, timestamp)
    
    print(f"\n[Strategy] Generating {n_samples} samples per class (Total: {n_samples*5})")
    print(f"[Output] {output_dir}")
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Use a base config
    cfg = GeneratorConfig(
        center_freq=4e8,
        time_window=2e-8,
        domain_x=0.5,
        domain_y=1.5,
        domain_z=0.005,
        granular_mode=True,
        base_seed=42
    )
    generator = DatasetGenerator(cfg)
    all_metadata = []
    
    for cls_name, (min_fi, max_fi) in CLASSES.items():
        print(f"\n--- Generating Class {cls_name} (Target FI: {min_fi}-{max_fi}%) ---")
        
        # We process in chunks to avoid memory issues if any, although here it's file IO
        for i in range(n_samples):
            # 1. Pick a random Target FI in the class range
            target_fi = random.uniform(min_fi, max_fi)
            
            # 2. Solve for required PVC
            required_pvc = inverse_convert_fi_to_pvc(target_fi)
            
            # 3. Validation and Clamping
            if required_pvc > 100:
                # We do not print warn for every sample in production, it's expected for HF
                required_pvc = 100.0
            
            # 4. Override Generator params
            specific_cfg = GeneratorConfig(
                center_freq=4e8,
                time_window=2e-8,
                domain_x=0.5,
                domain_y=1.5,
                domain_z=0.005,
                granular_mode=True,
                pvc_min=required_pvc,
                pvc_max=required_pvc, # Force exact value
                moisture_min=0.05,
                moisture_max=0.20,
                base_seed=random.randint(1000, 999999),
                output_dir=output_dir
            )
            
            single_gen = DatasetGenerator(specific_cfg)
            
            # ID scheme: 
            # C:  0-999
            # MC: 1000-1999
            # etc. requires n_samples <= 1000 if we use this multiplier.
            # Let's use a continuous offset based on n_samples
            
            cls_idx = list(CLASSES.keys()).index(cls_name)
            global_id = (cls_idx * n_samples) + i
            
            # Generate sample, DO NOT write metadata to disk yet (save_metadata=False)
            _, rows = single_gen.generate_samples(output_dir, n_samples=1, start_id=global_id, save_metadata=False)
            all_metadata.extend(rows)
            
    # Write aggregated metadata
    if all_metadata:
        import pandas as pd
        df = pd.DataFrame(all_metadata)
        # Format floats
        float_cols = df.select_dtypes(include=['float64', 'float32']).columns
        for col in float_cols:
            df[col] = df[col].apply(lambda x: float(f'{x:.5g}') if pd.notna(x) else x)
            
        csv_path = os.path.join(output_dir, "metadata.csv")
        df.to_csv(csv_path, index=False, float_format='%.5g')
        print(f"[OK] Full Metadata saved to {csv_path} with {len(df)} rows")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Generate balanced GPR dataset.")
    parser.add_argument("-n", "--count", type=int, default=SAMPLES_PER_CLASS, help="Samples per class")
    parser.add_argument("-o", "--output", type=str, default=OUT_DIR, help="Base Output directory")
    
    args = parser.parse_args()
    
    scale_pvc_for_classes(args.count, args.output)

#!/usr/bin/env python3
"""
Unified script to generate synthetic GPR data.
Replaces: generate_clean_dataset.py, generate_stratified_dataset.py, generate_augmented_dataset.py

Features:
- Generates samples for specified labels (CL, MC, MF, F, HF).
- Supports spatial augmentation (Left/Right antenna shifts).
- Uses standard geometry defaults (0.8m domain, 0.2m subgrade).
- Handles metadata creation automatically.
"""

import pandas as pd
import argparse
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.synthetic_data_generator import GeneratorConfig, BallastScenarioGenerator

def generate_dataset(output_dir, labels, n_per_label=50, start_id=20000, augment=False, offsets=[-0.10, 0.10]):
    """
    Generates synthetic GPR samples.
    
    Args:
        output_dir: Target directory.
        labels: List of class labels to generate.
        n_per_label: Base samples per label.
        start_id: Starting ID for filenames.
        augment: If True, generates Left/Right shifted versions for each sample.
        offsets: List of X-offsets (meters) for augmentation.
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"Generating dataset in: {output_dir}")
    print(f"Labels: {labels}")
    print(f"Base samples/label: {n_per_label}")
    print(f"Augmentation: {'Enabled' if augment else 'Disabled'}")
    
    # PVC Ranges for each class
    pvc_ranges = {
        'CL': (0.0, 5.0),
        'MC': (5.0, 20.0),
        'MF': (20.0, 40.0),
        'F':  (40.0, 60.0),
        'HF': (60.0, 100.0)
    }

    current_id = start_id
    all_rows = []
    
    for label in labels:
        if label not in pvc_ranges:
            print(f"Warning: Skipping unknown label '{label}'")
            continue
            
        pmin, pmax = pvc_ranges[label]
        print(f"\nProcessing {label} (PVC {pmin}-{pmax}%)...")
        
        # Configure Generator
        # Note: GeneratorConfig defaults (updated in source) are used:
        # domain_x=0.8, domain_y=1.5, subgrade=0.20
        # tx_x=0.375, rx_x=0.425
        
        cfg = GeneratorConfig(
            base_seed=current_id,
            add_waveform=True,
            add_source=True,
            # add_geometry_view is False by default (commented out in .in file)
            granular_mode=True,
            pvc_min=pmin,
            pvc_max=pmax,
            moisture_min=0.0, 
            moisture_max=0.15,
            # Explicitly set geometry to ensure consistency if defaults change
            domain_x=0.8,
            domain_y=1.5,
            subgrade_thickness=0.20,
            tx_x=0.375,
            rx_x=0.425
        )
        
        gen = BallastScenarioGenerator(cfg)
        
        # 1. Generate Base Samples
        print(f"  Generating {n_per_label} base samples...")
        temp_csv = f"temp_metadata_{label}.csv"
        
        df = gen.generate_dataset(
            out_dir=output_dir,
            n_samples=n_per_label,
            csv_name=temp_csv,
            start_id=current_id
        )
        
        # 2. Process Files (Augmentation & Metadata Collection)
        for _, row in df.iterrows():
            base_filename = row['filename']
            base_path = output_dir / base_filename
            
            # Read base content
            content = base_path.read_text(encoding='utf-8')
            
            # Add base entry (Center / Offset 0)
            row_dict = row.to_dict()
            row_dict['antenna_offset_x'] = 0.0
            all_rows.append(row_dict)
            
            if augment:
                for off in offsets:
                    # Determine suffix
                    suffix = "left" if off < 0 else "right"
                    new_filename = base_filename.replace(".in", f"_{suffix}.in")
                    new_path = output_dir / new_filename
                    
                    # Modify content
                    new_content = modify_antenna_position(content, off)
                    
                    # Write file
                    new_path.write_text(new_content, encoding='utf-8')
                    
                    # Add metadata entry
                    new_row = row_dict.copy()
                    new_row['filename'] = new_filename
                    new_row['antenna_offset_x'] = off
                    all_rows.append(new_row)
        
        # Cleanup temp CSV per label
        (output_dir / temp_csv).unlink(missing_ok=True)
        
        # Increment ID for next label
        current_id += n_per_label

    # Save Master Metadata
    master_csv = output_dir / "metadata.csv"
    if all_rows:
        pd.DataFrame(all_rows).to_csv(master_csv, index=False)
        print(f"\nDone. Total samples generated: {len(all_rows)}")
        print(f"Master metadata saved to: {master_csv}")
    else:
        print("\nNo samples generated.")

def modify_antenna_position(content, offset):
    """
    Parses .in content, finds 'hertzian_dipole' and 'rx', shifts X coordinate.
    Adds comment about offset.
    """
    lines = content.splitlines()
    new_lines = []
    
    comment_injected = False
    
    for line in lines:
        # Inject comment after header lines or near top
        if line.startswith("##") and not comment_injected:
            # Inject it early but ensure it doesn't break header block if possible
            # Just append typically works
            pass 
        
        if line.startswith("#hertzian_dipole:"):
            if not comment_injected:
                 new_lines.append(f"## Antenna Offset: {offset:+.2f} m")
                 comment_injected = True
                 
            parts = line.split()
            try:
                # #hertzian_dipole: z x y z src
                x = float(parts[2])
                new_x = x + offset
                parts[2] = f"{new_x:.4f}"
                new_lines.append(" ".join(parts))
            except ValueError:
                new_lines.append(line)
        
        elif line.startswith("#rx:"):
            parts = line.split()
            try:
                # #rx: x y z
                x = float(parts[1])
                new_x = x + offset
                parts[1] = f"{new_x:.4f}"
                new_lines.append(" ".join(parts))
            except ValueError:
                new_lines.append(line)
                
        else:
            new_lines.append(line)
            
    return "\n".join(new_lines) + "\n"

import configparser

def load_config(config_path):
    """
    Load configuration from INI file.
    """
    config = configparser.ConfigParser()
    config_path = Path(config_path)
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")
    
    config.read(config_path)
    
    if 'DatasetGeneration' not in config:
        raise ValueError(f"Section [DatasetGeneration] not found in {config_path}")
        
    cfg = config['DatasetGeneration']
    
    params = {
        'output_dir': cfg.get('output_dir', r'd:\Codigo\Synth-Data\Output'),
        'labels': cfg.get('generate_labels', 'CL MC MF F HF').split(),
        'n_per_label': cfg.getint('n_samples', 10),
        'start_id': cfg.getint('start_id', 20000),
        'augment': cfg.getboolean('augment', False)
    }
    return params

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Unified Synthetic GPR Data Generator (Config Driven)")
    
    parser.add_argument(
        "--config", 
        default=r"d:\Codigo\Synth-GPR\400MHz_full.ini", 
        help="Path to INI configuration file"
    )
    
    args = parser.parse_args()
    
    try:
        params = load_config(args.config)
        
        generate_dataset(
            output_dir=params['output_dir'], 
            labels=params['labels'], 
            n_per_label=params['n_per_label'], 
            start_id=params['start_id'], 
            augment=params['augment']
        )
    except Exception as e:
        print(f"Error loading configuration: {e}")
        sys.exit(1)

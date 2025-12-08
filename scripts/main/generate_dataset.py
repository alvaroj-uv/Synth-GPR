#!/usr/bin/env python3
"""
Unified script to generate synthetic GPR data for specific fouling classes.
Replaces generate_clean_dataset.py and generate_stratified_dataset.py.

Usage:
    python scripts/main/generate_dataset.py <output_dir> --labels <labels> [options]

Arguments:
    output_dir (str): Directory to save generated .in files.
    --labels (list): Fouling classes to generate (CL, MC, MF, F, HF).
    -n, --num (int): Samples per label.
    --start_id (int): Starting ID for filename numbering (e.g. s_0100).
    --moisture_max (float): Maximum moisture content (0.0 to 0.3).

Example:
    python scripts/main/generate_dataset.py d:/data/batch1 --labels CL MC -n 50 --start_id 100

Verification:
    1. Check if <output_dir> contains .in files (e.g., s_0100.in).
    2. Check if metadata_CL.csv (or other labels) exists in <output_dir>.
    3. Use visualization tool to verify geometry:
       python scripts/tools/visualization/visualize_gprmax_blueprint.py <output_dir>/s_0100.in
"""

import sys
import argparse
from pathlib import Path
import time

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.config import GeneratorConfig
from src.dataset_generator import DatasetGenerator

# Define PVC ranges for each class
PVC_RANGES = {
    'CL': (0.0, 5.0),    # Clean
    'MC': (5.0, 20.0),   # Moderately Clean
    'MF': (20.0, 40.0),  # Moderately Fouled
    'F':  (40.0, 60.0),  # Fouled
    'HF': (60.0, 100.0)  # Highly Fouled
}

def generate_dataset(output_dir, labels, n_per_label=50, start_id=10000, moisture_max=0.15, base_config=None):
    """
    Generates n samples for each requested label.
    
    Args:
        output_dir: Directory to save output files
        labels: List of fouling class labels (CL, MC, MF, F, HF)
        n_per_label: Number of samples per label
        start_id: Starting ID for filenames
        moisture_max: Maximum moisture content
        base_config: Optional GeneratorConfig with base settings (freq, geometry, etc.)
    """
    print(f"{'='*60}")
    print(f"Synthetic Dataset Generator")
    print(f"{'='*60}")
    print(f"Output Directory: {output_dir}")
    print(f"Labels:           {labels}")
    print(f"Samples/Label:    {n_per_label}")
    print(f"Start ID:         {start_id}")
    print(f"Moisture Max:     {moisture_max}")
    if base_config:
        print(f"Center Freq:      {base_config.center_freq/1e6:.0f} MHz")
    print(f"{'='*60}\n")
    
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    current_id = start_id
    total_generated = 0
    start_time = time.time()
    
    for label in labels:
        label_upper = label.upper()
        if label_upper not in PVC_RANGES:
            print(f"[WARN] Unknown label '{label}', skipping. Available: {list(PVC_RANGES.keys())}")
            continue
            
        pmin, pmax = PVC_RANGES[label_upper]
        print(f"-> Generating {label_upper} (PVC {pmin}-{pmax}%) ...")
        
        # If base_config provided, create a copy and override PVC/moisture
        if base_config:
            from dataclasses import replace
            cfg = replace(base_config, 
                pvc_min=pmin,
                pvc_max=pmax,
                moisture_max=moisture_max,
                base_seed=current_id
            )
        else:
            # Fallback to default config
            cfg = GeneratorConfig(
                base_seed=current_id,
                add_waveform=True,
                add_source=True,
                granular_mode=True,
                pvc_min=pmin,
                pvc_max=pmax,
                moisture_min=0.0, 
                moisture_max=moisture_max,
                min_ballast_thickness=0.25,
                max_ballast_thickness=0.45,
                rock_radius_max=0.032,
            )
        
        gen = DatasetGenerator(cfg)
        
        # Generate batch
        # We append the label to the metadata filename to avoid overwrites if running multiple batches
        metadata_name = f"metadata_{label_upper}.csv"
        
        files = gen.generate_samples(
            output_dir=output_dir,
            n_samples=n_per_label,
            start_id=current_id
        )
        
        count = n_per_label
        print(f"   Generated {count} samples. IDs: {current_id} - {current_id + count - 1}")
        
        current_id += count
        total_generated += count
        
    elapsed = time.time() - start_time
    print(f"\n{'='*60}")
    print(f"Completed in {elapsed:.2f}s")
    print(f"Total Samples Generated: {total_generated}")
    print(f"{'='*60}")
    
    return total_generated

if __name__ == "__main__":
    import sys
    from pathlib import Path
    
    # Add src to path for imports
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))
    from src.config import GeneratorConfig
    
    # Determine script name for default INI file
    script_name = Path(__file__).stem  # 'generate_dataset'
    default_ini = f"{script_name}.ini"
    
    # Check if default INI file exists
    use_ini = False
    config_file = None
    
    # Priority 1: Explicit INI file argument
    if len(sys.argv) >= 2 and sys.argv[1].endswith('.ini'):
        config_file = sys.argv[1]
        use_ini = True
    # Priority 2: Default INI file in current directory
    elif Path(default_ini).exists():
        config_file = default_ini
        use_ini = True
        print(f"Found default config: {default_ini}")
    
    # Use INI configuration if available
    if use_ini:
        try:
            config = GeneratorConfig.from_ini(config_file)
            
            print(f"Loaded configuration from: {config_file}")
            print(f"Output directory: {config.output_dir}")
            print(f"Labels: {config.labels}")
            print(f"Samples per label: {config.samples_per_label}")
            print(f"Start ID: {config.start_id}")
            print()
            
            # Generate dataset using config parameters
            generate_dataset(
                output_dir=config.output_dir,
                labels=config.labels,
                n_per_label=config.samples_per_label,
                start_id=config.start_id,
                moisture_max=config.moisture_max,
                base_config=config  # Pass full config for freq, geometry, etc.
            )
        except FileNotFoundError:
            print(f"Error: Config file not found: {config_file}")
            sys.exit(1)
        except Exception as e:
            print(f"Error loading config: {e}")
            sys.exit(1)
    
    # Fall back to command-line arguments
    else:
        print(f"No INI file found. Using command-line arguments.")
        print(f"(Tip: Create '{default_ini}' for easier configuration)")
        print()
        
        parser = argparse.ArgumentParser(
            description="Generate synthetic GPR dataset for specific fouling classes.",
            epilog=f"Alternatively, create a '{default_ini}' file with [workflow] section."
        )
        
        parser.add_argument("output_dir", help="Directory to save output files")
        
        parser.add_argument("--labels", nargs="+", default=['CL', 'MC', 'MF', 'F'], 
                            help=f"Labels to generate. Choices: {list(PVC_RANGES.keys())} (default: CL MC MF F)")
        
        parser.add_argument("-n", "--num", type=int, default=10, 
                            help="Number of samples per label (default: 10)")
        
        parser.add_argument("--start_id", type=int, default=1000, 
                            help="Starting ID for filenames (default: 1000)")
        
        parser.add_argument("--moisture_max", type=float, default=0.15, 
                            help="Maximum volumetric moisture content (default: 0.15)")

        args = parser.parse_args()
        
        generate_dataset(args.output_dir, args.labels, args.num, args.start_id, args.moisture_max)



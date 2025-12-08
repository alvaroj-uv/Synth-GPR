import pandas as pd
import argparse
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.synthetic_data_generator import GeneratorConfig, BallastScenarioGenerator

def generate_augmented_dataset(output_dir, labels, n_per_label=50, start_id=20000, offsets=[-0.10, 0.10]):
    """
    Generates samples and creates spatially augmented copies (Left/Right shifts).
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 1. Generate Base Dataset (Center)
    # We reuse the logic from generate_stratified_dataset.py roughly
    print("Generating base samples (Center)...")
    
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
            print(f"Skipping unknown label: {label}")
            continue
            
        pmin, pmax = pvc_ranges[label]
        print(f"  Generating {label} (PVC {pmin}-{pmax}%) base files...")
        
        cfg = GeneratorConfig(
            base_seed=current_id,
            # Widen domain to 0.8m to prevent antenna entering PML (0.05m) during augmentation
            domain_x=0.8,
            tx_x=0.375,
            rx_x=0.425,
            add_waveform=True,
            add_source=True,
            # add_geometry_view=True, # Disabled by default
            granular_mode=True,
            pvc_min=pmin,
            pvc_max=pmax,
            moisture_min=0.0, 
            moisture_max=0.15,
        )
        
        gen = BallastScenarioGenerator(cfg)
        
        # Helper DF
        df = gen.generate_dataset(
            out_dir=output_dir,
            n_samples=n_per_label,
            csv_name=f"temp_metadata_{label}.csv",
            start_id=current_id
        )
        
        # 2. Augment each file
        print(f"  Augmenting {label} files with offsets {offsets}...")
        
        for _, row in df.iterrows():
            base_filename = row['filename']
            base_path = output_dir / base_filename
            
            # Read base content
            content = base_path.read_text(encoding='utf-8')
            
            # Add base row to master list (offset 0)
            row_dict = row.to_dict()
            row_dict['antenna_offset_x'] = 0.0
            all_rows.append(row_dict)
            
            for off in offsets:
                # Determine suffix
                suffix = "left" if off < 0 else "right"
                new_filename = base_filename.replace(".in", f"_{suffix}.in")
                new_path = output_dir / new_filename
                
                # Create augmented content
                new_content = modify_antenna_position(content, off)
                
                # Write file
                new_path.write_text(new_content, encoding='utf-8')
                
                # Add metadata row
                new_row = row_dict.copy()
                new_row['filename'] = new_filename
                new_row['antenna_offset_x'] = off
                all_rows.append(new_row)
        
        # Cleanup temp csv
        (output_dir / f"temp_metadata_{label}.csv").unlink(missing_ok=True)
        
        current_id += n_per_label

    # Save Master Metadata
    master_csv = output_dir / "metadata.csv"
    pd.DataFrame(all_rows).to_csv(master_csv, index=False)
    print(f"Done. Total samples generated: {len(all_rows)}")

def modify_antenna_position(content, offset):
    """
    Parses .in content, finds 'hertzian_dipole' and 'rx', shifts X coordinate.
    Adds comment about offset.
    """
    lines = content.splitlines()
    new_lines = []
    
    # Inject comment near top
    comment_injected = False
    
    for line in lines:
        if line.startswith("##") and not comment_injected:
            new_lines.append(f"## Antenna Offset: {offset:+.2f} m")
            comment_injected = True
        
        if line.startswith("#hertzian_dipole:"):
            # Format: #hertzian_dipole: z x y z src
            parts = line.split()
            # parts[0]=cmd, parts[1]=pol, parts[2]=x, parts[3]=y, parts[4]=z, parts[5]=src
            try:
                x = float(parts[2])
                new_x = x + offset
                parts[2] = f"{new_x:.4f}"
                new_lines.append(" ".join(parts))
            except ValueError:
                new_lines.append(line)
        
        elif line.startswith("#rx:"):
            # Format: #rx: x y z
            parts = line.split()
            try:
                x = float(parts[1])
                new_x = x + offset
                parts[1] = f"{new_x:.4f}"
                new_lines.append(" ".join(parts))
            except ValueError:
                new_lines.append(line)
                
        else:
            new_lines.append(line)
            
    return "\n".join(new_lines) + "\n"

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate spatially augmented synthetic samples.")
    parser.add_argument("output_dir", help="Directory to save output files")
    parser.add_argument("--labels", nargs="+", default=['CL', 'MC', 'MF', 'F'], help="Labels to generate")
    parser.add_argument("-n", "--num", type=int, default=10, help="Base samples per label (Total = 3 * n)")
    parser.add_argument("--start_id", type=int, default=20000, help="Starting ID")
    
    args = parser.parse_args()
    
    generate_augmented_dataset(args.output_dir, args.labels, args.num, args.start_id)

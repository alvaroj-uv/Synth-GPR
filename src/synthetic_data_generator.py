
import argparse
import random
import configparser
import sys
from datetime import date
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import List, Dict, Any, Tuple

import numpy as np
import pandas as pd
import h5py

from .geometry_composer import ScenePainter, BackgroundLayer, SubgradeLayer, FormationLayer, GranularBallastLayer, AntennaLayer, SleeperLayer, fmt
from .config import GeneratorConfig, get_fi_class, get_fi_class_legacy, get_pvc_class, compute_fi, classify_fi, topp_mixing_model
from .file_writer import GPRMaxFileWriter
from .scenario_factory import ScenarioFactory
from .scene_validator import SceneValidator
import dataclasses

class BallastScenarioGenerator:
    # Main orchestrator for generating synthetic GPR ballast scenarios.
    # 
    # Responsible for:
    # 1. Sampling random parameters (Geometry, Moisture, PVC) based on configuration.
    # 2. Composing the gprMax input file using ScenePainter.
    # 3. Generating metadata for Machine Learning.
    # 
    # Attributes:
    #     cfg (GeneratorConfig): Configuration object containing ranges and settings.
    def __init__(self, config: GeneratorConfig):
        self.cfg = config
        if self.cfg.base_seed is not None:
            random.seed(self.cfg.base_seed)
            np.random.seed(self.cfg.base_seed)

    # --------------- main public API -----------------

    def generate_dataset(
        self,
        out_dir: str | Path,
        n_samples: int = 50,
        csv_name: str = "metadata.csv",
        start_id: int = 0,
    ) -> pd.DataFrame:
        # Generate n_samples .in files under out_dir and a CSV with metadata.
        out_dir = Path(out_dir)
        out_dir.mkdir(parents=True, exist_ok=True)

        metadata_rows: List[Dict[str, Any]] = []

        for i in range(n_samples):
            sample_id = start_id + i
            
            # 1. Sample scenario parameters
            context = self._sample_scenario_parameters()
            
            base_name = f"s_{sample_id:04d}"
            in_filename = f"{base_name}.in"

            # 2. Generate base file (deterministic)
            cfg_base = dataclasses.replace(self.cfg, enable_domain_randomization=False)
            in_text, scenario_info = self._compose_scenario(cfg_base, base_name, context["scenario_type"], context)
            (out_dir / in_filename).write_text(in_text + "\n", encoding="utf-8")

            # 3. Collect base metadata
            metadata_rows.append(self._create_metadata_row(
                sample_id, in_filename, context, scenario_info, is_randomized=False
            ))
            
            # 4. Generate antenna-shifted variants (same geometry, different observation point)
            if self.cfg.generate_antenna_variants:
                antenna_shift = self.cfg.antenna_shift_amount
                
                for suffix, shift in [("_L", -antenna_shift), ("_R", +antenna_shift)]:
                    variant_filename = f"s_{sample_id:05d}{suffix}.in"
                    
                    # Create variant by modifying the BASE text (not regenerating)
                    # Replace antenna positions in the already-generated file
                    new_tx_x = self.cfg.tx_x + shift
                    new_rx_x = self.cfg.rx_x + shift
                    
                    shifted_text = self._shift_antenna_in_text(
                        in_text, 
                        self.cfg.tx_x, self.cfg.rx_x,
                        new_tx_x, new_rx_x
                    )
                    
                    reference_comment = f"## Antenna-shifted variant ({suffix}) of base file: {in_filename}\n"
                    (out_dir / variant_filename).write_text(reference_comment + shifted_text + "\n", encoding="utf-8")
                    
                    # Copy metadata from base, update antenna info
                    variant_info = dict(scenario_info)
                    variant_info['tx_x'] = new_tx_x
                    variant_info['rx_x'] = new_rx_x
                    
                    metadata_rows.append(self._create_metadata_row(
                        sample_id, variant_filename, context, variant_info, 
                        is_randomized=False, base_file=in_filename
                    ))

        return self._save_metadata(metadata_rows, out_dir, csv_name)

    def _sample_scenario_parameters(self) -> Dict[str, Any]:
        # Sample all scenario parameters (geometry, moisture, PVC, FI classification).
        pvc = 0.0
        moisture = 0.0

        if self.cfg.granular_mode:
            scenario_type = "granular"
            pvc = random.uniform(self.cfg.pvc_min, self.cfg.pvc_max)
            moisture = random.uniform(self.cfg.moisture_min, self.cfg.moisture_max)
            
            rock_part, foul_part = self._sample_heights()
            rock_thickness = rock_part + foul_part
            fouling_thickness = 0.0
            
            FI = pvc
            FI_class = get_pvc_class(pvc)
            FI_class_legacy = get_fi_class_legacy(pvc)
        else:
            scenario_type = random.choice(["uniform", "vertical_gradient", "pockets", "wet"])
            rock_thickness, fouling_thickness = self._sample_heights()
            
            FI = compute_fi(rock_thickness, fouling_thickness)
            FI_class = classify_fi(FI)
            FI_class_legacy = classify_fi(FI)

        return {
            "scenario_type": scenario_type,
            "rock_thickness": rock_thickness,
            "fouling_thickness": fouling_thickness,
            "FI": FI,
            "FI_class": FI_class,
            "FI_class_legacy": FI_class_legacy,
            "pvc": pvc,
            "moisture": moisture
        }

    def _create_metadata_row(
        self,
        sample_id: int,
        filename: str,
        context: Dict[str, Any],
        scenario_info: Dict[str, Any],
        is_randomized: bool,
        base_file: str = None
    ) -> Dict[str, Any]:
        # Create a metadata dictionary for a single sample.
        row = {
            "sample_id": sample_id,
            "filename": filename,
            "scenario_type": context["scenario_type"],
            "rock_thickness_m": context["rock_thickness"],
            "fouling_thickness_m": context["fouling_thickness"],
            "FI_percent": context["FI"],
            "FI_class": context["FI_class"],
            "FI_class_legacy": context["FI_class_legacy"],
            "is_randomized": is_randomized,
            "base_file": base_file or filename,
        }
        row.update(scenario_info)
        return row

    def _save_metadata(self, metadata_rows: List[Dict], out_dir: Path, csv_name: str) -> pd.DataFrame:
        # Format and save metadata to CSV.
        df = pd.DataFrame(metadata_rows)
        
        priority_cols = ['sample_id', 'FI_class', 'filename', 'is_randomized', 'base_file']
        other_cols = [c for c in df.columns if c not in priority_cols]
        df = df[priority_cols + other_cols]
        
        float_cols = df.select_dtypes(include=['float64', 'float32']).columns
        for col in float_cols:
            df[col] = df[col].apply(lambda x: float(f'{x:.5g}') if pd.notna(x) else x)
        
        csv_path = out_dir / csv_name
        df.to_csv(csv_path, index=False, float_format='%.5g')
        return df

    # --------------- antenna shifting -----------------

    def _shift_antenna_in_text(
        self, 
        base_text: str, 
        old_tx_x: float, old_rx_x: float,
        new_tx_x: float, new_rx_x: float
    ) -> str:
        """
        Modify antenna positions in an already-generated .in file text.
        Uses line-by-line parsing for reliability.
        
        Formats:
        - #hertzian_dipole: polarization X Y Z waveform_id  
        - #rx: X Y Z
        """
        lines = base_text.split('\n')
        result_lines = []
        
        for line in lines:
            stripped = line.strip()
            
            # Handle hertzian_dipole line
            if stripped.startswith('#hertzian_dipole:'):
                # Parse: #hertzian_dipole: polarization X Y Z waveform_id
                parts = stripped.split()
                # parts = ['#hertzian_dipole:', 'z', 'X', 'Y', 'Z', 'waveform_id']
                if len(parts) >= 6:
                    parts[2] = f"{new_tx_x:.5g}"  # Replace X position
                    result_lines.append(' '.join(parts))
                    continue
            
            # Handle rx line
            elif stripped.startswith('#rx:'):
                # Parse: #rx: X Y Z
                parts = stripped.split()
                # parts = ['#rx:', 'X', 'Y', 'Z']
                if len(parts) >= 4:
                    parts[1] = f"{new_rx_x:.5g}"  # Replace X position
                    result_lines.append(' '.join(parts))
                    continue
            
            # Keep other lines unchanged
            result_lines.append(line)
        
        return '\n'.join(result_lines)

    # --------------- geometry sampling -----------------

    def _sample_heights(self) -> tuple[float, float]:
        # Sample rock and foul heights in a physically realistic way based on configuration ranges.
        # 
        # Returns:
        #     tuple[float, float]: (rock_thickness, foul_thickness)
        cfg = self.cfg
        total_ballast = random.uniform(
            cfg.min_ballast_thickness, cfg.max_ballast_thickness
        )
        foul = random.uniform(cfg.min_foul_thickness, cfg.max_foul_thickness)
        foul = min(foul, total_ballast)  # just in case
        rock = total_ballast - foul
        return rock, foul

    # --------------- file composition -----------------


    def _compose_scenario(
        self,
        config: GeneratorConfig,
        base_name: str,
        scenario_type: str,
        context: Dict[str, Any]
    ) -> tuple[str, Dict[str, Any]]:
        """
        Orchestrates the creation of the scenario using Factory and Writer.
        """
        # 1. Use Factory to create Painter
        # Pass context for layer configuration (e.g., PVC, moisture)
        painter = ScenarioFactory.create_painter(config, scenario_type, context)
            
        # 2. Execute Painting (Generate SceneDefinition)
        scene = painter.paint(base_name)
        
        # Validate Scene
        errors = SceneValidator.validate(scene)
        if errors:
             print(f"[{base_name}] Validation Errors:")
             for e in errors:
                 print(f"  ! {e}")
        
        # 3. Augment Metadata
        # Add context info (FI class, etc) to scene metadata for reporting, but PREFER realized values
        # (e.g. calculated fouling_thickness) over input context samples.
        for k, v in context.items():
            if k not in scene.metadata:
                scene.metadata[k] = v
        
        # 4. Use Writer to generate string
        # Extra headers for the top of the file
        extra_headers = {
             "FI (%)": context.get("FI", 0),
             "FI class": context.get("FI_class", "NA"),
             "FI Class Leg": context.get("FI_class_legacy", "NA")
        }
        
        final_text = GPRMaxFileWriter.write_scene(
            scene=scene,
            scenario_type=scenario_type,
            extra_headers=extra_headers
        )

        return final_text, scene.metadata

    # --------------- scenario implementations (Legacy/Superseded) -----------------
    # The following methods have been refactored into geometry_composer.py Layers.
    # We keep the structure clean by removing them.


# ------------------------------------------------------------
# Example usage
# ------------------------------------------------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate synthetic GPR ballast scenarios with configurable parameters."
    )
    
    # Simulation parameters

    parser.add_argument("--freq", type=float, default=1.5e9, help="Center frequency in Hz (default: 1.5e9)")
    parser.add_argument("--n_samples", type=int, default=50, help="Number of samples to generate")
    parser.add_argument("--out_dir", type=str, default="d:/Codigo/Synth-Data", help="Output directory")
    
    # Antenna positions
    
    # Antenna positions
    parser.add_argument("--tx_x", type=float, default=0.300, help="Transmitter X position")
    parser.add_argument("--rx_x", type=float, default=0.350, help="Receiver X position")
    parser.add_argument("--tx_rx_y", type=float, default=0.904, help="Transmitter/Receiver Y position")
    
    # Domain size (optional override)
    parser.add_argument("--domain_x", type=float, default=None, help="Domain X size (optional)")
    parser.add_argument("--domain_y", type=float, default=None, help="Domain Y size (optional)")
    parser.add_argument("--start_id", type=int, default=0, help="Starting ID for samples (default: 0)")

    # High-Fidelity / Granular options
    parser.add_argument("--granular", action="store_true", help="Enable High-Fidelity Granular Mode")
    parser.add_argument("--add_sleepers", action="store_true", help="Add concrete sleepers (ties) to the geometry")
    parser.add_argument("--pvc_min", type=float, default=0.0, help="Min PVC (0-100) for granular mode")
    parser.add_argument("--pvc_max", type=float, default=100.0, help="Max PVC (0-100) for granular mode")
    parser.add_argument("--moisture_min", type=float, default=0.0, help="Min moisture (0.0-1.0)")
    parser.add_argument("--moisture_max", type=float, default=0.3, help="Max moisture (0.0-1.0)")


    parser.add_argument("--config", type=str, help="Path to .ini configuration file")

    args = parser.parse_args()

    # Create config
    if args.config:
        print(f"Loading configuration from {args.config}...")
        cfg = GeneratorConfig.from_ini(args.config)
        
        # Apply runtime overrides that might not be in config or should be dynamic
        if args.start_id != 0 or cfg.base_seed is None:
             cfg.base_seed = 42 + args.start_id
             
        # Optional: Allow CLI overrides if needed (e.g. force granular mode via CLI even if config says False)
        if args.granular:
            print("CLI Override: Forcing Granular Mode")
            cfg.granular_mode = True
            
        # Ensure domain overrides work
        if args.domain_x is not None:
             cfg.domain_x = args.domain_x
        if args.domain_y is not None:
             cfg.domain_y = args.domain_y

    else:
        # Legacy CLI-driven config
        cfg = GeneratorConfig(
            base_seed=42 + args.start_id, # varies seed with start_id to avoid repeats if running multiple batches
            add_waveform=True,
            add_source=True,
            add_geometry_view=False,
            center_freq=args.freq,
            tx_x=args.tx_x,
            rx_x=args.rx_x,
            tx_rx_y=args.tx_rx_y,
            # Granular config
            granular_mode=args.granular,
            add_sleepers=args.add_sleepers,
            pvc_min=args.pvc_min,
            pvc_max=args.pvc_max,
            moisture_min=args.moisture_min,
            moisture_max=args.moisture_max
        )

        # Optional overrides
        if args.domain_x is not None:
            cfg.domain_x = args.domain_x
        if args.domain_y is not None:
            cfg.domain_y = args.domain_y
            
        # Check for output folder in config if not overridden by CLI default
        # CLI default is "d:/Codigo/Synth-Data". If user didn't change it, check config.
        # But args.out_dir always has a value.
        # Simple logic: If config has output_folder, update args.out_dir if it matches the default
        # or just print a warning if they differ? 
        # Better: let's look at the config object. We need to parse it ourselves here since GeneratorConfig doesn't store out_dir.
        
        # Re-read basics for out_dir
        if args.config:
            cp = configparser.ConfigParser()
            cp.read(args.config)
            if cp.has_option('Simulation', 'output_folder'):
                 ini_out = cp.get('Simulation', 'output_folder')
                 # If CLI argument is strictly default, overwrite with INI
                 # (This is slightly heuristic, but effective)
                 if args.out_dir == "d:/Codigo/Synth-Data":
                      args.out_dir = ini_out

    gen = BallastScenarioGenerator(cfg)

    print(f"Generating {args.n_samples} samples starting at ID {args.start_id}...")
    if cfg.granular_mode:
        print("  Mode: High-Fidelity Granular")
    print(f"  Frequency: {cfg.center_freq/1e6:.1f} MHz")
    print(f"  Output Dir: {args.out_dir}")
    
    out_df = gen.generate_dataset(
        out_dir=args.out_dir,
        n_samples=args.n_samples,
        csv_name="metadata.csv",
        start_id=args.start_id,
    )
    print(f"Done. Metadata saved to {Path(args.out_dir) / 'metadata.csv'}")
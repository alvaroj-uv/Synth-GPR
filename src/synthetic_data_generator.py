
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

from .geometry_composer import ScenePainter, BackgroundLayer, SubgradeLayer, FormationLayer, GranularBallastLayer, MasterPatternLayer, AntennaLayer, SleeperLayer, fmt
from .config import GeneratorConfig, get_fi_class, get_fi_class_legacy, get_pvc_class, compute_fi, classify_fi, topp_mixing_model

class BallastScenarioGenerator:
    """
    Main orchestrator for generating synthetic GPR ballast scenarios.
    
    Responsible for:
    1. Sampling random parameters (Geometry, Moisture, PVC) based on configuration.
    2. Composing the gprMax input file using ScenePainter.
    3. Generating metadata for Machine Learning.
    
    Attributes:
        cfg (GeneratorConfig): Configuration object containing ranges and settings.
    """
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
        """
        Generate n_samples .in files under out_dir and a CSV with metadata.
        """
        out_dir = Path(out_dir)
        out_dir.mkdir(parents=True, exist_ok=True)

        metadata_rows: List[Dict[str, Any]] = []

        for i in range(n_samples):
            idx = start_id + i
            
            pvc = 0.0
            moisture = 0.0

            if self.cfg.granular_mode:
                scenario_type = "granular"
                # Sample granular params
                pvc = random.uniform(self.cfg.pvc_min, self.cfg.pvc_max)
                moisture = random.uniform(self.cfg.moisture_min, self.cfg.moisture_max)
                
                # In granular mode, we don't pick 'uniform/vertical' etc.
                # And 'foul_h' from _sample_heights represents the legacy layer thickness.
                # We need total ballast thickness.
                rock_part, foul_part = self._sample_heights()
                rock_h = rock_part + foul_part # Total thickness
                foul_h = 0.0 # Not used in legacy sense
                
                # Recompute FI equivalent for metadata? 
                # FI is historically weight-based. PVC is volume-based. 
                # Let's just track them separately.
                # User Request: "FI of 21.77% labeled MF". Assume FI field should hold PVC to align with legacy analysis.
                FI = pvc 
                FI_class = get_pvc_class(pvc)
                FI_class_legacy = get_fi_class_legacy(pvc)
                
            else:
                # Decide scenario (Legacy)
                scenario_type = random.choice(
                    ["uniform", "vertical_gradient", "pockets", "wet"]
                )

                # Sample geometry (ballast and fouling thicknesses)
                rock_h, foul_h = self._sample_heights()

                # Compute FI and class
                FI = compute_fi(rock_h, foul_h)
                FI_class = classify_fi(FI)
                FI_class_legacy = classify_fi(FI) # Legacy scenarios map directly 


            # File naming
            base_name = f"s_{idx:04d}"
            in_filename = f"{base_name}.in"

            # Build content
            in_text, scenario_info = self._compose_file(
                base_name=base_name,
                scenario_type=scenario_type,
                rock_h=rock_h,
                foul_h=foul_h,
                FI=FI,
                FI_class=FI_class,
                FI_class_legacy=FI_class_legacy,
                pvc=pvc,
                moisture=moisture,
            )

            # Write base file
            (out_dir / in_filename).write_text(in_text + "\n", encoding="utf-8")

            # Collect metadata for base file
            row = {
                "sample_id": idx,
                "filename": in_filename,
                "scenario_type": scenario_type,
                "rock_height_m": rock_h,
                "foul_height_m": foul_h,
                "FI_percent": FI,
                "FI_class": FI_class,
                "FI_class_legacy": FI_class_legacy,
                "is_randomized": False,
                "base_file": in_filename,
            }
            row.update(scenario_info)
            metadata_rows.append(row)
            
            # Create 3 randomized variants
            for r_idx in range(1, 4):
                rand_filename = f"s_{idx:05d}_r{r_idx}.in"
                
                # Generate randomized variant (re-compose with domain randomization)
                cfg_rand = self.cfg
                # Temporarily enable randomization
                original_rand_state = cfg_rand.enable_domain_randomization
                cfg_rand.enable_domain_randomization = True
                
                rand_text, rand_info = self._compose_file(
                    base_name=base_name,
                    scenario_type=scenario_type,
                    rock_h=rock_h,
                    foul_h=foul_h,
                    FI=FI,
                    FI_class=FI_class,
                    FI_class_legacy=FI_class_legacy,
                    pvc=pvc,
                    moisture=moisture,
                )
                
                # Restore original state
                cfg_rand.enable_domain_randomization = original_rand_state
                
                # Add reference comment at top (using gprMax-compatible ## syntax)
                reference_comment = f"## Randomized variant {r_idx} of base file: {in_filename}\n"
                rand_text_with_ref = reference_comment + rand_text
                
                # Write randomized file
                (out_dir / rand_filename).write_text(rand_text_with_ref + "\n", encoding="utf-8")
                
                # Collect metadata for randomized variant
                rand_row = {
                    "sample_id": idx,
                    "filename": rand_filename,
                    "scenario_type": scenario_type,
                    "rock_height_m": rock_h,
                    "foul_height_m": foul_h,
                    "FI_percent": FI,
                    "FI_class": FI_class,
                    "FI_class_legacy": FI_class_legacy,
                    "is_randomized": True,
                    "base_file": in_filename,
                }
                rand_row.update(rand_info)
                metadata_rows.append(rand_row)

        df = pd.DataFrame(metadata_rows)
        
        # Reorder columns: sample_id, FI_class (label) first, then rest
        priority_cols = ['sample_id', 'FI_class', 'filename', 'is_randomized', 'base_file']
        other_cols = [c for c in df.columns if c not in priority_cols]
        df = df[priority_cols + other_cols]
        
        # Round float columns to 5 significant figures
        float_cols = df.select_dtypes(include=['float64', 'float32']).columns
        for col in float_cols:
            df[col] = df[col].apply(lambda x: float(f'{x:.5g}') if pd.notna(x) else x)
        
        # Always overwrite the metadata CSV to prevent duplicates
        csv_path = out_dir / csv_name
        df.to_csv(csv_path, index=False, float_format='%.5g')
        return df

    # --------------- geometry sampling -----------------

    def _sample_heights(self) -> tuple[float, float]:
        """
        Sample rock and foul heights in a physically realistic way based on configuration ranges.
        
        Returns:
            tuple[float, float]: (rock_thickness, foul_thickness)
        """
        cfg = self.cfg
        total_ballast = random.uniform(
            cfg.min_ballast_thickness, cfg.max_ballast_thickness
        )
        foul = random.uniform(cfg.min_foul_thickness, cfg.max_foul_thickness)
        foul = min(foul, total_ballast)  # just in case
        rock = total_ballast - foul
        return rock, foul

    # --------------- file composition -----------------

    def _compose_file(
        self,
        base_name: str,
        scenario_type: str,
        rock_h: float,
        foul_h: float,
        FI: float,
        FI_class: str,
        FI_class_legacy: str = "NA",
        pvc: float = 0.0,
        moisture: float = 0.0,
    ) -> tuple[str, Dict[str, Any]]:
        """
        Create the text of the .in file and return (text, scenario_metadata).
        """
        cfg = self.cfg

        # Base fouled material properties (Legacy support)
        base_foul_eps = random.uniform(cfg.bal_foul_eps_min, cfg.bal_foul_eps_max)
        base_foul_sigma = random.uniform(
            cfg.bal_foul_sigma_min, cfg.bal_foul_sigma_max
        )

        scenario_info: Dict[str, Any] = {
            "bal_rock_eps": cfg.bal_rock_eps,
            "bal_rock_sigma": cfg.bal_rock_sigma,
            "bal_foul_eps_base": base_foul_eps,
            "bal_foul_sigma_base": base_foul_sigma,
        }

        # --- NEW OOP SCENE PAINTER ---
        painter = ScenePainter(cfg)
        
        # 1. Background
        painter.add_layer(BackgroundLayer())
        
        # 2. Subgrade
        painter.add_layer(SubgradeLayer())
        
        # 3. Formation
        painter.add_layer(FormationLayer())
        
        # 4. Ballast
        if cfg.granular_mode:
            # Check for Master Pattern
            master_pattern_path = Path("src/patterns/ballast_master.json")
            if master_pattern_path.exists():
                painter.add_layer(MasterPatternLayer(str(master_pattern_path), pvc, moisture))
            else:
                # Fallback to legacy random placement
                # print("Warning: Master Pattern not found. using random placement.")
                painter.add_layer(GranularBallastLayer(None, pvc, moisture))
        else:
            # Fallback for legacy modes not fully implemented in OOP yet
            # For now, we only support Granular in this refactor pass as per plan
            # Or we can wrap legacy logic in a SimpleBallastLayer later.
            # Given the user context ("granular generation"), we prioritize Granular.
            # We implemented GranularBallastLayer in the composer.
            pass
            
        # 4.5 Sleepers (New Research Feature)
        if cfg.add_sleepers:
            painter.add_layer(SleeperLayer())

        # 5. Antenna
        if cfg.add_source:
            painter.add_layer(AntennaLayer())
            
        # Execute Painting
        setup_lines, geometry_lines, meta_painter = painter.paint(base_name)
        
        # Merge results (Update scenario info)
        scenario_info.update(meta_painter)

        # --- BUILD HEADER LAST ---
        header_lines: List[str] = []
        header_lines.append("## ------------------------------------------------------------")
        header_lines.append("## Generated gprMax Input File")
        header_lines.append(f"## Scenario: {scenario_type}")
        header_lines.append(f"## Date: {date.today().isoformat()}")
        header_lines.append(f"## Base Seed: {cfg.base_seed}")
        # header_lines.append(f"## Rock Height: {fmt(rock_h)}") # Now in scenario_info
        # header_lines.append(f"## Foul Height: {fmt(foul_h)}")
        header_lines.append(f"## FI (%): {fmt(FI)}")
        header_lines.append(f"## FI class: {FI_class}")
        header_lines.append(f"## FI Class Leg: {FI_class_legacy}")
        if cfg.granular_mode:
            header_lines.append(f"## Mode: Granular (High-Fidelity)")
            
        # Add dynamic details from painter metadata
        for k, v in scenario_info.items():
             header_lines.append(f"## {k}: {v}")

        return "\n".join(header_lines + setup_lines + geometry_lines), scenario_info
        for k, v in scenario_info.items():
            if k not in ["bal_rock_eps", "bal_rock_sigma", "bal_foul_eps_base", "bal_foul_sigma_base", "scenario_detail"]:
                # Format float values nicely if possible, otherwise str
                val_str = fmt(v) if isinstance(v, float) else str(v)
                header_lines.append(f"## {k}: {val_str}")
        
        # Add layer-specific air area metrics if available
        for layer_key in ["L1_air_percent", "L2_air_percent", "L3_air_percent"]:
            if layer_key in scenario_info:
                header_lines.append(f"## {layer_key}: {fmt(scenario_info[layer_key])}")

        header_lines.append("## ------------------------------------------------------------")

        # Assemble final text
        all_lines = header_lines + setup_lines + material_lines + geometry_lines
        text = "\n".join(all_lines)
        return text, scenario_info

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

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

from .geometry_composer import ScenePainter, BackgroundLayer, SubgradeLayer, FormationLayer, GranularBallastLayer, MasterPatternLayer, AntennaLayer, fmt
from .config import GeneratorConfig, get_fi_class, get_fi_class_legacy, get_pvc_class, compute_fi, classify_fi, topp_mixing_model

class BallastScenarioGenerator:
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

            # Write file
            (out_dir / in_filename).write_text(in_text + "\n", encoding="utf-8")

            # Collect metadata
            row = {
                "sample_id": idx,
                "filename": in_filename,
                "scenario_type": scenario_type,
                "rock_height_m": rock_h,
                "foul_height_m": foul_h,
                "FI_percent": FI,
                "FI_class": FI_class,
                "FI_class_legacy": FI_class_legacy,
            }
            row.update(scenario_info)  # add scenario-specific fields
            metadata_rows.append(row)

        df = pd.DataFrame(metadata_rows)
        # Append to existing CSV if it exists and we are adding more
        csv_path = out_dir / csv_name
        if start_id > 0 and csv_path.exists():
             df.to_csv(csv_path, mode='a', header=False, index=False)
        else:
             df.to_csv(csv_path, index=False)
        return df

    # --------------- geometry sampling -----------------

    def _sample_heights(self) -> tuple[float, float]:
        """
        Sample rock and foul heights in a physically realistic way.
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

    # --------------- scenario implementations -----------------

    def _add_rock_layer(
        self,
        materials: List[str],
        geometry: List[str],
        layer_idx: int,
        y_min: float,
        y_max: float,
        r_min: float,
        r_max: float,
        n_layers_total: int
    ) -> tuple[int, float, float]:
        """
        Generate a single layer of rocks with specific material properties.
        Returns: (rock_count, total_rock_area, air_percentage)
        """
        cfg = self.cfg
        
        # Material Variation Logic
        # Layer 0 (Bottom): Slightly higher eps/sigma (weathered/fines)
        # Layer N-1 (Top): Base eps/sigma (clean core)
        mat_suffix = f"L{layer_idx+1}"
        mat_name = f"bal_rock_{mat_suffix}"
        
        factor_idx = n_layers_total - 1 - layer_idx
        eps_l = cfg.bal_rock_eps * (1.0 + 0.03 * factor_idx)
        sig_l = cfg.bal_rock_sigma * (1.0 + 0.20 * factor_idx)
        
        # Define specific material for this layer
        materials.append(f"#material: {fmt(eps_l)} {fmt(sig_l)} 1 0 {mat_name}")
        
        geometry.append(f"## {mat_name} ({fmt(y_min)}-{fmt(y_max)}): r=[{fmt(r_min)}-{fmt(r_max)}]")
        
        fill_ratio = 0.60
        
        layer_cmds = self._generate_aggregates(
            0.0, cfg.domain_x,
            y_min, y_max,
            0.0, cfg.domain_z,
            radius_min=r_min,
            radius_max=r_max,
            target_fill_ratio=fill_ratio,
            material_name=mat_name
        )
        
        geometry.extend(layer_cmds)
        
        # Calculate air area
        # Parse radii from cylinder commands to calculate actual rock area
        total_rock_area = 0.0
        for cmd in layer_cmds:
            # Extract radius from command: "#cylinder: x y z x y z radius material"
            parts = cmd.split()
            if len(parts) >= 8:
                radius = float(parts[7])
                total_rock_area += np.pi * radius * radius
        
        # Layer box area (2D cross-section)
        layer_box_area = cfg.domain_x * (y_max - y_min)
        
        # Air area and percentage
        air_area = layer_box_area - total_rock_area
        air_percentage = (air_area / layer_box_area) * 100.0 if layer_box_area > 0 else 0.0
        
        return len(layer_cmds), total_rock_area, air_percentage

    def _generate_aggregates(
        self,
        x_min: float,
        x_max: float,
        y_min: float,
        y_max: float,
        z_min: float,
        z_max: float,
        radius_min: float | None = None,
        radius_max: float | None = None,
        target_fill_ratio: float = 0.60,
        material_name: str = "bal_rock"
    ) -> List[str]:
        """
        Generate explicit stone aggregates (cylinders in 2D) within the box.
        """
        cfg = self.cfg
        cmd_lines = []
        
        # Defaults to config if not provided
        r_min = radius_min if radius_min is not None else cfg.rock_radius_min
        r_max = radius_max if radius_max is not None else cfg.rock_radius_max
        
        # Simple random packing (Monte Carlo)
        volume = (x_max - x_min) * (y_max - y_min)
        target_rock_area = volume * target_fill_ratio
        current_rock_area = 0.0
        
        max_attempts = 2000
        rocks = [] # list of (x, y, r)

        attempts = 0
        while current_rock_area < target_rock_area and attempts < max_attempts:
            attempts += 1
            r = random.uniform(r_min, r_max)
            
            # Keep away from edges
            x = random.uniform(x_min + r, x_max - r)
            y = random.uniform(y_min + r, y_max - r)
            
            # Check overlap
            overlap = False
            for (rx, ry, rr) in rocks:
                dist_sq = (x - rx)**2 + (y - ry)**2
                min_dist = (r + rr)
                if dist_sq < min_dist**2:
                    overlap = True
                    break
            
            if not overlap:
                rocks.append((x, y, r))
                current_rock_area += np.pi * r * r
                
                # Generate gprMax cylinder command (Z axis infinite/long for 2D)
                # Generate gprMax cylinder command (Z axis infinite/long for 2D)
                # #cylinder: x1 y1 z1 x2 y2 z2 radius material
                # Generate gprMax cylinder command (Z axis infinite/long for 2D)
                # #cylinder: x1 y1 z1 x2 y2 z2 radius material
                cmd_lines.append(
                    f"#cylinder: {fmt(x)} {fmt(y)} 0.0 {fmt(x)} {fmt(y)} {fmt(cfg.domain_z)} {fmt(r)} {material_name}"
                )
                
        return cmd_lines

    def _add_granular_ballast(
        self,
        materials: List[str],
        geometry: List[str],
        ballast_bottom: float,
        rock_top: float,
        pvc: float,
        moisture: float,
    ) -> Dict[str, Any]:
        """
        High-Fidelity Granular Ballast (Multi-Layer Painter's Algo):
        1. Background Matrix: Fouling (if PVC > 0) or Air.
        2. Aggregates: 3 Layers of rocks, graded from Small (Bottom) to Large (Top).
        """
        cfg = self.cfg
        
        # 1. Define Fouling Material (Matrix)
        foul_eps = topp_mixing_model(moisture)
        foul_sigma = 0.001 + 0.2 * moisture 
        materials.append(f"#material: {fmt(foul_eps)} {fmt(foul_sigma)} 1 0 bal_foul_granular")

        # 2. Determine Fouling Height based on PVC (Horizon)
        foul_fill_height = (rock_top - ballast_bottom) * (pvc / 100.0)
        foul_horizon_y = ballast_bottom + foul_fill_height

        # 3. Draw Background Matrix (Painter's Step 1)
        # We draw the fouling box up to the horizon. Above that is implicit air (free_space).
        # Fix: gprMax snaps coords to grid. If thickness < dy/2, it snaps to 0 and causes 'lower < upper' error.
        if foul_fill_height > (cfg.dy * 0.5):
             geometry.append(f"## Fouling Matrix (PVC={pvc:.1f}%)")
             geometry.append(f"#box: 0.0 {fmt(ballast_bottom)} 0.0 {fmt(cfg.domain_x)} {fmt(foul_horizon_y)} {fmt(cfg.domain_z)} bal_foul_granular")

        # 4. Generate Aggregates in Layers (Painter's Step 2..N)
        geometry.append("## Granular Aggregates (Graded Layers)")
        
        n_layers = 3
        total_h = rock_top - ballast_bottom
        layer_h = total_h / n_layers
        
        # Radius grading: Small (Bottom) -> Large (Top)
        r_total_delta = cfg.rock_radius_max - cfg.rock_radius_min
        r_bin_step = r_total_delta / n_layers 
        
        rock_count_total = 0
        layer_metrics = {}  # Store per-layer air area metrics
        
        # Overlap factor: 1.0 means all layers span the full ballast height
        # This creates complete intermingling of all rock sizes
        overlap_ratio = 1.0
        
        for i in range(n_layers):
            # Nominal bounds
            y_nominal_min = ballast_bottom + i * layer_h
            y_nominal_max = ballast_bottom + (i + 1) * layer_h
            
            # Adjusted bounds for overlap
            # If not the bottom layer, start lower
            y_l_min = y_nominal_min
            if i > 0:
                y_l_min -= layer_h * overlap_ratio
                
            # Keep max overlap upwards? Maybe slight? 
            # Let's keep max as is, or maybe extended too?
            # Actually, standard Painter's just needs the new layer to intrude DOWNWARDS 
            # into the previous canvas.
            y_l_max = y_nominal_max
            
            # Layer Radius bounds (Graded)
            # Layer 0 (Bottom): [min, min + step] -> Smallest
            l_r_min = cfg.rock_radius_min + i * r_bin_step
            l_r_max = l_r_min + r_bin_step
            
            
            # Delegate to helper
            count, rock_area, air_pct = self._add_rock_layer(
                materials, geometry, i, 
                y_l_min, y_l_max, 
                l_r_min, l_r_max, 
                n_layers
            )
            rock_count_total += count
            
            # Store air metrics for this layer
            layer_metrics[f"L{i+1}_rock_count"] = count
            layer_metrics[f"L{i+1}_rock_area"] = float(rock_area)
            layer_metrics[f"L{i+1}_air_percent"] = float(air_pct)

        return {
            "scenario_detail": "granular_graded",
            "pvc": pvc,
            "moisture_content": moisture,
            "foul_eps_derived": float(foul_eps),
            "foul_sigma_derived": float(foul_sigma),
            "rock_count": rock_count_total,
            **layer_metrics
        }

    def _add_uniform_fouling(
        self,
        materials: List[str],
        geometry: List[str],
        ballast_bottom: float,
        foul_top: float,
        base_eps: float = 0.0,
        base_sigma: float = 0.0,
    ) -> Dict[str, Any]:
        """
        Simple case: one fouled layer overwriting the bottom of the rock.
        """
        cfg = self.cfg

        # Fouled layer - only add if strictly positive thickness
        if foul_top > ballast_bottom + 1e-9:
            geometry.append(f"## Layer: bal_foul ({fmt(ballast_bottom)}–{fmt(foul_top)})")
            geometry.append(f"#box: 0.0 {fmt(ballast_bottom)} 0.0   {fmt(cfg.domain_x)} {fmt(foul_top)} {fmt(cfg.domain_z)} bal_foul")

        return {"scenario_detail": "uniform"}

    def _add_vertical_gradient(
        self,
        materials: List[str],
        geometry: List[str],
        ballast_bottom: float,
        foul_top: float,
        base_eps: float,
        base_sigma: float,
    ) -> Dict[str, Any]:
        """
        Split fouled region into several sublayers with increasing eps/sigma.
        """
        cfg = self.cfg
        foul_thickness = foul_top - ballast_bottom
        if foul_thickness <= 0:
            return self._add_uniform_fouling(materials, geometry, ballast_bottom, ballast_bottom, base_eps, base_sigma)

        n_layers = random.randint(cfg.grad_min_layers, cfg.grad_max_layers)
        sub_thick = foul_thickness / n_layers
        eps_bottom = base_eps * 0.8
        eps_top = base_eps * 1.2
        sigma_bottom = base_sigma * 0.5
        sigma_top = base_sigma * 1.5

        eps_values = np.linspace(eps_bottom, eps_top, n_layers)
        sigma_values = np.linspace(sigma_bottom, sigma_top, n_layers)

        # Define materials
        grad_labels = []
        for i in range(n_layers):
            label = f"bal_foul_g{i+1}"
            grad_labels.append(label)
            materials.append(f"#material: {fmt(eps_values[i])} {fmt(sigma_values[i])} 1 0 {label}")

        # Define geometry (bottom up)
        y0 = ballast_bottom
        for i, label in enumerate(grad_labels):
            y1 = ballast_bottom + (i + 1) * sub_thick
            geometry.append(f"## Gradient Layer {i+1}: {label} ({fmt(y0)}–{fmt(y1)})")
            geometry.append(f"#box: 0.0 {fmt(y0)} 0.0   {fmt(cfg.domain_x)} {fmt(y1)} {fmt(cfg.domain_z)} {label}")
            y0 = y1

        return {
            "scenario_detail": "vertical_gradient",
            "grad_layers": n_layers,
            "grad_eps_min": float(eps_bottom),
            "grad_eps_max": float(eps_top),
        }

    def _add_pockets(
        self,
        materials: List[str],
        geometry: List[str],
        ballast_bottom: float,
        foul_top: float,
        rock_top: float,
        base_eps: float,
        base_sigma: float,
    ) -> Dict[str, Any]:
        """
        Uniform fouling layer plus localized high-contrast pockets.
        Pockets can be randomly placed anywhere in the ballast layer (ballast_bottom to rock_top).
        """
        cfg = self.cfg

        # 1. Base Fouled Layer (optional background fouling)
        # If foul_top > ballast_bottom, we have a base layer of fouling
        if foul_top > ballast_bottom + 1e-9:
            geometry.append(f"## Layer: bal_foul ({fmt(ballast_bottom)}–{fmt(foul_top)})")
            geometry.append(f"#box: 0.0 {fmt(ballast_bottom)} 0.0   {fmt(cfg.domain_x)} {fmt(foul_top)} {fmt(cfg.domain_z)} bal_foul")

        # 2. Pocket material
        # We'll use one pocket material type for now, or could vary per pocket
        pocket_eps = random.uniform(cfg.pocket_eps_min, cfg.pocket_eps_max)
        pocket_sigma = random.uniform(cfg.pocket_sigma_min, cfg.pocket_sigma_max)
        materials.append(f"#material: {fmt(pocket_eps)} {fmt(pocket_sigma)} 1 0 foul_pocket")

        # 3. Pockets (Random placement, overlapping allowed)
        # We allow pockets anywhere in the ballast (from ballast_bottom to rock_top)
        n_pockets = random.randint(1, cfg.max_pockets)
        
        geometry.append(f"## Fouling Pockets (Count: {n_pockets})")
        
        for i in range(n_pockets):
            # Random dimensions
            w = random.uniform(0.05, 0.25) # Width 5cm to 25cm
            h = random.uniform(0.02, 0.15) # Height 2cm to 15cm
            
            # Random center
            # Ensure at least part of the pocket is inside the domain/ballast
            # but allow them to be "messy" (clipping handled by min/max below)
            # Center X
            cx = random.uniform(0.0, cfg.domain_x)
            # Center Y
            cy = random.uniform(ballast_bottom, rock_top)
            
            # Box coords
            x1 = max(0.0, cx - w/2)
            x2 = min(cfg.domain_x, cx + w/2)
            y1 = max(ballast_bottom, cy - h/2)
            y2 = min(rock_top, cy + h/2)

            # Valid box check
            if y2 > y1 + 1e-5 and x2 > x1 + 1e-5:
                geometry.append(f"#box: {fmt(x1)} {fmt(y1)} 0.0   {fmt(x2)} {fmt(y2)} {fmt(cfg.domain_z)} foul_pocket")

        return {
            "scenario_detail": "pockets",
            "pocket_count": n_pockets,
            "pocket_eps": float(pocket_eps),
            "pocket_sigma": float(pocket_sigma),
        }

    def _add_wet_fouling(
        self,
        materials: List[str],
        geometry: List[str],
        ballast_bottom: float,
        foul_top: float,
        base_eps: float,
        base_sigma: float,
    ) -> Dict[str, Any]:
        """
        Wet fouling: top portion of fouled layer is saturated.
        """
        cfg = self.cfg
        foul_thickness = foul_top - ballast_bottom
        if foul_thickness <= 0:
            return self._add_uniform_fouling(materials, geometry, ballast_bottom, ballast_bottom, base_eps, base_sigma)

        wet_frac = random.uniform(0.3, 0.9)
        wet_thickness = foul_thickness * wet_frac
        wet_top = ballast_bottom + wet_thickness

        eps_factor = random.uniform(cfg.wet_eps_factor_min, cfg.wet_eps_factor_max)
        sigma_factor = random.uniform(cfg.wet_sigma_factor_min, cfg.wet_sigma_factor_max)
        wet_eps = base_eps * eps_factor
        wet_sigma = base_sigma * sigma_factor

        materials.append(f"#material: {fmt(wet_eps)} {fmt(wet_sigma)} 1 0 bal_foul_wet")

        # Dry fouling (bottom part)
        if wet_top > ballast_bottom + 1e-9:
            geometry.append(f"## Layer: bal_foul (dry) ({fmt(ballast_bottom)}–{fmt(wet_top)})")
            geometry.append(f"#box: 0.0 {fmt(ballast_bottom)} 0.0   {fmt(cfg.domain_x)} {fmt(wet_top)} {fmt(cfg.domain_z)} bal_foul")

        # Wet fouling (top part)
        if foul_top > wet_top + 1e-9:
            geometry.append(f"## Layer: bal_foul_wet ({fmt(wet_top)}–{fmt(foul_top)})")
            geometry.append(f"#box: 0.0 {fmt(wet_top)} 0.0   {fmt(cfg.domain_x)} {fmt(foul_top)} {fmt(cfg.domain_z)} bal_foul_wet")

        return {
            "scenario_detail": "wet",
            "wet_fraction": wet_frac,
            "wet_eps": float(wet_eps),
            "wet_sigma": float(wet_sigma),
        }

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
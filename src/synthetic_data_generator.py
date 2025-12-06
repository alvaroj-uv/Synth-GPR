import argparse
import random
import configparser
import sys
from datetime import date
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List, Dict, Any

import numpy as np
import pandas as pd


# ------------------------------------------------------------
# Utility: FI and classification
# ------------------------------------------------------------
def get_fi_class(fi_val: float) -> str:
    """
    Classification based on Percentage Voids Contaminated (PVC) as per user spec:
    1. Clean (CL): PVC <= 5%
    2. Moderately Clean (MC): 5% < PVC <= 20%
    3. Moderately Fouled (MF): 20% < PVC <= 40%
    4. Fouled (F): 40% < PVC <= 60%
    5. Highly Fouled (HF): PVC > 60%
    """
    if fi_val <= 5.0:
        return "CL" # Clean
    elif fi_val <= 20.0:
        return "MC" # Moderately Clean
    elif fi_val <= 40.0:
        return "MF" # Moderately Fouled
    elif fi_val <= 60.0:
        return "F"  # Fouled
    else:
        return "HF" # Highly Fouled / Failure

def get_fi_class_legacy(fi_val: float) -> str:
    """
    Selig & Waters (1994) standard classification (Legacy).
    Keep for comparison.
    CL: < 1
    MC: 1 - 10
    M: 10 - 20
    MF: 20 - 40
    HF: > 40
    """
    if fi_val < 1.0:
        return "CL"
    elif fi_val < 10.0:
        return "MC"
    elif fi_val < 20.0:
        return "M"
    elif fi_val < 40.0:
        return "MF"
    else:
        return "HF"

def get_pvc_class(pvc_val: float) -> str:
    """Classify based on PVC using the standard defined in get_fi_class."""
    return get_fi_class(pvc_val)

def compute_fi(rock_h: float, foul_h: float) -> float:
    total = rock_h + foul_h
    if total <= 0:
        return 0.0
    return (foul_h / total) * 100.0



def classify_fi(FI: float) -> str:
    # Selig & Waters style bands - short codes
    if FI < 20:
        return "CL"
    elif FI < 40:
        return "MF"
    # Wet fouling amplification factors
    wet_eps_factor_min: float = 1.2
    wet_eps_factor_max: float = 1.8
    wet_sigma_factor_min: float = 2.0
    wet_sigma_factor_max: float = 5.0

    # Pockets
    max_pockets: int = 4
    pocket_eps_min: float = 7.0
    pocket_eps_max: float = 10.0
    pocket_sigma_min: float = 0.005
    pocket_sigma_max: float = 0.03

    # Vertical gradient: number of fouled sublayers
    grad_min_layers: int = 2
    grad_max_layers: int = 5

    # Random seed base (optional)
    base_seed: int | None = None



# ------------------------------------------------------------
# Formatting Helper
# ------------------------------------------------------------
def topp_mixing_model(theta: float) -> float:
    """
    Topp's equation for soil dielectric constant based on volumetric water content.
    Ref: Topp et al (1980).
    theta: Volumetric water content (0.0 - 1.0)
    """
    # Clamp theta to realistic range
    theta = max(0.0, min(theta, 1.0))
    e_r = 3.03 + 9.3 * theta + 146.0 * theta**2 - 76.7 * theta**3
    return e_r

def fmt(val: float) -> str:
    """Format float to 5 significant figures."""
    if abs(val) < 1e-9:
        return "0.0"
    return f"{val:.5g}"

# ------------------------------------------------------------
# Config dataclass
# ------------------------------------------------------------

@dataclass
class GeneratorConfig:
    # Geometry and grid
    domain_x: float = 0.5
    domain_y: float = 1.3
    domain_z: float = 0.005

    dx: float = 0.005
    dy: float = 0.005
    dz: float = 0.005

    # Time window
    time_window: float = 1.5e-8

    # Waveform / antenna
    center_freq: float = 1.5e9  # Hz
    tx_x: float = 0.300
    rx_x: float = 0.35
    tx_rx_y: float = 0.904
    tx_rx_z: float = 0.0025 # Centered in Z for 2D
    add_waveform: bool = True
    add_source: bool = True
    add_geometry_view: bool = False

    # Granular & High-Fidelity Settings
    granular_mode: bool = False
    pvc_min: float = 0.0   # Percentage Voids Contaminated (0-100)
    pvc_max: float = 100.0
    
    # Aggregate properties
    rock_radius_min: float = 0.02
    rock_radius_max: float = 0.05
    
    # Moisture & Fouling Props
    moisture_min: float = 0.0  # Volumetric water content (0-1)
    moisture_max: float = 0.3
    fractal_dimension: float = 1.5 # Texture of fouling
    
    # Ballast/subgrade nominal depths (y-direction)
    min_ballast_thickness: float = 0.25 # Increased for granular realism
    max_ballast_thickness: float = 0.45 

    min_foul_thickness: float = 0.00
    max_foul_thickness: float = 0.10

    formation_thickness: float = 0.10
    subgrade_thickness: float = 0.05

    # Material ranges
    # Clean ballast
    bal_rock_eps: float = 5.0 
    bal_rock_sigma: float = 0.001

    # Base fouled material properties (Legacy/Fallback)
    bal_foul_eps_min: float = 6.0
    bal_foul_eps_max: float = 8.0
    bal_foul_sigma_min: float = 0.002
    bal_foul_sigma_max: float = 0.01

    # Wet fouling amplification factors
    wet_eps_factor_min: float = 1.2
    wet_eps_factor_max: float = 1.8
    wet_sigma_factor_min: float = 2.0
    wet_sigma_factor_max: float = 5.0

    # Pockets
    max_pockets: int = 4
    pocket_eps_min: float = 7.0
    pocket_eps_max: float = 10.0
    pocket_sigma_min: float = 0.005
    pocket_sigma_max: float = 0.03

    # Vertical gradient: number of fouled sublayers
    grad_min_layers: int = 2
    grad_max_layers: int = 5

    # Random seed base (optional)
    base_seed: int | None = None

    @classmethod
    def from_ini(cls, ini_path: str):
        """Load configuration from an INI file."""
        if not Path(ini_path).exists():
            raise FileNotFoundError(f"Config file not found: {ini_path}")
            
        config = configparser.ConfigParser()
        config.read(ini_path)
        
        args = {}
        
        # Helper to safely get values
        def get_float(section, key):
            return config.getfloat(section, key, fallback=None)
        def get_int(section, key):
            return config.getint(section, key, fallback=None)
        def get_bool(section, key):
            return config.getboolean(section, key, fallback=None)

        # [Geometry]
        if 'Geometry' in config:
            args['domain_x'] = get_float('Geometry', 'domain_x')
            args['domain_y'] = get_float('Geometry', 'domain_y')
            args['domain_z'] = get_float('Geometry', 'domain_z')
            args['dx'] = get_float('Geometry', 'dx')
            args['dy'] = get_float('Geometry', 'dy')
            args['dz'] = get_float('Geometry', 'dz')
            args['subgrade_thickness'] = get_float('Geometry', 'subgrade_thickness')
            args['formation_thickness'] = get_float('Geometry', 'formation_thickness')
            args['min_ballast_thickness'] = get_float('Geometry', 'min_ballast_thickness')
            args['max_ballast_thickness'] = get_float('Geometry', 'max_ballast_thickness')
            args['min_foul_thickness'] = get_float('Geometry', 'min_foul_thickness')
            args['max_foul_thickness'] = get_float('Geometry', 'max_foul_thickness')

        # [Simulation]
        if 'Simulation' in config:
            args['time_window'] = get_float('Simulation', 'time_window')
            args['center_freq'] = get_float('Simulation', 'center_freq')
            args['tx_x'] = get_float('Simulation', 'tx_x')
            args['rx_x'] = get_float('Simulation', 'rx_x')
            args['tx_rx_y'] = get_float('Simulation', 'tx_rx_y')
            args['tx_rx_z'] = get_float('Simulation', 'tx_rx_z')
            args['add_waveform'] = get_bool('Simulation', 'add_waveform')
            args['add_source'] = get_bool('Simulation', 'add_source')
            args['add_geometry_view'] = get_bool('Simulation', 'add_geometry_view')
            
            # Base seed
            seed_val = config.get('Simulation', 'base_seed', fallback=None)
            if seed_val and seed_val.strip():
                args['base_seed'] = int(seed_val)

        # [Granular]
        if 'Granular' in config:
            args['granular_mode'] = get_bool('Granular', 'granular_mode')
            args['pvc_min'] = get_float('Granular', 'pvc_min')
            args['pvc_max'] = get_float('Granular', 'pvc_max')
            args['rock_radius_min'] = get_float('Granular', 'rock_radius_min')
            args['rock_radius_max'] = get_float('Granular', 'rock_radius_max')
            args['max_pockets'] = get_int('Granular', 'max_pockets')

        # [Moisture]
        if 'Moisture' in config:
            args['moisture_min'] = get_float('Moisture', 'moisture_min')
            args['moisture_max'] = get_float('Moisture', 'moisture_max')
            args['fractal_dimension'] = get_float('Moisture', 'fractal_dimension')

        # [Materials]
        if 'Materials' in config:
            args['bal_rock_eps'] = get_float('Materials', 'bal_rock_eps')
            args['bal_rock_sigma'] = get_float('Materials', 'bal_rock_sigma')
            args['bal_foul_eps_min'] = get_float('Materials', 'bal_foul_eps_min')
            args['bal_foul_eps_max'] = get_float('Materials', 'bal_foul_eps_max')
            args['bal_foul_sigma_min'] = get_float('Materials', 'bal_foul_sigma_min')
            args['bal_foul_sigma_max'] = get_float('Materials', 'bal_foul_sigma_max')
            args['pocket_eps_min'] = get_float('Materials', 'pocket_eps_min')
            args['pocket_eps_max'] = get_float('Materials', 'pocket_eps_max')
            args['pocket_sigma_min'] = get_float('Materials', 'pocket_sigma_min')
            args['pocket_sigma_max'] = get_float('Materials', 'pocket_sigma_max')
            args['wet_eps_factor_min'] = get_float('Materials', 'wet_eps_factor_min')
            args['wet_eps_factor_max'] = get_float('Materials', 'wet_eps_factor_max')
            args['wet_sigma_factor_min'] = get_float('Materials', 'wet_sigma_factor_min')
            args['wet_sigma_factor_max'] = get_float('Materials', 'wet_sigma_factor_max')

        # [VerticalGradient]
        if 'VerticalGradient' in config:
            args['grad_min_layers'] = get_int('VerticalGradient', 'grad_min_layers')
            args['grad_max_layers'] = get_int('VerticalGradient', 'grad_max_layers')
            
        # Filter out None values to respect defaults
        args = {k: v for k, v in args.items() if v is not None}
        
        return cls(**args)


# ------------------------------------------------------------
# Scenario generator
# ------------------------------------------------------------

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

        # --- SECTIONS ---
        # Note: Header is built LAST to include scenario details
        setup_lines: List[str] = []
        material_lines: List[str] = []
        geometry_lines: List[str] = []
        
        # 1. Setup (Domain, Time, etc.)
        setup_lines.append(f"#title: {FI_class}_{scenario_type}")
        setup_lines.append(f"#domain: {fmt(cfg.domain_x)} {fmt(cfg.domain_y)} {fmt(cfg.domain_z)}")
        setup_lines.append(f"#dx_dy_dz: {fmt(cfg.dx)} {fmt(cfg.dy)} {fmt(cfg.dz)}")
        setup_lines.append(f"#time_window: {fmt(cfg.time_window)}")

        # 2. Materials (Base definitions)
        # Note: Granular mode adds its own materials dynamically, but keeping these doesn't hurt
        materials_used = False if cfg.granular_mode else True
        if materials_used:
             material_lines.append(f"#material: {fmt(cfg.bal_rock_eps)} {fmt(cfg.bal_rock_sigma)} 1 0 bal_rock")
             material_lines.append(f"#material: {fmt(base_foul_eps)} {fmt(base_foul_sigma)} 1 0 bal_foul")
        else:
             # Define minimal base materials for layers that stay constant
             material_lines.append(f"#material: {fmt(cfg.bal_rock_eps)} {fmt(cfg.bal_rock_sigma)} 1 0 bal_rock")
        
        material_lines.append("#material: 7.0 0.01 1 0 subgrade")
        material_lines.append("#material: 10.0 0.03 1 0 formation")

        # 3. Waveform
        if cfg.add_waveform:
            setup_lines.append(f"#waveform: ricker 1 {fmt(cfg.center_freq)} src")

        # 4. Geometry - Painter's Algorithm (Back to Front)
        
        # A. Background (Free Space)
        geometry_lines.append("## Fondo completo (free_space)")
        geometry_lines.append(f"#box: 0.0 0.0 0.0   {fmt(cfg.domain_x)} {fmt(cfg.domain_y)} {fmt(cfg.domain_z)} free_space")

        # B. Subgrade
        y_subgrade = cfg.subgrade_thickness
        geometry_lines.append(f"## Layer: subgrade (0.00–{fmt(y_subgrade)})")
        geometry_lines.append(f"#box: 0.0 0.0 0.0   {fmt(cfg.domain_x)} {fmt(y_subgrade)} {fmt(cfg.domain_z)} subgrade")

        # C. Formation
        y_formation_top = y_subgrade + cfg.formation_thickness
        geometry_lines.append(f"## Layer: formation ({fmt(y_subgrade)}–{fmt(y_formation_top)})")
        geometry_lines.append(f"#box: 0.0 {fmt(y_subgrade)} 0.0   {fmt(cfg.domain_x)} {fmt(y_formation_top)} {fmt(cfg.domain_z)} formation")

        # D. Ballast Region
        ballast_bottom = y_formation_top
        
        # Branching: Granular vs Legacy Homogeneous
        if cfg.granular_mode:
            # In granular mode, rock_h is the total ballast thickness
            # foul_h determines the "Horizon" based on PVC, but total thickness is rock_h
            total_ballast_h = rock_h 
            rock_top = ballast_bottom + total_ballast_h
            rock_top = min(rock_top, cfg.domain_y)
            
            # Call Granular Builder
            scenario_info.update(
                self._add_granular_ballast(
                    material_lines, 
                    geometry_lines, 
                    ballast_bottom, 
                    rock_top, 
                    pvc, 
                    moisture
                )
            )
        else:
            # Legacy Logic
            foul_top = ballast_bottom + foul_h
            rock_top = ballast_bottom + foul_h + rock_h
            rock_top = min(rock_top, cfg.domain_y)

            # 1. Define the entire ballast layer as Clean Rock
            geometry_lines.append(f"## Layer: bal_rock (Entire Ballast: {fmt(ballast_bottom)}–{fmt(rock_top)})")
            geometry_lines.append(f"#box: 0.0 {fmt(ballast_bottom)} 0.0   {fmt(cfg.domain_x)} {fmt(rock_top)} {fmt(cfg.domain_z)} bal_rock")

            # 2. Overwrite with Fouling
            if scenario_type == "uniform":
                scenario_info.update(self._add_uniform_fouling(material_lines, geometry_lines, ballast_bottom, foul_top, base_foul_eps, base_foul_sigma))
            elif scenario_type == "vertical_gradient":
                scenario_info.update(self._add_vertical_gradient(material_lines, geometry_lines, ballast_bottom, foul_top, base_foul_eps, base_foul_sigma))
            elif scenario_type == "pockets":
                # Now passing rock_top to allow pockets anywhere
                scenario_info.update(self._add_pockets(material_lines, geometry_lines, ballast_bottom, foul_top, rock_top, base_foul_eps, base_foul_sigma))
            elif scenario_type == "wet":
                scenario_info.update(self._add_wet_fouling(material_lines, geometry_lines, ballast_bottom, foul_top, base_foul_eps, base_foul_sigma))

            else:
                scenario_info.update(self._add_uniform_fouling(material_lines, geometry_lines, ballast_bottom, foul_top, base_foul_eps, base_foul_sigma))
            
            # Needed for legacy E. calculation
            rock_top = rock_top # variable exists

        # E. TX/RX
        if cfg.add_source:
            # Recalculate rock_top for safety if variable naming differed
            if cfg.granular_mode:
                total_ballast_h = rock_h
                antenna_y = ballast_bottom + total_ballast_h + 0.53
            else:
                antenna_y = ballast_bottom + foul_h + rock_h + 0.53
                
            # Enforce 53 cm air gap
            # Warn if antenna is out of bounds or too close to PML
            margin = 15 * cfg.dy  # 15 cells margin
            if antenna_y > (cfg.domain_y - margin):
                raise ValueError(
                    f"Antenna height {antenna_y:.4f} is too close to domain top {cfg.domain_y:.4f}. "
                    f"Must be < {cfg.domain_y - margin:.4f} (15 cells margin)."
                )

            geometry_lines.append("## TX/RX en aire (sobre la superficie + 53cm)")
            geometry_lines.append(f"#hertzian_dipole: z {fmt(cfg.tx_x)} {fmt(antenna_y)} {fmt(cfg.tx_rx_z)} src")
            geometry_lines.append(f"#rx: {fmt(cfg.rx_x)} {fmt(antenna_y)} {fmt(cfg.tx_rx_z)}")

        # F. Geometry View
        if cfg.add_geometry_view:
            geometry_lines.append(
                f"#geometry_view: 0 0 0  {fmt(cfg.domain_x)} {fmt(cfg.domain_y)} {fmt(cfg.domain_z)}  "
                f"{fmt(cfg.dx)} {fmt(cfg.dy)} {fmt(cfg.dz)} {base_name}.vtk n"
            )

        # --- BUILD HEADER LAST (using potentially updated scenario_info) ---
        header_lines: List[str] = []
        header_lines.append("## ------------------------------------------------------------")
        header_lines.append("## Generated gprMax Input File")
        header_lines.append(f"## Scenario: {scenario_type}")
        header_lines.append(f"## Date: {date.today().isoformat()}")
        header_lines.append(f"## Base Seed: {cfg.base_seed}")
        header_lines.append(f"## Rock Height: {fmt(rock_h)}")
        header_lines.append(f"## Foul Height: {fmt(foul_h)}")
        header_lines.append(f"## FI (%): {fmt(FI)}")
        header_lines.append(f"## FI class: {FI_class}")
        header_lines.append(f"## FI Class Leg: {FI_class_legacy}")
        if cfg.granular_mode:
            header_lines.append(f"## Mode: Granular (High-Fidelity)")
        
        # Add dynamic scenario details
        for k, v in scenario_info.items():
            if k not in ["bal_rock_eps", "bal_rock_sigma", "bal_foul_eps_base", "bal_foul_sigma_base", "scenario_detail"]:
                # Format float values nicely if possible, otherwise str
                val_str = fmt(v) if isinstance(v, float) else str(v)
                header_lines.append(f"## {k}: {val_str}")

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
        if foul_fill_height > 1e-9:
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
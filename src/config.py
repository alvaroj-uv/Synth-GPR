
import configparser
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Any

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
    else:
        return "F" # Fallback

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
    """
    Configuration Data Transfer Object (DTO) for the synthetic generator.
    
    This class holds all parameters governing the simulation, including:
    - Domain geometry (size, grid step).
    - Antenna settings (freq, positions).
    - Material properties (dielectric constant, conductivity).
    - Scenario parameters (moisture, fouling levels).
    
    Can be initialized directly or loaded from an INI file via `from_ini`.
    """
    # Geometry and grid
    domain_x: float = 0.5
    domain_y: float = 1.5   # Increased from 1.3 to accommodate thicker subgrade
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
    add_sleepers: bool = False # Disabled by default as per user request

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
    subgrade_thickness: float = 0.20 # Increased from 0.05 to avoid PML artifacts

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
            args['add_source'] = get_bool('Simulation', 'add_source')
            args['add_geometry_view'] = get_bool('Simulation', 'add_geometry_view')
            args['add_sleepers'] = get_bool('Simulation', 'add_sleepers')
            
            # Base seed
            seed_str = config.get('Simulation', 'base_seed', fallback=None)
            if seed_str and seed_str.strip():
                try:
                    args['base_seed'] = int(seed_str)
                except ValueError:
                    pass

        # [Granular]
        if 'Granular' in config:
            granular_mode = config.get('Granular', 'granular_mode', fallback='False')
            # Handle boolean string
            if isinstance(granular_mode, str):
                 granular_mode = granular_mode.lower() == 'true'
            args['granular_mode'] = granular_mode
            
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

        # Filter None values (use defaults)
        filtered_args = {k: v for k, v in args.items() if v is not None}
        
        return cls(**filtered_args)

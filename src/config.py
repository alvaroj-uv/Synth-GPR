
import configparser
from dataclasses import dataclass, field
from pathlib import Path



# ------------------------------------------------------------
# Config dataclass
# ------------------------------------------------------------

@dataclass(frozen=True)
class GeneratorConfig:
    # Configuration Data Transfer Object (DTO) for the synthetic generator.
    # 
    # This class holds all parameters governing the simulation.
    # Immutable: Changes require creating a new instance (e.g., using dataclasses.replace).
    # Domain size (Railway GPR standard)
    domain_x: float = 0.5
    domain_y: float = 1.5
    domain_z: float = 0.005
    
    # Domain Height Limits (Railway Literature)
    # Typical GPR antenna: 30-100cm above ballast surface
    # Max realistic height: subgrade(0.5) + formation(0.1) + ballast(0.45) + antenna(0.5) + buffer(0.1) = 1.65m
    max_domain_y: float = 1.65  # Hard limit from literature

    dx: float = 0.005
    dy: float = 0.005
    dz: float = 0.005
    
    # Time window
    time_window: float = 1.5e-8

    # Waveform / antenna
    center_freq: float = 1.5e9
    tx_x: float = 0.300
    rx_x: float = 0.35
    tx_rx_y: float = 1.4  # Raised to use domain efficiently (10cm below top, 50cm above max rocks)
    tx_rx_z: float = 0.0025
    add_waveform: bool = True
    add_source: bool = True
    add_geometry_view: bool = False
    add_sleepers: bool = False

    # Granular & High-Fidelity Settings
    granular_mode: bool = False
    pvc_min: float = 0.0
    pvc_max: float = 100.0
    
    # Aggregate properties
    rock_radius_min: float = 0.02
    rock_radius_max: float = 0.032
    
    # Rock Packing Parameters
    rock_layers: int = 3  # Number of vertical layers for rock placement
    rock_packing_target_fill: float = 0.6  # Target density (60% filled)
    rock_packing_max_attempts: int = 1000  # Max attempts for packing algorithm
    enable_rock_caching: bool = False  # If False, always generate fresh rocks
    
    # Moisture & Fouling Props
    moisture_min: float = 0.0
    moisture_max: float = 0.3
    fractal_dimension: float = 1.5
    
    # Fouling Distribution Parameters
    fouling_settled_fraction: float = 0.7  # 70% settles to bottom layer
    fouling_particle_size_min: float = 0.002  # 2mm
    fouling_particle_size_max: float = 0.008  # 8mm
    
    # Antenna Placement
    antenna_clearance_above_ballast: float = 0.50  # 50cm above highest rock (railway standard)
    antenna_rock_clearance: float = 0.02  # 2cm minimum clearance from rocks
    
    # Rock Z-Extent (Extrusion)
    rock_z_start: float = 0.0
    rock_z_end: float = 0.005  # Default to 0 (2D plane)
    
    # Rock Packing Strategy
    rock_packing_algorithm: str = "front_chain"  # "random", "poisson", "front_chain", "physics", "triangle"
    wang_tile_size: float = 0.1  # Size of Wang tiles in meters
    
    # Ballast/subgrade nominal depths
    subgrade_height: float = 0.3  # Increased to 0.3m for more realistic railway geometry
    min_ballast_thickness: float = 0.35  # More realistic range now that antenna is higher
    max_ballast_thickness: float = 0.55  # Max: subgrade(0.3) + formation(0.1) + ballast(0.55) = 0.95m > max_rock(0.9m) 

    min_foul_thickness: float = 0.00
    max_foul_thickness: float = 0.10

    formation_thickness: float = 0.10
    subgrade_thickness: float = 0.20

    # Degradation Parameters (Realistic ballast aging simulation)
    enable_degradation: bool = False
    degradation_level: float = 0.0  # 0-100% (0=fresh, 100=heavily degraded)
    breakage_probability_large: float = 0.15  # 15% of >40mm rocks break
    breakage_probability_medium: float = 0.05  # 5% of 20-40mm rocks break
    fines_threshold: float = 0.010  # 10mm - particles below this migrate
    fines_accumulation_zone: float = 0.3  # Bottom 30% of ballast

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
    
    # ============================================================
    # Domain Randomization (for ML robustness)
    # ============================================================
    enable_domain_randomization: bool = False
    
    soil_eps_variation: float = 0.2
    soil_sigma_variation: float = 0.5
    
    rock_eps_variation: float = 0.1
    rock_sigma_variation: float = 0.5
    
    moisture_randomization_range: float = 0.15
    
    spatial_jitter_sigma: float = 0.02
    
    noise_snr_min: float = 20.0
    noise_snr_max: float = 40.0
    add_noise: bool = False
    
    # Antenna-shifted variant generation
    generate_antenna_variants: bool = False
    antenna_shift_amount: float = 0.05  # 5cm shift left/right
    
    # ============================================================
    # Workflow Parameters (for script execution)
    # ============================================================
    output_dir: str = "output"
    labels: list = field(default_factory=lambda: ["C", "MC", "MF", "F", "HF"])
    samples_per_label: int = 10
    start_id: int = 1000
    
    num_jobs: int = 4
    gpu_devices: list = field(default_factory=list)
    
    feature_output_csv: str = "features.csv"
    
    show_plot: bool = False
    output_dpi: int = 150

    base_seed: int | None = None


    def __post_init__(self):
        # Validate configuration invariants with clear error messages.
        # 
        # Follows gprMax validation pattern: each parameter gets explicit
        # validation with descriptive error messages.
        # Spatial discretization validation
        if self.dx <= 0:
            raise ValueError("#dx_dy_dz: x-direction spatial step (dx) must be greater than zero")
        
        # PVC (Percentage Voids Contaminated) must be valid percentage
        if self.pvc_min < 0 or self.pvc_min > 100:
            raise ValueError(f"pvc_min must be between 0 and 100, got {self.pvc_min}")
        if self.pvc_max < 0 or self.pvc_max > 100:
            raise ValueError(f"pvc_max must be between 0 and 100, got {self.pvc_max}")
        if self.pvc_min > self.pvc_max:
            raise ValueError(f"pvc_min ({self.pvc_min}) cannot exceed pvc_max ({self.pvc_max})")
        
        # Moisture must be valid fraction
        if self.moisture_min < 0 or self.moisture_min > 1:
            raise ValueError(f"moisture_min must be between 0 and 1, got {self.moisture_min}")
        if self.moisture_max < 0 or self.moisture_max > 1:
            raise ValueError(f"moisture_max must be between 0 and 1, got {self.moisture_max}")
        if self.moisture_min > self.moisture_max:
            raise ValueError(f"moisture_min ({self.moisture_min}) cannot exceed moisture_max ({self.moisture_max})")
            
    
    @classmethod
    def from_ini(cls, ini_path: str):
        # Load configuration from an INI file.
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
            
            # Rock Packing
            args['rock_packing_algorithm'] = config.get('Granular', 'rock_packing_algorithm', fallback='wang')
            args['rock_packing_algorithm'] = config.get('Granular', 'rock_packing_algorithm', fallback='wang')
            args['enable_rock_caching'] = get_bool('Granular', 'enable_rock_caching')
            args['wang_tile_size'] = get_float('Granular', 'wang_tile_size')
            
            # Rock Z
            args['rock_z_start'] = get_float('Granular', 'rock_z_start')
            args['rock_z_end'] = get_float('Granular', 'rock_z_end')

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
        
        # [domain_randomization] (NEW)
        if 'domain_randomization' in config:
            args['enable_domain_randomization'] = get_bool('domain_randomization', 'enable_domain_randomization')
            args['soil_eps_variation'] = get_float('domain_randomization', 'soil_eps_variation')
            args['soil_sigma_variation'] = get_float('domain_randomization', 'soil_sigma_variation')
            args['rock_eps_variation'] = get_float('domain_randomization', 'rock_eps_variation')
            args['rock_sigma_variation'] = get_float('domain_randomization', 'rock_sigma_variation')
            args['moisture_randomization_range'] = get_float('domain_randomization', 'moisture_randomization_range')
            args['spatial_jitter_sigma'] = get_float('domain_randomization', 'spatial_jitter_sigma')
            args['noise_snr_min'] = get_float('domain_randomization', 'noise_snr_min')
            args['noise_snr_max'] = get_float('domain_randomization', 'noise_snr_max')
            args['add_noise'] = get_bool('domain_randomization', 'add_noise')
        
        # [workflow] (NEW)
        if 'workflow' in config:
            args['output_dir'] = config.get('workflow', 'output_dir', fallback=None)
            
            # Parse labels (comma-separated)
            labels_str = config.get('workflow', 'labels', fallback=None)
            if labels_str:
                args['labels'] = [l.strip() for l in labels_str.split(',')]
            
            args['samples_per_label'] = get_int('workflow', 'samples_per_label')
            args['start_id'] = get_int('workflow', 'start_id')
            args['num_jobs'] = get_int('workflow', 'num_jobs')
            
            # Parse GPU devices (comma-separated)
            gpu_str = config.get('workflow', 'gpu_devices', fallback=None)
            if gpu_str and gpu_str.strip():
                args['gpu_devices'] = [int(x.strip()) for x in gpu_str.split(',')]
            
            args['feature_output_csv'] = config.get('workflow', 'feature_output_csv', fallback=None)
            args['show_plot'] = get_bool('workflow', 'show_plot')
            args['output_dpi'] = get_int('workflow', 'output_dpi')
            
            # Antenna variants
            args['generate_antenna_variants'] = get_bool('workflow', 'generate_antenna_variants')
            args['antenna_shift_amount'] = get_float('workflow', 'antenna_shift_amount')



        # Filter None values (use defaults)
        filtered_args = {k: v for k, v in args.items() if v is not None}
        
        return cls(**filtered_args)

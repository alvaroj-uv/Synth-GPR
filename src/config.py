
import configparser
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional



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
    # Domain size (IEEE 2025 / Khosravi Largani et al. Guideline: 1.5 * lambda_max)
    # At 1.5 GHz, lambda_max=40cm -> domain_x=0.6m
    domain_x: float = 0.6
    domain_y: float = 1.5
    domain_z: float = 0.003   # Matched to dx for cubic cells

    # Domain Height Limits (Railway Literature)
    # Typical GPR antenna: 30-100cm above ballast surface
    # Max realistic height: subgrade(0.5) + formation(0.1) + ballast(0.45) + antenna(0.5) + buffer(0.1) = 1.65m
    max_domain_y: float = 1.65  # Hard limit from literature

    # Spatial discretization — Khosravi Largani et al. (2025) FDTD guideline:
    #   dx <= lambda_min / 10,  lambda_min = c / (fmax * sqrt(er_max))
    # At fc=1.5 GHz, fmax=2.317 GHz:
    #   er=14.4 (wet fouling max) -> need dx <= 3.41 mm -> 3 mm for physical perfection
    dx: float = 0.003
    dy: float = 0.003
    dz: float = 0.003
    
    # Time window — Mbubia Tchoua et al. (2026): 20 ns captures full ballast column + subgrade interface
    time_window: float = 2.0e-8

    # Waveform / antenna
    center_freq: float = 1.5e9
    tx_x: float = 0.300 # Center of 0.6m domain
    rx_x: float = 0.350 # 5cm offset (Bi-static)
    tx_rx_z: float = 0.0015  # centre of 3 mm domain_z
    add_waveform: bool = True
    add_source: bool = True
    add_geometry_view: bool = False
    add_sleepers: bool = False
    subgrade_wet: bool = False  # True: saturated subgrade εr=21 (Xie et al. 2010), False: εr=10

    # PML absorbing boundary (Benedetto et al. 2016): 10 cells on all sides
    pml_layers: int = 10

    # Multi-Offset Antenna Configuration (Roncoroni et al. 2025)
    # Allows for AVO (Amplitude-Versus-Offset) analysis.
    num_receivers: int = 1         # 1 = Single Offset, >1 = Linear Array
    receiver_spacing: float = 0.05 # Distance between receivers in meters
    monostatic: bool = False       # True: RX co-located with TX (single-antenna)

    @classmethod
    def create_physically_perfect(cls, center_freq_hz: float, er_max: float = 14.4, **kwargs):
        """
        Create a config instance with dimensions and resolution automatically scaled
        to meet IEEE 2025 (Khosravi Largani et al.) research guidelines.
        """
        from .physics import get_fdtd_recommendations
        recs = get_fdtd_recommendations(center_freq_hz, er_max=er_max)
        
        # Calculate antenna position (Center of new domain)
        tx_x = recs['domain_x'] / 2.0
        rx_x = tx_x + 0.05 # 5cm offset
        
        # Calculate total domain height needed with PML safety margins
        # Layer stack: subgrade + formation + max ballast
        # Antenna: ballast_top + antenna_clearance
        # PML: 10 cells at top = 10 * dx
        # Safety: antenna must be 15+ cells from PML = 15 * dx
        # Extra: 20% safety buffer for numerical stability
        antenna_clearance = recs['antenna_height']
        pml_thickness = 10 * recs['dx']          # PML cells at boundary
        pml_clearance = 15 * recs['dx']          # Minimum clearance from PML
        # Use actual min/max thicknesses from config
        subgrade_h = kwargs.get('subgrade_thickness', 0.20)
        formation_h = kwargs.get('formation_thickness', 0.10)
        max_ballast_h = kwargs.get('max_ballast_thickness', 0.55)
        layer_height = subgrade_h + formation_h + max_ballast_h
        # Domain must accommodate: layers + antenna clearance + air buffer for PML and safety
        # Air buffer = PML thickness + PML clearance + extra safety = 0.132 + 0.198 + 1.0 = 1.33m (use 1.5m)
        air_buffer = 1.5
        domain_y = layer_height + antenna_clearance + air_buffer
        
        return cls(
            center_freq=center_freq_hz,
            domain_x=recs['domain_x'],
            domain_y=domain_y,
            max_domain_y=domain_y + 0.5,
            domain_z=recs['dx'],
            dx=recs['dx'],
            dy=recs['dx'],
            dz=recs['dx'],
            tx_x=tx_x,
            rx_x=rx_x,
            tx_rx_z=recs['dx'] / 2.0,
            antenna_clearance_above_ballast=antenna_clearance,
            **kwargs
        )




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
    # Minimum surface-to-surface gap between rocks (metres).
    # Inspired by jagua-rs min_item_separation. 0.0 = rocks may touch.
    # Realistic ballast: 0.002–0.005 m (2–5 mm).
    rock_min_gap: float = 0.0
    # Particle Size Distribution type for radius sampling.
    # Inspired by ParticlePack/Distribution.cs (MosGeo, Geophysics 2019).
    # Options: "uniform" (flat, default), "en13450" (EN 13450 railway ballast), "fuller" (max density)
    rock_psd_type: str = "uniform"
    enable_rock_caching: bool = False  # If False, always generate fresh rocks

    
    # Moisture & Fouling Props
    moisture_min: float = 0.0
    moisture_max: float = 0.3
    fractal_dimension: float = 1.5
    
    # Fouling Distribution Parameters — 3-zone model (Benedetto et al. 2016)
    fouling_settled_fraction: float = 0.7   # kept for back-compat (= dense_fraction below)
    fouling_dense_fraction: float = 0.5     # zone 1: solid dense fouling (bal_foul)
    fouling_granular_fraction: float = 0.3  # zone 2: granular transition (bal_foul_granular)
    fouling_particle_size_min: float = 0.002  # 2mm
    fouling_particle_size_max: float = 0.008  # 8mm

    # Fouling PSD type: "standard" (coarser, 30% P200) or "a4" (Benedetto et al. 2016, 84.7% P200)
    fouling_psd_type: str = "standard"

    # Rock gravity settlement (Benedetto et al. 2016 vertical compaction)
    rock_gravity_settle: bool = True
    
    # Antenna Placement (Namdari et al. 2025: Radar height influences resolution/sensitivity)
    antenna_clearance_above_ballast: float = 0.50  # Default
    min_antenna_clearance: float = 0.30
    max_antenna_clearance: float = 0.80
    antenna_rock_clearance: float = 0.02  # 2cm minimum clearance from rocks
    
    # Angular Ballast (Realistic sharp rocks via triangulation - gprMax-Designer)
    angular_rocks: bool = False  # If True, rocks are rendered as polygons instead of cylinders
    rock_sides: int = 6         # Number of sides for the angular rock approximation (6=Hexagon)


    
    # Rock Z-Extent (Extrusion)
    rock_z_start: float = 0.0
    rock_z_end: float = 0.004  # full z extent = domain_z (2-D simulation)
    
    # Rock Packing Strategy
    rock_packing_algorithm: str = "circlify"  # "random", "poisson", "front_chain", "physics", "triangle"
    wang_tile_size: float = 0.1  # Size of Wang tiles in meters
    
    # Ballast/subgrade nominal depths
    min_ballast_thickness: float = 0.35  # More realistic range
    max_ballast_thickness: float = 0.55  # Max: subgrade(0.2) + formation(0.1) + ballast(0.55) = 0.85m 

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
    # Stratified Fouling — Bianchini Ciampoli et al. (2019)
    # Top and bottom halves of the ballast column get independent PVC values.
    # Only active when granular_mode=True.
    # ============================================================
    stratified_fouling: bool = False
    
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

    base_seed: Optional[int] = None


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

        self._check_fdtd_compliance()

    def _check_fdtd_compliance(self) -> None:
        """Warn when FDTD discretization or domain-size guidelines are violated.

        Guidelines from Khosravi Largani et al. (2025), IEEE GRSL:
          Rule 1 (discretization): dx <= lambda_min / 10
                  lambda_min = c / (fmax * sqrt(er_max))
                  fmax = 1.545 * center_freq  (Wang 2015 Ricker ratio)
          Rule 2 (domain width):  domain_x >= 1.5 * lambda_max
                  lambda_max = c / (fmin * sqrt(er_primary))
                  fmin = 0.455 * center_freq
        """
        import warnings, math
        C = 3e8
        fmax = self.center_freq * 1.545   # Wang (2015)
        fmin = self.center_freq * 0.455

        # Rule 1 — worst-case permittivity is wet fouling or subgrade (whichever is higher)
        er_max = max(self.bal_foul_eps_max * self.wet_eps_factor_max, 10.0)
        lam_min = C / (fmax * math.sqrt(er_max))
        dx_req  = lam_min / 10
        if self.dx > dx_req * 1.01:
            warnings.warn(
                f"FDTD Rule 1: dx={self.dx*1000:.1f}mm exceeds lambda_min/10={dx_req*1000:.2f}mm "
                f"(er_max={er_max:.1f}, fmax={fmax/1e9:.2f}GHz). "
                f"Reduce dx to <={dx_req*1000:.1f}mm for strict compliance.",
                UserWarning, stacklevel=3,
            )

        # Rule 2 — ballast rock is the primary propagation medium
        er_primary = self.bal_rock_eps
        lam_max   = C / (fmin * math.sqrt(er_primary))
        dom_req   = 1.5 * lam_max
        if self.domain_x < dom_req * 0.99:
            warnings.warn(
                f"FDTD Rule 2: domain_x={self.domain_x:.3f}m < 1.5*lambda_max={dom_req:.3f}m "
                f"(er_ballast={er_primary}, fmin={fmin/1e9:.3f}GHz). "
                f"Increase domain_x to >={dom_req:.3f}m.",
                UserWarning, stacklevel=3,
            )
            
    
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

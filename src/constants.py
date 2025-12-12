"""
Physical and domain constants for Railway GPR simulation.

References:
- Selig & Waters (1994): Track Geotechnology and Substructure Management
- Railway ballast specifications (20-60mm aggregate)
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class PhysicalConstants:
    """Railway GPR physical constants and specifications."""
    
    # Unit Conversions
    MM_TO_M: float = 1000.0
    M_TO_MM: float = 0.001
    
    # Ballast Layer Specifications (Selig & Waters, 1994)
    MIN_BALLAST_THICKNESS: float = 0.35  # meters
    MAX_BALLAST_THICKNESS: float = 0.55  # meters
    STANDARD_BALLAST_THICKNESS: float = 0.45  # meters
    
    # Other Layer Defaults
    FORMATION_THICKNESS: float = 0.10  # meters
    SUBGRADE_THICKNESS: float = 0.50  # meters
    
    # Laboratory Analysis
    STANDARD_LAYER_HEIGHT: float = 0.15  # meters (15cm sampling)
    
    # Sieve Standards (ASTM)
    SIEVE_NO4: float = 4.75   # mm (No. 4 sieve)
    SIEVE_NO10: float = 2.00  # mm
    SIEVE_NO40: float = 0.425  # mm
    SIEVE_NO200: float = 0.075  # mm (fines threshold)
    
    # Rock Aggregate Specifications
    MIN_ROCK_RADIUS: float = 0.02   # meters (20mm)
    MAX_ROCK_RADIUS: float = 0.032  # meters (32mm)
    
    # Antenna Configuration
    ANTENNA_CLEARANCE: float = 0.50  # meters above ballast
    MIN_ANTENNA_CLEARANCE: float = 0.02  # meters from rocks
    
    # Fouling Distribution
    FOULING_SETTLED_FRACTION: float = 0.7  # 70% settles to bottom
    
    # Domain Validation
    EPSILON: float = 1e-9  # Numerical tolerance
    DEFAULT_DT: float = 1e-10 # Default time step if missing
    
    # Simulation Heuristics
    FOULING_PARTICLE_COUNT_MULTIPLIER: int = 200 # particles per fractional PVC
    DEFAULT_ROCK_LAYERS: int = 10 # Default layers for packing

@dataclass(frozen=True)
class MaterialConstants:
    """Standard identifiers for scene materials."""
    AIR: str = "free_space"
    SUBGRADE: str = "subgrade"
    FORMATION: str = "formation"
    BALLAST_ROCK: str = "bal_rock"
    FOULING: str = "bal_foul_granular"
    SLEEPER: str = "sleeper"
    RAIL: str = "rail"
    
    # Defaults (Dielectric, Conductivity)
    AIR_PROPS: tuple = (1.0, 0.0)
    SUBGRADE_PROPS: tuple = (10.0, 0.02) # Approx
    FORMATION_PROPS: tuple = (10.0, 0.03) # S&W
    BALLAST_ROCK_PROPS: tuple = (5.5, 0.001) # Granite/Limestone
    FOULING_BASE_PROPS: tuple = (5.0, 0.01) # Dry clay/fines

@dataclass(frozen=True)
class SignalConstants:
    """Constants for GPR signal processing and feature extraction."""
    # Frequency Bands (Hz)
    FREQ_LOW_CUTOFF: float = 5e8    # 500 MHz
    FREQ_MID_CUTOFF: float = 1.5e9  # 1.5 GHz
    
    # STFT Parameters
    STFT_NPERSEG: int = 64
    STFT_NOVERLAP: int = 32
    
    # Feature Extraction
    DEFAULT_SLICE_COUNT: int = 14
    DEFAULT_GRID_SIZE: int = 160
    GRID_ROWS: int = 16
    GRID_COLS: int = 10
    
    # Numerical Stability
    LOG_EPSILON: float = 1e-12


@dataclass(frozen=True)
class PackingConstants:
    """Constants for rock packing algorithms."""
    # Defaults
    DEFAULT_FILL_RATIO: float = 0.6
    MAX_ATTEMPTS: int = 1000
    
    # Algorithm Specifics
    POISSON_K_ATTEMPTS: int = 30
    PHYSICS_ITERATIONS: int = 200
    PHYSICS_DAMPING: float = 0.5
    
    # Wang Tiles
    TILE_SIZE: float = 0.1  # meters
    WANG_SEED_MULTIPLIER: int = 12345
    
    # Edge Patterns (Margins in meters)
    MARGIN_EMPTY: float = 0.025
    MARGIN_SPARSE: float = 0.018
    MARGIN_MEDIUM: float = 0.012
    MARGIN_DENSE: float = 0.006

@dataclass(frozen=True)
class PhysicsConstants:
    """Constants for physics calculations and fouling classification."""
    # Fouling Index Thresholds (Selig & Waters, 1994)
    FI_CLEAN_THRESHOLD: float = 10.0
    FI_MODERATELY_FOULED_THRESHOLD: float = 20.0
    FI_FOULED_THRESHOLD: float = 40.0
    
    # Material Properties (Specific Gravities)
    DEFAULT_POROSITY: float = 0.4  # Ballast void fraction
    DEFAULT_BALLAST_DENSITY: float = 2.6  # Gs_b (granite/limestone)
    DEFAULT_FOULING_DENSITY: float = 2.6  # Gs_f (clay/mineral fines)
    
    # Topp's Model Coefficients (Topp et al., 1980)
    # Relates soil moisture to dielectric constant
    TOPP_C0: float = 3.03
    TOPP_C1: float = 9.3
    TOPP_C2: float = 146.0
    TOPP_C3: float = -76.7
    
    # Numerical Thresholds
    ZERO_EPSILON: float = 1e-9  # For near-zero checks

# Singleton instances
PC = PhysicalConstants()
MC = MaterialConstants()
SC = SignalConstants()
PAC = PackingConstants()
PHC = PhysicsConstants()

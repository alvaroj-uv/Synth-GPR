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
    M_TO_MM: float = 1000.0
    MM_TO_M: float = 0.001
    
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
    FOULING: str = "bal_foul_granular"       # granular / partially fouled
    FOULING_DENSE: str = "bal_foul"          # dense settled fouling (zone 1)
    SLEEPER: str = "sleeper"
    RAIL: str = "rail"
    
    # ── SINGLE SOURCE OF TRUTH for base material EM properties ──────────────
    # (relative_permittivity, conductivity_S_per_m). Every other place that
    # needs a default material value MUST reference these — do NOT redefine the
    # numbers elsewhere (config defaults point here; there is no separate
    # material table). Changing a value here changes it everywhere.
    #
    # Sources:
    #   Tosti & Benedetto (2018) NDT&E Int. 93, 131-140      — clean ballast
    #   Benedetto et al. (2017) Constr. Build. Mater.         — fouled ballast
    #   Shang et al. (2021) Sensors PMC8539047                — fully fouled
    #   PMC9003199 (2022) state-of-the-art review             — subgrade
    AIR_PROPS: tuple = (1.0, 0.0)
    SUBGRADE_PROPS: tuple = (8.0, 0.020)      # dry/compact railway formation (PMC9003199)
    SUBGRADE_EPS_SAT: float = 21.0            # saturated — Xie et al. (2010)
    FORMATION_PROPS: tuple = (10.0, 0.03)     # S&W
    BALLAST_ROCK_PROPS: tuple = (4.0, 0.001)  # clean dry granite/limestone, 400 MHz (Tosti 2018)
    FOULING_BASE_PROPS: tuple = (5.0, 0.005)  # lightly fouled ~10-24% (Benedetto 2017)
    FOULING_DENSE_PROPS: tuple = (6.5, 0.012) # fully fouled dry fines (Shang 2021)

    # Ballast scene materials (referenced by config + the pymunk ballast packer)
    CLEAN_BALLAST_PROPS: tuple    = (4.0,  0.001)  # Tosti & Benedetto (2018)
    FOULED_BALLAST_PROPS: tuple   = (5.0,  0.005)  # Benedetto et al. (2017)
    HF_BALLAST_PROPS: tuple       = (6.5,  0.012)  # Shang et al. (2021) fully fouled
    SUBGRADE_SOIL_PROPS: tuple    = (8.0,  0.020)  # PMC9003199 dry railway subgrade

    # ── CRIM ballast mixing model (packed-rock scenes + CRIM inversion) ─────
    # Used by physics.ballast_crim to map (fines fill, saturation) → (eps, σ).
    # NOTE: rock eps here is 6.1 (Brancadoro aggregate grains, matched-pair
    # validated 2026-06-30) while BALLAST_ROCK_PROPS above keeps 4.0 (Tosti
    # bulk value used by the 2D dataset pipeline). These describe different
    # things (grain vs homogenised bulk) — do not "unify" them blindly.
    # Hull anchors (zero tuning): (f=0,Sw=0)→eps 3.43 ≈ pit-ID11 clean 3.45;
    # (1,0)→4.80 ≈ Benedetto dry cap; (1,1)→12.5 ≈ field fouled 11.3–12.
    CRIM_ROCK_EPS: float = 6.1        # granite grains (Brancadoro)
    CRIM_FINES_EPS: float = 5.5       # mineral fines (Santamarina 2002)
    CRIM_WATER_EPS: float = 81.0      # free water
    CRIM_VOID_FRACTION: float = 0.42  # ballast void fraction (Brancadoro volumetric)
    CRIM_PACK_POROSITY: float = 0.40  # fines-pack internal porosity ('granular' zone)

@dataclass(frozen=True)
class SignalConstants:
    """Constants for GPR signal processing and feature extraction."""
    # Frequency Bands (Hz)
    FREQ_LOW_CUTOFF: float = 5e8    # 500 MHz
    FREQ_MID_CUTOFF: float = 1.5e9  # 1.5 GHz
    
    # STFT Parameters (legacy, in samples — still used by visualization scripts)
    STFT_NPERSEG: int = 64
    STFT_NOVERLAP: int = 32

    # Time-domain ballast/coda gate (ns) for windowed indicators.
    # LEGACY absolute gate — kept for visualization scripts only; the feature
    # extractor now uses the peak-relative gate below.
    # Windowed StAb / Hilbert-area / CrossNum / InflecNum — Li et al. (2023),
    # Shapovalov et al. (2026).
    CODA_WINDOW_NS: tuple = (6.0, 16.0)
    NS_PER_SEC: float = 1e9

    # ── Feature-extraction v2: physical units + peak-relative gating ────────
    # Version stamp emitted as meta_feature_version in every feature row so a
    # parquet records which feature definitions produced it (guards against
    # silent metric drift — see the dt/freq mis-scaling incident).
    # v2: physical units + peak-relative gate. v3: coda-first suite (coda_*) +
    # attenuation family (att_*), legacy whole-trace grid/slices/deciles off by
    # default (they encode the direct pulse, i.e. the antenna, not the ground).
    FEATURE_VERSION: int = 3
    # Wavelet widths in physical time (ns). At dt=0.1 ns (the REAL corpus time
    # base) these equal the legacy sample widths (2,4,8,16,32), so real-data
    # wavelet features are unchanged; synthetic data (dt≈0.0311 ns) now measures
    # the SAME physical scales instead of 3.2x smaller ones.
    WAVELET_WIDTHS_NS: tuple = (0.2, 0.4, 0.8, 1.6, 3.2)
    # STFT window in physical time (legacy 64 samples @ 0.1 ns = 6.4 ns).
    STFT_NPERSEG_NS: float = 6.4
    # Spectral band edges as fractions of the source centre frequency
    # (low < BAND_LOW_FRAC*fc <= mid < BAND_HIGH_FRAC*fc <= high). Replaces the
    # absolute 500 MHz / 1.5 GHz cutoffs, which are degenerate for 400 MHz data.
    BAND_LOW_FRAC: float = 0.75
    BAND_HIGH_FRAC: float = 1.5
    # Peak-relative coda gate for win_* features: start this long after the
    # direct-pulse peak (≈ one 400 MHz ricker period clears the main lobe), for
    # this length (16 ns = the common sim/real coda overlap used by the aligned
    # sim2real pipeline).
    CODA_GATE_START_AFTER_PEAK_NS: float = 4.5
    CODA_GATE_LENGTH_NS: float = 16.0

    # Energy-integration curve fractions (time-domain rolloff) — Li et al. (2023)
    ENERGY_CURVE_FRACTIONS: tuple = (0.25, 0.50, 0.75, 0.85)

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
    # Fouling Index Thresholds (Selig & Waters, 1994) — 5-class scheme
    FI_CLEAN_THRESHOLD: float = 1.0           # C  → MC boundary
    FI_MODERATELY_CLEAN_THRESHOLD: float = 10.0  # MC → MF boundary
    FI_MODERATELY_FOULED_THRESHOLD: float = 20.0  # MF → F  boundary
    FI_FOULED_THRESHOLD: float = 40.0         # F  → HF boundary

    # ========== SINGLE SOURCE OF TRUTH: MATERIAL PROPERTIES ==========
    # All material densities defined here. NEVER hardcode elsewhere.
    # Reference: Koohminski et al. (2025) Table 1

    # Lab Analysis Densities (Specific Gravities for Rb-f calculation)
    BALLAST_DENSITY_LABANALYSIS: float = 2.72     # Gs_b — crushed granite/limestone
    FOULING_DENSITY_LABANALYSIS: float = 2.58     # Gs_f — clay fouling

    # Peplinski Model Densities (Dielectric permittivity modeling)
    FOULING_BULK_DENSITY_PEPLINSKI: float = 1.9   # g/cm³ (for dielectric calculation)
    FOULING_SAND_DENSITY_PEPLINSKI: float = 2.66  # g/cm³ (sand component in Peplinski)

    # Physics Simulation Density (pymunk/gravity settling)
    BALLAST_DENSITY_PYMUNK: float = 1.55          # g/cm³ (for physics engine mass/weight)

    # Porosity & Void Properties
    DEFAULT_POROSITY: float = 0.4                 # Ballast void fraction

    # Legacy aliases (for backward compatibility, map to single source)
    DEFAULT_BALLAST_DENSITY: float = BALLAST_DENSITY_LABANALYSIS
    DEFAULT_FOULING_DENSITY: float = FOULING_DENSITY_LABANALYSIS
    
    # Topp's Model Coefficients (Topp et al., 1980)
    # Relates soil moisture to dielectric constant
    TOPP_C0: float = 3.03
    TOPP_C1: float = 9.3
    TOPP_C2: float = 146.0
    TOPP_C3: float = -76.7
    
    # Numerical Thresholds
    ZERO_EPSILON: float = 1e-9  # For near-zero checks

    # ========== PHYSICS & SIMULATION PARAMETERS ==========
    # Gravity Settling (pymunk-based ballast compaction)
    GRAVITY_SETTLE_TIME_STEP: float = 0.002         # 2 mm per settling step
    GRAVITY_SETTLE_DAMPING: float = 0.5             # Energy dissipation (from config.py)

    # Rock Growth/Packing Algorithms
    CIRCLE_GROW_STEP: float = 0.001                 # 1 mm per grow iteration
    PACKING_TIMEOUT_PER_START: float = 2.0          # 2 seconds per random start

    # Synthetic LDCP profiler — quasi-static point resistance (MPa)
    # Values calibrated to P.A.N.D.A. field data ranges (Benz Navarrete et al. 2022)
    LDCP_STEP_M: float = 0.001           # 1 mm depth step
    LDCP_QS_ROCK: float = 30.0           # granite/limestone aggregate
    LDCP_QS_FOULING: float = 2.0         # clay/fines (granular or dense)
    LDCP_QS_SUBGRADE: float = 8.0        # compacted subgrade
    LDCP_QS_FORMATION: float = 15.0      # sub-ballast formation
    LDCP_QS_VOID: float = 0.5            # open pore space
    LDCP_FH_FACTOR_CLAY: float = 1.5     # F factor: FI = %FH / F (clay fouling, Rojas-Vivanco 2025 eq. 9) — DEPRECATED for labeling, see fi_from_fouling_height

    # %FH -> FI quadratic (Rojas-Vivanco 2025, theoretical curves; matches the
    # exact equation used to label the REAL pandoscope data). FI = a*FH^2 + b*FH + c.
    # Three compaction states; pick by ballast porosity. This REPLACES the linear
    # FH/1.5 so synthetic height-FI is directly comparable to the real FI labels.
    FH_FI_LOOSE:   tuple = (-0.0013, 0.5570, 0.4170)   # loose ballast (phi high)
    FH_FI_MEDIUM:  tuple = (-0.0017, 0.6311, 0.4933)   # medium — used to label real data
    FH_FI_COMPACT: tuple = (-0.0022, 0.7248, 0.6753)   # compacted ballast (phi low)

def archie_sigma(
    porosity: float,
    saturation: float,
    rho_w: float = 40.0,
    a: float = 0.88,
    m: float = 1.37,
    n: float = 2.0,
) -> float:
    """Compute electrical conductivity (S/m) via Archie's law.

    σ = (σ_w × Φ^m × S_w^n) / a

    Args:
        porosity:   volumetric void fraction Φ (0–1)
        saturation: water saturation S_w (0–1)
        rho_w:      pore-water resistivity (Ωm); default 40 Ωm (fresh groundwater)
        a:          tortuosity factor (Koyan 2020 / Schön 1998: 0.88)
        m:          cementation exponent (0.88 / 1.37 for unconsolidated sand)
        n:          saturation exponent (standard: 2.0)

    Returns:
        σ in S/m

    Reference: Archie (1942); Koyan & Tronicke (2020) used ρ_w=25 Ωm, a=0.88, m=1.37.
    For clay-rich layers Archie underestimates σ (no surface conductance term);
    use explicit sigma override in those cases.
    """
    sigma_w = 1.0 / rho_w
    return sigma_w * (porosity ** m) * (saturation ** n) / a


# Singleton instances
PC = PhysicalConstants()
MC = MaterialConstants()
SC = SignalConstants()
PAC = PackingConstants()
PHC = PhysicsConstants()

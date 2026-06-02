"""
Physics and Classification Formulas.

This module contains domain-specific calculations and classification logic
for GPR simulation properties, separating them from configuration data.
"""

# Standard library imports
import math
from typing import Literal

# Local imports
from .constants import PHC


def classify_pvc(pvc_value: float, porosity: float = PHC.DEFAULT_POROSITY) -> str:
    """
    Classify ballast fouling based on input PVC, converting to FI first.
    
    WHY TWO-STEP CONVERSION:
    PVC (Percentage Void Contamination) is what we *measure* in simulations
    (volume of voids filled), but FI (Fouling Index) is the *standard* used 
    in civil engineering literature (Selig & Waters, 1994). We convert to FI
    to align with industry classification thresholds.
    
    Note:
        To achieve 'HF' (FI >= 40), you typically need PVC > 85% 
        (assuming std densities and porosity=0.4).
    
    Args:
        pvc_value: Percentage Void Contamination (0-100)
        porosity: Void fraction (0-1). Defaults to 0.4.
        
    Returns:
        Class code based on calculated FI.
    """
    fi_value = convert_pvc_to_fi(pvc_value, porosity=porosity)
    return classify_fouling_index(fi_value)


def compute_fouling_index(rock_thickness: float, fouling_thickness: float) -> float:
    """
    Compute Fouling Index (FI) as percentage of fouling in total ballast depth.
    
    WHY THIS APPROACH:
    This is a simplified geometric approximation used when we have explicit
    layer thicknesses. Less accurate than mass-based FI but computationally
    cheaper for quick estimates.
    """
    total = rock_thickness + fouling_thickness
    if total <= PHC.ZERO_EPSILON:
        return 0.0
    return (fouling_thickness / total) * 100.0


def convert_pvc_to_fi(
    pvc: float, 
    porosity: float = PHC.DEFAULT_POROSITY, 
    Gs_b: float = PHC.DEFAULT_BALLAST_DENSITY, 
    Gs_f: float = PHC.DEFAULT_FOULING_DENSITY
) -> float:
    """
    Convert Percentage Void Contamination (PVC) to Fouling Index (FI).
    
    WHY THIS CONVERSION MATTERS:
    PVC is volumetric (easy to measure in CT scans or simulations), but
    FI is mass-based (the civil engineering standard). Since ballast and
    fouling have different densities, a 10% volume increase doesn't mean
    10% mass increase. This formula accounts for specific gravities.
    
    Physics:
        PVC is Volumetric % of Voids filled.
        FI is Mass % of Total Sample (Selig & Waters).
        
    Formula:
        V_foul = (PVC/100) * porosity
        V_rock = 1 - porosity
        
        Mass_f = V_foul * Gs_f
        Mass_b = V_rock * Gs_b
        
        FI = (Mass_f / (Mass_f + Mass_b)) * 100
        
    Args:
        pvc: Percentage Void Contamination (0-100)
        porosity: Void fraction of clean ballast (default 0.4 for loose packing)
        Gs_b: Specific Gravity of Ballast (default 2.6 granite/limestone)
        Gs_f: Specific Gravity of Fouling (default 2.6, similar to rock if mineral)
        
    Returns:
        Fouling Index (0-100)
    """
    if pvc <= 0:
        return 0.0
    if porosity <= 0:
        return 0.0

    pvc = min(pvc, 100.0)
    porosity = min(porosity, 1.0)

    v_foul = (pvc / 100.0) * porosity
    v_rock = 1.0 - porosity
    
    # Note: Water density cancels out in the mass ratio calculation
    m_foul = v_foul * Gs_f
    m_rock = v_rock * Gs_b
    
    total_mass = m_foul + m_rock
    if total_mass <= PHC.ZERO_EPSILON:
        return 0.0
        
    fi = (m_foul / total_mass) * 100.0
    return fi


def inverse_convert_fi_to_pvc(
    target_fi: float, 
    porosity: float = PHC.DEFAULT_POROSITY, 
    Gs_b: float = PHC.DEFAULT_BALLAST_DENSITY, 
    Gs_f: float = PHC.DEFAULT_FOULING_DENSITY
) -> float:
    """
    Calculate required PVC (Volume %) to achieve a target FI (Mass %).
    
    WHY INVERSE CONVERSION:
    ML dataset generation requires target-driven generation. Given a desired
    label (e.g., "Heavily Fouled" = FI 40%), we need to know what PVC to
    use in the simulation. This is the mathematical inverse of the forward
    conversion.
    
    Formula derived from solving FI = Mf / (Mf + Mb):
        PVC = ((1-phi)/phi) * (Gs_b/Gs_f) * (FI / (100-FI)) * 100
        
    Args:
        target_fi: Target Fouling Index (0-100)
        porosity, Gs_b, Gs_f: Material properties (must match forward transform)
        
    Returns:
        Required PVC percentage (0-100). Returns >100 if target is physically 
        impossible with given porosity.
    """
    if target_fi <= 0:
        return 0.0
    if target_fi >= 100:
        # Impossible: means 0% rock
        return 999.0
        
    fi_ratio = target_fi / 100.0
    
    mass_ratio = fi_ratio / (1.0 - fi_ratio)
    
    # Convert mass ratio to volume ratio using specific gravities
    volume_ratio = mass_ratio * (Gs_b / Gs_f)
    
    if porosity <= PHC.ZERO_EPSILON: 
        return 0.0
        
    pvc_fraction = volume_ratio * (1.0 - porosity) / porosity
    return pvc_fraction * 100.0


def classify_fouling_index(fi: float) -> Literal["C", "MC", "MF", "F", "HF"]:
    """
    Classify fouling based on Fouling Index (FI).

    WHY THESE THRESHOLDS:
    5-class scheme from Selig & Waters (1994), matching the industry standard
    used in GPR + ML studies (e.g., Rojas-Vivanco et al. 2025, Transp. Geotech.).
    Splitting C from MC matters: the C/MC boundary (FI=1%) is where the
    confusion matrix in the literature shows the most misclassification.

    Classification (Selig & Waters, 1994):
        - Clean (C):               FI < 1%
        - Moderately Clean (MC):   1%  <= FI < 10%
        - Moderately Fouled (MF):  10% <= FI < 20%
        - Fouled (F):              20% <= FI < 40%
        - Highly Fouled (HF):      FI >= 40%

    Args:
        fi: Fouling Index (mass percentage)

    Returns:
        Classification code: "C", "MC", "MF", "F", or "HF"
    """
    if fi < PHC.FI_CLEAN_THRESHOLD:
        return "C"
    elif fi < PHC.FI_MODERATELY_CLEAN_THRESHOLD:
        return "MC"
    elif fi < PHC.FI_MODERATELY_FOULED_THRESHOLD:
        return "MF"
    elif fi < PHC.FI_FOULED_THRESHOLD:
        return "F"
    else:
        return "HF"


def topp_mixing_model(theta: float) -> float:
    """
    Topp's empirical equation for soil dielectric based on water content.
    
    WHY TOPP'S MODEL:
    GPR signal propagation depends on dielectric constant, which changes
    with moisture. Topp's polynomial (1980) is the geophysics standard for
    mineral soils, derived from lab measurements across soil types.
    
    Ref: Topp et al (1980). "Electromagnetic determination of soil water content"
    
    Args:
        theta: Volumetric water content (0.0 - 1.0)
        
    Returns:
        Relative dielectric constant (epsilon_r)
    """
    # Clamp to realistic soil moisture range
    theta = max(0.0, min(theta, 1.0))
    
    # Topp's empirical polynomial
    e_r = (PHC.TOPP_C0
           + PHC.TOPP_C1 * theta
           + PHC.TOPP_C2 * theta**2
           + PHC.TOPP_C3 * theta**3)
    return max(1.0, min(e_r, 81.0))


def fmt(val: float) -> str:
    """
    Format float to 5 significant figures for file output.
    
    WHY 5 SIGNIFICANT FIGURES:
    gprMax input files don't need full precision (noisy anyway), but we need
    enough digits to avoid truncation errors in material properties that
    affect wave speed calculations.
    """
    if abs(val) < PHC.ZERO_EPSILON:
        return "0.0"
    return f"{val:.5g}"


def _log_linear_interpolate(
    target_diameter: float, 
    diameter_lower: float, percent_passing_lower: float, 
    diameter_upper: float, percent_passing_upper: float
) -> float:
    """
    Log-Linear Interpolation for Particle Size Distribution (PSD).
    
    WHY LOG-LINEAR:
    Particle size data spans orders of magnitude (clay = 0.001mm, gravel = 10mm).
    Linear interpolation would be terrible. Semi-log (log particle size,
    linear % passing) is the geotechnical standard and matches how soil
    gradation curves behave physically.
    
    Formula:
        Px = P1 + (P2 - P1) * (log(dx) - log(d1)) / (log(d2) - log(d1))
    
    Args:
        target_diameter: Target diameter to interpolate at.
        diameter_lower, percent_passing_lower: First bounding point (diameter, % passing).
        diameter_upper, percent_passing_upper: Second bounding point (diameter, % passing).
    
    Returns:
        Interpolated Percent Passing (Px).
    """
    if target_diameter <= 0 or diameter_lower <= 0 or diameter_upper <= 0:
        return 0.0
        
    if abs(diameter_upper - diameter_lower) < PHC.ZERO_EPSILON:
        return percent_passing_lower
        
    log_target = math.log10(target_diameter)
    log_lower = math.log10(diameter_lower)
    log_upper = math.log10(diameter_upper)
    
    slope = (percent_passing_upper - percent_passing_lower) / (log_upper - log_lower)
    interpolated_percent = percent_passing_lower + slope * (log_target - log_lower)
    
    return max(0.0, min(100.0, interpolated_percent))


def circle_strip_intersection(cx: float, cy: float, radius: float,
                               y_min: float, y_max: float) -> float:
    """Area of a circle intersected with a horizontal strip [y_min, y_max]."""
    return (_circular_segment_area_below(cx, cy, radius, y_max) -
            _circular_segment_area_below(cx, cy, radius, y_min))


def _circular_segment_area_below(cx: float, cy: float, radius: float, line_y: float) -> float:
    """Area of a circle below the horizontal line y = line_y."""
    import math
    d = line_y - cy
    if d >= radius:
        return math.pi * radius ** 2
    if d <= -radius:
        return 0.0
    return radius ** 2 * (math.pi / 2 + math.asin(d / radius)) + d * math.sqrt(radius ** 2 - d ** 2)


def crim_bulk_eps(
    v_rock: float, eps_rock: float,
    v_fines: float, eps_fines: float,
    v_water: float, eps_water: float,
    v_air: float,
) -> float:
    """CRIM bulk dielectric constant (Barrett et al. 2019, Eq. 5).

    sqrt(eps_bulk) = sum_i V_i * sqrt(eps_i)   (Complex Refractive Index Method)
    """
    sqrt_eps = (v_rock  * math.sqrt(max(eps_rock,  1.0))
              + v_fines * math.sqrt(max(eps_fines, 1.0))
              + v_water * math.sqrt(max(eps_water, 1.0))
              + v_air   * 1.0)
    return max(1.0, sqrt_eps ** 2)


def surface_reflectivity_R(eps_above: float, eps_below: float) -> float:
    """Normal-incidence surface reflectivity (Barrett et al. 2019, Eq. 7).

    R = ((sqrt(eps1) - sqrt(eps2)) / (sqrt(eps1) + sqrt(eps2)))^2
    """
    a = math.sqrt(max(eps_above, 1e-9))
    b = math.sqrt(max(eps_below, 1e-9))
    denom = a + b
    if denom < 1e-12:
        return 0.0
    return ((a - b) / denom) ** 2


def attenuation_factor_npm(freq_hz: float, eps_real: float, sigma_eff: float) -> float:
    """EM signal attenuation alpha in Np/m (Barrett et al. 2019, Eq. 8).

    alpha = omega * sqrt(mu0*eps0*eps' / 2 * (sqrt(1 + tan^2(delta)) - 1))
    where tan(delta) = eps'' / eps',  eps'' = sigma / (omega * eps0)
    """
    eps0  = 8.854e-12
    mu0   = 4.0 * math.pi * 1e-7
    omega = 2.0 * math.pi * freq_hz
    eps_imag  = sigma_eff / (omega * eps0)
    tan_delta = eps_imag / max(eps_real, 1e-9)
    inner = mu0 * eps0 * eps_real / 2.0 * (math.sqrt(1.0 + tan_delta ** 2) - 1.0)
    return omega * math.sqrt(max(inner, 0.0))


def crim_fouling_eps(
    moisture: float,
    pvc: float,
    zone: str = 'granular',
    eps_mineral: float = 5.5,
    eps_water: float = 81.0,
) -> tuple:
    """CRIM-derived bulk εr and σ for a fouling particle (three-phase mix).

    Phases: solid mineral grains + pore water + pore air.
    sqrt(ε_bulk) = Σ V_i * sqrt(ε_i)  — Complex Refractive Index Method.

    Zone sets the internal porosity of the fines pack (gravity compaction):
        dense    φ = 0.32  (settled zone 1)
        granular φ = 0.40  (dispersed zone 2)
        sparse   φ = 0.48  (near-surface zone 3)

    Saturation: S = moisture / φ  (bulk water content → pore-space saturation)
    PVC boost: high contamination retains capillary water → +0.35 × PVC/100.

    Args:
        moisture:    bulk volumetric water content (0–1)
        pvc:         Percentage Void Contamination (0–100)
        zone:        'dense' | 'granular' | 'sparse'
        eps_mineral: εr of mineral grains (clay ≈ 5.5, Santamarina et al. 2002)
        eps_water:   εr of free water (≈ 81)

    Returns:
        (eps_r, sigma) — bulk relative permittivity and conductivity [S/m]
    """
    phi = {'dense': 0.32, 'granular': 0.40, 'sparse': 0.48}.get(zone, 0.40)

    # Bulk moisture → pore-space saturation, plus capillary retention from fouling
    saturation = min(moisture / max(phi, 1e-6) + 0.35 * (pvc / 100.0), 0.95)
    saturation = max(0.0, saturation)

    v_mineral = 1.0 - phi
    v_water   = saturation * phi
    v_air     = max(0.0, (1.0 - saturation) * phi)

    eps_r = crim_bulk_eps(
        v_rock=v_mineral, eps_rock=eps_mineral,
        v_fines=0.0,      eps_fines=1.0,
        v_water=v_water,  eps_water=eps_water,
        v_air=v_air,
    )

    # Surface conduction on grains + electrolytic transport through pore water
    sigma = max(0.005 * v_mineral + 0.1 * v_water, 0.001)
    return eps_r, sigma


def debye_decompose(eps_static: float, d_eps_frac: float, eps_inf_min: float = 1.0) -> tuple:
    """Split a static permittivity into (eps_inf, d_eps) for a 1-pole Debye model.

    gprMax's #material gets eps_inf (high-freq permittivity) and
    #add_dispersion_debye gets d_eps = eps_static - eps_inf, with the constraint
    eps_inf >= 1 (cannot go below vacuum). This caps the dispersive fraction so a
    low-eps material (e.g. fouling eps~4.5) can never produce eps_inf < 1, which
    gprMax rejects with 'requires a positive value of one or greater'.

    Args:
        eps_static:  the (constant) permittivity you have today, e.g. from CRIM.
        d_eps_frac:  desired fraction of eps_static to make dispersive (0-1).
        eps_inf_min: floor for eps_inf (default 1.0, gprMax minimum).

    Returns:
        (eps_inf, d_eps) — both safe to write; eps_inf + d_eps == eps_static
        whenever the cap is not hit, otherwise d_eps is reduced to keep eps_inf
        at the floor.
    """
    d_eps_frac = max(0.0, min(d_eps_frac, 1.0))
    d_eps = d_eps_frac * eps_static
    max_d_eps = max(0.0, eps_static - eps_inf_min)
    d_eps = min(d_eps, max_d_eps)
    eps_inf = eps_static - d_eps
    return round(eps_inf, 4), round(d_eps, 4)


def fi_from_fouling_height(fh_pct: float, porosity: float = None) -> float:
    """Convert %FH (fouled-ballast height fraction) to FI via the Rojas-Vivanco
    2025 theoretical quadratic — the SAME equation used to label the real
    pandoscope data, so synthetic height-FI is directly comparable.

    FI = a*FH^2 + b*FH + c, with (a,b,c) chosen by compaction state from
    ballast porosity:
        loose   (phi >= 0.65) : FH_FI_LOOSE
        medium  (default)     : FH_FI_MEDIUM  (real labels use this)
        compact (phi <= 0.55) : FH_FI_COMPACT

    Replaces the old linear FH/1.5 (PHC.LDCP_FH_FACTOR_CLAY), which diverged from
    the real labeling by up to ~20 FI points at high FH.

    Args:
        fh_pct:   percent fouling height (0-100), e.g. Lab_LDCP_FH.
        porosity: ballast void fraction; selects the compaction curve.
                  None -> medium (matches the real data's "Medium" labeling).

    Returns:
        Estimated FI (clamped to >= 0).
    """
    if porosity is None:
        a, b, c = PHC.FH_FI_MEDIUM
    elif porosity >= 0.65:
        a, b, c = PHC.FH_FI_LOOSE
    elif porosity <= 0.55:
        a, b, c = PHC.FH_FI_COMPACT
    else:
        a, b, c = PHC.FH_FI_MEDIUM

    fh = max(0.0, min(fh_pct, 100.0))
    return max(0.0, a * fh * fh + b * fh + c)


def get_percent_passing(d_target: float, psd_points: list) -> float:
    """
    Get Percent Passing at d_target using Log-Linear Interpolation on a PSD curve.
    
    Args:
        d_target: Diameter to query.
        psd_points: List of (Diameter, PercentPassing) tuples. 
                    Will be sorted internally if needed.
    """
    # Sort points by diameter ascending for consistent interpolation
    sorted_points = sorted(psd_points, key=lambda x: x[0])
    
    # Handle bounds — check upper first so duplicate x-values return the highest % passing
    if d_target >= sorted_points[-1][0]:
        return sorted_points[-1][1]
    if d_target < sorted_points[0][0]:
        return sorted_points[0][1]
        
    # Find bracketing interval and interpolate
    for i in range(len(sorted_points) - 1):
        diameter_lower, percent_lower = sorted_points[i]
        diameter_upper, percent_upper = sorted_points[i+1]
        
        if diameter_lower <= d_target <= diameter_upper:
            return _log_linear_interpolate(
                d_target, 
                diameter_lower, percent_lower,
                diameter_upper, percent_upper
            )
            
    return 0.0
def get_fdtd_recommendations(center_freq_hz: float, er_max: float = 14.4) -> dict:
    """
    Calculate FDTD simulation parameters based on IEEE 2025 guidelines.
    
    Ref: Khosravi Largani et al. (2025), "FDTD Medium Dimension Selection 
         Guidelines for GPR Synthetic Data Generation"
         
    Guidelines:
        1. Domain X/Y >= 1.5 * lambda_max (to minimize boundary reflections)
        2. dx <= lambda_min / 10         (to avoid numerical dispersion)
        3. Antenna Height > lambda_max/2 (to avoid near-field coupling)
    """
    c = 299792458.0
    # Ricker bandwidth: f_min is roughly 0.5 * f_c, f_max is roughly 1.5 * f_c
    f_min = 0.5 * center_freq_hz
    f_max = 1.5 * center_freq_hz
    
    # lambda_max (longest wave in air)
    lambda_max = c / f_min
    # lambda_min (shortest wave in wet soil)
    lambda_min = c / (f_max * math.sqrt(er_max))
    
    # 1. Domain Width (1.5 * lambda_max)
    recommended_width = 1.5 * lambda_max
    
    # 2. Resolution (lambda_min / 10)
    recommended_dx = lambda_min / 10.0
    
    # 3. Antenna Height (> lambda_max / 2)
    recommended_height = (lambda_max / 2.0) + 0.1  # 10cm safety buffer
    
    return {
        'domain_x': round(recommended_width, 3),
        'dx': round(recommended_dx, 4),
        'antenna_height': round(recommended_height, 3),
        'lambda_max': round(lambda_max, 3),
        'lambda_min': round(lambda_min, 4)
    }

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


def classify_fouling_index(fi: float) -> Literal["CL", "MF", "F", "HF"]:
    """
    Classify fouling based on Fouling Index (FI).
    
    WHY THESE THRESHOLDS:
    These are industry-standard categories from Selig & Waters (1994),
    derived from empirical studies correlating ballast contamination to
    track performance degradation. They're not arbitrary—they represent
    critical points where drainage and load-bearing capacity change.
    
    Classification (Selig & Waters, 1994):
        - Clean (CL):              FI < 10%
        - Moderately Fouled (MF):  10% <= FI < 20%
        - Fouled (F):              20% <= FI < 40%
        - Highly Fouled (HF):      FI >= 40%
    
    Args:
        fi: Fouling Index (mass percentage)
    
    Returns:
        Classification code: "CL", "MF", "F", or "HF"
    """
    if fi < PHC.FI_CLEAN_THRESHOLD:
        return "CL"
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

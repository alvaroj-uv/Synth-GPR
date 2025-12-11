"""
Physics and Classification Formulas.

This module contains domain-specific calculations and classification logic
for GPR simulation properties, separating them from configuration data.
"""

import math
from typing import Literal

# Classification Thresholds (Selig & Waters, 1994)
FI_CLEAN_THRESHOLD = 10.0
FI_MODERATELY_FOULED_THRESHOLD = 20.0
FI_FOULED_THRESHOLD = 40.0

# Default Material Properties
DEFAULT_POROSITY = 0.4
DEFAULT_BALLAST_DENSITY = 2.6  # Gs_b
DEFAULT_FOULING_DENSITY = 2.6  # Gs_f


def classify_pvc(pvc_value: float, porosity: float = DEFAULT_POROSITY) -> str:
    """
    Classify ballast fouling based on input PVC, converting to FI first.
    
    STRICT PHYSICS MODE:
    1. Converts PVC (Volume %) to FI (Mass %) using `convert_pvc_to_fi`.
    2. Classifies the resulting FI using Selig & Waters thresholds.
    
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
    """
    total = rock_thickness + fouling_thickness
    if total <= 0:
        return 0.0
    return (fouling_thickness / total) * 100.0


def convert_pvc_to_fi(pvc: float, porosity: float = 0.4, Gs_b: float = 2.6, Gs_f: float = 2.6) -> float:
    """
    Convert Percentage Void Contamination (PVC) to Fouling Index (FI).
    
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
        
    # Volumetric fractions (relative to total volume 1.0)
    v_foul = (pvc / 100.0) * porosity
    v_rock = 1.0 - porosity
    
    # Mass parts (density * volume)
    # rho_water cancels out in the ratio
    m_foul = v_foul * Gs_f
    m_rock = v_rock * Gs_b
    
    total_mass = m_foul + m_rock
    if total_mass <= 0:
        return 0.0
        
    fi = (m_foul / total_mass) * 100.0
    return fi


def inverse_convert_fi_to_pvc(target_fi: float, porosity: float = 0.4, Gs_b: float = 2.6, Gs_f: float = 2.6) -> float:
    """
    Calculate required PVC (Volume %) to achieve a target FI (Mass %).
    
    Inverse of `convert_pvc_to_fi`.
    Useful for generating datasets with specific fouling labels.
    
    Formula derived from solving FI = Mf / (Mf + Mb):
        PVC = ((1-phi)/phi) * (Gs_b/Gs_f) * (FI / (100-FI)) * 100
        
    Args:
        target_fi: Target Fouling Index (0-100)
        porosity, Gs_b, Gs_f: Material properties (must match forward transform)
        
    Returns:
        Required PVC percentage (0-100). Returns >100 if target is physically impossible with given porosity.
    """
    if target_fi <= 0:
        return 0.0
    if target_fi >= 100:
        return 999.0 # Impossible (would mean 0% rock)
        
    R = target_fi / 100.0
    
    # Ratio of Fouling Mass to Rock Mass needed
    # M_f / M_b = R / (1 - R)
    mass_ratio = R / (1.0 - R)
    
    # Volume Ratio needed
    # V_f / V_r = (M_f/Gs_f) / (M_b/Gs_b) = mass_ratio * (Gs_b / Gs_f)
    vol_ratio = mass_ratio * (Gs_b / Gs_f)
    
    # Solve for PVC using V_f = (PVC/100)*phi and V_r = 1-phi
    # (PVC/100)*phi / (1-phi) = vol_ratio
    # PVC/100 = vol_ratio * (1-phi)/phi
    
    if porosity <= 0: 
        return 0.0
        
    pvc_fraction = vol_ratio * (1.0 - porosity) / porosity
    return pvc_fraction * 100.0


def classify_fouling_index(fi: float) -> Literal["CL", "MF", "F", "HF"]:
    """
    Classify fouling based on Fouling Index (FI).
    
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
    if fi < FI_CLEAN_THRESHOLD:
        return "CL"
    elif fi < FI_MODERATELY_FOULED_THRESHOLD:
        return "MF"
    elif fi < FI_FOULED_THRESHOLD:
        return "F"
    else:
        return "HF"

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

def log_linear_interpolation(d_x: float, d1: float, p1: float, d2: float, p2: float) -> float:
    """
    Log-Linear Interpolation for Particle Size Distribution (PSD).
    
    Formula:
        Px = P1 + (P2 - P1) * (log(dx) - log(d1)) / (log(d2) - log(d1))
    
    Args:
        d_x: Target diameter to interpolate at.
        d1, p1: Diameter and Percent Passing of first bounding point.
        d2, p2: Diameter and Percent Passing of second bounding point.
    
    Returns:
        Interpolated Percent Passing (Px).
    """
    if d_x <= 0 or d1 <= 0 or d2 <= 0:
        # Avoid log domain error, fallback to linear or 0
        return 0.0
        
    if abs(d2 - d1) < 1e-9:
        return p1
        
    log_dx = math.log10(d_x)
    log_d1 = math.log10(d1)
    log_d2 = math.log10(d2)
    
    # Calculate slope in log-log space? No, usually Linear Percent vs Log Diameter.
    # Semi-log plot: X=Log(Size), Y=Linear(Percent)
    
    slope = (p2 - p1) / (log_d2 - log_d1)
    px = p1 + slope * (log_dx - log_d1)
    
    # Clamp to [0, 100] just in case
    return max(0.0, min(100.0, px))

def get_percent_passing(d_target: float, psd_points: list) -> float:
    """
    Get Percent Passing at d_target using Log-Linear Interpolation on a PSD curve.
    
    Args:
        d_target: Diameter to query.
        psd_points: List of (Diameter, PercentPassing) tuples. 
                    Must be sorted by diameter descending or ascending.
    """
    # 1. Sort points by diameter ascending just to be safe
    sorted_points = sorted(psd_points, key=lambda x: x[0])
    
    # 2. Check bounds
    if d_target <= sorted_points[0][0]:
        return sorted_points[0][1] # Smaller than smallest
    if d_target >= sorted_points[-1][0]:
        return sorted_points[-1][1] # Larger than largest
        
    # 3. Find interval
    for i in range(len(sorted_points) - 1):
        d1, p1 = sorted_points[i]
        d2, p2 = sorted_points[i+1]
        
        if d1 <= d_target <= d2:
            return log_linear_interpolation(d_target, d1, p1, d2, p2)
            
    return 0.0

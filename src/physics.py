"""
Physics and Classification Formulas.

This module contains domain-specific calculations and classification logic
for GPR simulation properties, separating them from configuration data.
"""

def classify_pvc(pvc_value: float) -> str:
    """
    Classify ballast fouling using Selig and Waters (1994) standard.
    
    Official thresholds:
        - C  (Clean):            0%  <= FI < 1%
        - MC (Moderately Clean): 1%  <= FI < 10%
        - MF (Moderately Fouled): 10% <= FI < 20%
        - F  (Fouled):           20% <= FI < 40%
        - HF (Highly Fouled):    FI >= 40%
    
    Args:
        pvc_value: Percentage Void Contamination (0-100)
        
    Returns:
        Class code: C, MC, MF, F, or HF
    """
    if pvc_value < 1.0:
        return "C"
    elif pvc_value < 10.0:
        return "MC"
    elif pvc_value < 20.0:
        return "MF"
    elif pvc_value < 40.0:
        return "F"
    else:
        return "HF"

# Backward compatibility aliases
get_fi_class = classify_pvc
get_pvc_class = classify_pvc

def compute_fouling_index(rock_thickness: float, fouling_thickness: float) -> float:
    """
    Compute Fouling Index (FI) as percentage of fouling in total ballast depth.
    """
    total = rock_thickness + fouling_thickness
    if total <= 0:
        return 0.0
    return (fouling_thickness / total) * 100.0

# Backward compatibility alias
compute_fi = compute_fouling_index

def classify_fouling_index(fouling_index: float) -> str:
    """Simply 3-band classification based on FI percentage."""
    if fouling_index < 20:
        return "CL"
    elif fouling_index < 40:
        return "MF"
    else:
        return "F"

# Backward compatibility alias
classify_fi = classify_fouling_index

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

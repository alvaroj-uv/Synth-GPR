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


# Singleton instance for easy access
PC = PhysicalConstants()

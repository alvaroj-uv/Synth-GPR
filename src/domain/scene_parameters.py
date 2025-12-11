"""
Scene Parameters Domain Object.

Type-safe parameters for scene generation, replacing Dict[str, Any].
"""

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class SceneParameters:
    """
    Type-safe parameters for scene generation.
    
    Replaces the untyped Dict[str, Any] in WorkOrder to provide:
    - Compile-time type checking
    - IDE autocomplete
    - Self-documenting code
    - Validation at construction
    
    Example:
        >>> params = SceneParameters(pvc=25.0, moisture=0.1)
        >>> params.pvc
        25.0
    """
    
    # Fouling Properties
    pvc: float = 0.0                    # Percentage Void Contamination (0-100%)
    moisture: float = 0.0               # Moisture content (0-1.0)
    
    # Layer Geometry
    ballast_thickness: float = 0.45     # Ballast layer thickness (meters)
    formation_thickness: float = 0.1    # Formation layer thickness (meters)
    subgrade_thickness: float = 0.5     # Subgrade layer thickness (meters)
    
    # Antenna Configuration
    antenna_offset: float = 0.0         # Horizontal antenna offset (meters)
    antenna_clearance: float = 0.5      # Clearance above ballast (meters)
    
    # Domain Override (None = use config defaults)
    domain_x: Optional[float] = None    # Domain width (meters)
    domain_y: Optional[float] = None    # Domain height (meters)
    domain_z: Optional[float] = None    # Domain depth (meters)
    
    # Rock Packing
    rock_z_start: Optional[float] = None  # Rock extrusion start
    rock_z_end: Optional[float] = None    # Rock extrusion end
    
    # Advanced
    porosity: Optional[float] = None    # Override porosity calculation
    
    def __post_init__(self):
        """Validate parameters."""
        if not (0 <= self.pvc <= 100):
            raise ValueError(f"pvc must be 0-100, got {self.pvc}")
        
        if not (0 <= self.moisture <= 1.0):
            raise ValueError(f"moisture must be 0-1.0, got {self.moisture}")
        
        if self.ballast_thickness < 0:
            raise ValueError(f"ballast_thickness must be positive, got {self.ballast_thickness}")
    
    def to_dict(self) -> dict:
        """Convert to dictionary for legacy compatibility."""
        return {
            'pvc': self.pvc,
            'moisture': self.moisture,
            'ballast_thickness': self.ballast_thickness,
            'formation_thickness': self.formation_thickness,
            'subgrade_thickness': self.subgrade_thickness,
            'antenna_offset': self.antenna_offset,
            'antenna_clearance': self.antenna_clearance,
            'domain_x': self.domain_x,
            'domain_y': self.domain_y,
            'domain_z': self.domain_z,
            'rock_z_start': self.rock_z_start,
            'rock_z_end': self.rock_z_end,
            'porosity': self.porosity,
        }

"""
Material value objects for domain modeling.

Replaces string-based material identifiers with type-safe value objects.
"""

from dataclasses import dataclass
from typing import Literal

# Type alias for valid material names
MaterialType = Literal[
    "subgrade",
    "formation", 
    "bal_rock",
    "bal_foul_granular",
    "free_space",
    "fouling_base"
]


@dataclass(frozen=True)
class Material:
    """
    Domain value object for electromagnetic material properties.
    
    Attributes:
        name: Material identifier
        permittivity: Relative permittivity (εᵣ, dimensionless)
        conductivity: Electrical conductivity (σ, S/m)
        permeability: Relative permeability (μᵣ, default 1.0)
        magnetic_loss: Magnetic loss (default 0.0)
    
    Example:
        >>> mat = Material("subgrade", permittivity=5.0, conductivity=0.01)
        >>> print(mat)
        Material(subgrade, εᵣ=5.0, σ=0.010 S/m)
    """
    name: str  # MaterialType causes issues with dynamic names
    permittivity: float       # εᵣ (relative permittivity)
    conductivity: float       # σ (S/m)
    permeability: float = 1.0 # μᵣ (relative permeability)
    magnetic_loss: float = 0.0
    
    def __str__(self) -> str:
        """Human-readable string representation."""
        return f"Material({self.name}, εᵣ={self.permittivity:.1f}, σ={self.conductivity:.3f} S/m)"
    
    def __repr__(self) -> str:
        """Detailed representation for debugging."""
        return (f"Material(name='{self.name}', permittivity={self.permittivity}, "
                f"conductivity={self.conductivity}, permeability={self.permeability}, "
                f"magnetic_loss={self.magnetic_loss})")
    
    def to_gprmax_command(self):
        """
        Convert to gprMax MaterialCommand format.
        
        Returns:
            MaterialCommand for use in gprMax input files
        """
        from ..gpr_commands import MaterialCommand
        return MaterialCommand(
            self.permittivity,
            self.conductivity,
            self.permeability,
            self.magnetic_loss,
            self.name
        )


class Materials:
    """
    Standard material library for GPR simulation.
    
    Provides type-safe access to common materials with physically
    realistic electromagnetic properties.
    """
    
    # Air/Free Space
    FREE_SPACE = Material(
        name="free_space",
        permittivity=1.0,
        conductivity=0.0,
        permeability=1.0,
        magnetic_loss=0.0
    )
    
    # Subgrade (typical soil)
    SUBGRADE = Material(
        name="subgrade",
        permittivity=5.0,
        conductivity=0.01
    )
    
    # Formation layer (compacted soil/rock)
    FORMATION = Material(
        name="formation",
        permittivity=6.0,
        conductivity=0.015
    )
    
    # Clean ballast rock (granite)
    BALLAST_ROCK = Material(
        name="bal_rock",
        permittivity=4.0,
        conductivity=0.001
    )
    
    # Fouling material base (clay/silt)
    FOULING_BASE = Material(
        name="fouling_base",
        permittivity=8.0,
        conductivity=0.02
    )
    
    @classmethod
    def get(cls, name: str) -> Material:
        """
        Get material by name (for dynamic access).
        
        Args:
            name: Material name
        
        Returns:
            Material object
        
        Raises:
            ValueError: If material name not found
        """
        materials = {
            "free_space": cls.FREE_SPACE,
            "subgrade": cls.SUBGRADE,
            "formation": cls.FORMATION,
            "bal_rock": cls.BALLAST_ROCK,
            "fouling_base": cls.FOULING_BASE,
        }
        
        if name not in materials:
            raise ValueError(f"Unknown material: {name}. Available: {list(materials.keys())}")
        
        return materials[name]

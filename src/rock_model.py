
from dataclasses import dataclass
from typing import Optional

@dataclass
class Rock:
    """
    Represents a single cylindrical rock in the ballast.
    
    Attributes:
        x: Horizontal center position (meters)
        y: Vertical center position (meters)
        radius: Rock radius (meters)
        z_start: Start of extrusion (meters, default 0)
        z_end: End of extrusion (meters, default domain_z)
    """
    x: float
    y: float
    radius: float
    z_start: float = 0.0
    z_end: float = 0.005
    
    def __str__(self) -> str:
        """Human-readable string representation."""
        return f"Rock(center=({self.x:.3f}, {self.y:.3f}), r={self.radius:.3f}m)"
    
    def __repr__(self) -> str:
        """Detailed representation for debugging."""
        return f"Rock(x={self.x}, y={self.y}, radius={self.radius}, z_start={self.z_start}, z_end={self.z_end})"


@dataclass
class PackingBounds:
    """
    Defines the rectangular bounding box for rock placement.
    """
    x_min: float
    x_max: float
    y_min: float
    y_max: float
    
    @property
    def width(self) -> float:
        return self.x_max - self.x_min
    
    @property
    def height(self) -> float:
        return self.y_max - self.y_min
    
    @property
    def area(self) -> float:
        return self.width * self.height



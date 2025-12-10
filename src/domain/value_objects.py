"""
Domain Value Objects for GPR Simulation.

Value objects are immutable objects that represent descriptive aspects
of the domain. They are compared by value, not identity.

References:
- Selig & Waters (1994): Track Geotechnology and Substructure Management
- Domain-Driven Design (Evans, 2003)
"""

from dataclasses import dataclass
from typing import Literal
import math


@dataclass(frozen=True)
class PercentageVoidContamination:
    """
    Percentage Void Contamination (PVC): Fouling level in ballast.
    
    Domain Definition (Selig & Waters, 1994):
        PVC = (V_fouling / V_voids) × 100%
    
    Where:
        V_fouling = Volume of fouling material in voids
        V_voids = Total void space in clean ballast
    
    Classification:
        Clean:              0-10%
        Moderately Fouled:  10-20%
        Fouled:             20-40%
        Highly Fouled:      >40%
    
    Attributes:
        value: PVC percentage (0-100)
    
    Example:
        >>> pvc = PercentageVoidContamination(value=25.0)
        >>> pvc.classification()
        'Fouled'
        >>> pvc.is_clean()
        False
    """
    value: float  # percentage (0-100)
    
    def __post_init__(self):
        """Validate PVC is in valid range."""
        if not (0 <= self.value <= 100):
            raise ValueError(
                f"PVC must be between 0-100%, got {self.value}%"
            )
    
    def classification(self) -> Literal["Clean", "Moderately Fouled", "Fouled", "Highly Fouled"]:
        """
        Returns fouling classification per Selig & Waters (1994).
        
        Returns:
            Classification string
        """
        if self.value < 10:
            return "Clean"
        elif self.value < 20:
            return "Moderately Fouled"
        elif self.value < 40:
            return "Fouled"
        else:
            return "Highly Fouled"
    
    def is_clean(self) -> bool:
        """Check if ballast is clean (PVC < 10%)."""
        return self.value < 10
    
    def is_fouled(self) -> bool:
        """Check if ballast is fouled (PVC >= 20%)."""
        return self.value >= 20
    
    def to_fouling_index(self, porosity: float) -> float:
        """
        Convert PVC to Fouling Index (FI).
        
        FI = PVC × porosity
        
        Args:
            porosity: Ballast porosity (0-1, typically ~0.4)
        
        Returns:
            Fouling Index percentage
        """
        return self.value * porosity
    
    def __str__(self) -> str:
        return f"{self.value:.1f}%"
    
    def __repr__(self) -> str:
        return f"PercentageVoidContamination(value={self.value})"


@dataclass(frozen=True)
class Point2D:
    """
    2D point in Cartesian coordinates.
    
    Immutable value object representing a position in 2D space.
    Used for geometric calculations and spatial relationships.
    
    Attributes:
        x: Horizontal coordinate (meters)
        y: Vertical coordinate (meters)
    
    Example:
        >>> p1 = Point2D(x=0.25, y=1.35)
        >>> p2 = Point2D(x=0.30, y=1.40)
        >>> p1.distance_to(p2)
        0.0707...
    """
    x: float
    y: float
    
    def distance_to(self, other: 'Point2D') -> float:
        """
        Calculate Euclidean distance to another point.
        
        Args:
            other: Target point
        
        Returns:
            Distance in meters
        """
        return math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)
    
    def offset(self, dx: float, dy: float) -> 'Point2D':
        """
        Create a new point offset by (dx, dy).
        
        Args:
            dx: Horizontal offset (meters)
            dy: Vertical offset (meters)
        
        Returns:
            New Point2D
        """
        return Point2D(x=self.x + dx, y=self.y + dy)
    
    def to_tuple(self) -> tuple[float, float]:
        """Convert to tuple (x, y)."""
        return (self.x, self.y)
    
    def __str__(self) -> str:
        return f"({self.x:.3f}, {self.y:.3f})"
    
    def __repr__(self) -> str:
        return f"Point2D(x={self.x}, y={self.y})"


@dataclass(frozen=True)
class Point3D:
    """
    3D point in Cartesian coordinates.
    
    Immutable value object representing a position in 3D space.
    Used for gprMax geometry and antenna positions.
    
    Attributes:
        x: Horizontal coordinate (meters)
        y: Vertical coordinate (meters)
        z: Depth/extrusion coordinate (meters)
    
    Example:
        >>> antenna = Point3D(x=0.25, y=1.35, z=0.0025)
        >>> antenna.to_2d()
        Point2D(x=0.25, y=1.35)
    """
    x: float
    y: float
    z: float
    
    def distance_to(self, other: 'Point3D') -> float:
        """
        Calculate 3D Euclidean distance to another point.
        
        Args:
            other: Target point
        
        Returns:
            Distance in meters
        """
        return math.sqrt(
            (self.x - other.x)**2 +
            (self.y - other.y)**2 +
            (self.z - other.z)**2
        )
    
    def distance_2d(self, other: 'Point3D') -> float:
        """
        Calculate 2D distance (ignoring Z).
        
        Useful for antenna clearance checks where Z is extrusion.
        
        Args:
            other: Target point
        
        Returns:
            2D distance in meters
        """
        return math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)
    
    def to_2d(self) -> Point2D:
        """Project to 2D (X-Y plane, discard Z)."""
        return Point2D(x=self.x, y=self.y)
    
    def offset(self, dx: float, dy: float, dz: float) -> 'Point3D':
        """
        Create a new point offset by (dx, dy, dz).
        
        Args:
            dx: Horizontal offset (meters)
            dy: Vertical offset (meters)
            dz: Depth offset (meters)
        
        Returns:
            New Point3D
        """
        return Point3D(x=self.x + dx, y=self.y + dy, z=self.z + dz)
    
    def to_tuple(self) -> tuple[float, float, float]:
        """Convert to tuple (x, y, z)."""
        return (self.x, self.y, self.z)
    
    def __str__(self) -> str:
        return f"({self.x:.3f}, {self.y:.3f}, {self.z:.4f})"
    
    def __repr__(self) -> str:
        return f"Point3D(x={self.x}, y={self.y}, z={self.z})"


@dataclass(frozen=True)
class Length:
    """
    Physical length with explicit units.
    
    Value object that prevents unit confusion by making units explicit.
    Useful for ballast thickness, antenna clearance, rock radius, etc.
    
    Attributes:
        value: Numeric value
        unit: Unit of measurement ('m', 'cm', 'mm')
    
    Example:
        >>> thickness = Length(value=40, unit='cm')
        >>> thickness.to_meters()
        0.4
        >>> thickness > Length(value=300, unit='mm')
        True
    """
    value: float
    unit: Literal['m', 'cm', 'mm']
    
    def to_meters(self) -> float:
        """
        Convert to meters regardless of unit.
        
        Returns:
            Length in meters
        """
        if self.unit == 'm':
            return self.value
        elif self.unit == 'cm':
            return self.value / 100.0
        elif self.unit == 'mm':
            return self.value / 1000.0
        else:
            raise ValueError(f"Unknown unit: {self.unit}")
    
    def to_centimeters(self) -> float:
        """Convert to centimeters."""
        return self.to_meters() * 100.0
    
    def to_millimeters(self) -> float:
        """Convert to millimeters."""
        return self.to_meters() * 1000.0
    
    def __eq__(self, other: object) -> bool:
        """Compare lengths by converted value (unit-agnostic)."""
        if not isinstance(other, Length):
            return NotImplemented
        return math.isclose(self.to_meters(), other.to_meters())
    
    def __lt__(self, other: 'Length') -> bool:
        """Compare lengths (unit-agnostic)."""
        return self.to_meters() < other.to_meters()
    
    def __le__(self, other: 'Length') -> bool:
        return self.to_meters() <= other.to_meters()
    
    def __gt__(self, other: 'Length') -> bool:
        return self.to_meters() > other.to_meters()
    
    def __ge__(self, other: 'Length') -> bool:
        return self.to_meters() >= other.to_meters()
    
    def __add__(self, other: 'Length') -> 'Length':
        """Add two lengths, result in meters."""
        return Length(value=self.to_meters() + other.to_meters(), unit='m')
    
    def __sub__(self, other: 'Length') -> 'Length':
        """Subtract lengths, result in meters."""
        return Length(value=self.to_meters() - other.to_meters(), unit='m')
    
    def __mul__(self, scalar: float) -> 'Length':
        """Multiply length by scalar."""
        return Length(value=self.value * scalar, unit=self.unit)
    
    def __str__(self) -> str:
        return f"{self.value}{self.unit}"
    
    def __repr__(self) -> str:
        return f"Length(value={self.value}, unit='{self.unit}')"

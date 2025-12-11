"""
Coordinate System Domain Model.

Centralizes geometry management using Layers and Anchors.
Replaces hardcoded offsets and implicit dependencies.
"""

from enum import Enum
from dataclasses import dataclass
from typing import Dict, Tuple

from .value_objects import Point3D


class Anchor(Enum):
    """
    Named vertical levels in the simulation domain.
    """
    BOTTOM = "bottom"             # y = 0.0
    SUBGRADE_TOP = "subgrade_top" # Top of subgrade layer
    FORMATION_TOP = "formation_top" # Top of formation/subballast
    BALLAST_BOTTOM = "ballast_bottom" # Usually same as FORMATION_TOP
    BALLAST_TOP = "ballast_top"   # Top of clean ballast
    ANTENNA_LEVEL = "antenna_level" # Center height of antenna
    DOMAIN_TOP = "domain_top"     # Top of simulation domain


@dataclass(frozen=True)
class LayerStack:
    """
    Configuration for vertical layer thicknesses.
    
    This is the Single Source of Truth for "How thick is X?".
    """
    subgrade_thickness: float = 0.5
    formation_thickness: float = 0.1
    ballast_thickness: float = 0.45
    antenna_clearance: float = 0.5   # Space above ballast for antenna
    air_buffer: float = 0.1          # Extra air above antenna
    
    @property
    def total_height(self) -> float:
        """Total required domain height."""
        return (self.subgrade_thickness + 
                self.formation_thickness + 
                self.ballast_thickness + 
                self.antenna_clearance + 
                self.air_buffer)


class Layer(Enum):
    """Semantic layers in the model."""
    SUBGRADE = "subgrade"
    FORMATION = "formation"
    BALLAST = "ballast"
    AIR = "air"


@dataclass(frozen=True)
class LayerBounds:
    """
    Geometric boundaries of a layer.
    
    Replaces raw tuples with semantic object.
    """
    bottom: float
    top: float
    
    @property
    def height(self) -> float:
        return self.top - self.bottom
    
    @property
    def center(self) -> float:
        return (self.top + self.bottom) / 2
        
    def contains_y(self, y: float) -> bool:
        """Check if Y is within this layer."""
        return self.bottom <= y <= self.top


class CoordinateSystem:
    """
    Service for resolving geometric coordinates.
    
    Translates semantic requests ("Top of Ballast") into absolute coordinates.
    Now supports Type-Safe Layer lookups (Phase 1 Refactoring).
    """
    
    def __init__(self, layer_stack: LayerStack, domain_x: float = 1.0, domain_z: float = 0.005):
        self.stack = layer_stack
        self.domain_x = domain_x
        self.domain_z = domain_z
        
        # Precompute absolute Y levels
        self._y_levels: Dict[Anchor, float] = {}
        self._compute_levels()
        
    def _compute_levels(self):
        """Calculate absolute Y heights for all anchors."""
        current_y = 0.0
        self._y_levels[Anchor.BOTTOM] = current_y
        
        # Subgrade
        current_y += self.stack.subgrade_thickness
        self._y_levels[Anchor.SUBGRADE_TOP] = current_y
        
        # Formation
        current_y += self.stack.formation_thickness
        self._y_levels[Anchor.FORMATION_TOP] = current_y
        # Legacy anchor (to be phased out, mapped to FORMATION_TOP)
        self._y_levels[Anchor.BALLAST_BOTTOM] = current_y
        
        # Ballast
        current_y += self.stack.ballast_thickness
        self._y_levels[Anchor.BALLAST_TOP] = current_y
        
        # Antenna
        current_y += self.stack.antenna_clearance
        self._y_levels[Anchor.ANTENNA_LEVEL] = current_y
        
        # Domain Top
        current_y += self.stack.air_buffer
        self._y_levels[Anchor.DOMAIN_TOP] = current_y
        
    def get_y(self, anchor: Anchor, offset: float = 0.0) -> float:
        """
        Get absolute Y coordinate for an anchor + offset.
        
        Args:
            anchor: The reference level (e.g., Anchor.BALLAST_TOP)
            offset: Additional offset in meters (positive = up)
            
        Returns:
            Absolute Y coordinate in meters
        """
        base_y = self._y_levels[anchor]
        return base_y + offset
    
    def bounds(self, layer: Layer) -> LayerBounds:
        """
        Get geometric bounds for a semantic layer (Type-Safe).
        """
        if layer == Layer.SUBGRADE:
            return LayerBounds(self.get_y(Anchor.BOTTOM), self.get_y(Anchor.SUBGRADE_TOP))
        elif layer == Layer.FORMATION:
            return LayerBounds(self.get_y(Anchor.SUBGRADE_TOP), self.get_y(Anchor.FORMATION_TOP))
        elif layer == Layer.BALLAST:
            # Use FORMATION_TOP as bottom for Ballast (single source of truth)
            return LayerBounds(self.get_y(Anchor.FORMATION_TOP), self.get_y(Anchor.BALLAST_TOP))
        elif layer == Layer.AIR:
            return LayerBounds(self.get_y(Anchor.BALLAST_TOP), self.get_y(Anchor.DOMAIN_TOP))
        else:
            raise ValueError(f"Unknown layer: {layer}")

    def get_layer_bounds(self, layer_name: str) -> Tuple[float, float]:
        """
        Legacy support for string-based bounds lookup.
        DEPRECATED: Use bounds(Layer.NAME) instead.
        """
        try:
            # Try to convert string to Enum
            layer = Layer(layer_name)
            b = self.bounds(layer)
            return (b.bottom, b.top)
        except ValueError:
             # Fallback for any legacy names not in Enum (none currently known)
             raise ValueError(f"Unknown layer: {layer_name}")
            
    def validate_point(self, point: Point3D) -> bool:
        """Check if a point is within the domain bounds."""
        valid_x = 0 <= point.x <= self.domain_x
        valid_y = 0 <= point.y <= self.get_y(Anchor.DOMAIN_TOP)
        valid_z = 0 <= point.z <= self.domain_z
        return valid_x and valid_y and valid_z

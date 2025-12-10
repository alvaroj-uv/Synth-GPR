"""
Scene Geometry Components

Focused components for managing different aspects of scene geometry.
This module splits the responsibilities of SceneCheckpoint into cohesive classes.
"""

from dataclasses import dataclass, field
from typing import List, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from .gpr_commands import (
        MaterialCommand, GeometryCommand, SourceCommand, 
        ReceiverCommand, DomainCommand, DxDyDzCommand, TimeWindowCommand
    )
    from .config import GeneratorConfig


@dataclass
class GeometryCollection:
    """
    Manages geometry and material commands for gprMax scene.
    
    Responsibility: Store and manage lists of materials and geometry objects.
    Single Responsibility: Geometry command storage.
    """
    materials: List['MaterialCommand'] = field(default_factory=list)
    geometry: List['GeometryCommand'] = field(default_factory=list)
    
    def add_material(self, cmd: 'MaterialCommand') -> None:
        """Add a material command to the collection."""
        self.materials.append(cmd)
    
    def add_geometry(self, cmd: 'GeometryCommand') -> None:
        """Add a geometry command (box, cylinder, etc.) to the collection."""
        self.geometry.append(cmd)
    
    def clone(self) -> 'GeometryCollection':
        """
        Create a shallow copy of the geometry collection.
        
        Commands are immutable, so shallow copy is safe.
        """
        return GeometryCollection(
            materials=list(self.materials),
            geometry=list(self.geometry)
        )
    
    def clear(self) -> None:
        """Clear all geometry and materials."""
        self.materials.clear()
        self.geometry.clear()
    
    def validate(self) -> List[str]:
        """
        Validate geometry collection state.
        
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        
        if not self.materials:
            errors.append("No materials defined")
        
        if not self.geometry:
            errors.append("No geometry commands defined")
        
        # Check for duplicate material names
        material_names = [m.name for m in self.materials if hasattr(m, 'name')]
        if len(material_names) != len(set(material_names)):
            errors.append("Duplicate material names found")
        
        return errors
    
    @property
    def total_commands(self) -> int:
        """Total number of commands in collection."""
        return len(self.materials) + len(self.geometry)


@dataclass
class AntennaConfiguration:
    """
    Manages antenna sources and receivers for GPR simulation.
    
    Responsibility: Store and manage antenna placement.
    Single Responsibility: Antenna configuration.
    """
    sources: List['SourceCommand'] = field(default_factory=list)
    receivers: List['ReceiverCommand'] = field(default_factory=list)
    
    def add_source(self, cmd: 'SourceCommand') -> None:
        """Add a source command (waveform + dipole)."""
        self.sources.append(cmd)
    
    def add_receiver(self, cmd: 'ReceiverCommand') -> None:
        """Add a receiver command."""
        self.receivers.append(cmd)
    
    def reset(self) -> None:
        """
        Clear all antennas.
        
        Used when cloning scene for variants with different antenna positions.
        """
        self.sources.clear()
        self.receivers.clear()
    
    def clone_empty(self) -> 'AntennaConfiguration':
        """
        Create empty antenna configuration.
        
        Used for scene variants that need new antenna placement.
        """
        return AntennaConfiguration()
    
    def validate(self) -> List[str]:
        """
        Validate antenna configuration.
        
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        
        # Filter actual physical sources (exclude Waveform definitions)
        # We check class name string to avoid circular imports of proper types
        physical_sources = [
            s for s in self.sources 
            if not s.__class__.__name__.startswith('Waveform')
        ]
        
        if not physical_sources:
            errors.append("No antenna sources defined (HertzianDipole etc.)")
        
        if not self.receivers:
            errors.append("No antenna receivers defined")
        
        if len(physical_sources) != len(self.receivers):
            errors.append(
                f"Mismatch: {len(physical_sources)} sources but {len(self.receivers)} receivers. "
                "Usually should match for bistatic GPR."
            )
        
        return errors
    
    @property
    def is_configured(self) -> bool:
        """Check if antennas are properly configured."""
        return len(self.sources) > 0 and len(self.receivers) > 0


@dataclass
class RockCollection:
    """
    Manages rock positions and properties for quality checking.
    
    Responsibility: Track rock aggregates in ballast layer.
    Single Responsibility: Rock position tracking.
    """
    positions: List[Any] = field(default_factory=list)
    
    def add_rock(self, position: Any) -> None:
        """Add a rock position."""
        self.positions.append(position)
    
    def clear(self) -> None:
        """Clear all rock positions."""
        self.positions.clear()
    
    def clone(self) -> 'RockCollection':
        """Create a copy of rock collection."""
        return RockCollection(positions=list(self.positions))
    
    def validate(self) -> List[str]:
        """
        Validate rock collection.
        
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        
        if len(self.positions) < 10:
            errors.append(
                f"Too few rocks ({len(self.positions)}). "
                "Need at least 10 for realistic GPR signatures."
            )
        
        if len(self.positions) > 10000:
            errors.append(
                f"Excessive rocks ({len(self.positions)}). "
                "May cause performance issues."
            )
        
        return errors
    
    @property
    def count(self) -> int:
        """Number of rocks in collection."""
        return len(self.positions)


@dataclass(frozen=True)
class DomainSettings:
    """
    gprMax domain configuration settings.
    
    Responsibility: Store immutable domain parameters.
    Single Responsibility: Domain configuration.
    
    Immutable (frozen=True) because domain settings shouldn't change
    after scene initialization.
    """
    domain_cmd: 'DomainCommand'
    dx_dy_dz_cmd: 'DxDyDzCommand'
    time_window_cmd: 'TimeWindowCommand'
    
    @classmethod
    def from_config(cls, config: 'GeneratorConfig') -> 'DomainSettings':
        """
        Create domain settings from generator configuration.
        
        Args:
            config: GeneratorConfig with domain parameters
            
        Returns:
            Immutable DomainSettings instance
        """
        from .gpr_commands import DomainCommand, DxDyDzCommand, TimeWindowCommand
        
        return cls(
            domain_cmd=DomainCommand(config.domain_x, config.domain_y, config.domain_z),
            dx_dy_dz_cmd=DxDyDzCommand(config.dx, config.dy, config.dz),
            time_window_cmd=TimeWindowCommand(config.time_window)
        )
    
    def validate(self) -> List[str]:
        """
        Validate domain settings.
        
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        
        # Check domain dimensions
        x, y, z = self.get_domain_dimensions()
        if x <= 0 or y <= 0 or z <= 0:
            errors.append(f"Invalid domain dimensions: ({x}, {y}, {z}). Must be positive.")
        
        # Check discretization
        dx, dy, dz = self.get_discretization()
        if dx <= 0 or dy <= 0 or dz <= 0:
            errors.append(f"Invalid discretization: ({dx}, {dy}, {dz}). Must be positive.")
        
        # Check resolution (domain should be larger than discretization)
        if dx >= x or dy >= y or dz >= z:
            errors.append(
                f"Discretization ({dx}, {dy}, {dz}) too coarse for "
                f"domain ({x}, {y}, {z})"
            )
        
        # Check time window
        if self.time_window_cmd.time_window <= 0:
            errors.append(
                f"Invalid time window: {self.time_window_cmd.time_window}. Must be positive."
            )
        
        return errors
    
    def get_domain_dimensions(self) -> tuple[float, float, float]:
        """Get domain dimensions (x, y, z)."""
        return (
            self.domain_cmd.x,
            self.domain_cmd.y,
            self.domain_cmd.z
        )
    
    def get_discretization(self) -> tuple[float, float, float]:
        """Get spatial discretization (dx, dy, dz)."""
        return (
            self.dx_dy_dz_cmd.dx,
            self.dx_dy_dz_cmd.dy,
            self.dx_dy_dz_cmd.dz
        )

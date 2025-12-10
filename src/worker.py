"""
Worker base class and protocols for the Factory Architecture.

Workers are specialized components that perform specific tasks 
during scene generation. Each worker:
- Executes a specific step (e.g., paint air, place rocks)
- Performs quality checks after completion
- Logs issues to the QualityLog

Usage:
    class MyWorker(Worker):
        name = "MyWorker"
        
        def execute(self, checkpoint, params, materials, tools):
            # Do work...
            
        def quality_check(self, checkpoint) -> List[str]:
            # Return list of errors
            return []
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, TYPE_CHECKING

# Import new scene components
from .scene_geometry import GeometryCollection, AntennaConfiguration, DomainSettings, RockCollection

if TYPE_CHECKING:
    from .config import GeneratorConfig
    from .work_order import WorkOrderSystem
    from .scene_descriptor import SceneDefinition


@dataclass
class SceneCheckpoint:
    """
    Coordinator for scene state that can be cloned for variant generation.
    
    REFACTORED: Now uses composition instead of God Object pattern.
    Each responsibility is delegated to a focused component.
    
    Components:
    - _geometry_collection: GeometryCollection (materials & geometry commands)
    - _antenna_config: AntennaConfiguration (sources & receivers)
    - _rock_collection: RockCollection (rock position tracking)
    - domain_settings: DomainSettings (gprMax domain config)
    """
    config: 'GeneratorConfig'
    work_order: Optional['WorkOrderSystem'] = None
    coordinate_system: Optional[Any] = None
    
    # Composed components (use composition instead of direct storage)
    _geometry_collection: GeometryCollection = field(default_factory=GeometryCollection)
    _antenna_config: AntennaConfiguration = field(default_factory=AntennaConfiguration)
    _rock_collection: RockCollection = field(default_factory=RockCollection)
    domain_settings: Optional[DomainSettings] = None
    
    # Legacy fields (being phased out)
    metadata: Dict[str, Any] = field(default_factory=dict)  # DEPRECATED: Use work_order.blackboard
    assembled: Optional['SceneDefinition'] = None
    
    def __post_init__(self):
        """Auto-initialize domain settings if config is present."""
        if self.config and self.domain_settings is None:
            self.domain_settings = DomainSettings.from_config(self.config)
    
    def clone(self) -> 'SceneCheckpoint':
        """
        Create a deep copy for variant generation.
        
        Antennas are reset (to be filled by AntennaWorker).
        Geometry and rocks are copied (shared structure for variants).
        """
        cloned = SceneCheckpoint(
            config=self.config,  # Config is immutable, share reference
            work_order=self.work_order,  # Share reference to blackboard
            coordinate_system=self.coordinate_system,
            domain_settings=self.domain_settings,  # Immutable, share
            metadata=dict(self.metadata),  # Copy metadata (legacy)
            assembled=None,  # Reset assembly on clone
        )
        cloned._geometry_collection = self._geometry_collection.clone()
        cloned._antenna_config = self._antenna_config.clone_empty()
        cloned._rock_collection = self._rock_collection.clone()
        return cloned
    
    # ========================================================================
    # Delegation methods
    # ========================================================================
    
    def add_material(self, cmd: Any) -> None:
        """Add a material command (delegates to geometry collection)."""
        self._geometry_collection.add_material(cmd)
    
    def add_geometry(self, cmd: Any) -> None:
        """Add a geometry command (delegates to geometry collection)."""
        self._geometry_collection.add_geometry(cmd)
    
    def add_source(self, cmd: Any) -> None:
        """Add a source command (delegates to antennas)."""
        self._antenna_config.add_source(cmd)
    
    def add_receiver(self, cmd: Any) -> None:
        """Add a receiver command (delegates to antennas)."""
        self._antenna_config.add_receiver(cmd)
    
    # ========================================================================
    # Legacy properties for backward compatibility
    # Workers expect scene.materials, scene.geometry, scene.sources, etc.
    # ========================================================================
    
    @property
    def materials(self) -> List[Any]:
        """Access materials list (backward compatibility)."""
        return self._geometry_collection.materials
    
    @property
    def geometry(self) -> List[Any]:
        """Access geometry commands list (backward compatibility - most common access)."""
        return self._geometry_collection.geometry
    
    @property
    def geometry_commands(self) -> List[Any]:
        """Access geometry commands list (backward compatibility - alternative name)."""
        return self._geometry_collection.geometry
    
    @property
    def sources(self) -> List[Any]:
        """Access sources list (backward compatibility)."""
        return self._antenna_config.sources
    
    @property
    def receivers(self) -> List[Any]:
        """Access receivers list (backward compatibility)."""
        return self._antenna_config.receivers
    
    @property
    def domain_cmd(self) -> Any:
        """Access domain command (legacy compatibility)."""
        return self.domain_settings.domain_cmd if self.domain_settings else None
    
    @property
    def dx_dy_dz_cmd(self) -> Any:
        """Access discretization command (legacy compatibility)."""
        return self.domain_settings.dx_dy_dz_cmd if self.domain_settings else None
    
    @property
    def time_window_cmd(self) -> Any:
        """Access time window command (legacy compatibility)."""
        return self.domain_settings.time_window_cmd if self.domain_settings else None
    
    @property
    def rock_positions(self) -> List[Any]:
        """Access rock positions list (backward compatibility)."""
        return self._rock_collection.positions
    
    def validate_all(self) -> List[str]:
        """
        Validate entire scene by checking all components.
        
        Returns:
            List of all validation errors across all components
        """
        errors = []
        
        # Validate each component
        errors.extend(self._geometry_collection.validate())
        errors.extend(self._antenna_config.validate())
        errors.extend(self._rock_collection.validate())
        
        if self.domain_settings:
            errors.extend(self.domain_settings.validate())
        else:
            errors.append("Domain settings not initialized")
        
        # Cross-component validation
        if not self.coordinate_system:
            errors.append("Coordinate system not initialized")
        
        if not self.assembled and self._antenna_config.is_configured:
            errors.append("Scene configured but not assembled")
        
        return errors
    
    def log_issue(
        self, 
        worker: str, 
        issue_type: str, 
        severity: str, 
        description: str,
        context: Dict[str, Any] = None
    ) -> None:
        """Log a quality issue (redirects to WorkOrderSystem)."""
        if self.work_order:
            self.work_order.log_issue(
                worker=worker,
                issue_type=issue_type,
                severity=severity,
                description=description,
                context=context or {}
            )



class Worker(ABC):
    """
    Abstract base class for all production workers.
    
    Each worker is responsible for:
    1. Executing a specific step in scene generation
    2. Performing quality checks after completion
    3. Logging any issues found
    
    Workers should be stateless - all state is passed via SceneCheckpoint.
    """
    name: str = "Worker"  # Override in subclasses
    
    @abstractmethod
    def execute(
        self,
        checkpoint: SceneCheckpoint,
        params: Dict[str, Any],
        materials: Any,  # MaterialWarehouse
        tools: Any       # ToolWarehouse
    ) -> None:
        """
        Perform work on the scene checkpoint.
        
        Args:
            checkpoint: The scene state being built
            params: Sampled scenario parameters
            materials: MaterialWarehouse for getting materials
            tools: ToolWarehouse for validators, writers, etc.
        """
        pass
    
    @abstractmethod
    def quality_check(self, checkpoint: SceneCheckpoint) -> List[str]:
        """
        Validate the work done by this worker.
        
        Returns:
            List of error strings. Empty list means QC passed.
        """
        pass
    
    def _log_issue(
        self,
        checkpoint: SceneCheckpoint,
        issue_type: str,
        severity: str,
        description: str,
        context: Dict[str, Any] = None
    ) -> None:
        """Helper to log issues via checkpoint."""
        checkpoint.log_issue(
            worker=self.name,
            issue_type=issue_type,
            severity=severity,
            description=description,
            context=context
        )

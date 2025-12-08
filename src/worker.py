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
from .gpr_commands import DomainCommand, DxDyDzCommand, TimeWindowCommand

if TYPE_CHECKING:
    from .config import GeneratorConfig
    from .work_order import WorkOrderSystem
    from .scene_descriptor import SceneDefinition


@dataclass
class SceneCheckpoint:
    """
    Snapshot of scene state that can be cloned for variant generation.
    
    The checkpoint holds both physical state (geometry) and logical state (WorkOrderSystem).
    """
    config: 'GeneratorConfig'
    work_order: Optional['WorkOrderSystem'] = None  # Mutable blackboard system
    materials: List[Any] = field(default_factory=list)
    geometry: List[Any] = field(default_factory=list)
    sources: List[Any] = field(default_factory=list)
    receivers: List[Any] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)  # DEPRECATED: Use work_order
    rock_positions: List[Any] = field(default_factory=list)
    assembled: Optional['SceneDefinition'] = None
    
    # Domain-level commands (set once)
    domain_cmd: Any = None
    dx_dy_dz_cmd: Any = None
    time_window_cmd: Any = None
    
    def __post_init__(self):
        """Auto-initialize domain commands if config is present."""
        if self.config:
            if self.domain_cmd is None:
                self.domain_cmd = DomainCommand(self.config.domain_x, self.config.domain_y, self.config.domain_z)
            if self.dx_dy_dz_cmd is None:
                self.dx_dy_dz_cmd = DxDyDzCommand(self.config.dx, self.config.dy, self.config.dz)
            if self.time_window_cmd is None:
                self.time_window_cmd = TimeWindowCommand(self.config.time_window)
    
    def clone(self) -> 'SceneCheckpoint':
        """
        Create a deep copy for variant generation.
        
        Sources and receivers are reset (to be filled by AntennaWorker).
        Geometry and materials are copied (shared structure for variants).
        """
        return SceneCheckpoint(
            config=self.config,  # Config is immutable, share reference
            work_order=self.work_order,  # Share reference to blackboard
            materials=list(self.materials),  # Shallow copy - commands are immutable
            geometry=list(self.geometry),  # Shallow copy
            sources=[],  # Reset - will be filled by AntennaWorker
            receivers=[],  # Reset
            metadata=dict(self.metadata),  # Copy metadata dict
            rock_positions=list(self.rock_positions),  # Copy for QC
            assembled=None,  # Reset assembly on clone
            domain_cmd=self.domain_cmd,
            dx_dy_dz_cmd=self.dx_dy_dz_cmd,
            time_window_cmd=self.time_window_cmd,
        )
    
    def add_material(self, cmd: Any) -> None:
        """Add a material command."""
        self.materials.append(cmd)
    
    def add_geometry(self, cmd: Any) -> None:
        """Add a geometry command (box, cylinder, etc.)."""
        self.geometry.append(cmd)
    
    def add_source(self, cmd: Any) -> None:
        """Add a source command (waveform, dipole)."""
        self.sources.append(cmd)
    
    def add_receiver(self, cmd: Any) -> None:
        """Add a receiver command."""
        self.receivers.append(cmd)
    
    def log_issue(
        self, 
        worker: str, 
        issue_type: str, 
        severity: str, 
        description: str,
        context: Dict[str, Any] = None
    ) -> None:
        """Log a quality issue (Reditects to WorkOrderSystem)."""
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

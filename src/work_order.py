"""
WorkOrder: The central blackboard for Factory Workers.

This module manages the state and parameters shared between workers.
Workers read inputs from the WorkOrder and write their outputs (calculations, stats) back to it.
It includes an audit trail to track which worker modified what data.
"""

from typing import Any, Dict, List, Optional, TYPE_CHECKING
from dataclasses import dataclass, field
from datetime import datetime

if TYPE_CHECKING:
    from .domain.scene_parameters import SceneParameters

@dataclass
class AuditEntry:
    worker: str
    action: str
    key: Optional[str] = None
    value: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass(frozen=True)
class WorkOrder:
    """
    Invariant configuration for a specific scenario generation job.
    
    This is created once by the Simulation Manager and passed down.
    It should NOT be modified by workers.
    """
    id: str
    typed_params: 'SceneParameters'  # Type-safe parameters (required)
    
    @classmethod
    def from_sampled_params(cls, sample_id: str, params: dict) -> 'WorkOrder':
        """
        Factory method for creating WorkOrder from sampled parameters.
        
        Args:
            sample_id: Unique identifier (e.g., "5000" becomes "s_5000")
            params: Dictionary with 'pvc', 'moisture', etc. from sampler
            
        Returns:
            WorkOrder with typed parameters
            
        Example:
            >>> params = {'pvc': 25.0, 'moisture': 0.1}
            >>> wo = WorkOrder.from_sampled_params(5000, params)
            >>> wo.id
            's_5000'
        """
        from .domain import SceneParameters
        
        typed_params = SceneParameters(
            pvc=params.get('pvc', 0.0),
            moisture=params.get('moisture', 0.0),
            ballast_thickness=params.get('ballast_thickness', 0.45),
            pvc_top=params.get('pvc_top', None),
            pvc_bottom=params.get('pvc_bottom', None),
        )
        
        scene_id = f"s_{sample_id:04d}"
        return cls(id=scene_id, typed_params=typed_params)
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get parameter from typed_params.
        
        Example:
            >>> wo = WorkOrder(id="test", typed_params=SceneParameters(pvc=25.0))
            >>> wo.get('pvc', 0.0)
            25.0
        """
        if hasattr(self.typed_params, key):
            return getattr(self.typed_params, key)
        return default
        
    def validate(self) -> None:
        """
        Enforce physical invariants. Fail fast if configuration is impossible.
        
        Note: Most validation now happens in SceneParameters.__post_init__.
        This method handles cross-parameter validation only.
        """
        # Antenna should never be below ground
        if self.typed_params.antenna_offset is not None:
            domain_x = self.typed_params.domain_x or 0.5
            if abs(self.typed_params.antenna_offset) > domain_x / 2:
                raise ValueError(
                    f"WorkOrder Error: antenna_offset {self.typed_params.antenna_offset} "
                    f"exceeds domain bounds"
                )


class WorkOrderSystem:
    """
    The central mutable blackboard that travels through the factory.
    
    Stores the invariant WorkOrder and accumulates:
    - Shared State (Blackboard)
    - Audit Logs
    - Results/Statistics
    """
    def __init__(self, work_order: WorkOrder):
        self._work_order = work_order
        self._blackboard: Dict[str, Any] = {} # Mutable shared state
        self._audit_log: List[AuditEntry] = []
        self._issues: List[Dict[str, Any]] = [] # Quality Control Log
        self._log_audit("System", "INIT", "WorkOrderId", work_order.id)
    
    @property
    def work_order(self) -> WorkOrder:
        """Access the invariant work order."""
        return self._work_order
        
    def get_input(self, key: str, default: Any = None) -> Any:
        """Get an input parameter from the invariant WorkOrder."""
        return self._work_order.get(key, default)
        
    def get(self, key: str, default: Any = None) -> Any:
        """
        Retrieve a value from the blackboard (shared state).
        """
        return self._blackboard.get(key, default)
    
    def set(self, key: str, value: Any, worker_name: str) -> None:
        """
        Write a value to the blackboard.
        """
        self._blackboard[key] = value
        self._log_audit(worker_name, "SET", key, str(value))
        
    def log(self, message: str, worker_name: str) -> None:
        """Log a generic message to the audit trail and console."""
        self._log_audit(worker_name, "LOG", None, message)
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] [{worker_name}] {message}")
    
    def log_issue(self, worker: str, issue_type: str, severity: str, description: str, context: Dict = None) -> None:
        """Log a quality issue (Single Source of QC)."""
        issue = {
            "worker": worker,
            "type": issue_type,
            "severity": severity,
            "description": description,
            "context": context or {},
            "timestamp": datetime.now().isoformat()
        }
        self._issues.append(issue)
        # Also log to audit trail for chronology
        self._log_audit(worker, f"QC_{severity.upper()}", issue_type, description)
        
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] [{worker}] [QC:{severity.upper()}] {description}")
        
    def _log_audit(self, worker: str, action: str, key: Optional[str], value: Optional[str]) -> None:
        self._audit_log.append(AuditEntry(worker, action, key, value))
        
    def export_history(self) -> List[Dict[str, str]]:
        return [
            {
                "timestamp": e.timestamp.isoformat(),
                "worker": e.worker,
                "action": e.action,
                "key": e.key or "",
                "value": e.value or ""
            }
            for e in self._audit_log
        ]
        
    def export_issues(self) -> List[Dict[str, Any]]:
        """Export all quality issues."""
        return list(self._issues)

    def export_metadata(self) -> Dict[str, Any]:
        """Export WorkOrder inputs + blackboard state for metadata logging."""
        # Start with typed params as base
        meta = self._work_order.typed_params.to_dict()
        
        # Overlay Blackboard outputs (Worker results)
        for k, v in self._blackboard.items():
            if isinstance(v, (int, float, str, bool)):
                meta[k] = v
                
        # Critical Identifiers
        meta['sample_id'] = self._work_order.id
        
        return meta

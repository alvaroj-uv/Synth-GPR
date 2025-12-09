"""
WorkOrder: The central blackboard for Factory Workers.

This module manages the state and parameters shared between workers.
Workers read inputs from the WorkOrder and write their outputs (calculations, stats) back to it.
It includes an audit trail to track which worker modified what data.
"""

from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime

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
    params: Dict[str, Any] = field(default_factory=dict)
    
    def get(self, key: str, default: Any = None) -> Any:
        return self.params.get(key, default)
        
    def validate(self) -> None:
        """
        Enforce physical invariants. Fail fast if configuration is impossible.
        """
        # 1. Dimensions
        for dim in ['domain_x', 'domain_y', 'domain_z']:
            val = self.params.get(dim)
            if val is not None and val <= 0:
                raise ValueError(f"WorkOrder Error: {dim} must be positive, got {val}")
                
        # 2. Percentages (PVC)
        pvc = self.params.get('pvc')
        if pvc is not None and not (0 <= pvc <= 100):
            raise ValueError(f"WorkOrder Error: PVC must be 0-100, got {pvc}")
            
        # 3. Fractions (Moisture)
        moisture = self.params.get('moisture')
        if moisture is not None and not (0 <= moisture <= 1.0):

            raise ValueError(f"WorkOrder Error: moisture must be 0-1.0, got {moisture}")
            
        # 4. Geometry Invariants (Fail Fast)
        # Antenna should never be below ground
        offset = self.params.get('antenna_offset')
        if offset is not None:
             if abs(offset) > self.params.get('domain_x', 0.5) / 2:
                 raise ValueError(f"WorkOrder Error: antenna_offset {offset} exceeds domain bounds")


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
        """Get an input parameter from the invariant key."""
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
        """
        Extract complete metadata for the scenario.
        Combines Input Params and Blackboard Output.
        """
        # Start with input parameters
        meta = self._work_order.params.copy()
        
        # Overlay Blackboard outputs (Worker results)
        # e.g. rock_count, highest_rock_y
        for k, v in self._blackboard.items():
            if isinstance(v, (int, float, str, bool)):
                meta[k] = v
                
        # Critical Identifiers
        meta['sample_id'] = self._work_order.id
        
        return meta

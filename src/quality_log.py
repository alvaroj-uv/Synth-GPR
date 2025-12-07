"""
Quality Logging System for Scenario Generation.

This module provides data structures for tracking quality issues
during scenario generation. Workers can log issues they detect,
and the system collects them for analysis and learning.

Usage:
    log = QualityLog()
    log.log_issue(
        worker="BallastWorker",
        issue_type="floating_rock",
        severity="warning",
        description="Rock at (0.3, 0.7) has no support below",
        context={"rock_x": 0.3, "rock_y": 0.7, "rock_radius": 0.02}
    )
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Any, Optional
from enum import Enum


class IssueSeverity(Enum):
    """Severity levels for quality issues."""
    INFO = "info"           # Minor observation, no action needed
    WARNING = "warning"     # Potential issue, may need attention
    ERROR = "error"         # Definite issue, requires repair
    CRITICAL = "critical"   # Blocks production, must fix


class IssueType(Enum):
    """Types of quality issues that can occur."""
    FLOATING_ROCK = "floating_rock"       # Rock with no support beneath
    ROCK_OVERLAP = "rock_overlap"         # Two rocks intersecting
    OUT_OF_BOUNDS = "out_of_bounds"       # Geometry outside domain
    ANTENNA_CLEARANCE = "antenna_clearance"  # Rock too close to antenna
    MATERIAL_UNDEFINED = "material_undefined"  # Used undefined material
    WAVEFORM_UNDEFINED = "waveform_undefined"  # Used undefined waveform
    NEGATIVE_DIMENSION = "negative_dimension"  # Invalid geometry size


class RepairAction(Enum):
    """Actions taken to repair issues."""
    NONE = "none"                     # Not repaired
    PATCHED_WITH_FOULING = "patched"  # Added fouling beneath
    SETTLED_ROCK = "settled"          # Moved rock downward
    ERASED_ROCK = "erased"            # Removed rock entirely
    SHRUNK_GEOMETRY = "shrunk"        # Reduced geometry size


@dataclass
class QualityIssue:
    """
    A single quality issue logged by a worker.
    
    Attributes:
        worker_name: Name of the worker that detected the issue
        issue_type: Category of the issue (from IssueType enum)
        severity: How serious the issue is (from IssueSeverity enum)
        description: Human-readable explanation
        context: Parameters/values that caused the issue (for ML learning)
        repair_action: How the issue was fixed (if at all)
        timestamp: When the issue was logged
    """
    worker_name: str
    issue_type: str
    severity: str
    description: str
    context: Dict[str, Any]
    repair_action: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for export."""
        return {
            "worker": self.worker_name,
            "type": self.issue_type,
            "severity": self.severity,
            "description": self.description,
            "repaired": self.repair_action is not None,
            "repair_action": self.repair_action,
            "timestamp": self.timestamp.isoformat(),
            **self.context  # Flatten context for ML
        }


@dataclass
class QualityLog:
    """
    Central quality log shared across all workers.
    
    Tracks issues detected during scene generation for:
    1. Repair by the AssemblerWorker
    2. Export for ML analysis of bad parameter combinations
    
    Example:
        log = QualityLog()
        log.log_issue("BallastWorker", "floating_rock", "warning", 
                      "Rock floating", {"rock_y": 0.7})
        print(f"Total issues: {len(log.issues)}")
    """
    issues: List[QualityIssue] = field(default_factory=list)
    repairs: List[Dict[str, Any]] = field(default_factory=list)
    
    def log_issue(
        self,
        worker: str,
        issue_type: str,
        severity: str,
        description: str,
        context: Dict[str, Any]
    ) -> QualityIssue:
        """
        Log a new quality issue.
        
        Args:
            worker: Name of the worker detecting the issue
            issue_type: Category (use IssueType enum values)
            severity: How serious (use IssueSeverity enum values)
            description: Human-readable message
            context: Dict of parameters that caused issue
            
        Returns:
            The created QualityIssue for optional further modification
        """
        issue = QualityIssue(
            worker_name=worker,
            issue_type=issue_type,
            severity=severity,
            description=description,
            context=context
        )
        self.issues.append(issue)
        return issue
    
    def log_repair(self, issue: QualityIssue, action: str) -> None:
        """
        Record that an issue was repaired.
        
        Args:
            issue: The QualityIssue that was fixed
            action: What action was taken (use RepairAction enum values)
        """
        issue.repair_action = action
        self.repairs.append({
            "issue_type": issue.issue_type,
            "action": action,
            "timestamp": datetime.now().isoformat()
        })
    
    def get_issues_by_worker(self, worker: str) -> List[QualityIssue]:
        """Get all issues logged by a specific worker."""
        return [i for i in self.issues if i.worker_name == worker]
    
    def get_issues_by_type(self, issue_type: str) -> List[QualityIssue]:
        """Get all issues of a specific type."""
        return [i for i in self.issues if i.issue_type == issue_type]
    
    def get_unrepaired_issues(self) -> List[QualityIssue]:
        """Get issues that haven't been repaired yet."""
        return [i for i in self.issues if i.repair_action is None]
    
    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of all logged issues."""
        from collections import Counter
        return {
            "total_issues": len(self.issues),
            "total_repairs": len(self.repairs),
            "by_type": dict(Counter(i.issue_type for i in self.issues)),
            "by_severity": dict(Counter(i.severity for i in self.issues)),
            "by_worker": dict(Counter(i.worker_name for i in self.issues)),
            "repair_rate": len(self.repairs) / max(len(self.issues), 1)
        }
    
    def export_for_ml(self) -> List[Dict[str, Any]]:
        """
        Export issues as list of dicts for ML analysis.
        
        Each dict contains flattened context parameters,
        making it easy to convert to a DataFrame.
        """
        return [issue.to_dict() for issue in self.issues]
    
    def clear(self) -> None:
        """Clear all issues and repairs."""
        self.issues.clear()
        self.repairs.clear()

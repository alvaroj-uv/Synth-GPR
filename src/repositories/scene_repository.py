"""
Abstract Scene Repository interface.

Defines the contract for scene persistence, following the Repository pattern.
This allows swapping storage backends (filesystem, database, cloud) without
changing domain logic.
"""

from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from pathlib import Path
from dataclasses import dataclass
import json


@dataclass
class SceneMetadata:
    """
    Metadata for a generated scene.
    
    This is a lightweight representation suitable for queries and filtering.
    Attributes match the CSV metadata currently saved.
    """
    id: str
    label: str  # 'C', 'MF', 'F', 'HF'
    pvc: float
    fi: float
    classification: str  # 'Clean', 'Moderately Fouled', etc.
    porosity: float
    rock_count: int
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for CSV/JSON serialization."""
        return {
            'id': self.id,
            'label': self.label,
            'pvc': self.pvc,
            'fi': self.fi,
            'classification': self.classification,
            'porosity': self.porosity,
            'rock_count': self.rock_count,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SceneMetadata':
        """Create from dictionary."""
        return cls(
            id=data['id'],
            label=data['label'],
            pvc=float(data['pvc']),
            fi=float(data['fi']),
            classification=data['classification'],
            porosity=float(data['porosity']),
            rock_count=int(data['rock_count']),
        )


class SceneRepository(ABC):
    """
    Abstract repository for GPR scene persistence.
    
    Responsibilities:
    - Save/retrieve complete scenes
    - Query scenes by metadata (classification, PVC range, etc.)
    - Abstract storage implementation details
    
    This allows domain logic to remain clean while enabling:
    - Easy testing (InMemoryRepository)
    - Flexible backends (filesystem, SQLite, cloud storage)
    - Performance optimization (caching, indexing)
    """
    
    @abstractmethod
    def save(
        self,
        scene_id: str,
        gprmax_content: str,
        metadata: SceneMetadata
    ) -> None:
        """
        Save a complete scene.
        
        Args:
            scene_id: Unique identifier (e.g., "s_0001")
            gprmax_content: Complete .in file content
            metadata: Scene metadata for querying
        """
        pass
    
    @abstractmethod
    def find_by_id(self, scene_id: str) -> Optional[str]:
        """
        Retrieve .in file content by ID.
        
        Args:
            scene_id: Scene identifier
        
        Returns:
            gprMax .in file content, or None if not found
        """
        pass
    
    @abstractmethod
    def get_metadata(self, scene_id: str) -> Optional[SceneMetadata]:
        """
        Retrieve metadata for a scene.
        
        Args:
            scene_id: Scene identifier
        
        Returns:
            SceneMetadata or None if not found
        """
        pass
    
    @abstractmethod
    def find_all(self) -> List[SceneMetadata]:
        """
        List all scene metadata.
        
        Returns:
            List of all scene metadata (sorted by ID)
        """
        pass
    
    @abstractmethod
    def find_by_classification(self, classification: str) -> List[SceneMetadata]:
        """
        Query scenes by fouling classification.
        
        Args:
            classification: 'Clean', 'Moderately Fouled', 'Fouled', 'Highly Fouled'
        
        Returns:
            List of matching scene metadata
        """
        pass
    
    @abstractmethod
    def count(self) -> int:
        """
        Count total scenes in repository.
        
        Returns:
            Total number of scenes
        """
        pass
    
    @abstractmethod
    def exists(self, scene_id: str) -> bool:
        """
        Check if scene exists.
        
        Args:
            scene_id: Scene identifier
        
        Returns:
            True if scene exists
        """
        pass


class InMemorySceneRepository(SceneRepository):
    """
    In-memory repository for testing.
    
    Stores scenes in dictionaries for fast access without file I/O.
    Useful for unit tests and development.
    """
    
    def __init__(self):
        """Initialize empty in-memory storage."""
        self._scenes: Dict[str, str] = {}  # id -> .in content
        self._metadata: Dict[str, SceneMetadata] = {}  # id -> metadata
    
    def save(
        self,
        scene_id: str,
        gprmax_content: str,
        metadata: SceneMetadata
    ) -> None:
        """Save scene to memory."""
        self._scenes[scene_id] = gprmax_content
        self._metadata[scene_id] = metadata
    
    def find_by_id(self, scene_id: str) -> Optional[str]:
        """Retrieve .in content from memory."""
        return self._scenes.get(scene_id)
    
    def get_metadata(self, scene_id: str) -> Optional[SceneMetadata]:
        """Retrieve metadata from memory."""
        return self._metadata.get(scene_id)
    
    def find_all(self) -> List[SceneMetadata]:
        """List all metadata in memory."""
        return sorted(self._metadata.values(), key=lambda m: m.id)
    
    def find_by_classification(self, classification: str) -> List[SceneMetadata]:
        """Filter metadata by classification."""
        return [
            m for m in self._metadata.values()
            if m.classification == classification
        ]
    
    def count(self) -> int:
        """Count scenes in memory."""
        return len(self._scenes)
    
    def exists(self, scene_id: str) -> bool:
        """Check if scene exists in memory."""
        return scene_id in self._scenes
    
    def clear(self) -> None:
        """Clear all data (test helper)."""
        self._scenes.clear()
        self._metadata.clear()

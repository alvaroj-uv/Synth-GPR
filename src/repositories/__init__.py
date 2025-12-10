"""
Repository interfaces for scene persistence.

Implements the Repository pattern from Domain-Driven Design,
abstracting persistence concerns from domain logic.
"""

from .scene_repository import SceneRepository, SceneMetadata, InMemorySceneRepository
from .filesystem_repository import FileSystemSceneRepository

__all__ = [
    "SceneRepository",
    "SceneMetadata",
    "FileSystemSceneRepository",
    "InMemorySceneRepository",
]

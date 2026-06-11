"""
Scene domain model: plain dataclasses describing a parsed gprMax scene.

This module is the data contract between the parser (``parser.py``) and every
renderer (``drawing.py``, ``scene_3d.py``, dashboards). It must stay free of
parsing and matplotlib concerns — geometry in, geometry out.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class AbstractGeom(ABC):
    x: float = field(init=False)
    y: float = field(init=False)
    z: float = field(init=False)

    @abstractmethod
    def _set_anchor(self) -> None:
        """Set the shared x/y/z anchor for this geometry."""

    @property
    def xyz(self) -> tuple[float, float, float]:
        return self.x, self.y, self.z


@dataclass
class BoxGeom(AbstractGeom):
    x1: float
    y1: float
    x2: float
    y2: float
    material: str
    z1: float = 0.0   # depth extent (3D); ignored by 2D drawing
    z2: float = 0.0

    def __post_init__(self) -> None:
        self._set_anchor()

    def _set_anchor(self) -> None:
        self.x = (self.x1 + self.x2) / 2.0
        self.y = (self.y1 + self.y2) / 2.0
        self.z = (self.z1 + self.z2) / 2.0


@dataclass
class CylinderGeom(AbstractGeom):
    x1: float
    y1: float
    z1: float
    x2: float
    y2: float
    z2: float
    radius: float
    material: str

    def __post_init__(self) -> None:
        self._set_anchor()

    def _set_anchor(self) -> None:
        self.x = (self.x1 + self.x2) / 2.0
        self.y = (self.y1 + self.y2) / 2.0
        self.z = (self.z1 + self.z2) / 2.0


@dataclass
class TriangleGeom(AbstractGeom):
    x1: float; y1: float
    x2: float; y2: float
    x3: float; y3: float
    material: str
    z1: float = 0.0
    z2: float = 0.0
    z3: float = 0.0

    def __post_init__(self) -> None:
        self._set_anchor()

    def _set_anchor(self) -> None:
        self.x = (self.x1 + self.x2 + self.x3) / 3.0
        self.y = (self.y1 + self.y2 + self.y3) / 3.0
        self.z = (self.z1 + self.z2 + self.z3) / 3.0


@dataclass
class SphereGeom(AbstractGeom):
    x: float
    y: float
    z: float
    radius: float
    material: str

    def _set_anchor(self) -> None:
        pass


@dataclass
class PolygonGeom(AbstractGeom):
    vertices: list  # [(x, y), ...]
    material: str

    def __post_init__(self) -> None:
        self._set_anchor()

    def _set_anchor(self) -> None:
        # Anchor at the vertex centroid so .xyz works like other geometries
        # (z stays 0: polygons are 2D cross-section particles).
        if self.vertices:
            self.x = sum(v[0] for v in self.vertices) / len(self.vertices)
            self.y = sum(v[1] for v in self.vertices) / len(self.vertices)
        else:
            self.x = 0.0
            self.y = 0.0
        self.z = 0.0


@dataclass
class AntennaPos:
    x: float
    y: float
    z: float = 0.0


@dataclass
class SceneData:
    domain_x: float = 0.0
    domain_y: float = 0.0
    domain_z: float = 0.0
    title: str = ""
    boxes: list[BoxGeom] = field(default_factory=list)
    cylinders: list[CylinderGeom] = field(default_factory=list)
    triangles: list[TriangleGeom] = field(default_factory=list)
    spheres: list[SphereGeom] = field(default_factory=list)
    polygons: list[PolygonGeom] = field(default_factory=list)
    tx: Optional[AntennaPos] = None
    receivers: list[AntennaPos] = field(default_factory=list)
    meta: dict = field(default_factory=dict)

    @property
    def geometries(self) -> list[AbstractGeom]:
        return [*self.boxes, *self.cylinders, *self.triangles, *self.spheres, *self.polygons]

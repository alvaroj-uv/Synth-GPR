
import math
from dataclasses import dataclass, field
from typing import Optional, List, Tuple, Any


@dataclass
class Rock:
    """
    Represents a single rock in the ballast.

    A rock is always defined by its circle (x, y, radius). The polygon
    representation (vertices) is optional — set by calling polygonize()
    on a packing strategy, or by the physics-based Mbubia generator.

    Attributes:
        x:        Horizontal center (m)
        y:        Vertical center (m)
        radius:   Circle radius (m) — bounding circle for polygon rocks
        z_start:  Extrusion start (m)
        z_end:    Extrusion end (m)
        vertices: 2D polygon vertices [(x, y), ...] — None for circle rocks
        material: Material name string — None when assigned by the worker layer
    """
    x: float
    y: float
    radius: float
    z_start: float = 0.0
    z_end: float = 0.005
    vertices: Optional[List[Tuple[float, float]]] = field(default=None, repr=False)
    material: Optional[str] = None

    @property
    def is_polygon(self) -> bool:
        """True if this rock has explicit polygon geometry."""
        return self.vertices is not None and len(self.vertices) >= 3

    @property
    def centroid(self) -> Tuple[float, float]:
        """Centroid of polygon vertices, or (x, y) for circle rocks."""
        if not self.is_polygon:
            return (self.x, self.y)
        xs = [v[0] for v in self.vertices]
        ys = [v[1] for v in self.vertices]
        return (sum(xs) / len(xs), sum(ys) / len(ys))

    def __str__(self) -> str:
        shape = f"{len(self.vertices)}-gon" if self.is_polygon else "circle"
        mat = f", {self.material}" if self.material else ""
        return f"Rock({shape}, center=({self.x:.3f}, {self.y:.3f}), r={self.radius:.3f}m{mat})"

    def __repr__(self) -> str:
        return (f"Rock(x={self.x}, y={self.y}, radius={self.radius}, "
                f"z_start={self.z_start}, z_end={self.z_end}, "
                f"polygon={self.is_polygon}, material={self.material})")


@dataclass
class PackingBounds:
    """
    Defines the rectangular bounding box for rock placement.
    """
    x_min: float
    x_max: float
    y_min: float
    y_max: float

    @property
    def width(self) -> float:
        return self.x_max - self.x_min

    @property
    def height(self) -> float:
        return self.y_max - self.y_min

    @property
    def area(self) -> float:
        return self.width * self.height


@dataclass
class Layer:
    """
    A named stratum within a multi-layer ballast scene.

    Learned from Mbubia: realistic GPR scenes need independent
    physics simulations per layer, composited via painter's algorithm.

    Attributes:
        name:     Human-readable label ("upper", "lower", "transition", …)
        material: Material identifier string (assigned by the EM worker layer,
                  not the physics packer)
        y_min:    Absolute y-coordinate of layer bottom (m)
        y_max:    Absolute y-coordinate of layer top (m)
        priority: Painter's algorithm draw order — lower priority drawn first,
                  higher priority drawn on top. Overlapping layers with different
                  priorities create gradational mixing zones.
    """
    name: str
    material: str
    y_min: float
    y_max: float
    priority: int = 0

    @property
    def height(self) -> float:
        """Layer thickness in metres."""
        return self.y_max - self.y_min

    @property
    def bounds(self) -> PackingBounds:
        """PackingBounds for this layer (x-extent set to zero; caller fills x)."""
        return PackingBounds(x_min=0.0, x_max=0.0, y_min=self.y_min, y_max=self.y_max)




import math
from dataclasses import dataclass, field
from typing import Optional, List, Tuple

import numpy as np


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
    # 3-D centre coordinate. None → 2-D rock (z_start/z_end are the thin-slab
    # extrusion for 2-D rendering). Set → 3-D sphere centred at (x, y, z).
    z: Optional[float] = None

    @property
    def ndim(self) -> int:
        """2 for a planar rock, 3 when a z centre is set (sphere)."""
        return 3 if self.z is not None else 2

    @property
    def position(self) -> Tuple[float, ...]:
        """(x, y) in 2-D, (x, y, z) in 3-D — the dimension-agnostic centre."""
        return (self.x, self.y, self.z) if self.z is not None else (self.x, self.y)

    @property
    def is_polygon(self) -> bool:
        """True if this rock has explicit polygon geometry (2-D only)."""
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
    """Axis-aligned packing region — 2-D by default, 3-D when z bounds are set.

    Dimension-agnostic: ``ndim`` reports 2 or 3, and ``lengths`` / ``mins`` give
    the per-axis spans and origins so a packer can pack into either without
    knowing the dimension up front.
    """
    x_min: float
    x_max: float
    y_min: float
    y_max: float
    z_min: Optional[float] = None
    z_max: Optional[float] = None

    @property
    def ndim(self) -> int:
        return 3 if (self.z_min is not None and self.z_max is not None) else 2

    @property
    def width(self) -> float:
        return self.x_max - self.x_min

    @property
    def height(self) -> float:
        return self.y_max - self.y_min

    @property
    def depth(self) -> float:
        return (self.z_max - self.z_min) if self.ndim == 3 else 0.0

    @property
    def area(self) -> float:
        return self.width * self.height

    @property
    def volume(self) -> float:
        """3-D volume (== area in 2-D)."""
        return self.area * self.depth if self.ndim == 3 else self.area

    @property
    def lengths(self) -> List[float]:
        """Per-axis spans: [w, h] in 2-D, [w, h, d] in 3-D."""
        return [self.width, self.height, self.depth] if self.ndim == 3 else [self.width, self.height]

    @property
    def mins(self) -> List[float]:
        """Per-axis origins: [x_min, y_min] or [x_min, y_min, z_min]."""
        return [self.x_min, self.y_min, self.z_min] if self.ndim == 3 else [self.x_min, self.y_min]


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


def rip_polygon_vertices(
    cx: float,
    cy: float,
    r_mean: float,
    rng: Optional[np.random.Generator] = None,
    n_vertices_range: Tuple[int, int] = (8, 12),
    roughness: float = 0.25,
) -> List[Tuple[float, float]]:
    """Build one Random Irregular Polygon (RIP, Li et al. 2023) centred at
    (cx, cy) with mean radius r_mean:

        vertex_i = (r_mean + delta_r_i) * [cos(theta_i), sin(theta_i)]

    with uniform angular base plus small jitter to break regular symmetry,
    and per-vertex radial perturbation delta_r_i in [-roughness, +roughness] *
    r_mean.

    Shape-only helper, decoupled from any packing/placement algorithm — the
    RSA-based rip_packing.RIPPacking uses this internally for its own placed
    rocks, but it can equally be applied to circles from ANY packer (pymunk,
    circlify, rcpgen, ...) to get Li-2023-style irregular polygon rocks
    without being tied to RIP's own RSA placement. See
    layer_scene_builder._pack_layer_rocks's ``rock_shape="rip"`` option.
    """
    rng = rng if rng is not None else np.random.default_rng()
    n = int(rng.integers(n_vertices_range[0], n_vertices_range[1] + 1))

    angles = np.linspace(0.0, 2.0 * math.pi, n, endpoint=False)
    angle_jitter = rng.uniform(-math.pi / n * 0.4, math.pi / n * 0.4, n)
    angles = np.sort(angles + angle_jitter)

    radii = r_mean * (1.0 + rng.uniform(-roughness, roughness, n))

    return [
        (cx + float(r) * math.cos(float(a)), cy + float(r) * math.sin(float(a)))
        for r, a in zip(radii, angles)
    ]



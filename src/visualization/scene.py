from __future__ import annotations
from abc import ABC, abstractmethod
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional
import re

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from matplotlib.axes import Axes

from ..file_reader import parse_metadata_comments
from .materials import LEGEND_ORDER, MATERIALS, MaterialStyle, get_style, jitter_color


# ── Data model ────────────────────────────────────────────────────────────────

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

    def _set_anchor(self) -> None:
        pass


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


# ── Parser ────────────────────────────────────────────────────────────────────

def parse_in_file(path: Path) -> SceneData:
    """Parse a gprMax .in file into SceneData (single 2D + 3D geometry parser).

    Handles: #domain, #title, #box, #fractal_box, #triangle, #cylinder, #sphere, #polygon,
    #hertzian_dipole, #rx, the ``antenna_like_GSSI(...)`` python-call line, and
    ``## key: value`` metadata comments (JSON-decoded via
    ``file_reader.parse_metadata_comments``). Z-coordinates are captured so the
    same SceneData drives both the 2D projection and the 3D orthographic views.
    """
    scene = SceneData()
    with open(path, encoding="utf-8", errors="replace") as fh:
        lines = fh.readlines()

    scene.meta = parse_metadata_comments(lines)

    for raw in lines:
        line = raw.strip()
        if not line:
            continue

        # Antenna inserted via a #python block: the call line does NOT start
        # with '#', so handle it before the '#'-only guard. Draw a stand-in
        # case box + tx marker from the call args (used by the 3D views).
        if line.startswith("antenna_like_GSSI"):
            args = re.findall(r"-?\d+\.?\d*(?:e-?\d+)?", line.split("(", 1)[1])
            if len(args) >= 3:
                cx, cy, zs = float(args[0]), float(args[1]), float(args[2])
                case = (0.300, 0.300, 0.178) if "400" in line else (0.170, 0.108, 0.045)
                scene.boxes.append(BoxGeom(
                    x1=cx - case[0] / 2, y1=cy - case[1] / 2, z1=zs,
                    x2=cx + case[0] / 2, y2=cy + case[1] / 2, z2=zs + case[2],
                    material="antenna",
                ))
                scene.tx = AntennaPos(x=cx, y=cy, z=zs)
            continue

        if not line.startswith("#"):
            continue
        tokens = line.split()
        if not tokens:
            continue
        cmd = tokens[0]

        if cmd == "#title:":
            scene.title = " ".join(tokens[1:])
        elif cmd == "#domain:":
            scene.domain_x = float(tokens[1])
            scene.domain_y = float(tokens[2])
            if len(tokens) > 3:
                scene.domain_z = float(tokens[3])
        elif cmd == "#box:":
            # #box: x1 y1 z1 x2 y2 z2 material
            scene.boxes.append(BoxGeom(
                x1=float(tokens[1]), y1=float(tokens[2]), z1=float(tokens[3]),
                x2=float(tokens[4]), y2=float(tokens[5]), z2=float(tokens[6]),
                material=tokens[7],
            ))
        elif cmd == "#fractal_box:":
            # #fractal_box: x1 y1 z1 x2 y2 z2 frac_dim wx wy wz n_mat soil box_id [seed]
            # Rendered like a box of its soil material (heterogeneous fill).
            scene.boxes.append(BoxGeom(
                x1=float(tokens[1]), y1=float(tokens[2]), z1=float(tokens[3]),
                x2=float(tokens[4]), y2=float(tokens[5]), z2=float(tokens[6]),
                material=tokens[12],
            ))
        elif cmd == "#triangle:":
            # #triangle: x1 y1 z1 x2 y2 z2 x3 y3 z3 thickness material
            material = tokens[11] if len(tokens) > 11 else tokens[10]
            scene.triangles.append(TriangleGeom(
                x1=float(tokens[1]), y1=float(tokens[2]),
                x2=float(tokens[4]), y2=float(tokens[5]),
                x3=float(tokens[7]), y3=float(tokens[8]),
                material=material,
                z1=float(tokens[3]), z2=float(tokens[6]), z3=float(tokens[9]),
            ))
        elif cmd == "#sphere:":
            # #sphere: x y z radius material
            scene.spheres.append(SphereGeom(
                x=float(tokens[1]), y=float(tokens[2]), z=float(tokens[3]),
                radius=float(tokens[4]), material=tokens[5],
            ))
        elif cmd == "#cylinder:":
            # #cylinder: x1 y1 z1 x2 y2 z2 radius material
            scene.cylinders.append(CylinderGeom(
                x1=float(tokens[1]), y1=float(tokens[2]), z1=float(tokens[3]),
                x2=float(tokens[4]), y2=float(tokens[5]), z2=float(tokens[6]),
                radius=float(tokens[7]),
                material=tokens[8],
            ))
        elif cmd == "#polygon:":
            # #polygon: n_vertices x1 y1 z1 x2 y2 z2 ... material
            n = int(tokens[1])
            verts = [(float(tokens[2 + i*3]), float(tokens[3 + i*3])) for i in range(n)]
            material = tokens[2 + n*3]
            scene.polygons.append(PolygonGeom(vertices=verts, material=material))
        elif cmd == "#hertzian_dipole:":
            # #hertzian_dipole: polarisation x y z waveform_id
            scene.tx = AntennaPos(x=float(tokens[2]), y=float(tokens[3]),
                                  z=float(tokens[4]))
        elif cmd == "#rx:":
            # #rx: x y z
            scene.receivers.append(AntennaPos(
                x=float(tokens[1]), y=float(tokens[2]), z=float(tokens[3]),
            ))

    return scene


# ── Geometry renderer ─────────────────────────────────────────────────────────
# Material appearance (colors, hatches, labels, per-rock HSV jitter) is NOT
# defined here — it comes exclusively from .materials (the single registry
# shared with the 3D renderer). Add new materials there, not in this module.

def _rocks_y_max(scene: SceneData) -> float:
    """Return the highest Y coordinate of any ballast rock geometry.

    Used to auto-zoom the viewport when rocks occupy only a small fraction of
    the full domain height (e.g. generic pipeline with a large air gap above).
    Returns 0.0 if no rock geometry is present.
    """
    y = 0.0
    for tri in scene.triangles:
        if tri.material.startswith("bal_rock"):
            y = max(y, tri.y1, tri.y2, tri.y3)
    for cyl in scene.cylinders:
        if cyl.material.startswith("bal_rock"):
            y = max(y, cyl.y + cyl.radius)
    for poly in scene.polygons:
        if poly.vertices:
            y = max(y, max(v[1] for v in poly.vertices))
    return y


def _view_y_max(scene: SceneData, headroom: float = 0.12) -> float:
    """Y-axis upper limit for rendering.

    - If rocks occupy < 60 % of domain height, zoom in (generic pipeline with air gap).
    - Always extends to include antenna position when above domain_y (Mbubia scenes).
    """
    rock_top = _rocks_y_max(scene)
    if rock_top > 0 and rock_top < 0.6 * scene.domain_y:
        y_max = rock_top * (1.0 + headroom)
    else:
        y_max = scene.domain_y

    # Include antenna if it sits above the current view (e.g. Mbubia monostatic)
    if scene.tx and scene.tx.y > y_max:
        y_max = scene.tx.y * (1.0 + 0.06)  # 6 % headroom above antenna

    return y_max


def draw_geometry(ax: Axes, scene: SceneData) -> None:
    """Draw boxes, cylinders, antennas, MC box, boundary lines, and legend."""
    dx, dy = scene.domain_x, scene.domain_y
    ax.set_facecolor(get_style("free_space").color)

    seen_mats: set[str] = set()

    for box in scene.boxes:
        style = get_style(box.material)
        ax.add_patch(mpatches.Rectangle(
            (box.x1, box.y1), box.x2 - box.x1, box.y2 - box.y1,
            facecolor=style.color,
            edgecolor="black" if style.hatch else "none",
            linewidth=0.4,
            hatch=style.hatch,
            zorder=1,
        ))
        seen_mats.add(box.material)

    # Triangles are fan-triangulated from the rock centre (x1,y1 is always the
    # shared apex), so we group by centre to assign one jittered colour per rock.
    # Which materials get jitter is decided by the registry (base_hsv set).
    _rock_groups: dict = defaultdict(list)
    _other_tris = []
    for tri in scene.triangles:
        if get_style(tri.material).base_hsv is not None:
            _rock_groups[(round(tri.x1, 5), round(tri.y1, 5), tri.material)].append(tri)
        else:
            _other_tris.append(tri)

    for tri in _other_tris:
        style = get_style(tri.material, fallback_color="#AAAAAA")
        ax.add_patch(mpatches.Polygon(
            [(tri.x1, tri.y1), (tri.x2, tri.y2), (tri.x3, tri.y3)],
            facecolor=style.color, edgecolor="#333333", linewidth=0.25, zorder=2,
        ))
        seen_mats.add(tri.material)

    _rng = np.random.default_rng(42)
    for (_, _, mat), tris in _rock_groups.items():
        color = jitter_color(mat, _rng)
        for tri in tris:
            ax.add_patch(mpatches.Polygon(
                [(tri.x1, tri.y1), (tri.x2, tri.y2), (tri.x3, tri.y3)],
                facecolor=color, edgecolor=(0, 0, 0, 0.2), linewidth=0.2, zorder=2,
            ))
        seen_mats.add(mat)

    for cyl in scene.cylinders:
        style = get_style(cyl.material, fallback_color="#AAAAAA")
        ax.add_patch(mpatches.Circle(
            (cyl.x, cyl.y), cyl.radius,
            facecolor=style.color, edgecolor="#333333", linewidth=0.25, zorder=2,
        ))
        seen_mats.add(cyl.material)

    for poly in scene.polygons:
        # Per-grain jitter when the registry defines a base_hsv, flat otherwise
        color = jitter_color(poly.material, _rng)
        if color is None:
            color = get_style(poly.material, fallback_color="#AAAAAA").color
        ax.add_patch(mpatches.Polygon(
            poly.vertices, closed=True,
            facecolor=color, edgecolor=(0, 0, 0, 0.2), linewidth=0.2, zorder=2,
        ))
        seen_mats.add(poly.material)

    if scene.tx:
        ax.plot(scene.tx.x, scene.tx.y, marker="v", color="#E82020",
                markersize=7, zorder=5, linestyle="none", label="TX")
    
    # Plot all receivers (Multi-Offset support - Roncoroni 2025)
    for i, rx in enumerate(scene.receivers):
        label = "RX" if i == 0 else None  # Only first one for legend
        ax.plot(rx.x, rx.y, marker="^", color="#1060D0",
                markersize=7, zorder=5, linestyle="none", label=label)

    # Virtual Sieve Layer Box (Orange dashed)
    mc_y_min = scene.meta.get("mc_y_min")
    mc_y_max = scene.meta.get("mc_y_max")
    if mc_y_min is not None and mc_y_max is not None:
        ax.add_patch(mpatches.Rectangle(
            (0, float(mc_y_min)), dx, float(mc_y_max) - float(mc_y_min),
            linewidth=1.5, edgecolor="#FF6600", facecolor="none",
            linestyle="--", zorder=6, label="Sieve Box"
        ))

    # MC Global Ballast Box (Green dotted)
    b_bottom = scene.meta.get("ballast_bottom_y")
    b_top = scene.meta.get("ballast_top_y")
    if b_bottom is not None and b_top is not None:
        ax.add_patch(mpatches.Rectangle(
            (0, float(b_bottom)), dx, float(b_top) - float(b_bottom),
            linewidth=1.5, edgecolor="#00AA00", facecolor="none",
            linestyle=":", zorder=6, label="MC Ballast"
        ))
        
    # Virtual LDCP Scan Line (Red solid line down the middle)
    ldcp_x = scene.meta.get("ldcp_x")
    if ldcp_x is not None and b_bottom is not None and b_top is not None:
        ax.plot([float(ldcp_x), float(ldcp_x)], [float(b_bottom), float(b_top)],
                color="#E82020", linewidth=2.0, linestyle="-", zorder=7, label="LDCP Scan")

    boundary_ys: set[float] = set()
    for box in scene.boxes:
        if box.material in ("subgrade", "formation", "bal_foul_granular"):
            boundary_ys.update({round(box.y1, 6), round(box.y2, 6)})
    for y in sorted(boundary_ys):
        if 0 < y < dy:
            ax.axhline(y, color="#AAAAAA", linewidth=0.6, linestyle="--", zorder=0)

    ax.add_patch(mpatches.Rectangle(
        (0, 0), dx, dy,
        fill=False, edgecolor="black", linewidth=1.5, zorder=7,
    ))

    ax.set_xlim(0, dx)
    ax.set_ylim(0, _view_y_max(scene))
    ax.set_aspect("equal")
    ax.set_xlabel("x (m)", fontsize=9)
    ax.set_ylabel("y (m)", fontsize=9)
    ax.tick_params(labelsize=8)
    ax.grid(visible=True, alpha=0.15, linewidth=0.4)

    _draw_axis_break(ax, "top")
    _draw_axis_break(ax, "bottom")
    _draw_legend(ax, scene, seen_mats, mc_y_min)
    _draw_meta_annotation(ax, scene)


def render_geometry_figure(
    scene: SceneData,
    title: str = "",
    dpi: int = 150,
    max_height: float = 14.0,
    base_width: float = 6.0,
) -> tuple:
    """Create a standalone figure for a single geometry panel.

    Returns (fig, ax) ready for saving or further annotation.
    unified_visualizer.py uses this when it needs a self-contained
    geometry image (not a subplot inside a dashboard).
    """
    # Scale both axes proportionally so wide domains get wide figures.
    # 3.5 inches per metre gives a readable scale for scenes up to ~5m wide.
    INCHES_PER_METRE = 3.5
    content_h = _view_y_max(scene)
    fig_w = min(scene.domain_x * INCHES_PER_METRE, 16.0)
    fig_h = min(content_h   * INCHES_PER_METRE, max_height)
    fig, ax = plt.subplots(figsize=(fig_w, fig_h), dpi=dpi)
    if title:
        ax.set_title(title, fontsize=10, fontweight="bold")
    draw_geometry(ax, scene)
    fig.tight_layout()
    return fig, ax


def save_figure(fig, path: Path, dpi: int = 150) -> Path:
    """Save and close a matplotlib figure.

    Centralises fig.savefig + plt.close so callers outside src/visualization
    never need to import matplotlib directly.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, bbox_inches="tight", dpi=dpi, facecolor="white")
    plt.close(fig)
    return path


def _draw_axis_break(ax: Axes, location: str = "bottom", size: float = 0.015) -> None:
    d = size
    kwargs = dict(transform=ax.transAxes, color="black", clip_on=False, linewidth=1)
    y = 0 if location == "bottom" else 1
    for x0 in (0, 1):
        ax.plot((x0 - d, x0 + d), (y - d - d / 2, y + d - d / 2), **kwargs)
        ax.plot((x0 - d, x0 + d), (y - d + d / 2, y + d + d / 2), **kwargs)


def _draw_legend(ax: Axes, scene: SceneData, seen_mats: set[str], mc_y_min) -> None:
    patches = []
    for mat in LEGEND_ORDER:
        if mat in seen_mats:
            style = MATERIALS[mat]
            patches.append(mpatches.Patch(
                facecolor=style.color, edgecolor="#555555",
                hatch=style.hatch, linewidth=0.5, label=style.label,
            ))
    if scene.tx:
        patches.append(plt.Line2D([0], [0], marker="v", color="#E82020",
                                  markersize=7, linestyle="none", label="TX"))
    if scene.receivers:
        label = "RX" if len(scene.receivers) == 1 else "RX Array"
        patches.append(plt.Line2D([0], [0], marker="^", color="#1060D0",
                                  markersize=7, linestyle="none", label=label))


    if mc_y_min is not None:
        patches.append(mpatches.Patch(
            facecolor="none", edgecolor="#FF6600", linewidth=1.2,
            linestyle="--", label="MC sampling box",
        ))
    if patches:
        ax.legend(handles=patches, loc="upper left", bbox_to_anchor=(1.02, 1.0),
                  fontsize=7, framealpha=0.95, borderpad=0.5)


def _draw_meta_annotation(ax: Axes, scene: SceneData) -> None:
    _KEY_LABELS = {
        "pvc":             "PVC requested",
        "mc_pvc_measured": "PVC measured (MC)",
        "Lab_FI":          "Lab FI",
        "Lab_Class":       "Class",
        "rock_count":      "Rocks",
    }
    lines = [f"{label}: {scene.meta[key]}"
             for key, label in _KEY_LABELS.items() if key in scene.meta]
    if lines:
        ax.text(0.01, 0.99, "\n".join(lines),
                transform=ax.transAxes, fontsize=7, va="top",
                bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8))

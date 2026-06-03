from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional
import json

import matplotlib.colors
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.axes import Axes


# ── Data model ────────────────────────────────────────────────────────────────

@dataclass
class BoxGeom:
    x1: float
    y1: float
    x2: float
    y2: float
    material: str


@dataclass
class CylinderGeom:
    x: float
    y: float
    radius: float
    material: str


@dataclass
class TriangleGeom:
    x1: float; y1: float
    x2: float; y2: float
    x3: float; y3: float
    material: str


@dataclass
class AntennaPos:
    x: float
    y: float


@dataclass
class SceneData:
    domain_x: float = 0.0
    domain_y: float = 0.0
    title: str = ""
    boxes: list = field(default_factory=list)      # list[BoxGeom]
    cylinders: list = field(default_factory=list)  # list[CylinderGeom]
    triangles: list = field(default_factory=list)  # list[TriangleGeom]
    tx: Optional[AntennaPos] = None
    receivers: list[AntennaPos] = field(default_factory=list)
    meta: dict = field(default_factory=dict)


# ── Parser ────────────────────────────────────────────────────────────────────

def parse_in_file(path: Path) -> SceneData:
    """Parse a gprMax .in file into SceneData.

    Handles: #domain, #title, #box, #cylinder, #hertzian_dipole, #rx
    and ## key: value metadata comments (JSON-decoded when possible).
    """
    scene = SceneData()
    with open(path, encoding="utf-8", errors="replace") as fh:
        for raw in fh:
            line = raw.strip()
            if not line:
                continue

            if line.startswith("## ") and ":" in line:
                key, _, val = line[3:].partition(":")
                k, v = key.strip(), val.strip()
                try:
                    scene.meta[k] = json.loads(v)
                except (json.JSONDecodeError, ValueError):
                    scene.meta[k] = v
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
            elif cmd == "#box:":
                # #box: x1 y1 z1 x2 y2 z2 material
                scene.boxes.append(BoxGeom(
                    x1=float(tokens[1]), y1=float(tokens[2]),
                    x2=float(tokens[4]), y2=float(tokens[5]),
                    material=tokens[7],
                ))
            elif cmd == "#fractal_box:":
                # #fractal_box: x1 y1 z1 x2 y2 z2 frac_dim wx wy wz n_mat soil box_id [seed]
                # Rendered like a box of its soil material (heterogeneous fill).
                scene.boxes.append(BoxGeom(
                    x1=float(tokens[1]), y1=float(tokens[2]),
                    x2=float(tokens[4]), y2=float(tokens[5]),
                    material=tokens[12],
                ))
            elif cmd == "#triangle:":
                # #triangle: x1 y1 z1 x2 y2 z2 x3 y3 z3 material
                scene.triangles.append(TriangleGeom(
                    x1=float(tokens[1]), y1=float(tokens[2]),
                    x2=float(tokens[4]), y2=float(tokens[5]),
                    x3=float(tokens[7]), y3=float(tokens[8]),
                    material=tokens[10],
                ))
            elif cmd == "#cylinder:":
                # #cylinder: x1 y1 z1 x2 y2 z2 radius material
                scene.cylinders.append(CylinderGeom(
                    x=float(tokens[1]), y=float(tokens[2]),
                    radius=float(tokens[7]),
                    material=tokens[8],
                ))
            elif cmd == "#hertzian_dipole:":
                # #hertzian_dipole: polarisation x y z waveform_id
                scene.tx = AntennaPos(x=float(tokens[2]), y=float(tokens[3]))
            elif cmd == "#rx:":
                # #rx: x y z
                scene.receivers.append(AntennaPos(x=float(tokens[1]), y=float(tokens[2])))

    return scene


# ── Material styles ───────────────────────────────────────────────────────────

@dataclass
class MaterialStyle:
    color: str
    hatch: Optional[str] = None
    label: str = ""


STYLES: dict[str, MaterialStyle] = {
    "free_space":        MaterialStyle("#F0F4F8", None, "Air"),
    "subgrade":          MaterialStyle("#2F4F4F", "-",  "Subgrade"),
    "formation":         MaterialStyle("#BDB76B", "+",  "Formation"),
    "bal_rock":          MaterialStyle("#5A5A5A", "/",  "Ballast Rock"),
    "bal_rock_L1":       MaterialStyle("#A1887F", "/",   "Rock L1"),
    "bal_rock_L2":       MaterialStyle("#8D6E63", "//",  "Rock L2"),
    "bal_rock_L3":       MaterialStyle("#6D4C41", "///", "Rock L3"),
    "bal_foul":          MaterialStyle("#4B3621", ".",  "Fouling (dense)"),
    "bal_foul_granular": MaterialStyle("#C8A055", ".",  "Fouling"),
    "foul_soil":         MaterialStyle("#B5651D", "xx", "Fouling (heterogeneous)"),
    "concrete_sleeper":  MaterialStyle("#708090", "x",  "Sleeper"),
}

for _i in range(1, 10):
    STYLES[f"bal_foul_g{_i}"] = MaterialStyle(
        color=matplotlib.colors.to_hex(plt.cm.YlOrBr(0.3 + _i * 0.07)),
        hatch="." * ((_i % 3) + 1),
        label=f"Foul L{_i}",
    )

_LEGEND_ORDER = [
    "subgrade", "formation",
    "bal_rock", "bal_rock_L1", "bal_rock_L2", "bal_rock_L3",
    "bal_foul", "bal_foul_granular", "foul_soil",
    *[f"bal_foul_g{i}" for i in range(1, 10)],
    "concrete_sleeper",
]


# ── Geometry renderer ─────────────────────────────────────────────────────────

def draw_geometry(ax: Axes, scene: SceneData) -> None:
    """Draw boxes, cylinders, antennas, MC box, boundary lines, and legend."""
    dx, dy = scene.domain_x, scene.domain_y
    ax.set_facecolor(STYLES.get("free_space", MaterialStyle("#F0F4F8")).color)

    seen_mats: set[str] = set()

    for box in scene.boxes:
        style = STYLES.get(box.material, MaterialStyle("#CCCCCC", None, box.material))
        ax.add_patch(mpatches.Rectangle(
            (box.x1, box.y1), box.x2 - box.x1, box.y2 - box.y1,
            facecolor=style.color,
            edgecolor="black" if style.hatch else "none",
            linewidth=0.4,
            hatch=style.hatch,
            zorder=1,
        ))
        seen_mats.add(box.material)

    for tri in scene.triangles:
        style = STYLES.get(tri.material, MaterialStyle("#AAAAAA", None, tri.material))
        ax.add_patch(mpatches.Polygon(
            [(tri.x1, tri.y1), (tri.x2, tri.y2), (tri.x3, tri.y3)],
            facecolor=style.color, edgecolor="#333333", linewidth=0.25, zorder=2,
        ))
        seen_mats.add(tri.material)

    for cyl in scene.cylinders:
        style = STYLES.get(cyl.material, MaterialStyle("#AAAAAA", None, cyl.material))
        ax.add_patch(mpatches.Circle(
            (cyl.x, cyl.y), cyl.radius,
            facecolor=style.color, edgecolor="#333333", linewidth=0.25, zorder=2,
        ))
        seen_mats.add(cyl.material)


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
    ax.set_ylim(0, dy)
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
    Both render_in_file.py and the blueprint use this when they need
    a self-contained geometry image (not a subplot inside a dashboard).
    """
    aspect = scene.domain_y / max(scene.domain_x, 1e-6)
    fig_h  = min(base_width * aspect * 0.75, max_height)
    fig, ax = plt.subplots(figsize=(base_width, fig_h), dpi=dpi)
    if title:
        ax.set_title(title, fontsize=10, fontweight="bold")
    draw_geometry(ax, scene)
    fig.tight_layout()
    return fig, ax


def _draw_axis_break(ax: Axes, location: str = "bottom", size: float = 0.015) -> None:
    d = size
    kwargs = dict(transform=ax.transAxes, color="black", clip_on=False, linewidth=1)
    y = 0 if location == "bottom" else 1
    for x0 in (0, 1):
        ax.plot((x0 - d, x0 + d), (y - d - d / 2, y + d - d / 2), **kwargs)
        ax.plot((x0 - d, x0 + d), (y - d + d / 2, y + d + d / 2), **kwargs)


def _draw_legend(ax: Axes, scene: SceneData, seen_mats: set[str], mc_y_min) -> None:
    patches = []
    for mat in _LEGEND_ORDER:
        if mat in seen_mats:
            style = STYLES[mat]
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
        ax.legend(handles=patches, loc="upper right", fontsize=7, framealpha=0.85)


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

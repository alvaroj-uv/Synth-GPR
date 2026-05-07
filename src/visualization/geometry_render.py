from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.axes import Axes

from src.visualization.in_parser import SceneData


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
    "bal_foul_granular": MaterialStyle("#C8A055", ".",  "Fouling"),
    "concrete_sleeper":  MaterialStyle("#708090", "x",  "Sleeper"),
}

_LEGEND_ORDER = ["subgrade", "formation", "bal_rock", "bal_foul_granular", "concrete_sleeper"]


def draw_geometry(ax: Axes, scene: SceneData) -> None:
    """
    Draw all geometry objects from a SceneData onto ax.

    Renders boxes, cylinders, TX/RX antennas, the MC sampling box overlay,
    layer boundary guide lines, metadata annotation, and legend.
    """
    dx, dy = scene.domain_x, scene.domain_y

    ax.set_facecolor(STYLES.get("free_space", MaterialStyle("#F0F4F8")).color)

    seen_mats: set[str] = set()

    for box in scene.boxes:
        style = STYLES.get(box.material, MaterialStyle("#CCCCCC", None, box.material))
        ax.add_patch(mpatches.Rectangle(
            (box.x1, box.y1), box.x2 - box.x1, box.y2 - box.y1,
            facecolor=style.color, edgecolor="none", zorder=1,
        ))
        seen_mats.add(box.material)

    for cyl in scene.cylinders:
        style = STYLES.get(cyl.material, MaterialStyle("#AAAAAA", None, cyl.material))
        ax.add_patch(mpatches.Circle(
            (cyl.x, cyl.y), cyl.radius,
            facecolor=style.color, edgecolor="#333333", linewidth=0.25, zorder=2,
        ))
        seen_mats.add(cyl.material)

    if scene.tx:
        ax.plot(scene.tx.x, scene.tx.y, marker="v", color="#E82020",
                markersize=7, zorder=5, linestyle="none")
    if scene.rx:
        ax.plot(scene.rx.x, scene.rx.y, marker="^", color="#1060D0",
                markersize=7, zorder=5, linestyle="none")

    # MC sampling box
    mc_y_min = scene.meta.get("mc_y_min")
    mc_y_max = scene.meta.get("mc_y_max")
    if mc_y_min is not None and mc_y_max is not None:
        ax.add_patch(mpatches.Rectangle(
            (0, float(mc_y_min)), dx, float(mc_y_max) - float(mc_y_min),
            linewidth=1.2, edgecolor="#FF6600", facecolor="none",
            linestyle="--", zorder=6,
        ))

    # Layer boundary guide lines
    boundary_ys: set[float] = set()
    for box in scene.boxes:
        if box.material in ("subgrade", "formation", "bal_foul_granular"):
            boundary_ys.update({round(box.y1, 6), round(box.y2, 6)})
    for y in sorted(boundary_ys):
        if 0 < y < dy:
            ax.axhline(y, color="#AAAAAA", linewidth=0.6, linestyle="--", zorder=0)

    ax.set_xlim(0, dx)
    ax.set_ylim(0, dy)
    ax.set_aspect("equal")
    ax.set_xlabel("x (m)", fontsize=9)
    ax.set_ylabel("y (m)", fontsize=9)
    ax.tick_params(labelsize=8)
    ax.grid(visible=True, alpha=0.15, linewidth=0.4)

    _draw_legend(ax, scene, seen_mats, mc_y_min)
    _draw_meta_annotation(ax, scene)


def _draw_legend(ax: Axes, scene: SceneData, seen_mats: set[str],
                 mc_y_min) -> None:
    patches = []
    for mat in _LEGEND_ORDER:
        if mat in seen_mats:
            style = STYLES[mat]
            patches.append(mpatches.Patch(
                facecolor=style.color, edgecolor="#555555",
                linewidth=0.5, label=style.label,
            ))
    if scene.tx:
        patches.append(plt.Line2D([0], [0], marker="v", color="#E82020",
                                  markersize=7, linestyle="none", label="TX"))
    if scene.rx:
        patches.append(plt.Line2D([0], [0], marker="^", color="#1060D0",
                                  markersize=7, linestyle="none", label="RX"))
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

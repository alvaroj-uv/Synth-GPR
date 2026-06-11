"""
Generic 2D scene rendering for SceneData.

Draws the physical scene only: layers, rocks, grains, antenna markers, layer
boundary guides, legend, and metadata annotation. Research-specific overlays
(MC sieve box, MC ballast box, LDCP scan line) intentionally do NOT live
here — callers that want them must opt in via ``overlays.draw_research_overlays``
after calling ``draw_geometry`` (the dashboard does; see ``dashboard.py``).

Material appearance (colors, hatches, labels, per-rock HSV jitter) comes
exclusively from ``.materials`` (the single registry shared with the 3D
renderer). Add new materials there, not in this module.
"""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from matplotlib.axes import Axes

from .materials import LEGEND_ORDER, MATERIALS, get_style, jitter_color
from .model import SceneData

# Shared legend placement — overlays.py reuses this when it appends its own
# legend entries, so the legend never jumps position between plain and
# overlaid figures.
LEGEND_KWARGS = dict(loc="upper left", bbox_to_anchor=(1.02, 1.0),
                     fontsize=7, framealpha=0.95, borderpad=0.5)


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
    """Draw the physical scene: layers, rocks, antennas, boundaries, legend.

    Research overlays (MC/LDCP) are NOT drawn — call
    ``overlays.draw_research_overlays(ax, scene)`` afterwards if needed.
    """
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
    _draw_legend(ax, scene, seen_mats)
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


def _draw_legend(ax: Axes, scene: SceneData, seen_mats: set[str]) -> None:
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

    if patches:
        ax.legend(handles=patches, **LEGEND_KWARGS)


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

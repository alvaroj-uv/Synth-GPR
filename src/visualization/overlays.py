"""
Research-specific overlays for 2D geometry plots — opt-in, never automatic.

``drawing.draw_geometry`` renders only the physical scene. Analysis views that
need the Monte-Carlo / LDCP diagnostics (currently the dashboard and the
unified visualizer's geometry mode) call ``draw_research_overlays(ax, scene)``
AFTER ``draw_geometry``. Publication and generic figures simply skip the call
and stay clean.

Each overlay draws only when its driving keys exist in ``scene.meta``:
  - Virtual sieve layer box (orange dashed): ``mc_y_min`` / ``mc_y_max``
  - MC global ballast box (green dotted):    ``ballast_bottom_y`` / ``ballast_top_y``
  - Virtual LDCP scan line (red solid):      ``ldcp_x`` (+ the ballast keys)
"""

from __future__ import annotations

import matplotlib.patches as mpatches
from matplotlib.axes import Axes

from .drawing import LEGEND_KWARGS
from .model import SceneData


def draw_research_overlays(ax: Axes, scene: SceneData) -> None:
    """Draw MC sieve box, MC ballast box, and LDCP scan line from scene.meta.

    Must be called after ``draw_geometry`` (it extends the legend that
    draw_geometry created). A scene without the meta keys draws nothing.
    """
    dx = scene.domain_x

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

    if mc_y_min is not None:
        _append_legend_entry(ax, mpatches.Patch(
            facecolor="none", edgecolor="#FF6600", linewidth=1.2,
            linestyle="--", label="MC sampling box",
        ))


def _append_legend_entry(ax: Axes, handle) -> None:
    """Extend the legend draw_geometry built, keeping its placement."""
    legend = ax.get_legend()
    handles = []
    if legend is not None:
        # matplotlib >= 3.7 uses .legend_handles; older versions .legendHandles
        handles = list(getattr(legend, "legend_handles", None)
                       or getattr(legend, "legendHandles", []))
    handles.append(handle)
    ax.legend(handles=handles, **LEGEND_KWARGS)

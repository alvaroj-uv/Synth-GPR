"""
High-level rendering entry points: .in file → geometry PNG.

This is the importable seam between pipelines and the visualization package.
Anything that needs "render this .in file as a PNG" (the generation pipeline,
the unified_visualizer CLI, batch scripts) calls ``render_geometry_png`` —
never a subprocess to a CLI script. It auto-dispatches 2D vs 3D and opts the
figure into the MC/LDCP research overlays (a no-op for scenes without the
overlay meta keys).
"""

from __future__ import annotations

import logging
from pathlib import Path

import matplotlib.pyplot as plt

from .drawing import render_geometry_figure
from .overlays import draw_research_overlays
from .parser import parse_in_file
from .scene_3d import render_3d_views

logger = logging.getLogger(__name__)


def detect_3d_file(in_path: Path) -> bool:
    """Detect if a .in file is 3D (contains #sphere commands)."""
    with open(in_path, "r", encoding="utf-8", errors="replace") as f:
        return any("#sphere:" in line for line in f)


def render_geometry_png(
    in_path: Path,
    out_path: Path,
    dpi: int = 150,
    title: str = None,
    metadata: str = None,
) -> Path:
    """Render the geometry of a .in file to PNG (auto-detects 2D vs 3D).

    Args:
        in_path: .in file to render
        out_path: destination PNG path (parent dirs created)
        title: custom plot title (default: file stem; for 3D, stem + class)
        metadata: optional annotation text drawn in a box at bottom-right
                  (2D only)

    Returns:
        The path the PNG was written to.
    """
    in_path = Path(in_path)
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    if detect_3d_file(in_path):
        _render_3d(in_path, out_path, dpi=dpi, title=title)
        return out_path

    logger.info(f"Parsing {in_path.name}...")
    scene = parse_in_file(in_path)

    logger.info("Rendering geometry...")
    fig, ax = render_geometry_figure(scene, title=title or in_path.stem, dpi=dpi)
    # Diagnostic view: opt into the MC/LDCP research overlays (no-op unless
    # the scene carries the MC/LDCP meta keys)
    draw_research_overlays(ax, scene)
    if metadata:
        ax.text(0.98, 0.02, metadata,
                transform=ax.transAxes, fontsize=9, verticalalignment='bottom',
                horizontalalignment='right', family='monospace',
                bbox=dict(boxstyle='round', facecolor='#E8F4FF', alpha=0.95,
                          edgecolor='#1060D0', linewidth=2))
    fig.savefig(out_path, dpi=dpi, bbox_inches="tight")
    logger.info(f"✓ Saved: {out_path}")
    plt.close(fig)
    return out_path


def _render_3d(in_path: Path, out_path: Path, dpi: int = 150, title: str = None) -> None:
    """Render a 3D .in file via the orthogonal-views renderer."""
    logger.info(f"Parsing 3D scene {in_path.name}...")
    scene = parse_in_file(in_path)
    if title is None:
        title = f"{in_path.stem} - {scene.meta.get('Lab_Class', '?')} class"
    fig = render_3d_views(scene, title=title, dpi=dpi)
    fig.savefig(out_path, dpi=dpi, bbox_inches="tight")
    logger.info(f"✓ Saved: {out_path}")
    plt.close(fig)

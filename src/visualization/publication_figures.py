"""
Publication-Quality Figure Export for gprMax Scene Visualization

Generates professional, print-ready figures suitable for:
- Journal articles
- Conference presentations
- Thesis/dissertations
- Technical reports

Features:
- High DPI (300+ for printing)
- Professional fonts and sizing
- Proper aspect ratios
- Material color coding
- Tight layout control
- Side-by-side comparisons
- Multi-panel figures with shared colorbars
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional, List, Tuple
import warnings

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.axes import Axes
import numpy as np

from .drawing import draw_geometry, render_geometry_figure
from .model import SceneData
from .parser import parse_in_file

logger = logging.getLogger(__name__)

# Professional figure parameters
PUBLICATION_PARAMS = {
    'figure.dpi': 100,  # Internal resolution
    'savefig.dpi': 300,  # Export resolution (300 dpi for printing)
    'font.family': 'sans-serif',
    'font.sans-serif': ['Helvetica', 'Arial'],
    'font.size': 10,
    'axes.labelsize': 11,
    'axes.titlesize': 12,
    'xtick.labelsize': 9,
    'ytick.labelsize': 9,
    'legend.fontsize': 9,
    'lines.linewidth': 1.5,
    'lines.markersize': 6,
}


class PublicationFigureGenerator:
    """Generate publication-quality figures from gprMax scene data"""

    @staticmethod
    def save_high_quality_figure(
        fig: plt.Figure,
        output_path: Path | str,
        dpi: int = 300,
        bbox_inches: str = "tight",
        pad_inches: float = 0.1,
        transparent: bool = False,
    ) -> Path:
        """
        Save a matplotlib figure with publication-quality settings.

        Args:
            fig: matplotlib Figure object
            output_path: Path to save the figure
            dpi: Resolution in DPI (300 for printing, 150 for screen)
            bbox_inches: "tight" to remove whitespace
            pad_inches: Padding around the figure
            transparent: Whether to save with transparent background

        Returns:
            Path to saved figure
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Apply tight layout before saving
        fig.tight_layout()

        fig.savefig(
            output_path,
            dpi=dpi,
            bbox_inches=bbox_inches,
            pad_inches=pad_inches,
            transparent=transparent,
            facecolor='white' if not transparent else 'none',
        )
        logger.info(f"Saved publication figure: {output_path}")
        return output_path

    @staticmethod
    def save_scene_cross_section(
        scene: SceneData,
        output_path: Path | str,
        title: str = "",
        dpi: int = 300,
        figsize: Tuple[float, float] = (8, 6),
    ) -> Path:
        """
        Generate publication-quality cross-section of the scene.

        Shows:
        - All layers with exact Y-coordinates
        - Rock positions as colored shapes
        - Fouling region as shaded area
        - Material color coding
        - Antenna positions with markers
        - Grid and scale bar

        Args:
            scene: SceneData object from parse_in_file
            output_path: Where to save the PNG
            title: Optional title for the figure
            dpi: Output resolution (300 for printing)
            figsize: Figure size in inches (width, height)

        Returns:
            Path to saved figure
        """
        # Create figure with professional settings
        fig, ax = plt.subplots(figsize=figsize, dpi=100)

        # Draw the geometry
        draw_geometry(ax, scene)

        # Add title if provided
        if title:
            ax.set_title(title, fontsize=14, fontweight='bold', pad=15)

        # Enhance appearance
        ax.set_xlabel('Position (m)', fontsize=12, fontweight='bold')
        ax.set_ylabel('Depth (m)', fontsize=12, fontweight='bold')

        # Note: draw_geometry() already adds metadata via _draw_meta_annotation()
        # No need to add duplicate metadata box here

        # Save with high quality
        return PublicationFigureGenerator.save_high_quality_figure(
            fig, output_path, dpi=dpi
        )

    @staticmethod
    def save_comparison_figures(
        in_paths: List[Path | str],
        output_dir: Path | str = "figures",
        dpi: int = 300,
    ) -> List[Path]:
        """
        Generate side-by-side comparison figures for multiple scenes.

        Useful for comparing:
        - Different PVC levels (0%, 25%, 50%, 75%, 100%)
        - Different packing algorithms
        - Before/after configurations

        Args:
            in_paths: List of .in file paths to compare
            output_dir: Directory to save comparison figures
            dpi: Output resolution

        Returns:
            List of paths to saved figures
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        saved_paths = []

        # Parse all scenes
        scenes = []
        titles = []
        for path in in_paths:
            path = Path(path)
            try:
                scene = parse_in_file(path)
                scenes.append(scene)
                # Extract PVC or other identifying info from metadata
                pvc = scene.meta.get('pvc', 'N/A')
                titles.append(f"{path.stem}\n(PVC: {pvc}%)")
            except Exception as e:
                logger.warning(f"Could not parse {path}: {e}")
                continue

        if not scenes:
            logger.error("No valid scenes to compare")
            return []

        # Create side-by-side figure
        n_scenes = len(scenes)
        fig, axes = plt.subplots(
            1, n_scenes,
            figsize=(4 * n_scenes, 6),
            dpi=100,
        )

        # Handle single scene case
        if n_scenes == 1:
            axes = [axes]

        # Draw each scene
        for ax, scene, title in zip(axes, scenes, titles):
            draw_geometry(ax, scene)
            ax.set_title(title, fontsize=11, fontweight='bold')
            if ax is not axes[0]:
                ax.set_ylabel('')

        fig.suptitle(
            'Configuration Comparison',
            fontsize=14,
            fontweight='bold',
            y=1.00,
        )

        output_path = output_dir / f"comparison_all_{len(scenes)}_panel.png"
        saved_paths.append(
            PublicationFigureGenerator.save_high_quality_figure(
                fig, output_path, dpi=dpi
            )
        )

        return saved_paths

    @staticmethod
    def save_pvc_variation_series(
        base_in_path: Path | str,
        pvc_levels: List[float] = None,
        output_dir: Path | str = "figures",
        dpi: int = 300,
    ) -> List[Path]:
        """
        Generate a series of figures showing PVC variation effect.

        This is a template method - in practice, you would generate
        multiple .in files with different PVC levels, then visualize them.

        Args:
            base_in_path: Template .in file path
            pvc_levels: List of PVC percentages to show
            output_dir: Where to save figures
            dpi: Output resolution

        Returns:
            List of saved figure paths
        """
        if pvc_levels is None:
            pvc_levels = [0, 25, 50, 75, 100]

        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        # In real usage, you would generate .in files for each PVC level
        # For now, we create a template showing the concept
        base_scene = parse_in_file(Path(base_in_path))

        fig, axes = plt.subplots(
            1, len(pvc_levels),
            figsize=(4 * len(pvc_levels), 5),
            dpi=100,
        )

        if len(pvc_levels) == 1:
            axes = [axes]

        for ax, pvc in zip(axes, pvc_levels):
            draw_geometry(ax, base_scene)
            ax.set_title(f'{pvc}% PVC', fontsize=11, fontweight='bold')
            if ax is not axes[0]:
                ax.set_ylabel('')

        fig.suptitle(
            'PVC Effect on Geometry',
            fontsize=14,
            fontweight='bold',
        )

        output_path = output_dir / "pvc_series_5panel.png"
        saved_paths = [
            PublicationFigureGenerator.save_high_quality_figure(
                fig, output_path, dpi=dpi
            )
        ]

        return saved_paths

    @staticmethod
    def save_grid_layout(
        in_paths: List[Path | str],
        output_path: Path | str = "figures/grid_layout.png",
        ncols: int = 3,
        dpi: int = 300,
    ) -> Path:
        """
        Create a grid layout of multiple scenes.

        Useful for showcasing dataset diversity or variation.

        Args:
            in_paths: List of .in file paths
            output_path: Where to save the grid
            ncols: Number of columns in the grid
            dpi: Output resolution

        Returns:
            Path to saved figure
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Parse all scenes
        scenes = []
        for path in in_paths:
            try:
                scenes.append(parse_in_file(Path(path)))
            except Exception as e:
                logger.warning(f"Could not parse {path}: {e}")

        if not scenes:
            logger.error("No valid scenes for grid")
            return output_path

        n_scenes = len(scenes)
        nrows = (n_scenes + ncols - 1) // ncols  # Ceiling division

        fig, axes = plt.subplots(
            nrows, ncols,
            figsize=(4 * ncols, 4 * nrows),
            dpi=100,
        )

        # Handle axis indexing for 1D/2D cases
        if nrows == 1 and ncols == 1:
            axes = [[axes]]
        elif nrows == 1 or ncols == 1:
            axes = axes.reshape(nrows, ncols)
        else:
            axes = axes.reshape(nrows, ncols)

        # Draw scenes
        for idx, (ax_row, scene) in enumerate(
            zip(axes.flat, scenes)
        ):
            draw_geometry(ax_row, scene)
            pvc = scene.meta.get('pvc', 'N/A')
            ax_row.set_title(f'Scene {idx + 1}\n(PVC: {pvc}%)',
                           fontsize=9)

        # Hide unused subplots
        for ax in axes.flat[n_scenes:]:
            ax.set_visible(False)

        fig.suptitle(
            f'Dataset Overview ({n_scenes} scenes)',
            fontsize=14,
            fontweight='bold',
        )

        return PublicationFigureGenerator.save_high_quality_figure(
            fig, output_path, dpi=dpi
        )


def _format_metadata_box(meta: dict) -> str:
    """Format metadata for display in annotation box"""
    if not meta:
        return ""

    key_labels = {
        "pvc": "PVC",
        "Lab_FI": "Lab FI",
        "Lab_Class": "Class",
        "rock_count": "Rocks",
        "domain_x": "Domain X",
        "domain_y": "Domain Y",
    }

    lines = []
    for key, label in key_labels.items():
        if key in meta:
            value = meta[key]
            lines.append(f"{label}: {value}")

    return "\n".join(lines) if lines else ""


def apply_publication_style():
    """Apply professional matplotlib style settings"""
    plt.rcParams.update(PUBLICATION_PARAMS)


# Convenience function for quick export
def export_scene_as_pdf(
    in_path: Path | str,
    output_path: Path | str = None,
) -> Path:
    """
    Quick export of a scene to PDF (vector format).

    PDF is ideal for publications and presentations.

    Args:
        in_path: Path to .in file
        output_path: Where to save (defaults to same stem .pdf)

    Returns:
        Path to saved PDF
    """
    in_path = Path(in_path)
    if output_path is None:
        output_path = in_path.with_suffix('.pdf')

    scene = parse_in_file(in_path)
    fig, ax = render_geometry_figure(
        scene,
        title=in_path.stem,
        dpi=100,
    )

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    fig.savefig(
        output_path,
        format='pdf',
        bbox_inches='tight',
        pad_inches=0.05,
    )
    logger.info(f"Exported to PDF: {output_path}")
    plt.close(fig)

    return output_path


# Convenience function for quick export
def export_scene_as_svg(
    in_path: Path | str,
    output_path: Path | str = None,
) -> Path:
    """
    Quick export of a scene to SVG (vector format).

    SVG is scalable and editable in vector graphics editors.

    Args:
        in_path: Path to .in file
        output_path: Where to save (defaults to same stem .svg)

    Returns:
        Path to saved SVG
    """
    in_path = Path(in_path)
    if output_path is None:
        output_path = in_path.with_suffix('.svg')

    scene = parse_in_file(in_path)
    fig, ax = render_geometry_figure(
        scene,
        title=in_path.stem,
        dpi=100,
    )

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    fig.savefig(
        output_path,
        format='svg',
        bbox_inches='tight',
        pad_inches=0.05,
    )
    logger.info(f"Exported to SVG: {output_path}")
    plt.close(fig)

    return output_path

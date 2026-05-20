"""
Helper utilities for Streamlit layer editor.
Orchestrates config building, scene generation, and visualization.
"""

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import numpy as np
import matplotlib.pyplot as plt

from src.config import GeneratorConfig
from src.production_line import ProductionLine
from src.work_order import WorkOrder, WorkOrderSystem
from src.domain.coordinates import LayerStack, CoordinateSystem, Anchor, Layer
from src.physics import get_fdtd_recommendations
from src.visualization.scene import parse_in_file, render_geometry_figure
from src.file_writer import GPRMaxFileWriter
from src.scene_descriptor import SceneDefinition


def build_config_from_inputs(
    frequency_hz: float,
    angular_rocks: bool,
    rock_sides: int,
    pvc: float,
) -> GeneratorConfig:
    """
    Build GeneratorConfig from UI inputs.

    Args:
        frequency_hz: Center frequency in Hz
        angular_rocks: True for polygonal rocks, False for circular
        rock_sides: Number of sides (only used if angular_rocks=True)
        pvc: Percentage void contamination (0-100)

    Returns:
        Fully configured GeneratorConfig ready for production line
    """
    cfg = GeneratorConfig.create_physically_perfect(
        center_freq_hz=frequency_hz,
        angular_rocks=angular_rocks,
        rock_sides=rock_sides if angular_rocks else 0,
        pvc_min=float(pvc),
        pvc_max=float(pvc),
        moisture_min=0.1,
        moisture_max=0.1,
    )
    return cfg


def compute_layer_layout(
    subgrade_m: float,
    formation_m: float,
    ballast_m: float,
    antenna_clearance_m: float = 0.5,
    air_buffer_m: float = 1.5,
    domain_x: float = 0.6,
    domain_z: float = 0.003,
) -> CoordinateSystem:
    """
    Compute layer boundaries and antenna position.

    Args:
        subgrade_m: Subgrade thickness
        formation_m: Formation thickness
        ballast_m: Ballast thickness
        antenna_clearance_m: Space above ballast for antenna
        air_buffer_m: PML + safety buffer above antenna
        domain_x, domain_z: Domain dimensions (for completeness)

    Returns:
        CoordinateSystem with all Y-level anchors computed
    """
    stack = LayerStack(
        subgrade_thickness=subgrade_m,
        formation_thickness=formation_m,
        ballast_thickness=ballast_m,
        antenna_clearance=antenna_clearance_m,
        air_buffer=air_buffer_m,
    )

    coords = CoordinateSystem(
        layer_stack=stack,
        domain_x=domain_x,
        domain_z=domain_z,
    )

    return coords


def validate_antenna_placement(coords: CoordinateSystem, pml_margin_m: float = 0.15) -> dict:
    """
    Validate antenna position relative to PML boundary.

    Args:
        coords: Computed coordinate system
        pml_margin_m: Minimum safe distance from domain top to antenna

    Returns:
        Dict with 'is_safe' (bool), 'antenna_y', 'domain_top', 'clearance', 'status' (str)
    """
    antenna_y = coords.get_y(Anchor.ANTENNA_LEVEL)
    domain_top = coords.get_y(Anchor.DOMAIN_TOP)
    clearance = domain_top - antenna_y
    is_safe = clearance >= pml_margin_m

    if is_safe:
        status = f"✓ Safe clearance: {clearance:.4f}m (margin: {pml_margin_m}m)"
    else:
        status = f"✗ Too close to PML: {clearance:.4f}m (need {pml_margin_m}m)"

    return {
        "is_safe": is_safe,
        "antenna_y": antenna_y,
        "domain_top": domain_top,
        "clearance": clearance,
        "status": status,
    }


def generate_scene_checkpoint(
    cfg: GeneratorConfig,
    pvc: float,
    moisture: float = 0.1,
):
    """
    Run production line to generate scene geometry.

    Args:
        cfg: GeneratorConfig
        pvc: Percentage void contamination
        moisture: Soil moisture fraction

    Returns:
        SceneCheckpoint with populated geometry, materials, sources
    """
    params = {
        'pvc': float(pvc),
        'moisture': float(moisture),
    }

    work_order = WorkOrder.from_sampled_params(1, params)
    work_order_system = WorkOrderSystem(work_order)

    production_line = ProductionLine(cfg)
    checkpoint = production_line.run(work_order_system)

    return checkpoint


def preview_geometry(checkpoint) -> plt.Figure:
    """
    Generate matplotlib figure of geometry cross-section.

    Args:
        checkpoint: SceneCheckpoint with assembled geometry

    Returns:
        matplotlib.figure.Figure ready for st.pyplot()
    """
    with tempfile.NamedTemporaryFile(suffix=".in", mode="w", delete=False) as f:
        temp_path = Path(f.name)
        # Write scene to temp file
        scene_def = SceneDefinition(
            config=checkpoint.config,
            domain_commands=[checkpoint.domain_cmd] if checkpoint.domain_cmd else [],
            material_commands=checkpoint.materials,
            geometry_commands=checkpoint.geometry,
            source_commands=list(checkpoint.sources) + list(checkpoint.receivers),
            metadata=checkpoint.metadata,
        )
        content = GPRMaxFileWriter.write_scene(scene_def, "Streamlit_POC")
        f.write(content)

    try:
        # Parse and render
        scene = parse_in_file(temp_path)
        fig, _ = render_geometry_figure(scene, title="Ballast Geometry Preview", dpi=100)
        return fig
    finally:
        temp_path.unlink()  # Clean up temp file


def export_in_file(checkpoint) -> str:
    """
    Generate .in file content as string (no file I/O).

    Args:
        checkpoint: SceneCheckpoint

    Returns:
        String containing gprMax .in file format
    """
    scene_def = SceneDefinition(
        config=checkpoint.config,
        domain_commands=[checkpoint.domain_cmd] if checkpoint.domain_cmd else [],
        material_commands=checkpoint.materials,
        geometry_commands=checkpoint.geometry,
        source_commands=list(checkpoint.sources) + list(checkpoint.receivers),
        metadata=checkpoint.metadata,
    )

    content = GPRMaxFileWriter.write_scene(scene_def, "Streamlit_POC")
    return content


def get_fdtd_info(frequency_hz: float) -> dict:
    """
    Get FDTD recommendations for a frequency.

    Args:
        frequency_hz: Center frequency in Hz

    Returns:
        Dict with domain_x, dx, antenna_height, lambda_max, lambda_min
    """
    recs = get_fdtd_recommendations(frequency_hz)
    return {
        "domain_x_m": recs["domain_x"],
        "dx_mm": recs["dx"] * 1000,
        "antenna_height_m": recs["antenna_height"],
        "lambda_max_m": recs["lambda_max"],
        "lambda_min_m": recs["lambda_min"],
    }

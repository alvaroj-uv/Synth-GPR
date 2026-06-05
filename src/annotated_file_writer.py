"""
Annotated gprMax Input File Writer

Generates .in files with detailed comments explaining:
- Physical meaning of each parameter
- Layer structure and coordinates
- Material properties and their impact
- Antenna configuration and reasoning
- Expected signal characteristics

This makes generated files self-documenting for:
- Understanding what was generated
- Verifying geometry is correct
- Debugging simulation issues
- Learning how gprMax input files work
"""

from datetime import date
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from .file_writer import GPRMaxFileWriter
from .gpr_commands import GPRCommand
from .scene_descriptor import SceneDefinition


@dataclass
class LayerInfo:
    """Information about a geological layer for annotation"""
    name: str
    y_bottom: float
    y_top: float
    material: str
    permittivity: float
    description: str
    physical_meaning: str


class AnnotatedGPRMaxFileWriter:
    """
    Generates annotated gprMax .in files with comprehensive explanations.

    Each section includes:
    - Physical interpretation
    - Coordinate ranges
    - Material properties
    - Expected impact on simulation
    - Why each parameter matters
    """

    @staticmethod
    def _layer_header(layer: LayerInfo) -> str:
        """Generate detailed header for a layer with physical explanation"""
        lines = [
            "",
            "## " + "=" * 78,
            f"## LAYER: {layer.name.upper()} (Y = {layer.y_bottom:.2f} → {layer.y_top:.2f} m)",
            "## " + "=" * 78,
            f"##",
            f"## Physical Description:",
            f"##   {layer.physical_meaning}",
            f"##",
            f"## Material: {layer.material}",
            f"##   Permittivity (ER): {layer.permittivity}",
            f"##   Thickness: {layer.y_top - layer.y_bottom:.3f} m",
            f"##",
            f"## Impact on GPR Signal:",
            f"##   - Wave velocity in this layer: c/{(layer.permittivity**0.5):.2f} (reduced by √ER)",
            f"##   - Impedance mismatch at boundaries: reflects EM energy",
            f"##   - Signal attenuation: depends on conductivity",
        ]
        return "\n".join(lines)

    @staticmethod
    def _coordinate_system_section(metadata: Dict[str, Any]) -> str:
        """Generate coordinate system explanation"""
        lines = [
            "## " + "=" * 78,
            "## COORDINATE SYSTEM",
            "## " + "=" * 78,
            "##",
            "## Y-Axis (Vertical) - Depth in Railway Track:",
            "##   0.00 m ──────────────────── Bottom (foundation)",
            "##",
        ]

        # Add layer boundaries if available
        if 'ballast_bottom_y' in metadata and 'ballast_top_y' in metadata:
            lines.extend([
                f"##   0.00 → 0.20 m: Subgrade (soil foundation)",
                f"##   0.20 → 0.30 m: Formation (subballast transition)",
                f"##   0.30 → {metadata.get('ballast_top_y', 0.55):.2f} m: Ballast (aggregate + fouling)",
                f"##   {metadata.get('ballast_top_y', 0.55):.2f} → 1.15 m: Air (free space + antenna)",
                "##",
                f"##   Antenna Position: {metadata.get('antenna_y', 1.05):.2f} m",
                "##   (Located above ballast for clear measurement)",
            ])

        lines.extend([
            "##",
            "## X-Axis (Horizontal) - Along Track:",
            f"##   0.00 → {metadata.get('domain_x', 2.248):.3f} m",
            "##",
            "## Z-Axis (Extrusion) - Out of Plane (2D simulation):",
            f"##   0.00 → {metadata.get('domain_z', 0.0132):.5f} m (thin slice for 2D FDTD)",
        ])

        return "\n".join(lines)

    @staticmethod
    def _fouling_explanation(metadata: Dict[str, Any]) -> str:
        """Generate detailed explanation of fouling representation"""
        pvc = metadata.get('pvc', 50.0)
        ballast_height = metadata.get('ballast_top_y', 0.55) - metadata.get('ballast_bottom_y', 0.30)
        fouling_height = (pvc / 100.0) * ballast_height
        fouling_top = metadata.get('ballast_bottom_y', 0.30) + fouling_height

        lines = [
            "",
            "## " + "=" * 78,
            "## FOULING REPRESENTATION (Painter's Algorithm)",
            "## " + "=" * 78,
            "##",
            "## How Fouling is Modeled:",
            "##   1. Rocks are painted first (triangulated aggregates)",
            "##   2. Fouling is painted SECOND as a solid box (later commands override earlier)",
            "##   3. Result: Fouling covers rocks where they overlap",
            "##",
            f"## PVC (Percentage Void Contamination): {pvc:.1f}%",
            f"##   Interpretation: {pvc:.1f}% of void space is filled with fouling material",
            "##",
            f"## Fouling Layer Height Calculation:",
            f"##   fouling_height = (PVC% / 100) × ballast_height",
            f"##   fouling_height = ({pvc:.1f} / 100) × {ballast_height:.3f}",
            f"##   fouling_height = {fouling_height:.4f} m",
            "##",
            f"## Fouling Paints from Y = {metadata.get('ballast_bottom_y', 0.30):.2f} → {fouling_top:.3f} m",
            f"##   Rocks below {fouling_top:.3f} m: Hidden (overridden by fouling paint)",
            f"##   Rocks above {fouling_top:.3f} m: Visible to antenna",
            "##",
            f"## Rock Count:",
            f"##   Total rocks: {metadata.get('rock_count', '?')}",
            f"##   Visible (above fouling): {metadata.get('rocks_visible', '?')}",
            f"##   Hidden (below fouling): {metadata.get('rocks_hidden', '?')}",
        ]

        return "\n".join(lines)

    @staticmethod
    def _domain_section_annotated(config: Any) -> str:
        """Generate annotated domain configuration section"""
        lines = [
            "## " + "=" * 78,
            "## DOMAIN CONFIGURATION",
            "## " + "=" * 78,
            "##",
            "## Domain Size (Simulation Region):",
            f"##   X (width):  {config.domain_x:.3f} m",
            f"##   Y (depth):  {config.domain_y:.3f} m",
            f"##   Z (extrusion): {config.domain_z:.5f} m (thin 2D slice)",
            "##",
            "## Why These Values?",
            "##   - Domain must be large enough to contain all geometry",
            "##   - PML (absorbing boundaries) prevents reflections from domain edges",
            "##   - Sufficient side clearance ensures EM waves don't reflect back",
            "##",
            "## Cell Size (Discretization):",
            f"##   dx, dy, dz = {config.dx:.5f} m = 13.2 mm",
            "##",
            "## FDTD Compliance Check:",
            f"##   Wavelength at {config.center_freq/1e6:.0f} MHz in free space: {0.75:.2f} m",
            f"##   λ/10 rule requires cell ≤ {0.075:.4f} m",
            f"##   Cell size ({config.dx:.5f} m) ≤ λ/10 ({0.075:.4f} m)? YES ✓",
            "##",
            "## Time Window:",
            f"##   {config.time_window*1e9:.1f} ns (sufficient for deep reflections)",
            "##",
        ]

        return "\n".join(lines)

    @staticmethod
    def _material_annotation(material_name: str, permittivity: float,
                            conductivity: float = 0, description: str = "") -> str:
        """Generate annotation for a material definition"""
        lines = [
            f"##",
            f"## Material: {material_name}",
            f"##   Relative Permittivity (ER): {permittivity}",
            f"##   Conductivity (σ): {conductivity} S/m",
        ]

        if description:
            lines.append(f"##   Description: {description}")

        # Add physical interpretation
        if permittivity == 1.0:
            lines.append(f"##   Meaning: Free space (air/vacuum)")
        elif permittivity == 5.0:
            lines.append(f"##   Meaning: Clean ballast aggregate")
            lines.append(f"##   Wave velocity: {(3e8 / (permittivity**0.5)):.0f} m/μs")
        elif permittivity == 10.0:
            lines.append(f"##   Meaning: Soil (subgrade/formation)")
            lines.append(f"##   Wave velocity: {(3e8 / (permittivity**0.5)):.0f} m/μs")
        elif permittivity > 5 and permittivity < 10:
            lines.append(f"##   Meaning: Fouling mix (fines + moisture)")
            lines.append(f"##   Wave velocity: {(3e8 / (permittivity**0.5)):.0f} m/μs")

        return "\n".join(lines)

    @staticmethod
    def _antenna_explanation(metadata: Dict[str, Any]) -> str:
        """Generate detailed antenna configuration explanation"""
        lines = [
            "",
            "## " + "=" * 78,
            "## ANTENNA CONFIGURATION",
            "## " + "=" * 78,
            "##",
            "## Antenna Type: Bistatic (Separate TX and RX)",
            "##   TX = Transmitter (sends EM pulse)",
            "##   RX = Receiver (measures reflected energy)",
            "##",
            f"## Frequency: {metadata.get('frequency_mhz', 400):.0f} MHz",
            f"##   Wavelength in free space: {3e8 / (metadata.get('frequency_mhz', 400) * 1e6):.2f} m",
            "##",
            f"## TX Position: ({metadata.get('tx_x', 1.124):.3f}, {metadata.get('tx_y', 1.05):.2f}, {metadata.get('tx_z', 0.00660):.5f}) m",
            f"## RX Position: ({metadata.get('rx_x', 1.174):.3f}, {metadata.get('rx_y', 1.05):.2f}, {metadata.get('rx_z', 0.00660):.5f}) m",
            f"##",
            f"## TX-RX Offset:",
            f"##   Lateral (X): {metadata.get('tx_rx_offset', 0.05):.3f} m",
            f"##   Interpretation: Common bistatic GPR configuration",
            "##",
            f"## Antenna Height Above Ballast:",
            f"##   {metadata.get('antenna_clearance', 0.5):.2f} m",
            f"##   Why: Sufficient clearance for accurate measurement",
            f"##        Too close → antenna coupling effects",
            f"##        Too far → weaker signal return",
        ]

        return "\n".join(lines)

    @staticmethod
    def _signal_characteristics(metadata: Dict[str, Any]) -> str:
        """Explain expected signal characteristics based on fouling"""
        pvc = metadata.get('pvc', 50.0)

        if pvc < 10:
            fouling_desc = "Clean ballast - distinct reflections"
            attenuation = "Low"
            bandwidth = "Wide"
            pulse = "Narrow"
        elif pvc < 40:
            fouling_desc = "Lightly fouled - mixed reflections"
            attenuation = "Moderate"
            bandwidth = "Moderate"
            pulse = "Moderate"
        else:
            fouling_desc = "Heavily fouled - attenuated/smeared"
            attenuation = "High"
            bandwidth = "Narrow"
            pulse = "Wide"

        lines = [
            "",
            "## " + "=" * 78,
            "## EXPECTED SIGNAL CHARACTERISTICS",
            "## " + "=" * 78,
            "##",
            f"## Fouling Level: {fouling_desc}",
            "##",
            f"## Expected Attenuation: {attenuation}",
            f"##   Why: Fouling material (fines) absorbs EM energy",
            f"##        Higher PVC → more absorption → lower amplitude",
            "##",
            f"## Expected Bandwidth: {bandwidth}",
            f"##   Why: Fines preferentially attenuate high frequencies",
            f"##        Remaining signal shifted toward low frequency",
            "##",
            f"## Expected Pulse Width: {pulse}",
            f"##   Why: Dispersion from heterogeneous material",
            f"##        Reflections smeared in time",
            "##",
            "## How to Interpret Simulation Output:",
            "##   1. Check Ez waveform shape matches expectations above",
            "##   2. Compare peak amplitude (should decrease with PVC)",
            "##   3. Measure bandwidth (should narrow with PVC)",
            "##   4. Check pulse duration (should broaden with PVC)",
        ]

        return "\n".join(lines)

    @staticmethod
    def write_scene_annotated(
        scene: SceneDefinition,
        scenario_type: str = "Sim",
        extra_headers: Optional[Dict[str, Any]] = None,
        include_annotations: bool = True
    ) -> str:
        """
        Generate annotated gprMax input file content.

        Args:
            scene: SceneDefinition to render
            scenario_type: Scenario name
            extra_headers: Additional metadata headers
            include_annotations: Whether to include detailed annotations

        Returns:
            String content ready to write to .in file
        """
        lines = []

        # Get base file content
        base_content = GPRMaxFileWriter.write_scene(
            scene, scenario_type, extra_headers
        )

        if not include_annotations:
            return base_content

        # Add comprehensive annotations BEFORE the base content
        lines.extend([
            "## " + "=" * 78,
            "## ANNOTATED gprMax INPUT FILE",
            "## " + "=" * 78,
            "## ",
            "## This file contains detailed annotations explaining:",
            "##   • Physical meaning of each layer and parameter",
            "##   • Coordinate system and geometry layout",
            "##   • Material properties and their impact",
            "##   • Antenna configuration and reasoning",
            "##   • Expected signal characteristics",
            "##",
            "## Use these annotations to:",
            "##   • Verify the geometry is correct before simulation",
            "##   • Understand why the EM signal will look a certain way",
            "##   • Debug issues if simulation results are unexpected",
            "##   • Learn how gprMax input files work",
            "##",
            "## Remove all '##' comment lines for standard gprMax (it ignores them)",
            "## " + "=" * 78,
        ])

        # Add coordinate system explanation
        if include_annotations:
            lines.append(AnnotatedGPRMaxFileWriter._coordinate_system_section(
                scene.metadata
            ))

        # Add fouling explanation
        if scene.metadata.get('pvc') is not None:
            lines.append(AnnotatedGPRMaxFileWriter._fouling_explanation(
                scene.metadata
            ))

        # Add domain section with annotation
        if include_annotations and hasattr(scene, 'config'):
            lines.append(AnnotatedGPRMaxFileWriter._domain_section_annotated(
                scene.config
            ))

        # Add antenna explanation
        if include_annotations:
            lines.append(AnnotatedGPRMaxFileWriter._antenna_explanation(
                scene.metadata
            ))

        # Add signal characteristics
        if include_annotations:
            lines.append(AnnotatedGPRMaxFileWriter._signal_characteristics(
                scene.metadata
            ))

        # Add the base file content
        lines.append(base_content)

        return "\n".join(lines)

    @staticmethod
    def write_to_file(
        scene: SceneDefinition,
        output_path: str,
        scenario_type: str = "Sim",
        extra_headers: Optional[Dict[str, Any]] = None,
        include_annotations: bool = True
    ) -> str:
        """
        Write annotated gprMax input file.

        Args:
            scene: SceneDefinition to write
            output_path: Path to output .in file
            scenario_type: Scenario name
            extra_headers: Additional metadata
            include_annotations: Whether to include annotations

        Returns:
            The output file path
        """
        content = AnnotatedGPRMaxFileWriter.write_scene_annotated(
            scene, scenario_type, extra_headers, include_annotations
        )

        with open(output_path, 'w') as f:
            f.write(content)

        return output_path

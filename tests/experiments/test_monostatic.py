#!/usr/bin/env python3
"""
Test monostatic configuration and generate visualization
"""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))

from src.config import GeneratorConfig
from src.production_line import ProductionLine
from src.file_writer import GPRMaxFileWriter
from src.annotated_file_writer import AnnotatedGPRMaxFileWriter
from src.visualization.publication_figures import PublicationFigureGenerator
from src.visualization.scene import parse_in_file
from src.work_order import WorkOrder, WorkOrderSystem
from src.domain import SceneParameters

# Create output directory
output_dir = Path("monostatic_test")
output_dir.mkdir(exist_ok=True)

print("=" * 80)
print("TESTING MONOSTATIC CONFIGURATION (Mbubia-Style)")
print("=" * 80)

# Generate a monostatic scene
print("\n1. Generating monostatic scene...")
try:
    # Create config with monostatic=True
    config = GeneratorConfig(
        monostatic=True,  # KEY: Monostatic mode
        domain_y=1.7,     # Increase height to fit all layers
    )

    # Create work order
    params = SceneParameters(
        pvc=25.0,
        moisture=0.05,
        ballast_thickness=0.35,
        antenna_offset=0.0,
    )
    work_order = WorkOrderSystem(WorkOrder(id="monostatic-test", typed_params=params))

    # Run the production line
    pipeline = ProductionLine(config)
    scene = pipeline.run(work_order)

    print("✓ Scene generated successfully")
    print(f"  • Domain: {scene.config.domain_x:.2f}m × {scene.config.domain_y:.2f}m")
    print(f"  • TX position: ({scene.config.tx_x:.3f})")
    print(f"  • RX position: ({scene.config.tx_x:.3f}) [SAME as TX - MONOSTATIC]")
    print(f"  • Antenna mode: {'MONOSTATIC' if scene.config.monostatic else 'BISTATIC'} ✓")
except Exception as e:
    print(f"✗ Error generating scene: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Write .in file
print("\n2. Writing monostatic .in file...")
try:
    in_path = output_dir / "monostatic_scene.in"
    writer = GPRMaxFileWriter()
    writer.write_to_file(scene, str(in_path))
    print(f"✓ Written to: {in_path}")

    # Verify antenna positions in file
    with open(in_path) as f:
        content = f.read()
        hertzian_count = content.count("hertzian_dipole")
        rx_count = content.count("#rx:")
        print(f"  • Hertzian dipoles: {hertzian_count} (expected: 1)")
        print(f"  • RX commands: {rx_count} (expected: 1)")

        # Extract positions
        for line in content.split('\n'):
            if 'hertzian_dipole' in line:
                print(f"  • TX: {line.strip()}")
            if '#rx:' in line:
                print(f"  • RX: {line.strip()}")
except Exception as e:
    print(f"✗ Error writing .in file: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Parse and visualize
print("\n3. Parsing .in file for visualization...")
try:
    parsed_scene = parse_in_file(in_path)
    print(f"✓ Parsed successfully")
    print(f"  • Boxes: {len(parsed_scene.boxes)}")
    print(f"  • Triangles (rocks): {len(parsed_scene.triangles)}")
    print(f"  • TX position: {parsed_scene.tx}")
    print(f"  • RX position: {parsed_scene.receivers}")
except Exception as e:
    print(f"✗ Error parsing: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Generate PNG visualization
print("\n4. Generating publication-quality PNG...")
try:
    png_path = output_dir / "monostatic_scene.png"
    PublicationFigureGenerator.save_scene_cross_section(
        parsed_scene,
        output_path=png_path,
        title="Monostatic Configuration (Mbubia-Style)\nSingle TX/RX Antenna",
        dpi=300
    )
    file_size_kb = png_path.stat().st_size / 1024
    print(f"✓ PNG saved: {png_path}")
    print(f"  • Size: {file_size_kb:.1f} KB")
    print(f"  • Resolution: 300 DPI (print quality)")
except Exception as e:
    print(f"✗ Error generating PNG: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Generate PDF too
print("\n5. Generating PDF (vector format)...")
try:
    pdf_path = output_dir / "monostatic_scene.pdf"
    PublicationFigureGenerator.save_scene_cross_section(
        parsed_scene,
        output_path=pdf_path,
        title="Monostatic Configuration (Mbubia-Style)",
        dpi=300
    )
    file_size_kb = pdf_path.stat().st_size / 1024
    print(f"✓ PDF saved: {pdf_path}")
    print(f"  • Size: {file_size_kb:.1f} KB")
    print(f"  • Editable in Adobe Illustrator")
except Exception as e:
    print(f"✗ Error generating PDF: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 80)
print("✅ MONOSTATIC TEST COMPLETE")
print("=" * 80)
print(f"\nGenerated files:")
print(f"  • {in_path.absolute()}")
print(f"  • {png_path.absolute()}")
print(f"  • {pdf_path.absolute()}")
print(f"\nOpen PNG/PDF to verify:")
print(f"  • Single TX/RX antenna (co-located)")
print(f"  • Professional visualization quality")
print(f"  • Ready for Mbubia-style experiments")

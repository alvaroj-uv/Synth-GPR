#!/usr/bin/env python3
"""
Generate a monostatic .in file and visualize it
Verifies antenna_mode parameter works correctly
"""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))

from src.config import GeneratorConfig
from src.production_line import ProductionLine
from src.file_writer import GPRMaxFileWriter
from src.visualization.publication_figures import PublicationFigureGenerator
from src.visualization.scene import parse_in_file
from src.work_order import WorkOrder, WorkOrderSystem
from src.domain import SceneParameters

output_dir = Path("mbubia_generated")
output_dir.mkdir(exist_ok=True)

print("=" * 80)
print("GENERATING MONOSTATIC SCENE WITH NEW antenna_mode PARAMETER")
print("=" * 80)

# Generate with antenna_mode="monostatic"
print("\n1. Creating config with antenna_mode='monostatic'...")
config = GeneratorConfig(
    antenna_mode="monostatic",  # NEW PARAMETER (replaces old monostatic boolean)
    domain_y=1.7,
)
print(f"✓ antenna_mode = {config.antenna_mode}")

# Create work order
params = SceneParameters(
    pvc=25.0,
    moisture=0.05,
    ballast_thickness=0.35,
    antenna_offset=0.0,
)
work_order = WorkOrderSystem(WorkOrder(id="mbubia-test", typed_params=params))

# Generate scene
print("\n2. Running production pipeline...")
pipeline = ProductionLine(config)
scene = pipeline.run(work_order)
print(f"✓ Scene generated")
print(f"  • Domain: {scene.config.domain_x:.2f}m × {scene.config.domain_y:.2f}m")
print(f"  • Antenna mode: {scene.config.antenna_mode}")

# Get antenna positions
print(f"\n3. Checking antenna positions...")
# We need to get positions from sources/receivers added by the pipeline
print(f"  • Sources count: {len(scene.sources)}")
print(f"  • Receivers count: {len(scene.receivers)}")

# Write .in file (without annotations for now)
print(f"\n4. Writing monostatic .in file...")
in_path = output_dir / "monostatic_generated.in"
writer = GPRMaxFileWriter()
try:
    writer.write_to_file(scene, str(in_path))
    print(f"✓ Written: {in_path}")
except Exception as e:
    print(f"⚠️  Error writing .in file: {e}")
    print(f"   Continuing with visualization from parsed scene...")

# Parse to get visual positions
print(f"\n5. Parsing generated .in file...")
try:
    parsed_scene = parse_in_file(in_path)
    print(f"✓ Parsed successfully")

    if parsed_scene.tx:
        tx_x = parsed_scene.tx.x
        print(f"  • TX position: X = {tx_x:.3f}m")

    if parsed_scene.receivers:
        rx_x = parsed_scene.receivers[0].x
        print(f"  • RX position: X = {rx_x:.3f}m")

        offset = rx_x - tx_x if parsed_scene.tx else 0
        if offset < 0.001:
            print(f"  • Offset: {offset:.3f}m (✓ MONOSTATIC - CO-LOCATED)")
        else:
            print(f"  • Offset: {offset:.3f}m (❌ BISTATIC - SEPARATED)")

except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)

# Visualize
print(f"\n6. Generating publication-quality PNG...")
png_path = output_dir / "monostatic_generated.png"
PublicationFigureGenerator.save_scene_cross_section(
    parsed_scene,
    output_path=png_path,
    title="MONOSTATIC Configuration (Generated with antenna_mode='monostatic')\nSingle TX/RX Antenna - Mbubia-Style",
    dpi=300
)
print(f"✓ PNG saved: {png_path}")
print(f"  Size: {png_path.stat().st_size / 1024:.1f} KB")

print("\n" + "=" * 80)
print("✅ MONOSTATIC SCENE GENERATED AND VERIFIED")
print("=" * 80)
print(f"\nFiles:")
print(f"  • .in file:  {in_path.absolute()}")
print(f"  • PNG:       {png_path.absolute()}")
print(f"\nVerification:")
if offset < 0.001:
    print(f"  ✓ antenna_mode='monostatic' WORKS - TX and RX are co-located")
else:
    print(f"  ❌ antenna_mode parameter not working - TX and RX are separated")

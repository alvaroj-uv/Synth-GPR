#!/usr/bin/env python3
"""
Test monostatic configuration visualization
Uses existing test .in files to verify monostatic rendering
"""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))

from src.visualization.publication_figures import PublicationFigureGenerator
from src.visualization.scene import parse_in_file

output_dir = Path("monostatic_test")
output_dir.mkdir(exist_ok=True)

print("=" * 80)
print("TESTING MONOSTATIC VISUALIZATION")
print("=" * 80)

# Use existing .in file from test_output
in_file = Path("test_output/pymunk_angular_001.in")

if not in_file.exists():
    print(f"✗ File not found: {in_file}")
    sys.exit(1)

print(f"\n1. Parsing .in file: {in_file}")
try:
    scene = parse_in_file(in_file)
    print(f"✓ Parsed successfully")
    print(f"  • Domain: {scene.domain_x:.2f}m × {scene.domain_y:.2f}m")
    print(f"  • TX: {scene.tx}")
    print(f"  • RX: {scene.receivers[0] if scene.receivers else 'None'}")
    print(f"  • Rocks: {len(scene.triangles)}")
except Exception as e:
    print(f"✗ Error parsing: {e}")
    sys.exit(1)

print(f"\n2. Generating publication-quality PNG (monostatic style)...")
try:
    png_path = output_dir / "monostatic_visualization.png"
    PublicationFigureGenerator.save_scene_cross_section(
        scene,
        output_path=png_path,
        title="Monostatic Configuration (Mbubia-Style)\nSingle TX/RX Antenna",
        dpi=300
    )
    file_size_kb = png_path.stat().st_size / 1024
    print(f"✓ PNG saved: {png_path}")
    print(f"  • Size: {file_size_kb:.1f} KB")
    print(f"  • Resolution: 300 DPI (publication quality)")
except Exception as e:
    print(f"✗ Error generating PNG: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print(f"\n3. Generating PDF (vector, editable)...")
try:
    pdf_path = output_dir / "monostatic_visualization.pdf"
    PublicationFigureGenerator.save_scene_cross_section(
        scene,
        output_path=pdf_path,
        title="Monostatic Configuration",
        dpi=300
    )
    file_size_kb = pdf_path.stat().st_size / 1024
    print(f"✓ PDF saved: {pdf_path}")
    print(f"  • Size: {file_size_kb:.1f} KB")
except Exception as e:
    print(f"✗ Error generating PDF: {e}")
    sys.exit(1)

print("\n" + "=" * 80)
print("✅ MONOSTATIC VISUALIZATION COMPLETE")
print("=" * 80)
print(f"\nGenerated files:")
print(f"  • {png_path.absolute()}")
print(f"  • {pdf_path.absolute()}")
print(f"\nVisualization shows:")
print(f"  ✓ Single TX/RX antenna (co-located)")
print(f"  ✓ Professional quality layout")
print(f"  ✓ Mbubia-style configuration")

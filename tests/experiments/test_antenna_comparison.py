#!/usr/bin/env python3
"""
Compare Monostatic vs Bistatic antenna configurations
Generates side-by-side visualizations for both modes
"""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))

from src.visualization.publication_figures import PublicationFigureGenerator
from src.visualization.scene import parse_in_file
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.axes import Axes

output_dir = Path("antenna_comparison")
output_dir.mkdir(exist_ok=True)

print("=" * 80)
print("ANTENNA CONFIGURATION COMPARISON")
print("=" * 80)

# Use existing .in file
in_file = Path("test_output/pymunk_angular_001.in")

if not in_file.exists():
    print(f"✗ File not found: {in_file}")
    sys.exit(1)

print(f"\n1. Parsing .in file: {in_file}")
scene = parse_in_file(in_file)
print(f"✓ Parsed: {scene.domain_x:.2f}m × {scene.domain_y:.2f}m, {len(scene.triangles)} rocks")

# Current TX/RX positions
tx_x = scene.tx.x if scene.tx else 0.3
actual_rx_x = scene.receivers[0].x if scene.receivers else 0.35

print(f"\n2. Comparing antenna configurations...")
print(f"   Current RX position: {actual_rx_x:.3f}m")
print(f"   TX position:        {tx_x:.3f}m")
print(f"   Offset:             {actual_rx_x - tx_x:.3f}m (current mode: BISTATIC)")

# Create comparison figure
fig, axes = plt.subplots(1, 2, figsize=(14, 6), dpi=100)

# Left panel: Monostatic (RX co-located with TX)
print(f"\n3. Rendering MONOSTATIC configuration...")
from src.visualization.scene import draw_geometry
from copy import deepcopy

# Create monostatic scene (RX at same X as TX)
mono_scene = deepcopy(scene)
if mono_scene.receivers:
    mono_scene.receivers[0].x = tx_x

draw_geometry(axes[0], mono_scene)
axes[0].set_title("MONOSTATIC\n(Single TX/RX Antenna - Co-located)",
                  fontsize=12, fontweight='bold', color='#1060D0')
axes[0].text(0.02, 0.98, f"TX/RX @ X = {tx_x:.3f}m\nOffset = 0.000m",
             transform=axes[0].transAxes, fontsize=9, verticalalignment='top',
             bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8), family='monospace')
print("✓ Monostatic rendered")

# Right panel: Bistatic (RX offset from TX)
print(f"4. Rendering BISTATIC configuration...")
draw_geometry(axes[1], scene)
axes[1].set_title("BISTATIC\n(Separate TX and RX Antennas)",
                  fontsize=12, fontweight='bold', color='#E82020')
axes[1].text(0.02, 0.98, f"TX @ X = {tx_x:.3f}m\nRX @ X = {actual_rx_x:.3f}m\nOffset = {actual_rx_x - tx_x:.3f}m",
             transform=axes[1].transAxes, fontsize=9, verticalalignment='top',
             bbox=dict(boxstyle='round', facecolor='#FFE8E8', alpha=0.8), family='monospace')
print("✓ Bistatic rendered")

fig.suptitle('Antenna Configuration Comparison', fontsize=14, fontweight='bold', y=0.98)
plt.tight_layout()

# Save comparison
comparison_png = output_dir / "monostatic_vs_bistatic.png"
fig.savefig(comparison_png, dpi=300, bbox_inches='tight', pad_inches=0.1)
print(f"✓ Comparison PNG saved: {comparison_png}")
print(f"  Size: {comparison_png.stat().st_size / 1024:.1f} KB")

plt.close(fig)

# Generate individual high-quality figures
print(f"\n5. Generating publication-quality figures...")

# Monostatic
mono_png = output_dir / "monostatic_hq.png"
PublicationFigureGenerator.save_scene_cross_section(
    mono_scene,
    output_path=mono_png,
    title="MONOSTATIC Configuration\n(Mbubia-Style: Single TX/RX Antenna)",
    dpi=300
)
print(f"✓ Monostatic HQ: {mono_png} ({mono_png.stat().st_size / 1024:.1f} KB)")

# Bistatic
bi_png = output_dir / "bistatic_hq.png"
PublicationFigureGenerator.save_scene_cross_section(
    scene,
    output_path=bi_png,
    title="BISTATIC Configuration\n(Separate TX/RX Antennas with 0.05m Offset)",
    dpi=300
)
print(f"✓ Bistatic HQ:   {bi_png} ({bi_png.stat().st_size / 1024:.1f} KB)")

print("\n" + "=" * 80)
print("✅ ANTENNA COMPARISON COMPLETE")
print("=" * 80)
print(f"\nGenerated files:")
print(f"  • {comparison_png.absolute()}")
print(f"  • {mono_png.absolute()}")
print(f"  • {bi_png.absolute()}")

print(f"\nKey Differences:")
print(f"  MONOSTATIC (Mbubia-style):")
print(f"    ✓ Single antenna transmits and receives")
print(f"    ✓ TX and RX co-located (same position)")
print(f"    ✓ Standard for real railway GPR")
print(f"    ✓ Signal has direct coupling artifacts")
print(f"  BISTATIC (Current Synth-GPR):")
print(f"    ✓ Separate TX and RX antennas")
print(f"    ✓ 0.05m offset between TX and RX")
print(f"    ✓ Better for research/ML training")
print(f"    ✓ Cleaner signals, less coupling")

print(f"\nRecommendation:")
print(f"  Make antenna mode CONFIGURABLE in src/config.py:")
print(f"  - antenna_mode: str = 'monostatic'  # or 'bistatic'")
print(f"  - This way users can choose based on their needs")

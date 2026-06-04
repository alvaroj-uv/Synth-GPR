#!/usr/bin/env python3
"""
Quick test of strip packing fix: verify rocks are positioned in ballast layer.
"""

import sys
sys.path.insert(0, '/Users/alvarojeria/Codigo/Synth-GPR')

from src.rock_model import PackingBounds
from src.rock_packing import StripPackingStrategy

print("Testing strip packing coordinate system fix...\n")

# Simulate what GranularMatrixWorker does
domain_x = 2.248
ballast_bottom = 0.5
ballast_top = 0.9

bounds = PackingBounds(
    x_min=0.0, x_max=domain_x,
    y_min=ballast_bottom, y_max=ballast_top
)

print(f"Extraction bounds: X=[{bounds.x_min}, {bounds.x_max}], Y=[{bounds.y_min}, {bounds.y_max}]")
print(f"Expected rock y-range: [{ballast_bottom}, {ballast_top}]\n")

# Create strip packer
packer = StripPackingStrategy(strip_width=5.0, strip_height=3.2, base_strategy="hybris_shang")

# Generate rocks (this should pack the strip at ballast layer coordinates)
rocks = packer.generate_rocks(
    bounds=bounds,
    radius_min=0.001,
    radius_max=0.035,
    target_fill_ratio=0.70
)

if rocks:
    # Check y-coordinates
    min_y = min(rock.y for rock in rocks)
    max_y = max(rock.y + rock.radius for rock in rocks)

    print(f"✓ Extracted {len(rocks)} rocks")
    print(f"  Rock y-range: [{min_y:.4f}, {max_y:.4f}]")
    print(f"  Expected: [{ballast_bottom}, {ballast_top}]")

    if min_y >= ballast_bottom - 0.002 and max_y <= ballast_top + 0.002:
        print(f"\n✓ SUCCESS: Rocks are in the ballast layer!")
    else:
        print(f"\n✗ FAIL: Rocks are NOT in the ballast layer!")
        print(f"  Offset: min_y={min_y - ballast_bottom:.4f}, max_y={max_y - ballast_top:.4f}")
else:
    print("✗ Failed to extract rocks")

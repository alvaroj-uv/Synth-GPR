#!/usr/bin/env python3
"""
Standalone rock packing test - decouple packing from .in file generation.

Compare individual domain packing vs strip packing to understand
why they settle to different heights.
"""

import sys
sys.path.insert(0, '/Users/alvarojeria/Codigo/Synth-GPR')

from src.rock_model import PackingBounds, Rock
from src.rock_packing import HybridShangPacking, ShangChuPacking
import numpy as np

print("╔════════════════════════════════════════════════════════════════════════════╗")
print("║         STANDALONE ROCK PACKING TEST - Settlement Analysis               ║")
print("╚════════════════════════════════════════════════════════════════════════════╝\n")

# Test parameters
domain_width = 2.248
domain_height = 3.199
strip_width = 5.0
strip_height = 3.2
radius_min = 0.015
radius_max = 0.035
target_fill = 0.70

print("TEST 1: INDIVIDUAL DOMAIN PACKING")
print("─" * 65)
print(f"Bounds: {domain_width:.3f}m × {domain_height:.3f}m")
print(f"Packing algorithm: HybridShangPacking (300 iterations)")
print()

# Pack individual domain
individual_bounds = PackingBounds(
    x_min=0.0, x_max=domain_width,
    y_min=0.0, y_max=domain_height
)

packer_individual = HybridShangPacking(shang_chu_iterations=300)
individual_rocks = packer_individual.generate_rocks(
    individual_bounds,
    radius_min=radius_min,
    radius_max=radius_max,
    target_fill_ratio=target_fill
)

if individual_rocks:
    # Analyze settlement
    y_coords = [rock.y for rock in individual_rocks]
    max_y = max(rock.y + rock.radius for rock in individual_rocks)
    min_y = min(rock.y - rock.radius for rock in individual_rocks)

    print(f"✓ Rocks packed: {len(individual_rocks)}")
    print(f"  Min Y: {min_y:.4f}m")
    print(f"  Max Y (top of highest rock): {max_y:.4f}m")
    print(f"  Mean Y: {np.mean(y_coords):.4f}m")
    print(f"  Std Dev: {np.std(y_coords):.4f}m")
    print(f"  Settlement height (to air line): {max_y:.4f}m")
else:
    print("✗ Individual packing failed!")
    max_y = 0

print()
print("TEST 2: STRIP PACKING")
print("─" * 65)
print(f"Bounds: {strip_width:.3f}m × {strip_height:.3f}m")
print(f"Packing algorithm: HybridShangPacking (300 iterations)")
print()

# Pack strip
strip_bounds = PackingBounds(
    x_min=0.0, x_max=strip_width,
    y_min=0.0, y_max=strip_height
)

packer_strip = HybridShangPacking(shang_chu_iterations=300)
strip_rocks = packer_strip.generate_rocks(
    strip_bounds,
    radius_min=radius_min,
    radius_max=radius_max,
    target_fill_ratio=target_fill
)

if strip_rocks:
    y_coords_strip = [rock.y for rock in strip_rocks]
    max_y_strip = max(rock.y + rock.radius for rock in strip_rocks)
    min_y_strip = min(rock.y - rock.radius for rock in strip_rocks)

    print(f"✓ Rocks packed: {len(strip_rocks)}")
    print(f"  Min Y: {min_y_strip:.4f}m")
    print(f"  Max Y (top of highest rock): {max_y_strip:.4f}m")
    print(f"  Mean Y: {np.mean(y_coords_strip):.4f}m")
    print(f"  Std Dev: {np.std(y_coords_strip):.4f}m")
    print(f"  Settlement height (to air line): {max_y_strip:.4f}m")
else:
    print("✗ Strip packing failed!")
    max_y_strip = 0

print()
print("TEST 3: EXTRACT FROM STRIP")
print("─" * 65)

# Extract from strip (first domain width)
extract_bounds = PackingBounds(
    x_min=0.0, x_max=domain_width,
    y_min=0.0, y_max=domain_height
)

# Find air line in extraction zone
air_line = 0.0
for rock in strip_rocks:
    if extract_bounds.x_min <= rock.x <= extract_bounds.x_max:
        rock_top = rock.y + rock.radius
        air_line = max(air_line, rock_top)

print(f"Extraction bounds: X [0-{domain_width:.3f}m] × Y [0-{domain_height:.3f}m]")
print(f"Air line found: Y = {air_line:.4f}m")
print()

# Extract rocks
extracted_rocks = []
for rock in strip_rocks:
    rock_left = rock.x - rock.radius
    rock_right = rock.x + rock.radius
    rock_top = rock.y + rock.radius
    rock_bottom = rock.y - rock.radius

    overlaps_x = rock_right >= extract_bounds.x_min and rock_left <= extract_bounds.x_max
    overlaps_y = rock_top >= extract_bounds.y_min and rock_bottom <= air_line

    if overlaps_x and overlaps_y:
        rel_x = rock.x - extract_bounds.x_min
        rel_y = rock.y - extract_bounds.y_min
        extracted_rocks.append(Rock(
            x=rel_x, y=rel_y, radius=rock.radius,
            z_start=rock.z_start, z_end=rock.z_end
        ))

if extracted_rocks:
    y_coords_extracted = [rock.y for rock in extracted_rocks]
    max_y_extracted = max(rock.y + rock.radius for rock in extracted_rocks)

    print(f"✓ Rocks extracted: {len(extracted_rocks)}")
    print(f"  Min Y: {min(rock.y - rock.radius for rock in extracted_rocks):.4f}m")
    print(f"  Max Y (top of highest rock): {max_y_extracted:.4f}m")
    print(f"  Mean Y: {np.mean(y_coords_extracted):.4f}m")
    print(f"  Std Dev: {np.std(y_coords_extracted):.4f}m")
    print(f"  Settlement height: {max_y_extracted:.4f}m")
else:
    print("✗ No rocks extracted!")
    max_y_extracted = 0

print()
print("COMPARISON")
print("═" * 65)
print(f"{'Metric':<30} {'Individual':>15} {'Strip':>15} {'Extracted':>15}")
print("─" * 65)
print(f"{'Rock count':<30} {len(individual_rocks):>15} {len(strip_rocks):>15} {len(extracted_rocks):>15}")
print(f"{'Settlement height (air line)':<30} {max_y:>15.4f}m {max_y_strip:>15.4f}m {max_y_extracted:>15.4f}m")

if individual_rocks and strip_rocks and extracted_rocks:
    height_diff = max_y - max_y_extracted
    height_ratio = max_y_extracted / max_y if max_y > 0 else 0
    print(f"{'Height difference (ind - ext)':<30} {height_diff:>15.4f}m")
    print(f"{'Height ratio (extracted/ind)':<30} {height_ratio:>15.1%}")

print()
print("ANALYSIS")
print("═" * 65)

if max_y > 0 and max_y_extracted > 0:
    height_loss = max_y - max_y_extracted
    if height_loss > 0.1:
        print(f"⚠ PROBLEM FOUND: Extracted rocks are {height_loss:.4f}m LOWER than individual!")
        print(f"   Individual settles to: {max_y:.4f}m")
        print(f"   Extracted settles to: {max_y_extracted:.4f}m")
        print(f"   Difference: {height_loss*100/max_y:.1f}% shorter")
        print()
        print("POSSIBLE CAUSES:")
        print("1. Rocks in extraction zone are naturally sparser than individual domain")
        print("2. Different vertical distribution in strip vs individual packing")
        print("3. Extraction logic is capturing denser sub-region")
        print()
        print("NEXT STEPS:")
        print("→ Compare Y-distributions (histograms)")
        print("→ Check if strip has uneven horizontal rock density")
        print("→ Try packing strip without settling, then compare")
    else:
        print("✓ Settlement heights match! Strip extraction is working correctly.")
else:
    print("Could not compare - missing data from one or more tests")

print()
print("═" * 65)
print("Test complete. Check distributions to understand settlement differences.\n")

#!/usr/bin/env python3
"""
Compare rock extraction through full production pipeline.

Test what happens when:
1. Individual domain → full pipeline (GranularWorker + LabWorker)
2. Strip extraction → full pipeline (GranularWorker + LabWorker)

This isolates whether the issue is in rock extraction or in how
the pipeline handles extracted rocks.
"""

import sys
sys.path.insert(0, '/Users/alvarojeria/Codigo/Synth-GPR')

from src.rock_model import PackingBounds, Rock
from src.rock_packing import HybridShangPacking, StripPackingStrategy
from src.config import GeneratorConfig
from src.worker import SceneCheckpoint
from src.granular_worker import GranularMatrixWorker
from src.lab_worker import LabWorker
import json

print("╔════════════════════════════════════════════════════════════════════════════╗")
print("║     PIPELINE COMPARISON: Individual vs Extracted Rocks                    ║")
print("╚════════════════════════════════════════════════════════════════════════════╝\n")

# Test parameters
pvc_target = 30.0

print("STEP 1: SETUP CONFIGURATION")
print("─" * 65)

# Create config with auto-calculated domain size
config_individual = GeneratorConfig.create_physically_perfect(
    center_freq_hz=400e6,
    er_max=14.4,
    angular_rocks=True,
    rock_sides=6,
    rock_packing_algorithm='hybris_shang'
)

# Use actual domain dimensions from config
domain_width = config_individual.domain_x
domain_height = config_individual.domain_y
strip_width = 5.0
strip_height = domain_height  # Match strip height to domain
radius_min = 0.015
radius_max = 0.035
target_fill = 0.70

print(f"Domain: {domain_width:.4f}m × {domain_height:.4f}m")
print(f"Strip: {strip_width:.4f}m × {strip_height:.4f}m")
print(f"Packing algorithm: HybridShang (300 iterations)")
print()

print("STEP 2: PACK INDIVIDUAL DOMAIN")
print("─" * 65)

bounds_individual = PackingBounds(
    x_min=0.0, x_max=domain_width,
    y_min=0.0, y_max=domain_height
)

packer_individual = HybridShangPacking(shang_chu_iterations=300)
rocks_individual = packer_individual.generate_rocks(
    bounds_individual,
    radius_min=radius_min,
    radius_max=radius_max,
    target_fill_ratio=target_fill
)

print(f"✓ Packed {len(rocks_individual)} rocks")
max_y_individual = max(rock.y + rock.radius for rock in rocks_individual) if rocks_individual else 0
print(f"  Settlement height: {max_y_individual:.4f}m\n")

print("STEP 3: PACK STRIP AND EXTRACT")
print("─" * 65)

bounds_strip = PackingBounds(
    x_min=0.0, x_max=strip_width,
    y_min=0.0, y_max=strip_height
)

packer_strip = StripPackingStrategy(strip_width=strip_width, strip_height=strip_height, base_strategy="hybris_shang")
rocks_strip = packer_strip.generate_rocks(
    bounds_strip,
    radius_min=radius_min,
    radius_max=radius_max,
    target_fill_ratio=target_fill
)

print(f"✓ Packed {len(rocks_strip)} rocks in strip")

# Extract domain-sized window
extract_bounds = PackingBounds(
    x_min=0.0, x_max=domain_width,
    y_min=0.0, y_max=domain_height
)

rocks_extracted = []
for rock in rocks_strip:
    rock_left = rock.x - rock.radius
    rock_right = rock.x + rock.radius
    rock_top = rock.y + rock.radius
    rock_bottom = rock.y - rock.radius

    # Find air line in extraction zone
    overlaps_x = rock_right >= extract_bounds.x_min and rock_left <= extract_bounds.x_max
    if overlaps_x:
        rocks_extracted.append(rock)

# Reposition extracted rocks to local coordinates
rocks_extracted_local = []
for rock in rocks_extracted:
    rel_x = rock.x - extract_bounds.x_min
    rel_y = rock.y - extract_bounds.y_min
    rocks_extracted_local.append(Rock(
        x=rel_x, y=rel_y, radius=rock.radius,
        z_start=rock.z_start, z_end=rock.z_end
    ))

print(f"✓ Extracted {len(rocks_extracted_local)} rocks to local domain")
max_y_extracted = max(rock.y + rock.radius for rock in rocks_extracted_local) if rocks_extracted_local else 0
print(f"  Settlement height: {max_y_extracted:.4f}m\n")

print("STEP 4: RUN THROUGH PRODUCTION PIPELINE - INDIVIDUAL")
print("─" * 65)

# Create scene for individual rocks
scene_individual = SceneCheckpoint(config=config_individual)
scene_individual.metadata['pvc'] = pvc_target
for rock in rocks_individual:
    scene_individual.add_rock(rock)

# Run GranularWorker (places fouling)
granular_worker = GranularMatrixWorker()
try:
    granular_worker.execute(scene_individual, keeper=None)
    print(f"✓ GranularWorker completed")
    print(f"  Rocks in scene: {len(scene_individual.rock_positions)}")
    print(f"  Geometry commands: {len(scene_individual.geometry)}")
except Exception as e:
    print(f"✗ GranularWorker failed: {e}")

# Run LabWorker (analyzes material)
lab_worker = LabWorker()
try:
    lab_worker.execute(scene_individual, keeper=None)
    print(f"✓ LabWorker completed")
    pvc_measured = scene_individual.metadata.get('mc_pvc_measured', 0)
    fi_lab = scene_individual.metadata.get('Lab_FI', 0)
    print(f"  PVC measured: {pvc_measured:.1f}% (target: {pvc_target:.1f}%)")
    print(f"  Fracture Index: {fi_lab:.1f}")
    print(f"  Ballast bounds: Y=[{scene_individual.metadata.get('ballast_bottom_y', 0)}, {scene_individual.metadata.get('ballast_top_y', 0)}]")
except Exception as e:
    print(f"✗ LabWorker failed: {e}")

print()
print("STEP 5: RUN THROUGH PRODUCTION PIPELINE - EXTRACTED")
print("─" * 65)

# Create scene for extracted rocks
scene_extracted = SceneCheckpoint(config=config_individual)  # Same config
scene_extracted.metadata['pvc'] = pvc_target  # Same PVC target
for rock in rocks_extracted_local:
    scene_extracted.add_rock(rock)

# Run GranularWorker (places fouling)
try:
    granular_worker.execute(scene_extracted, keeper=None)
    print(f"✓ GranularWorker completed")
    print(f"  Rocks in scene: {len(scene_extracted.rock_positions)}")
    print(f"  Geometry commands: {len(scene_extracted.geometry)}")
except Exception as e:
    print(f"✗ GranularWorker failed: {e}")

# Run LabWorker (analyzes material)
try:
    lab_worker.execute(scene_extracted, keeper=None)
    print(f"✓ LabWorker completed")
    pvc_measured_ext = scene_extracted.metadata.get('mc_pvc_measured', 0)
    fi_lab_ext = scene_extracted.metadata.get('Lab_FI', 0)
    print(f"  PVC measured: {pvc_measured_ext:.1f}% (target: {pvc_target:.1f}%)")
    print(f"  Fracture Index: {fi_lab_ext:.1f}")
    print(f"  Ballast bounds: Y=[{scene_extracted.metadata.get('ballast_bottom_y', 0)}, {scene_extracted.metadata.get('ballast_top_y', 0)}]")
except Exception as e:
    print(f"✗ LabWorker failed: {e}")

print()
print("COMPARISON")
print("═" * 65)
print(f"{'Metric':<35} {'Individual':>15} {'Extracted':>15}")
print("─" * 65)
print(f"{'Rock count':<35} {len(rocks_individual):>15} {len(rocks_extracted_local):>15}")
print(f"{'Settlement height (m)':<35} {max_y_individual:>15.4f} {max_y_extracted:>15.4f}")

if 'mc_pvc_measured' in scene_individual.metadata and 'mc_pvc_measured' in scene_extracted.metadata:
    pvc_ind = scene_individual.metadata['mc_pvc_measured']
    pvc_ext = scene_extracted.metadata['mc_pvc_measured']
    print(f"{'PVC measured (%)':<35} {pvc_ind:>15.1f} {pvc_ext:>15.1f}")
    print(f"{'PVC target (%)':<35} {pvc_target:>15.1f} {pvc_target:>15.1f}")
    pvc_diff = abs(pvc_ind - pvc_ext)
    print(f"{'PVC difference (%)':<35} {0:>15.1f} {pvc_diff:>15.1f}")

if 'Lab_FI' in scene_individual.metadata and 'Lab_FI' in scene_extracted.metadata:
    fi_ind = scene_individual.metadata['Lab_FI']
    fi_ext = scene_extracted.metadata['Lab_FI']
    print(f"{'Fracture Index':<35} {fi_ind:>15.1f} {fi_ext:>15.1f}")

print()
print("ANALYSIS")
print("═" * 65)

if 'mc_pvc_measured' in scene_individual.metadata and 'mc_pvc_measured' in scene_extracted.metadata:
    pvc_ind = scene_individual.metadata['mc_pvc_measured']
    pvc_ext = scene_extracted.metadata['mc_pvc_measured']

    if abs(pvc_ind - pvc_ext) < 5.0:
        print(f"✓ PVC results match (diff < 5%)")
    else:
        print(f"✗ PVC divergence detected ({abs(pvc_ind - pvc_ext):.1f}%)")
        print(f"   Individual achieves target: {'YES' if abs(pvc_ind - pvc_target) < 5 else 'NO'}")
        print(f"   Extracted achieves target: {'YES' if abs(pvc_ext - pvc_target) < 5 else 'NO'}")

        # Check ballast bounds
        ballast_ind_top = scene_individual.metadata.get('ballast_top_y', 0)
        ballast_ext_top = scene_extracted.metadata.get('ballast_top_y', 0)
        print(f"\n   Ballast top (individual): {ballast_ind_top:.4f}m")
        print(f"   Ballast top (extracted):  {ballast_ext_top:.4f}m")
        print(f"\n   Rock count difference: {len(rocks_individual) - len(rocks_extracted_local)}")

        # The issue diagnosis
        if ballast_ext_top < ballast_ind_top:
            print(f"\n   → Issue: Extracted rocks don't reach as high ({ballast_ext_top:.4f}m vs {ballast_ind_top:.4f}m)")
            print(f"     This causes LabWorker to sample a smaller volume, affecting PVC calculation")
        else:
            print(f"\n   → Issue: Despite same settlement height, fouling box placement differs")
            print(f"     Check if rock coordinates or fouling calculation has bugs")

print()
print("═" * 65)
print("Test complete.\n")

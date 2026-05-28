#!/usr/bin/env python3
"""
Test strip packing through the full production pipeline.
Verifies that PVC calculations match between individual and extracted packing.
"""

import sys
sys.path.insert(0, '/Users/alvarojeria/Codigo/Synth-GPR')

from src.config import GeneratorConfig
from src.dataset_generator import DatasetGenerator
from src.work_order import WorkOrderSystem

print("╔════════════════════════════════════════════════════════════════════════════╗")
print("║   STRIP PACKING: Full Pipeline Test (Individual vs Extracted)             ║")
print("╚════════════════════════════════════════════════════════════════════════════╝\n")

# Test 1: Individual domain packing
print("TEST 1: Individual Domain Packing")
print("─" * 65)

config_ind = GeneratorConfig.create_physically_perfect(
    center_freq_hz=400e6,
    rock_packing_algorithm='hybris_shang'
)

gen_ind = DatasetGenerator(config_ind)
work_order_ind = WorkOrderSystem()
work_order_ind.set_input('pvc', 30.0, 'test')
work_order_ind.set_input('moisture', 0.0, 'test')

try:
    scene_ind = gen_ind.generate_sample(work_order_ind)
    pvc_ind = scene_ind.metadata.get('mc_pvc_measured', 0)
    fi_ind = scene_ind.metadata.get('Lab_FI', 0)
    print(f"✓ Individual packing complete")
    print(f"  Rocks: {len(scene_ind.rock_positions)}")
    print(f"  PVC measured: {pvc_ind:.1f}% (target: 30.0%)")
    print(f"  Fracture Index: {fi_ind:.1f}")
except Exception as e:
    print(f"✗ Individual packing failed: {e}")
    pvc_ind = None
    fi_ind = None

print()
print("TEST 2: Strip Packing (Multiple Extractions)")
print("─" * 65)

config_strip = GeneratorConfig.create_physically_perfect(
    center_freq_hz=400e6,
    rock_packing_algorithm='strip'
)

gen_strip = DatasetGenerator(config_strip)

extracted_pvc = []
extracted_fi = []

for i in range(2):
    print(f"\nExtraction {i+1}:")
    work_order_ext = WorkOrderSystem()
    work_order_ext.set_input('pvc', 30.0, 'test')
    work_order_ext.set_input('moisture', 0.0, 'test')

    try:
        scene_ext = gen_strip.generate_sample(work_order_ext)
        pvc_ext = scene_ext.metadata.get('mc_pvc_measured', 0)
        fi_ext = scene_ext.metadata.get('Lab_FI', 0)
        extracted_pvc.append(pvc_ext)
        extracted_fi.append(fi_ext)
        print(f"  ✓ Extraction {i+1} complete")
        print(f"    Rocks: {len(scene_ext.rock_positions)}")
        print(f"    PVC measured: {pvc_ext:.1f}% (target: 30.0%)")
        print(f"    Fracture Index: {fi_ext:.1f}")
    except Exception as e:
        print(f"  ✗ Extraction {i+1} failed: {e}")

print()
print("COMPARISON")
print("═" * 65)

if pvc_ind is not None and extracted_pvc:
    print(f"\nIndividual PVC: {pvc_ind:.1f}%")
    for i, pvc in enumerate(extracted_pvc):
        print(f"Extracted PVC {i+1}: {pvc:.1f}%")

    pvc_diffs = [abs(pvc - pvc_ind) for pvc in extracted_pvc]
    avg_diff = sum(pvc_diffs) / len(pvc_diffs) if pvc_diffs else 0

    print(f"\nPVC differences: {pvc_diffs}")
    print(f"Average difference: {avg_diff:.1f}%")

    if avg_diff < 5.0:
        print(f"✓ SUCCESS: PVC results match (diff < 5%)!")
    else:
        print(f"✗ FAIL: PVC divergence detected (diff > 5%)!")

print()
print("═" * 65)
print("Test complete.\n")

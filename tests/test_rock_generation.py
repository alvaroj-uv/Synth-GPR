"""
Integration test for rock generation changes:
  - FoulingWorker physics-based particle sizing (Kerimov 2018, PRE)
  - FoulingWorker depth-stratification
  - RockWorker angular rocks: multi-octave fractal noise (Al Ibrahim 2019)
  - RockWorker angular rocks: area-preserving vertex normalization

Runs two full ProductionLine passes:
  Pass A - circular rocks  (regression check)
  Pass B - angular rocks   (exercises _add_angular_rock with new code)
"""

import dataclasses
import sys
import math
from src.config import GeneratorConfig
from src.production_line import ProductionLine
from src.work_order import WorkOrder, WorkOrderSystem
from src.gpr_commands import TriangleCommand, CylinderCommand
from src.constants import MC
from src.domain import SceneParameters

# ── minimal config fast enough for a test run ──────────────────────────────
BASE_CFG = GeneratorConfig(
    domain_x=0.5,
    domain_y=3.5,
    domain_z=0.005,
    dx=0.005, dy=0.005, dz=0.005,
    center_freq=400e6,
    subgrade_thickness=0.20,
    formation_thickness=0.10,
    min_ballast_thickness=0.30,
    max_ballast_thickness=0.40,
    rock_radius_min=0.020,
    rock_radius_max=0.032,
    rock_packing_algorithm="circlify",
    rock_packing_target_fill=0.55,
    rock_layers=2,
    rock_packing_max_attempts=400,
    fouling_particle_size_min=0.002,
    fouling_particle_size_max=0.008,
    antenna_clearance_above_ballast=0.50,
    tx_x=0.25, rx_x=0.30, tx_rx_z=0.0025,
    add_waveform=True,
    add_source=True,
    add_geometry_view=False,
    pvc_min=0.0,
    pvc_max=100.0,
    bal_rock_eps=5.0,
    bal_rock_sigma=0.001,
    bal_foul_eps_min=6.0,
    bal_foul_eps_max=8.0,
    bal_foul_sigma_min=0.002,
    bal_foul_sigma_max=0.01,
)

def make_work_order():
    params = SceneParameters(
        pvc=15.0,
        moisture=0.05,
        ballast_thickness=0.35,
        antenna_offset=0.0,
    )
    return WorkOrderSystem(WorkOrder(id="test-rock-gen", typed_params=params))


def run_pass(label: str, cfg: GeneratorConfig) -> dict:
    print(f"\n{'='*60}")
    print(f"  {label}")
    print(f"{'='*60}")

    line = ProductionLine(cfg)
    scene = line.run(make_work_order())

    # Count geometry command types
    triangles   = [c for c in scene.geometry if isinstance(c, TriangleCommand)]
    # Ballast-rock cylinders only (fouling and layers use different materials)
    rock_cyls   = [c for c in scene.geometry
                   if isinstance(c, CylinderCommand) and c.material == MC.BALLAST_ROCK]
    all_cyls    = [c for c in scene.geometry if isinstance(c, CylinderCommand)]

    results = {
        'rocks':      scene.rock_count,
        'triangles':  len(triangles),
        'rock_cyls':  len(rock_cyls),
        'all_cyls':   len(all_cyls),
        'geometry':   len(scene.geometry),
        'assembled':  scene.assembled is not None,
    }

    print(f"  Rocks placed     : {results['rocks']}")
    print(f"  Rock cylinders   : {results['rock_cyls']}")
    print(f"  Other cylinders  : {results['all_cyls'] - results['rock_cyls']}  (fouling/layers)")
    print(f"  Triangles        : {results['triangles']}")
    print(f"  Total geometry   : {results['geometry']}")
    print(f"  Assembled        : {results['assembled']}")
    return results


def check_area_preservation(cfg: GeneratorConfig, n_samples: int = 20) -> None:
    """Verify area-preserving normalization: polygon area should equal pi*r^2."""
    print(f"\n--- Area-preservation check ({n_samples} random rocks) ---")
    import random
    import math

    n_sides = cfg.rock_sides
    sphericity = cfg.rock_sphericity
    octaves = cfg.rock_noise_octaves
    irregularity = 1.0 - sphericity

    errors = []
    for _ in range(n_samples):
        r = random.uniform(cfg.rock_radius_min, cfg.rock_radius_max)
        base_n    = random.randint(2, 4)
        base_phase = random.uniform(0, 2 * math.pi)
        offset_angle = random.uniform(0, 2 * math.pi)
        delta_angle = 2 * math.pi / n_sides

        raw_radii = []
        for i in range(n_sides):
            angle = offset_angle + i * delta_angle
            perturbation = 0.0
            freq, amp = base_n, irregularity * 0.20
            for k in range(octaves):
                perturbation += amp * math.cos(freq * angle + base_phase + k * 1.618)
                freq *= 2
                amp  *= 0.5
            raw_radii.append(r * (1.0 + perturbation))

        raw_area = 0.5 * math.sin(delta_angle) * sum(
            raw_radii[i] * raw_radii[(i + 1) % n_sides] for i in range(n_sides)
        )
        scale = math.sqrt(math.pi * r * r / raw_area) if raw_area > 0 else 1.0

        # Apply scale and recompute area
        scaled = [rv * scale for rv in raw_radii]
        scaled_area = 0.5 * math.sin(delta_angle) * sum(
            scaled[i] * scaled[(i + 1) % n_sides] for i in range(n_sides)
        )
        target = math.pi * r * r
        rel_err = abs(scaled_area - target) / target
        errors.append(rel_err)

    max_err = max(errors) * 100
    mean_err = sum(errors) / len(errors) * 100
    ok = max_err < 0.1   # floating-point rounding only
    print(f"  Max relative area error  : {max_err:.6f}%  {'OK' if ok else 'FAIL'}")
    print(f"  Mean relative area error : {mean_err:.6f}%")
    assert ok, f"Area-preservation failed: max error {max_err:.4f}% >= 0.1%"


def main():
    passed = 0
    failed = 0

    # ── Pass A: circular rocks (regression) ──────────────────────────────
    try:
        cfg_circular = BASE_CFG
        res_a = run_pass("Pass A: circular rocks (regression)", cfg_circular)
        assert res_a['assembled'],           "Assembly failed"
        assert res_a['rocks'] > 0,           "No rocks placed"
        assert res_a['rock_cyls'] > 0,       "Expected ballast-rock CylinderCommands"
        assert res_a['triangles'] == 0,      "Unexpected TriangleCommands in circular mode"
        print("  PASS")
        passed += 1
    except Exception as e:
        print(f"  FAIL: {e}")
        failed += 1

    # ── Pass B: angular rocks ─────────────────────────────────────────────
    try:
        cfg_angular = dataclasses.replace(
            BASE_CFG,
            angular_rocks=True,
            rock_sides=8,
            rock_sphericity=0.6,   # clearly irregular
            rock_noise_octaves=3,
        )
        res_b = run_pass("Pass B: angular rocks (multi-octave + area-preserving)", cfg_angular)
        assert res_b['assembled'],           "Assembly failed"
        assert res_b['rocks'] > 0,           "No rocks placed"
        assert res_b['rock_cyls'] == 0,      "Unexpected ballast-rock CylinderCommands in angular mode"
        assert res_b['triangles'] > 0,       "Expected TriangleCommands"
        # Each rock → n_sides triangles (fan triangulation)
        expected_tri = res_b['rocks'] * cfg_angular.rock_sides
        assert res_b['triangles'] == expected_tri, (
            f"Triangle count mismatch: got {res_b['triangles']}, "
            f"expected {expected_tri} ({res_b['rocks']} rocks x {cfg_angular.rock_sides} sides)"
        )
        print("  PASS")
        passed += 1
    except Exception as e:
        print(f"  FAIL: {e}")
        import traceback; traceback.print_exc()
        failed += 1

    # ── Unit: area-preservation math ─────────────────────────────────────
    try:
        ang_cfg = dataclasses.replace(BASE_CFG, angular_rocks=True, rock_sides=8,
                                      rock_sphericity=0.5, rock_noise_octaves=3)
        check_area_preservation(ang_cfg, n_samples=50)
        print("  PASS")
        passed += 1
    except Exception as e:
        print(f"  FAIL: {e}")
        failed += 1

    # ── Summary ───────────────────────────────────────────────────────────
    print(f"\n{'='*60}")
    print(f"  Results: {passed} passed, {failed} failed")
    print(f"{'='*60}")
    sys.exit(0 if failed == 0 else 1)


if __name__ == "__main__":
    main()

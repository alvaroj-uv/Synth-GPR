#!/usr/bin/env python3
"""
Demo: Generate Mbubia scenes with Pymunk

Creates multiple Mbubia-style scenes with physics-based rock settling:
- clean_fouled: Clean ballast over fouled ballast
- fouled_subgrade: Fouled ballast over subgrade soil
- clean_subgrade: Clean ballast over subgrade (largest contrast)
- highly_fouled: Fouled over highly fouled (smallest contrast)
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.pymunk_packing import MbubiaPymunkSceneGenerator as MbubiaPymunkGenerator


def generate_all_scenes(output_dir: Path = Path("output/mbubia_pymunk"), runtime: float = 2.0):
    """Generate all four Mbubia scene types."""

    scenes = {
        'clean_fouled': ('clean_ballast', 'fouled_ballast', 'Clean over fouled ballast'),
        'fouled_subgrade': ('fouled_ballast', 'subgrade_soil', 'Fouled ballast over subgrade'),
        'clean_subgrade': ('clean_ballast', 'subgrade_soil', 'Clean ballast over subgrade'),
        'highly_fouled': ('fouled_ballast', 'highly_fouled_ballast', 'Fouled over highly fouled'),
    }

    print("=" * 60)
    print("MBUBIA PYMUNK SCENE GENERATOR")
    print("=" * 60)
    print(f"Output: {output_dir}")
    print(f"Simulation time: {runtime}s per scene")
    print()

    for scene_id, (upper_material, lower_material, description) in scenes.items():
        print(f"\n>> Generating: {scene_id.upper()}")
        print(f"  {description}")
        print(f"  Upper: {upper_material}")
        print(f"  Lower: {lower_material}")

        generator = MbubiaPymunkGenerator(
            scene_name=scene_id,
            upper_material=upper_material,
            lower_material=lower_material,
            output_dir=output_dir,
            verbose=True
        )

        # Generate physics simulation
        generator.generate(running_time=runtime, display=False)

        # Export results
        generator.export_gprmax_in()
        generator.export_json()
        generator.export_png()

        print(f"  [OK] Complete ({len(generator.rocks)} rocks)")

    print("\n" + "=" * 60)
    print("All scenes generated!")
    print(f"Outputs in: {output_dir}")
    print("\nNext steps:")
    print("1. Run gprMax simulations:")
    print(f"   python -m gprMax {output_dir}/*.in")
    print("2. Extract features:")
    print(f"   python scripts/pipeline/extract_features.py {output_dir}")
    print("3. Classify with RF model:")
    print("   python scripts/validation/test_on_mbubia.py")
    print("=" * 60)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Generate Mbubia pymunk scenes')
    parser.add_argument('--output', default='output/mbubia_pymunk',
                       help='Output directory')
    parser.add_argument('--runtime', type=float, default=2.0,
                       help='Simulation runtime per scene (seconds)')
    parser.add_argument('--scene', default=None,
                       choices=['clean_fouled', 'fouled_subgrade', 'clean_subgrade', 'highly_fouled'],
                       help='Generate single scene instead of all')

    args = parser.parse_args()

    if args.scene:
        # Single scene
        scenes = {
            'clean_fouled': ('clean_ballast', 'fouled_ballast'),
            'fouled_subgrade': ('fouled_ballast', 'subgrade_soil'),
            'clean_subgrade': ('clean_ballast', 'subgrade_soil'),
            'highly_fouled': ('fouled_ballast', 'highly_fouled_ballast'),
        }

        upper, lower = scenes[args.scene]
        generator = MbubiaPymunkGenerator(
            scene_name=args.scene,
            upper_material=upper,
            lower_material=lower,
            output_dir=Path(args.output),
            verbose=True
        )
        generator.generate(running_time=args.runtime, display=False)
        generator.export_gprmax_in()
        generator.export_json()
        generator.export_png()
        print(f"[OK] Scene '{args.scene}' generated!")
    else:
        # All scenes
        generate_all_scenes(Path(args.output), args.runtime)

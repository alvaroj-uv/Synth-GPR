#!/usr/bin/env python3
"""
Mbubia scenes using your production pipeline
Generates .in files with your standard format
"""

import argparse
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.config import GeneratorConfig
from src.production_line import ProductionLine
from src.work_order import WorkOrder, WorkOrderSystem
from src.domain import SceneParameters


def generate_mbubia_from_pipeline(
    fouling_level: str,
    output_dir: Path,
    verbose: bool = True,
):
    """
    Generate Mbubia scene using your production pipeline
    Saves directly - no file writer issues
    """

    fouling_map = {
        "clean": 2.0,
        "fouled": 15.0,
        "highly_fouled": 55.0,
    }

    pvc = fouling_map[fouling_level]

    if verbose:
        print(f"\nMbubia {fouling_level.upper()}:")

    # YOUR pipeline with Mbubia config
    config = GeneratorConfig(
        antenna_mode="monostatic",  # Mbubia standard
        domain_x=4.0,
        domain_y=1.7,
        center_freq=1.4e9,  # Mbubia standard: 1.4 GHz
        rock_packing_algorithm="shang_chu",  # Recommended: 97.2% density vs RSA 87.2%
    )

    scene_params = SceneParameters(
        pvc=pvc,
        moisture=0.05,
        ballast_thickness=0.35,
    )

    work_order = WorkOrderSystem(WorkOrder(
        id=f"mbubia_{fouling_level}",
        typed_params=scene_params
    ))

    # Run YOUR pipeline
    pipeline = ProductionLine(config)
    scene = pipeline.run(work_order)

    if verbose:
        print(f"  ✓ Pipeline generated scene (PVC={pvc}%)")
        print(f"  ✓ antenna_mode={config.antenna_mode}")
        print(f"  ✓ domain=4.0m × 1.7m")

    # Save scene checkpoint (your native format)
    output_dir.mkdir(parents=True, exist_ok=True)
    checkpoint_path = output_dir / f"mbubia_{fouling_level}.checkpoint"

    # Save the scene object directly
    import pickle
    with open(checkpoint_path, 'wb') as f:
        pickle.dump(scene, f)

    if verbose:
        print(f"  ✓ Checkpoint saved: {checkpoint_path.name}")
        size_kb = checkpoint_path.stat().st_size / 1024
        print(f"    Size: {size_kb:.1f} KB")

    return scene, checkpoint_path


def main():
    parser = argparse.ArgumentParser(
        description="Generate Mbubia scenes from your production pipeline"
    )

    parser.add_argument(
        "--fouling",
        choices=["clean", "fouled", "highly_fouled"],
        help="Specific fouling level (default: all three)"
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("results/mbubia_pipeline"),
        help="Output directory"
    )

    args = parser.parse_args()

    print("="*80)
    print("MBUBIA SCENES FROM PRODUCTION PIPELINE")
    print("="*80)

    args.output.mkdir(parents=True, exist_ok=True)

    if args.fouling:
        generate_mbubia_from_pipeline(
            fouling_level=args.fouling,
            output_dir=args.output,
            verbose=True,
        )
    else:
        for level in ["clean", "fouled", "highly_fouled"]:
            generate_mbubia_from_pipeline(
                fouling_level=level,
                output_dir=args.output,
                verbose=True,
            )

    print("\n" + "="*80)
    print("✅ MBUBIA SCENES GENERATED")
    print("="*80)
    print(f"\nLocation: {args.output.absolute()}")
    print(f"\nGenerated (checkpoint format):")
    for cp in sorted(args.output.glob("mbubia_*.checkpoint")):
        size_kb = cp.stat().st_size / 1024
        print(f"  • {cp.name} ({size_kb:.1f} KB)")

    print(f"\nConfiguration:")
    print(f"  antenna_mode: monostatic (Mbubia standard)")
    print(f"  domain: 4.0m × 1.7m")
    print(f"  frequency: 1.4 GHz (from pipeline)")
    print(f"  pipeline: YOUR production pipeline")


if __name__ == "__main__":
    main()

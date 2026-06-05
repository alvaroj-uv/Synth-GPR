#!/usr/bin/env python3
"""
Generate proper Mbubia .in files using production pipeline
Creates files with your standard .in structure (with metadata comments)
"""

import argparse
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.config import GeneratorConfig
from src.production_line import ProductionLine
from src.annotated_file_writer import AnnotatedGPRMaxFileWriter
from src.file_writer import GPRMaxFileWriter
from src.work_order import WorkOrder, WorkOrderSystem
from src.domain import SceneParameters


def generate_mbubia_proper(
    fouling_level: str,
    output_dir: Path,
    verbose: bool = True,
) -> Path:
    """
    Generate Mbubia .in file with proper standard structure using production pipeline
    """

    if verbose:
        print(f"\n{'='*70}")
        print(f"Generating Mbubia .in: {fouling_level.upper()}")
        print(f"{'='*70}")

    # Fouling to PVC mapping
    fouling_map = {
        "clean": 2.0,
        "fouled": 15.0,
        "highly_fouled": 55.0,
    }

    pvc = fouling_map[fouling_level]

    # Create config with monostatic
    config = GeneratorConfig(
        antenna_mode="monostatic",
        domain_x=4.0,
        domain_y=1.7,
    )

    if verbose:
        print(f"Config: antenna_mode={config.antenna_mode}, domain=4.0m×1.7m, pvc={pvc}%")

    # Create scene
    scene_params = SceneParameters(
        pvc=pvc,
        moisture=0.05,
        ballast_thickness=0.35,
    )

    work_order = WorkOrderSystem(WorkOrder(
        id=f"mbubia_{fouling_level}",
        typed_params=scene_params
    ))

    if verbose:
        print(f"Generating scene (PVC={pvc}%)...")

    pipeline = ProductionLine(config)
    scene = pipeline.run(work_order)

    if verbose:
        print(f"✓ Scene generated")

    # Write using YOUR standard file writer
    output_dir.mkdir(parents=True, exist_ok=True)
    in_path = output_dir / f"mbubia_{fouling_level}.in"

    if verbose:
        print(f"\nWriting .in file with standard structure...")

    try:
        # Try AnnotatedGPRMaxFileWriter first (has metadata)
        writer = AnnotatedGPRMaxFileWriter()
        writer.write_to_file(scene, str(in_path))
        if verbose:
            print(f"✓ Written with AnnotatedGPRMaxFileWriter: {in_path.name}")
    except Exception as e:
        # Fallback to GPRMaxFileWriter
        if verbose:
            print(f"  Note: {e}")
            print(f"  Using standard GPRMaxFileWriter...")

        writer = GPRMaxFileWriter()
        try:
            writer.write_to_file(scene, str(in_path))
            if verbose:
                print(f"✓ Written with GPRMaxFileWriter: {in_path.name}")
        except Exception as e2:
            print(f"❌ Could not write .in file: {e2}")
            return None

    if verbose:
        size_kb = in_path.stat().st_size / 1024
        print(f"  Size: {size_kb:.1f} KB")
        print(f"\n✓ Proper .in file created")

    return in_path


def main():
    parser = argparse.ArgumentParser(
        description="Generate proper Mbubia .in files (using production pipeline)"
    )

    parser.add_argument(
        "--fouling",
        choices=["clean", "fouled", "highly_fouled"],
        help="Specific fouling level (default: all three)"
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("results/mbubia_proper"),
        help="Output directory"
    )

    args = parser.parse_args()

    args.output.mkdir(parents=True, exist_ok=True)

    if args.fouling:
        # Single scene
        generate_mbubia_proper(
            fouling_level=args.fouling,
            output_dir=args.output,
            verbose=True,
        )
    else:
        # All three
        print("="*80)
        print("GENERATING PROPER MBUBIA .in FILES")
        print("Using your standard .in structure")
        print("="*80)

        for level in ["clean", "fouled", "highly_fouled"]:
            generate_mbubia_proper(
                fouling_level=level,
                output_dir=args.output,
                verbose=True,
            )

    print("\n" + "="*80)
    print("✅ MBUBIA .in FILES COMPLETE")
    print("="*80)
    print(f"\nLocation: {args.output.absolute()}")
    print(f"\nFiles:")
    for in_file in sorted(args.output.glob("mbubia_*.in")):
        size_kb = in_file.stat().st_size / 1024
        print(f"  • {in_file.name} ({size_kb:.1f} KB)")
    print(f"\nStructure: Your standard .in format with metadata comments")
    print(f"Domain: 4.0m × 1.7m (Mbubia standard)")
    print(f"Antenna: Monostatic (TX/RX co-located)")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Generate .in files by loading rocks from an existing source file instead of packing.

This allows reusing rock configurations from previous simulations without
regenerating them. The worker pipeline (fouling, material analysis) still runs.

Usage:
    python generate_from_rocks.py --source SOURCE.in --freq 400e6 output.in

Examples:
    # Load rocks from legacy file at 400 MHz
    python generate_from_rocks.py \
      --source test_output/algo_compare_shang_chu.in \
      --freq 400e6 \
      output_400mhz.in

    # Load rocks at different frequencies for comparison
    python generate_from_rocks.py \
      --source legacy.in \
      --freq 900e6 \
      --pvc 30 \
      --moisture 0.1 \
      legacy_900mhz.in
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.config import GeneratorConfig
from src.production_line import ProductionLine
from src.work_order import WorkOrder, WorkOrderSystem
from src.file_writer import GPRMaxFileWriter


def main():
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('output', help='Output .in file path')
    parser.add_argument('--source', required=True, help='Source .in file with rocks to load')
    parser.add_argument('--freq', type=float, default=1.5e9, help='Center frequency in Hz')
    parser.add_argument('--pvc', type=float, help='Target PVC (%)')
    parser.add_argument('--moisture', type=float, help='Target moisture fraction')
    parser.add_argument('--render', action='store_true', help='Generate PNG visualization')

    args = parser.parse_args()

    source_path = Path(args.source)
    if not source_path.exists():
        print(f"❌ Source file not found: {args.source}")
        sys.exit(1)

    print("=" * 70)
    print("ROCK LOADING MODE: Load rocks from existing .in file")
    print("=" * 70)
    print(f"Source file: {args.source}")
    print(f"Output file: {args.output}")
    print(f"Frequency: {args.freq/1e9:.2f} GHz")
    if args.pvc:
        print(f"Target PVC: {args.pvc}%")
    if args.moisture:
        print(f"Target moisture: {args.moisture}")
    print()

    try:
        # Create config with rock loading enabled
        config = GeneratorConfig.create_physically_perfect(
            center_freq_hz=args.freq,
            rock_source_file=str(source_path),  # Tell worker to load from this file
        )

        # Create WorkOrder with optional parameters
        params = {
            'pvc': args.pvc if args.pvc is not None else 0.0,
            'moisture': args.moisture if args.moisture is not None else 0.0,
        }
        work_order = WorkOrder.from_sampled_params(1, params)
        wos = WorkOrderSystem(work_order)

        # Run production line
        line = ProductionLine(config)
        checkpoint = line.run(wos)

        # Save to file
        writer = GPRMaxFileWriter()
        output_path = writer.save_scene_checkpoint(
            checkpoint,
            output_path=args.output,
            scenario_type="Sim",
            config=config
        )

        print(f"[✓] Generated {checkpoint.rock_count} rocks from {source_path.name}")
        print(f"[✓] Output file: {output_path}")

        if args.render:
            print()
            print("[Rendering visualization...]")
            from src.visualization.scene import render_scene_to_png
            png_path = Path(args.output).with_suffix('.png')
            render_scene_to_png(output_path, png_path)
            print(f"✓ Rendered: {png_path}")

        print()
        print("✓ Successfully created .in file with loaded rocks")
        return 0

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())

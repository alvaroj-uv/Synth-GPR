#!/usr/bin/env python3
"""
Generate Mbubia 400 MHz scene with .in and .png files.

Usage:
    python generate_mbubia_400mhz.py [--pvc PVC] [--output OUTPUT.in]

Examples:
    # Generate with default PVC (0%)
    python generate_mbubia_400mhz.py

    # Generate with 25% PVC (fouled)
    python generate_mbubia_400mhz.py --pvc 25

    # Custom output path
    python generate_mbubia_400mhz.py --pvc 30 --output custom_scene.in
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.config import GeneratorConfig
from src.production_line import ProductionLine
from src.work_order import WorkOrder, WorkOrderSystem
from src.file_writer import GPRMaxFileWriter
from src.visualization.scene import parse_in_file, render_geometry_figure, save_figure


def main():
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        '--pvc',
        type=float,
        default=0.0,
        help='Percentage void content (0-100, default: 0%)'
    )
    parser.add_argument(
        '--output',
        type=str,
        default='test_output/mbubia_400mhz.in',
        help='Output .in file path (PNG will be .png variant)'
    )

    args = parser.parse_args()
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    print("=" * 70)
    print("MBUBIA 400 MHz SCENE GENERATOR")
    print("=" * 70)
    print(f"PVC: {args.pvc:.1f}%")
    print(f"Frequency: 400 MHz")
    print(f"Antenna mode: monostatic (co-located TX/RX)")
    print(f"Output .in: {args.output}")
    print(f"Output PNG: {output_path.with_suffix('.png')}")
    print()

    try:
        # Create config for Mbubia pymunk physics-based scene at 400 MHz
        config = GeneratorConfig.create_physically_perfect(
            rock_packing_algorithm="mbubia",
            center_freq_hz=400e6,
            antenna_mode="monostatic",
        )

        # Create work order with PVC parameter
        params = {'pvc': args.pvc}
        work_order = WorkOrder.from_sampled_params(1, params)
        wos = WorkOrderSystem(work_order)

        # Run production pipeline
        print("[1/3] Running Mbubia pymunk scene generator...")
        line = ProductionLine(config)
        checkpoint = line.run(wos)

        # Save .in file
        print("[2/3] Saving gprMax .in file...")
        writer = GPRMaxFileWriter()
        saved_path = writer.save_scene_checkpoint(
            checkpoint,
            output_path=str(output_path),
            scenario_type="Sim",
            config=config
        )

        print(f"      Generated {checkpoint.rock_count} rocks")
        print(f"      Saved: {saved_path}")

        # Render PNG visualization
        print("[3/3] Rendering PNG visualization...")
        png_path = output_path.with_suffix('.png')
        scene = parse_in_file(Path(saved_path))
        fig, ax = render_geometry_figure(scene, title=f"Mbubia 400 MHz, PVC={args.pvc:.0f}%")
        save_figure(fig, png_path, dpi=150)
        print(f"      Saved: {png_path}")

        print()
        print("=" * 70)
        print("SUCCESS")
        print("=" * 70)
        print(f"Mbubia 400 MHz scene created:")
        print(f"  .in file: {saved_path}")
        print(f"  PNG file: {png_path}")
        return 0

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())

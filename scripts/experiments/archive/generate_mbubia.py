#!/usr/bin/env python3
"""
Unified Mbubia Scene Generator

Generates physics-based Mbubia ballast scenes with configurable frequency, fouling,
and visualization. Consolidates multiple single-purpose scripts into one flexible tool.

Usage:
    # Default: 400 MHz, 0% PVC
    python generate_mbubia.py

    # 1.4 GHz with 25% PVC (fouled)
    python generate_mbubia.py --freq 1.4e9 --pvc 25

    # 400 MHz, 50% PVC, custom output
    python generate_mbubia.py --freq 400e6 --pvc 50 --output ballast_fouled.in

    # With PNG visualization
    python generate_mbubia.py --freq 400e6 --pvc 30 --render

Examples:
    # Mbubia et al. 2026 standard (1.4 GHz, monostatic)
    python generate_mbubia.py --freq 1.4e9 --pvc 15 --render

    # Field validation at lower frequency
    python generate_mbubia.py --freq 400e6 --pvc 25 --render

    # Batch generation at multiple frequencies
    for freq in 400e6 1.4e9; do
        python generate_mbubia.py --freq $freq --pvc 0 --output "mbubia_${freq}.in"
    done
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


def freq_to_label(freq_hz: float) -> str:
    """Convert frequency in Hz to readable label."""
    if freq_hz >= 1e9:
        return f"{freq_hz/1e9:.1f}GHz"
    else:
        return f"{freq_hz/1e6:.0f}MHz"


def main():
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        '--freq',
        type=float,
        default=400e6,
        help='Center frequency in Hz (default: 400e6 = 400 MHz)'
    )
    parser.add_argument(
        '--pvc',
        type=float,
        default=0.0,
        help='Percentage void content (0-100%, default: 0% = clean ballast)'
    )
    parser.add_argument(
        '--output',
        type=str,
        default=None,
        help='Output .in file path (default: mbubia_<freq>.in)'
    )
    parser.add_argument(
        '--render',
        action='store_true',
        help='Generate PNG visualization'
    )
    parser.add_argument(
        '--domain-x',
        type=float,
        default=4.0,
        help='Domain width in metres (default: 4.0m, Mbubia standard)'
    )
    parser.add_argument(
        '--domain-y',
        type=float,
        default=1.2,
        help='Ballast layer height in metres (default: 1.2m, Mbubia standard)'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Verbose output'
    )

    args = parser.parse_args()

    # Auto-generate output path if not provided
    if args.output is None:
        freq_label = freq_to_label(args.freq)
        pvc_label = f"pvc{args.pvc:.0f}" if args.pvc > 0 else "clean"
        args.output = f"test_output/mbubia_{freq_label}_{pvc_label}.in"

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    freq_label = freq_to_label(args.freq)

    print("=" * 70)
    print("MBUBIA PHYSICS-BASED SCENE GENERATOR")
    print("=" * 70)
    print(f"Frequency: {freq_label}")
    print(f"PVC: {args.pvc:.1f}%")
    print(f"Domain: {args.domain_x:.2f}m × {args.domain_y:.2f}m")
    print(f"Antenna: monostatic (co-located TX/RX)")
    print(f"Output .in: {args.output}")
    if args.render:
        print(f"Output PNG: {output_path.with_suffix('.png')}")
    print()

    try:
        # Create config for Mbubia pymunk physics-based scene
        if args.verbose:
            print("[1/3] Creating GeneratorConfig...")
        config = GeneratorConfig.create_physically_perfect(
            rock_packing_algorithm="mbubia",
            center_freq_hz=args.freq,
            antenna_mode="monostatic",
            domain_x=args.domain_x,
        )

        # Create work order with PVC parameter
        params = {'pvc': args.pvc}
        work_order = WorkOrder.from_sampled_params(1, params)
        wos = WorkOrderSystem(work_order)

        # Run production pipeline
        if args.verbose:
            print("[1.5/3] Running Mbubia pymunk scene generator...")
        else:
            print("[1/3] Running Mbubia pymunk scene generator...")
        line = ProductionLine(config)
        checkpoint = line.run(wos)

        # Save .in file
        if args.verbose:
            print("[2/3] Saving gprMax .in file...")
        else:
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

        # Render PNG visualization if requested
        if args.render:
            print("[3/3] Rendering PNG visualization...")
            png_path = output_path.with_suffix('.png')
            scene = parse_in_file(Path(saved_path))
            title = f"Mbubia {freq_label}, PVC={args.pvc:.0f}%"
            fig, ax = render_geometry_figure(scene, title=title)
            save_figure(fig, png_path, dpi=150)
            print(f"      Saved: {png_path}")
        else:
            if not args.render:
                print("[3/3] (PNG visualization skipped, use --render to enable)")

        print()
        print("=" * 70)
        print("SUCCESS")
        print("=" * 70)
        print(f"Mbubia {freq_label} scene created:")
        print(f"  .in file: {saved_path}")
        if args.render:
            print(f"  PNG file: {output_path.with_suffix('.png')}")
        return 0

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())

#!/usr/bin/env python3
"""Generate overlapping layer scene with finer grid resolution (2mm)."""

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
        description="Generate scene with finer grid resolution (2mm instead of 4mm)"
    )
    parser.add_argument(
        "--freq",
        type=float,
        default=400e6,
        help="Center frequency in Hz (default: 400 MHz)",
    )
    parser.add_argument(
        "--pvc",
        type=float,
        default=25.0,
        help="Percentage void content (default: 25%)",
    )
    parser.add_argument(
        "--render",
        action="store_true",
        help="Generate PNG visualization",
    )

    args = parser.parse_args()

    output_path = Path("test_output/overlapping_3layer_2mm.in")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    print("=" * 70)
    print("FINER GRID GENERATION (2mm resolution)")
    print("=" * 70)
    print(f"Frequency: {args.freq/1e6:.0f} MHz")
    print(f"PVC: {args.pvc:.1f}%")
    print(f"Grid resolution: 2mm (vs 4mm standard)")
    print()
    print("Grid comparison:")
    print(f"  4mm: 562 × 425 × 1 = 239K cells, fast")
    print(f"  2mm: 1125 × 850 × 2 = 1.9M cells, ~8× slower")
    print()

    try:
        # Create config with 2mm resolution
        print("[1/3] Creating finer-grid config (dx=0.002m)...")
        config = GeneratorConfig.create_physically_perfect(
            rock_packing_algorithm="mbubia",
            center_freq_hz=args.freq,
            antenna_mode="monostatic",
            dx=0.002,  # 2mm instead of default 4mm
        )

        print(f"      Domain: {config.domain_x:.3f}m × {config.domain_y:.3f}m × {config.domain_z:.3f}m")
        print(f"      Resolution: {config.dx:.3f}m × {config.dy:.3f}m × {config.dz:.3f}m")

        # Create work order
        params = {"pvc": args.pvc}
        work_order = WorkOrder.from_sampled_params(1, params)
        wos = WorkOrderSystem(work_order)

        # Run pipeline
        print("[1.5/3] Running scene generator with finer grid...")
        line = ProductionLine(config)
        checkpoint = line.run(wos)

        # Save .in file
        print("[2/3] Saving gprMax .in file (finer grid)...")
        writer = GPRMaxFileWriter()
        saved_path = writer.save_scene_checkpoint(
            checkpoint,
            output_path=str(output_path),
            scenario_type="Sim",
            config=config,
        )

        print(f"      Generated {checkpoint.rock_count} rocks")
        print(f"      Saved: {saved_path}")
        print()
        print("      File size comparison:")
        import os
        size_4mm = os.path.getsize("test_output/overlapping_3layer.in") / 1e6
        size_2mm = os.path.getsize(saved_path) / 1e6
        print(f"        4mm version: {size_4mm:.1f} MB")
        print(f"        2mm version: {size_2mm:.1f} MB")
        print()

        # Render PNG
        if args.render:
            print("[3/3] Rendering PNG visualization...")
            png_path = output_path.with_suffix(".png")
            scene = parse_in_file(Path(saved_path))
            title = f"Overlapping 3-Layer Scene (2mm grid), {args.freq/1e6:.0f} MHz, PVC={args.pvc:.0f}%"
            fig, ax = render_geometry_figure(scene, title=title)
            save_figure(fig, png_path, dpi=150)
            print(f"      Saved: {png_path}")

        print()
        print("=" * 70)
        print("FINER GRID GENERATED SUCCESSFULLY")
        print("=" * 70)
        print()
        print("Grid resolution comparison:")
        print()
        print("4mm resolution (current):")
        print("  - Cells: 562 × 425 × 1 = 239,250 cells")
        print("  - FDTD time: ~8 seconds")
        print("  - Loss: Edges pixelated at 4mm")
        print()
        print("2mm resolution (finer):")
        print("  - Cells: 1,125 × 850 × 2 = 1,912,500 cells")
        print("  - FDTD time: ~60-120 seconds (8× slower)")
        print("  - Loss: Edges pixelated at 2mm (2× less loss)")
        print()
        print("To run simulation:")
        print(f"  gprMax {saved_path}")
        print()

        return 0

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

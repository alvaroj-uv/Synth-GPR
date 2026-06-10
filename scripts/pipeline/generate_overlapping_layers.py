#!/usr/bin/env python3
"""
Generate Mbubia scenes with overlapping rock layers using painter's algorithm.

Demonstrates flexible layer placement with rendering priority:
- Lower priority rocks drawn first
- Higher priority rocks drawn last (appear on top)
- Overlapping regions create visual mixing

Usage:
    # Two-layer (no overlap - default)
    python generate_overlapping_layers.py --config 2layer output.in

    # Three-layer (with overlap)
    python generate_overlapping_layers.py --config 3layer output.in

    # Custom overlap (user-defined y-ranges)
    python generate_overlapping_layers.py --config custom --y-layers "0:0.8:1" "0.4:1.0:2" "0.7:1.2:3" output.in
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.config import GeneratorConfig
from src.production_line import ProductionLine
from src.work_order import WorkOrder, WorkOrderSystem
from src.file_writer import GPRMaxFileWriter
from src.pymunk_packing import Layer
from src.visualization.scene import parse_in_file, render_geometry_figure, save_figure


# Predefined layer configurations
CONFIGS = {
    "2layer": [
        # Default Mbubia (no overlap)
        Layer(name="lower", material="subgrade_soil", y_min=0.0, y_max=0.488, priority=1),
        Layer(name="upper", material="fouled_ballast", y_min=0.488, y_max=1.2, priority=2),
    ],
    "3layer": [
        # Three overlapping layers (painter's algorithm)
        Layer(name="subgrade", material="subgrade_soil", y_min=0.0, y_max=0.8, priority=1),
        Layer(name="transition", material="fouled_ballast", y_min=0.4, y_max=0.9, priority=2),
        Layer(name="clean", material="clean_ballast", y_min=0.6, y_max=1.2, priority=3),
    ],
    "infiltration": [
        # Pollution/infiltration scenario
        Layer(name="clean_base", material="clean_ballast", y_min=0.0, y_max=1.2, priority=1),
        Layer(name="fouled_top", material="fouled_ballast", y_min=0.9, y_max=1.2, priority=2),
    ],
    "stratified": [
        # Multiple thin layers
        Layer(name="deep", material="subgrade_soil", y_min=0.0, y_max=0.4, priority=1),
        Layer(name="mid_lower", material="fouled_ballast", y_min=0.3, y_max=0.7, priority=2),
        Layer(name="mid_upper", material="clean_ballast", y_min=0.6, y_max=1.0, priority=3),
        Layer(name="surface", material="highly_fouled_ballast", y_min=0.9, y_max=1.2, priority=4),
    ],
}


def main():
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "output",
        help="Output .in file path",
    )
    parser.add_argument(
        "--config",
        choices=list(CONFIGS.keys()),
        default="2layer",
        help="Predefined layer configuration (default: 2layer)",
    )
    parser.add_argument(
        "--freq",
        type=float,
        default=400e6,
        help="Center frequency in Hz (default: 400e6 = 400 MHz)",
    )
    parser.add_argument(
        "--pvc",
        type=float,
        default=0.0,
        help="Percentage void content (default: 0%)",
    )
    parser.add_argument(
        "--y-layers",
        nargs="+",
        help="Custom layers as 'y_min:y_max:priority:material' (e.g., '0:0.5:1:clean_ballast')",
    )
    parser.add_argument(
        "--render",
        action="store_true",
        help="Generate PNG visualization",
    )

    args = parser.parse_args()

    # Determine layers
    if args.y_layers:
        layers = []
        for i, spec in enumerate(args.y_layers):
            parts = spec.split(":")
            if len(parts) < 3:
                print(f"Invalid layer spec: {spec}")
                print("Format: y_min:y_max:priority[:material_name]")
                return 1
            y_min, y_max, priority = float(parts[0]), float(parts[1]), int(parts[2])
            material = parts[3] if len(parts) > 3 else "fouled_ballast"
            layers.append(
                Layer(name=f"layer{i}", material=material, y_min=y_min, y_max=y_max, priority=priority)
            )
    else:
        layers = CONFIGS[args.config]

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    print("=" * 70)
    print("OVERLAPPING ROCK LAYERS (Painter's Algorithm)")
    print("=" * 70)
    print(f"Configuration: {args.config}")
    print(f"Frequency: {args.freq/1e6:.0f} MHz")
    print(f"PVC: {args.pvc:.1f}%")
    print()
    print("Layer structure (by priority - lower drawn first, higher on top):")
    for layer in sorted(layers, key=lambda L: L.priority):
        print(f"  Priority {layer.priority}: {layer.name:15} [{layer.y_min:.2f}–{layer.y_max:.2f}m] {layer.material}")
    print()

    try:
        # Create config
        config = GeneratorConfig.create_physically_perfect(
            rock_packing_algorithm="mbubia",
            center_freq_hz=args.freq,
            antenna_mode="monostatic",
        )

        # Create work order
        params = {"pvc": args.pvc}
        work_order = WorkOrder.from_sampled_params(1, params)
        wos = WorkOrderSystem(work_order)

        # Run pipeline (note: currently MbubiaWorker doesn't use custom layers)
        # To fully support this, would need to modify MbubiaWorker
        print("[1/3] Running scene generator...")
        line = ProductionLine(config)
        checkpoint = line.run(wos)

        # Save .in file
        print("[2/3] Saving gprMax .in file...")
        writer = GPRMaxFileWriter()
        saved_path = writer.save_scene_checkpoint(
            checkpoint,
            output_path=str(output_path),
            scenario_type="Sim",
            config=config,
        )
        print(f"      Generated {checkpoint.rock_count} rocks")
        print(f"      Saved: {saved_path}")

        # Render PNG
        if args.render:
            print("[3/3] Rendering PNG visualization...")
            png_path = output_path.with_suffix(".png")
            scene = parse_in_file(Path(saved_path))
            title = f"Overlapping Layers ({args.config}), {args.freq/1e6:.0f} MHz, PVC={args.pvc:.0f}%"
            fig, ax = render_geometry_figure(scene, title=title)
            save_figure(fig, png_path, dpi=150)
            print(f"      Saved: {png_path}")

        print()
        print("=" * 70)
        print("SUCCESS - Overlapping layers generated")
        print("=" * 70)
        return 0

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

import sys
import argparse
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from src.config import GeneratorConfig
from src.production_line import ProductionLine
from src.work_order import WorkOrder, WorkOrderSystem
from src.file_writer import GPRMaxFileWriter

def main():
    parser = argparse.ArgumentParser(description="Generate a single standalone gprMax .in blueprint.")
    parser.add_argument("--out",      type=Path,  default=Path("standalone_blueprint.in"),
                        help="Output .in file path")
    parser.add_argument("--algo",     type=str,   default="circlify",
                        help="Rock packing algorithm (circlify, front_chain, etc.)")
    parser.add_argument("--psd",      type=str,   default="uniform",
                        choices=["uniform", "en13450", "fuller"],
                        help="Particle size distribution: uniform | en13450 | fuller")
    parser.add_argument("--pvc",      type=float, default=0.0,
                        help="Percentage Voids Contaminated (PVC) 0-100")
    parser.add_argument("--moisture", type=float, default=0.0,
                        help="Moisture content 0.0-1.0")
    parser.add_argument("--granular", action="store_true",
                        help="Enable the new Unified Mission-Based Granular Matrix generation")
    parser.add_argument("--render",   action="store_true",
                        help="Also render a PNG geometry figure after writing the .in file")

    args = parser.parse_args()

    # 1. Setup config
    cfg = GeneratorConfig(
        add_waveform=True,
        add_source=True,
        rock_packing_algorithm=args.algo,
        rock_psd_type=args.psd,
        granular_mode=args.granular,
        pvc_min=args.pvc,
        pvc_max=args.pvc,
        moisture_min=args.moisture,
        moisture_max=args.moisture
    )

    # 2. Setup Production Line
    pipeline = ProductionLine(cfg)

    # 3. Create single work order
    params = {'pvc': args.pvc, 'moisture': args.moisture}
    work_order = WorkOrder.from_sampled_params(1, params)
    wos = WorkOrderSystem(work_order)

    # 4. Generate checkpoint
    print(f"Generating scene | algo={args.algo!r}  psd={args.psd!r}  PVC={args.pvc}%")
    checkpoint = pipeline.run(wos)

    # 5. Validate
    errors = checkpoint.validate_all()
    if errors:
        print("Validation Warnings:")
        for err in errors:
            print(f"  - {err}")

    # 6. Save .in file
    out_path = args.out.resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)

    written_path = GPRMaxFileWriter.save_scene_checkpoint(
        checkpoint,
        output_path=str(out_path),
        scenario_type="Standalone_Blueprint"
    )

    print(f"\nSuccessfully generated: {written_path}")
    print(f"  Rocks Placed : {checkpoint.rock_count}")
    print(f"  Density      : {checkpoint.metadata.get('achieved_density', 0.0):.3f}")

    # 7. Optionally render PNG
    if args.render:
        import matplotlib
        matplotlib.use("Agg")
        from src.visualization.scene import parse_in_file, render_geometry_figure
        png_path = out_path.with_suffix(".png")
        scene = parse_in_file(out_path)
        fig, _ = render_geometry_figure(scene, title=f"{out_path.stem} [{args.psd}]")
        fig.savefig(png_path, dpi=150, bbox_inches="tight")
        print(f"  PNG          : {png_path}")

if __name__ == "__main__":
    main()

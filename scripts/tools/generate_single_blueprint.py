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
    parser.add_argument("--out", type=Path, default=Path("standalone_blueprint.in"), help="Output .in file path")
    parser.add_argument("--algo", type=str, default="circlify", help="Rock packing algorithm (circlify, front_chain, etc.)")
    parser.add_argument("--pvc", type=float, default=0.0, help="Percentage Voids Contaminated (PVC) 0-100")
    parser.add_argument("--moisture", type=float, default=0.0, help="Moisture content 0.0-1.0")
    
    args = parser.parse_args()

    # 1. Setup config
    cfg = GeneratorConfig(
        add_waveform=True,
        add_source=True,
        rock_packing_algorithm=args.algo,
        pvc_min=args.pvc,
        pvc_max=args.pvc,
        moisture_min=args.moisture,
        moisture_max=args.moisture
    )
    
    # 2. Setup Production Line
    pipeline = ProductionLine(cfg)
    
    # 3. Create single work order
    params = {
        'pvc': args.pvc,
        'moisture': args.moisture
    }
    work_order = WorkOrder.from_sampled_params(1, params)
    wos = WorkOrderSystem(work_order)
    
    # 4. Generate checkpoint
    print(f"Generating scene with algorithm '{args.algo}' (PVC={args.pvc}%)...")
    checkpoint = pipeline.run(wos)
    
    # 5. Validate
    errors = checkpoint.validate_all()
    if errors:
        print("Validation Warnings:")
        for err in errors:
            print(f"  - {err}")
            
    # 6. Save using the standard GPRMaxFileWriter (Ensures perfect .in format)
    out_path = args.out.resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    
    written_path = GPRMaxFileWriter.save_scene_checkpoint(
        checkpoint,
        output_path=str(out_path),
        scenario_type="Standalone_Blueprint"
    )
    
    print(f"\nSuccessfully generated standalone blueprint: {written_path}")
    print(f"Rocks Placed: {checkpoint.rock_count}")
    print(f"Density:      {checkpoint.metadata.get('achieved_density', 0.0):.3f}")

if __name__ == "__main__":
    main()

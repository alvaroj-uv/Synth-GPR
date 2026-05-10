import sys
import argparse
import json
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import math

# Add src to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from src.rock_packing import PackingBounds
from src.warehouses import ToolWarehouse
from src.gpr_commands import CylinderCommand

def main():
    parser = argparse.ArgumentParser(description="Standalone script to generate ONLY a bounding box of packed rocks.")
    parser.add_argument("--algo", type=str, default="circlify", help="Packing algorithm (random, poisson, front_chain, circlify, etc.)")
    parser.add_argument("--xmin", type=float, default=0.0)
    parser.add_argument("--xmax", type=float, default=1.0)
    parser.add_argument("--ymin", type=float, default=0.0)
    parser.add_argument("--ymax", type=float, default=0.5)
    parser.add_argument("--rmin", type=float, default=0.02)
    parser.add_argument("--rmax", type=float, default=0.04)
    parser.add_argument("--density", type=float, default=0.6)
    parser.add_argument("--out", type=str, default="standalone_box")
    
    args = parser.parse_args()

    # 1. Setup
    from src.config import GeneratorConfig
    import dataclasses
    
    bounds = PackingBounds(args.xmin, args.xmax, args.ymin, args.ymax)
    cfg = GeneratorConfig()
    cfg = dataclasses.replace(cfg, rock_packing_algorithm=args.algo)
    
    warehouse = ToolWarehouse(cfg)
    strategy = warehouse.get_tool("rock_packer")
    
    print(f"Generating rocks using {strategy.__class__.__name__}...")
    rocks = strategy.generate_rocks(bounds, args.rmin, args.rmax, target_fill_ratio=args.density, max_attempts=500)
    
    # Calculate achieved density
    area_rocks = sum([math.pi * r.radius**2 for r in rocks])
    achieved_density = area_rocks / bounds.area
    print(f"Done! Generated {len(rocks)} rocks with a packing density of {achieved_density:.3f}")
    
    out_stem = Path(args.out)
    out_stem.parent.mkdir(parents=True, exist_ok=True)
    
    # 2. Output JSON
    json_path = out_stem.with_suffix(".json")
    rock_data = [{"x": r.x, "y": r.y, "radius": r.radius} for r in rocks]
    with open(json_path, 'w') as f:
        json.dump({"metadata": {"algo": args.algo, "density": achieved_density}, "rocks": rock_data}, f, indent=2)
        
    # 3. Output .in file (Just the Box)
    in_path = out_stem.with_suffix(".in")
    with open(in_path, 'w') as f:
        f.write(f"#title: Standalone Rock Box ({args.algo})\n")
        f.write(f"#domain: {args.xmax + 0.1} {args.ymax + 0.1} 0.1\n")
        f.write("#dx_dy_dz: 0.002 0.002 0.002\n")
        f.write("#time_window: 10e-9\n\n")
        f.write("#material: 6.0 0.01 1 0 ballast_rock\n\n")
        f.write("## === ROCKS ONLY ===\n")
        for rock in rocks:
            cmd = CylinderCommand(rock.x, rock.y, 0.0, rock.x, rock.y, 0.1, rock.radius, "ballast_rock")
            f.write(cmd.render() + "\n")
            
    # 4. Output PNG
    png_path = out_stem.with_suffix(".png")
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.set_title(f"{args.algo.capitalize()} Box | Density: {achieved_density:.3f}")
    ax.set_xlim(bounds.x_min - 0.05, bounds.x_max + 0.05)
    ax.set_ylim(bounds.y_min - 0.05, bounds.y_max + 0.05)
    ax.set_aspect('equal')
    
    rect = patches.Rectangle((bounds.x_min, bounds.y_min), bounds.width, bounds.height, 
                             linewidth=2, edgecolor='red', facecolor='none', linestyle='--')
    ax.add_patch(rect)
    for rock in rocks:
        circle = patches.Circle((rock.x, rock.y), rock.radius, edgecolor='black', facecolor='slategray', alpha=0.9)
        ax.add_patch(circle)
        
    plt.tight_layout()
    plt.savefig(png_path, dpi=150)
    plt.close()
    
    print(f"-> Saved JSON: {json_path}")
    print(f"-> Saved .in : {in_path}")
    print(f"-> Saved PNG : {png_path}")

if __name__ == "__main__":
    main()

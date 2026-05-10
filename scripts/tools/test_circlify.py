import sys
import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from src.rock_packing import CirclifyPacking, PackingBounds
from src.gpr_commands import CylinderCommand

def main():
    bounds = PackingBounds(0.0, 1.0, 0.0, 0.5)
    r_min = 0.02
    r_max = 0.04
    
    print("Generating rocks using CirclifyPacking...")
    strategy = CirclifyPacking()
    rocks = strategy.generate_rocks(bounds, r_min, r_max, target_fill_ratio=0.75, max_attempts=150)
    
    # Calculate density
    import math
    area_rocks = sum([math.pi * r.radius**2 for r in rocks])
    density = area_rocks / bounds.area
    print(f"Done! Generated {len(rocks)} rocks with a packing density of {density:.3f}")
    
    # 1. Generate PNG
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.set_title(f"CirclifyPacking (A1.0 Heuristic)\nCount: {len(rocks)} | Density: {density:.3f}")
    ax.set_xlim(bounds.x_min - 0.05, bounds.x_max + 0.05)
    ax.set_ylim(bounds.y_min - 0.05, bounds.y_max + 0.05)
    ax.set_aspect('equal')
    
    # Draw Bounds
    rect = patches.Rectangle((bounds.x_min, bounds.y_min), bounds.width, bounds.height, 
                             linewidth=2, edgecolor='red', facecolor='none', linestyle='--')
    ax.add_patch(rect)
    
    # Draw Rocks
    for rock in rocks:
        circle = patches.Circle((rock.x, rock.y), rock.radius, 
                                edgecolor='black', facecolor='slategray', alpha=0.9, linewidth=0.5)
        ax.add_patch(circle)
        
    png_path = os.path.join(os.path.dirname(__file__), "circlify_test.png")
    plt.tight_layout()
    plt.savefig(png_path, dpi=150)
    print(f"-> Saved Image: {png_path}")
    
    # 2. Generate .in file
    in_path = os.path.join(os.path.dirname(__file__), "circlify_test.in")
    
    with open(in_path, 'w') as f:
        f.write("#title: Circlify Packing Test\n")
        f.write("#domain: 1.0 0.5 0.1\n")
        f.write("#dx_dy_dz: 0.002 0.002 0.002\n")
        f.write("#time_window: 10e-9\n\n")
        f.write("#material: 6.0 0.01 1 0 ballast_rock\n\n")
        f.write("## === BALLAST ROCKS ===\n")
        
        for rock in rocks:
            # Create a 3D cylinder for each rock (extruding along Z)
            cmd = CylinderCommand(rock.x, rock.y, 0.0, rock.x, rock.y, 0.1, rock.radius, "ballast_rock")
            f.write(cmd.render() + "\n")
            
    print(f"-> Saved gprMax input: {in_path}")

if __name__ == "__main__":
    main()

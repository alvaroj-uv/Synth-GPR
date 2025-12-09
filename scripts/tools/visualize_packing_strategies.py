
import sys
import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import time
import numpy as np

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from rock_packing import PoissonDiskPacking, FrontChainPacking, PhysicsPacking, TrianglePacking, PackingBounds

def visualize_strategy(ax, strategy, name, bounds, r_min, r_max):
    print(f"Running {name}...")
    start = time.time()
    
    # Run Generation
    # Use reasonable target fill for each
    if "Physics" in name:
        target_fill = 0.85
    elif "Triangle" in name:
        target_fill = 0.0 # Ignored
    else:
        target_fill = 0.75
        
    rocks = strategy.generate_rocks(bounds, r_min, r_max, target_fill_ratio=target_fill, max_attempts=150)
    
    duration = time.time() - start
    
    # Calculate stats
    area_rocks = sum([np.pi * r.radius**2 for r in rocks])
    density = area_rocks / bounds.area
    
    # Plot formatting
    ax.set_title(f"{name}\nDensity: {density:.2f} | Time: {duration:.2f}s | Count: {len(rocks)}")
    ax.set_xlim(bounds.x_min, bounds.x_max)
    ax.set_ylim(bounds.y_min, bounds.y_max)
    ax.set_aspect('equal')
    
    # Draw Bounds
    rect = patches.Rectangle((bounds.x_min, bounds.y_min), 
                             bounds.x_max - bounds.x_min, 
                             bounds.y_max - bounds.y_min, 
                             linewidth=2, edgecolor='black', facecolor='none')
    ax.add_patch(rect)
    
    # Draw Rocks
    for rock in rocks:
        # random color based on radius
        color = plt.cm.viridis((rock.radius - r_min) / (r_max - r_min))
        circle = patches.Circle((rock.x, rock.y), rock.radius, 
                                facecolor=color, edgecolor='black', linewidth=0.5, alpha=0.8)
        ax.add_patch(circle)

def main():
    # Setup
    bounds = PackingBounds(0.0, 1.0, 0.0, 0.5)
    r_min = 0.02
    r_max = 0.04
    
    # Increased to 4 subplots
    fig, axes = plt.subplots(2, 2, figsize=(12, 8))
    axes = axes.flatten()
    
    strategies = [
        (PoissonDiskPacking(), "Poisson Disk"),
        (FrontChainPacking(), "Front-Chain"),
        (PhysicsPacking(), "Physics (Relaxation)"),
        (TrianglePacking(), "Triangle (Mesh)")
    ]
    
    for ax, (strat, name) in zip(axes, strategies):
        visualize_strategy(ax, strat, name, bounds, r_min, r_max)
        
    plt.tight_layout()
    output_path = os.path.join(os.path.dirname(__file__), "packing_comparison.png")
    plt.savefig(output_path, dpi=150)
    print(f"\nVisualization saved to: {output_path}")

if __name__ == "__main__":
    main()

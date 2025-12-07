import argparse
import random
import json
import time
import math
import numpy as np
from pathlib import Path

def generate_rsa_pattern(width, height, r_min, r_max, target_density=0.60, max_attempts=500000):
    """
    Generates a master pattern of non-overlapping circles using Random Sequence Absorption (RSA).
    
    Args:
        width, height: Domain size in meters.
        r_min, r_max: Radius range in meters.
        target_density: Target area fraction (0.0 - 1.0).
        max_attempts: Safety limit for iterations.
        
    Returns:
        List of dicts: [{'x': x, 'y': y, 'r': r}, ...]
    """
    rocks = []
    
    # Grid optimization for collision detection
    # Cell size = max diameter. A point can only collide with rocks in 3x3 neighbor cells.
    cell_size = 2 * r_max
    cols = int(math.ceil(width / cell_size))
    rows = int(math.ceil(height / cell_size))
    grid = [[[] for _ in range(cols)] for _ in range(rows)]
    
    current_area = 0.0
    total_area = width * height
    
    print(f"Generating Master Pattern ({width}x{height}m)...")
    print(f"Grid: {cols}x{rows} cells. Cell size: {cell_size:.4f}m")
    
    start_time = time.time()
    attempts = 0
    consecutive_failures = 0
    max_consecutive_failures = 2000 # Stop if we can't place rocks anymore
    
    while current_area / total_area < target_density and attempts < max_attempts:
        attempts += 1
        
        # 1. Random Candidate
        r = random.uniform(r_min, r_max)
        # Keep away from edges by r to ensure full circles (though we handle wrapping/clipping at runtime usually)
        # For a master texture we want it full, so we can allow some edge overlaps if we treat it as continuous,
        # but simpler to just keep inside for now.
        x = random.uniform(r, width - r)
        y = random.uniform(r, height - r)
        
        # 2. Check Collision
        gx = int(x / cell_size)
        gy = int(y / cell_size)
        
        collision = False
        
        # Check 3x3 neighbors
        for ix in range(max(0, gx-1), min(cols, gx+2)):
            for iy in range(max(0, gy-1), min(rows, gy+2)):
                for neighbor in grid[iy][ix]:
                    nx, ny, nr = neighbor['x'], neighbor['y'], neighbor['r']
                    dist_sq = (x - nx)**2 + (y - ny)**2
                    min_dist = (r + nr)
                    if dist_sq < min_dist**2:
                        collision = True
                        break
                if collision: break
            if collision: break
            
        if not collision:
            # 3. Add Rock
            rock = {'x': x, 'y': y, 'r': r}
            rocks.append(rock)
            grid[gy][gx].append(rock)
            current_area += math.pi * r * r
            consecutive_failures = 0
        else:
            consecutive_failures += 1
            
        if consecutive_failures > max_consecutive_failures:
            print(f"Stopping early: {consecutive_failures} consecutive failures. Saturation reached.")
            break
            
        if attempts % 10000 == 0:
            p = (current_area / total_area) * 100
            print(f"  Attempt {attempts}: Density={p:.2f}%, Rocks={len(rocks)}")

    elapsed = time.time() - start_time
    density = (current_area / total_area) * 100
    print(f"Finished in {elapsed:.2f}s. Final Density: {density:.2f}%. Total Rocks: {len(rocks)}")
    
    return rocks

def main():
    parser = argparse.ArgumentParser(description="Generate Master Ballast Pattern (RSA)")
    parser.add_argument("--width", type=float, default=10.0, help="Domain width (m)")
    parser.add_argument("--height", type=float, default=2.0, help="Domain height (m)")
    parser.add_argument("--r_min", type=float, default=0.02, help="Min radius (m)")
    parser.add_argument("--r_max", type=float, default=0.05, help="Max radius (m)")
    parser.add_argument("--density", type=float, default=0.60, help="Target density (0.0-1.0)")
    parser.add_argument("--output", type=str, default="src/patterns/ballast_master.json", help="Output JSON path")
    
    args = parser.parse_args()
    
    # Ensure output dir exists
    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    
    rocks = generate_rsa_pattern(
        args.width, args.height, 
        args.r_min, args.r_max, 
        args.density
    )
    
    data = {
        "metadata": {
            "width": args.width,
            "height": args.height,
            "r_min": args.r_min,
            "r_max": args.r_max,
            "count": len(rocks),
            "generated_at": time.strftime("%Y-%m-%d %H:%M:%S")
        },
        "rocks": rocks
    }
    
    with open(out_path, 'w') as f:
        json.dump(data, f, indent=2)
        
    print(f"Saved master pattern to {out_path}")

if __name__ == "__main__":
    main()

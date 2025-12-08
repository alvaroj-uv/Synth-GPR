import argparse
import random
import json
import time
import math
from pathlib import Path
import sys
import os

# Add scripts directory to path to import sibling if needed, 
# but for stability I will embrace the RSA logic here directly or refactor later.
# To allow importing generate_master_pattern, we need to mess with sys.path
sys.path.append(os.path.dirname(__file__))

# Try to import RSA generator, otherwise fallback to local copy to avoid import errors
try:
    from generate_master_pattern import generate_rsa_pattern
except ImportError:
    print("Could not import generate_rsa_pattern. Please ensure it is in the same directory.")
    sys.exit(1)

def generate_polygon_from_circle(cx, cy, r, num_vertices_range=(5, 9), roughness=0.2):
    """
    Converts a circle (cx, cy, r) into an irregular polygon.
    
    Args:
        cx, cy: Center coordinates.
        r: Radius of the base circle.
        num_vertices_range: Tuple (min, max) vertices.
        roughness: factor of radius variation (0.0 - 1.0).
        
    Returns:
        List of (x, y) tuples representing vertices.
    """
    num_verts = random.randint(*num_vertices_range)
    vertices = []
    
    # Sort angles to ensure convex-ish / star-shaped (monotonically increasing)
    angles = sorted([random.uniform(0, 2 * math.pi) for _ in range(num_verts)])
    
    # Distribute angles more evenly? 
    # Current method: random angles sorted. 
    # Better method for nicer rocks: evenly spaced + jitter.
    
    angles = []
    base_step = 2 * math.pi / num_verts
    for i in range(num_verts):
        # jitter up to 40% of step
        jitter = random.uniform(-0.4 * base_step, 0.4 * base_step)
        angle = i * base_step + jitter
        angles.append(angle)
        
    for theta in angles:
        # Vary radius per vertex
        # r_var = r * (1 + random.uniform(-roughness, roughness))
        # Ensure we stay somewhat inside the r max to avoid collision violation?
        # Actually RSA checks collision on 'r'. If we extend beyond 'r', we might collide.
        # So we should vary radius *inwards* mostly, or reduce base RSA radius slightly.
        # Let's assume r is the bounding circle, so we vary between 0.7r and 1.0r
        
        r_current = r * random.uniform(1.0 - roughness, 1.0)
        
        vx = cx + r_current * math.cos(theta)
        vy = cy + r_current * math.sin(theta)
        vertices.append((vx, vy))
        
    return vertices

def main():
    parser = argparse.ArgumentParser(description="Generate Irregular Ballast Pattern (Polygons)")
    parser.add_argument("--width", type=float, default=10.0, help="Domain width (m)")
    parser.add_argument("--height", type=float, default=2.0, help="Domain height (m)")
    parser.add_argument("--r_min", type=float, default=0.03, help="Min radius (m)")
    parser.add_argument("--r_max", type=float, default=0.06, help="Max radius (m)")
    parser.add_argument("--density", type=float, default=0.55, help="Target density (0.0-1.0)")
    parser.add_argument("--roughness", type=float, default=0.3, help=" irregular roughness (0-1)")
    parser.add_argument("--output", type=str, default="src/patterns/ballast_irregular_master.json", help="Output JSON path")
    
    args = parser.parse_args()
    
    # Ensure output dir exists
    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    
    print("Generating RSA base circles...")
    # 1. Generate Base Circles
    circles = generate_rsa_pattern(
        args.width, args.height,
        args.r_min, args.r_max,
        target_density=args.density
    )
    
    print(f"post-processing {len(circles)} rocks into polygons...")
    
    # 2. Convert to Polygons
    polygons = []
    for c in circles:
        verts = generate_polygon_from_circle(
            c['x'], c['y'], c['r'], 
            roughness=args.roughness
        )
        polygons.append({
            'center': {'x': c['x'], 'y': c['y']},
            'base_radius': c['r'],
            'vertices': verts
        })
        
    data = {
        "metadata": {
            "type": "irregular_polygon",
            "width": args.width,
            "height": args.height,
            "r_min": args.r_min,
            "r_max": args.r_max,
            "count": len(polygons),
            "generated_at": time.strftime("%Y-%m-%d %H:%M:%S")
        },
        "rocks": polygons
    }
    
    with open(out_path, 'w') as f:
        json.dump(data, f, indent=2)
        
    print(f"Saved irregular pattern to {out_path}")

if __name__ == "__main__":
    main()

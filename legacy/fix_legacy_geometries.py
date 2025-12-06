#!/usr/bin/env python3
"""
Script to update legacy gprMax .in files to the new geometry standards.
Standards:
- Domain X: 0.8m (was 0.5m)
- Domain Y: 1.5m (was 1.3m)
- Subgrade Thickness: 0.20m (was 0.05m)

Transformation Logic:
1. Centering (X-axis):
   - The original content (rocks, antennas) occupied 0.0-0.5m.
   - We calculate an offset dx = (0.8 - 0.5) / 2 = 0.15m.
   - We shift all "local" objects (cylinders, antennas) by +dx.
   - We resize "global" objects (subgrade, formation, free_space boxes) to fill 0.0-0.8m.

2. Lifting (Y-axis):
   - The original subgrade was 0.05m. New is 0.20m.
   - Vertical Shift dy = 0.15m.
   - We shift all valid objects (rocks, antennas, formation layer) up by +dy.
   - Note: Subgrade box grows from [0, 0.05] to [0, 0.20].
   - Formation box shifts from [0.05, 0.15] to [0.20, 0.30].
   - Ballast sits on top of formation (0.30+).

Usage:
    python fix_legacy_geometries.py <directory_of_in_files>
"""

import sys
import re
from pathlib import Path
import argparse

def fmt(val):
    """Format float to reasonable precision."""
    return f"{val:.5g}"

def parse_line(line):
    """Extract command and parts."""
    parts = line.split()
    if not parts:
        return None, []
    cmd = parts[0]
    args = parts[1:]
    return cmd, args

def process_file(filepath, output_dir=None, dry_run=False):
    """Reads a file, applies geometric transforms, writes valid output."""
    path = Path(filepath)
    content = path.read_text(encoding='utf-8')
    lines = content.splitlines()
    
    new_lines = []
    
    # Target Geometry
    TARGET_X = 0.8
    TARGET_Y = 1.5
    TARGET_SUBGRADE = 0.20
    FORMATION_THICKNESS = 0.10 # Assumed constant
    
    # Detected Old Geometry (defaults)
    old_x = 0.5
    old_subgrade = 0.05
    
    # Scan for domain to detect if update is needed
    needs_update = True
    for line in lines:
        if line.startswith("#domain:"):
            parts = line.split()
            if len(parts) >= 4:
                chk_x = float(parts[1])
                chk_y = float(parts[2])
                if abs(chk_x - TARGET_X) < 0.01 and abs(chk_y - TARGET_Y) < 0.01:
                    print(f"Skipping {path.name}: Already updated.")
                    return False

    dx = (TARGET_X - old_x) / 2  # 0.15
    dy_lift = TARGET_SUBGRADE - old_subgrade # 0.15
    
    print(f"Processing {path.name}...")
    print(f"  -> Shifting X by +{dx:.3f} (Centering)")
    print(f"  -> Shifting Y by +{dy_lift:.3f} (Subgrade Lift)")

    for line in lines:
        line_stripped = line.strip()
        
        # Pass through comments (except specific metadata updates?)
        if line_stripped.startswith("##"):
            # Update geometry view comment if present
            if "#geometry_view:" in line:
                 # Reconstruct standard commented geometry view
                 gv = f"## #geometry_view: 0 0 0 {fmt(TARGET_X)} {fmt(TARGET_Y)} 0.005 0.005 0.005 0.005 {path.stem}.vti n"
                 new_lines.append(gv)
                 continue
            new_lines.append(line)
            continue
            
        cmd, args = parse_line(line_stripped)
        
        # 1. Domain
        if cmd == "#domain:":
            # Force new domain
            # args: x y z
            z = args[2] if len(args) > 2 else "0.005"
            new_lines.append(f"#domain: {fmt(TARGET_X)} {fmt(TARGET_Y)} {z}")
            
        # 2. Geometry View
        elif cmd == "#geometry_view:":
             # Reconstruct standard
             new_lines.append(f"#geometry_view: 0 0 0 {fmt(TARGET_X)} {fmt(TARGET_Y)} 0.005 0.005 0.005 0.005 {path.stem}.vti n")

        # 3. Boxes (Layers)
        elif cmd == "#box:":
            # Format: x1 y1 z1 x2 y2 z2 mat
            try:
                x1, y1, z1 = float(args[0]), float(args[1]), float(args[2])
                x2, y2, z2 = float(args[3]), float(args[4]), float(args[5])
                mat = args[6]
                
                # Logic:
                # If it's a global layer (spanning full old width), stretch it.
                is_full_width = (abs(x1 - 0.0) < 0.01 and abs(x2 - old_x) < 0.01)
                
                # Update X
                new_x1, new_x2 = x1, x2
                if is_full_width:
                    new_x1, new_x2 = 0.0, TARGET_X
                else:
                    # It's a localized box? Shift it.
                    new_x1 += dx
                    new_x2 += dx
                    
                # Update Y
                new_y1, new_y2 = y1, y2
                
                if mat == "free_space":
                    # Background -> Full new domain
                     new_y1 = 0.0
                     new_y2 = TARGET_Y
                
                elif mat == "subgrade":
                    # Subgrade -> Grow from bottom
                    new_y1 = 0.0
                    new_y2 = TARGET_SUBGRADE
                    
                elif mat == "formation":
                    # Formation -> Sit on subgrade
                    new_y1 = TARGET_SUBGRADE
                    new_y2 = TARGET_SUBGRADE + FORMATION_THICKNESS
                    
                else:
                    # Rocks, Ballast, etc. -> Shift up
                    # Check if it was sitting on old formation (0.15)
                    # Simple shift implies:
                    if y1 > 0.01: new_y1 += dy_lift
                    if y2 > 0.01: new_y2 += dy_lift
                
                new_lines.append(f"#box: {fmt(new_x1)} {fmt(new_y1)} {fmt(z1)} {fmt(new_x2)} {fmt(new_y2)} {fmt(z2)} {mat}")
                
            except ValueError:
                new_lines.append(line)
        
        # 4. Cylinders (Rocks)
        elif cmd == "#cylinder:":
            # x y z x y z r mat
             try:
                c_x, c_y, c_z = float(args[0]), float(args[1]), float(args[2])
                # args[3], args[4], args[5] are end coords (usually same for 2D cylinder along Z)
                rad = float(args[6])
                mat = args[7]
                
                # Shift Center
                new_x = c_x + dx
                new_y = c_y + dy_lift
                
                new_lines.append(f"#cylinder: {fmt(new_x)} {fmt(new_y)} {c_z} {fmt(new_x)} {fmt(new_y)} {args[5]} {rad} {mat}")

             except ValueError:
                new_lines.append(line)
                
        # 5. Hertzian Dipole / RX
        elif cmd == "#hertzian_dipole:":
            # z x y z src
            try:
                x = float(args[1])
                y = float(args[2])
                new_x = x + dx
                new_y = y + dy_lift
                
                # Validate bounds
                if new_x > TARGET_X or new_x < 0:
                    print(f"  WARNING: Transformed TX X={new_x} out of bounds!")
                
                new_lines.append(f"#hertzian_dipole: {args[0]} {fmt(new_x)} {fmt(new_y)} {args[3]} {args[4]}")
                
            except ValueError:
                 new_lines.append(line)
                 
        elif cmd == "#rx:":
             # x y z
             try:
                x = float(args[0])
                y = float(args[1])
                new_x = x + dx
                new_y = y + dy_lift
                
                new_lines.append(f"#rx: {fmt(new_x)} {fmt(new_y)} {args[2]}")
             except ValueError:
                 new_lines.append(line)
                 
        else:
            new_lines.append(line)
            
    # Write output
    if not dry_run:
        out_path = path if output_dir is None else Path(output_dir) / path.name
        out_path.write_text('\n'.join(new_lines), encoding='utf-8')
        
    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Update legacy .in files to new geometry.")
    parser.add_argument("input_dir", help="Directory containing .in files")
    parser.add_argument("--output_dir", help="Optional output directory (overwrites inplace if omitted)")
    
    args = parser.parse_args()
    
    inputs = list(Path(args.input_dir).glob("*.in"))
    print(f"Found {len(inputs)} input files.")
    
    count = 0
    for p in inputs:
        if process_file(p, args.output_dir):
            count += 1
            
    print(f"Updated {count} files.")

#!/usr/bin/env python3
"""
3D render of voxel rock geometry — from a rocks-only #geometry_objects_read
HDF5 array OR a full gprMax geometry .vti (thresholded to one material).

Complements unified_visualizer.py (which is 2-D matplotlib); 3-D VTK/pyvista
voxel rendering is a distinct concern, so it lives as its own tool alongside
the other specialised visualisation scripts.

Inputs:
  *.h5   — int16 array from src.rock_voxelizer.write_geometry_hdf5
           (-1 background, >=0 = rock cells). Rendered directly.
  *.vti  — gprMax GeometryView output. Thresholded to the material whose name
           contains --material (default "granite"; matches the namespaced
           "granite{...}" that #geometry_objects_read produces).

Examples:
  python scripts/visualization/render_voxel_rocks_3d.py \
      experiments/2026-07-01/rock_shape_ab/shape_polyhedron_rocks.h5

  python scripts/visualization/render_voxel_rocks_3d.py \
      experiments/2026-07-01/rock_shape_ab/shape_polyhedron.vti \
      --material granite --slab 0.10 --edges -o poly.png

Requires: pyvista (pip install pyvista). Renders offscreen -> PNG.
"""
import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import numpy as np


def _grid_from_h5(path: Path, dx: float):
    """rocks-only int16 array -> pyvista ImageData with a boolean 'rock' cell mask."""
    import h5py
    import pyvista as pv
    with h5py.File(path) as f:
        data = f["data"][:]
        if "dx_dy_dz" in f.attrs:            # honour the array's own spacing
            dx = float(f.attrs["dx_dy_dz"][0])
    grid = pv.ImageData()
    grid.dimensions = np.array(data.shape) + 1        # cell data => +1 point dims
    grid.spacing = (dx, dx, dx)
    grid.cell_data["rock"] = (data.flatten(order="F") >= 0).astype(np.uint8)
    n = int((data >= 0).sum())
    print(f"[h5] {data.shape} cells, {n} rock cells, phi={n/data.size:.3f}, dx={dx}")
    return grid.threshold(0.5, scalars="rock")


def _grid_from_vti(path: Path, material: str):
    """gprMax GeometryView .vti -> ImageData thresholded to the material(s)
    whose name contains `material` (case-insensitive substring)."""
    import pyvista as pv
    # Map material name -> integer id from the XML <Material> tags gprMax appends.
    with open(path, "rb") as f:
        f.seek(-40000, 2)
        tail = f.read().decode("latin-1")
    ids = {int(m.group(2)): m.group(1)
           for m in re.finditer(r'<Material name="([^"]+)">(\d+)</Material>', tail)}
    want = sorted(i for i, nm in ids.items() if material.lower() in nm.lower())
    if not want:
        raise SystemExit(f"no material matching '{material}' in {path.name}; "
                         f"available: {sorted(set(ids.values()))}")
    print(f"[vti] material '{material}' -> ids {want} "
          f"({', '.join(ids[i] for i in want)})")
    grid = pv.read(str(path))
    arr_name = grid.cell_data.keys()[0] if grid.cell_data else "Material"
    mat = grid.cell_data[arr_name]
    grid.cell_data["sel"] = np.isin(mat, want).astype(np.uint8)
    return grid.threshold(0.5, scalars="sel")


def render(input_path: Path, output: Path, material: str = "granite",
           dx: float = 0.002, slab: float = None, edges: bool = False,
           azimuth: float = 30.0, elevation: float = 20.0,
           color: str = "#7d7266", window=(1500, 1200)) -> Path:
    import pyvista as pv
    pv.OFF_SCREEN = True

    ip = Path(input_path)
    if ip.suffix == ".h5":
        rocks = _grid_from_h5(ip, dx)
    elif ip.suffix == ".vti":
        rocks = _grid_from_vti(ip, material)
    else:
        raise SystemExit(f"unsupported input {ip.suffix}; use .h5 or .vti")

    if slab:                                   # thin cross-track slab for legibility
        b = rocks.bounds
        rocks = rocks.clip_box([b[0], b[1], b[2], b[2] + slab, b[4], b[5]],
                               invert=False)

    p = pv.Plotter(off_screen=True, window_size=window)
    p.add_mesh(rocks, color=color, smooth_shading=not edges, show_edges=edges,
               edge_color="#3a332c", line_width=1,
               specular=0.4, specular_power=20, ambient=0.25)
    p.add_axes(line_width=3)
    p.camera_position = "xz"
    p.camera.azimuth = azimuth
    p.camera.elevation = elevation
    p.add_text(ip.stem, font_size=11)
    p.set_background("white")
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    p.screenshot(str(output))
    print(f"saved {output}")
    return output


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("input", type=Path, help="rocks .h5 or gprMax geometry .vti")
    ap.add_argument("-o", "--output", type=Path, default=None,
                    help="output PNG (default: <input stem>_3d.png beside input)")
    ap.add_argument("--material", default="granite",
                    help="material name substring to threshold in a .vti (default granite)")
    ap.add_argument("--dx", type=float, default=0.002,
                    help="cell size for .h5 without a dx_dy_dz attr (default 0.002)")
    ap.add_argument("--slab", type=float, default=None, metavar="M",
                    help="clip to a cross-track slab of this thickness (m) for legibility")
    ap.add_argument("--edges", action="store_true", help="draw voxel edges")
    ap.add_argument("--azimuth", type=float, default=30.0)
    ap.add_argument("--elevation", type=float, default=20.0)
    args = ap.parse_args()

    out = args.output or args.input.with_name(args.input.stem + "_3d.png")
    render(args.input, out, material=args.material, dx=args.dx,
           slab=args.slab, edges=args.edges,
           azimuth=args.azimuth, elevation=args.elevation)


if __name__ == "__main__":
    main()

"""
Voxelise packed rocks into a gprMax #geometry_objects_read HDF5 array.

Pipeline position: sits between the sphere packers (sphere_packing_3d /
rcpgenerator, unchanged) and the deck writer. Each packed sphere is replaced
in-place by a shape inscribed in its bounding sphere, so the packing's
non-overlap guarantee and virtual-sieve grading survive any shape swap.

    pack_spheres() -> [PackedSphere]                      (unchanged)
        |
    voxelize_rocks(rocks, shape_fn, ...) -> int16 array   (-1 = transparent)
        |
    write_geometry_hdf5(rocks.h5) + write_materials_file(rock_materials.txt)
        |
    deck: #geometry_objects_read: x0 y0 z0 rocks.h5 rock_materials.txt

gprMax contract (verified against gprMax input_cmds_geometry.py sources):
  - HDF5 root dataset ``data``, np.int16, shape (nx, ny, nz)
  - root attribute ``dx_dy_dz`` = (dx, dy, dz) floats, must equal model grid
  - -1 cells keep whatever material is already built (painter's algorithm)
  - value v >= 0 selects the (v+1)-th #material line of the materials file
  - imported materials are namespaced ``name{filestem}`` by gprMax, so they
    never clash with same-named materials in the main deck
  - both files are resolved against CWD then the input-file directory: emit
    BARE filenames and place both files next to the .in deck (same rule as
    #excitation_file on Windows drive-letter paths)

Bit-parity with #sphere (control case): gprMax build_sphere snaps the centre
to a cell index xc = round(x/dx) and keeps cells whose CENTRE (i+0.5)*dx lies
within r. sphere_shape() reproduces exactly that, so a voxelised sphere scene
must match a native #sphere scene cell-for-cell.
"""
from __future__ import annotations

from pathlib import Path
from typing import Callable, List, Sequence

import numpy as np

from .gpr_commands import MaterialCommand
from .sphere_packing_3d import PackedSphere

# Shape function contract: (px, py, pz, cx, cy, cz, r, idx) -> bool mask.
# px/py/pz are absolute cell-centre coordinate arrays (broadcastable), cx/cy/cz
# the rock centre snapped to a cell corner, r the bounding-sphere radius, idx
# the rock's index in the packing (for per-rock reproducible shape params).
# The returned mask MUST stay inside the bounding sphere ||p-c|| <= r, so the
# packer's non-overlap guarantee holds for any shape.
ShapeFn = Callable[..., np.ndarray]


def sphere_shape(px, py, pz, cx, cy, cz, r, idx) -> np.ndarray:
    """Exact replica of gprMax build_sphere's cell test (control case)."""
    return (px - cx) ** 2 + (py - cy) ** 2 + (pz - cz) ** 2 <= r ** 2


def make_scaled_sphere_shape(scale: float) -> ShapeFn:
    """Sphere shrunk to scale*r — volume-matched control for shape A/Bs.

    scale=0.745 matches the ~0.41 volume ratio of the default ellipsoid and
    polyhedron shapes, isolating pure shape (vs granite volume) effects.
    """
    def shape(px, py, pz, cx, cy, cz, r, idx):
        return sphere_shape(px, py, pz, cx, cy, cz, r * scale, idx)
    return shape


def make_ellipsoid_shape(seed: int = 42,
                         aspect_b: tuple = (0.60, 0.85),
                         aspect_c: tuple = (0.45, 0.70)) -> ShapeFn:
    """Randomly-oriented triaxial ellipsoid inscribed in the bounding sphere.

    Semi-axes (r, b*r, c*r) with b, c drawn per-rock from the given ranges —
    defaults approximate EN 933 flakiness/elongation of crushed ballast
    (~1 : 0.7 : 0.5). Orientation is a uniform random rotation per rock,
    reproducible from (seed, idx) so matched-pair A/B scenes reuse shapes.
    """
    def shape(px, py, pz, cx, cy, cz, r, idx):
        rng = np.random.default_rng((seed, idx))
        b = rng.uniform(*aspect_b)
        c = rng.uniform(*aspect_c)
        # Uniform random rotation via QR of a Gaussian matrix
        q, rr = np.linalg.qr(rng.normal(size=(3, 3)))
        q *= np.sign(np.diag(rr))
        d = np.stack(np.broadcast_arrays(px - cx, py - cy, pz - cz), axis=-1)
        local = d @ q  # rotate into ellipsoid frame
        return (local[..., 0] / r) ** 2 + (local[..., 1] / (b * r)) ** 2 \
             + (local[..., 2] / (c * r)) ** 2 <= 1.0
    return shape


def make_polyhedron_shape(seed: int = 42,
                          n_points: tuple = (10, 18)) -> ShapeFn:
    """Angular convex polyhedron: hull of random points on the bounding sphere.

    The 3D analogue of the 2D RIP #triangle stones — flat faces and sharp
    edges like crushed granite. Per-rock vertex count drawn from n_points;
    everything reproducible from (seed, idx). Inscribed in the bounding
    sphere by construction (hull of points ON the sphere). Volume ratio vs
    the sphere is ~0.42 mean (0.15–0.59) for 10–18 vertices — nearly the
    same as make_ellipsoid_shape's defaults (~0.42), so ellipsoid vs
    polyhedron on one packing is a volume-matched angularity comparison,
    while either-vs-sphere confounds shape with granite volume fraction.
    """
    from scipy.spatial import ConvexHull

    def shape(px, py, pz, cx, cy, cz, r, idx):
        rng = np.random.default_rng((seed, idx))
        n = int(rng.integers(n_points[0], n_points[1] + 1))
        v = rng.normal(size=(n, 3))
        v *= r / np.linalg.norm(v, axis=1, keepdims=True)
        eqs = ConvexHull(v).equations          # (nfaces, 4): n·x + d <= 0 inside
        d = np.stack(np.broadcast_arrays(px - cx, py - cy, pz - cz), axis=-1)
        return (d @ eqs[:, :3].T + eqs[:, 3] <= 0.0).all(axis=-1)
    return shape


def voxelize_rocks(
    rocks: Sequence[tuple],
    origin: tuple,
    size_cells: tuple,
    dx: float,
    shape_fn: ShapeFn = sphere_shape,
    material_index: int = 0,
) -> np.ndarray:
    """Rasterise rocks into an int16 label array for #geometry_objects_read.

    Args:
        rocks:      iterable of (cx, cy, cz, r) in gprMax DOMAIN coordinates
                    (caller does any packing-axis swap, as with SphereCommand).
        origin:     (x0, y0, z0) domain coordinate of the array's lower-left
                    corner — pass the same values to GeometryObjectsReadCommand.
                    Snapped to the grid internally (gprMax rounds it anyway).
        size_cells: (nx, ny, nz) array dimensions.
        dx:         grid spacing (cubic cells, matching #dx_dy_dz).
        shape_fn:   per-rock inside/outside test (default: exact #sphere).
        material_index: value written for rock cells (row of materials file).

    Returns:
        np.int16 array (nx, ny, nz): -1 background, material_index inside rocks.
    """
    nx, ny, nz = size_cells
    data = np.full((nx, ny, nz), -1, dtype=np.int16)
    # Array origin in whole cells (gprMax: xs = round(x/dx))
    ox, oy, oz = (int(round(v / dx)) for v in origin)

    for idx, (cx, cy, cz, r) in enumerate(rocks):
        # Snap centre to a cell corner exactly like gprMax build_sphere
        cxs, cys, czs = (round(v / dx) * dx for v in (cx, cy, cz))
        # Bounding box in array-local cells (superset; shape_fn decides)
        is_ = max(int(round((cxs - r) / dx)) - 1 - ox, 0)
        if_ = min(int(round((cxs + r) / dx)) + 1 - ox, nx)
        js_ = max(int(round((cys - r) / dx)) - 1 - oy, 0)
        jf_ = min(int(round((cys + r) / dx)) + 1 - oy, ny)
        ks_ = max(int(round((czs - r) / dx)) - 1 - oz, 0)
        kf_ = min(int(round((czs + r) / dx)) + 1 - oz, nz)
        if is_ >= if_ or js_ >= jf_ or ks_ >= kf_:
            continue  # rock entirely outside the array

        # Absolute cell-centre coordinates of the local bounding box
        px = ((np.arange(is_, if_) + ox) + 0.5)[:, None, None] * dx
        py = ((np.arange(js_, jf_) + oy) + 0.5)[None, :, None] * dx
        pz = ((np.arange(ks_, kf_) + oz) + 0.5)[None, None, :] * dx

        mask = shape_fn(px, py, pz, cxs, cys, czs, r, idx)
        sub = data[is_:if_, js_:jf_, ks_:kf_]
        sub[mask] = material_index

    return data


def write_geometry_hdf5(path: Path, data: np.ndarray, dx: float) -> None:
    """Write the label array in the exact format #geometry_objects_read expects."""
    import h5py
    with h5py.File(path, "w") as f:
        f.attrs["dx_dy_dz"] = (dx, dx, dx)
        f.create_dataset("data", data=data.astype(np.int16))


def write_materials_file(path: Path, materials: List[MaterialCommand]) -> None:
    """Write #material lines; row order defines the array's integer mapping."""
    lines = [m.get_cmd_string() for m in materials]
    Path(path).write_text("\n".join(lines) + "\n", encoding="utf-8")


def spheres_to_domain_coords(spheres: Sequence[PackedSphere]) -> List[tuple]:
    """Map PackedSphere packing axes to gprMax domain axes.

    The 3D pipeline packs with axis 1 = vertical: PackedSphere.y is gprMax Z
    and PackedSphere.z is gprMax Y (see generate_3d_scene.inflation_spheres),
    the same swap SphereCommand emission does.
    """
    return [(s.x, s.z, s.y, s.r) for s in spheres]

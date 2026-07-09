"""
Grid-resolution control for the shape-invisibility result (rock_shape_ab).

Question: is "shape is invisible at 420 MHz" an artifact of the dx=2mm grid?
Test: identical compact scene, ONE shared packing, volume-matched sphere-small
vs polyhedron, voxelised and run at BOTH dx=2mm and dx=1mm. If the
sphere-vs-polyhedron coda correlation stays ~1.0 at both resolutions, the
shape invisibility is physical (Rayleigh regime, set by wavelength), not a
staircasing/resolution artifact.

Compact domain + Hertzian dipole (not the full GSSI antenna): for a RELATIVE
shape A/B the source and domain cancel, and this fits the 6 GB GPU at 1mm
(full 0.5x0.5x0.8 m at 1mm = 200M cells does not). Writes 4 decks:
{sphere-small, polyhedron} x {2mm, 1mm}, all on the same packing.
"""
import sys
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO))

from src.constants import MC
from src.gpr_commands import MaterialCommand
from src.rock_voxelizer import (
    make_polyhedron_shape, make_scaled_sphere_shape,
    spheres_to_domain_coords, voxelize_rocks,
    write_geometry_hdf5, write_materials_file,
)
from src.sphere_packing_3d import PackingBounds3D, pack_spheres

HERE = Path(__file__).parent

# ── Compact scene geometry (metres) ──────────────────────────────────────────
DOM_X = DOM_Y = 0.30
DOM_Z = 0.40
SUBGRADE_TOP = 0.12         # subgrade 0..0.12
BALLAST_TOP  = 0.32         # ballast 0.12..0.32 (0.20 m), air above
STANDOFF_Z   = 0.35         # dipole 3 cm above surface
TIME_WINDOW  = 18e-9
FREQ         = 420e6

# Materials (single source of truth): void fill + granite grains + subgrade
VOID_EPS, VOID_SIG = 4.5, 0.001
GRANITE_EPS, GRANITE_SIG = MC.CRIM_ROCK_EPS, 0.001   # 6.1
SUBGRADE_EPS, SUBGRADE_SIG = 10.0, 0.010

# ── Pack ONCE (shared across all 4 decks) ────────────────────────────────────
def make_packing():
    bounds = PackingBounds3D(
        x_min=0.05, x_max=0.25,               # gpr X (lateral), margin for PML+r
        y_min=0.15, y_max=0.29,               # packing axis 1 -> gpr Z (vertical)
        z_min=0.05, z_max=0.25,               # gpr Y (lateral)
    )
    spheres = pack_spheres(bounds, r_min=0.019, r_max=0.030,
                           target_phi=0.35, seed=42)
    print(f"[pack] {len(spheres)} spheres")
    return spheres


def write_deck(spheres, shape_key, dx):
    """Voxelise the shared packing with the given shape at dx, write h5 +
    materials + a dipole deck. Returns the .in path."""
    shape_fn = {"sphere_small": make_scaled_sphere_shape(0.745),
                "polyhedron":   make_polyhedron_shape(seed=42)}[shape_key]
    tag = f"{shape_key}_dx{int(dx*1000)}mm"

    nx, ny = int(round(DOM_X / dx)), int(round(DOM_Y / dx))
    nz = int(round((BALLAST_TOP - SUBGRADE_TOP) / dx))
    data = voxelize_rocks(spheres_to_domain_coords(spheres),
                          origin=(0.0, 0.0, SUBGRADE_TOP),
                          size_cells=(nx, ny, nz), dx=dx, shape_fn=shape_fn)
    n_rock = int((data >= 0).sum())
    h5 = HERE / f"{tag}_rocks.h5"
    mat = HERE / f"{tag}_materials.txt"
    write_geometry_hdf5(h5, data, dx)
    write_materials_file(mat, [MaterialCommand(GRANITE_EPS, GRANITE_SIG, 1.0, 0.0, "granite")])

    def f(v): return f"{v:.5f}"
    cx = cy = DOM_X / 2
    lines = [
        f"## shape-dx verification: {tag}  (phi_slab={n_rock/data.size:.3f})",
        f"#domain: {DOM_X} {DOM_Y} {DOM_Z}",
        f"#dx_dy_dz: {dx} {dx} {dx}",
        f"#time_window: {TIME_WINDOW:g}",
        "",
        f"#material: {SUBGRADE_EPS} {SUBGRADE_SIG} 1.0 0.0 subgrade",
        f"#material: {VOID_EPS} {VOID_SIG} 1.0 0.0 void",
        "",
        f"#waveform: ricker 1 {FREQ:g} rick",
        f"#hertzian_dipole: y {f(cx)} {f(cy)} {f(STANDOFF_Z)} rick",
        f"#rx: {f(cx + 0.02)} {f(cy)} {f(STANDOFF_Z)}",
        "",
        f"#box: 0 0 0 {DOM_X} {DOM_Y} {SUBGRADE_TOP} subgrade",
        f"#box: 0 0 {SUBGRADE_TOP} {DOM_X} {DOM_Y} {BALLAST_TOP} void",
        f"#geometry_objects_read: 0 0 {SUBGRADE_TOP} {h5.name} {mat.name}",
        "",
        "#messages: n",
    ]
    inp = HERE / f"{tag}.in"
    inp.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"[deck] {inp.name}  ({nx}x{ny}x{nz} array, {n_rock} rock cells)")
    return inp


def main():
    spheres = make_packing()
    np.savetxt(HERE / "packing.csv",
               [(s.x, s.y, s.z, s.r) for s in spheres],
               delimiter=",", header="x,y,z,r", comments="")
    for dx in (0.002, 0.001):
        for shape in ("sphere_small", "polyhedron"):
            write_deck(spheres, shape, dx)
    print("\nnext: run the 4 .in files, then compare_dx.py")


if __name__ == "__main__":
    main()

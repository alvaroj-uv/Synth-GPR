"""
Tests for src/rock_voxelizer.py — the #geometry_objects_read voxel-rock path.

The bit-parity test against gprMax's build_sphere is the load-bearing one: the
voxel pipeline's validation (experiments/2026-07-01/voxel_rock_control, A-scan
bit-identical to native #sphere) rests on sphere_shape replicating gprMax's
cell test exactly. If sphere_shape or the bounding-box arithmetic drifts, this
test fails before an expensive FDTD comparison would.
"""

# Third-party imports
import numpy as np
import pytest

# Local imports
from src.gpr_commands import MaterialCommand
from src.rock_voxelizer import (
    make_ellipsoid_shape,
    make_polyhedron_shape,
    make_scaled_sphere_shape,
    sphere_shape,
    voxelize_rocks,
    write_geometry_hdf5,
    write_materials_file,
)

DX = 0.002


def gprmax_build_sphere(xc, yc, zc, r, dx, shape):
    """Direct port of gprMax geometry_primitives_ext.pyx build_sphere loop
    (v3.1.7): centre snapped to cell index, keep cells whose CENTRE lies
    within r."""
    solid = np.zeros(shape, dtype=bool)
    xs = max(int(round((xc * dx - r) / dx)) - 1, 0)
    xf = min(int(round((xc * dx + r) / dx)) + 1, shape[0])
    ys = max(int(round((yc * dx - r) / dx)) - 1, 0)
    yf = min(int(round((yc * dx + r) / dx)) + 1, shape[1])
    zs = max(int(round((zc * dx - r) / dx)) - 1, 0)
    zf = min(int(round((zc * dx + r) / dx)) + 1, shape[2])
    for i in range(xs, xf):
        for j in range(ys, yf):
            for k in range(zs, zf):
                if np.sqrt((i + 0.5 - xc) ** 2 * dx ** 2
                           + (j + 0.5 - yc) ** 2 * dx ** 2
                           + (k + 0.5 - zc) ** 2 * dx ** 2) <= r:
                    solid[i, j, k] = True
    return solid


class TestSphereParity:
    def test_bit_parity_with_gprmax_build_sphere(self):
        """sphere_shape must match gprMax's rasterisation cell-for-cell."""
        rng = np.random.default_rng(7)
        mismatches = 0
        for _ in range(20):
            r = rng.uniform(0.010, 0.033)
            cx, cy, cz = (rng.uniform(0.05, 0.15) for _ in range(3))
            ref = gprmax_build_sphere(round(cx / DX), round(cy / DX),
                                      round(cz / DX), r, DX, (100, 100, 100))
            got = voxelize_rocks([(cx, cy, cz, r)], origin=(0, 0, 0),
                                 size_cells=(100, 100, 100), dx=DX) >= 0
            mismatches += int((ref != got).sum())
        assert mismatches == 0

    def test_sphere_volume_close_to_analytic(self):
        r = 0.025  # 12.5 cells
        data = voxelize_rocks([(0.1, 0.1, 0.1, r)], origin=(0, 0, 0),
                              size_cells=(100, 100, 100), dx=DX)
        vol_vox = (data >= 0).sum() * DX ** 3
        vol_ana = 4 / 3 * np.pi * r ** 3
        assert abs(vol_vox - vol_ana) / vol_ana < 0.05

    def test_origin_offset_consistency(self):
        """An array with a shifted origin must hold the same voxels as the
        corresponding slab of a zero-origin array (guards the f1/f2/f3
        placement arithmetic of #geometry_objects_read)."""
        r = 0.025
        off = voxelize_rocks([(0.1, 0.1, 0.2, r)], origin=(0, 0, 0.150),
                             size_cells=(100, 100, 100), dx=DX)
        full = voxelize_rocks([(0.1, 0.1, 0.2, r)], origin=(0, 0, 0),
                              size_cells=(100, 100, 200), dx=DX)
        assert (off == full[:, :, 75:175]).all()


class TestShapes:
    """Every shape must stay inside its bounding sphere — that contract is
    what lets shapes swap in-place without re-checking packing overlaps."""

    @pytest.mark.parametrize("factory", [
        lambda: make_ellipsoid_shape(seed=42),
        lambda: make_polyhedron_shape(seed=42),
        lambda: make_scaled_sphere_shape(0.745),
    ])
    def test_inscribed_in_bounding_sphere(self, factory):
        r = 0.025
        sph = voxelize_rocks([(0.1, 0.1, 0.1, r)], origin=(0, 0, 0),
                             size_cells=(100, 100, 100), dx=DX) >= 0
        shp = voxelize_rocks([(0.1, 0.1, 0.1, r)], origin=(0, 0, 0),
                             size_cells=(100, 100, 100), dx=DX,
                             shape_fn=factory()) >= 0
        assert not (shp & ~sph).any()
        assert 0.1 < shp.sum() / sph.sum() < 1.0

    def test_shapes_reproducible_from_seed(self):
        r = 0.025
        a = voxelize_rocks([(0.1, 0.1, 0.1, r)], origin=(0, 0, 0),
                           size_cells=(100, 100, 100), dx=DX,
                           shape_fn=make_ellipsoid_shape(seed=42))
        b = voxelize_rocks([(0.1, 0.1, 0.1, r)], origin=(0, 0, 0),
                           size_cells=(100, 100, 100), dx=DX,
                           shape_fn=make_ellipsoid_shape(seed=42))
        assert (a == b).all()


class TestWriters:
    def test_hdf5_round_trip(self, tmp_path):
        h5py = pytest.importorskip("h5py")
        data = voxelize_rocks([(0.1, 0.1, 0.1, 0.025)], origin=(0, 0, 0),
                              size_cells=(60, 60, 60), dx=DX)
        p = tmp_path / "rocks.h5"
        write_geometry_hdf5(p, data, DX)
        with h5py.File(p) as f:
            assert f["data"].dtype == np.int16          # -1 must be representable
            assert tuple(np.round(f.attrs["dx_dy_dz"], 9)) == (DX, DX, DX)
            assert (f["data"][:] == data).all()

    def test_materials_file_row_order(self, tmp_path):
        p = tmp_path / "mats.txt"
        write_materials_file(p, [MaterialCommand(6.1, 0.001, 1.0, 0.0, "granite")])
        assert p.read_text(encoding="utf-8").splitlines()[0] \
            == "#material: 6.1 0.001 1 0.0 granite"

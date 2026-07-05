# Voxel Rock Pipeline — Sphere Control Validation

**Date:** 2026-07-01
**Goal:** Validate the new `#geometry_objects_read` voxel-rock path against the
native `#sphere` path before using it for realistic rock shapes (ellipsoids,
spherical harmonics). If the voxel writer, coordinate origin, and axis order
are correct, a voxelised sphere scene must reproduce the native sphere scene
exactly — same built geometry, same A-scan.

## Why this exists

To model realistic (non-spherical) ballast rocks in 3D, arbitrary shapes must
be imported as an int16 voxel array via `#geometry_objects_read` (gprMax has
no ellipsoid/polyhedron primitive). The architecture keeps the sphere packing
untouched and swaps each sphere in-place for a shape inscribed in its bounding
sphere, so non-overlap and virtual-sieve grading survive any shape change.
New infrastructure validated here:

- `src/rock_voxelizer.py` — rasterises packed rocks into the gprMax HDF5
  format (`data` int16, `dx_dy_dz` attr, −1 = transparent); `sphere_shape`
  replicates gprMax `build_sphere`'s cell test exactly; `make_ellipsoid_shape`
  is the first realistic-shape hook (EN 933-like aspect ratios).
- `GeometryObjectsReadCommand` in `src/gpr_commands.py`.
- `--rock-shape {sphere, voxel-sphere, voxel-ellipsoid}` and `--sphere-file`
  in `scripts/pipeline/generate_3d_scene.py`.

## Critical finding along the way

**rcpgenerator is NOT deterministic across runs even with a fixed seed** —
two consecutive runs with seed 42 produced different packings (first attempt:
2.3 M mismatched cells between the "identical" decks). Any matched-pair A/B
with this packer must share one packing via `--sphere-file` (CSV saved on
first run, reloaded verbatim on later runs — 3D analogue of the 2D
rock-library / `rock_source_file` pattern).

## Scene

Standard 3D GSSI-400 scene (0.50 × 0.50 × 0.80 m, dx = 2 mm, 25 M cells,
30 ns): subgrade eps 10 (0–0.15 m), ballast 0.15–0.50 m as 233 granite rocks
(eps 6.1, r 19–32 mm, φ 0.38 in packing zone) in void fill eps 4.5 /
σ 0.001 (eps_eff ≈ 5.1 clean), 5 cm standoff, GSSI 400 MHz antenna.

Both decks share `packing_seed42.csv`:

```
generate_3d_scene.py --rocks --void-eps 4.5 --void-sigma 0.001 \
    --sphere-file packing_seed42.csv --out ctrl_sphere_native.in
generate_3d_scene.py --rocks --void-eps 4.5 --void-sigma 0.001 \
    --rock-shape voxel-sphere --sphere-file packing_seed42.csv \
    --out ctrl_sphere_voxel.in
```

## Results

**Geometry (from .vti, cell-by-cell over all 25 M cells): BIT-IDENTICAL.**
All 2,063,702 rock cells match; the only difference is the material label
(`granite` vs gprMax's namespaced `granite{ctrl_sphere_voxel_rock_materials}`,
identical eps/sigma). Zero cells differ otherwise.

**A-scan (Ey = GSSI co-pol component, rx1, 7790 samples, dt = 3.85 ps).**
The GSSI-400 antenna is y-polarised, so Ey (peak 5.5 V/m) is the received
signal in the 3D scene — NOT Ez (cross-pol, 2.2 V/m) as in the 2D pipeline.

| Pair | max residual | RMS residual | r | bit-identical |
|---|---|---|---|---|
| native no-smooth vs **voxel** | **0.0000 %** | 0.0000 % | 1.000000000 | **YES** |
| native smoothed vs voxel | 7.31 % of peak | 1.18 % | 0.998732 | no |
| native smoothed vs native no-smooth | 7.31 % of peak | 1.18 % | 0.998732 | no |

(Ez gives the same verdict: bit-identical for no-smooth vs voxel; 6.27 % /
1.02 % / r = 0.998995 against the smoothed deck.)

**Verdict: the voxel path is exactly validated.** With dielectric smoothing
disabled on the native spheres (`#sphere: ... granite n`), the voxel deck's
A-scan is bit-identical to the native one on every field component. The
entire residual between the default deck and the voxel deck is dielectric
smoothing — gprMax never smooths imported voxel geometry (hard-coded
`averaging=False`), while native volumetric objects smooth rock/void
interface cells by default. The residual is concentrated at 8–10 ns (ballast
coda), exactly where rock interfaces matter (see `ascan_overlay.png`).

**Methodological consequence:** future shape A/Bs (sphere vs ellipsoid vs
harmonic) must compare voxel-vs-voxel, or native-with-`--sphere-smoothing n`
vs voxel — never default-native vs voxel, or the smoothing difference (~7 %
peak co-pol, same order as a plausible shape effect) contaminates the
comparison.

## Files

| File | Description |
|---|---|
| `packing_seed42.csv` | Shared sphere packing (x,y,z,r) — SSOT for both decks |
| `ctrl_sphere_native.in` | Control deck: 233 native `#sphere` (default smoothing) |
| `ctrl_sphere_native_nosmooth.in` | Same, `--sphere-smoothing n` |
| `ctrl_sphere_voxel.in` | Test deck: same rocks via `#geometry_objects_read` |
| `ascan_overlay.png` | 3-trace overlay + residuals (unified_visualizer --overlay) |
| `ctrl_sphere_voxel_rocks.h5` | int16 voxel array (250×250×175, −1 background) |
| `ctrl_sphere_voxel_rock_materials.txt` | Materials file (row 0 = granite) |
| `ctrl_sphere_*.vti` | Built-geometry views (ParaView) |
| `ctrl_sphere_*.out` | FDTD outputs |

## Next step (separate experiment)

Matched-pair A/B on the SAME packing: `voxel-sphere` vs `voxel-ellipsoid`
(and later clump/spherical-harmonic shapes) to measure whether rock shape
moves the 420 MHz coda at all, before investing in shape realism.

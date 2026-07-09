# Rock Shape A/B — Does Particle Shape Matter at 420 MHz?

**Date:** 2026-07-01
**Question:** Do realistic (non-spherical) rock shapes change the GPR response
vs spheres, at GSSI-400 frequencies? Prerequisite infrastructure validated in
`../voxel_rock_control/` (voxel path bit-identical to native `#sphere`).

## Design

Four scenes, all on the **identical 233-rock packing** (`packing_seed42.csv`),
all via the voxel path (no dielectric smoothing anywhere — see control
experiment), differing ONLY in the per-rock shape carved inside each packed
bounding sphere:

| Deck | Shape | phi_slab (granite) | Volume vs sphere |
|---|---|---|---|
| `ctrl_sphere_voxel` | sphere (baseline) | 0.189 | 1.00 |
| `shape_sphere_small` | sphere, r × 0.745 | ~0.078 | 0.41 |
| `shape_ellipsoid` | random triaxial ellipsoid (EN 933-ish 1:0.7:0.6) | 0.078 | 0.41 |
| `shape_polyhedron` | convex hull of 10–18 random surface points (angular) | 0.080 | 0.42 |

Inscribed shapes shrink rock volume (ellipsoid/hull ≈ 0.41× the sphere), so
**shape-vs-sphere is volume-confounded**. The small-sphere control breaks the
confound: the bottom three rows are volume-matched, isolating pure shape
(elongation + orientation + angularity). Note the volume-matched trio still
differ in max dimension (ellipsoid long axis = full 2r ≈ 64 mm vs small-sphere
48 mm), so this also tests characteristic-length sensitivity at fixed volume.

Scene otherwise standard: 0.5×0.5×0.8 m, dx = 2 mm, void fill eps 4.5/σ 0.001,
GSSI 400 antenna, 30 ns. Analysis on **Ey (co-pol)**, coda window 8–18 ns.

## Results

| Pair | r_full | r_coda | max res | RMS coda | coda lag |
|---|---|---|---|---|---|
| **volume changes (0.19 → 0.08):** | | | | | |
| sphere vs sphere-small | 0.9624 | 0.797 | 39.1 % | 10.7 % | −0.18 ns |
| sphere vs ellipsoid | 0.9634 | 0.803 | 38.6 % | 10.6 % | −0.18 ns |
| sphere vs polyhedron | 0.9636 | 0.805 | 38.4 % | 10.5 % | −0.17 ns |
| **volume-matched (pure shape):** | | | | | |
| sphere-small vs ellipsoid | 0.99996 | 0.99994 | 0.95 % | 0.17 % | 0.00 ns |
| sphere-small vs polyhedron | 0.99996 | 0.99992 | 0.86 % | 0.24 % | 0.00 ns |
| ellipsoid vs polyhedron | 0.99990 | 0.99998 | 1.39 % | 0.27 % | 0.00 ns |

Coda energy: sphere 2446; small-sphere 1353; ellipsoid 1336; polyhedron 1390.

## Verdict (single-seed; n=1 packing)

**At 420 MHz, the coda measures granite volume fraction, not particle shape.**

- All three volume-matched shapes are interchangeable: r ≥ 0.9999, residuals
  ≤ 0.3 % RMS — below even the dielectric-smoothing effect (~1.2 % RMS).
  Elongation, random orientation, angular facets, and even a 30 % difference
  in maximum particle dimension at fixed volume: all invisible.
- Changing volume fraction (0.19 → 0.08) produces a huge, shape-independent
  signature: r_coda ≈ 0.80, −45 % coda energy, −0.18 ns earlier coda
  (lower eps_eff). Sphere→small-sphere is indistinguishable from
  sphere→ellipsoid.

This is Rayleigh-regime behaviour (rocks ≈ λ/5 in the matrix): scattering
follows volume and contrast, insensitive to morphology — consistent with
Couchman 2024 (shape/fabric discrimination is a ≥2 GHz Mie effect) and with
the DZT-calibration verdict that the coda is geometry-dominated in the sense
of *amount and placement* of rock, not particle morphology.

**Practical consequence: sphere models with the correct granite volume
fraction are adequate at 400 MHz; realistic shapes are not worth voxel-path
cost for this antenna.** Shape modelling only becomes a candidate again if we
move to GHz-range simulations.

**Caveats:** one packing/seed, one frequency, r = 19–32 mm rocks, dx = 2 mm
(cm-scale shape differences fully resolved, so the null is physical, not a
resolution artifact); fouling-free scene.

## Files

| File | Description |
|---|---|
| `packing_seed42.csv` | Shared packing (copied from ../voxel_rock_control) |
| `ctrl_sphere_voxel.{in,out}` + `_rocks.h5` | Baseline (copied, not re-run) |
| `shape_sphere_small.{in,out}` + `_rocks.h5` | Volume-matched sphere control |
| `shape_ellipsoid.{in,out}` + `_rocks.h5` | Ellipsoid rocks |
| `shape_polyhedron.{in,out}` + `_rocks.h5` | Angular hull rocks |
| `shape_slices.png` | XZ slices of the four rock arrays |
| `ascan_overlay.png` | Ey overlay + residuals |

Generation (per shape):
```
generate_3d_scene.py --rocks --void-eps 4.5 --void-sigma 0.001 \
    --rock-shape voxel-{sphere-small,ellipsoid,polyhedron} \
    --sphere-file packing_seed42.csv --out shape_X.in
```

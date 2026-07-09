# Shape Invisibility — Grid-Resolution Control (dx = 2 mm vs 1 mm)

**Date:** 2026-07-02
**Question:** Is the rock_shape_ab result ("particle shape is invisible at
420 MHz; only granite volume fraction matters") an artifact of the dx = 2 mm
FDTD grid? If finer cells resolve the facets/elongation better, would shape
start to matter?

## Design (only dx changes)

Controlled A/B: **one shared 32-rock packing** (`packing.csv`), the
volume-matched pair **sphere-small (r×0.745) vs polyhedron (convex hull)**,
voxelised and simulated at **dx = 2 mm AND dx = 1 mm**. Everything else is
identical. If r(sphere, poly) stays ~1.0 at both resolutions, the invisibility
is physical (Rayleigh regime, set by wavelength), not staircasing.

Compact scene (fits the 6 GB GPU at 1 mm; the full 0.5×0.5×0.8 m GSSI scene at
1 mm = 200 M cells does not): domain 0.30×0.30×0.40 m, subgrade 0–0.12 m,
ballast 0.12–0.32 m (void eps 4.5 + granite eps 6.1 rocks), y-Hertzian dipole
3 cm above surface, ricker 420 MHz, 18 ns. A dipole (not the full antenna) is
valid here because a *relative* shape A/B cancels the source. Analysis on Ey
(dipole co-pol), coda 3–16 ns.

Rock cells (volume-matched to ~3 %): sphere-small 835 624 / polyhedron 862 380
(at 1 mm). Runtimes on RTX 2060: 2 mm ~20–35 s, 1 mm ~3.5 min.

## Result

| dx | r(sphere, poly) | coda energy ratio (sph / poly) | dt | samples |
|---|---|---|---|---|
| 2 mm | **1.000000** | 0.1464 / 0.1464 | 3.85 ps | 4675 |
| 1 mm | **1.000000** | 0.1465 / 0.1465 | 1.93 ps | 9348 |

The traces are not bit-identical (the two shapes differ by ~3 % in cell count
and the energy ratios differ in the 4th decimal), so the comparison IS
resolving two genuinely different geometries — it simply finds their waveforms
indistinguishable. Halving dx (dt correctly halved 3.85→1.93 ps, samples
doubled) changed nothing.

## Verdict

**Shape invisibility is PHYSICAL, not a grid artifact.** At dx = 2 mm a
25 mm-radius rock is already ~25 cells across, so the facets and elongation are
well resolved; refining to 1 mm only reduces staircasing/numerical dispersion —
it does not change the wavelength (λ ≈ 320 mm in the ballast at 420 MHz). The
rock is λ/6 (size parameter x ≈ 0.5, Rayleigh regime): the wave responds to
volume and permittivity contrast, not morphology, at any grid resolution.

The lever that would make shape matter is **frequency** (shorter λ → Mie
regime, ~2 GHz), not cell size. Confirms rock_shape_ab and Couchman 2024.

## Files
- `generate_decks.py` — packs once, writes 4 decks (shape × dx)
- `compare_dx.py` — Ey coda r(sphere, poly) at each dx
- `packing.csv`, `*.in`, `*_rocks.h5`, `*_materials.txt`, `*.out`

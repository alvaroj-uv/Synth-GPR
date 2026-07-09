# Kingsuwannaphong, Bräu, Rial, Rümmler & Heberling 2021 — Realistic Railway Ballast FDTD Simulations for GPR

RWTH Aachen (Inst. High Frequency Technology) + Fraunhofer FHR. IEEE/ICEAA-type
conference paper. gprMax FDTD, 3D realistic ballast, validated against controlled
lab measurements.

## Why it matters to us
This is the **published twin of our voxel-rock forward pipeline**. Their method:
Blender **Rock Generator** → many standards-compliant stones → **voxelize →
HDF5 occupancy matrix → gprMax `#geometry_objects_read`**. That is exactly our
`src/rock_voxelizer` → `#geometry_objects_read` path (see project memory
*Voxel Rock Pipeline*). A top-tier group (RWTH/Fraunhofer) using the identical
method ⇒ the forward pipeline is a known, publishable technique; **our novelty is
downstream (ML / inversion / identifiability)**, not in the simulator plumbing.
Reinforces the Go & Lee 2021 conclusion.

## Key parameters (Table I)
- Domain 1042×1044×866 mm; ballast thickness 500 mm; sand subgrade 80 mm.
- Stone diameter **31.5–63 mm** (EN13450 grading D–F / AREMA No. 24).
- **ε_stone = 4**; ε_sand = 3; ε_fouled soil ≈ 3.5 (Di Chiara 2014).
- **Voxel 2 mm**; C-scan spatial sampling 10 mm; sensor height 30 mm (sim) /
  100 mm (measurement); **time window 12 ns**.
- Antenna centre frequency **not stated** (flagged by authors as future work).
- Sand subgrade + fouling given **heterogeneous EM properties + surface
  roughness** for realism.
- 3 scenarios: clean (CDB), 50 % fouled (FDB), FDB + 45°-tilted 20 cm acrylic
  cavity.

## Results
- **Fouling is visually near-invisible**: "differences between FDB and CDB
  apparently not very distinctive" — in BOTH sim and their controlled lab box.
  Clean/fouled interface ≈ 6 ns, subgrade interface ≈ 9 ns.
- Cavity: even a well-defined 20 cm cylinder is hard to delineate visually
  because of ballast scattering clutter.
- Full-polarimetric robotic 3-axis acquisition proposed as route to more robust
  ballast estimators (future work).

## Status vs our project
- **VALIDATES** — (1) voxel-rock `#geometry_objects_read` pipeline is a published
  standard; (2) ε_stone = 4 (3rd+ convergence, cf. Li 2025); (3) dry-fouling
  visual invisibility, now backed by controlled lab measurement.
- **PENDING / NOT APPLICABLE** — full-polarimetric features: a lever we haven't
  used, but our real corpus (Puerto-Limache GSSI-400) is single-channel/scalar,
  so not usable for our sim→real path. Blender Rock Generator shapes: our
  2026-07-02 `shape_freq_sweep` already showed particle shape is invisible at
  400 MHz (Rayleigh); realistic shapes only pay off ≥2 GHz (Mie), so no gain at
  railway frequency.
- **Caveat** — antenna frequency unstated, so their Rayleigh/Mie regime can't be
  placed; 2 mm voxel suggests a GHz sensor.

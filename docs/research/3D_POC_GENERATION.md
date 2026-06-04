# 3D Proof-of-Concept: Input Generation & Visualization

Documentation of the 3D FDTD proof-of-concept (POC) pipeline that extends the 2D
GPR ballast-fouling dataset into true 3D geometry. Goal: quantify the accuracy
drop from 2D (cylindrical wave spreading, 1/r) to 3D (spherical spreading, 1/r²)
for the waveform-only fouling classifier.

**Scripts:**
- Generation: [scripts/main/generate_3d_inputs.py](../scripts/main/generate_3d_inputs.py)
- Visualization: [scripts/visualization/render_in_file.py](../scripts/visualization/render_in_file.py) (auto-detects 2D vs 3D)
- 3D render core: [scripts/visualization/render_3d_in_file.py](../scripts/visualization/render_3d_in_file.py)

---

## 1. Domain Geometry (400 MHz, IEEE 2025 compliant)

Domain dimensions are **frequency-derived** via `get_fdtd_recommendations()` in
[src/physics.py](../src/physics.py), following Khosravi Largani et al. (2025),
"FDTD Medium Dimension Selection Guidelines for GPR Synthetic Data Generation".

| Parameter | Value (400 MHz) | Rule |
|-----------|-----------------|------|
| Domain X (length) | 2.248 m | ≥ 1.5 × λ_max |
| Domain Y (depth) | 1.15 m | layer stack + antenna clearance |
| Domain Z (width) | 0.40 m | fixed transverse (survey-perpendicular) |
| Grid spacing dx=dy=dz | 0.0132 m (13.2 mm) | ≤ λ_min / 10 |
| Antenna height | 0.80 m | > λ_max / 2 |

Where for a Ricker pulse at f_c = 400 MHz: f_min ≈ 0.5·f_c, f_max ≈ 1.5·f_c;
λ_max = c/f_min ≈ 1.50 m (air); λ_min = c/(f_max·√ε_max) ≈ 0.13 m (wet soil, ε_max=14.4).

### Vertical layer stack (Y axis, bottom → top)

| Layer | Y range (m) | Thickness |
|-------|-------------|-----------|
| Subgrade | 0.00 – 0.20 | 0.20 |
| Formation | 0.20 – 0.30 | 0.10 |
| **Ballast (rocks)** | **0.30 – 0.55** | **0.25** |
| Antenna clearance (air) | 0.55 – 1.05 | 0.50 |
| Air buffer | 1.05 – 1.15 | 0.10 |

Antenna TX placed at the **middle of the clearance zone** (y = 0.80 m), well above
ballast top (0.55 m) to avoid near-field coupling. RX offset +0.15 m in X.

---

## 2. Sphere-Packed Ballast

Rocks are modeled as `#sphere` commands (3D analog of the 2D `#cylinder`/`#triangle`).

- **150 spheres/sample** (raised from initial 80 for realistic density).
- Radius ~ N(0.020, 0.003) m, clipped to [0.015, 0.035].
- **Confined to ballast zone only**: y ∈ [0.30+r, 0.55−r], x ∈ [r, Dx−r], z ∈ [r, Dz−r].
- Grid-accelerated collision detection (10×10×10 spatial hash) prevents overlap.

### Fouling representation

A `#box` of `bal_foul_granular` fills the ballast void **up to a class-specific
height**, placed *before* the spheres so rocks (rendered after) overwrite it —
leaving fouling only in inter-rock voids. Heights are **offsets from ballast
bottom** (0.30 m):

| Class | Fouling y_max (m) | Penetration |
|-------|-------------------|-------------|
| C (Clean) | 0.32 | 2 cm |
| MC | 0.35 | 5 cm |
| MF | 0.38 | 8 cm |
| F | 0.45 | 15 cm |
| HF (Highly Fouled) | 0.50 | 20 cm |

200 samples per class → 1000 total. Output: `input_files_3d_poc/s_00000.in … s_00999.in`.

---

## 3. PML Absorbing Boundary

`#pml_cells: N N N N N N` (6-param form, all faces). Sized at **10% of the
smallest domain dimension**, minimum 10 cells:

```
pml_cells = max(10, int(0.1 * DOMAIN_Z / DX))
```

For the 400 MHz domain (Dz=0.4, dx=0.0132) this yields 10 cells = 0.132 m ≈ 12% of
Dz — consistent with the 2D reference (`#pml_cells: 10 10 0 10 10 0`).

**Lesson learned:** an earlier hard-coded `cells=10` at dx=0.01 on a 0.4 m domain
gave 25% PML coverage (~3 wavelengths) — far too thick, wasting compute. PML should
be ~0.1–0.2 wavelengths. Always size PML relative to the *smallest* domain dimension.

---

## 4. File Format (matches 2D convention)

Generated `.in` files mirror the 2D `GPRMaxFileWriter` layout exactly:

1. `## ===...===` separator + metadata header block (sorted keys, git hash, seed).
2. `## ===...===` closing separator.
3. **Section headers placed directly before their command groups** (NOT bundled):
   `## Domain Configuration`, `## Sources and Receivers`, `## Materials`, `## Geometry`.
4. Commands rendered **in build order** (no priority sort) so headers stay attached
   to their groups.
5. Trailing commented `## #geometry_view: ...` for optional VTK export in Paraview.

**Lesson learned:** the command framework's priority-based sort (Header priority=0)
pulled all section headers to the top, orphaning them. Fix: render the 3D command
list in insertion order instead of sorting by priority.

`SphereCommand` was added to [src/gpr_commands.py](../src/gpr_commands.py) (priority 20,
same as objects/cylinders) to support `#sphere` in the command framework.

---

## 5. Visualization — Three Orthogonal Views with True Axis Alignment

`render_in_file.py` auto-detects 3D files (presence of `#sphere`) and dispatches to
the 3D renderer. Three views: TOP (X-Z), FRONT (X-Y), SIDE (Z-Y).

### Alignment requirement
- TOP and FRONT must share the **same on-screen X-axis width** (both span Dx).
- FRONT and SIDE must share the **same on-screen Y-axis height** (both span Dy).

### Why GridSpec failed (key lesson)
`set_aspect('equal')` **overrides** GridSpec `width_ratios`/`height_ratios`:
matplotlib resizes each axes box to satisfy the equal-aspect constraint, which
desynchronizes the TOP (full-width) and FRONT (half-width column) widths. No amount
of ratio tuning fixes this because aspect wins.

### The fix: manual `add_axes()` with shared pixels-per-metre
Compute one `ppm` (inches per metre) and place all three axes explicitly:

```python
ppm = target_plot_width / Dx          # shared scale for ALL views
ax_top   : width = Dx*ppm, height = Dz*ppm   at (left,           top_b)
ax_front : width = Dx*ppm, height = Dy*ppm   at (left,           bottom)   # below TOP
ax_side  : width = Dz*ppm, height = Dy*ppm   at (left+Dx*ppm+gap, bottom)  # right of FRONT
```

This guarantees identical widths (TOP/FRONT) and heights (FRONT/SIDE) and a single
consistent scale — a 2 cm rock looks the same in every view. Do **not** use
`tight_layout()` with manual axes (it warns and can misplace them).

**Naming gotcha:** the local helper was first named `rect`, colliding with the
`Rectangle` import aliased `rect` inside the box-drawing loops → `'Rectangle' object
is not callable`. Renamed to `axes_rect`.

Example output: [output/s_00500_3d_views.png](../output/s_00500_3d_views.png).

---

## 6. Verification Checklist

A generated file should satisfy:
- [ ] `## Lab_Class:` matches expected class for its sample-id band (0–199=C, …, 800–999=HF)
- [ ] Fouling `#box` present at the class-specific y_max (C may skip if ≤ ballast_min+0.01)
- [ ] ~150 `#sphere` commands, all with y ∈ [ballast_min, ballast_max] (±radius)
- [ ] `#domain`, `#material` (×4), `#waveform`, `#hertzian_dipole`, `#rx`, `#pml_cells` present
- [ ] TX y above ballast top; antenna height > λ_max/2
- [ ] Two `## ===` separators; four section headers each above their command group
- [ ] Trailing commented `## #geometry_view:`

---

## 7. Next Steps

1. Run gprMax 3D FDTD on the 1000 `.in` files (~4–5 h on A100).
2. Extract the 572 waveform features from the 3D `.out` files.
3. Build parquet; train waveform-only RF.
4. Compare 3D balanced accuracy vs the 2D baseline (88.68%) to quantify the
   2D→3D domain gap.

See also: [docs/IN_FILE_GENERATION.md](IN_FILE_GENERATION.md) (2D pipeline),
[docs/PACKING_ALGORITHMS.md](PACKING_ALGORITHMS.md),
[docs/studies/FDTD Medium Dimension Selection.md](studies/FDTD%20Medium%20Dimension%20Selection.md).

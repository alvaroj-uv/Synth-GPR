# Shape Visibility vs Frequency — Rayleigh → Mie transition

**Date:** 2026-07-02
**Question:** rock_shape_ab + shape_dx_verify showed particle shape is invisible
at 420 MHz (and that this is not a grid artifact). The physics argument is that
420 MHz sits in the Rayleigh regime (size parameter x ≈ 0.5). Prediction: raise
the frequency, shrink λ, push the rocks toward x ≈ 1–3 (Mie), and the sphere vs
polyhedron waveforms should DIVERGE. This closes the argument that **frequency,
not cell size, is the lever for shape sensitivity**.

## Design (only frequency changes)

Same compact scene and dx = 1 mm as shape_dx_verify. **Reuses the EXACT 1 mm
rock HDF5 arrays** (sphere-small, polyhedron — volume-matched, same 32-rock
packing); only the ricker centre frequency of the y-dipole changes. 8 runs:
{sphere, poly} × {0.42, 1.0, 1.5, 2.4} GHz. Analysis on Ey, coda 3–16 ns.
Source is a point dipole (no GSSI model exists at GHz); valid because a
*relative* shape A/B cancels the source. Each deck also writes a geometry .vti.

## Result

| freq | size param x = 2πa/λ | r(sphere, polyhedron) | regime |
|---|---|---|---|
| 420 MHz | 0.49 | **1.000000** | Rayleigh — shape invisible |
| 1.0 GHz | 1.17 | 0.999979 | transition — barely |
| 1.5 GHz | 1.76 | 0.997546 | Mie — starts to diverge |
| 2.4 GHz | 2.81 | **0.972903** | Mie — clearly visible |

Monotonic drop, tracking the size parameter across x ≈ 1 (see
`shape_vs_frequency.png`): flat at r = 1.0 through the Rayleigh band, a knee
near x ≈ 1.2, then a clear decline as the rocks enter the Mie regime.

## Verdict

**Confirmed: the lever for shape sensitivity is FREQUENCY, not grid resolution.**
The full physical picture is now closed across three experiments:
- rock_shape_ab: shape invisible at 420 MHz (volume fraction is everything).
- shape_dx_verify: not a dx artifact (r = 1.000000 at both 2 mm and 1 mm).
- shape_freq_sweep (this): shape *becomes* visible as frequency rises into Mie.

This is exactly the Rayleigh→Mie transition and matches Couchman 2024 (shape/
fabric discrimination is a ≥2 GHz effect). Operationally: 400 MHz railway GPR
cannot see particle morphology — spheres with the right volume fraction suffice;
a ~2 GHz system would be needed to exploit shape/grading.

## Caveats

- The effect at 2.4 GHz is real but still modest (r = 0.973; waveforms 97%
  correlated) — envelope correlation understates waveform differences, and
  x = 2.8 is early Mie. Deeper Mie (higher x) would diverge further.
- dx = 1 mm at 2.4 GHz is ~λ/20 in granite (borderline); numerical dispersion
  may slightly *suppress* the true high-frequency shape effect, so 0.973 is if
  anything a conservative (upper) bound on r.
- Compact 0.30 m domain + dipole: fine for the relative A/B; absolute waveforms
  are near-field/boundary-truncated at 420 MHz (irrelevant to the trend).

## Files
- `generate_decks.py`, `compare_freq.py`, `shape_vs_frequency.png`
- `{sphere,poly}_rocks.h5` (reused geometry), `*.in`, `*.out`, `*.vti`

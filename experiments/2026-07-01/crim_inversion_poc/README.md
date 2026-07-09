# CRIM-Parameterized Layer Inversion — Synthetic Recovery POC

**Date:** 2026-07-01
**Question:** If the ballast layer is parameterized by physical mixing fractions
— fines fill f (fouling axis) and pack saturation S_w (moisture axis) — instead
of a free (eps, σ), can the 2D envelope inversion recover them from a single
420 MHz trace? This measures best-case identifiability (inversion crime: same
forward operator for target and trials).

## Why CRIM parameterization

- The rock-shape A/B (`../rock_shape_ab/`) showed the 420 MHz coda measures
  granite volume fraction / eps_eff only → mixing fractions are exactly the
  information the waveform carries.
- Bounded physical unknowns (0 ≤ f, S_w ≤ 1) truncate the d–ε degeneracy ridge.
- σ is coupled to the same unknowns (surface conduction + electrolytic rule
  from `src.physics.crim_fouling_eps`), so amplitude decay constrains S_w
  instead of being a free nuisance.
- Downstream: (f, S_w, thickness) feed P1/P6/P7 of the Rojas-Vivanco 2026
  indicator fault tree (`docs/studies/vivanco_2.md`).

## Parameterization hull (no tuning — falls on the field calibration points)

| (f, S_w) | eps_b | σ_b | Matches |
|---|---|---|---|
| (0, 0) clean | 3.43 | 0.001 | pit-ID11 analytic clean 3.45; Benedetto 3.51 |
| (1, 0) dry fouled | 4.80 | 0.0013 | Benedetto dry cap 5.35 — dry fines barely move eps |
| (1, 1) saturated fouled | 12.50 | 0.018 | pit-ID11 fouled 11.3; Mbubia 11–12 |

Chain: rock skeleton 0.58 (eps 6.1) + void 0.42 → fines pack (internal φ 0.40,
mineral eps 5.5) fills fraction f of voids; water (eps 81) only inside the pack.

## Forward model

2D flat 3-layer (`scripts/calibration/invert_pk20000m_envelope.py`, v3 PK20000m
geometry, dx=3 mm, 22 ns), GSSI-calibrated excitation, subgrade/formation fixed
at defaults. Objective: Hilbert-envelope Pearson r in the 4–18 ns coda.
2D justified: engine is ~5 s/run (vs ~2.5 min 3D); flat-layer timing is
dimension-independent; envelope-r is scale-invariant so 2D/3D spreading
differences don't bias it. 3D GSSI twin reserved as verification tier.

## Design

Synthetic target at **off-grid truth (f=0.35, S_w=0.60)** → eps_b=5.078,
σ_b=0.0040. Grid: f ∈ {0, 0.2, 0.4, 0.6, 0.8, 1.0} × S_w ∈ {0, 0.25, 0.5,
0.75, 1.0} (30 runs).

Command:
```
python scripts/calibration/invert_pk20000m_envelope.py --mode crim \
    --synthetic-target 0.35,0.6 --workdir experiments/2026-07-01/crim_inversion_poc
```

## Results (30-run grid, 7.6 s/run; see `recovery_surface.png`)

**eps_eff is identified almost exactly; the (f, S_w) split is fully degenerate
along the iso-eps_eff contour.**

- Best cell: (f=0.40, S_w=0.50) r=0.9994 → eps_b=5.09 vs truth 5.078. The
  r>0.99 set spans eps_b 5.09–5.10 only — sharp single-trace eps_eff recovery.
- BUT r>0.95 includes four cells with nearly identical eps_b and wildly
  different physics: (0.2, 1.0), (0.4, 0.5), (0.6, 0.25), (1.0, 0.0) — from
  "lightly fouled, saturated" to "fully fouled, bone dry".
- All 30 combos collapse onto a single r(eps_b) curve (left panel): the
  envelope objective sees ONE number per layer, eps_eff. Textbook
  non-injectivity (2 unknowns → 1 observable), now in CRIM coordinates.
- The σ coupling did NOT break it: envelope-r is scale-invariant, and along
  the ridge σ_b varies only 0.0013→0.0040 — too little waveform-shape change.

## Interpretation

The good news: the physically-bounded CRIM box plus a single 420 MHz trace
pins the *wet-fouling state* (eps_eff) essentially exactly — and eps_eff is
what the group's real FI labels respond to anyway (Benedetto: field FI signal
is mostly moisture; pit-ID11: clean 3.45 / fouled 11.3 = our (0,0) and (1,1)
corners). The honest deliverable per trace is **eps_eff (or the iso-contour
in (f, S_w) space), not a (f, S_w) point**.

Splitting f from S_w needs a second, water-specific observable:
1. **Water Debye dispersion** — frequency-dependent loss distinguishes water
   from dry fines (Qin 2023 τ-method lead); check band-limited spectral
   ratios at 420 MHz feasibility first.
2. **Absolute amplitude / attenuation** — requires amplitude-faithful
   modelling (3D or 3D→2D transform) and trusted gain; envelope-r discards it.
3. **Two-season surveys** — f is quasi-static, S_w varies; differencing
   isolates the moisture axis.
4. **Priors** — pandoscope layer data or drainage records constrain S_w.

## Update (same day): two-term objective partially breaks the wall

The Pearson-r objective is scale-invariant — it discards the amplitude decay
that σ (hence pore water) imposes. A per-trace, gain-immune attenuation
observable was added: **late/early coda envelope-energy ratio**
(`coda_energy_ratio` in `src/signal_processing.py`; windows 4–11 / 11–18 ns
after first break). Direct test on the ridge cells: the dry extreme
(f=1, S_w=0) has **+42 % coda energy and −27 % late/early ratio** vs truth —
loudly separable by amplitude despite identical envelope shape.

Two-term objective (`--objective shape+amp`):
`score = r − 1.0·|log(ratio_syn / ratio_target)|`

Recovery grid rerun, same off-grid truth (see `objective_comparison.png`,
`results_crim_amp.csv`):

| Objective | cells > 0.95 | their f range |
|---|---|---|
| shape only | 4 | 0.2 – 1.0 (whole ridge) |
| shape + amplitude | **1** — (0.4, 0.5), nearest node to truth | — |

Impostor scores: (1.0, 0.0) 0.956→0.635; (0.2, 1.0) 0.966→0.861;
(0.6, 0.25) 0.999→0.944 (nearest ridge neighbour — σ differs from truth by
only ~15 %, so residual ambiguity of roughly ±0.2 in f / ±0.25 in S_w
remains at this grid resolution and zero noise).

**Conclusion: eps_eff from envelope shape + moisture axis from envelope
energy — two observables from ONE trace, no new hardware.** The energy ratio
is computed within a single trace so absolute gain (DZT scale, missing GSSI
V_ref) cancels; it is NOT immune to 2D-vs-3D spreading — calibrate that
offset once with a 3D run before applying to real data.

## Caveats

Inversion crime (same forward operator), single layer inverted, thicknesses
fixed from B-scan picks, subgrade/formation eps fixed, noise-free. Field
performance will be worse; the d–eps thickness degeneracy is untested here.

## Files

- `results_crim.csv` — shape-only grid (f, S_w, σ_b, eps_b, r)
- `results_crim_amp.csv` — two-term grid (score, r_shape, ratio)
- `recovery_surface.png` — r(eps_b) collapse + (f, S_w) ridge heatmap
- `objective_comparison.png` — shape-only vs shape+amp side by side

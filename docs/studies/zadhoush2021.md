# Zadhoush 2020 (PhD thesis, Edinburgh) — Optimising CRIM shape factor + GPR time-zero

**Citation:** Zadhoush, H. (2020). *Numerical Modelling of Ground Penetrating Radar for
Optimisation of the Time-Zero Adjustment and Complex Refractive Index Model.* PhD thesis,
University of Edinburgh (supervisor: A. Giannopoulos — the gprMax author). Journal spin-offs:
Zadhoush, Giannopoulos & Giannakis (2021) *Remote Sensing* 13(4):723 (CRIM shape factor);
Zadhoush & Giannopoulos (2021) *Near Surface Geophysics* (time-zero).

Closest methodological sibling to our CRIM inversion so far: same gprMax + CRIM + spherical
aggregates + Peplinski-moisture stack, from the gprMax group itself.

## The two contributions

### 1. The CRIM "shape factor" α is a tunable parameter, not a fixed 0.5

CRIM is `eps_mix^α = Σ V_i · eps_i^α`. The ubiquitous α = 0.5 (√-mixing, spherical grains) is a
**convention, not a law** — its accuracy "has never been rigorously tested." Zadhoush builds a
64-model FDTD training set of heterogeneous concrete (aggregate + cement + air-void + water),
computes each bulk eps from the reflected wavelet TWTT, and fits α to minimise CRIM-vs-FDTD error:

- **α = 0.13** minimises error for concrete (with the thesis's explicit time-zero method).
- **α = 0.25** if a naive positive-peak-to-positive-peak time-zero is used instead.
- Literature spread: 0.5 (default), 0.46, 0.65–0.66 (Dobson/Peplinski/Gardner).
- Validated experimentally: 1 GHz horn over concrete blocks with widening air gaps; α = 0.13
  beat α = 0.5 on measured bulk permittivity.

### 2. Time-zero / TWTT picking is COUPLED to the permittivity estimate

The shape factor moved from 0.13 → 0.25 **purely by changing the time-zero picking method** —
nothing else. Message: fix time-zero/TWTT first; only then is the CRIM/permittivity estimate
trustworthy. The thesis's whole first half derives a time-zero position robust to unknown target
depth/shape/material (tested across depths, shapes, half-space eps, antennas; lab-validated).

Also: Chapter 4 justifies modelling aggregates as **spheres** (cf. our shape-invisible result);
compares CRIM against **Rayleigh** and **Böttcher** mixing models.

## What it contributes to us (docs/architecture + crim_inversion_poc)

- **Actionable: α is a free knob we've been leaving at 0.5.** `src.physics.crim_bulk_eps`
  hardcodes √-mixing (α = 0.5). We could calibrate α for ballast the same way (small FDTD training
  set, or fit against our 3 field anchors 3.43/4.80/12.5) as a refinement of the eps_eff ↔ (f, S_w)
  map. **DO NOT copy α = 0.13** — that is concrete-specific. Our √-CRIM hitting all three field
  anchors with zero tuning is reassuring, but α-sensitivity is a natural extension for the
  identifiability paper.
- **Reinforces the time-zero concern.** Our eps_eff recovery depends on first-break/TWTT picking,
  and we carry a known +4 ns shift (420 MHz validated pipeline) plus five first-break
  implementations (debt D7). Zadhoush shows picking method alone can nearly double the fitted
  mixing exponent → get time-zero right before trusting any inverted permittivity.
- **Methodological validation.** gprMax + CRIM + spheres + Peplinski moisture is a PhD-grade,
  gprMax-group-endorsed methodology — good to cite for the thesis.

**Status:** REFERENCE + PENDING (α-calibration as a CRIM-inversion refinement; time-zero method
review tied to debt D7 / the +4 ns shift).

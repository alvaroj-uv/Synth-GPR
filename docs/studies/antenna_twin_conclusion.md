# Antenna Twin Investigation — Conclusion

**Date:** 2026-06-02
**Question:** Is the antenna model (idealized point source vs. realistic GSSI
antenna) the cause of the synthetic→real frequency-feature gap?
**Verdict:** **No. The antenna is not the gap.** Direction closed.

Origin: the "antenna twin" idea from the validation roadmap (see
`lahnsteiner2024_notes.md`) — replace the bare Hertzian dipole with a realistic
antenna to better match real 400 MHz GPR.

## What was tested

Two A/B tests, increasing in fidelity. Real reference throughout:
`docs/input/feature_dataset_real.csv` (n=101 Site-1, 400 MHz), median
mean=703 / median=480 / dom=320 MHz. Metric = `_extract_frequency_features`
(same definition for sim and real, no metric artifact).

### Test 1 — Waveform only (2D, cheap)
Ricker → GSSI-style Gaussian excitation on a bare dipole, 400 MHz. 24 traces
(`scripts/main/waveform_ab.py`).
- Gaussian shifted spectrum **away** from real on 2/3 descriptors.
- **Why it was the wrong test:** the Gaussian@1.71 GHz is optimised *jointly with
  the antenna housing* inside gprMax's `antenna_like_GSSI` model. Feeding it to a
  bare dipole uses half a matched pair. GPR-repo's own author defaults to
  Ricker+dipole (`inputfile.py` antenna=False) — same as this project.

### Test 2 — Full antenna twin (3D, 2mm, expensive)
Official `antenna_like_GSSI_400` (validated Warren/Giannakis geometry) via the
supported `#python` import, vs. z-dipole. 3 FI × {dipole, antenna} = 6 traces
in a compact 0.38×0.38×0.608 m, 2 mm domain (~11M cells)
(`scripts/main/antenna_twin_ab.py`).

| Descriptor | dipole | antenna | REAL | Closer |
|---|---|---|---|---|
| mean_freq | 621 | 486 | 703 | dipole |
| median_freq | 400 | 467 | 480 | **antenna (13 off)** |
| dom_freq | 317 | 533 | 320 | dipole |

Antenna closer on **1/3**. (Note: arms radiate on different components —
z-dipole→Ez, GSSI y-bowtie→Ey — so the loader picks the dominant component by
energy; the two arms are therefore not the identical physical quantity.)

## Conclusion

Both tests — increasingly faithful — fail to move the synthetic spectrum toward
real. This **rules out the source/antenna** as the cause of the gap and redirects
attention to the **ground/coda physics** (fouling scattering; see
`project_freq_signature_causes` in memory, and the heterogeneous-fouling study).

A useful negative result, not a dead end.

## Caveats (do not over-claim)
- n=3 in the 3D test — proof-of-concept, not a powered study.
- Compact stand-in scene (0.38 m box, 2 cm rocks, simplified layers), **not** the
  real 80k track geometry; absolute frequencies here are not directly comparable.
- Dipole-Ez vs antenna-Ey are not the identical physical quantity.

## Dormant infrastructure kept (not removed)
Left in the codebase, default-off / opt-in, in case the direction is revisited:
- `config.source_waveform` ("ricker" default | "gaussian") + `gaussian_excitation_freq` — wired in `AntennaWorker`.
- `scripts/main/waveform_ab.py` — 2D ricker-vs-gaussian harness.
- `scripts/main/antenna_twin_ab.py` — 3D GSSI-400 twin harness (uses the official `#python` antenna import).
- 3D renderer (`src/visualization/scene_3d.py`) — now parses the GSSI `#python` antenna call + `fouling` material.

**Do not** spend more GPU scaling the antenna twin unless a new hypothesis
emerges; the negative result is consistent across two methods.

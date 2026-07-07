# Alsahli & Alsulmi 2023 — Automatic Detection of Sand Fouling Levels Using Supervised ML (Saudi Railway)

Arab. J. Sci. Eng. (King Fahd Univ.). Case study on Saudi Rail Company (SAR) data.

## What it is
3-class sand-fouling classification (high / moderate / clean) on railway track —
**from track-geometry-car data, NOT GPR.** 23 geometry features (profile,
alignment, gauge, warp, twist) per 0.3 m location. 11,905 balanced instances
(3.6 km). ANN 96.14 %, RF 95.91 %, Logistic Tree 83.68 %, DT 78.01 %; 10-fold
stratified CV in Weka. RF preferred (≈ANN accuracy, 4 min vs 141 min). Profile +
alignment are the dominant feature groups. Labels validated by lab sieve FI on 9
ballast bags (clean FI=2, moderate FI=22, high FI=75).

## Why it matters to us (mostly positioning, non-GPR)
- **The non-GPR competitor for the SAME target.** They hit 96 % on the same 3
  fouling levels from geometry data. But geometry senses the *mechanical
  consequence* of fouling (stiffness/settlement → profile/alignment deviations),
  only once track geometry has already degraded, at ~0.3 m resolution. **GPR's
  edge = direct subsurface sensing of the contamination itself, earlier and
  finer.** Clean justification for GPR in the thesis vs "geometry-ML already
  gets 96 %."
- **Confirms our label framework.** FI = P4 + P200 with the exact Selig bins
  (Clean <1 … Highly fouled >40); also notes the South-Korean FI=35 / No.200-only
  variant — the same two FI systems we already track. External confirmation.
- **Modest method notes:** RF ≈ ANN but ~35× faster (matches our RF choice);
  leave-one-group-out feature-category ablation as an importance method.

## Status vs our project
- **REFERENCE (positioning + label confirmation).** Non-GPR modality → **no
  waveform features transfer**, and the 96 % is NOT a target for us (their
  geometry signal is strong/low-dim/well-separated; our GPR fouling signal is
  weak/entangled). Value is thesis framing (GPR vs geometry-ML) + Selig-FI
  confirmation. Part of the SLR ballast-ML corpus, not the GPR forward/inversion
  pipeline.

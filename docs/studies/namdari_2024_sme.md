# Namdari et al. 2024 — Advancing Precision Agriculture: ML-Enhanced GPR for Root-Zone Soil Moisture (Mega Farms)

Namdari, Moradikia, Zekavat, Askari, Mangoubi, Petkie (WPI SoilX). TechRxiv
preprint 2024-04-08 (doi 10.36227/techrxiv.171259801.15539242/v1). **Full-framework
follow-on to their 2023 WiSEE descriptive-stats paper (`stats.md`)** — same group,
this one adds the whole synthetic→real ML pipeline and performance numbers.

## Why it matters to us
This is the closest published analogue to our **entire** pipeline (not just the
feature step): gprMax synthetic labeled data → feature engineering → RF →
validate/calibrate/integrate with real data. Their features are waveform-only
(descriptive stats, peaks, FFT), matching our core no-metadata constraint.
**Strong design precedent — but a fundamentally easier problem than ours.**

## Framework (4 stages)
1. **HYDRO CLAMP** synthetic generation: pick layer ε 5–21 (3 layers, 0–150 cm),
   convert to VWC via **Topp** (ε=3.03+9.3θ+146θ²−76.7θ³), generate depths; write
   .in. 150,000 sims, 1.5 GHz Ricker, 3-layer soil, air-coupled (Tx/Rx 2 m up,
   drone), **PEC reflector at max depth**, Ez extracted, 40 ns / 8100 samples.
2. **Real validation/calibration:** AKELA **SFCW** radar, 400–2000 MHz, IQ range
   bins; a **Ricker-window-in-frequency** trick reshapes SFCW spectra to match the
   gprMax Ricker → **MAE 0.05** sim-vs-real.
3. **Feature engineering + model selection:** Descriptive Stats, **ANOVA** (top-100
   by F-stat), **Peak** (count, amplitude, spacing, area-under-peaks, time-index),
   PCA. Models RF/GBR/SVR/NN. Feature sets cut dims >98%.
4. **SME + integration:** 70/15/15 split; **weighted loss** combines 30 real + synth.

## Results
- **RF best: R²=0.97**, test RMSE ~5.2 (raw). Peak feature set (5 features) gives
  the **lowest RMSE of all** — beats the raw 8100-pt A-scan.
- Integrating 30 real samples via weighted loss → only **modest** gain
  (RF test RMSE 0.93→0.92, val 1.21→1.10).
- RF: 1000 trees, max_depth 3.

## Status vs our project
- **VALIDATES** — (1) our 4-stage skeleton (synth gprMax → features → RF → real
  calibration) is a published, working design; (2) feature-based RF beats raw
  A-scan; (3) small real corpus gives only modest transfer gain (mirrors our
  Sim→Real Gap result, n≈101).
- **PENDING (cheap)** — add Peak features **area-under-peaks** + **spacing/time-index**
  (we lack these); try **ANOVA F-stat** per-class feature selection alongside RF-Gini.
  Both tie to the existing `stats.md` PENDING (Q1–Q4 quartile means on the gated coda).
- **REFERENCE / cross-link** — **Topp** ε↔θ as an empirical alternative to CRIM for
  water content (soil-specific, less physical for rock/air/water mix; don't adopt
  blindly). Weighted-loss real+synth recipe for joint training (but our real
  features were non-separable → weighting won't fix that).
- **CAUTION — their R²=0.97 does NOT transfer to us.** Their problem is easier on 4
  axes: (a) **regression** of monotonic moisture vs our overlapping fouling
  **classes**; (b) **1.5–2 GHz** (clean layer resolution) vs our 400 MHz below the
  scattering knee; (c) **PEC backstop** → artificially high SNR; (d) **no scattering
  medium** (no ballast rocks) vs our geometry-dominated coda. Cite as a pipeline
  template, not a performance target.

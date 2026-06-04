# Real GPR Data — Reusable Methodology Checklist

Lessons distilled from validating synthetic-trained models against the real
Site-1 field traces (`docs/input`, Rojas-Vivanco data). Follow this **before**
processing real traces or the large French corpus, to avoid silently invalid
results. Each item cost us a debugging cycle this session.

---

## 1. Preprocessing must be bit-for-bit identical (train vs test)

The single biggest failure: real traces came in at ~1/33 the amplitude scale of
the synthetic training data because `preprocess_signal`'s peak-normalization
(step 6, divide by `max|signal|`) was skipped on the real side. A RF that
learned absolute-amplitude thresholds then collapsed to one class.

- [ ] Same dewow / DC-removal.
- [ ] Same direct-wave handling (find direct wave, set zero, **+30 sample shift**
      per the Rojas pipeline = antenna→surface travel).
- [ ] Same bandpass (Rojas: **150–800 MHz**).
- [ ] Same coda window (cut to area of interest).
- [ ] Same **peak normalization to max|amplitude| = 1** on BOTH sides.
- [ ] (Rojas extra we skipped) **BGR background removal**, window = 1000 signals.
- [ ] Hilbert with **mirror padding** (`concat(reversed, original)`, take 2nd
      half) to kill edge artifacts — `use_mirroring=True` in our code.

## 2. Time support must match

Synthetic traces (644 samples, with direct pulse) and real `_S1` traces (250
samples, coda only) had incompatible supports → grid/slice/frequency features
became non-comparable (~483/572 features had |drift|>2 IQR — a pure artifact).

- [ ] Same number of samples / same coda window on both sides.
- [ ] Same dt (here 0.1 ns = `PC.DEFAULT_DT`; real antenna is 400 MHz).
- [ ] If lengths differ, re-window the longer side to match (see
      `build_parquet_coda_aligned.py`).

## 3. Use the correct classification bins

Rojas notebook bins are **NOT** Selig & Waters. Using Selig (1/10/20/40) on the
real FI gave a degenerate distribution (MC=1, F=72); the correct notebook bins
gave a healthy spread.

- [ ] Bins: **C 0–10, MC 10–20, MF 20–30, F 30–40, HF ≥40** (notebook cell 12),
      applied identically to synthetic and real labels.
- [ ] FI=0.4933 (and 0.4170 loose / 0.6753 compact) = the FH=0 intercept of the
      FI equation → these are **CLEAN (C)**, not missing data. Do not drop.

## 4. Match the validation method to the data's nature

- [ ] **Paired/curated data** (e.g. `df_GPR_match_filtrado`: 112 traces hand-
      matched 1:1 to FI by ID, sampled at sounding positions): score
      **per-trace**. This is legitimate; the matching is real.
- [ ] **Continuous sweep** (the field B-scan along Pk): use **block
      regularization** (`regularizar_bloques`, mode per 5 m / 20 m block, ties →
      higher class). Do NOT block-regularize a dispersed curated subset — its
      traces are spatially far apart (n_traza gaps of hundreds/thousands).
- [ ] Report **balanced accuracy** (not global accuracy) on imbalanced sets, plus
      within-±1-class for the ordinal FI scale.

## 5. Diagnose before blaming the model

Order of checks that pinned the real bottleneck (do them in this order):

1. [ ] Feature-scale drift sim vs real (median ratio per top feature). Catches
       preprocessing mismatches fast.
2. [ ] Spearman of FI vs each feature. Tells you if signal exists at all and
       **where** (here: only `median_frequency`, `mean_frequency`,
       `spectral_flatness`, ρ~0.45 — fouling attenuates high frequencies).
3. [ ] **Real-only** model via CV. If a model trained purely on reals is ≈chance,
       the data is non-separable — no feature/model/adaptation trick will help.
4. [ ] Domain adaptation (synth + few reals, CV). If B≈A, few reals are drowned
       out by the synthetic bulk.

## 6. Know what the real traces are FOR

- A single site with n≈100 is **not a trainable corpus** for 5-class fouling
  (the paper needs thousands of soundings across 4700 km).
- Real traces are best used as a **measuring stick for the simulator**: compare
  sim-vs-real feature distributions to decide which physical parameters to
  calibrate. Their value is diagnostic, not training.

---

See also: `docs/FEATURE_EXTRACTION.md`, `docs/VALIDATION.md`,
`docs/ANTENNA_CALIBRATION.md`, and scripts in `scripts/main/`
(`extract_features_real.py`, `validate_real.py`, `diagnose_real.py`,
`spearman_real.py`, `sim2real_gap.py`, `domain_adapt.py`).

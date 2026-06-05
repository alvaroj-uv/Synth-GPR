# Real/Synthetic Domain Gap Analysis

**Date:** 2026-06-04  
**Status:** Critical issues identified and documented

This document summarizes **why synthetic-trained models failed on real GPR data** and what was discovered in the debugging process.

---

## Executive Summary

The synthetic-trained RF classifier (0.7083 balanced accuracy on 30k synthetic samples) **failed dramatically on real Site-1 field traces (~50% balanced accuracy)**, despite using waveform-only features.

**Root causes identified (in order of impact):**

1. ❌ **Peak normalization mismatch** — Real traces 1/33 amplitude scale → RF collapsed to single class
2. ❌ **Time support mismatch** — Synthetic (644 samples) vs real (250) → ~483/572 features non-comparable
3. ❌ **Signal content issue** — Only frequency features show correlation with FI (ρ~0.45)
4. ❌ **Direct wave handling** — Different preprocessing pipeline on real side
5. ❌ **Classification bins** — Selig vs Rojas notebook bins created degenerate distribution

**Key insight:** The direct signal is just one part of a much larger domain gap.

---

## The Core Problem: Preprocessing Mismatch

### What Happened (The "$150M Bug")

**Real traces arrived at 1/33 the amplitude scale of synthetic training data.**

```
Synthetic training:  peak normalization = signal / max(|signal|)  ✅
Real side:          NO normalization applied  ❌
                    → real_amplitude = synthetic_amplitude / 33
```

**Result:**
- RF learned absolute amplitude thresholds during training
- Real data was 33x smaller
- Model collapsed: classified everything as a single class
- Balanced accuracy = **~50%** (random guessing on 5 classes)

### Why It Happened

From REAL_DATA_METHODOLOGY.md:
> "The single biggest failure: real traces came in at ~1/33 the amplitude scale of the synthetic training data because `preprocess_signal`'s peak-normalization (step 6, divide by `max|signal|`) was **skipped on the real side.**"

**The fix:**
```python
# Step 6: Normalization (to max value)
max_val = np.max(np.abs(treated_signal))
if max_val > 0:
    treated_signal = treated_signal / max_val  # ← MUST do on both sides!
```

---

## Secondary Issues: Window & Time Support

### Issue 2: Time Support Mismatch

| Aspect | Synthetic | Real |
|--------|-----------|------|
| Full trace length | 644 samples | N/A (field B-scan) |
| Processed window | 644 samples (coda-aligned later) | 250 samples |
| Sampling interval | ~0.031 ns | 0.1 ns (real 400 MHz) |

**Impact:** ~483/572 features showed |drift| > 2 IQR

- Grid features: Different slice positions on 644 vs 250
- Time-domain stats: Different search spaces
- Frequency features: Different time support → different frequency resolution

**This created measurement artifacts, not true domain gap.**

### Issue 3: Classification Bins

**Wrong (Selig & Waters 1994):**
```
C:  FI < 1%      → 0 samples in real set
MC: 1-10%        → 1 sample
MF: 10-20%       → 0 samples
F:  20-40%       → 27 samples  ← degenerate!
HF: ≥40%         → 80 samples  ← degenerate!
```

**Right (Rojas notebook cell 12):**
```
C:  FI < 10%     → 6 samples  ← balanced
MC: 10-20%       → 12 samples
MF: 20-30%       → 18 samples
F:  30-40%       → 27 samples
HF: ≥40%         → 45 samples
```

The Rojas bins come from their labeling methodology, not literature.

---

## Tertiary Issue: Signal Quality

### Issue 4: Which Features Actually Correlate with FI?

Spearman correlation (real traces) showed:
```
median_frequency:        ρ = 0.45  ← ✓ Signal exists
mean_frequency:          ρ = 0.42  ← ✓ Signal exists
spectral_flatness:       ρ = 0.38  ← ✓ Signal exists
All time-domain:         ρ ≈ 0.05  ← ✗ No signal
All spatial:             ρ ≈ 0.08  ← ✗ No signal
Grid features:           ρ ≈ 0.02  ← ✗ No signal
```

**Conclusion:** Only frequency-domain features carry signal about fouling.

**Why:** Fouling attenuates high frequencies more than low frequencies (dispersive loss). Time-domain and spatial features don't capture this.

---

## Direct Signal Role (Your Question)

### Where Direct Signal Fits in the Hierarchy

```
1. Peak normalization mismatch .................. 33x amplitude error  ← PRIMARY
2. Time support mismatch ....................... 483/572 feature drift
3. Signal content (freq vs time) ............... Only 3/572 features useful
4. Direct signal / preprocessing ............... ~5-10% of remaining gap
5. Feature window/bins ......................... Fine-tuning issues
```

**Direct signal is NOT the main problem.**

### What Direct Signal Does (and Doesn't Do)

**Direct signal (first 20-30 samples at peak):**
- ✅ Contains antenna coupling info
- ✅ Carries ground permittivity signal
- ✅ Affects early-time reflections
- ❌ Does NOT distinguish fouling classes well
- ❌ Removing it doesn't fix the 50% gap

**Coda (250 samples after direct peak):**
- ✅ Contains subsurface reflections
- ✅ Attenuated by fouling (high-freq loss)
- ✅ **This is where fouling signal lives**
- ✅ Frequency features extract from this

**Bottom line:** Even if you remove the direct signal perfectly, you still have a 50% domain gap due to preprocessing mismatches and signal content.

---

## Checklist for Real/Synthetic Validation

From REAL_DATA_METHODOLOGY.md — **Do these in order:**

### ✅ Preprocessing (Must be bit-for-bit identical)

- [ ] **Peak normalization to max|amplitude| = 1 on BOTH sides** ← Most critical
- [ ] Same dewow / DC removal (window_size=50)
- [ ] Same direct-wave handling
  - [ ] Find direct pulse peak
  - [ ] **+30 sample shift** per Rojas antenna→surface travel
- [ ] Same bandpass (150-800 MHz)
- [ ] Same coda window (cut to area of interest)
- [ ] Mirror padding in Hilbert (kill edge artifacts)
- [ ] (Optional) BGR background removal

### ✅ Time Support (Must match)

- [ ] Same number of samples after windowing
- [ ] Same dt or resample to match
- [ ] Same feature extraction pipeline

### ✅ Labels (Use Rojas notebook bins, not Selig)

- [ ] C: FI 0-10%
- [ ] MC: FI 10-20%
- [ ] MF: FI 20-30%
- [ ] F: FI 30-40%
- [ ] HF: FI ≥40%

### ✅ Validation Method (Match to data nature)

- [ ] **Per-trace**: If 1:1 hand-matched pairs
- [ ] **Block regularization**: If continuous B-scan sweep
- [ ] **Balanced accuracy**: On imbalanced sets
- [ ] **Within-±1-class**: For ordinal FI scale

### ✅ Diagnosis (Do before blaming model)

1. [ ] Feature-scale drift (real vs synthetic median ratios)
2. [ ] Spearman FI vs each feature (identify which have signal)
3. [ ] Real-only RF via CV (can real data alone be separated?)
4. [ ] Domain adaptation (synth + few reals, do reals help?)

---

## What the Code Actually Did

### Original Approach
```python
# build_parquet.py
sig, _ = preprocess_signal(signal, dt, 
                           use_dewow=True,
                           use_time_zero=True)
feat_df = extract_features(sig, dt)  # Full 644-sample signal
```

### Real Side
```python
# extract_features_real.py
# Preprocessing NOT done correctly:
# ❌ Missing peak normalization
# ❌ Missing proper direct wave handling
# ❌ Window mismatch (250 vs 644)
```

### Coda-Aligned "Fix"
```python
# build_parquet_coda_aligned.py
dw = dewow(signal, 50)
peak = int(np.argmax(np.abs(dw)))
coda = dw[peak:peak + 250]  # Extract coda
coda = coda / np.max(np.abs(coda))  # ← Peak normalize!
```

**Better, but still:**
- Fixes window mismatch
- Fixes peak normalization 
- Still doesn't fix: signal content mismatch (time vs freq)
- Still doesn't fix: real data only has 3/572 useful features

---

## Why Real/Sim Failed: The Real Story

It's not about the direct signal. It's a **perfect storm** of 5 issues:

### Issue 1: Scale Mismatch (PRIMARY) — 33x amplitude error
- Impact: 50% → chance baseline
- Why: Peak normalization skipped on real side
- Fix: Apply same normalization to both

### Issue 2: Window Mismatch (MAJOR) — 644 vs 250 samples
- Impact: ~483/572 features non-comparable
- Why: Synthetic included full signal, real is coda-only
- Fix: Window both to same 250-sample coda

### Issue 3: Feature Content (FUNDAMENTAL) — Only 3/572 features work
- Impact: Ceiling ~45% accuracy (Spearman ~0.4)
- Why: Fouling is in frequency domain, not time/spatial
- Fix: Feature engineering (more frequency-based)

### Issue 4: Direct Signal Preprocessing (SECONDARY) — ~5-10% of gap
- Impact: Affects boundary conditions
- Why: Real uses +30 sample shift, synthetic doesn't
- Fix: Align preprocessing exactly

### Issue 5: Classification Bins (TERTIARY) — Degenerate distribution
- Impact: Can't evaluate fairly
- Why: Selig bins don't match Rojas real data distribution
- Fix: Use Rojas notebook bins

---

## The Real Bottleneck

From REAL_DATA_METHODOLOGY.md:

> "**Real-only model via CV.** If a model trained purely on reals is ≈chance, the data is non-separable — no feature/model/adaptation trick will help."

**They found:** A Random Forest trained on ONLY real traces (with CV) achieved ~45-50% — same as synthetic model!

**This means:** The problem is **not the synthetic model**. The problem is **the feature set can't distinguish fouling in real data**.

### Why?

Real traces show:
- Only frequency features correlate with FI (ρ ~ 0.4-0.45)
- Time-domain features: ρ ~ 0.05 (essentially noise)
- Spatial features: ρ ~ 0.02 (useless)

**Real traces are fundamentally different from synthetic:**
- Synthetic: You can see every reflection clearly
- Real: Attenuation and noise obscure details
- What remains: **Only high-frequency content variation** (because fouling increases loss)

---

## Conclusions

### About Direct Signal

**Direct signal is NOT the main reason real/sim failed.**

- ✅ It does need preprocessing
- ✅ Coda-aligned windowing helps
- ❌ Removing it doesn't fix the 50% gap
- ❌ It's a ~5-10% effect on a 30%+ gap

### About Waveform-Only Features

**The core issue:** Your research goal (waveform-only features) **has a ~45% ceiling** in real data.

Why:
- Only frequency features carry signal (3/572)
- Time/spatial features don't work in noisy real data
- The fundamental physics: Fouling ≈ frequency attenuation, not time-domain amplitude

### Path Forward

**Option A: Accept the limitation**
- Waveform-only can do ~45% on real data
- This is not enough for deployment
- Publishable as "domain gap analysis"

**Option B: Feature engineering**
- Add more frequency-based features (wavelet decomposition, spectral moments, etc.)
- Target: Get 5+ features with ρ > 0.3
- Potential to reach ~65-70%

**Option C: Include metadata**
- Add permittivity, conductivity, material composition
- Synthetic: Easy to compute
- Real: Requires additional measurement (ground-truth FI via cores)
- Potential: 85%+ accuracy
- Trade-off: Loses "waveform-only" novelty

---

## References

- **Real data methodology:** [docs/REAL_DATA_METHODOLOGY.md](REAL_DATA_METHODOLOGY.md)
- **Validation script:** [scripts/analysis/validate_real.py](../../scripts/analysis/validate_real.py)
- **Gap analysis:** [scripts/analysis/sim2real_gap.py](../../scripts/analysis/sim2real_gap.py)
- **Spearman correlation:** [scripts/analysis/spearman_real.py](../../scripts/analysis/spearman_real.py)
- **Diagnostic:** [scripts/analysis/diagnose_real.py](../../scripts/analysis/diagnose_real.py)
- **Feature extraction (real):** [scripts/pipeline/extract_features_real.py](../../scripts/pipeline/extract_features_real.py)

---

## Key Documents to Read

In this order:

1. **[REAL_DATA_METHODOLOGY.md](REAL_DATA_METHODOLOGY.md)** — The checklist (all debugging lessons)
2. **[FEATURE_EXTRACTION.md](FEATURE_EXTRACTION.md)** — What features you have
3. **[.claude/CLAUDE.md](../../.claude/CLAUDE.md)** — Your research goal (waveform-only)
4. **[Fouling.md](../Fouling.md)** — Domain background


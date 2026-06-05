# Direct Signal Handling in Training Pipeline

**Date:** 2026-06-04  
**Analysis Scope:** Signal preprocessing, feature extraction, baseline model training

---

## Quick Answer

**NO — The direct signal was NOT removed in the baseline model training.**

The baseline model (0.7083 balanced accuracy on 30k samples) was trained on:
- ✅ **Full preprocessed signal** (644 samples, including direct pulse)
- ✅ **Time-zero corrected** (first break at index 0)
- ❌ **NOT truncated** to exclude direct arrival

---

## What Happened in Training

### 1. Original Baseline Pipeline

**File:** `scripts/pipeline/build_parquet.py`

```python
# Line 78-81: Preprocess full signal
sig, _ = preprocess_signal(df[ez_col].values, dt,
                           use_dewow=True,
                           use_gain=False,
                           use_time_zero=True)

# Line 87: Extract features from FULL preprocessed signal
feat_df = extract_features(pd.DataFrame({"Time": time, ez_col: sig}), dt=dt)
```

**Key Points:**
- `preprocess_signal()` returns `(treated_signal, start_idx)` 
- Code captures `sig` but **ignores `start_idx`** (the underscore means unused)
- `treated_signal` is time-zero corrected but **full length** (644 samples)
- Features extracted from entire signal (direct pulse + subsurface reflections)

### 2. What Preprocessing Does

**From src/signal_processing.py:**

```python
def preprocess_signal(signal, dt, use_dewow=True, use_gain=False, 
                      gain_params=None, use_time_zero=True):
    
    # 1. Dewow (removes DC drift)
    treated_signal = dewow(treated_signal, window_size=50)
    
    # 2. Time-Zero Correction (aligns first break to index 0)
    fb_idx = detect_first_break(treated_signal)  # Finds direct pulse peak
    if use_time_zero:
        treated_signal = time_zero_correction(treated_signal, fb_idx)
    
    # 3. Bandpass Filter (150-800 MHz)
    treated_signal = filtfilt(b, a, treated_signal)
    
    # 4. Normalization to max
    treated_signal = treated_signal / max_val
    
    # Returns: full signal (644 samples) with first break at index 0
    return treated_signal, start_idx
```

**Result:** First break is aligned to index 0, but the entire 644-sample signal is kept.

---

## Why This Matters

### Problem: Domain Mismatch

**Real GPR Data:** 250 samples of post-direct-pulse coda only
- Raw samples 61-310 in the real acquisition
- Starts at direct pulse peak
- No pre-pulse or early arrival data

**Synthetic Training Data (Baseline):** 644 samples including direct pulse
- Includes ~112 samples before and after direct pulse
- Full signal from antenna ringing through subsurface reflections
- Different time support than real data

### Impact on Features

**Time-domain features affected:**
- `grid_signal_time_*` — Position-sensitive, different window size
- `slices` — Divides signal differently (644 vs 250)
- `peak_max`, `peak_min` — Different search space
- `area_signal` — Integrates over different range

**Result:** ~483/572 features showed **|drift| > 2 IQR**, a measurement artifact rather than true domain gap.

---

## The Solution: Coda-Aligned Training

**File:** `scripts/pipeline/build_parquet_coda_aligned.py` (newer approach)

```python
def coda_window(signal: np.ndarray) -> np.ndarray:
    """Return 250 samples starting at direct-pulse peak (matches real data)."""
    
    # Step 1: Dewow
    dw = dewow(signal, 50)
    
    # Step 2: Find direct pulse peak
    peak = int(np.argmax(np.abs(dw)))
    
    # Step 3: Extract 250 samples starting at peak (mirrors real data)
    coda = dw[peak:peak + 250]
    
    # Step 4: Normalize
    m = np.max(np.abs(coda))
    if m > 0:
        coda = coda / m
    
    return coda  # 250 samples, post-direct-pulse
```

**This approach:**
- ✅ Extracts exactly the same window as real data (250 samples from direct pulse peak)
- ✅ Removes the direct pulse itself (it's at the boundary, mostly excluded)
- ✅ Includes only post-pulse coda (subsurface reflections)
- ✅ Makes synthetic and real features directly comparable

---

## Timeline: Direct Signal Handling

### Phase 1: Original Baseline (30k samples)
- **Data:** Full 644-sample signal including direct pulse
- **Model:** RF classifier, 0.7083 balanced accuracy
- **Issue:** Domain mismatch with real data (which is coda-only)
- **Status:** Published but limited real-world applicability

### Phase 2: Domain Gap Discovery
- **Finding:** 483/572 features showed drift from window size mismatch
- **Root cause:** Synthetic = 644 samples (full), Real = 250 samples (coda)
- **Realization:** Direct signal is present in synthetic but absent in real

### Phase 3: Coda-Aligned Training
- **Solution:** Window both sides to 250 samples starting at direct pulse peak
- **Dataset:** `dataset_coda_features.parquet` (synthetic, coda-aligned)
- **Benefit:** Fair comparison with real data
- **Status:** Newer approach for improved domain alignment

---

## Direct Signal in Your Waveforms

### What is the "Direct Signal"?

In GPR, when transmitter and receiver are close (bistatic antenna), the **direct signal** is:
- The first arrival (ground wave) — travels along surface or near-surface
- Peak typically at sample index ~112 in your 644-sample signal
- Dominated by antenna coupling and air propagation
- Followed by subsurface reflections (the "coda")

### In Your Data

```
Sample Index    Content
0-20            Pre-pulse ringing (antenna excitation)
20-112          Direct pulse/ground wave rise
112-130         Direct pulse peak + early subsurface
130-644         Subsurface reflections (coda)
```

### Why Include vs Exclude?

**Arguments for including (original baseline):**
- Larger signal support = more information
- Ground wave contains soil permittivity info
- Less truncation of natural signal

**Arguments for excluding (coda-aligned):**
- Matches real data window
- Real data lacks pre-pulse and direct signal
- Fair comparison with field measurements
- Removes antenna coupling effects

---

## Current State & Recommendations

### What Was Trained
- ✅ **Baseline (0.7083):** Full 644-sample signal, direct pulse included
- ✅ **Coda-aligned:** 250-sample window, direct pulse excluded

### For Future Training

**If training new models:** Use coda-aligned approach
```python
# scripts/pipeline/build_parquet_coda_aligned.py
python scripts/pipeline/build_parquet_coda_aligned.py
```

This ensures:
1. Synthetic matches real data window size
2. Features are comparable across domains
3. No measurement artifacts from window size mismatch

**If using baseline (0.7083):** Be aware of the window mismatch when:
- Comparing to real GPR accuracy
- Extracting features from field data
- Validating on Benedetto/literature benchmarks

---

## What the Code Actually Does

### Time-Zero Correction vs Direct Signal Removal

Your code distinguishes between two operations:

**1. Time-Zero Correction** (what you DO)
```python
def time_zero_correction(signal, first_break_idx):
    """Shift signal so first break is at index 0."""
    shifted[:-first_break_idx] = signal[first_break_idx:]
    return shifted  # Still full length, just shifted
```
- ✅ Aligns first break to index 0
- ❌ Does NOT remove the direct signal
- Result: First break at index 0, but signal still 644 samples

**2. Direct Signal Removal** (what you DON'T do in baseline)
```python
def remove_direct_signal(signal, keep_samples_after_peak=250):
    """Extract only post-direct-pulse coda."""
    peak = np.argmax(np.abs(signal))
    return signal[peak:peak + keep_samples_after_peak]
```
- ❌ Not in baseline pipeline
- ✅ Used in coda-aligned variant
- Result: Only 250 samples of post-direct-pulse signal

---

## Summary Table

| Aspect | Baseline (30k) | Coda-Aligned |
|--------|---|---|
| Signal length | 644 samples | 250 samples |
| Includes direct pulse | ✅ Yes | ❌ No (excluded) |
| Time-zero corrected | ✅ Yes | ✅ Yes |
| Matches real data window | ❌ No | ✅ Yes |
| Feature drift | ⚠️ High (~483 feats) | ✅ Low |
| Training dataset | dataset_*_features.parquet | dataset_coda_features.parquet |
| Baseline accuracy | 0.7083 balanced | Not yet published |

---

## References

- **Your preprocessing:** [src/signal_processing.py](../src/signal_processing.py)
- **Baseline pipeline:** [scripts/pipeline/build_parquet.py](../scripts/pipeline/build_parquet.py)
- **Coda-aligned pipeline:** [scripts/pipeline/build_parquet_coda_aligned.py](../scripts/pipeline/build_parquet_coda_aligned.py)
- **RGPR comparison:** [docs/RGPR_COMPARISON_ANALYSIS.md](RGPR_COMPARISON_ANALYSIS.md)
- **Direct signal theory:** Diamanti & Annan (2013) — [docs/studies/diamanti.md](studies/diamanti.md)


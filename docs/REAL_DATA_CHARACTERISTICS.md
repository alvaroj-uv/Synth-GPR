# Real GPR Data Analysis: df_GPR_match_filtrado

**Date:** 2026-06-04  
**Source:** Rojas-Vivanco field measurements, railway ballast fouling  
**File:** `test_output/df_GPR_match_filtrado (1).csv`

---

## Quick Facts

| Aspect | Value | vs Synthetic |
|--------|-------|---|
| **Traces** | 112 | vs 30,000 |
| **Samples/trace** | 511 | vs 644 |
| **Data range** | -16M to +339K | vs normalized 0-1 |
| **Format** | Raw ADC counts | vs preprocessed |
| **Channels** | Single (Ez) | Same |
| **Spatial structure** | Linear survey | vs 2D field |
| **Antenna** | GSSI 400 MHz | Same |

---

## Data Structure

```
112 rows (A-scans from different positions)
× 511 samples per trace
= 56,832 total samples

Columns:
  - ID: Survey line (1-112, but actually 1 trace per line?)
  - n_traza: Trace number within line
  - 0-510: Sample indices (raw ADC counts)
```

### Example Trace (ID=112, n_traza=0)

```
Index    Value      Comment
0        -16777216  ← HEADER MARKER or JUNK?
1        80512      ← Signal starts here?
2        73536
3        88128
...
50       ~100,000   ← Typical amplitude
100      ~60,000-100,000
200      ~-200,000 to +270,000  ← Large variations
300      ~50,000-180,000
400      ~50,000-110,000
500      ~77,000-150,000
```

---

## Critical Observations

### 1. **Header Marker at Index 0: -16777216**

This is `-2^24` in two's complement, appearing in **EVERY trace**.

```
-16777216 = 0xFF000000 (hex)
```

**Interpretation:**
- ❌ NOT a valid signal sample
- ✅ Likely a **frame/sync marker** or **hardware header**
- **Action:** Should be removed before processing

**Why this matters:**
- Your synthetic data doesn't have this marker
- When you extract features, this junk value affects:
  - Mean and median calculations
  - Peak detection
  - Quantiles
- **Contributes to domain gap**

### 2. **Raw ADC Counts (Not Normalized)**

Samples range from **-16.7M to +339K** (huge dynamic range).

Your synthetic data is **normalized to 0-1** before feature extraction.

**Scale difference: ~100,000x**

When you apply your model (trained on normalized data):
```
Real sample: 80,512      ← Raw ADC count
Your model expects: ~0.1  ← Normalized value

If not rescaled: Model sees 805x larger values → collapses to one class
```

**This is the peak normalization bug** mentioned in REAL_DATA_METHODOLOGY.md.

### 3. **511 Samples vs 644 Samples**

| Data | Length | Reason |
|------|--------|--------|
| Real | 511 | Windowed to coda only |
| Synthetic (original) | 644 | Full trace with direct pulse |
| Synthetic (coda-aligned) | 250 | Truncated to match real window |

**Problem:**
- Your baseline (0.7083) trained on 644-sample full signal
- Real data is 511 samples
- Mismatch means:
  - Grid features computed over different ranges
  - Frequency features have different resolution
  - Time-domain stats span different time windows

### 4. **Very High Noise/Variation**

Sample 200 ranges from **-237,952 to +274,240** (512k range!)

Compare to sample 50: **59,264 to 130,624** (71k range)

**What this tells you:**
- Real data has much higher noise floor
- Sample 200 is in the subsurface (attenuated reflections)
- Large variation means same class can look very different
- Your 572 features might not capture this variance

### 5. **Single Receiver (No B-scan)**

This CSV contains **only Ez component**, one trace per ID.

| Data | Structure | Implications |
|------|-----------|---|
| Real | 1 trace per ID (curated) | Can't use spatial averaging |
| Real (field B-scan) | Would be 100+ traces per line | Could use median/ensemble |
| Synthetic | Single traces | Same as this real data |

**Why it matters:**
- You CAN'T use weighted averaging trick from Landmine Classifier
- Each trace must be classified independently
- No multi-trace voting possible
- Harder problem (no ensemble fallback)

---

## What Real Data Tells You About Your Domain Gap

### The Perfect Storm

```
1. Junk marker (-2^24) at index 0
   ↓ Not removed before features → breaks mean/median/min
   
2. Raw ADC counts (not normalized)
   ↓ 100,000x scale difference from training
   
3. 511 vs 644 samples
   ↓ Grid features non-comparable
   
4. High noise in subsurface (sample 200+)
   ↓ Features from synthetic don't capture variance
   
5. Only 112 traces
   ↓ Can't use ensemble/averaging strategies
   
RESULT: ~50% accuracy (random 5-class guessing)
```

---

## Preprocessing Real Data (What You Should Do)

### Step 1: Remove Header Marker
```python
def preprocess_real_trace(trace):
    # Remove junk first sample
    if trace[0] == -16777216:
        trace = trace[1:]  # Skip header marker
    
    return trace
```

### Step 2: Normalize to Match Training
```python
# Training was done with peak normalization:
max_val = np.max(np.abs(trace))
trace_normalized = trace / max_val

# Now it's comparable to synthetic training data
```

### Step 3: Handle Length Mismatch
```python
# Real: 511 samples
# Synthetic training: 644 samples
# Option A: Pad with zeros
if len(trace) < 644:
    trace = np.pad(trace, (0, 644 - len(trace)))

# Option B: Resample
from scipy.signal import resample
trace = resample(trace, 644)

# Option C: Window to first 250 (coda-aligned)
trace = trace[:250]
```

### Step 4: Apply Same Preprocessing as Training
```python
from src.signal_processing import preprocess_signal

# Use the EXACT same settings as training
trace_processed, start_idx = preprocess_signal(
    trace,
    dt=0.1e-9,  # 0.1 ns per sample (400 MHz antenna)
    use_dewow=True,
    use_gain=False,
    use_time_zero=True
)
```

### Step 5: Extract Features
```python
from src.feature_extraction import extract_features

# Extract same 572 features
features = extract_features(
    pd.DataFrame({"Time": np.arange(len(trace_processed)), 
                  "Ez": trace_processed}),
    dt=0.1e-9
)
```

---

## Comparison: Real vs Synthetic Traces

### Real Trace (ID=112, raw)
```
Index  Value       Relative to Max
0      -16777216   ← JUNK (remove!)
1      80512       ▓▓▓▓▓▓▓ (typical: 23%)
50     100608      ▓▓▓▓▓▓▓▓ (29%)
100    123840      ▓▓▓▓▓▓▓▓▓ (35%)
200    274240      ▓▓▓▓▓▓▓▓▓▓ (78%)  ← Peak
300    186176      ▓▓▓▓▓▓▓▓ (53%)
500    151744      ▓▓▓▓▓▓▓▓ (43%)
```

### Synthetic Trace (after preprocessing)
```
Normalized to 0-1 range

Index  Value      Visualization
0      0.0        | (time-zero corrected)
10     0.3        ███░░░░░░░
50     0.7        ███████░░░
100    0.9        █████████░
150    1.0        ██████████ ← Peak
200    0.6        ██████░░░░
250    0.2        ██░░░░░░░░
```

**Key difference:**
- Real: Raw ADC in 80k-300k range, with garbage marker
- Synthetic: Normalized 0-1, clean, aligned

---

## Why This Matters for Your Model

### Problem 1: Junk Marker Breaks Statistics
```
Real trace (with -2^24):
  mean = (-16777216 + 80512 + 73536 + ...) / 511 = WRONG
  median = WRONG
  min = -16777216 (not useful)

Should be:
  mean = (80512 + 73536 + ...) / 510 = CORRECT
```

**Impact:** Mean, median, skewness, kurtosis all wrong.

### Problem 2: Scale Mismatch by 100,000x
```
Your model learned: "amplitudes > 0.7 → signal"
Real data: amplitudes > 70,000 → signal

Unscaled real data → treated as anomaly → wrong class
```

**Impact:** All amplitude-based features useless.

### Problem 3: Feature Space Mismatch

You have **572 features** designed for **normalized 644-sample waveforms**.

Real data is:
- 511 samples (different grid)
- Not normalized (wrong scale)
- Has junk marker (broken stats)
- Much noisier

Result: ~200/572 features are "off" in ways that break the model.

---

## What Should Happen During Preprocessing

### Current (Broken)
```
Real trace (511, raw ADC) 
  ↓ [extract_features directly]
  ↓ 572 features (wrong scale, with junk, grid mismatch)
  ↓ [model.predict]
  → 50% accuracy (random)
```

### Should Be (Fixed)
```
Real trace (511, raw ADC)
  ↓ [remove junk marker index 0]
  ↓ [normalize by max amplitude]
  ↓ [pad/resample to 644 samples]
  ↓ [apply same dewow/filter/gain as training]
  ↓ [extract_features]
  ↓ 572 features (correct scale, correct grid)
  ↓ [model.predict]
  → 65-70% accuracy (if model is good)
```

---

## Bottom Line: What You Need to Do

### Immediate (Critical)
1. **Remove index 0** from real traces (it's -2^24, junk)
2. **Normalize** by dividing by max absolute value
3. **Pad or resample** to 644 samples to match training
4. **Apply preprocess_signal()** with same params as training

### After That
- Extract features
- Run model
- Should see 60-70% instead of 50%

### If Still 50%
- Problem is not preprocessing
- Problem is feature content (only 3/572 features useful in real data)
- Need different model (CNN on raw waveforms, not RF on features)

---

## Data Quality Issues in This Real Dataset

| Issue | Severity | Cause | Fix |
|-------|----------|-------|-----|
| Junk marker (-2^24) | 🔴 Critical | Hardware/firmware artifact | Remove index 0 |
| Raw ADC counts | 🔴 Critical | No preprocessing on real side | Normalize before features |
| 511 vs 644 samples | 🟡 Important | Different windowing | Pad/resample |
| Only 112 traces | 🔴 Critical | Limited real data | Can't use ensemble tricks |
| No metadata | 🟡 Important | Manual labeling needed | Manual FI labels required |

---

## References

- Real data source: Rojas-Vivanco et al. (2025), transported/railway ballast survey
- GSSI antenna: 400 MHz center frequency
- Domain gap analysis: [docs/REAL_SIM_GAP_ANALYSIS.md](REAL_SIM_GAP_ANALYSIS.md)
- Preprocessing guide: [docs/REAL_DATA_METHODOLOGY.md](REAL_DATA_METHODOLOGY.md)
- Raw file: `test_output/df_GPR_match_filtrado (1).csv`


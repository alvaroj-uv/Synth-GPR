# Mbubia Scene Guide

**Date:** 2026-06-04  
**Reference:** Tchoua et al. (2026), Transportation Engineering  
**Document:** `docs/studies/mbubia.md`

---

## What Was Created

4 Mbubia-style synthetic gprMax scenes in `output/mbubia_scenes/`:

| Scene | Description | Layers | Upper εr | Lower εr | Notes |
|-------|-------------|--------|----------|----------|-------|
| **clean_fouled** | Clean over fouled | 2 | 4.10 | 4.23 | Small contrast |
| **fouled_subgrade** | Fouled over subgrade | 2 | 4.23 | 5.50 | Medium contrast |
| **clean_subgrade** | Clean over subgrade | 2 | 4.10 | 5.50 | Largest contrast |
| **highly_fouled** | Fouled over highly fouled | 2 | 4.23 | 4.35 | Very small contrast |

---

## Key Properties

### Domain
```
X: 4.0 m (scan direction, realistic for railway survey)
Y: 1.2 m (vertical/depth direction)
Z: 0.001 m (2D, negligible thickness)
```

### Grid Resolution
```
dx = dy = 0.002 m  (2 mm cells)
dz = 0.001 m       (negligible in 2D)
→ Total cells: 2000 × 600 × 1 = 1.2M cells
→ Computational cost: HIGH (10-20x more than your scenes)
```

### Antenna
```
Type: Hertzian dipole (point source)
Frequency: 1.4 GHz center frequency (Ricker pulse)
→ Much higher frequency than your 400 MHz
→ Shorter wavelength: λ = c/f ≈ 0.21 m in air
→ Better resolution, but less penetration
```

### Recording
```
Time window: 20 ns
Sampling: ~0.031 ns per sample
→ ~644 samples per trace (same as your synthetic!)
```

### Antenna Placement
```
Height above surface: 0.30 m (monostatic antenna)
Position: x = 2.0 m (center, for A-scan) or swept for B-scan
→ Ground-coupled antenna (direct contact with surface)
```

---

## Geometry: Realistic Rock Packing

### Unlike Your Approach
| Aspect | Your Code | Mbubia |
|--------|-----------|--------|
| **Rock shapes** | Circles (2D) or cylinders (3D) | Random polygons (6-12 sides) |
| **Packing** | Algorithm-driven (circlify, RSA, etc.) | Random polygon placement |
| **Rock count** | ~1000 per scene | ~900 (338 upper + 553 lower + lower = ~1200) |
| **Density control** | Via fill ratio parameter | Via polygon density per layer |
| **Material variation** | Single material per layer | Two distinct materials (clean vs fouled) |

### Example Geometry (Clean-Fouled)
```
Layer 1 (Fouled): 0.0 - 0.488 m
  - Material: bal_foul_granular (εr=4.23, σ=0.005)
  - 553 random polygons
  - Represents void-filled fines

Layer 2 (Clean): 0.488 - 0.8 m
  - Material: bal_rock_L1 (εr=4.10, σ=0.001)
  - 338 random polygons
  - Represents clean ballast

Interface: Flat at y = 0.488 m (clean layer boundary)
```

---

## Why Mbubia Matters for Your Research

### 1. **Validates Stratigraphy Detection**
Your task: Detect fouling from waveforms  
Mbubia task: Detect **layer interfaces** from B-scans (Mask R-CNN)

**Complementary:** You classify a homogeneous layer as clean/fouled. Mbubia can detect *where* the layer boundary is.

### 2. **Tests Different Frequency**
- Your 400 MHz: Lower frequency, deeper penetration
- Mbubia 1.4 GHz: Higher frequency, better resolution

**Question:** Do fouling-detection features work across frequencies?

### 3. **Uses Realistic Rock Geometry**
Your cylinders/circles: Simplified, computationally cheap  
Mbubia polygons: Realistic, scattering-rich, closer to real rocks

**Question:** Does your RF model overfit to cylindrical rocks?

### 4. **Two-Layer Stratigraphy**
Your scenes: Mostly single fouled/clean layer  
Mbubia: Clear layer boundary, tests interface separation

**Question:** Can you separate signals from different layers?

---

## Running Mbubia Simulations

### Prerequisites
```bash
# Check if gprMax is installed
python -c "import gprMax; print(gprMax.__version__)"

# If missing:
pip install gprMax
```

### Run Simulation
```bash
# Single simulation
python -m gprMax output/mbubia_scenes/mbubia_clean_fouled.in

# Results in:
# output/mbubia_scenes/mbubia_clean_fouled.out (HDF5)
```

### Expected Output
```
Input file: ~700 KB
Simulation time: 5-15 minutes per scene (1.2M cells)
Output file: ~50-100 MB (B-scan format)
```

### Extract Features
```bash
# Same as your pipeline
python scripts/pipeline/extract_features.py output/mbubia_scenes
# → output/mbubia_features.csv (572 features per A-scan)
```

---

## Analysis: Compare Mbubia vs Your Synthetic

### Metadata Comparison

**Your synthetic (30k samples):**
```
Domain: 0.6 × 0.5 m (smaller)
Frequency: 400 MHz (lower)
Rocks: Cylinders/circles (simplified)
Layers: Single fouled/clean layer
Features: 572 waveform features
Baseline: 0.7083 balanced accuracy on synthetic
```

**Mbubia scenes (4 samples):**
```
Domain: 4.0 × 1.2 m (larger, realistic)
Frequency: 1.4 GHz (higher)
Rocks: Random polygons (realistic)
Layers: Two distinct layers with interface
Features: Same 572 (if we extract them)
Baseline: N/A (not yet tested)
```

### What Should Match?
```
A-scan length: 644 samples ✓ (same time window)
Sample interval: ~0.031 ns ✓ (same Δt)
Frequency band: Different (400 vs 1.4 GHz)
Rock geometry: Different (cylinders vs polygons)
Stratigraphy: Different (single vs two layers)
```

### What's Different?
```
Antenna frequency: 3.5× higher (1.4 vs 0.4 GHz)
Domain size: 6.7× larger (4 vs 0.6 m X, 2.4× larger Y)
Rock count: Similar (~900 vs ~1000)
Grid cells: ~1.2M vs ~360k (3.3× more cells)
```

---

## Feature Extraction from Mbubia

### Expected Issues
1. **Frequency mismatch:** Your RF was trained on 400 MHz data, Mbubia is 1.4 GHz
   - Frequency-domain features will be shifted
   - Time-domain features might transfer better

2. **Rock geometry:** Polygons vs cylinders
   - Scattering patterns different
   - Could affect amplitude/envelope features

3. **Layer interface:** Two-layer geometry
   - Strong reflection at interface
   - Could create peaks not seen in single-layer synthetic

### What to Extract
```python
# Same feature extraction pipeline
from src.feature_extraction import extract_features

# Expect: 
#   - Peak at interface boundary (y ≈ 0.488 m)
#   - Two distinct frequency signatures (one per layer)
#   - Higher-amplitude returns (1.4 GHz scatters more)
```

---

## Validation Path

### Step 1: Simulate Mbubia Scenes
```bash
for file in output/mbubia_scenes/*.in; do
    python -m gprMax "$file"
done
```

### Step 2: Extract Features
```bash
python scripts/pipeline/extract_features.py output/mbubia_scenes \
    --output output/mbubia_features.csv
```

### Step 3: Classify with Your RF
```python
import joblib
import pandas as pd

# Load trained model
rf = joblib.load('output/rf_model_waveform_only.joblib')

# Load Mbubia features
mbubia = pd.read_csv('output/mbubia_features.csv')

# Predict
predictions = rf.predict(mbubia.iloc[:, 1:])  # Skip ID column

# Analyze
print(f"Predictions: {pd.Series(predictions).value_counts()}")
# Expected: Some class imbalance due to two-layer geometry
```

### Step 4: Analyze Results
```
Question: Does RF trained on 400 MHz work on 1.4 GHz data?
Expected: Lower accuracy (domain gap)

Question: Can RF separate clean from fouled in two-layer scene?
Expected: Interference from interface reflection

Question: Which features are most useful?
Expected: Frequency-domain features may shift, time-domain may be more robust
```

---

## Paper Summary (Tchoua et al. 2026)

**Title:** "GPR and AI for Automated Railway Trackbed Stratigraphy and Fouling Assessment"

**Key Methods:**
1. **Mask R-CNN:** Detect layer interfaces in B-scans (instance segmentation)
2. **XGBoost/SVR:** Estimate permittivity and thickness from A-scans
3. **Rb-f index:** Convert permittivity to fouling level

**Results:**
- Interface detection: IoU ≈ 0.81 (good)
- Permittivity estimation: R² > 0.9 (excellent)
- Real field data: Robust transfer from synthetic to field

**Relevance to Your Work:**
- Shows **hybrid approach** (image + signal) works better than waveform-only
- Demonstrates **domain gap is surmountable** with proper design
- Validates **synthetic training + real deployment** feasibility

---

## Next Actions

### If gprMax Available:
```bash
# Simulate all Mbubia scenes
python -m gprMax output/mbubia_scenes/*.in

# Extract features and test with your RF
python scripts/pipeline/extract_features.py output/mbubia_scenes
```

### If gprMax Not Available:
```bash
# Install it
pip install gprMax

# Or use alternative:
# Copy features manually from simulation logs
```

### Comparative Analysis:
Compare accuracy on:
1. Your synthetic (400 MHz, single layer)
2. Mbubia (1.4 GHz, two layers)
3. Real field data (~400 MHz, unknown stratigraphy)

**Goal:** Understand where domain gap comes from (frequency? geometry? stratigraphy?)

---

## References

- **Mbubia Tchoua et al. (2026):** https://doi.org/10.1016/j.treng.2025.100415
- **Your paper notes:** `docs/studies/mbubia.md`
- **Generated scenes:** `output/mbubia_scenes/`


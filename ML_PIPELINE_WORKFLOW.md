# ML Data Pipeline Workflow

## Overview
This document describes the complete workflow from scene generation to ML-ready feature dataset.

## Workflow Steps

### **Step 1: Generate .in Files** (Scene Generation)
```bash
python scripts/main/generate_dataset.py output/ml_batch1 \
  --labels C MC MF F HF \
  -n 100 \
  --start_id 1000
```

**Output**:
- `output/ml_batch1/s1000.in` to `s1499.in` (500 files total)
- `output/ml_batch1/metadata.csv` with columns: `[sample_id, FI_class, pvc, moisture, ...]`

---

### **Step 2: Run gprMax Simulations** (Manual/External)
```bash
# Navigate to output directory
cd output/ml_batch1

# Run gprMax on all .in files (example command - adjust for your setup)
for file in *.in; do
    python -m gprMax "$file" --gpu
done
```

**Output**:
- `s1000.out` to `s1499.out` (HDF5 format with signal data)

---

### **Step 2.5: Verify Output (Recommended)**
```bash
# Visualize blueprint + signal for quality check
visualize_all_test.bat
# Output: sXXXX.png (Side-by-side Geometry + A-scan)
```

---

### **Step 3: Extract Features** (Signal Processing → ML Features)
```bash
python scripts/main/extract_features.py output/ml_batch1 \
  --output feature_dataset.csv
```

**What it does**:
1. Reads `metadata.csv` (labels: FI_class)
2. Loads each `.out` file (GPR signals) using `src/data_loader.py`
3. Extracts 500+ features using `src/feature_extraction.py`
4. Consolidates into `feature_dataset.csv`

**Output**:
- `output/ml_batch1/feature_dataset.csv`
- Columns: `[sample_id, FI_class, mean, rms, skewness, ..., grid_15_9]` (502+ columns)

---

### **Step 4: Train ML Model** (Your Existing Pipeline)
```python
import pandas as pd
from sklearn.ensemble import RandomForestClassifier

# Load feature dataset
df = pd.read_csv('output/ml_batch1/feature_dataset.csv')

# Separate features and labels
X = df.drop(['sample_id', 'FI_class'], axis=1)
y = df['FI_class']

# Train model
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X, y)
```

---

## Complete Example

```bash
# 1. Generate 1000 samples across all classes
python scripts/main/generate_dataset.py output/dataset_v1 \
  --labels C MC MF F HF \
  -n 200 \
  --start_id 0

# 2. Run gprMax (manually or via batch script)
cd output/dataset_v1
# ... run gprMax on all .in files ...

# 3. Extract features
python scripts/main/extract_features.py output/dataset_v1

# 4. Result: feature_dataset.csv ready for ML training!
```

---

## Feature Types Extracted (500+ Features)

### Time-Domain (50+ features)
- Statistical: mean, RMS, std, skewness, kurtosis
- Quantiles: 25th, 50th, 75th percentiles
- Deciles: 10%, 20%, ..., 90%
- Signal properties: zero crossings, peak values, crest factor

### Frequency-Domain (20+ features)
- FFT spectrum: area, peak
- Spectral properties: dominant freq, bandwidth, centroid
- Spectral entropy, flatness

### Hilbert Transform (50+ features)
- Envelope statistics: mean, RMS, std, skew, kurtosis
- Envelope quantiles and deciles

### Time-Frequency (STFT) (10+ features)
- Energy in frequency bands (low/mid/high)
- Spectral centroid variance

### Spatial Features (400+ features)
- 14 slice statistics (28 features)
- 16x10 grid features (480 features):
  - Signal amplitude
  - Hilbert envelope
  - Imaginary Hilbert

---

## File Structure

```
output/ml_batch1/
├── s1000.in         # gprMax input (scene definition)
├── s1000.out        # gprMax output (GPR signal, HDF5)
├── s1001.in
├── s1001.out
├── ...
├── metadata.csv      # Labels and parameters
└── feature_dataset.csv  # ML-ready features
```

---

## Tips

1. **Parallel gprMax**: Use GNU Parallel or Python multiprocessing to run simulations in parallel
2. **GPU Acceleration**: Add `--gpu` flag to gprMax for faster simulations
3. **Batch Processing**: Generate and simulate in batches to manage memory
4. **Quality Control**: Check for missing .out files before feature extraction
5. **Feature Selection**: Use correlation analysis to remove redundant features

---

## Troubleshooting

**Missing .out files**: The extract_features script will skip and warn about missing files

**Memory issues**: Process in smaller batches (e.g., 100 samples at a time)

**HDF5 errors**: Ensure gprMax completed successfully - check .out file size

**Feature extraction failure**: Check that .out file contains expected fields (Ez, Hx, etc.)

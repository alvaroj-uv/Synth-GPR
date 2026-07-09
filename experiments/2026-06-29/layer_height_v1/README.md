# Experiment: Layer-Height Synthetic Dataset v1

**Date:** 2026-06-29  
**Goal:** Generate synthetic GPR training data for sim→real layer depth regression.

## Motivation

Real pandoscope data (112 labeled pits, `D:/Codigo/Data_Labled`) provides:
- `Prof_BS` (clean ballast bottom depth): 0.26–0.79 m
- `Prof_BC` (total ballast depth): 0.38–1.08 m

The target is to train an RF/XGBoost regressor on **synthetic** gprMax traces
and evaluate it on the 112 real labeled traces, using Prof_BS and Prof_BC as
ground truth. This avoids the FI conversion ambiguity and tests clean sim→real
transfer with a direct geometric label.

## Dataset Design

**Parameter grid (regular):**
- Fouled ballast thickness: 0, 5, 10, 15, 20, 25, 30, 35, 40 cm (9 levels)
- Clean ballast thickness: 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75 cm (11 levels)
- Total samples: 99

**Material properties:**
- Clean ballast: eps=3.45, sigma=0.0 (Benedetto 2017 validated)
- Subgrade: eps=10.0, sigma=0.01 (fixed)
- **Fouled ballast eps: sampled Uniform(4.0, 11.0) per simulation** (seed=42)
  - Covers FI~5% (eps=4) through FI~47% (eps=11, pit ID11 calibrated)
  - Makes regressor robust to unknown fouling level at test time

**Layer stack (top → bottom):**
```
[antenna @ 10 cm clearance]
fouled_ballast   eps~U(4,11)  sigma=0.05   (thickness=0 for clean cases)
clean_ballast    eps=3.45     sigma=0.0
subgrade         eps=10.0     sigma=0.01   (fixed 50 cm)
```

**Simulation params:**
- 420 MHz Gaussian bistatic 30 mm (validated from DEFAULT.toml)
- Domain: 50 cm wide, 2D FDTD
- Time window: 50 ns (matches real GSSI DZT)

## Labels

`metadata.csv` columns:
| Column | Description |
|---|---|
| `sample_id` | 1–99 |
| `in_file` | filename of .in file |
| `fouled_m` | fouled layer thickness (m) — analog of Prof_BC − Prof_BS |
| `clean_m` | clean layer thickness (m) — analog of Prof_BS |
| `total_m` | total ballast depth (m) = fouled_m + clean_m — analog of Prof_BC |
| `eps_fouled` | permittivity of fouled layer (sampled) |

## File List

| File | Status |
|---|---|
| `generate_layer_height_dataset.py` (in scripts/pipeline/) | Script |
| `metadata.csv` | Labels |
| `sample_0001.in` … `sample_0099.in` | gprMax input files |
| `sample_0001.out` … `sample_0099.out` | gprMax output (pending) |
| `feature_dataset.csv` | Extracted features (pending) |

## Pipeline

```bash
# 1. Generate .in files (done)
python scripts/pipeline/generate_layer_height_dataset.py \
    --out experiments/2026-06-29/layer_height_v1

# 2. Run FDTD for each .in file
cd experiments/2026-06-29/layer_height_v1
# In conda gprMax env:
for f in sample_*.in; do python -m gprMax "$f"; done

# 3. Extract features + build training CSV
python scripts/pipeline/extract_features_layer_height.py \
    experiments/2026-06-29/layer_height_v1

# 4. Train RF/XGBoost regressor
# Target: clean_m (Prof_BS) and/or total_m (Prof_BC)
# Evaluate: Spearman corr + MAE on 112 real pandoscope traces
```

## Expected Results

- RF should learn the relationship: deeper reflector → later coda peak
- Key features expected to drive prediction: `att_band_mid_decay`, `coda_grid_*`, reflection peak timing
- Real evaluation against Prof_BS/Prof_BC will quantify sim→real transfer quality

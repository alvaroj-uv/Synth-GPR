# Dataset Structure Analysis for RF Training

## Overview
- **Total Samples**: 80,000
  - `output/gpr_dataset_10k`: 50,000 samples
  - `output/dataset_variants`: 30,000 samples

Each sample consists of:
- `.in` file: Text metadata (simulation parameters)
- `.out` file: HDF5 binary file (simulation output with Ez field data)

---

## INDEPENDENT VARIABLES (Features)

### Dataset: `gpr_dataset_10k`

**Numerical Parameters from .in file headers:**

| # | Attribute | Type | Purpose |
|---|-----------|------|---------|
| 1 | `pvc` | Float | PVC (polyvinyl chloride) content |
| 2 | `moisture` | Float | Moisture content |
| 3 | `achieved_density` | Float | Actual density achieved |
| 4 | `porosity` | Float | Porosity ratio |
| 5 | `Lab_FI` | Float | Lab Fouling Index |
| 6 | `Lab_FI_local` | Float | Lab FI local measurement |
| 7 | `Lab_FR` | Float | Lab Fouling Ratio |
| 8 | `Lab_er_bulk_leng` | Float | Bulk relative permittivity (length) |
| 9 | `Lab_bulk_eps` | Float | Bulk epsilon (permittivity) |
| 10 | `Lab_alpha_400MHz_npm` | Float | Attenuation @ 400 MHz (nepers/meter) |
| 11 | `Lab_alpha_2GHz_npm` | Float | Attenuation @ 2 GHz (nepers/meter) |
| 12 | `Lab_surface_R` | Float | Surface reflectance |
| 13 | `Lab_LDCP_FI_est` | Float | LDCP-estimated FI |
| 14 | `Lab_LDCP_FH` | Float | LDCP FH measurement |
| 15 | `Lab_LDCP_qs_mean` | Float | LDCP mean quality factor |
| 16 | `Lab_clean_ballast_mm` | Float | Clean ballast thickness (mm) |
| 17 | `mc_rock_fraction` | Float | Material composition: rock fraction |
| 18 | `mc_fouling_fraction` | Float | Material composition: fouling fraction |
| 19 | `mc_subgrade_fraction` | Float | Material composition: subgrade fraction |
| 20 | `mc_formation_fraction` | Float | Material composition: formation fraction |
| 21 | `mc_void_fraction` | Float | Material composition: void fraction |
| 22 | `mc_pvc_measured` | Float | Material composition: PVC measured |
| 23 | `ballast_top_y` | Float | Ballast top Y coordinate |
| 24 | `ballast_bottom_y` | Float | Ballast bottom Y coordinate |
| 25 | `mc_y_max` | Float | Material composition max Y |
| 26 | `mc_y_min` | Float | Material composition min Y |
| 27 | `mc_y_local_max` | Float | Material composition local max Y |
| 28 | `ldcp_x` | Float | LDCP X coordinate |
| 29 | `Base Seed` | Integer | Random seed for simulation |

**Metadata (not used as features):**
- `Scenario`: "Sim" (all simulation)
- `Date`: Generation date
- `Git Version`: Code version
- `FI_class`: Class version (derived from Lab_Class)

---

### Dataset: `dataset_variants`

**Extended parameters (all of above PLUS):**

| # | Attribute | Type | Purpose |
|---|-----------|------|---------|
| 1-28 | *(same as gpr_dataset_10k)* |
| 29 | `Lab_P4` | Float | Particle size @ #4 sieve |
| 30 | `Lab_P200` | Float | Particle size @ #200 sieve |
| 31 | `Lab_Porosity` | Float | Measured porosity |
| 32 | `Lab_PSD` | List | Particle size distribution (array) |
| 33 | `Lab_delta_frac_detectable` | Float | Detectable delta fraction |
| 34 | `Lab_delta_max` | Float | Maximum delta |
| 35 | `Lab_delta_min` | Float | Minimum delta |

**Configuration Parameters (metadata, can be used for stratification):**
- `Antenna`: "1 RX @ 0.05m spacing"
- `Frequency`: "400 MHz"
- `Rock Shape`: "Angular (6-sided)"
- `Packing`: "shang_chu (uniform PSD)"
- `CONFIG_*`: Various configuration parameters (moisture, PVC sampled, etc.)

---

## DEPENDENT VARIABLE (Target/Label)

**Source**: `Lab_Class` from .in file headers

**Classification Classes** (Fouling Severity - 5 classes):
1. **C** - Clean (no fouling)
2. **MC** - Moderately Clean
3. **MF** - Moderately Fouled
4. **F** - Fouled
5. **HF** - Highly Fouled

---

## HDF5 OUTPUT FILES (.out)

### Structure
- **Format**: HDF5 binary
- **Top-level Group**: `/rxs/` (receivers)
  - Contains time-series Ez field data for each receiver
  - Data: Electric field Z-component measurements
  - Can be downsampled or processed into statistical features

### Possible Feature Extraction from Ez:
- Mean, std, min, max of Ez field
- Energy/power metrics
- Frequency domain features (via FFT)
- Wavelet coefficients
- Time-domain statistics

---

## Data Split Strategy

### Training Setup
- **Training Samples**: ~64,000 (80%)
- **Test Samples**: ~16,000 (20%)
- **Stratification**: By `Lab_Class` to maintain class distribution

### Class Distribution
Expected distribution (from samples):
- Balanced to slightly imbalanced (varies by dataset)
- Use `class_weight='balanced'` in RF to handle any imbalance

---

## Feature Engineering Pipeline

1. **Load .in metadata** → Extract 28-35 numerical parameters
2. **Load .out HDF5** → Extract Ez field features (time-series → statistics)
3. **Combine features** → Single feature vector per sample
4. **Normalize** (optional) → StandardScaler or similar
5. **Train RF** → RandomForestClassifier on combined features
6. **Evaluate** → Classification report, confusion matrix, feature importances

---

## Notes

- Both datasets use same `.in` file format but with different parameter ranges
- `dataset_variants` is enriched with additional laboratory measurements
- `.out` files contain simulation-based Ez field data (electromagnetic response)
- Total feature dimension: 28-35+ (depending on Ez extraction method)
- 80,000 samples is sufficient for robust RF training with 5-class problem

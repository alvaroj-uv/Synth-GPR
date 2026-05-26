# SynthGPR — Dataset & Pipeline Documentation

## 1. Project Overview

Synth-GPR generates synthetic Ground Penetrating Radar (GPR) data for railway ballast fouling
classification. It combines gprMax electromagnetic (FDTD) simulations with signal feature
extraction to produce ML-ready datasets.

The goal is to classify ballast fouling level into 5 categories based on the received GPR
A-scan waveform.

---

## 2. Fouling Classes

| Class | Label | Description |
|-------|-------|-------------|
| C     | Clean | No fouling material in voids |
| MC    | Moderately Clean | Minimal fouling |
| MF    | Mixed Fouling | Partial void contamination |
| F     | Fouled | Significant fouling |
| HF    | Highly Fouled | Voids mostly filled with fines |

Fouling is parameterized by:
- **PVC** (Percentage Void Contamination): volume fraction of voids filled by fouling material
- **Moisture**: moisture content of the fouling material (0–100%)

---

## 3. Data Pipeline

```
.in file  ──►  gprMax FDTD simulation  ──►  .out file  ──►  feature extraction  ──►  parquet
(geometry,      (runs on GPU)               (HDF5,           (500+ features)          (ML dataset)
 materials,                                  EM wave)
 config)
```

### 3.1 Input Files (.in)

gprMax input files located in `output/gpr_dataset_10k/` (e.g. `s_00000.in`).

Each file has two sections:

#### Header Block (## comments) — Scenario Metadata

All variables appear as `## key: value` lines at the top of the file.

| Variable | Description |
|----------|-------------|
| `pvc` | Percentage Void Contamination (input parameter) |
| `moisture` | Moisture content of fouling material |
| `achieved_density` | Actual packing density after rock placement |
| `porosity` | 1 - achieved_density |
| `FI_class` | Fouling Index class label: C / MC / MF / F / HF |
| `Lab_FI` | Fouling Index (global, length-averaged) |
| `Lab_FI_local` | Fouling Index (local, near measurement point) |
| `Lab_Class` | Alternative class label derived from Lab_FI |
| `Lab_FR` | Fouling Ratio |
| `Lab_er_bulk_leng` | Bulk dielectric permittivity (length-averaged) |
| `Lab_bulk_eps` | Bulk permittivity at the LDCP point |
| `Lab_surface_R` | Surface reflectivity coefficient |
| `Lab_alpha_400MHz_npm` | Attenuation at 400 MHz (Np/m) |
| `Lab_alpha_2GHz_npm` | Attenuation at 2 GHz (Np/m) |
| `Lab_clean_ballast_mm` | Thickness of clean ballast above fouling (mm) |
| `mc_rock_fraction` | Volume fraction occupied by rocks |
| `mc_fouling_fraction` | Volume fraction occupied by fouling material |
| `mc_subgrade_fraction` | Volume fraction occupied by subgrade |
| `mc_formation_fraction` | Volume fraction occupied by formation layer |
| `mc_void_fraction` | Volume fraction of empty voids |
| `mc_pvc_measured` | Measured PVC (may differ from input pvc) |
| `mc_y_min` | Bottom Y coordinate of ballast region (m) |
| `mc_y_max` | Top Y coordinate of ballast region (m) |
| `mc_y_local_max` | Local top Y (used for local FI calculation) |
| `ballast_bottom_y` | Y coordinate of ballast base layer |
| `ballast_top_y` | Y coordinate of ballast surface |
| `ldcp_x` | X position of the LDCP measurement point |
| `Lab_LDCP_FH` | LDCP Fouling Height |
| `Lab_LDCP_FI_est` | LDCP estimated Fouling Index |
| `Lab_LDCP_qs_mean` | LDCP mean scattering parameter |

#### gprMax Configuration Block

| Command | Example | Meaning |
|---------|---------|---------|
| `#domain` | `2.248 3.199 0.0132` | Simulation domain (x y z) in metres |
| `#dx_dy_dz` | `0.0132 0.0132 0.0132` | Cell size — 13.2 mm (λ/10 at 400 MHz) |
| `#time_window` | `2e-08` | Simulation duration: 20 ns |
| `#pml_cells` | `10 10 0 10 10 0` | Absorbing boundary thickness (cells) |
| `#waveform` | `ricker 1 4e+08 ricker_src` | Ricker wavelet source at 400 MHz |
| `#hertzian_dipole` | `z x y z name` | Transmitter antenna position |
| `#rx` | `x y z` | Receiver antenna position (offset +0.05 m in x) |
| `#material` | `er sigma 1 0 name` | Dielectric material definition |

#### Materials

| Name | er (typical) | Notes |
|------|-------------|-------|
| `subgrade` | 10 | Bottom soil layer |
| `formation` | 10 | Transition layer above subgrade |
| `bal_rock` | 5 | Clean ballast aggregate |
| `bal_foul_granular` | varies | Fouling mix — er depends on pvc + moisture |

#### Geometry Block

Defines spatial layout using gprMax primitives:
- `#box` — rectangular regions (free space, subgrade, formation)
- `#triangle` — triangulated angular rock aggregates (Shang-Chu packing)

---

### 3.2 Output Files (.out)

HDF5 binary files produced by gprMax after FDTD simulation (e.g. `s_00000.out`, ~27 KB each).

Content: the Ez (vertical electric field) component of the electromagnetic wave recorded at the
receiver antenna over time. This is the GPR A-scan — a time series representing the reflected
wave that returns from subsurface interfaces and scatterers.

The shape of this waveform changes depending on fouling level:
- **Clean ballast**: distinct reflection pulses from air-ballast and ballast-subgrade interfaces
- **Fouled ballast**: attenuated, dispersed, smeared waveform (fines absorb high frequencies
  and homogenize the medium, reducing scattering contrast)

---

### 3.3 Feature Extraction

All signal features are extracted from the .out file Ez waveform. Features are grouped as:

#### Time-Domain Statistics (applied to raw Ez signal)
`mean`, `root_mean_square`, `standard_deviation`, `median`, `skewness`, `kurtosis_value`,
`percentile_25/50/75`, `peak_max`, `peak_min`, `crest_factor`, `number_zeros`, `area_signal`,
`second_derivative`, `decile_10` through `decile_90`

#### Hilbert Envelope Statistics (applied to instantaneous amplitude)
Same set as time-domain, prefixed with `hilbert_`: `hilbert_mean`, `hilbert_root_mean_square`,
etc. Also includes `area_hilbert`.

The Hilbert envelope captures pulse energy independent of phase. Fouled ballast produces a
wider, lower-amplitude envelope due to scattering and attenuation.

#### Frequency Domain (FFT)
`area_fourier`, `fourier_peak_max`, `dominant_frequency`, `bandwidth`, `mean_frequency`,
`median_frequency`, `spectral_entropy`, `spectral_flatness`

Fouling attenuates high frequencies → dominant frequency shifts down, bandwidth narrows,
spectral entropy changes.

#### Time-Frequency (STFT)
Energy in three depth bands:
- Low (< 500 MHz): `stft_energy_low_mean`, `stft_energy_low_max`
- Mid (500–1500 MHz): `stft_energy_mid_mean`, `stft_energy_mid_max`
- High (> 1500 MHz): `stft_energy_high_mean`, `stft_energy_high_max`
- `stft_centroid_std`: temporal variation of spectral centroid

#### Slice Statistics (14 time slices)
Signal divided into 14 equal segments. For each slice i (0–13):
`stat_slice_i_mean`, `stat_slice_i_std`

Early slices (0–3) correspond to shallow reflections (ballast surface); late slices to deeper
interfaces. Std deviation distinguishes rough clean ballast from smooth fouled ballast.

#### Grid Features (16×10 spatial-temporal grid)
Signal resampled to 160 points, arranged as 16 rows × 10 columns. Three channels extracted
at each of the 160 grid points:
- `grid_signal_time_i_j`: raw amplitude
- `grid_hilbert_envelope_i_j`: envelope amplitude
- `grid_hilbert_imag_i_j`: imaginary part of analytic signal

Total: 160 × 3 = 480 grid features.

---

## 4. Training Dataset

**File**: `parquet/training_dataset_10k.parquet`
**Source**: `output/gpr_dataset_10k/` (.in and .out file pairs)
**Shape**: 50,000 rows × 612 columns

### Column Groups

| Group | Count | Source |
|-------|-------|--------|
| Signal component label (`Signal`) | 1 | .out metadata |
| Time-domain stats | ~25 | .out Ez waveform |
| Hilbert envelope stats | ~25 | .out Ez waveform |
| Fourier features | 8 | .out Ez waveform |
| STFT features | 7 | .out Ez waveform |
| Slice stats | 28 | .out Ez waveform |
| Grid features | 480 | .out Ez waveform |
| Scenario metadata | ~35 | .in header |

### Target Labels

| Column | Type | Classes |
|--------|------|---------|
| `FI_class` | Primary label | C, MC, MF, F, HF |
| `Lab_Class` | Alternative label | C, MC, MF, F, HF (different distribution) |
| `Lab_FI` | Continuous FI | 0.0 – 1.0 |
| `Lab_FI_local` | Local continuous FI | 0.0 – 1.0 |

### Class Distribution (FI_class)

| Class | Count |
|-------|-------|
| F     | 11,715 |
| MC    | 11,101 |
| C     | 10,566 |
| MF    |  8,403 |
| HF    |  8,215 |

---

## 5. Key Physics Parameters

- **Antenna frequency**: 400 MHz (Ricker wavelet)
- **Antenna separation**: 0.05 m (TX–RX offset)
- **Cell size**: 0.0132 m = 13.2 mm (λ/10 rule)
- **Time window**: 20 ns
- **PML boundary**: 10 cells on x/y faces
- **Ballast layer**: ~0.3–0.68 m depth depending on scenario
- **Rock packing**: Shang-Chu angular aggregate algorithm (zero overlaps, ~43% void ratio)
- **Fouling material permittivity**: computed from pvc + moisture via mixing formula

---

## 6. Notes

- The `Signal` column contains the string `"Ez"` (field component name), not numeric data.
- Parquet files are excluded from git (`.gitignore`). Dataset is local only.
- Python environment: `C:\Users\barba\miniconda3\python.exe`
- gprMax simulations were run on GPU (`run_simulations_gpu.bat`).

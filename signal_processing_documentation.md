# Synth-GPR Signal Processing System Documentation

## Overview

The Synth-GPR signal processing system implements a comprehensive pipeline for GPR data analysis, specifically optimized for railway ballast fouling detection. The system follows published methodologies and provides both individual processing functions and complete workflows.

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                   SIGNAL PROCESSING SYSTEM ARCHITECTURE                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │                        signal_processing.py (Facade)                    │  │
│  │                                                                         │  │
│  │  ┌─────────────────┐       ┌─────────────────┐       ┌─────────────┐  │  │
│  │  │                 │       │                 │       │             │  │  │
│  │  │  preprocessing  │       │  vivanco_pipel  │       │  spectral_  │  │  │
│  │  │  .py            │       │  ine.py         │       │  attributes │  │  │
│  │  │  (Basic ops)    │       │  (Complete      │       │  .py        │  │  │
│  │  │                 │       │   workflows)    │       │  (Advanced │  │  │
│  │  └─────────────────┘       └─────────────────┘       │  analysis)  │  │  │
│  │                                                      └─────────────┘  │  │
│  │                                                                         │  │
│  │  ┌─────────────────┐       ┌─────────────────┐       ┌─────────────┐  │  │
│  │  │                 │       │                 │       │             │  │  │
│  │  │  bscan_process  │       │  reflector_pick │       │  coda_objec │  │  │
│  │  │  ing.py         │       │  ing.py         │       │  tives.py  │  │  │
│  │  │  (2D processing)│       │  (Reflector     │       │  (Coda     │  │  │
│  │  │                 │       │   analysis)     │       │  analysis) │  │  │
│  │  └─────────────────┘       └─────────────────┘       └─────────────┘  │  │
│  └─────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │                        SUPPORTING MODULES                               │  │
│  │                                                                         │  │
│  │  ┌─────────────────┐       ┌─────────────────┐       ┌─────────────┐  │  │
│  │  │                 │       │                 │       │             │  │  │
│  │  │  dzt_io.py      │       │  constants.py  │       │  physics.py │  │  │
│  │  │  (Data I/O)     │       │  (Parameters)   │       │  (Physics  │  │  │
│  │  └─────────────────┘       └─────────────────┘       │  utils)    │  │  │
│  │                                                      └─────────────┘  │  │
│  └─────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Module Structure

### 1. Core Modules

#### signal_processing.py (Facade)
- **Purpose**: Main entry point and facade pattern implementation
- **Role**: Provides unified access to all signal processing functions
- **Pattern**: Facade pattern - delegates to specialized submodules
- **Status**: Split into focused modules (2026-07-02, debt D12)

#### preprocessing.py
- **Purpose**: Fundamental signal processing operations
- **Key Functions**:
  - `time_gate()` - Direct wave removal by time gating
  - `background_subtraction()` - Common-mode reference subtraction
  - `dewow()` - Low-frequency noise removal
  - `detect_first_break()` - First break detection (Coppens/STA-LTA)
  - `preprocess_signal()` - Complete preprocessing chain
  - `predictive_deconvolution()` - Wiener deconvolution

#### vivanco_pipeline.py
- **Purpose**: Complete Rojas-Vivanco (2025) processing workflow
- **Key Functions**:
  - `vivanco_preprocess()` - 7-step single-trace pipeline
  - `vivanco_preprocess_bscan()` - B-scan wrapper with rolling BGR
  - `vivanco_extract_features()` - 262-feature extraction
  - `predict_dzt_fouling()` - Complete classification workflow

### 2. Advanced Analysis Modules

#### spectral_attributes.py
- **Purpose**: Spectral and time-frequency analysis
- **Key Functions**:
  - `compute_spectrum()` - FFT-based spectral analysis
  - `compute_spectrogram()` - Short-Time Fourier Transform
  - `calculate_instantaneous_attributes()` - Hilbert transform attributes
  - `mpm_decompose()` - Matrix Pencil Method decomposition

#### bscan_processing.py
- **Purpose**: 2D B-scan processing algorithms
- **Key Functions**:
  - `agc_bscan()` - Automatic Gain Control
  - `fk_filter()` - Frequency-Wavenumber filtering
  - `kirchhoff_migration()` - Diffraction stack migration
  - `ica_multifractal_denoise()` - Advanced denoising pipeline

#### reflector_picking.py
- **Purpose**: Reflector detection and depth conversion
- **Key Functions**:
  - `pick_reflector()` - Hilbert envelope peak detection
  - `reflector_to_depth()` - Travel-time to depth conversion
  - `picks_to_layer_toml()` - Convert picks to gprMax TOML

#### coda_objectives.py
- **Purpose**: Coda wave analysis for fouling detection
- **Key Functions**:
  - `coda_envelope_correlation()` - Coda envelope similarity
  - `coda_energy_ratio()` - Energy distribution analysis
  - `coda_wasserstein_distance()` - Statistical distance metrics

## Processing Pipelines

### 1. Rojas-Vivanco (2025) Pipeline

```
┌─────────────────────────────────────────────────────────────────────────────┐
│               ROJAS-VIVANCO (2025) 7-STEP PIPELINE                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Step 1: Normalize to direct wave peak amplitude                             │
│  Step 2: Remove DC offset (dewow)                                          │
│  Step 3: Backward shift 30 samples (align direct wave at window[30])         │
│  Step 4: Bandpass filter (150-800 MHz)                                     │
│  Step 5: Window to 7 ns duration                                           │
│  Step 6: Background removal (BGR)                                           │
│  Step 7: Hilbert envelope extraction                                       │
│                                                                             │
│  Output: processed signal + pre_bgr signal + 262 features                   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Python Implementation:**
```python
result = vivanco_preprocess(signal, dt)
# Returns: {'processed': processed_signal, 'pre_bgr': pre_bgr_signal}

features = vivanco_extract_features(processed_signal, pre_bgr_signal, feature_names)
```

### 2. Standard Preprocessing Chain

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    STANDARD PREPROCESSING CHAIN                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Step 1: Direct wave removal (time_gate or background_subtraction)         │
│  Step 2: Dewow (low-frequency removal)                                      │
│  Step 3: First break detection                                              │
│  Step 4: Time-zero correction (align first breaks)                          │
│  Step 5: Bandpass filtering                                                │
│  Step 6: Gain application (TVG or AGC)                                      │
│  Step 7: Normalization                                                      │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Python Implementation:**
```python
processed = preprocess_signal(raw_trace, dt, method='background_subtraction')
```

### 3. Complete Classification Workflow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                COMPLETE CLASSIFICATION WORKFLOW                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Step 1: Read DZT file (dzt_io.read_dzt_traces)                            │
│  Step 2: Apply B-scan preprocessing (vivanco_preprocess_bscan)              │
│  Step 3: Extract features for each trace (vivanco_extract_features)         │
│  Step 4: Load pre-trained XGBoost model                                     │
│  Step 5: Predict fouling classes                                            │
│  Step 6: Decode class labels                                                 │
│  Step 7: Return predictions, labels, features, and processed data            │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Python Implementation:**
```python
results = predict_dzt_fouling('input.dzt', 'model.pkl', n_bscan=500)
# Returns: {'predictions': [...], 'labels': [...], 'feat_matrix': DataFrame, ...}
```

## Key Algorithms and References

### Direct Wave Removal Methods

1. **Time Gating** (Wang & Liu 2017)
   - `time_gate(signal, dt, gate_ns)`
   - Zeros samples before specified time gate
   - Simple and effective for consistent geometries

2. **Background Subtraction** (Wang & Liu 2017)
   - `background_subtraction(bscan, reference_trace)`
   - Subtracts common-mode reference from each trace
   - Effective for removing coherent noise

3. **SVD Removal** (Liu, Song & Lu 2017)
   - `svd_remove_direct_wave(bscan, p=None)`
   - Zeros first singular value in SVD decomposition
   - Quantitative rank selection with `svd_select_p()`

### First Break Detection

1. **Coppens Energy Ratio** (Coppens 1985)
   - `detect_first_break_coppens(signal, window_size)`
   - Energy-based picker using moving window ratios
   - Robust to noise but computationally intensive

2. **STA/LTA** (Earle & Shearer 1994)
   - `detect_first_break_sta_lta(signal, sta_win, lta_win)`
   - Short-term average to long-term average ratio
   - Fast and widely used in seismology

### Advanced Processing

1. **Predictive Deconvolution** (Xiong 2024)
   - `predictive_deconvolution(signal, lag, operator_length)`
   - Wiener prediction-error filter with Tikhonov regularization
   - Removes predictable components (multiples, ringing)

2. **Matrix Pencil Method** (Sarkar & Pereira 1995)
   - `mpm_decompose(signal, p, dt)`
   - Damped exponential decomposition via Hankel SVD
   - Extracts modal components from signals

3. **Multifractal Denoising** (Li 2022)
   - `ica_multifractal_denoise(bscan)`
   - FastICA + wavelet transform modulus maxima analysis
   - Advanced denoising preserving multifractal structure

## Feature Extraction

### 262-Feature Schema

The Rojas-Vivanco pipeline extracts 262 features organized into categories:

1. **Time-Domain Features** (50 features)
   - Amplitude statistics (mean, std, skewness, kurtosis)
   - Energy metrics (total, windowed, ratios)
   - Zero-crossing rates and durations

2. **Frequency-Domain Features** (100 features)
   - Spectral moments (centroid, bandwidth, roll-off)
   - Peak frequencies and magnitudes
   - Band energy ratios

3. **Time-Frequency Features** (50 features)
   - STFT coefficients and statistics
   - Spectrogram entropy and texture

4. **Hilbert Attributes** (30 features)
   - Envelope statistics
   - Instantaneous phase and frequency metrics

5. **Coda Wave Features** (32 features)
   - Coda energy ratios
   - Envelope correlations
   - Statistical distances

### Feature Extraction Usage

```python
# Extract features for ML model
features = vivanco_extract_features(processed_signal, pre_bgr_signal, feature_names)

# Features are automatically resampled to 70 samples for model compatibility
```

## B-scan Processing

### 2D Processing Functions

1. **Automatic Gain Control**
   - `agc_bscan(bscan, window_ns)`
   - Vectorized implementation (~100× faster than per-trace)
   - Uniform filtering for consistent amplitude scaling

2. **F-K Filtering**
   - `fk_filter(bscan, dt, dx, f_range, k_range)`
   - Frequency-Wavenumber domain filtering
   - Removes horizontal events (direct wave, ringing)
   - Selects dipping reflectors by apparent velocity

3. **Kirchhoff Migration**
   - `kirchhoff_migration(bscan, dt, dx, velocity)`
   - Diffraction stack for zero-offset data
   - Collapses hyperbolic tails to true positions
   - Aperture-limited implementation

### B-scan Workflow Example

```python
# Load B-scan data
bscan, meta = read_dzt_traces('input.dzt', num_traces=1000)
dt = meta['sample_interval_ns'] * 1e-9
dx = meta['trace_interval_m']

# Apply 2D processing
bscan_agc = agc_bscan(bscan, window_ns=50)
bscan_fk = fk_filter(bscan_agc, dt, dx, f_range=(100e6, 1e9), k_range=(0, 100))
bscan_migrated = kirchhoff_migration(bscan_fk, dt, dx, velocity=0.1)
```

## Reflector Analysis

### Depth Conversion

```python
# Pick reflector from processed trace
peak_idx = pick_reflector(processed_signal, skip_window=10)

# Convert to depth
depth_m = reflector_to_depth(peak_idx, dt, relative_permittivity=4.0)

# Convert picks to gprMax TOML for synthetic scene generation
layer_toml = picks_to_layer_toml(bscan_picks, dt, dx, material_params)
```

### Physics-Based Conversion

Uses Sussmann et al. (2000) formula:
```
d = (c × t_oneway) / sqrt(ε_r)
```

Where:
- `d` = depth (meters)
- `c` = speed of light (299,792,458 m/s)
- `t_oneway` = one-way travel time (seconds)
- `ε_r` = relative permittivity (dimensionless)

## Coda Wave Analysis

### Key Metrics for Fouling Detection

1. **Coda Envelope Correlation**
   - Measures similarity between coda envelopes
   - High correlation indicates similar fouling conditions

2. **Coda Energy Ratio**
   - Ratio of coda energy to total energy
   - Higher ratios indicate more complex scattering (potential fouling)

3. **Wasserstein Distance**
   - Statistical distance between coda distributions
   - Quantifies differences in energy distribution

### Usage Example

```python
# Compute coda metrics
correlation = coda_envelope_correlation(trace1, trace2)
energy_ratio = coda_energy_ratio(signal, dt, gate_start=5e-9, gate_length=10e-9)
distance = coda_wasserstein_distance(signal1, signal2)
```

## Performance Considerations

### Optimization Strategies

1. **Vectorized Operations**
   - `agc_bscan()` uses `uniform_filter1d` for 100× speedup
   - Batch processing where possible

2. **Memory Efficiency**
   - Process traces in chunks for large datasets
   - Use generators for streaming data

3. **Parallel Processing**
   - B-scan operations are embarrassingly parallel
   - Use `multiprocessing` or `joblib` for trace-level parallelism

### Computational Complexity

| Operation | Complexity | Notes |
|-----------|------------|-------|
| `time_gate()` | O(n) | Simple array slicing |
| `dewow()` | O(n×w) | w = dewow window size |
| `bandpass_filter()` | O(n×order) | Butterworth filter |
| `svd_denoise()` | O(m×n²) | m = traces, n = samples |
| `agc_bscan()` | O(m×n) | Vectorized implementation |
| `fk_filter()` | O(m×n×log(n)) | FFT-based |
| `kirchhoff_migration()` | O(m×n×a) | a = aperture size |

## Integration with Other Modules

### Data Flow Connections

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    SIGNAL PROCESSING INTEGRATION                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────┐       ┌─────────────┐       ┌─────────────────┐       │
│  │             │       │             │       │                 │       │
│  │  dzt_io.py  │──────▶│signal_proce│──────▶│ vivanco_pipel  │       │
│  │  (Input)    │       │ ssing.py    │       │  ine.py         │       │
│  │             │       │             │       │                 │       │
│  └─────────────┘       └─────────────┘       └────────────┬─────────┘       │
│                                                          │                 │
│                                                          ▼                 │
│                                                  ┌─────────────────┐       │
│                                                  │                 │       │
│                                                  │feature_extract │       │
│                                                  │ ion.py          │       │
│                                                  │                 │       │
│                                                  └────────────┬─────┘       │
│                                                           │                 │
│                                                           ▼                 │
│                                                  ┌─────────────────┐       │
│                                                  │                 │       │
│                                                  │  ML Models      │       │
│                                                  │  (XGBoost, etc.)│       │
│                                                  └─────────────────┘       │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │                        VISUALIZATION INTEGRATION                      │  │
│  │                                                                         │  │
│  │  ┌─────────────────┐       ┌─────────────────┐       ┌─────────────┐  │  │
│  │  │                 │       │                 │       │             │  │  │
│  │  │  visualization/ │◄──────┤signal_processing│◄──────┤  dzt_io.py  │  │  │
│  │  │  (Plotting)     │       │                 │       │  (Data)     │  │  │
│  │  └─────────────────┘       └─────────────────┘       └─────────────┘  │  │
│  └─────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Usage Examples

### Example 1: Basic Signal Processing

```python
from src.signal_processing import preprocess_signal, time_gate

# Load a single trace
raw_trace = ...  # From DZT file or simulation
dt = 0.02e-9  # 20 ps sample interval

# Apply basic preprocessing
processed = preprocess_signal(raw_trace, dt, method='time_gate', gate_ns=5.0)

# Or use time gating directly
gated_signal = time_gate(raw_trace, dt, gate_ns=5.0)
```

### Example 2: Complete Fouling Classification

```python
from src.signal_processing import predict_dzt_fouling

# Process entire DZT file and classify fouling
results = predict_dzt_fouling(
    dzt_path='field_data.dzt',
    model_pkl='models/fouling_classifier.pkl',
    n_bscan=500,
    bgr_window=100
)

# Access results
print(f"Predictions: {results['predictions']}")
print(f"Labels: {results['labels']}")
print(f"Feature matrix shape: {results['feat_matrix'].shape}")
```

### Example 3: Advanced B-scan Processing

```python
from src.signal_processing import agc_bscan, fk_filter
from src.dzt_io import read_dzt_traces

# Load B-scan data
bscan, meta = read_dzt_traces('input.dzt', num_traces=1000)
dt = meta['sample_interval_ns'] * 1e-9
dx = meta['trace_interval_m']

# Apply advanced processing
bscan_processed = agc_bscan(bscan, window_ns=50)
bscan_filtered = fk_filter(
    bscan_processed, 
    dt, dx, 
    f_range=(100e6, 1e9), 
    k_range=(0, 100)
)
```

### Example 4: Feature Extraction for Custom Model

```python
from src.signal_processing import vivanco_preprocess, vivanco_extract_features

# Process single trace
result = vivanco_preprocess(signal, dt)
processed = result['processed']
pre_bgr = result['pre_bgr']

# Define features of interest
feature_names = [
    'mean_amplitude', 'peak_frequency', 'energy_ratio',
    'envelope_std', 'spectral_centroid'
]

# Extract features
features = vivanco_extract_features(processed, pre_bgr, feature_names)
```

## Best Practices

### Data Quality Checks

1. **Validate Input Data**
   - Check for NaN/inf values
   - Verify sample interval consistency
   - Validate trace lengths

2. **Parameter Selection**
   - Use appropriate gate times based on antenna height
   - Select bandpass frequencies based on antenna specs
   - Choose BGR window sizes based on expected reflector spacing

3. **Result Validation**
   - Visualize processed traces
   - Check feature distributions
   - Validate depth conversions with known reflectors

### Performance Optimization

1. **Batch Processing**
   - Process multiple traces together where possible
   - Use vectorized operations

2. **Memory Management**
   - Process large datasets in chunks
   - Use generators for streaming data

3. **Parallelization**
   - Parallelize trace-level operations
   - Use joblib or multiprocessing

### Error Handling

1. **Input Validation**
   - Validate all function inputs
   - Provide clear error messages

2. **Graceful Degradation**
   - Handle edge cases (empty traces, constant signals)
   - Provide fallback methods when primary methods fail

3. **Logging**
   - Log processing parameters
   - Record warnings and errors
   - Track processing times for performance monitoring

## Troubleshooting

### Common Issues and Solutions

**Issue: Poor first break detection**
- *Cause*: Low signal-to-noise ratio
- *Solution*: Apply dewow or bandpass filtering first
- *Alternative*: Try different picker (Coppens vs STA/LTA)

**Issue: Artifacts in processed data**
- *Cause*: Inappropriate filter parameters
- *Solution*: Adjust bandpass frequencies or filter order
- *Check*: Validate filter response with frequency analysis

**Issue: Incorrect depth conversions**
- *Cause*: Wrong relative permittivity value
- *Solution*: Calibrate with known reflectors
- *Check*: Verify travel time calculations

**Issue: Memory errors with large datasets**
- *Cause*: Loading entire dataset at once
- *Solution*: Process in chunks or use generators
- *Check*: Monitor memory usage during processing

## Future Development Directions

### Potential Enhancements

1. **Additional Processing Algorithms**
   - Wavelet-based denoising
   - Machine learning-based filtering
   - Advanced migration algorithms

2. **Performance Improvements**
   - GPU acceleration for key operations
   - Optimized batch processing
   - Memory-mapped file support

3. **Extended Feature Sets**
   - Deep learning feature extraction
   - Time-frequency texture features
   - Multivariate statistical features

4. **Integration Enhancements**
   - Real-time processing support
   - Streaming data interfaces
   - Cloud processing capabilities

## References

### Primary Methodological References

1. **Wang & Liu (2017)** - Direct wave removal methods
2. **Rojas-Vivanco et al. (2025)** - Complete processing pipeline
3. **Liu, Song & Lu (2017)** - SVD coherent noise removal
4. **Coppens (1985)** - Energy ratio first break detection
5. **Earle & Shearer (1994)** - STA/LTA detection method
6. **Xiong et al. (2024)** - Predictive deconvolution
7. **Li et al. (2022)** - Multifractal denoising

### Implementation References

- **Unpingco (2014)** - Windowing functions
- **Sarkar & Pereira (1995)** - Matrix Pencil Method
- **Sussmann et al. (2000)** - Depth conversion physics
- **Yilmaz (2001)** - Seismic processing methods
- **Daniels (2005)** - GPR-specific processing

This comprehensive documentation provides a complete guide to the Synth-GPR signal processing system, covering architecture, algorithms, usage patterns, and best practices.
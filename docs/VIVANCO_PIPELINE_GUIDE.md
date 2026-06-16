# Vivanco Signal Processing Pipeline

Complete implementation of the 7-step signal processing pipeline from **Rojas-Vivanco 2025** paper.

## Overview

The pipeline transforms raw GPR A-scans into clean, normalized envelope signals suitable for machine learning feature extraction.

```
Raw Signal
    ↓
1. Direct Wave Normalization (peak amplitude)
    ↓
2. DC-Shift Removal (zero-mean centering)
    ↓
3. Direct Wave Elimination (+30 sample shift)
    ↓
4. Bandpass Filter (150-800 MHz)
    ↓
5. Truncation (50 ns window)
    ↓
6. BGR Filter (1000-trace moving average)
    ↓
7. Analytic Envelope (Hilbert transform)
    ↓
Processed Signal (ready for feature extraction)
```

## Processing Steps

### 1. Direct Wave Normalization
- Identifies the direct wave peak (first major energy arrival, 0-20 ns)
- Normalizes entire signal by peak amplitude
- Purpose: Removes amplitude variations due to hardware gain differences

**Result:** Signal amplitude → ±1.0 range

### 2. DC-Shift Removal
- Subtracts mean value from signal
- Ensures zero-mean centering
- Purpose: Removes DC component and baseline offset

**Result:** Signal mean = 0.0

### 3. Direct Wave Elimination
- Sets time zero at direct wave peak
- Applies 30-sample shift (antenna-to-surface travel time)
- Discards initial pulse
- Purpose: Isolates subsurface reflections (coda region)

**Result:** Signal starts after direct wave + 30 samples

### 4. Bandpass Filter
- **Type:** Butterworth IIR, order 4
- **Frequency range:** 150-800 MHz
- **Method:** Zero-phase filtering (filtfilt)
- Purpose: Removes noise outside signal bandwidth

**Result:** Frequency-filtered signal

### 5. Signal Truncation
- Extracts window of interest (default: 50 ns)
- Reduces noise and computation
- Purpose: Focuses on relevant coda region

**Result:** Signal length ≈ 50 ns / dt_ns samples

### 6. BGR Filter (Background Removal)
- **Only for multi-trace processing**
- Moving average across traces (default: 1000-trace window)
- Subtracts background from each trace
- Purpose: Removes coherent noise patterns

**Formula:** `processed[i] = signal[i] - mean(signal[i-500:i+500])`

**Result:** Noise reduction across the radargram

### 7. Analytic Envelope
- Applies Hilbert transform to get analytic signal
- Extracts magnitude (envelope)
- Assumes signal already normalized by maximum
- Purpose: Removes oscillations, preserves energy structure

**Result:** Smooth envelope suitable for feature extraction

## Usage

### Basic: Process DZT file (real data)
```bash
python scripts/proceso_senal_vivanco.py \
  D:/Codigo/Data/PUERTO-LIMACHE*.DZT \
  --max-traces 1000 \
  -o output.npz
```

### Basic: Process synthetic .out file
```bash
python scripts/proceso_senal_vivanco.py \
  output_test/ballast_eps51_optimized.out \
  -o output.npz
```

### Advanced: Custom parameters
```bash
python scripts/proceso_senal_vivanco.py \
  data.DZT \
  --max-traces 5000 \
  --bgr-window 500 \
  --window-length 100 \
  -o processed.npz
```

### Parameters
- `--max-traces`: Maximum number of traces to read (DZT only, default: all)
- `--no-bgr`: Skip BGR filter (useful for single traces)
- `--bgr-window`: BGR moving window size (default: 1000 traces)
- `--window-length`: Truncation window in nanoseconds (default: 50 ns)
- `-o, --output`: Save processed signals as NPZ file

## Output Format

### NPZ File Structure
```python
import numpy as np

data = np.load('output.npz')
processed = data['processed']    # [n_traces, n_samples]
dt_ns = float(data['dt_ns'])     # Sampling interval in ns
```

### Dimensions
- **DZT (real):** (n_traces, ~419) - 50 ns window, dt≈0.0978 ns
- **.out (synthetic):** (1, ~6724) - 50 ns window, dt≈0.0071 ns

## Example: Using Processed Data

```python
import numpy as np
from pathlib import Path

# Load processed signals
data = np.load('output_test/vivanco_processed_dzt.npz')
processed = data['processed']
dt_ns = float(data['dt_ns'])

# Convert to time axis
n_samples = processed.shape[1]
t_ns = np.arange(n_samples) * dt_ns

# Extract first trace
trace_1 = processed[0, :]

# Display statistics
print(f"Shape: {processed.shape}")
print(f"dt: {dt_ns:.6f} ns")
print(f"Window: {(n_samples-1)*dt_ns:.2f} ns")
print(f"Mean: {processed.mean():.6f}")
print(f"Std: {processed.std():.6f}")
```

## Feature Extraction

After processing with Vivanco pipeline, common features include:

- **Time-domain:** Peak value, RMS, energy, skewness, kurtosis
- **Frequency:** FFT magnitude, spectral centroid, bandwidth
- **Envelope:** Peak envelope, envelope integral, envelope decay rate
- **Hilbert:** Instantaneous amplitude, instantaneous frequency, instantaneous phase

## References

- **Rojas-Vivanco et al. (2025):** "In-house paper defining docs/input pipeline"
  - FI=0.4933 is CLEAN (not missing)
  - Notebook bins: 0/10/20/30/40
  - Field validation: block-regularized along Pk, not per-trace

## Performance

| Data Type | Size | Processing Time |
|-----------|------|-----------------|
| 100 DZT traces | (100, 419) | ~1 second |
| 1000 DZT traces | (1000, 419) | ~10 seconds |
| Synthetic .out | (1, 6724) | ~0.1 seconds |

## Troubleshooting

### "High freq exceeds Nyquist"
- Occurs when fs/2 < 800 MHz
- Automatically capped at 99% of Nyquist
- Check your dt_ns value

### BGR filter produces noise
- Occurs with insufficient traces (window > available traces)
- Solution: Use `--no-bgr` for small datasets

### Output shape smaller than expected
- Normal: Truncation removes late-time noise
- Check `--window-length` parameter

## API Reference

### VivancoPipeline Class

```python
from scripts.proceso_senal_vivanco import VivancoPipeline

# Initialize
pipeline = VivancoPipeline(dt_ns=0.097847)

# Process single trace
result = pipeline.process_single_trace(
    signal=raw_signal,
    window_length_ns=50,
    normalize_direct_wave=True,
    remove_dc=True,
    eliminate_dw=True,
    apply_bandpass=True,
    compute_envelope=True
)

# Access intermediate results
envelope = result['signal_envelope']
filtered = result['signal_filtered']
direct_wave_peak_idx = result['direct_wave_peak_idx']

# Process multiple traces
processed_2d = pipeline.process_multiple_traces(
    signals_2d=traces_array,
    apply_bgr=True,
    bgr_window=1000,
    window_length_ns=50
)
```

## File Locations

- **Script:** `scripts/proceso_senal_vivanco.py`
- **Visualization:** `visualize_vivanco_pipeline.py`
- **Pipeline visualization:** `output_test/vivanco_pipeline_steps.png`
- **Processed outputs:** `output_test/vivanco_processed_*.npz`

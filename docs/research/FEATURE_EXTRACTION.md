# Feature Extraction Reference

This document details the features extracted from Ground Penetrating Radar (GPR) A-Scans by the `src/feature_extraction.py` module. These features are designed to capture the statistical, spectral, and morphological characteristics of the signal to differentiate between Clean (CL) and Fouled (F, HF) ballast.

## 1. Time Domain Statistics
Basic statistical measures applied to the raw signal amplitude.

| Feature | Description | Physical Interpretation |
| :--- | :--- | :--- |
| **Mean / Median** | Central tendency. | DC offset or bias (usually removed during preprocessing). |
| **RMS / Standard Deviation** | Root Mean Square / Spread. | Overall signal energy/strength. Higher variation often indicates scattering. |
| **Skewness / Kurtosis** | Asymmetry / Tailedness. | Deviation from Gaussian noise; indicates impulsive events (strong reflections). |
| **Peak Max / Min** | Maximum excursion. | Strength of the strongest reflector (e.g., interface). |
| **Crest Factor** | Peak / RMS. | Impulsiveness of the signal. |
| **Zero Crossings** | Count of sign changes. | Proxy for dominant frequency (in time domain). |
| **Area** | Sum of absolute values. | Total accumulated energy response. |
| **Second Derivative (Inflexion)** | Count of sign changes in 2nd derivative. | Roughness/complexity of the waveform. |
| **Deciles / Percentiles** | Value at 10%, 25%, ..., 90%. | Distribution shape analysis. |

## 2. Hilbert Transform (Instantaneous Attributes)
The Hilbert Transform computes the analytic signal, allowing extraction of the **Envelope** (Instantaneous Amplitude), which represents the energy envelope independent of phase.

| Feature | Description |
| :--- | :--- |
| **Hilbert Mean / RMS / Std** | Statistics applied to the envelope. |
| **Hilbert Peak / Crest** | Maximum energy packet strength. |

**Significance:** The envelope is crucial for detecting the "smearing" effect of scattering in fouled ballast. Clean ballast typically has distinct reflection pulses; fouled ballast dictates chaotic scattering that widens the envelope.

## 3. Frequency Domain (Fourier Analysis)
Features derived from the Fast Fourier Transform (FFT) spectrum.

| Feature | Description | Physical Interpretation |
| :--- | :--- | :--- |
| **Dominant Frequency** | Frequency with max magnitude. | Center frequency shift due to attenuation (fouling absorbs high freq). |
| **Bandwidth (-3dB)** | Width of the primary peak. | pulse broadening / dispersion. |
| **Mean / Median Frequency** | Spectral centroid / bisector. | Shift towards lower frequencies indicates wet/fouled material (attenuation). |
| **Spectral Entropy** | Randomness of spectrum. | Complexity of texture; scattering increases entropy. |
| **Spectral Flatness** | Geometric mean / Arithmetic mean. | Tonal vs. Noise-like. Saturated fouling might act more like a homogeneous medium (tonal) vs scattering (noisy). |
| **Area Fourier** | Sum of spectrum. | Total spectral energy. |

## 4. Time-Frequency (STFT)
Short-Time Fourier Transform features, analyzing how frequency content changes with depth (time).

*   **Bands:**
    *   **Low**: < 500 MHz
    *   **Mid**: 500 - 1500 MHz
    *   **High**: > 1500 MHz
*   **Features**: Mean and Max energy in each band.
*   **Centroid Variance**: Standard deviation of the spectral centroid over time. High variance implies dispersive media.

## 5. Morphological / Spatial Features

### Slice Statistics
The signal vector is divided into **14 equal slices**.
*   **Features**: `stat_slice_i_mean`, `stat_slice_i_std` for i=0..13.
*   **Usage**: Localizes roughness. Shallow slices (0-3) correspond to the ballast surface/top. High Standard Deviation in shallow slices correlates with "rough" texture (Clean Ballast voids). Low deviation suggests "smooth" texture (Fouling filling the voids).

### Grid Features
The signal is resampled to **160 points** and treated as a 16x10 grid (or simply a vector of 160 points).
*   **Features**:
    *   `grid_signal_time_i_j`: Raw amplitude at resampled point.
    *   `grid_hilbert_envelope_i_j`: Envelope amplitude.
    *   `grid_hilbert_imag_i_j`: Imaginary component of Analytic signal.
*   **Golden Zone**: Indices roughly 40-60 (Grid rows 4-5) typically align with the main ballast bed reflection in standard geometries. High energy here indicates strong scattering (Clean), while attenuation indicates Fouling/Moisture.

---

## 6. Metadata
Constant attributes passed through from the HDF5 file:
*   `Title` (Class Label)
*   `Scenario` (Simulation type)
*   `FI` (Fouling Index)

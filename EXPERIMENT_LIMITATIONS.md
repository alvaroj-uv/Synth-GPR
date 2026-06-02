# Waveform-Only RF Model: Complete Limitations Audit

## 1. DATA LIMITATIONS

### 1.1 Synthetic Data Only
- **Issue**: All 80k samples are from gprMax FDTD simulations, not real-world GPR field measurements
- **Impact**: Unknown sim-to-real domain gap; field data may have:
  - Different noise characteristics
  - Actual antenna crosstalk (simulations use idealized antenna)
  - Environmental variability (temperature, soil moisture changes)
  - Multiple reflections and mode conversions
- **Mitigation needed**: Validate on real ballast track GPR data before deployment

### 1.2 Single Antenna Configuration
- **Issue**: All simulations use one fixed antenna setup (1 RX @ 0.05m spacing, 400 MHz)
- **Impact**: Model won't generalize to:
  - Different GPR equipment (e.g., GSSI SIR, IDS, MALA)
  - Multi-channel GPR systems
  - Different frequencies (e.g., 900 MHz, 2 GHz)
  - Different antenna spacing
- **Mitigation needed**: Retrain or fine-tune for each new antenna/frequency

### 1.3 Generic Antenna Model
- **Issue**: Simulations use idealized Hertzian dipole, not a commercial antenna
- **Impact**: 
  - No realistic TX-RX crosstalk (simulations have <0.01% coupling)
  - Field antennas have 20-50% crosstalk, which significantly alters waveforms
  - Real antenna response is frequency-dependent in ways the dipole isn't
- **Gap**: 88.68% accuracy may drop 5-15% on field data due to crosstalk alone

### 1.4 One-Dimensional A-Scans Only
- **Issue**: Model trained on single Ez vertical component (Hz field absent, Hx not measured)
- **Impact**: Can't use:
  - Full EM wave polarization information
  - Multi-component cross-correlation (e.g., Ez-Hx phase shifts detect anisotropy)
  - Transverse isotropy in ballast (rock orientation affects signal)
- **Limitation**: Real GPR systems often have multiple receiver pairs; this model ignores that richness

### 1.5 Uniform Ballast Geometry
- **Issue**: All simulated ballast:
  - Same nominal rock size (~4mm radius)
  - Same fouling particle PSD (either "standard" or "a4" Benedetto silty material)
  - Uniform depth-wise settlement
  - 1-D layering (no lateral variability)
- **Impact**: Won't generalize to:
  - Ballast with mixed rock sizes (real tracks have >2:1 size variation)
  - Different fouling materials (coal dust, clay, organic matter)
  - Buried objects (sleeper fragments, fasteners)
  - Ballast with voids or slumping (3-D structure)

### 1.6 No Preprocessing Variability
- **Issue**: All signals use fixed preprocessing (dewow, time-zero correction, bandpass)
- **Impact**: Real field data preprocessing varies:
  - Different time-zero picking accuracy
  - Varying bandpass choices per user
  - Some data has gain functions, others don't
  - Quality of dewow filter depends on survey conditions
- **Assumption**: Model expects perfectly preprocessed input

---

## 2. FEATURE ENGINEERING LIMITATIONS

### 2.1 Limited Feature Diversity
- **Issue**: 572 features are all statistical/spectral measures of a single 1-D signal
- **Impact**: Missing:
  - Wavelet features (not computed for this model)
  - Deep learned features (CNN embeddings)
  - Temporal context (treats each A-scan as isolated; ignores B-scan neighbors)
  - Multi-scale texture features
- **Baseline note**: CLAUDE.md mentions "baseline: 0.7083" on 30k samples—this suggests that 572 features alone are near saturation for waveform-only prediction

### 2.2 No Physics-Informed Features
- **Issue**: All features are black-box signal processing; no material-property features
- **Impact**: Model doesn't explicitly capture:
  - Attenuation (relates to material loss)
  - Dispersion (frequency-dependent velocity)
  - Dielectric constant (most direct ballast property)
- **Interpretation problem**: Top feature `hilbert_standard_deviation` is descriptive but not mechanistic

### 2.3 Grid Features Lack Spatial Context
- **Issue**: `grid_signal_time_*` and `grid_hilbert_*` features divide A-scan into arbitrary 1-D slices (no justification for grid resolution)
- **Impact**: 
  - Optimal grid size not tuned
  - Fouling is localized (top 10cm), but grid may average it away
  - No adaptive slicing based on signal energy

---

## 3. MODEL & VALIDATION LIMITATIONS

### 3.1 Train/Test Split Issues
- **Split method**: Stratified 80/20 on full 80k samples
- **Issue 1**: No explicit isolation by dataset source
  - 50k gpr_dataset_10k + 30k dataset_variants mixed randomly
  - gpr_dataset_10k has Lab_LDCP_FI_est (original); dataset_variants has calculated FI_est
  - If model learns to exploit this difference, it's a hidden source of leakage
- **Issue 2**: Stratification by class only; ignores:
  - Sampling bias (dataset_variants overrepresents fouled samples ~97% fouled vs 50% in 10k)
  - Temporal structure (if samples were ordered by fouling level, train/test could split a trend)
- **Missing**: Cross-validation across source datasets (should test gpr_dataset_10k model on dataset_variants)

### 3.2 Class Imbalance Not Properly Addressed
- **Class distribution**: C=10k, MC=22.6k, MF=9.5k, F=18.9k, HF=19k
- **Issue 1**: `class_weight="balanced"` in RF helps, but:
  - MF is smallest (9.5k); its 70% precision is the weakest
  - F and HF together dominate (37.9k); model may be biased to those
- **Issue 2**: Balanced accuracy is appropriate metric, but recall breakdown shows:
  - MF recall = 72% (28% of MF samples misclassified!)
  - This is the fouling class most relevant to track maintenance (precursor to F)

### 3.3 Random Forest Hyperparameters Not Tuned
- **Fixed settings**: 300 trees, max_features="sqrt", min_samples_leaf=2, balanced weights
- **Issue**: No grid search or cross-validation for hyperparameter optimization
  - Might be underfitting (too few trees?) or overfitting (min_samples_leaf=2 is permissive)
  - n_estimators=300 chosen arbitrarily
- **CV results**: 0.8815 +/- 0.0018 is stable, but lower bound (0.8797) shows room for optimization

### 3.4 No Confidence Calibration
- **Problem**: Predictions are hard class labels; no uncertainty quantification
- **Real-world impact**: 
  - Field technician doesn't know which predictions are confident vs. borderline
  - Confusing MF ↔ F cases (precision 70-84%) should have uncertainty flags
- **Missing**: Probability outputs, prediction intervals, or confidence scores

### 3.5 No External Validation
- **Issue**: Model tested only on train/test split of same 80k dataset
- **Missing validations**:
  - Independent real-world test set (actual track GPR surveys)
  - Temporal validation (train on old data, test on new data)
  - Spatial validation (train on Track A, test on Track B)
  - Cross-antenna validation (train on 400 MHz, test on 900 MHz)

---

## 4. FEATURE IMPORTANCE LIMITATIONS

### 4.1 Feature Importance Misleading for RF
- **Top features**: hilbert_standard_deviation (2.09%), area_fourier (2.06%), skewness (1.91%)
- **Issue 1**: Importance scores are very flat (top 20 features: 2.09% down to 0.73%)
  - Suggests no single feature dominates; model is ensemble of many weak signals
  - Top feature explains only 2% of variance
- **Issue 2**: Feature importance doesn't imply causation
  - High importance ≠ physically meaningful for fouling
  - Could be capturing simulation artifacts (e.g., numerical dispersion in FDTD)

### 4.2 Grid Features Overrepresented in Top-20
- **Observation**: `grid_signal_time_*` and `grid_hilbert_*` appear ~5 times in top-20
- **Issue**: These are redundant slices of the same A-scan
  - RF feature selection doesn't remove multicollinearity
  - Importance is distributed across correlated features rather than concentrated

---

## 5. EXPERIMENTAL DESIGN LIMITATIONS

### 5.1 No Ablation Study
- **Missing**: 
  - Performance breakdown by feature group (statistical vs. spectral vs. grid)
  - Contribution of specific preprocessing steps (dewow, bandpass, time-zero)
  - Impact of removing worst-performing classes (e.g., train without MF)
- **Would clarify**: Where the 11.3% gap (vs. 99.98% with metadata) comes from

### 5.2 No Comparison to Baselines
- **Missing comparisons**:
  - Simple statistical rules (e.g., "if RMS > threshold, then fouled")
  - Single-feature models (e.g., just area_fourier)
  - Frequency-domain classifier (peak frequency alone)
  - Deep learning baseline (CNN on raw A-scan)
- **Impact**: Can't assess whether 88.68% is good or if a simpler model achieves 85%

### 5.3 No Domain Shift Analysis
- **Issue**: Merges gpr_dataset_10k + dataset_variants without quantifying their difference
  - gpr_dataset_10k: Lab_LDCP_FI_est from actual LabWorker calculation
  - dataset_variants: Lab_LDCP_FI_est from formula (FH/1.5)
  - Are they equivalent? Unknown
- **Test needed**: Train on 10k, test on variants (and vice versa)

### 5.4 Fixed Preprocessing Pipeline
- **Issue**: All samples undergo identical preprocessing
- **Real-world variability**: 
  - Field surveys may have different time-zero accuracy (±0.5 ns)
  - Gain curves vary by equipment and soil type
  - Bandpass filter parameters not standardized
- **Test needed**: Robustness to ±0.5 ns time-zero jitter, ±10% gain noise

---

## 6. GENERALIZATION LIMITATIONS

### 6.1 Single Ballast Type
- **Issue**: All fouling is simulated clay/silt (standardized or A4 PSD)
- **Real-world ballast**: Contains:
  - Coal dust (conductive, different permittivity)
  - Sand/silt mix (variable grading)
  - Organic matter (moisture dependent)
  - Bound fines (cemented by rust or biology)
- **Impact**: Model won't generalize to different fouling compositions

### 6.2 No Moisture Variability
- **Issue**: All simulations fix moisture content per sample
- **Real-world**: Moisture changes seasonally, diurnally, with weather
  - Moisture ε_r ≈ 80 (huge effect on permittivity)
  - Could dominate the waveform over fouling effects
- **Gap**: Model never trained on noisy/wet conditions

### 6.3 Temperature Effects Ignored
- **Issue**: FDTD conductivity/permittivity held constant
- **Real-world**: Temperature affects:
  - Soil conductivity (doubled over 0–40°C range)
  - Material dielectric loss
  - Antenna response
- **Impact**: Cold winter track may look different from summer track to model

---

## 7. REPORTING & TRANSPARENCY LIMITATIONS

### 7.1 No Error Analysis
- **Missing**: Detailed error cases
  - Which samples are consistently misclassified?
  - Do errors correlate with specific fouling percentages?
  - Are errors clustered in certain parameter ranges (e.g., high moisture)?

### 7.2 No Statistical Significance Testing
- **Reported**: 88.68% balanced accuracy, no confidence interval
- **Missing**: 
  - 95% CI on accuracy (likely ±0.5–1.0% given 16k test samples)
  - Statistical test of whether waveform-only is significantly worse than with metadata
  - Pairwise comparisons between classes (are C vs HF differences significant?)

### 7.3 Reproducibility Issues
- **Assumptions**:
  - Python 3.x, scikit-learn ≥1.0, pandas ≥1.3 (not specified)
  - Random seed = 42, but GPUs/CPUs may produce slightly different FP32 rounding
  - Feature extraction code in `src/feature_extraction.py` (not reviewed here)
- **Missing**: Full dependencies list, Docker image, or exact package versions

---

## 8. RESEARCH CONTEXT LIMITATIONS

### 8.1 Mismatch with CLAUDE.md Baseline
- **CLAUDE.md states**: "Baseline: 0.7083 balanced accuracy on 30k samples with 572 waveform features"
- **Current result**: 0.8868 on 80k samples (25% relative improvement)
- **Questions**:
  - Was the 30k baseline trained differently? (Different RF params? Different preprocessing?)
  - Is the improvement from more data, better hyperparameters, or lab_worker fixes?
  - Unclear which 30k subset was used for baseline

### 8.2 Lab_LDCP_FI_est Validity Question
- **Issue**: For dataset_variants, Lab_LDCP_FI_est was calculated using formula (FH/1.5)
- **Not empirically validated**: 
  - Formula derived from gpr_dataset_10k correlation
  - Assumes same relationship holds in variants (may not if fouling composition differs)
- **Test needed**: Compare calculated FI_est to actual LDCP measurements on real ballast

### 8.3 No Cite for Formula
- **Formula**: Lab_LDCP_FI_est = Lab_LDCP_FH / 1.5 comes from "Rojas-Vivanco 2025 eq. 9"
- **Missing**: 
  - Full reference (journal, doi)
  - Context (is this for clay fouling only? All ballast?)
  - Derivation or empirical range where formula is valid

---

## 9. PRACTICAL DEPLOYMENT LIMITATIONS

### 9.1 Processing Time Unknown
- **Missing**: How long does feature extraction + prediction take?
  - Is it real-time suitable for field surveys?
  - Or requires post-processing at office?

### 9.2 No Robustness to Noise
- **Issue**: Waveforms in simulations are noise-free
- **Missing**: Testing on data with realistic GPR noise (SNR 20-40 dB)
  - Does 88.68% drop to 80% or 70% with noise?

### 9.3 No Handling of Bad/Saturated Traces
- **Real-world**: Some A-scans are clipped, saturated, or invalid
- **Missing**: Preprocessing to detect and skip bad traces

---

## 10. SUMMARY: KEY UNKNOWNS

| Limitation | Severity | Impact on Accuracy |
|---|---|---|
| Synthetic data only (no real tracks) | **CRITICAL** | ±5-15% unknown domain gap |
| Single antenna/frequency | HIGH | Won't transfer to different GPR systems |
| No noise robustness | HIGH | ±3-8% with realistic field noise |
| Class imbalance (MF worst) | MEDIUM | 70% precision on MF is weak; may miss early fouling |
| No ablation study | MEDIUM | Unknown which features/preprocessing matter |
| No comparison to baselines | MEDIUM | Can't assess if 88.68% is actually good |
| Formula-derived Lab_LDCP_FI_est (variants) | MEDIUM | Unvalidated extrapolation |
| Moisture/temperature variability ignored | MEDIUM | Model hasn't seen real environmental variation |
| Flat feature importance (top: 2%) | LOW | Hard to interpret; suggests weak signal |

---

## RECOMMENDATIONS FOR NEXT STEPS

1. **Validate on real GPR data** (ballast track survey with known lab fouling samples)
2. **Test domain transfer**: Train on gpr_dataset_10k, test on dataset_variants
3. **Add robustness testing**: Noise injection, preprocessing perturbation, antenna variation
4. **Ablation study**: Feature importance decomposition by signal component
5. **Compare to simpler baselines**: Frequency-domain classifier, threshold rules
6. **Calibrate predictions**: Return probability scores + uncertainty, not hard labels
7. **Characterize failure modes**: Which fouling patterns does the model miss?
8. **Document assumptions**: Exactly which preprocessing, antenna, frequency, rock size, etc.

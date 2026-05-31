# Notes: Lahnsteiner et al. 2024 — Object Detection in Multi-Antenna GPR

**Citation:** Lahnsteiner, L. et al. *Automatic Object Detection in Radargrams of Multi-Antenna GPR Systems Based on Simulation Data for Railway Infrastructure Analysis.* Appl. Sci. 2024, 14, 3521. https://doi.org/10.3390/app14083521

**Key claim:** A detection model trained *exclusively* on synthetic gprMax data successfully detects objects in real railway GPR data (SSIM sim/real ≈ 0.95).

---

## Ideas Relevant to Synth-GPR

### 1. Antenna Digital Twin (high priority)
They built a digital twin of the IDS AM200 antenna using **Taguchi optimization** (Warren & Giannopoulos 2011) by matching:
- Antenna crosstalk (TX→RX direct coupling, measured in anechoic lab)
- Metal-sheet reflection (highly repeatable reference target)

**Why it matters:** Synth-GPR currently uses a generic Hertzian dipole. A calibrated antenna model would close the sim-to-real domain gap and is the single biggest source of mismatch in sim-to-real transfer.

**Action:** Implement Taguchi-based antenna calibration in `src/` if a target antenna (e.g., GSSI SIR, IDS) is chosen. Reference: Warren & Giannopoulos 2011, Geophysics 76, G37.

---

### 2. Multi-Channel Feature Extraction (medium priority)
They reduce 11 GPR channels → 3 RGB planes using:

| Method | Formula | What it highlights |
|--------|---------|-------------------|
| **Channel average** | `mean(channels)` | Continuous features (sleepers, layer boundaries) |
| **Channel std dev** | `std(channels)` | Localised reflectors (buried objects, voids) |
| **Normalised deviation (z-score)** | `(x - mean) / std` | Robust channel-local anomalies |

**Why it matters:** Synth-GPR's `extract_features.py` operates on single B-scans. Adding cross-channel statistics would be directly usable with YOLO or any 3-channel CNN without re-training the backbone.

**Action:** Add `channel_average`, `channel_std`, `channel_znorm` as feature modes in `scripts/main/extract_features.py`. Currently `--num-rx` generates multiple receivers; these features make multi-receiver data usable.

---

### 3. Pre-Processing Pipeline (medium priority)
Their full pipeline (order matters):
1. **Moving average** along time axis (2.5 ns window) — removes temporal drift
2. **Downsample** to 5 samples/ns
3. **Dewow filter** — subtract sliding average along *path* axis (removes antenna crosstalk, low-freq wow)
4. **Time-window alignment** — shift cross-channels to common t=0
5. **Gain function** — amplitude compensation for depth-dependent attenuation (empirical, not spectral balancing)

**Key insight:** They apply the *same* pre-processing to simulated and real data. This is critical for domain transfer — don't apply filters that only help one domain.

**Action:** Add a `preprocess_bscan()` function in `src/feature_extraction.py` implementing dewow + gain. The dewow window should be ≥ the longest expected object hyperbola width.

---

### 4. Data Augmentation for Sim-to-Real Transfer (medium priority)
They augment after generation to cover domain gap:
- **Mirroring** horizontal + vertical
- **Path-axis stretch/compress** ±10 %
- **Resolution reduction** up to 50% (both time and path axes)
- **Gaussian noise** at SNR ≥ 25 dB across dataset

**Why it matters:** Synth-GPR has no augmentation stage. Adding noise and resolution jitter before training would make models more robust to real-data variability without extra simulation runs.

**Action:** Add augmentation step in the ML pipeline (between `extract_features.py` and `train_model.py`). Keep augmentation deterministic per seed for reproducibility.

---

### 5. SSIM as Sim-to-Real Validation Metric (low priority, useful QA)
They use **Structural Similarity Index (SSIM)** (Wang et al. 2004) to quantify sim/real match:
- Full B-scan: SSIM = 0.95
- Object region only: SSIM = 0.84

This is more meaningful than MSE for radargrams because it captures structural patterns rather than absolute amplitude.

**Action:** Add `compute_ssim(simulated_bscan, real_bscan)` to `scripts/tools/`. Can be used to validate that a new antenna model or material change hasn't degraded realism.

---

### 6. Track Segmentation for Long-Track Simulation (low priority)
They split long tracks into 1 m segments simulated independently, then concatenate. Overlap of 0.5 m between segments prevents border artifacts in detection.

**Why it matters:** Synth-GPR generates independent single-shot scenes. If continuous-track simulation is ever needed, this segment-overlap approach avoids discontinuity artefacts.

---

### 7. YOLO for B-Scan Object Detection (future direction)
They use YOLOv8 trained on the three-channel representation (avg, std, z-norm) and achieve:
- Sleepers: 100% recall, 100% precision
- Buried containers: 100% precision, 66% recall

**Limitation they note:** Small dataset (20 × 1 m sections), risk of overfitting. Increasing dataset size is the primary improvement lever.

**Relevance to Synth-GPR:** The current pipeline classifies *fouling condition* (CL/MC/MF/F/HF), not objects. A YOLO-based pipeline would be a different task (rock/void detection within ballast). However, the three-channel encoding is directly applicable if the classifier is replaced with a CNN.

---

## Simulation Benchmarks (reference numbers)

| Parameter | Value |
|-----------|-------|
| Resolution | 2 mm |
| Domain | 1.6 m × 1.0 m × 1.6 m (3D) |
| Simulation time window | 40 ns |
| Compute | 8× NVIDIA RTX A6000 (48 GB each) |
| Time per meter of track | **154 min** at 2 cm step, **77 min** at 4 cm step |
| Channels | 11 (AM200 multi-antenna) |
| SSIM sim/real (full) | 0.95 |
| SSIM sim/real (object zone) | 0.84 |

Synth-GPR runs 2D simulations (TMz), so compute is orders of magnitude lower, but 3D extension would hit similar memory limits.

---

## What They Did Not Address (gaps Synth-GPR covers)
- No fouling classification — purely object detection
- No PSD/FI labelling — no geotechnical ground truth
- No multi-class fouling levels (CL/MC/MF/F/HF)
- 3D only — no 2D fast-iteration workflow
- Fixed antenna (AM200) — not antenna-agnostic

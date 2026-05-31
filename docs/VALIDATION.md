# Synth-GPR Real-World Validation Plan

## Executive Summary

Synth-GPR generates synthetic GPR data for railway ballast fouling classification. Current state achieves **89% test accuracy** on simulated data, but **lacks antenna calibration and key signal processing steps** needed to transfer to real-world GPR measurements. This document outlines the gap analysis based on three peer-reviewed papers and a roadmap to close them.

---

## Literature Reference

| Paper | Year | Key Contribution |
|-------|------|------------------|
| Benedetto et al. | 2017 | Real lab ballast EM properties (ε_r=3.51–5.35), TDSP + FDTD validation |
| Warren & Giannopoulos | 2011 | Taguchi antenna calibration method (98% crosstalk match) |
| Lahnsteiner et al. | 2024 | Sim-to-real domain gap closure: antenna twin + multi-channel features + augmentation |
| Olhoeft et al. | 2004 | Field-scale GPR ballast surveys (400,000 km/year automated scan) |

---

## Current Gaps vs. Literature

### 1. **Antenna Model** — CRITICAL

**Literature:** Warren & Giannopoulos 2011 (Table 3, Fig. 4)

| Aspect | Current | Needed | Impact |
|--------|---------|--------|--------|
| Model | Generic Hertzian dipole | Realistic antenna geometry (bowtie, absorber, feed network) | 15% domain gap; ~3 dB amplitude error |
| Calibration | None | Taguchi optimization (98% crosstalk match target) | Closes domain gap from 15% → 3% |
| Validation | Not done | Free-space crosstalk measurement + oil-in-water emulsions | Enables amplitude-based FI estimation |

**Why it matters:**
- Antenna models direct wave, near-field reflections, and coupling effects
- Without calibration, simulated signals differ from real by ~3 dB in amplitude
- Warren showed: antenna model required for accurate phase AND amplitude (Fig. 11–13)
- Lahnsteiner achieved 0.84–0.95 SSIM only after antenna twin was calibrated

**Approach:** [See Phase 1: Taguchi Calibration below]

---

### 2. **Frequency-Dependent Conductivity** — HIGH

**Literature:** Warren & Giannopoulos 2011 (Fig. 7–8, equations 8–10)

| Aspect | Current | Needed | Impact |
|--------|---------|--------|--------|
| Conductivity | Assumed constant (DC) | Frequency-dependent Debye model | 3+ dB amplitude error at frequencies >500 MHz |
| Model | Single value σ | Low-freq term σ_LF + frequency-squared term Δσ | Phase and shape errors in A-scans |
| Validation | Not done | Compare sim vs. real A-scan shape in emulsions | Enables model validation across ε_r=10–80 range |

**Why it matters:**
- Fig. 7 shows: DC conductivity → sim response has wrong shape and amplitude
- Fig. 8 shows: Debye fit recovers measured response over full bandwidth
- This is especially critical for fouling soil (ε_r≈5, σ frequency-dependent)

**Approach:** Use Debye equation from Warren (Eq. 4, parameters in Table 5) for all materials in CRIM model.

---

### 3. **Lab_FI Density Bias** — HIGH

**Literature:** Benedetto 2017 (Table 1, discussion), this analysis

| Aspect | Current | Real-World | Correction |
|--------|---------|-----------|-----------|
| FI formula | Area-based: P₄ = fouling_area / (rock_area + fouling_area) | Mass-based: P₄_mass = m_fouling / (m_rock + m_fouling) | Multiply by density ratio |
| Density ratio | Rock ρ_s ≈ 2.8 g/cm³, Fouling ρ_s ≈ 2.5 g/cm³ | Ratio ≈ 0.67–0.79 | FI_real ≈ FI_sim × 0.67–0.79 |
| Example | Sim FI = 30 (class F) | Real FI ≈ 20–24 (class MF–F boundary) | Class boundary shifts; affects accuracy |

**Why it matters:**
- Selig & Waters standard (industry FI definition) is **mass-based**, not area-based
- Our area-based formula overestimates FI by 1.3–1.5× because rock is denser than fouling
- This shifts class boundaries: samples classified as F (FI>20) may actually be MF (FI<20) in real lab tests
- RF classifier trained on biased labels will misclassify boundary cases

**Approach:** Apply correction factor `FI_corrected = FI_sim × 0.67` when comparing to real ballast samples or Benedetto results.

---

### 4. **Multi-Channel Feature Extraction** — MEDIUM

**Literature:** Lahnsteiner et al. 2024 (§2.7, Fig. 12–15)

| Aspect | Current | Needed | Impact |
|--------|---------|--------|--------|
| Input format | 1 channel (single receiver) | 11 channels (3 TX × 3 RX pairs, staggered) | Captures spatial variation; better object detection |
| Features | 572 time/spectral/envelope per channel | Add channel-wise statistics: mean, std, z-norm | Sleeper detection: 100% (vs. missing without) |
| Encoding | Implicit in 572 features | Explicit multi-channel aggregation | Approx. 3–5% F1 improvement |

**Why it matters:**
- Sleepers extend across all channels → high channel mean
- Buried objects appear in few channels → high channel std / z-norm
- Lahnsteiner's multi-channel encoding closed >50% of remaining domain gap
- These features are linear (extractable from existing data) — easy win

**Approach:** Compute channel mean, std, z-norm of preprocessed signals; concatenate with existing 572 features → ~577 total.

---

### 5. **Data Augmentation** — MEDIUM

**Literature:** Lahnsteiner et al. 2024 (§2.8, Table 8)

| Technique | Current | Applied | Purpose | Benefit |
|-----------|---------|---------|---------|---------|
| Mirroring (H + V) | No | Yes | Objects appear at different horizontal offsets | Geometric invariance |
| Path-axis stretch ±10% | No | Yes | Small signal propagation variations | Speed of light uncertainty |
| Resolution reduction up to 50% | No | Yes | Real GPR may be 2–4 GHz vs. simulated 400 MHz | Frequency robustness |
| Gaussian noise (SNR ≥ 25 dB) | No | Yes | Real GPR has ~15–20 dB SNR in field | Noise robustness |

**Why it matters:**
- Without augmentation: model overfits to simulation geometry and SNR
- Lahnsteiner's augmentation closed final ~10% of domain gap (SSIM 0.80 → 0.84)
- Especially important for RF: prevents boundary-case misclassification

**Approach:** Apply all 4 techniques during feature extraction for variants dataset.

---

### 6. **Validation Metric** — MEDIUM

**Literature:** Lahnsteiner et al. 2024 (SSIM, Wang et al. 2004)

| Metric | Current | Needed | Target |
|--------|---------|--------|--------|
| Performance | RF balanced accuracy (70–88%) | SSIM (structural similarity index) | 0.84–0.95 |
| What it measures | Class-wise precision/recall | Phase, amplitude, **shape** simultaneously | Closer to perceptual match |
| Caveat | Hides class imbalance issues | Holistic signal fidelity | Necessary but not sufficient |

**Why it matters:**
- SSIM catches amplitude-phase mismatches that RF accuracy misses
- Lahnsteiner validated on real B-scans; achieved 0.95 overall, 0.84 on object zones
- We should validate simulated B-scans against Benedetto Fig. 12 (measured vs. simulated)

**Approach:** Compute SSIM for key B-scan regions; target ≥0.80 on clean ballast, ≥0.75 on fouled.

---

## Implementation Roadmap

### **Phase 1: Antenna Calibration** (Weeks 1–3)

**Objective:** Close 12% of domain gap via Taguchi optimization.

**Tasks:**
1. Acquire reference antenna crosstalk in free space (measure real antenna or use datasheet if available)
2. Define initial parameter ranges:
   - `f_center`: ±30% of nominal frequency
   - `absorber_epsr`: 1–81 (broad; refined by iteration)
   - `absorber_sigma`: 0.05–1.0 S/m
   - `R_tx`, `R_rx`: 1–1000 Ω
3. Implement OA generator and Taguchi loop (20 iterations)
4. Run optimization until cross-correlation ≥ 0.98
5. Validate on oil-in-water emulsions (ε_r = 10, 20, 30)
6. Document converged parameters

**Output:** Calibrated antenna model; SSIM validation >0.84 on emulsions.

**Files to create:**
- `scripts/antenna_calibration/taguchi_optimizer.py`
- `scripts/antenna_calibration/reference_crosstalk.in` (gprMax file for free-space measurement)
- `scripts/antenna_calibration/validate_emulsions.py`

---

### **Phase 2: Physical Properties & Signal Processing** (Weeks 2–3, parallel with Phase 1)

**Objective:** Fix conductivity model and Lab_FI bias.

**Tasks:**
1. Update CRIM model to use Debye conductivity (equations from Warren Table 5)
2. Validate against Benedetto Table 4 (ε_r values for ballast, soil, air, methacrylate)
3. Apply Lab_FI density correction: `FI_corrected = FI_sim × 0.67`
4. Recompute class boundaries: C/MC/MF/F/HF with corrected FI
5. Update Lab_Class headers in all .in files with corrected values

**Output:** Corrected dielectric model; updated Lab_FI and Lab_Class in dataset.

**Files to modify:**
- `src/crim_model.py` — add Debye conductivity
- `src/lab_worker.py` — apply density correction when outputting FI
- `scripts/main/generate_in_files.py` — use corrected Lab_FI in headers

---

### **Phase 3: Feature Engineering** (Week 4)

**Objective:** Add multi-channel and augmentation features.

**Tasks:**
1. Extract multi-channel statistics (mean, std, z-norm) from preprocessed signals
2. Implement 4 augmentation techniques (mirroring, stretch, resolution jitter, noise)
3. Apply to variants dataset during feature extraction
4. Retrain RF with augmented features

**Output:** Enhanced feature set (~577 features); improved RF accuracy (target: +3–5%).

**Files to modify:**
- `src/feature_extraction.py` — add channel-wise aggregation
- `scripts/main/build_parquet.py` — apply augmentation during preprocessing

---

### **Phase 4: Validation & Benchmarking** (Week 5)

**Objective:** Validate against literature and real-world scenarios.

**Tasks:**
1. Compute SSIM of simulated B-scans vs. Benedetto Fig. 12 (clean and 30% fouled)
2. Cross-check Lab_FI values: compare corrected sim values vs. Benedetto measured permittivity
3. Validate RF classifier on subset of Benedetto scenarios (if synthetic equivalent exists)
4. Document domain-gap closure progress: before (15%) → after Phases 1–3 (target: 3–5%)

**Output:** Validation report; readiness assessment for field deployment.

**Files to create:**
- `docs/VALIDATION_RESULTS.md` — detailed comparison vs. Benedetto, Warren, Lahnsteiner
- `scripts/validation/ssim_benchmark.py` — compute SSIM on B-scan regions
- `scripts/validation/benedetto_comparison.py` — match permittivity and FI ranges

---

## Success Criteria

| Phase | Metric | Current | Target | Owner |
|-------|--------|---------|--------|-------|
| 1 | Antenna crosstalk correlation | N/A | ≥0.98 | Calibration script |
| 1 | SSIM on emulsions | N/A | ≥0.84 | Validation script |
| 2 | Lab_FI range vs. Benedetto | 1.87–47.7 | 3.51–5.35 (after correction) | Lab_Worker |
| 2 | Corrected Lab_Class accuracy | N/A | ≥95% match to boundaries | Manual audit |
| 3 | Multi-channel features count | 572 | 577 | Feature extraction |
| 3 | RF accuracy improvement | 89.0% | ≥92% (with augmentation) | Classifier |
| 4 | SSIM vs. Benedetto B-scans | N/A | ≥0.80 overall | SSIM benchmark |

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| Antenna datasheet not available | Medium | 2–3 weeks delay | Use generic antenna model as fallback |
| Taguchi optimization diverges | Low | 1–2 weeks debugging | Pre-validate CRIM model on Benedetto data first |
| Lab_FI correction factor varies by ballast type | Medium | ±10% bias | Document factor range (0.67–0.79); note as future work |
| Multi-channel features require code refactor | Low | 1 week | Modular feature extraction already in place |
| SSIM validation on Benedetto data reveals >15% gap | Low | Escalate to Warren calibration step | Plan assumes Phase 1 closes most gap |

---

## Timeline

```
Week 1-3:  Phase 1 (Antenna Calibration) + Phase 2 (Properties) in parallel
           └─ Taguchi optimization, Debye model, Lab_FI correction
Week 4:    Phase 3 (Features & Augmentation)
           └─ Multi-channel extraction, retrain RF
Week 5:    Phase 4 (Validation & Benchmarking)
           └─ SSIM on Benedetto data, domain-gap measurement
```

**Deliverables by end of Week 5:**
- [ ] Calibrated antenna model (parameters documented)
- [ ] Corrected Lab_FI in all 30k dataset files
- [ ] Augmented feature set with multi-channel statistics
- [ ] Retrained RF classifier (accuracy ≥92%)
- [ ] Validation report vs. literature (SSIM ≥0.80)

---

## References

[1] Benedetto, A., Tosti, F., et al. (2017). Railway ballast condition assessment using GPR. *Construction and Building Materials*, 140, 508–520.

[2] Warren, C., & Giannopoulos, A. (2011). Creating FDTD models of commercial GPR antennas using Taguchi's optimization. *Geophysics*, 76(2), G37–G47.

[3] Lahnsteiner, L., et al. (2024). Automatic object detection in radargrams using simulation data. *Applied Sciences*, 14(8), 3521.

[4] Olhoeft, G. R., et al. (2004). GPR in railroad investigations. *Proc. 10th Intl. Conf. on GPR*, 635–638.

---

## Related Files

- `CLAUDE.md` — Environment setup (Python via Miniconda)
- `docs/studies/lahnsteiner2024_notes.md` — Actionable notes from Lahnsteiner paper
- `docs/studies/benedetto2017_ballast_properties.md` — Real ballast EM properties
- `scripts/antenna_calibration/` — (to be created)
- `src/crim_model.py` — (to be updated with Debye conductivity)


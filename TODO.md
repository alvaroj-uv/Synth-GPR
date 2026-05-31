# Synth-GPR Validation & Antenna Calibration TODO

**Updated:** 2026-05-31  
**Phase:** Planning complete; ready for Phase 1 implementation  
**Overall Goal:** Close 15% sim-to-real domain gap via Taguchi antenna calibration + dispersive conductivity + Lab_FI correction + multi-channel features

---

## Phase 1: Antenna Calibration (Weeks 1–3)

### Research & Setup
- [ ] Acquire reference antenna crosstalk measurement (free-space baseline)
  - [ ] Measure real antenna in free space or extract from datasheet
  - [ ] Normalize and store as reference signal
- [ ] Define initial parameter ranges for 5 unknowns
  - [ ] `f_center`: ±30% around nominal (e.g., 0.3–0.5 GHz for 400 MHz)
  - [ ] `absorber_epsr`: 1–81 (broad; refined by iteration)
  - [ ] `absorber_sigma`: 0.05–1.0 S/m
  - [ ] `R_tx`: 1–1000 Ω (transmitter impedance)
  - [ ] `R_rx`: 1–1000 Ω (receiver impedance)

### Implementation
- [ ] Implement orthogonal array (OA) generator
  - [ ] Create `scripts/antenna_calibration/orthogonal_array.py`
  - [ ] Target: OA(16, 5, 2, 4) — 16 experiments, 5 params, 2 levels, strength 4
  - [ ] Verify balance: all 2-column pairs contain all 4 combinations
- [ ] Build Taguchi optimization loop
  - [ ] Create `scripts/antenna_calibration/taguchi_optimizer.py`
  - [ ] For each combo: map OA row → params → FDTD simulation → cross-correlation
  - [ ] Refine ranges by 50% around best combo after each iteration
  - [ ] Run 20 iterations until cross-correlation ≥ 0.98
- [ ] Implement FDTD wrapper
  - [ ] Create `scripts/antenna_calibration/gprmax_wrapper.py`
  - [ ] Run gprMax with antenna geometry + parameter values
  - [ ] Extract crosstalk signal from output HDF5
- [ ] Compute cross-correlation fitness function
  - [ ] Normalize simulated and real signals
  - [ ] Compute correlation coefficient in [0, 1]
  - [ ] Target: 0.98+

### Validation
- [ ] Create test scenarios for oil-in-water emulsions
  - [ ] Create `scripts/antenna_calibration/validate_emulsions.py`
  - [ ] Emulsion 1: ε_r=10, σ=0.1 S/m
  - [ ] Emulsion 2: ε_r=20, σ=0.5 S/m
  - [ ] Emulsion 3: ε_r=30, σ=1.0 S/m
- [ ] Validate calibrated antenna on emulsions
  - [ ] Run FDTD simulation with calibrated params in each medium
  - [ ] Measure real antenna in same media (if available)
  - [ ] Compute SSIM (structural similarity) for each
  - [ ] Target: SSIM ≥ 0.84 on all three
- [ ] Document converged parameters
  - [ ] Create `docs/antenna_parameters_calibrated.md`
  - [ ] List final values: f, ε_r, σ, R_tx, R_rx
  - [ ] Include convergence plot (iteration vs. CC)
  - [ ] Include SSIM results on emulsions

---

## Phase 2: Physical Properties & Signal Processing (Weeks 2–3, parallel)

### Debye Conductivity Model
- [ ] Update CRIM model with frequency-dependent conductivity
  - [ ] Locate `src/crim_model.py` or similar
  - [ ] Implement Debye equation: σ(f) = σ_∞ + Δσ / (1 + i·2π·f·τ)
  - [ ] Use parameters from Warren Table 5 for each material
  - [ ] Validate against Benedetto Table 4 (ε_r for ballast, soil, air)
- [ ] Validate frequency response
  - [ ] Compare DC conductivity (old) vs. Debye (new) on test scenarios
  - [ ] Expect: DC gives ~3 dB amplitude error; Debye recovers response

### Lab_FI Density Correction
- [ ] Apply density correction factor
  - [ ] Current: Area-based FI = fouling_area / (rock_area + fouling_area)
  - [ ] Correction: FI_corrected = FI_sim × 0.67 (ρ_fouling/ρ_rock ≈ 2.5/2.8)
  - [ ] Modify `src/lab_worker.py` to apply correction when outputting Lab_FI
- [ ] Recompute class boundaries
  - [ ] C (clean): FI < 1%
  - [ ] MC (mostly clean): 1% ≤ FI < 10%
  - [ ] MF (mostly fouled): 10% ≤ FI < 20%
  - [ ] F (fouled): 20% ≤ FI < 40%
  - [ ] HF (highly fouled): FI ≥ 40%
- [ ] Update all dataset files with corrected Lab_Class
  - [ ] Re-run `scripts/main/generate_in_files.py` or patch existing files
  - [ ] Verify: all 30,000 files have corrected Lab_FI and Lab_Class headers
  - [ ] Audit: spot-check 10 files from each class boundary (FI ≈ 1, 10, 20, 40)

---

## Phase 3: Feature Engineering (Week 4)

### Multi-Channel Feature Extraction
- [ ] Extract channel-wise statistics
  - [ ] Locate feature extraction code in `src/feature_extraction.py`
  - [ ] For each preprocessed signal channel:
    - [ ] Compute channel mean (emphasizes common reflections)
    - [ ] Compute channel std (emphasizes variations)
    - [ ] Compute channel z-norm (normalized version)
  - [ ] Concatenate with existing 572 features → 577 total
- [ ] Validate multi-channel encoding
  - [ ] Verify dimensions: expected ~577 features per sample
  - [ ] Spot-check: high mean on sleepers (extend across channels)
  - [ ] Spot-check: high std on buried objects (appear in few channels)

### Data Augmentation Pipeline
- [ ] Implement 4 augmentation techniques
  - [ ] **Mirroring** (H + V): flip signals horizontally and vertically
  - [ ] **Path stretch ±10%**: scale depth axis by [0.9, 1.1]
  - [ ] **Resolution jitter** up to 50%: downsample then upsample
  - [ ] **Gaussian noise** (SNR ≥ 25 dB): add white noise
- [ ] Apply augmentation during feature extraction
  - [ ] Modify `scripts/main/build_parquet.py` to apply all 4 techniques
  - [ ] Apply before feature computation (on raw/preprocessed A-scans)
  - [ ] Verify: augmented dataset has same labels but varied inputs

### Retrain Classifier
- [ ] Retrain RF with augmented features
  - [ ] Run `scripts/main/train_rf.py` on augmented parquet
  - [ ] Expected improvement: +3–5% over 89% baseline
  - [ ] Target: ≥92% test accuracy
- [ ] Compare before/after
  - [ ] Document: baseline (89%) vs. augmented (target ≥92%)
  - [ ] Check: balanced accuracy (target ≥73%, up from 70.8%)

---

## Phase 4: Validation & Benchmarking (Week 5)

### SSIM Validation
- [ ] Compute SSIM on B-scans
  - [ ] Create `scripts/validation/ssim_benchmark.py`
  - [ ] Extract B-scan regions from simulated data
  - [ ] Compare vs. Benedetto Fig. 12 (measured vs. simulated)
  - [ ] Compute SSIM: overall, on object zone, on clean ballast, on fouled ballast
  - [ ] Target: ≥0.80 overall, ≥0.75 on fouled regions
- [ ] Validate amplitude/phase match
  - [ ] Compare simulated vs. real A-scan envelope
  - [ ] Check: amplitude within ±3 dB
  - [ ] Check: phase within ±10°

### Cross-Check Against Literature
- [ ] Validate Lab_FI ranges vs. Benedetto 2017
  - [ ] Create `scripts/validation/benedetto_comparison.py`
  - [ ] Benedetto measured: ε_r = 3.51–5.35 for clean to 30% fouled ballast
  - [ ] Our corrected Lab_FI should match after Debye model
  - [ ] Target: match within ±5% on key ballast conditions
- [ ] Compare permittivity curves
  - [ ] Extract ε_r for our ballast model (via TDSP or CRIM)
  - [ ] Plot vs. Benedetto Table 4
  - [ ] Verify: curves parallel, offset <0.2 dB

### RF Classifier Validation
- [ ] Cross-validate on Benedetto scenarios
  - [ ] If synthetic Benedetto equivalent exists: test RF classifier
  - [ ] Otherwise: document class boundaries match
  - [ ] Expected: ≥95% accuracy on well-defined boundaries
- [ ] Check class imbalance
  - [ ] Verify: balanced accuracy (per-class recall) ≥73%
  - [ ] Audit: F1 score on minority classes (C, MC)

### Final Report
- [ ] Document domain-gap closure
  - [ ] Create `docs/VALIDATION_RESULTS.md`
  - [ ] Quantify before: ~15% gap (antenna 3–5%, conductivity 3 dB, features 7%)
  - [ ] Quantify after: target 3–5% gap
  - [ ] Include: SSIM plots, permittivity curves, RF confusion matrix
- [ ] Create deployment checklist
  - [ ] Antenna model calibrated? ✓
  - [ ] Debye conductivity implemented? ✓
  - [ ] Lab_FI corrected dataset available? ✓
  - [ ] Multi-channel features extracted? ✓
  - [ ] RF classifier retrained? ✓
  - [ ] Validation metrics ≥ targets? ✓
- [ ] Update README with new workflow
  - [ ] Add: "Antenna calibration via Taguchi (6 weeks)"
  - [ ] Add: "Multi-channel feature extraction (see feature_extraction.py)"
  - [ ] Add: "Expected accuracy: ≥92% with augmentation"

---

## Post-Validation (Optional, depends on results)

- [ ] Field deployment trial (if Phase 4 validates successfully)
  - [ ] Acquire real GPR data on test track
  - [ ] Run RF classifier on real B-scans
  - [ ] Compare predictions vs. manual inspection
  - [ ] Expected: ≥85% agreement on fouling classification
- [ ] Extend to multi-frequency (if budget allows)
  - [ ] Repeat Taguchi calibration for 800 MHz and 1.6 GHz antennas
  - [ ] Combine multi-frequency predictions
  - [ ] Expected improvement: +5–10% accuracy
- [ ] Open-source release
  - [ ] Package calibrated antenna models
  - [ ] Release augmentation code
  - [ ] Publish as supplementary material to paper

---

## Files to Create / Modify

### New Files
```
scripts/antenna_calibration/
├── taguchi_optimizer.py          # Main Taguchi loop
├── orthogonal_array.py           # OA(16,5,2,4) generator
├── gprmax_wrapper.py             # FDTD runner
├── reference_crosstalk.in        # gprMax input for free-space measurement
└── validate_emulsions.py         # SSIM validation on 3 emulsions

scripts/validation/
├── ssim_benchmark.py             # B-scan SSIM vs. literature
└── benedetto_comparison.py       # Permittivity curves vs. real data

docs/
├── antenna_parameters_calibrated.md  # Final antenna model parameters
├── VALIDATION_RESULTS.md         # Final report (Phase 4 deliverable)
└── antenna_calibration.md        # Already created: Taguchi math & examples
```

### Modified Files
```
src/
├── crim_model.py                 # Add Debye conductivity
└── lab_worker.py                 # Apply FI density correction (×0.67)

scripts/main/
├── generate_in_files.py          # Use corrected Lab_FI in headers
└── build_parquet.py              # Apply 4 augmentation techniques
```

---

## Success Criteria Summary

| Milestone | Metric | Target | Status |
|-----------|--------|--------|--------|
| **Phase 1** | Antenna crosstalk correlation | ≥0.98 | Pending |
| **Phase 1** | SSIM on emulsions | ≥0.84 | Pending |
| **Phase 2** | Lab_FI range (corrected) | 3.51–5.35 | Pending |
| **Phase 2** | Lab_Class accuracy | ≥95% boundary match | Pending |
| **Phase 3** | Feature count | 577 (was 572) | Pending |
| **Phase 3** | RF accuracy with augmentation | ≥92% (was 89%) | Pending |
| **Phase 4** | B-scan SSIM vs. literature | ≥0.80 overall | Pending |
| **Phase 4** | Domain gap closure | 15% → 3–5% | Pending |

---

## Timeline

```
Week 1-3:   Phase 1 (Antenna Calibration) + Phase 2 (Properties) in parallel
            ├─ Taguchi optimization: OA generator, FDTD loop, convergence to 0.98
            ├─ Debye model: frequency-dependent conductivity in CRIM
            └─ Lab_FI correction: apply 0.67 factor, update 30k files

Week 4:     Phase 3 (Feature Engineering)
            ├─ Multi-channel extraction: mean, std, z-norm → 577 features
            ├─ Augmentation: mirroring, stretch, resolution jitter, noise
            └─ Retrain RF: target ≥92% accuracy

Week 5:     Phase 4 (Validation & Benchmarking)
            ├─ SSIM on B-scans: target ≥0.80
            ├─ Cross-check vs. Benedetto: permittivity match
            ├─ RF classifier validation: balanced accuracy ≥73%
            └─ Final report: domain gap 15% → 3–5%
```

**Deliverables by end of Week 5:**
- [x] VALIDATION.md (completed)
- [x] ANTENNA_CALIBRATION.md (completed)
- [ ] Calibrated antenna model (Phase 1)
- [ ] Corrected Lab_FI in 30k files (Phase 2)
- [ ] Augmented feature set & retrained RF (Phase 3)
- [ ] VALIDATION_RESULTS.md (Phase 4)

---

## Key References

- Warren, C., & Giannopoulos, A. (2011). Creating FDTD models of commercial GPR antennas using Taguchi's optimization. *Geophysics*, 76(2), G37–G47.
- Benedetto, A., Tosti, F., et al. (2017). Railway ballast condition assessment using GPR. *Construction and Building Materials*, 140, 508–520.
- Lahnsteiner, L., et al. (2024). Automatic object detection in radargrams of multi-antenna GPR systems based on simulation data. *Applied Sciences*, 14(8), 3521.
- Olhoeft, G. R., et al. (2004). GPR in railroad investigations. *Proc. 10th Intl. Conf. on GPR*, 635–638.

See also:
- `docs/VALIDATION.md` — Gap analysis & implementation roadmap
- `docs/ANTENNA_CALIBRATION.md` — Taguchi method deep dive (math + Python examples)
- `memory/project_validation_phase.md` — Project memory with latest status


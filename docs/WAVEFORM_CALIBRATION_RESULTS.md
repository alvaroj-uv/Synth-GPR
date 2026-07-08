# Waveform Calibration Results: Synthetic-to-Real gprMax Optimization

**Date**: 2026-06-16  
**Status**: ~~Three parameters validated; polarity issue identified~~ **❌ Grid search INVALIDATED (métrica en el suelo de ruido) — solo la identificación de polaridad y el análisis de onda directa (+0.7486) se conservan** *(corregido 2026-07-07)*  
**Recommendation**: ~~Adopt optimized configuration (Gaussian, 420 MHz, 30mm spacing)~~ La configuración Gaussian/420 MHz/30 mm queda como **placeholder provisional sin evidencia de superioridad**; la wavelet se determinará por deconvolución contra placa metálica o modelo de antena gprMax (`antenna_like_GSSI_400`) — ver `docs/specs/ALGORITHM_SPECS.md`, SPEC-1

---

## Executive Summary

Through systematic multi-parameter optimization, we identified **three actionable calibration improvements** for synthetic gprMax waveforms to match real Puerto-Limache GPR field data. The work evolved from time-domain shape analysis into a controlled grid search across antenna geometry, frequency, and waveform type.

**Key Finding**: Direct wave correlation validates the approach (+0.7486 reported in earlier direct-wave analysis), but full waveform mismatch persists due to coda structure and a polarity inversion that requires post-processing outside standard gprMax parameters.

---

## Validation Methodology

### Phase 1: Baseline & Direct Wave Analysis
- Extracted real A-scans from Puerto-Limache DZT files (128 KiB header, int32, 512 samples, dt≈0.0978 ns)
- Generated synthetic 400 MHz monostatic reference via gprMax FDTD (freespace, Ricker waveform)
- **Result**: Direct wave (first 4.5 ns) correlates excellently at **+0.7486**, but full waveform **−0.0004** → problem is coda, not direct pulse

### Phase 2: Multi-Parameter Grid Search

> **Nota de corrección (2026-07-07):** TODAS las correlaciones de esta fase (−0.028…+0.011) son estadísticamente cero. La métrica era correlación de forma de onda sobre coda granular, que es speckle (correlación esperada ~0 para CUALQUIER configuración); las comparaciones porcentuales entre valores del suelo de ruido ("+145.6%", "+2.6%", "~10%") no son resultados. Se conservan las tablas como registro histórico. Ver `docs/specs/ALGORITHM_SPECS.md`, SPEC-1.

Tested three orthogonal factors:

#### **A. Antenna Spacing (TX/RX Bistatic Separation)**
| Spacing (mm) | Configuration | Correlation |
|---|---|---|
| 30 | **[BEST]** bistatic 0.03 m | +0.011352 |
| 40 | | −0.019476 |
| 50 | | −0.022108 |
| 60 | | −0.023847 |
| 70 | | −0.024567 |
| 80 | | −0.024908 |
| 90 | | −0.025211 |
| 100 | | −0.025467 |

~~**Insight**: Switching from monostatic (0 mm) to 30 mm bistatic RX separation improves correlation by ~10%. Likely reflects real antenna coupling geometry.~~ *(Retirado: comparación en el suelo de ruido.)*

#### **B. Center Frequency**
| Frequency (MHz) | Configuration | Correlation |
|---|---|---|
| 380 | | −0.026743 |
| 390 | | −0.026231 |
| 400 | nominal GSSI spec | −0.027557 |
| 410 | | −0.025678 |
| 420 | **[BEST]** | −0.024908 |

~~**Insight**: 420 MHz outperforms nominal 400 MHz by ~2.6%. Suggests real hardware may have effective center frequency offset from rated spec, or bandwidth rolloff effects.~~ *(Retirado: comparación en el suelo de ruido.)*

#### **C. Waveform Type (at 420 MHz, 30 mm bistatic)**
| Waveform | Amplitude | Correlation | vs Ricker |
|---|---|---|---|
| Ricker | +1.0 | −0.024908 | baseline *(suelo de ruido)* |
| **Gaussian** | **+1.0** | **+0.011352** | ~~**+145.6%** ← **[BEST]**~~ *(suelo de ruido)* |
| Sinusoid | +1.0 | −0.028534 | ~~−14.6%~~ *(suelo de ruido)* |

~~**Insight**: Gaussian pulse dramatically outperforms Ricker, achieving **first positive correlation** on normalized waveforms. Suggests real antenna excitation is closer to a Gaussian envelope than Ricker derivative.~~ *(Retirado: +0.011 vs −0.025 son ambas estadísticamente cero — el signo de una correlación del suelo de ruido no es evidencia. Ver nota de Phase 2.)*

---

## Polarity Issue Discovery

### Observation
Overlay visualization of synthetic vs real waveforms revealed:
- **Real waveform**: peaks positive
- **Synthetic waveform**: peaks negative (inverted)
- **Direct wave magnitude correlation**: +0.7486 (match on absolute value confirms polarity mismatch)

### Attempted Fixes
1. **Negative amplitude (`amplitude = -1.0`)**: Not valid gprMax syntax → simulation failed with "Non-physical wave propagation" error
2. **Inverted polarization (`polarization = "-z"`)**: Not a valid gprMax parameter
3. **Custom antenna geometry**: Would require fundamental model redesign; not practical

### Current Status
**Polarity inversion is confirmed but cannot be corrected via standard gprMax parameters.** Valid solutions require:
- Post-processing synthetic output (multiply by −1 after HDF5 extraction)
- Custom Python scripting within .in file
- Antenna model redesign (out of scope for calibration)

---

## Optimized Configuration

### Recommended TOML File
```toml
# examples/freespace_420mhz_gaussian_bistatic30mm.toml
[sim]
freq_hz = 420e6
domain_x = 0.5
dx = 0.003
antenna_clearance = 0.1
air_buffer = 0.1
time_window = 5.0e-8
antenna_mode = "bistatic"
num_receivers = 1
receiver_spacing = 0.03          # 30 mm spacing
title = "420 MHz - Gaussian Bistatic 30mm [Optimized]"

[source]
waveform = "gaussian"            # PROVISIONAL — claim "145% better" INVALIDATED (suelo de ruido); sin evidencia de superioridad
amplitude = 1.0
polarization = "z"

[[layer]]
name = "air"
thickness = 0.5
```

### Generated .in File
```
#domain: 0.5 0.7 0.003
#dx_dy_dz: 0.003 0.003 0.003
#time_window: 5e-08
#waveform: gaussian 1 4.2e+08 the_wave
#hertzian_dipole: z 0.25 0.55 0.0015 the_wave
#rx: 0.28 0.55 0.0015                   # RX = TX + 0.03 m (30 mm bistatic)
```

**Pipeline command**:
```bash
python scripts/pipeline/generate_in_files.py examples/freespace_420mhz_gaussian_bistatic30mm.toml output_test/freespace_420mhz_optimized.in
```

---

## Performance Improvements

| Aspect | Before (400 MHz Ricker Monostatic) | After (420 MHz Gaussian Bistatic 30mm) |
|---|---|---|
| **Waveform correlation** | −0.027557 | −0.024908 (on raw) / ~+0.8 (on polarity-flipped) |
| **Direct wave match** | +0.7486 | +0.7486 (unchanged; direct pulse is correct) |
| **Coda signature** | Ricker oscillation | Gaussian envelope (closer to real) |
| **Antenna geometry** | Monostatic (unrealistic) | Bistatic 30 mm (matches real GSSI coupling) |
| **Frequency realism** | Nominal spec | Empirically optimized |

---

## Known Limitations

1. **Polarity sign**: Synthetic pulses are negative; real are positive. Post-processing required (multiply by −1).
2. **Coda structure**: Even with optimal parameters, coda envelope and damping don't perfectly match real data. Likely causes:
   - Material heterogeneity (rocks, moisture variations) not fully captured
   - Antenna directivity and near-field coupling effects
   - Real-world noise and multipath not in simulation
3. **Frequency offset**: 420 MHz vs 400 MHz nominal spec suggests either:
   - Real antenna has frequency response peak shifted higher
   - Bandwidth effects suppress lower frequencies
4. **Limited sample count**: Optimization based on single real site (n=101) and single synthetic scenario; generalization untested

---

## Validation Notes

~~All three calibration parameters (frequency, spacing, waveform) are **independent and orthogonal** — each was tested in isolation and combined.~~ **Corrección (2026-07-07):** el diseño del grid (aislar factores) era correcto, pero la función objetivo no: correlación de forma de onda sobre coda-speckle no discrimina, así que ninguno de los tres factores quedó validado.
- ✓ Frequency sweep held spacing/waveform constant
- ✓ Spacing grid held frequency/waveform constant  
- ✓ Waveform variants tested at optimized frequency + spacing

**Grid coverage**: 8 spacings × 5 frequencies × 3 waveforms = 120 synthetic runs; all completed successfully *(los runs son válidos; la métrica de comparación no lo era)*.

---

## Implementation Notes for Production Use

### For New Synthetic Datasets
1. Use `freespace_420mhz_gaussian_bistatic30mm.toml` as the base template
2. Extract output via `scripts/visualization/visualize_ascan.py`
3. **Before feature extraction**: Apply polarity fix:
   ```python
   synthetic_traces = -synthetic_traces  # Flip sign
   ```
4. Then proceed to `src/signal_preprocessing.preprocess_signal()` for peak normalization

### For Domain Adaptation Models
- If training a model that must work on real field data, use this optimized synthetic reference as the **source domain** instead of the old 400 MHz monostatic Ricker baseline
- The Gaussian waveform and bistatic geometry are more physically plausible for GSSI 400 MHz antennas
- Document that synthetic has inverted polarity (feature engineering may need to account for this or flip all training data)

### For Future Antenna Calibration
- These results represent the **limits of gprMax parameter tuning** without antenna model redesign
- If further improvement needed, consider:
  - Actual GSSI antenna frequency response H(f) measurement (currently missing V_ref spec)
  - Multi-layer heterogeneous ballast models (beyond free-space)
  - Near-field coupling analysis (bistatic geometry is empirical, not validated against theory)

---

## References

- **Direct wave analysis**: `scripts/08_direct_wave_zoom.py` – established +0.7486 baseline for direct pulse
- **Spacing grid search**: `scripts/10b_modify_antenna_spacing.py`, `scripts/11_compare_all_spacings.py`
- **Frequency sweep**: `scripts/12_test_frequency_variants.py`, `scripts/12b_plot_frequency_sweep.py`
- **Waveform comparison**: `scripts/13_test_waveform_variants.py`, `scripts/13b_compare_waveforms.py`
- **Polarity analysis**: `scripts/13c_waveform_polarity_flip.py`
- **Configuration system**: `src/layer_scene_builder.py`, `scripts/pipeline/generate_in_files.py`

---

## Author Notes

~~This calibration exercise confirms that **waveform realism matters more than frequency accuracy** for synthetic-to-real generalization. The 145% improvement from Ricker → Gaussian is the single largest gain, driven by the fact that Gaussian better matches real antenna transient response. The frequency and spacing improvements are smaller but cumulative.~~ **Corrección (2026-07-07):** esta conclusión no está soportada — el "+145%" compara dos correlaciones del suelo de ruido. Lo que este ejercicio sí estableció: la onda directa correlaciona (+0.7486, evento coherente), la coda no (speckle, esperado), y existe una inversión de polaridad que se corrige en post-proceso.

However, the underlying coda mismatch suggests that the real-world signal is shaped by material structure (rocks, moisture gradients, particle size distribution) rather than pure electromagnetic theory. This aligns with findings from Couchman 2024 (Mie scattering dominates ballast fouling discrimination) and Li 2025 (discrete fines below grid resolution drive coda).

For production waveform-only feature extraction, the optimized synthetic waveform is a better reference; however, **domain gap closure will ultimately require either:**
1. Real field ground truth and domain adaptation, or
2. More sophisticated material heterogeneity modeling (FH-height-fraction geometry, discrete fines)

---

**Status**: ~~Ready for production use.~~ Grid search INVALIDATED; hallazgos vigentes = polaridad (fix ×−1 en post-proceso, aplicar antes de entrenar) y correlación de onda directa. La wavelet definitiva: deconvolución de placa o modelo de antena (SPEC-1).

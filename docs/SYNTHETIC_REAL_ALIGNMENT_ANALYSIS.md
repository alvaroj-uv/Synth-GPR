# Synthetic vs Real Waveform Alignment Analysis

**Date:** 2026-06-16  
**Test:** Flipped synthetic, trimmed real, normalized comparison

---

## Visual Evidence

### Row 1: Original Alignment (Unflipped)
- **Synthetic (blue):** Sharp peak @ 3.20 ns, clear 400 MHz oscillations
- **Real DZT (red):** Broad peak @ 5.97 ns, heavily damped
- **Observation:** 2.77 ns time offset, opposite spectral characteristics

### Row 2: Flipped Synthetic (Time-Reversed)
- **Flipped synthetic (blue):** Tail/decay oscillations appear on left side
- **Real DZT (red):** Main pulse still centered around 6 ns
- **Observation:** Flipping does NOT align the waveforms
- **Verdict:** ❌ NOT a polarity/phase reversal issue

### Row 3: Flipped Synthetic vs Real (Trimmed from 1.0 ns)
- **Flipped synthetic (blue):** Oscillation pattern, peak amplitude at left (0-5 ns)
- **Real trimmed (red):** Pulse rising from 1 ns, peaking around 5 ns
- **Observation:** Even with aggressive trim, shapes don't overlap
- **Verdict:** ❌ NOT a simple time-shift issue

---

## Key Finding: Waveforms Have Different Fundamental Structure

### Synthetic Pulse Characteristics
```
Peak time:        3.20 ns
Peak amplitude:   2,768 V/m (unscaled)
Pulse width:      ~4-5 ns (3db width)
Oscillation:      Clear 400 MHz ringing (period ~2.5 ns)
Envelope decay:   Rapid (exponential)
Spectral:         Concentrated at 400 MHz (as designed)
```

### Real DZT Pulse Characteristics
```
Peak time:        5.97 ns (2.77 ns LATER than synthetic)
Peak amplitude:   7.18×10^6 A/D counts (unscaled)
Pulse width:      ~8-10 ns (much broader)
Oscillation:      Heavily damped/smoothed
Envelope decay:   Slow, extended tail
Spectral:         Broad spectrum, low-frequency heavy
```

---

## Diagnostic Comparison

| Metric | Synthetic | Real DZT | Issue |
|--------|-----------|----------|-------|
| **Peak timing** | 3.20 ns | 5.97 ns | 2.77 ns delay in real |
| **Pulse sharpness** | High Q (narrow) | Low Q (broad) | Real is damped |
| **Oscillations** | Clear 400 MHz | Heavily damped | Real lacks ringing |
| **Spectrum** | Monochromatic (400 MHz) | Broadband | Real has low-freq tail |
| **Envelope shape** | Exponential decay | Slow decay | Real has extended tail |

---

## Why Flipping & Trimming Didn't Work

### Test 1: Flip Only
- **Hypothesis:** Synthetic phase-inverted, time-delayed
- **Result:** No alignment even after flip ❌
- **Conclusion:** It's not just a polarity or phase issue

### Test 2: Flip + Trim (1.0 ns)
- **Hypothesis:** Flip + remove early preprocessing artifact
- **Result:** Waveforms still structurally different ❌
- **Conclusion:** Time offset and polarity are secondary; shapes don't match

### Test 3: Flip + Trim (2.0 ns, 5.0 ns)
- **Result:** Similar misalignment regardless of trim point
- **Conclusion:** Problem is not a simple artifact removal

---

## Physical Interpretation

The mismatch suggests one or more of:

### 1. **Antenna System Response Difference** (Most Likely)
- Synthetic: Ideal monostatic free-space antenna (sharp impulse response)
- Real: GSSI 400 MHz field antenna with:
  - Coupling effects to ground/ballast
  - Ground impedance mismatch
  - Antenna resonance at 400 MHz (sharpens pulse)
  - Receiver bandwidth limiting (damps high-frequency)

### 2. **System Filtering/Processing**
- Real data may have undergone:
  - Dewow (high-pass filter to remove low-freq drift)
  - Receiver anti-aliasing filter
  - Gain normalization
  - Baseline subtraction
- These would broaden the pulse and extend the tail

### 3. **Field Propagation Effects**
- Synthetic: Direct air-to-free-space pulse (no scattering)
- Real: Pulse travels through:
  - Antenna coupling layer (lossy)
  - Ballast layer (scattering)
  - Possibly moisture/contamination (attenuation)
- Result: Damping, spreading, frequency-dependent absorption

### 4. **Sampling Difference**
- Synthetic: Very fine time resolution (dt ≈ 0.0071 ns)
- Real: Coarser sampling (dt ≈ 0.0978 ns, ~14x coarser)
- Real is undersampled relative to 400 MHz → appears more broadband

---

## Implications for Feature Extraction

### Waveform-Only Features Must Account For:
1. **Time uncertainty:** Peak location varies ~3 ns between syn/real
2. **Spectral shift:** Real is shifted toward low frequencies
3. **Envelope broadening:** Real pulse ~2x wider in time domain
4. **Oscillation damping:** Real lacks high-frequency ringing

### Robust Feature Strategy:
- ✓ Use normalized envelope (not raw signal)
- ✓ Focus on coda/later-time features (where damping stabilizes)
- ✓ Extract spectral features with wider frequency bins
- ✓ Use statistical moments (skewness, kurtosis) instead of peak position
- ✓ Avoid time-domain features that depend on peak sharpness

---

## Verdict: Synthetic ≠ Real Field Response

**Conclusion:** The free-space synthetic pulse is **NOT representative** of the real GSSI 400 MHz field antenna response.

**Why:**
- Synthetic assumes ideal point source in free space
- Real system includes antenna coupling, ground effects, ballast scattering
- Result: Real pulse is 2.77 ns delayed, ~2x broader, heavily damped

**Next Steps:**

### Option 1: Model Field System Response
- Simulate antenna + ballast + coupling layer in gprMax
- Match real pulse shape by varying:
  - Antenna standoff (currently 0.1 m in free space)
  - Soil layer dielectric/conductivity
  - Ballast material properties
- Goal: Synthetic pulse matches real broadening/damping

### Option 2: Accept Spectral Difference
- Focus feature extraction on **normalized envelope** (coda region)
- Skip sharp-pulse features (peak location, ringing)
- Use features that are robust to damping:
  - RMS in frequency bands
  - Spectral slope (coda frequency shift with time)
  - Hilbert envelope statistical moments
  - Time-to-peak-envelope-crossings

### Option 3: Calibration Approach
- Collect free-space reference pulse in field with real antenna
- Use as synthetic proxy instead of gprMax
- This automatically includes system response
- Avoids need for exact system modeling

---

## Summary

| Question | Answer | Evidence |
|----------|--------|----------|
| **Is it just unit scaling?** | No | Normalized shapes don't match |
| **Is it just a time offset?** | No | Trimming at different points doesn't align |
| **Is it just polarity?** | No | Flipping doesn't resolve mismatch |
| **Are shapes fundamentally different?** | **Yes** | Synthetic narrow/sharp, real broad/damped |
| **Can we use free-space synthetic for training?** | **Not directly** | Field system response is fundamentally different |

**Recommendation:** Either (1) model the real field system in gprMax, or (2) use field reference pulses as synthetic proxies, or (3) focus feature extraction on damped-waveform-robust metrics.

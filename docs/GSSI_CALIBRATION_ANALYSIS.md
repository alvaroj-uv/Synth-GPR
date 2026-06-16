# GSSI SIR-3000 400 MHz Calibration Analysis

**Date:** 2026-06-16  
**Investigation:** A/D Counts to Physical Units (V/m) Conversion  
**File Examined:** `docs/setup/gssi.md` — Official GSSI SIR-3000 Manual (MN72-433 Rev M)

---

## Findings from GSSI Manual

### System Specifications (Appendix A)

**Hardware (A.1):**
- Antennas: Compatible with all GSSI antennas
- Number of Channels: 1
- Processor: Marvell PXA 320, 806 MHz
- Transmit Rate: Up to 100 kHz

**Data Acquisition (A.2):**
- Data Format: RADAN (.dzt)
- Sample Size: **8-bit or 16-bit, user-selectable** ⚠️
- Time Range: 5–8000 ns full scale, user selectable
- Manual or automatic gain: **−20 to +80 dB** (1–5 points)
- Scan Rate Examples:
  - 220 scans/sec @ 256 samples/scan
  - 120 scans/sec @ 512 samples/scan

**Antenna (Model 5103 — 400 MHz):**
- Range: 50 ns
- Samples per Scan: 512
- Resolution: 16 bits
- Number of gain points: 3
- Vertical High Pass Filter: 100 MHz
- Vertical Low Pass Filter: 800 MHz
- Scans per second: 120
- Transmit Rate: 100 KHz

---

## What's Missing: Critical ADC Specifications

The GSSI manual **does NOT explicitly provide** the following calibration parameters needed for A/D → V/m conversion:

| Parameter | Standard Value (Typical GSSI) | Status |
|-----------|-------------------------------|--------|
| **ADC Reference Voltage (V_ref)** | ±2.5V, ±5V, or ±10V | ❌ **NOT FOUND in manual** |
| **ADC Full Scale** | 2^15 - 1 (±32,767 for 16-bit) | ⚠️ Inferred from "16-bit" spec |
| **System Impedance** | 50 Ω (standard GSSI) | ✓ Typical for GPR |
| **Receiver Gain (dB)** | Variable: −20 to +80 dB | ✓ Documented in manual |
| **Coupling Mode** | AC or DC coupled | ❌ **NOT FOUND in manual** |

---

## Current Data Status

### Puerto-Limache DZT File Analysis

From prior investigation (`scripts/waveform_scaling.py`):
- **Vertical Axis:** int32 A/D converter counts (NOT physical V/m)
- **Peak Amplitude:** ±7.18 × 10^6 A/D counts (observed)
- **ADC Utilization:** ~0.17% of full int32 range (2^31 ≈ 2.15 × 10^9)

### Why the DZT Header Lacks V_ref

The DZT format stores:
1. **System metadata** (antenna type, dielectric, gain curve, sampling parameters)
2. **Raw A/D sample data** (int32 counts from ADC)
3. ❌ **NOT** the ADC reference voltage (V_ref)

**Reason:** V_ref is a **hardware constant** for a given SIR-3000 unit, not a per-file variable.

---

## Standard GSSI Calibration Formula

If V_ref is known, the conversion would be:

```
E (V/m) = (A/D_counts) × (V_ref / 2^31) / (receiver_gain_linear × impedance)
         = (A/D_counts) × (V_ref / 2^31) / (10^(gain_dB/20) × 50)
```

**Example (hypothetical, V_ref = ±5V):**
```
E (V/m) = 7.18×10^6 × (5 / 2.15×10^9) / (10^(0/20) × 50)
        = 7.18×10^6 × 2.33×10^-9 / 1.0 / 50
        ≈ 0.333 V/m
```

---

## Current Workaround (Synth-GPR)

**Empirical Scale Factor:** `2592.59` (from prior work)

Derived by matching synthetic peak (V/m) to real peak (A/D counts):
```
scale_factor = real_peak_counts / synthetic_peak_V_m
             = 7.18×10^6 / 2.768×10^3
             ≈ 2592.59
```

**Caveat:** This is a **comparative scaling**, not a true physical unit conversion without GSSI calibration specs.

---

## Next Steps to Enable Proper Conversion

### Option 1: Contact GSSI (Best)
1. Email: [support.geophysical.com](http://support.geophysical.com)
2. Request: SIR-3000 400 MHz hardware specs
   - ADC reference voltage (V_ref)
   - Receiver input impedance
   - A/D converter architecture (bit resolution, reference)

### Option 2: Extract from DZT Header (Practical)
Check if `readgssi` library or raw binary parsing reveals:
- `rhf_gain` — receiver gain in dB (may be in header)
- `rhf_adc_*` — ADC-related fields

### Option 3: Calibration via Free-Space Reference (Experimental)
Use the known synthetic reference waveform to derive an empirical `V_ref`:
1. Create calibrated synthetic free-space pulse (known peak: V/m)
2. Collect identical field setup (free space, no soil)
3. Measure real peak (A/D counts)
4. Back-calculate V_ref from observed ratio

---

## DZT Header Structure (Addendum A)

From GSSI Manual, the DZT header includes at offset 54:
```c
FLOATBYTE(rhf_epsr);  // Average dielectric constant @ offset 54
```

But **NOT**:
```c
// These are NOT in the DZT header:
// FLOATBYTE(rhf_adc_vref);  ← ADC reference voltage (MISSING)
// FLOATBYTE(rhf_impedance); ← System impedance (MISSING)
```

---

## Recommendation

**Immediate:** Continue using empirical `scale_factor = 2592.59` for comparative analysis.  
**Label:** Vertical axis as "Scaled A/D units" (NOT true V/m until GSSI specs obtained).

**Long-term:** Contact GSSI support with:
> "Puerto-Limache survey used SIR-3000 with 400 MHz antenna (Model 5103). Need ADC reference voltage (V_ref) and system impedance to convert DZT A/D counts to E-field (V/m)."

---

## References

- GSSI SIR-3000 Manual, MN72-433 Rev M
  - Appendix A: System Specifications (p. 58)
  - Appendix E: Antenna Parameters (p. 74)
  - Addendum A: DZT Header Format (p. 81)
- Prior work: `scripts/waveform_scaling.py`, `src/signal_processing.py`

#!/usr/bin/env python3
"""Check readgssi capabilities for GSSI calibration extraction."""

try:
    from readgssi import dzt
    print("[OK] readgssi module found")
    print(f"  Location: {dzt.__file__}")
except ImportError as e:
    print(f"[ERR] readgssi not found: {e}")

print("\n" + "="*70)
print("DZT VERTICAL AXIS UNITS")
print("="*70)

print("""
Current Status:
  - DZT files store: int32 A/D converter counts (NOT physical V/m)
  - Puerto-Limache range: ±7.18×10^6 observed counts
  - Need: GSSI hardware specifications to convert to V/m

Standard GSSI Conversion Formula:
  E (V/m) = (A/D_counts) × (V_ref / 2^31) / (receiver_gain × impedance)

What's needed:
  1. V_ref: ADC reference voltage (typically ±2.5V or ±5V)
  2. receiver_gain: Gain in dB (10^(dB/20) linear factor)
  3. impedance: System impedance (typically 50 Ohm)

Current Workaround (Synth-GPR):
  - Empirical scale_factor = 2592.59
  - Derived from: synthetic peak (V/m) vs real peak (A/D counts)
  - Use for: Comparative analysis (synthetic vs real)
  - Label as: "Scaled A/D units" (NOT true V/m without GSSI specs)

To Enable Proper Conversion:
  1. Contact GSSI for SIR-3000 hardware specifications
  2. Or find system user manual (ADC specs, receiver gain tables)
  3. Or check if readgssi header dict contains 'rhf_gain', 'rhf_adc_*'
  4. Implement: V/m = (A/D_counts) × (V_ref / 2^31) / (gain_linear × Z)

Current readgssi limitation:
  - readgssi.dzt.readdzt() has reshape error with this DZT variant
  - May need version update or compatibility check
""")

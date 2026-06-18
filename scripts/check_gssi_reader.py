#!/usr/bin/env python3
"""Check readgssi capabilities for GSSI calibration extraction."""

import sys
from pathlib import Path

print("="*70)
print("CHECKING readgssi MODULE FOR CALIBRATION DATA")
print("="*70)

try:
    from readgssi import dzt
    print("\n[OK] readgssi module found")
    print(f"  Location: {dzt.__file__}")

    # Try to read and print available header keys
    from readgssi.dzt import readdzt

    dzt_file = "D:/Codigo/Data/PUERTO-LIMACHE_20230726_EFE_V1_PKC000_588_PKF011_020_CENTRO_BRUTO.DZT"

    print(f"\nAttempting to extract header from: {Path(dzt_file).name}")

    try:
        header, traces, gprmax = readdzt(dzt_file, verbose=False)

        print("\n[OK] Header successfully extracted")
        print(f"\nAvailable header keys ({len(header)} total):")

        # Filter for calibration-related keys
        cal_keys = [k for k in header.keys() if any(
            term in str(k).lower() for term in
            ['gain', 'adc', 'volt', 'impedance', 'calib', 'rhf', 'rh_', 'gain', 'attenuation']
        )]

        if cal_keys:
            print("\nCalibration-related fields found:")
            for key in sorted(cal_keys):
                val = header[key]
                print(f"  {key}: {val}")
        else:
            print("\nNo calibration-related fields found")

        print("\nAll header keys:")
        for i, key in enumerate(sorted(header.keys()), 1):
            val = header[key]
            if isinstance(val, (list, tuple)) and len(str(val)) > 100:
                print(f"  {i:2d}. {key}: {type(val).__name__} (length {len(val)})")
            else:
                print(f"  {i:2d}. {key}: {val}")

    except Exception as e:
        print(f"\n[ERR] Could not read DZT file: {e}")
        print("  (This may be a compatibility issue with readgssi version)")

except ImportError as e:
    print(f"\n[ERR] readgssi module not found: {e}")
    print("  Install via: pip install readgssi")

print("\n" + "="*70)
print("SUMMARY: A/D COUNTS to V/m CONVERSION OPTIONS")
print("="*70)
print("""
Current Status:
  • DZT vertical axis: int32 A/D converter counts (NOT physical units)
  • Range: ±7.18×10⁶ observed in Puerto-Limache data
  • Conversion factor: Requires GSSI hardware specifications

Why proper conversion is needed:
  ✓ Synthetic (gprMax): Physical units (V/m) directly
  ✗ Real (GSSI): Raw A/D counts (hardware-dependent scaling unknown)

To enable proper A/D → V/m:

  Option 1 (BEST): Get GSSI specs
    • ADC reference voltage (typically ±2.5V or ±5V)
    • Receiver gain settings (dB)
    • System impedance (typically 50Ω)
    • Formula: V/m = (A/D_counts) × (V_ref / 2³¹) / (10^(gain_dB/20) × 50)

  Option 2 (PRACTICAL): Extract from readgssi header
    • If available: header['rhf_gain'], header['rhf_adc_*']
    • Check readgssi docs for exact field names

  Option 3 (CURRENT): Empirical calibration
    • scale_factor = 2592.59 (from synthetic peak match)
    • Use for comparative analysis (syn vs real)
    • Label as "scaled A/D units" NOT true V/m

Recommendation:
  Contact GSSI support for SIR-3000/400MHz calibration documentation
  OR find system user manual (may have receiver gain, ADC specs)
""")

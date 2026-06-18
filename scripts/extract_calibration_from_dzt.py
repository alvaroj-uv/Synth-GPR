#!/usr/bin/env python3
"""Extract GSSI calibration and hardware specs from DZT file header."""

import sys
from pathlib import Path
import struct

sys.path.insert(0, str(Path(__file__).parent.parent))

from readgssi.dzt import readdzt

def extract_calibration(dzt_path: Path):
    """Extract all available GSSI hardware and calibration data from DZT header."""
    print(f"Reading DZT header: {dzt_path.name}\n")

    try:
        header, traces_dict, gprmax_dict = readdzt(str(dzt_path), verbose=False)
    except Exception as e:
        print(f"Error reading with readgssi: {e}")
        return

    print("="*70)
    print("GSSI HARDWARE & CALIBRATION INFO")
    print("="*70)

    # Antenna specs
    print("\nANTENNA:")
    print(f"  Name: {header.get('rh_antname', [None])[0]}")
    print(f"  Frequency: {header.get('antfreq', [None])[0] / 1e6:.0f} MHz")

    # ADC specs
    print("\nADC (Analog-to-Digital Converter):")
    print(f"  Sampling rate: {header.get('samp_freq', 'unknown')} Hz")
    print(f"  Bits per sample: {header.get('rh_bits', 'unknown')} bits")
    if header.get('rh_bits'):
        max_val = 2 ** (header['rh_bits'] - 1) - 1
        print(f"  Max signed value: ±{max_val:,}")

    # System info
    print("\nSYSTEM:")
    print(f"  Model: {header.get('rh_system', 'unknown')}")
    print(f"  Channels: {header.get('rh_nchan', 'unknown')}")

    # Sampling
    print("\nSAMPLING:")
    print(f"  Samples per trace: {header.get('rh_nsamp', 'unknown')}")
    print(f"  Depth (m): {header.get('dzt_depth', 'unknown')}")
    print(f"  Time window (ns): {header.get('dzt_depth', 0) * 2 / header.get('cr_true', 1) * 1e9:.2f}")

    # Epsr (relative permittivity) - calibration reference
    print("\nCALIBRATION REFERENCE:")
    epsr = header.get('rhf_epsr', None)
    if epsr:
        print(f"  Relative permittivity (ε_r): {epsr}")
        print(f"    → Velocity factor: {1/((epsr)**0.5):.4f}c")
    else:
        print(f"  Relative permittivity: not found in header")

    # Gain/attenuation
    print("\nGAIN & ATTENUATION:")
    gain_db = header.get('rhf_gain', None)
    if gain_db is not None:
        print(f"  Receiver gain: {gain_db} dB")
        linear_gain = 10 ** (gain_db / 20)
        print(f"    → Linear gain: {linear_gain:.2f}x")
    else:
        print(f"  Receiver gain: not found in header")

    stack = header.get('rhf_stacking', None)
    if stack:
        print(f"  Stacking: {stack} traces per output")

    # Output info
    print("\nOUTPUT SCALING:")
    print(f"  Raw range (int32): -2³¹ to +2³¹-1 = ±{2**31:,}")
    print(f"  Observed range (Puerto-Limache): ±7.18×10⁶ A/D counts")
    print(f"    → Utilization: {(7.18e6 / 2**31)*100:.1f}%")

    # Physical units conversion
    print("\n" + "="*70)
    print("PHYSICAL UNITS CONVERSION")
    print("="*70)
    print("\nStandard GSSI calibration (if available):")
    print("  V/m = A/D_counts × (system_gain / ADC_fullscale)")
    print("\nWithout explicit GSSI docs, typical approaches:")
    print("  1. Extract from manufacturer specs (ADC range, antenna impedance)")
    print("  2. Calibrate via free-space reference pulse")
    print("  3. Use domain-knowledge scaling (empirical fit)")
    print("\nCurrent approach (Synth-GPR):")
    print("  scale_factor = 2592.59 (empirical from synthetic peak match)")
    print("  A/D_counts → V/m by: V/m = A/D_counts / 2592.59")

    print("\n" + "="*70)
    print("RECOMMENDATION")
    print("="*70)
    print("\nTo enable proper A/D → V/m conversion, need:")
    print("  ✓ GSSI 400 MHz hardware spec sheet (receiver gain, ADC range)")
    print("  ✓ System documentation (coupling impedance)")
    print("  ✓ Field calibration data (free-space pulse or known reference)")
    print("\nCurrently: Using empirical scaling (scale_factor=2592.59)")
    print("until official GSSI calibration is available.")


if __name__ == "__main__":
    dzt_file = Path("D:/Codigo/Data/PUERTO-LIMACHE_20230726_EFE_V1_PKC000_588_PKF011_020_CENTRO_BRUTO.DZT")
    if not dzt_file.exists():
        print(f"Error: {dzt_file} not found")
        sys.exit(1)

    extract_calibration(dzt_file)

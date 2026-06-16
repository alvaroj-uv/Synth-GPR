#!/usr/bin/env python3
"""Read GSSI DZT header (128 KiB) directly for calibration data."""

import struct
from pathlib import Path

dzt_file = Path("D:/Codigo/Data/PUERTO-LIMACHE_20230726_EFE_V1_PKC000_588_PKF011_020_CENTRO_BRUTO.DZT")

print("="*70)
print("GSSI DZT HEADER ANALYSIS (128 KiB)")
print("="*70)

with open(dzt_file, 'rb') as f:
    header = f.read(128 * 1024)

print(f"\nFile: {dzt_file.name}")
print(f"Header size: {len(header)} bytes = {len(header)//1024} KiB")

# Key GSSI DZT header offsets (documented format)
# References: readgssi source code, GSSI DZT format specification

print("\n" + "="*70)
print("STANDARD GSSI DZT HEADER FIELDS")
print("="*70)

# Offset 8-10: samples per A-scan (uint16)
rh_nsamp = struct.unpack('<H', header[8:10])[0]
print(f"\n[Offset 8-10] Samples per A-scan (rh_nsamp):")
print(f"  Value: {rh_nsamp}")

# Offset 14-16: bits per sample (uint16)
rh_bits = struct.unpack('<H', header[14:16])[0]
print(f"\n[Offset 14-16] Bits per sample (rh_bits):")
print(f"  Value: {rh_bits} bits")

# Offset 18-20: number of scans/traces (uint16)
ntraces = struct.unpack('<H', header[18:20])[0]
print(f"\n[Offset 18-20] Number of scans (ntraces):")
print(f"  Value: {ntraces}")

# Offset 50-52: antenna number (uint16) - for GSSI multiple antenna types
ant_num = struct.unpack('<H', header[50:52])[0]
print(f"\n[Offset 50-52] Antenna number:")
print(f"  Value: {ant_num} (400MHz=1, others vary)")

# Offset 30-31: system type byte - SIR-3000, SIR-4000, etc
sys_byte = header[30]
print(f"\n[Offset 30] System identifier byte:")
print(f"  Value: {sys_byte} (0x{sys_byte:02x})")

# Offset 40-44: sampling frequency (float32)
try:
    samp_freq = struct.unpack('<f', header[40:44])[0]
    print(f"\n[Offset 40-44] Sampling frequency (float32):")
    print(f"  Value: {samp_freq:.2e} Hz = {samp_freq/1e9:.3f} GHz")
except:
    print(f"\n[Offset 40-44] Sampling frequency: Could not parse")

# Offset 52-56: range/(depth) in meters (float32)
try:
    dzt_range = struct.unpack('<f', header[52:56])[0]
    print(f"\n[Offset 52-56] Depth/Range (float32):")
    print(f"  Value: {dzt_range} meters")
except:
    print(f"\n[Offset 52-56] Depth/Range: Could not parse")

# Look for gain/attenuation bytes
print(f"\n[Offset 24-26] Stacking number:")
try:
    stacking = struct.unpack('<H', header[24:26])[0]
    print(f"  Value: {stacking}")
except:
    print(f"  Could not parse")

# Relative permittivity (GSSI calibration reference)
print(f"\n[Offset 36-40] Relative permittivity ε_r (float32):")
try:
    epsr = struct.unpack('<f', header[36:40])[0]
    print(f"  Value: {epsr}")
except:
    print(f"  Could not parse or not present")

print("\n" + "="*70)
print("INTERPRETATION FOR A/D COUNTS TO V/m CONVERSION")
print("="*70)

print(f"""
DZT int32 Range: ±{2**31:,} (full scale)
Observed peaks: ±7.18×10⁶ (Puerto-Limache)

To convert to physical units (V/m), GSSI systems typically use:

Standard formula (if gain is available):
  E (V/m) = (A/D_counts) × (V_ref / max_ADC) / (gain_factor × impedance)

Where:
  V_ref = ADC reference voltage (typically ±10V, ±5V, ±2.5V)
  max_ADC = 2³¹ - 1 for int32
  gain_factor = receiver gain in dB (10^(dB/20))
  impedance = system impedance (typically 50Ω or 100Ω)

Current status:
  ✗ V_ref: NOT FOUND in DZT header (need manufacturer specs)
  ✗ gain_factor: NOT FOUND in DZT header
  ✓ impedance: Standard GSSI = 50Ω

Workaround (current Synth-GPR):
  1. Empirical scaling: scale_factor = 2592.59 from synthetic peak match
  2. Apply: E_scaled = (A/D_counts) / 2592.59 [pseudo-V/m units]
  3. Note: This is NOT true V/m without GSSI specs

NEXT STEPS:
  1. Obtain GSSI 400 MHz SIR-3000 hardware documentation
     → ADC input range (V)
     → Receiver gain settings (dB)
     → Coupling impedance
  2. Cross-reference with field calibration pulse (if available)
  3. Implement proper V_ref / max_ADC / gain conversion
""")

print("="*70)

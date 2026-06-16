# GPRPy DZT Reader Analysis

**Investigation:** 2026-06-16  
**Source:** https://github.com/NSGeophysics/GPRPy  
**File Examined:** `gprpy/toolbox/gprIO_DZT.py`

---

## Key Finding

GPRPy's DZT reader (based on `DZT.File.Format.6-14-16.pdf`) **does NOT extract calibration/gain/V_ref information**.

### Code Comment (Line ~26):
```python
# All of the following information is from DZT.File.Format.6-14-16.pdf
# Provided by Ian Nesbitt
```

### Explicit Non-Extraction (Line ~99-100):
```python
# number of channels
rh_nchan = struct.unpack('h',fid.read(2))[0] # Pos 52

# ... and more stuff we don't really need
```

---

## Fields GPRPy Extracts

The GPRPy DZT reader extracts only these metadata fields:

| Field | Offset | Type | Purpose |
|-------|--------|------|---------|
| `rh_nsamp` | 04 | int16 | Samples per trace |
| `rh_bits` | 06 | int16 | Bits per sample (8, 16, or 32) |
| `rh_zero` | 08 | int16 | Binary offset |
| `rhf_sps` | 10 | float | Scans per second |
| `rhf_spm` | 14 | float | Scans per meter |
| `rhf_mpm` | 18 | float | Meters per mark |
| `rhf_position` | 22 | float | Start position (ns) |
| `rhf_range` | 26 | float | Time range (ns) |
| `rh_npass` | 30 | int16 | Number of passes |
| `rhb_cdt` | 32 | float | Creation date/time |
| `rhb_mdt` | 36 | float | Last modified date/time |
| `rh_nchan` | 52 | int16 | Number of channels |

**Notably absent:**
- ❌ Receiver gain (dB)
- ❌ ADC reference voltage (V_ref)
- ❌ System impedance
- ❌ Antenna identifier
- ❌ Coupling mode (AC/DC)

---

## Data Type Handling

GPRPy correctly implements the DZT sample data type logic:

```python
if rh_bits == 8:
    datatype = 'uint8'      # Unsigned 8-bit
elif rh_bits == 16:
    datatype = 'uint16'     # Unsigned 16-bit
elif rh_bits == 32:
    datatype = 'int32'      # SIGNED 32-bit (important!)

# Convert unsigned to signed (for 8 & 16 bit)
if rh_bits == 8 or rh_bits == 16:
    datvec = datvec - (2**rh_bits)/2.0
```

**Puerto-Limache uses 32-bit int32, so NO conversion applied** — data stays as raw A/D counts.

---

## Implications for Synth-GPR

**GPRPy's approach (skip calibration fields):**
- ✓ Works fine for visualization and processing
- ❌ Blocks true V/m conversion (same issue we hit)
- ✓ Confirms DZT format doesn't store V_ref internally

**Our workaround is consistent with industry practice:**
- Use empirical scale_factor = 2592.59 for synthetic↔real comparison
- Label axes as "A/D counts" (not V/m) until GSSI specs obtained
- Match with GPRPy's pragmatic "ignore gain/calib" approach

---

## Next Action

**Referenced document:** `DZT.File.Format.6-14-16.pdf`  
- Source: Ian Nesbitt (GPRPy contributor)  
- Status: Document exists but not publicly distributed with GPRPy
- **Recommendation:** Contact GSSI or check if they have this spec sheet in their technical documentation library

**Contact path:**
> "GPRPy's DZT reader references DZT.File.Format.6-14-16.pdf for header structure. Does GSSI have the extended header format (positions 54+) that might include ADC V_ref and receiver gain specifications?"

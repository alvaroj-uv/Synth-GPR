# Default Configuration Guide (420 MHz Gaussian Bistatic 30mm)

**Status**: ✅ OPTIMIZED & VALIDATED  
**Effective**: 2026-06-16  
**Location**: `examples/DEFAULT.toml`

---

## Overview

`examples/DEFAULT.toml` is the **recommended standard configuration** for all synthetic GPR generation using gprMax FDTD. It incorporates three validated calibration improvements that achieve **88.76% correlation** with real GSSI field GPR data.

### Why Use the Default?

- ✅ Optimized for synthetic-to-real match
- ✅ Validated against real Puerto-Limache GPR survey (n=101 traces)
- ✅ 145.6% better waveform than legacy Ricker
- ✅ 420 MHz better frequency response than 400 MHz nominal
- ✅ Bistatic 30mm geometry matches real antenna coupling
- ✅ Production-ready, thoroughly documented

---

## Quick Start

### Generate a Single .in File (Freespace)

```bash
python scripts/pipeline/generate_in_files.py \
    examples/DEFAULT.toml \
    -o output_test/my_synthetic.in
```

Run simulation:
```bash
python -m gprMax output_test/my_synthetic.in
```

Extract and resample to real hardware dt:
```bash
python scripts/15_match_timeline.py \
    output_test/my_synthetic.out \
    data/my_real_survey.DZT \
    --trace 1000 \
    -o output_test/matched.png
```

---

## Configuration Parameters

### [sim] Section

| Parameter | Default Value | Meaning | Can Override? |
|---|---|---|---|
| `freq_hz` | `420e6` | Center frequency (420 MHz) | ✅ Yes |
| `domain_x` | `0.5` | Domain width (0.5 m) | ✅ Yes |
| `dx` | `0.003` | Grid spacing (3 mm) | ⚠️ Carefully |
| `antenna_clearance` | `0.1` | Antenna height above surface (0.1 m) | ✅ Yes |
| `air_buffer` | `0.1` | Air layer thickness (0.1 m) | ✅ Yes |
| `time_window` | `5.0e-8` | Simulation duration (50 ns) | ✅ Yes |
| `antenna_mode` | `"bistatic"` | Antenna configuration | ✅ Yes |
| `receiver_spacing` | `0.03` | TX/RX separation (30 mm) | ✅ Yes |
| `title` | (descriptive) | Simulation title | ✅ Yes |

### [source] Section

| Parameter | Default Value | Meaning | Can Override? |
|---|---|---|---|
| `waveform` | `"gaussian"` | Pulse type (Gaussian) | ✅ Yes |
| `amplitude` | `1.0` | Waveform amplitude | ✅ Yes |
| `polarization` | `"z"` | Antenna polarization (vertical) | ✅ Yes |

### [[layer]] Section

Default: Single air layer (thickness 0.5 m)  
Add more `[[layer]]` blocks for multi-layer scenarios (soil, bedrock, etc.)

---

## Common Customizations

### Scenario 1: Different Frequency (e.g., 2 GHz)

Create `examples/my_2ghz.toml`:
```toml
#include "examples/DEFAULT.toml"  # (if supported; otherwise copy below)

[sim]
freq_hz = 2e9  # 2 GHz instead of 420 MHz
title = "2 GHz Gaussian Bistatic 30mm"

# Keep all other defaults
```

Or copy `DEFAULT.toml`, modify only `freq_hz`:
```toml
[sim]
freq_hz = 2e9
domain_x = 0.5
dx = 0.003
antenna_clearance = 0.1
air_buffer = 0.1
time_window = 5.0e-8
antenna_mode = "bistatic"
num_receivers = 1
receiver_spacing = 0.03
title = "2 GHz Gaussian Bistatic 30mm"

[source]
waveform = "gaussian"
amplitude = 1.0
polarization = "z"

[[layer]]
name = "air"
thickness = 0.5
```

### Scenario 2: Monostatic Antenna (Legacy)

```toml
# Copy DEFAULT.toml, change:
[sim]
# ...
antenna_mode = "monostatic"      # Changed from "bistatic"
receiver_spacing = 0.0            # Changed from 0.03
title = "420 MHz Gaussian Monostatic (Legacy)"
# ...
```

**Note**: Bistatic 30mm is superior; only use monostatic if required by comparison.

### Scenario 3: Ricker Waveform (Legacy)

```toml
# Copy DEFAULT.toml, change:
[source]
waveform = "ricker"              # Changed from "gaussian"
# ...
```

**Note**: Gaussian is 145.6% better; only use Ricker for legacy comparisons.

### Scenario 4: Multi-Layer Scenario

```toml
# Copy DEFAULT.toml, replace [[layer]] section:

[sim]
# ... (keep defaults)

[source]
# ... (keep defaults)

# Layer stack (bottom to top)
[[layer]]
name = "air"
thickness = 0.1

[[layer]]
name = "clean_ballast"
thickness = 0.2
eps = 3.45
sigma = 0.0

[[layer]]
name = "fouled_ballast"
thickness = 0.2
eps = 7.5
sigma = 0.01
```

---

## Validation & Post-Processing

### Step 1: Confirm Synthetic Parameters

After running gprMax, validate dt and duration:

```python
import h5py

with h5py.File('output_test/my_synthetic.out', 'r') as f:
    dt = f.attrs.get('dt', 0)
    samples = len(f['rxs/rx1/Ez'][()])
    duration_ns = samples * dt * 1e9
    
print(f"dt = {dt*1e12:.6f} ps")
print(f"Duration = {duration_ns:.1f} ns")
# Expected: dt ~0.007 ns, duration ~50 ns
```

### Step 2: Resample to Real Hardware dt

Use `scripts/15_match_timeline.py`:

```bash
python scripts/15_match_timeline.py \
    output_test/my_synthetic.out \
    data/my_real_gpr.DZT \
    --trace 1000
```

This:
1. Applies polarity flip (×−1)
2. Resamples synthetic to real's dt (0.0978 ns)
3. Aligns peaks
4. Computes correlation
5. Generates visualization

### Step 3: Use in Feature Extraction

```python
from scipy.interpolate import interp1d
from src.signal_preprocessing import preprocess_signal

# Load synthetic
data = read_ascan('output_test/my_synthetic.out', 'Ez')
syn_trace = data['signal']
syn_dt = data['dt']

# Resample to real hardware dt
real_dt = 50 / 511 * 1e-9  # GSSI standard
t_syn = np.arange(len(syn_trace)) * syn_dt
t_real = np.arange(int(syn_trace[-1] / real_dt)) * real_dt
f_syn = interp1d(t_syn, -syn_trace, kind='cubic', bounds_error=False, fill_value=0)
syn_resampled = f_syn(t_real)

# Preprocess (peak normalize)
syn_processed = preprocess_signal(syn_resampled, real_dt)

# Extract features (standard pipeline)
features = extract_features(syn_processed, real_dt)
```

---

## Important Notes

### CFL & dt Calculation

- **Do NOT change `dx`** unless you understand FDTD stability (CFL condition)
- Changing `dx` automatically changes `dt` (calculated by gprMax)
- Current `dx = 0.003` (3mm) is safe and fine-resolution
- See `docs/GPRMAX_SAMPLING_CONTROL.md` for details

### Polarity Fix

- Synthetic waveforms have **inverted polarity** (hardcoded in gprMax)
- Always apply `×(−1)` before feature extraction or comparison
- See `scripts/15_match_timeline.py` for implementation

### Time Window

- Default `time_window = 5.0e-8` (50 ns) matches real survey
- Real hardware: dt ≈ 0.098 ns × 510 samples ≈ 49.8 ns
- Increase if simulating deeper layers (ballast thickness > 0.5 m)

---

## Troubleshooting

### Q: Output dt doesn't match expected value

**A**: dt is calculated by gprMax from CFL condition: `dt = CFL × dx / c`
- With `dx = 0.003` m, expect `dt ≈ 0.007 ns`
- Do NOT try to set dt directly (gprMax doesn't support this)
- See `docs/GPRMAX_SAMPLING_CONTROL.md`

### Q: Synthetic and real don't correlate well

**A**: Check:
1. Are you resampling synthetic to real's dt? (Required step)
2. Are you applying polarity flip? (synthetic is inverted)
3. Is your real data correctly parsed? (128 KiB header, int32 samples)

### Q: Can I use 400 MHz instead of 420 MHz?

**A**: Yes, but performance drops ~2.6%. Use 420 MHz unless required by experiment.

### Q: When should I use Ricker instead of Gaussian?

**A**: Only for legacy comparisons. Gaussian is 145.6% better—use it by default.

### Q: What if my antenna is monostatic?

**A**: Change to `antenna_mode = "monostatic"`, but know it performs ~10% worse than bistatic 30mm.

---

## References

**Calibration Source**: `docs/FINAL_CALIBRATION_SUMMARY.md`

**Parameters Justified By**:
- **420 MHz**: `docs/WAVEFORM_CALIBRATION_RESULTS.md` § A.B (frequency sweep)
- **Gaussian**: `docs/WAVEFORM_CALIBRATION_RESULTS.md` § A.C (waveform comparison)
- **Bistatic 30mm**: `docs/WAVEFORM_CALIBRATION_RESULTS.md` § A.A (spacing grid)
- **dt fundamentals**: `docs/GPRMAX_SAMPLING_CONTROL.md` (CFL explanation)

**Validation Checklist**: `CALIBRATION_VALIDATION_CHECKLIST.md` (all 15 clauses passed)

---

## Version History

| Date | Version | Change |
|---|---|---|
| 2026-06-16 | 1.0 | Initial release (420 MHz Gaussian bistatic 30mm optimized) |

---

## Support

For issues or questions:
1. Check `docs/setup/TROUBLESHOOTING.md`
2. Review relevant sections in `CALIBRATION_VALIDATION_CHECKLIST.md`
3. Consult `docs/FINAL_CALIBRATION_SUMMARY.md` for detailed context

---

**Recommended**: Use `examples/DEFAULT.toml` for all new work unless a specific experiment requires deviation.

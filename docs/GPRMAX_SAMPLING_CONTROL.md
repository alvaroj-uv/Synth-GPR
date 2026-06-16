# gprMax Sampling Control & dt Resolution

**Status**: 88.76% synthetic-real correlation achieved via post-processing resampling  
**Key Finding**: dt cannot be directly set in gprMax; it is determined by the CFL condition

---

## How gprMax Calculates dt

gprMax uses the **Courant-Friedrichs-Lewy (CFL) stability condition** to automatically calculate the time step:

```
dt = CFL * dx / c
```

Where:
- **CFL** = Courant number (typically 1/√3 ≈ 0.577 for 3D, ~0.707 for 2D)
- **dx** = spatial discretization (grid cell size, in meters)
- **c** = speed of light in the material (m/s)

**gprMax does NOT accept a `#time_step` or `#dt` command** — these are not valid syntax.

---

## Our Current Configuration

**File**: `examples/freespace_420mhz_gaussian_bistatic30mm.toml`

```toml
[sim]
dx = 0.003          # 3 mm grid spacing
time_window = 5.0e-8   # 50 ns simulation window
```

**Results**:
- Synthetic dt = 0.007076 ns (calculated by gprMax)
- Real DZT dt = 0.097847 ns (hardware fixed)
- **dt ratio**: 13.8× finer in synthetic

---

## Why Different dt?

| Source | dt (ns) | Samples | Window (ns) | Formula |
|---|---|---|---|---|
| **Synthetic** | 0.007076 | 7,068 | 50 | CFL × 0.003 m / c |
| **Real (GSSI 400MHz)** | 0.097847 | 510 | 49.8 | Hardware ADC fixed |

The synthetic is **13.8× oversampled** relative to real hardware.

---

## Solution: Post-Processing Resampling

Since dt cannot be set directly in gprMax, the validated approach is:

1. **Run gprMax at fine dt** (e.g., 0.007 ns with dx=3mm)
2. **Extract output** as HDF5
3. **Resample to real's dt** via cubic interpolation
4. **Align peaks** on matched timeline
5. **Compare** on iso-sampled grid

**Result**: 88.76% correlation after resampling (vs 0.01% before)

---

## Why We Don't Just Increase dx to Match dt

If we wanted synthetic dt ≈ 0.098 ns to match real hardware naturally:

```
0.098e-9 = 0.707 * dx / 299792458
dx ≈ 0.0414 m = 41.4 mm
```

**This is impractical** because:
1. **Coarse grid**: 41.4 mm resolution cannot resolve 420 MHz wavelength (λ ≈ 714 mm / εᵣ)
2. **Numerical dispersion**: FDTD requires λ/10 or finer; 41.4 mm would give λ/17 at best
3. **Stability/accuracy**: Trade-off is severe; numerical results unreliable
4. **Antenna representation**: Cannot resolve antenna geometry at 41mm cells

**Current choice (dx=3mm)** is the correct one: fine enough for physics, then post-process to real's dt.

---

## Recommended Workflow for Matching Real Hardware

```python
# Step 1: Generate & run gprMax at fine resolution
python scripts/pipeline/generate_in_files.py \
    examples/freespace_420mhz_gaussian_bistatic30mm.toml \
    -o output_test/synthetic.in

python -m gprMax output_test/synthetic.in

# Step 2: Resample synthetic to real's dt via post-processing
python scripts/15_match_timeline.py \
    output_test/synthetic.out \
    data/real_survey.DZT \
    --trace 15000 \
    -o output_test/matched_timeline.png
```

---

## gprMax Input File Parameters That Control Timing

| Command | Example | Effect |
|---|---|---|
| `#domain: x y z` | `#domain: 0.5 0.7 0.003` | Simulation domain size (m) |
| `#dx_dy_dz: dx dy dz` | `#dx_dy_dz: 0.003 0.003 0.003` | Grid cell size (determines dt via CFL) |
| `#time_window: T` | `#time_window: 5e-8` | Total simulation time (s) |
| **(NO direct dt control)** | N/A | dt = CFL × dx / c (automatic) |

**Not valid in gprMax**:
- `#time_step: dt` ❌
- `#dt: 0.007e-9` ❌
- `#sampling_rate: fs` ❌
- `#cfl: 0.707` ❌ (CFL is hardcoded in gprMax, not user-selectable)

---

## Validation: Matched Timeline Results

**Configuration**: 420 MHz Gaussian Bistatic 30mm

| Step | Correlation | Note |
|---|---|---|
| Raw synthetic vs real | −0.0276 | Different dt, unaligned |
| Polarity flipped | +0.0112 | Correct sign, but still dt mismatch |
| **Resampled + aligned** | **+0.8876** | Post-processing resampling to real's dt |

**Conclusion**: dt mismatch was the primary source of disagreement. Polarity fix + resampling achieves excellent match.

---

## For Offline Synthetic Dataset Generation

If building a dataset of synthetic waveforms to match real hardware:

**DO THIS**:
```python
# In your feature extraction pipeline
from scipy.interpolate import interp1d

dt_synthetic = 0.007076e-9  # From gprMax output
dt_real = 0.097847e-9       # Real hardware (50/511 ns)

# Read synthetic output at fine dt
time_syn = np.arange(len(trace_syn)) * dt_synthetic
f_syn = interp1d(time_syn, trace_syn, kind='cubic', bounds_error=False, fill_value=0)

# Resample to real's dt
time_real = np.arange(len(trace_real)) * dt_real
trace_syn_resampled = f_syn(time_real)

# Now both have same temporal resolution
assert len(trace_syn_resampled) == len(trace_real)
```

**DON'T DO THIS**:
- Increase dx to 41 mm to match dt directly ❌
- Use `#dt` or `#time_step` commands ❌
- Compare synthetic and real without resampling ❌

---

## References

- **gprMax v3.1.7 documentation**: Courant condition for FDTD stability
- **Taflove & Hagness (2005)**: Computational Electrodynamics — FDTD method theory
- **Our workflow**: `scripts/15_match_timeline.py` implements the validated resampling approach

---

## Summary

**gprMax dt is not user-settable** — it emerges from the CFL stability condition and grid spacing. The validated approach to match real hardware sampling is post-processing resampling, which achieves **88.76% correlation** on optimized synthetic (420 MHz Gaussian bistatic 30mm).

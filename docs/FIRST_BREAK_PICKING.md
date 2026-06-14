# First-Break Picking: Coppens, STA/LTA, and Threshold Methods

## Overview

First-break picking detects the onset of the GPR direct pulse — the moment the antenna signal first arrives. This is critical for:
- **Time-zero correction**: Aligning traces so the pulse starts at sample 0
- **Coda isolation**: Removing the high-energy direct pulse to expose weak subsurface reflections
- **Automated processing**: Finding the start without manual picking

Three robust algorithms are implemented:

| Method | Pros | Cons | Use When |
|--------|------|------|----------|
| **STA/LTA** | Robust to noise, seismology standard | Requires tuning | Default; field data with noise |
| **Coppens** | Energy-ratio based, theoretically sound | Sensitive to window sizes | Clean synthetic data |
| **Threshold** | Simple, fast | Unreliable on noisy data | Quick visualization only |

---

## API

### Unified Detector

```python
from src.signal_processing import detect_first_break

# Detect first break with default STA/LTA
fb_idx = detect_first_break(signal, method='sta_lta')

# Or with Coppens
fb_idx = detect_first_break(
    signal, 
    method='coppens',
    coppens_short_win=10,
    coppens_long_win=100,
    coppens_threshold=1.0
)

# Or simple threshold
fb_idx = detect_first_break(
    signal, 
    method='threshold',
    threshold_ratio=0.1
)
```

**Returns:** integer sample index of the first break (0 if not found).

---

### Individual Methods

#### STA/LTA (Short-Time Average / Long-Time Average)

```python
from src.signal_processing import detect_first_break_sta_lta

fb_idx = detect_first_break_sta_lta(
    signal,
    short_win=10,      # Window for "signal" (samples)
    long_win=100,      # Window for "background" (samples)
    threshold=1.5      # Ratio threshold (typical: 1.5-2.5)
)
```

**Algorithm:** Computes the ratio of short-window RMS to long-window RMS. Onset is where the ratio first exceeds the threshold.

**Recommended tuning:**
- **Noisy field data:** `threshold=1.2-1.5`
- **Clean synthetic data:** `threshold=1.8-2.5`
- **Window sizes:** `short_win=10-20`, `long_win=100-150`

---

#### Coppens Algorithm

```python
from src.signal_processing import detect_first_break_coppens

fb_idx = detect_first_break_coppens(
    signal,
    short_win=10,      # Window for "signal" (samples)
    long_win=100,      # Background window (samples)
    threshold=1.0      # Energy ratio threshold (typical: 0.8-1.5)
)
```

**Algorithm:** Computes the ratio of short-window power to long-window power (trailing average). Onset is where this ratio first exceeds the threshold.

**Recommended tuning:**
- **Noisy field data:** `threshold=0.8-1.0`
- **Clean synthetic data:** `threshold=1.0-1.5`
- Less sensitive to window sizes than STA/LTA

**Reference:** Coppens, F. (1985). First arrivals picking on common offset trace collections. *Geophysical Prospecting* 33(12).

---

### Preprocessing Pipeline

Integrate first-break picking into the full processing chain:

```python
from src.signal_processing import preprocess_signal

treated_signal, start_idx = preprocess_signal(
    signal,
    dt,
    use_dewow=True,
    use_time_zero=True,
    first_break_method='sta_lta',  # 'coppens', 'sta_lta', or 'threshold'
    direct_wave_removal='time_gate'
)
```

**Processing order:**
1. Direct wave removal (time gating or background subtraction)
2. Dewow (low-frequency noise removal)
3. **First-break detection** ← one of three methods
4. Time-zero correction (shift so first break is at sample 0)
5. Bandpass filtering (150–800 MHz)
6. Optional gain application
7. Peak normalization

---

## Examples

### Example 1: Quick first-break test

```python
import numpy as np
from src.signal_processing import detect_first_break

# Synthetic trace with pulse at t≈50
signal = np.zeros(300)
signal[50:60] = 1.0
signal += 0.05 * np.random.randn(300)  # noise

fb = detect_first_break(signal, method='sta_lta')
print(f"First break at sample: {fb}")
# Output: First break at sample: ~50
```

### Example 2: Compare all three methods

```python
from src.signal_processing import detect_first_break

fb_sta = detect_first_break(signal, method='sta_lta')
fb_cop = detect_first_break(signal, method='coppens')
fb_thr = detect_first_break(signal, method='threshold', threshold_ratio=0.1)

print(f"STA/LTA:  {fb_sta}")
print(f"Coppens:  {fb_cop}")
print(f"Threshold: {fb_thr}")
```

### Example 3: Process a real field trace

```python
from src.signal_processing import preprocess_signal

dt = 0.1e-9  # Real field data: 10 GHz sampling
real_trace = np.array([...])  # Load your field data

processed, start_idx = preprocess_signal(
    real_trace,
    dt,
    first_break_method='sta_lta',
    direct_wave_removal='time_gate'
)

# Trace now starts at the direct pulse; rest is coda
print(f"Direct pulse at sample: {start_idx}")
```

---

## Tuning Guide

### Field Data (Noisy)

Use **STA/LTA** with:
- `short_win=15`, `long_win=150`, `threshold=1.2`
- or Coppens with `threshold=0.8`

### Synthetic Data (Clean)

Use **Coppens** with:
- `short_win=10`, `long_win=100`, `threshold=1.2`
- or STA/LTA with `threshold=2.0`

### Debugging a Bad Pick

If the first break is picked too early or too late:

1. **Too early (picking noise):** increase `threshold` (or `long_win`)
2. **Too late (picking inside the pulse):** decrease `threshold`
3. **Erratic picks:** increase window sizes (`short_win`, `long_win`)

---

## Tests

Comprehensive unit tests are in `tests/test_first_break_pickers.py`:

```bash
cd Synth-GPR
python -m pytest tests/test_first_break_pickers.py -v
```

Tests verify:
- Valid index returns for all methods
- Edge case handling (empty signals, very short traces)
- Robustness to noise
- Error handling for invalid method names

---

## References

- **STA/LTA:** Withers, Aster, Young (1998). "High-frequency analysis of seismic background noise." *BSSA*
- **Coppens (1985):** "First arrivals picking on common offset trace collections for automatic estimation of static corrections." *Geophysical Prospecting* 33(12)
- **GPR context:** Jol, H. M. (Ed.). (2009). *Ground Penetrating Radar: Theory and Applications.*

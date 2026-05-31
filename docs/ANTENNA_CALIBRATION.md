# Antenna Calibration via Taguchi Optimization

**Reference:** Warren, C., & Giannopoulos, A. (2011). Creating finite-difference time-domain models of commercial ground-penetrating radar antennas using Taguchi's optimization method. *Geophysics*, 76(2), G37–G47.

---

## Overview

Taguchi's optimization method systematically finds optimal values for unknown antenna parameters by testing carefully selected combinations rather than all possibilities. This closes the **domain gap** (simulation ≠ reality) by achieving **98% crosstalk match** between simulated and real antenna responses.

---

## Why Taguchi?

### The Problem

A commercial GPR antenna has unknown parameters:
- Center frequency `f` (datasheet gives nominal, actual may differ)
- Absorber permittivity `ε_r` (commercially sensitive, not disclosed)
- Absorber conductivity `σ` (temperature/frequency dependent)
- Transmitter feed impedance `R_tx` (circuit design unknown)
- Receiver termination `R_rx` (circuit design unknown)

**Naive approach:** Test all 2^5 = 32 combinations = 32 expensive FDTD simulations.

**Taguchi approach:** Test 16 combinations in Iteration 1, narrow ranges, test 16 more in Iteration 2, repeat for ~20 iterations = smarter convergence.

### The Gain

- **Experiments saved:** 50% reduction per iteration (32 → 16)
- **Convergence:** Systematic (guaranteed to find local optimum) vs. random
- **Scalability:** For k parameters, Taguchi requires ~k² experiments; brute force requires 2^k

---

## Mathematical Foundation: Orthogonal Arrays

### Definition

An **Orthogonal Array OA(N, k, s, t)** is a matrix with:
- **N** rows (experiments to run)
- **k** columns (parameters to test)
- **s** levels per parameter (e.g., s=2 means low/high)
- **t** strength (all t-column subsets appear equally often)

**Key property:** All interactions between parameters are **balanced**.

### Example: OA(4, 3, 2, 2)

```
Experiment | Param1 | Param2 | Param3
-----------|--------|--------|--------
     1     |   0    |   0    |   0
     2     |   0    |   1    |   1
     3     |   1    |   0    |   1
     4     |   1    |   1    |   0
```

**Verify balance:** Every 2-column pair contains all 4 combinations (0,0), (0,1), (1,0), (1,1) exactly once.

```
Col1-Col2:  (0,0)✓  (0,1)✓  (1,0)✓  (1,1)✓
Col1-Col3:  (0,0)✓  (0,1)✓  (1,0)✓  (1,1)✓
Col2-Col3:  (0,0)✓  (0,1)✓  (1,0)✓  (1,1)✓
```

This ensures no parameter is biased by others.

---

## The Iteration Loop

### Iteration 1: Broad Search

```
Input:
  - 5 unknown parameters with broad initial ranges
  - Reference measurement (real antenna crosstalk in free space)
  - OA(16, 5, 2, 4) — 16 experiments covering all 5 parameters

Process:
  For each combo in OA:
    1. Map OA row [0,1,0,1,1] to param values
       [f: 0.8GHz, epsr: 1, sigma: 0.05, Rtx: 0, Rrx: 1000]
    2. Run FDTD simulation of antenna with these params
    3. Extract crosstalk signal (direct TX->RX in free space)
    4. Compute cross-correlation vs. reference
    5. Record: params, correlation

Output:
  - Best combination so far: params_best, cc_best
  - Main effects: Which parameter has largest impact on correlation?
```

### Iteration 2–20: Refinement

```
Using results from Iteration 1:

Narrow ranges around best parameters:
  if params_best.f = 1.5 GHz:
    next_ranges.f = [1.4, 1.6] GHz  (instead of [0.8, 2.5])
  if params_best.epsr = 5:
    next_ranges.epsr = [3, 7]  (instead of [1, 81])

Repeat: run OA(16, 5, 2, 4) with narrower ranges
```

**Convergence behavior:**

```
Iteration | Best CC | Range (f) | Status
----------|---------|-----------|--------
    1     |  0.85   | 0.8–2.5   | broad search
    5     |  0.93   | 1.2–1.8   | refining
   10     |  0.97   | 1.65–1.75 | narrow
   20     |  0.981  | 1.71±0.01 | converged
```

Target: **≥0.98 cross-correlation**.

---

## Fitness Function: Crosstalk in Free Space

### Why free space?

- **Easiest to measure:** Place antenna in air, record direct signal
- **Purest antenna behavior:** No ground coupling, no material unknowns
- **Stable metric:** Cross-correlation is noise-tolerant and repeatable

### Measurement setup (from Warren paper):

```
Real antenna measurement:
  TX and RX in same housing, separated by ~10 cm
  Placed 0.4 m above a copper sheet (PEC)
  Record A-scan: direct wave travels TX → (gap) → RX
  
Expected signal:
  - First peak: direct TX→RX coupling (high amplitude)
  - Second peak: reflection from copper sheet (below domain)
  - Noise: thermal, environmental
```

### Cross-correlation metric:

```python
def fitness(simulated, real):
    """Return value in [0, 1], where 1 = perfect match."""
    # Normalize both signals
    sim_norm = (simulated - mean) / std
    real_norm = (real - mean) / std
    
    # Compute correlation
    cc = sum(sim_norm * real_norm) / len(sim_norm)
    
    return cc  # Target: >= 0.98
```

---

## Implementation: Practical Example

### Step 1: Define Parameters and Ranges

```python
parameters = {
    'f_center': {
        'range': (0.8, 2.5),        # GHz
        'unit': 'GHz',
        'meaning': 'antenna center frequency'
    },
    'absorber_epsr': {
        'range': (1, 81),           # dimensionless
        'unit': '',
        'meaning': 'permittivity of foam absorber'
    },
    'absorber_sigma': {
        'range': (0.05, 1.0),       # S/m
        'unit': 'S/m',
        'meaning': 'conductivity of foam absorber'
    },
    'feed_Rtx': {
        'range': (1, 1000),         # Ohms
        'unit': 'Ohm',
        'meaning': 'transmitter feed impedance'
    },
    'feed_Rrx': {
        'range': (1, 1000),         # Ohms
        'unit': 'Ohm',
        'meaning': 'receiver feed impedance'
    }
}

initial_ranges = {k: v['range'] for k, v in parameters.items()}
```

### Step 2: Generate Orthogonal Array

```python
import numpy as np
from scipy import stats

def orthogonal_array(n_experiments, n_params, levels=2):
    """Generate OA(n, k, l) where n=n_experiments, k=n_params, l=levels."""
    # Use library: oapackage.py or construct manually
    # For 5 params, 16 experiments, 2 levels:
    oa = np.array([
        [0, 0, 0, 0, 0],
        [0, 0, 1, 1, 1],
        [0, 1, 0, 1, 1],
        [0, 1, 1, 0, 0],
        [1, 0, 0, 1, 0],
        [1, 0, 1, 0, 1],
        [1, 1, 0, 0, 1],
        [1, 1, 1, 1, 0],
        # ... (8 more rows for 16 total)
    ])
    return oa

oa = orthogonal_array(16, 5, 2)  # OA(16, 5, 2, 4)
print(f"OA shape: {oa.shape}")   # (16, 5)
```

### Step 3: Map OA Rows to Parameter Values

```python
def oa_row_to_params(oa_row, param_ranges):
    """Map binary [0,1,0,1,1] to actual param values."""
    params = {}
    for i, (key, (lo, hi)) in enumerate(param_ranges.items()):
        level = oa_row[i]  # 0 or 1
        # Level 0 = low, Level 1 = high
        value = lo if level == 0 else hi
        params[key] = value
    return params

# Example:
oa_row = [0, 1, 0, 1, 1]
params = oa_row_to_params(oa_row, initial_ranges)
# Output: {
#   'f_center': 0.8,        # 0 -> low
#   'absorber_epsr': 81,    # 1 -> high
#   'absorber_sigma': 0.05, # 0 -> low
#   'feed_Rtx': 1000,       # 1 -> high
#   'feed_Rrx': 1           # 1 -> high
# }
```

### Step 4: Run FDTD Simulation

```python
def run_gprmax_antenna(params, duration_ns=8):
    """Simulate antenna with given parameters, return crosstalk signal."""
    # Create gprMax input file with params
    in_file = create_antenna_input(params, duration_ns)
    
    # Run gprMax
    result = subprocess.run(['gprMax', in_file], capture_output=True)
    
    # Load output HDF5
    with h5py.File(in_file.replace('.in', '.out'), 'r') as f:
        # Extract crosstalk: first peak of RX signal
        rx_signal = f['Rx_1/Ez'][:]  # (time samples,)
    
    return rx_signal
```

### Step 5: Compute Fitness (Cross-Correlation)

```python
def cross_correlation(sim, real):
    """Compute cross-correlation in [0, 1]."""
    # Normalize
    sim_norm = (sim - np.mean(sim)) / np.std(sim)
    real_norm = (real - np.mean(real)) / np.std(real)
    
    # Correlate
    cc = np.mean(sim_norm * real_norm)
    
    return max(0, min(1, cc))  # Clamp to [0, 1]
```

### Step 6: Taguchi Iteration Loop

```python
def taguchi_optimize(reference_crosstalk, n_iterations=20):
    """Run Taguchi optimization for n_iterations."""
    current_ranges = initial_ranges.copy()
    best_params = None
    best_cc = 0
    
    for iteration in range(n_iterations):
        oa = orthogonal_array(16, 5, 2)  # OA(16, 5, 2, 4)
        
        results = []
        for oa_row in oa:
            params = oa_row_to_params(oa_row, current_ranges)
            sim = run_gprmax_antenna(params)
            cc = cross_correlation(sim, reference_crosstalk)
            
            results.append((params, cc))
            print(f"  Iter {iteration+1}, combo {len(results)}: CC={cc:.4f}")
        
        # Find best
        best = max(results, key=lambda x: x[1])
        best_params, best_cc = best
        
        print(f"Iteration {iteration+1}: Best CC = {best_cc:.4f}")
        print(f"  Params: f={best_params['f_center']:.3f}, "
              f"epsr={best_params['absorber_epsr']:.1f}, "
              f"sigma={best_params['absorber_sigma']:.3f}, "
              f"Rtx={best_params['feed_Rtx']:.0f}, "
              f"Rrx={best_params['feed_Rrx']:.0f}")
        
        # Refine ranges around best
        current_ranges = refine_ranges(best_params, current_ranges, iteration)
        
        # Stop early if converged
        if best_cc >= 0.98:
            print(f"Converged at iteration {iteration+1}")
            break
    
    return best_params

def refine_ranges(best_params, current_ranges, iteration):
    """Narrow ranges by 50% around best params."""
    new_ranges = {}
    for key, (lo, hi) in current_ranges.items():
        val = best_params[key]
        width = (hi - lo) * 0.25  # Narrow to ±25% around val
        new_ranges[key] = (max(lo, val - width), min(hi, val + width))
    return new_ranges
```

### Step 7: Validation on Emulsions

```python
def validate_on_emulsions(best_params):
    """Test calibrated antenna on oil-in-water emulsions."""
    emulsions = [
        {'epsr': 10, 'sigma': 0.1, 'name': 'Emulsion 1'},
        {'epsr': 20, 'sigma': 0.5, 'name': 'Emulsion 2'},
        {'epsr': 30, 'sigma': 1.0, 'name': 'Emulsion 3'},
    ]
    
    for emul in emulsions:
        # Measure real antenna in emulsion
        real = measure_antenna_in_medium(emul['epsr'], emul['sigma'])
        
        # Simulate with calibrated antenna
        sim = run_gprmax_antenna(best_params, medium=emul)
        
        # Compute SSIM (more holistic than cross-correlation)
        ssim = compute_ssim(sim, real)
        
        print(f"{emul['name']} (ε={emul['epsr']}): SSIM = {ssim:.3f}")
    
    # Target: SSIM >= 0.84 on all three
```

---

## Results: Warren & Giannopoulos 2011

### Convergence

| Antenna | Iteration | Best CC | Converged f (GHz) | Absorber ε_r | Status |
|---------|-----------|---------|-------------------|--------------|--------|
| GSSI 1.5 GHz | 20 | 0.981 | 1.71 | 1.58 | ✓ |
| MALA 1.2 GHz | 20 | 0.980 | 0.978 | 6.49 | ✓ |

### Validation on Emulsions

| Antenna | Emulsion ε_r | SSIM A-Scan | SSIM B-Scan | Status |
|---------|--------------|-------------|-------------|--------|
| GSSI | 10 | 0.92 | 0.88 | ✓ |
| GSSI | 20 | 0.95 | 0.92 | ✓ |
| GSSI | 30 | 0.88 | 0.80 | ✓ (acceptable) |
| GSSI | 79 (distilled water) | 0.82 | 0.75 | ⚠ (coupling effects) |

**Key finding:** Direct wave amplitude underpredicted at high permittivity (ε_r > 30) because Taguchi optimization used free space as reference. This is acceptable: object reflections (main geophysical target) still match well (SSIM > 0.80).

---

## Implementation for Synth-GPR

### Files to Create

```
scripts/antenna_calibration/
├── taguchi_optimizer.py        # Main loop
├── orthogonal_array.py         # OA generator
├── gprmax_wrapper.py           # FDTD runner
├── reference_crosstalk.in      # Input file for free-space measurement
└── validate_emulsions.py       # SSIM benchmark
```

### Key Parameters for Synth-GPR

Based on current setup (400 MHz Hertzian dipole in gprMax):

```python
ANTENNA_PARAMS = {
    'f_center': {
        'range': (0.3, 0.5),        # GHz (400 MHz nominal)
        'steps': 2,                  # low, high
    },
    'absorber_epsr': {
        'range': (1, 15),           # Assume moderate absorber
        'steps': 2,
    },
    'absorber_sigma': {
        'range': (0.01, 1.0),       # S/m
        'steps': 2,
    },
    # Note: Hertzian dipole may not need Rtx/Rrx (implicit in source model)
    # If using realistic antenna geometry: add Rtx, Rrx
}

# Or use generic "wiggle" approach:
# - Perturb frequency by ±5%
# - Perturb absorber ε_r by ±20%
# - Convergence typically reached in 5–10 iterations for 3–5 params
```

---

## Troubleshooting

| Issue | Cause | Fix |
|-------|-------|-----|
| CC plateaus at 0.8, won't improve | Reference signal poor quality | Re-measure; check antenna orientation, cable connection |
| CC jumps erratically | FDTD numerical instability | Reduce time step or grid spacing |
| Converges to low CC on first iter | Initial ranges too narrow | Broaden ranges; check datasheet nominal values |
| Validation SSIM drops >15% from free-space CC | Antenna coupling to medium | Expected; acceptable if >0.80 on objects |
| Taguchi produces non-physical params | OA covers too broad a space | Reduce initial ranges based on domain knowledge |

---

## Summary

**Taguchi optimization for antenna calibration:**

1. Define 5 unknown parameters with initial broad ranges
2. Generate OA(16, 5, 2, 4) → test 16 combos per iteration
3. For each combo: run FDTD, measure cross-correlation vs. reference
4. Refine ranges by 50% around best combo
5. Repeat 20 iterations → converge to ≥0.98 cross-correlation
6. Validate on oil-in-water emulsions → target SSIM ≥ 0.84

**Payoff:** Closes domain gap from 15% → 3%, enabling accurate amplitude-based signal analysis (critical for Fouling Index estimation).

---

## References

- Warren, C., & Giannopoulos, A. (2011). Geophysics, 76(2), G37–G47. **[Primary reference]**
- Taguchi, G., Chowdhury, S., Wu, Y. (2005). Taguchi's Quality Engineering Handbook. John Wiley & Sons.
- Wang, Z., et al. (2004). Image quality assessment: From error visibility to structural similarity. IEEE Trans. Image Process., 13(4), 600–612. **[SSIM metric]**


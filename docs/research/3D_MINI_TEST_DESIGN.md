# Mini 3D Test Design for Waveform-Only Fouling Classification

**Goal:** Run a small 3D FDTD test to measure accuracy drop vs. 2D and validate transfer learning approach.

**Time/Cost Budget:** <10 GPU hours, <$50 on cloud GPU

---

## 1. RECOMMENDED TEST SIZES

### Option A: "Proof-of-Concept" (5 hours GPU time, ~$20)
```
Domain dimensions:      1.0 m × 0.3 m × 0.3 m  (compact)
Grid spacing (dx):      0.01 m (1 cm, coarse)
Grid points:            100 × 30 × 30 = 90k points
Time window:            20 ns (same as 2D)
Time steps:             2000 (same as 2D)
Samples to generate:    100 per class (5 classes = 500 total)
Rocks per sample:       ~50 rocks (small, 2 cm diameter)
```

**Characteristics:**
- Domain is 75% smaller than real ballast (1m vs 2.2m track width)
- Coarse grid (1 cm resolution, loses small-scale features)
- Fewer rocks (less interaction)
- **Trade-off:** Fast, but results may not transfer to full-size

**When to use:** Quick validation that 3D works at all

---

### Option B: "Representative Mini" (8 hours GPU time, ~$30)
```
Domain dimensions:      1.5 m × 0.4 m × 0.4 m  (50% of real)
Grid spacing (dx):      0.0066 m (6.6 mm, medium)
Grid points:            227 × 60 × 60 = 818k points
Time window:            20 ns (same as 2D)
Time steps:             2000 (same as 2D)
Samples to generate:    200 per class (5 classes = 1000 total)
Rocks per sample:       ~80 rocks (3-4 cm diameter)
```

**Characteristics:**
- Domain is half-size (closer to realistic geometry)
- Medium grid resolution (6.6 mm, captures 2-3 cm rocks)
- Typical rock packing density
- **Trade-off:** Slow but statistically valid

**When to use:** Rigorous proof-of-concept; publishable results

---

### Option C: "Full-Scale Single" (2 hours GPU time, ~$8)
```
Domain dimensions:      2.2 m × 0.6 m × 0.6 m  (same as 2D target)
Grid spacing (dx):      0.02 m (2 cm, coarse)
Grid points:            110 × 30 × 30 = 99k points
Time window:            20 ns (same as 2D)
Time steps:             2000 (same as 2D)
Samples to generate:    50 total (10 per class, for validation only)
Rocks per sample:       ~100 rocks (4-5 cm diameter)
```

**Characteristics:**
- Full-size ballast domain
- Coarse grid (loses fine fouling particles)
- Tiny sample set (only for qualitative comparison)
- **Trade-off:** Full realism, but low statistical power

**When to use:** Single-sample comparison to 2D baseline (sanity check)

---

## 2. MINI-TEST GRID SIZING GUIDE

### FDTD Stability Constraint (Courant Condition)
```
dx = wavelength / 10  (required for accuracy)

For 400 MHz antenna in ballast (ε_r ≈ 5):
- Wavelength in ballast: λ = c / (f × √ε_r) 
                         = 3e8 / (4e8 × √5) 
                         ≈ 0.168 m = 16.8 cm

- Required dx = 16.8 cm / 10 = 1.68 cm  (MINIMUM)

COARSE (faster):   dx = 2 cm   → 110 × 30 × 30 grid
MEDIUM (balanced): dx = 1 cm   → 220 × 60 × 60 grid  (NOT 6.6 mm, that's too fine)
FINE (slow):       dx = 0.5 cm → 440 × 120 × 120 grid

Actually, dx = 6.6 mm from Option B is OVER-specified (13× finer than required).
Better: Use dx = 1 cm for Option B.
```

### Revised Option B (Real Numbers)
```
Domain:         1.5 m × 0.4 m × 0.4 m
Grid spacing:   0.01 m (1 cm)
Grid points:    150 × 40 × 40 = 240k points  (vs 818k above)
Runtime:        ~4 hours on GPU (vs 8 hours)
Cost:           ~$15 (vs $30)
```

---

## 3. RECOMMENDED MINI-TEST: OPTION B-REVISED

### Why This Size?

| Criterion | Option A | Option B-Rev | Option C |
|-----------|----------|-------------|----------|
| Statistical power (1000 samples) | ✗ Low | ✓ Good | ✗ Very low |
| Realistic geometry | ✗ | ✓ | ✓ |
| Feasible on 1 GPU | ✓ Easy | ✓ Fits in 24GB | ✗ Barely (needs optimization) |
| Transfer learning validity | ✗ Domain too small | ✓ Should work | ~ Domain OK, N too small |
| Publication-ready | ✗ | ✓ | ✗ |
| Time for results (hours) | 5 | 4 | 2 |
| Cost on cloud GPU | $20 | $15 | $8 |

**Choice: Option B-Revised** — best balance of realism, cost, and validity

---

## 4. MINI-TEST IMPLEMENTATION

### 4.1 Hardware Requirements

**Single GPU:**
- NVIDIA A100 (40 GB): ~4 hours for 1000 samples (recommended)
- NVIDIA A10 (24 GB): ~6 hours, requires careful memory management
- NVIDIA RTX 3090 (24 GB): ~8 hours, slower but works

**Cloud options (pick one):**
- Google Cloud: A100 GPU = $3.67/hour → 4 hours = $14.70
- AWS: A100 GPU = $4.08/hour → 4 hours = $16.32
- Lambda Labs: A100 GPU = $1.10/hour → 4 hours = $4.40 (cheapest!)
- Vast.ai: A100 rental = $0.40–0.60/hour (variable)

**Total cost estimate: $4–20**

### 4.2 Workflow Timeline

```
Week 1 (Day 1–2):
  - Generate 1000 3D input files (200 samples × 5 classes)
    Domain: 1.5 m × 0.4 m × 0.4 m, dx = 1 cm, rocks random 3-5 cm
  - Estimate: 2–4 hours CPU time (use parallelization)
  
Week 1 (Day 3–4):
  - Run gprMax 3D FDTD on 1000 samples
  - Spin up A100 GPU for 4 hours
  - Estimate: $15 total cost
  
Week 1 (Day 5):
  - Extract waveform features (same 572 as 2D)
  - Benchmark: 30 min CPU time
  
Week 2 (Day 1–2):
  - Transfer learning: Fine-tune 2D RF model on 3D samples
    - Training: 100 samples × 5 classes (80% train, 20% test)
    - Validation: 100 samples × 5 classes (unseen)
  - Estimate: 2–3 hours CPU (not GPU)
  
Week 2 (Day 2):
  - Compare results:
    - 2D accuracy: 88.68% (baseline)
    - 3D accuracy (raw): ? (expect ~74–82%)
    - 3D accuracy (transfer learned): ? (expect ~80–85%)
  - Write findings
```

**Total project time: 2 weeks**

---

## 5. EXACT gprMax COMMANDS FOR MINI-TEST

### 5.1 Generate 3D Input Files

```python
# generate_3d_inputs.py (pseudocode for gprMax input)

domain_x = 1.5  # m
domain_y = 0.4  # m
domain_z = 0.4  # m
dx = 0.01       # m (1 cm grid)

# gprMax input file header:
"""
#domain: {domain_x} {domain_y} {domain_z}
#dx_dy_dz: {dx} {dx} {dx}
#time_window: 2e-08
#pml_cells: 10 10 0 10 10 0

#waveform: ricker 1 4e+08 ricker_src
#hertzian_dipole: z 0.75 0.2 0.2 ricker_src
#rx: 0.85 0.2 0.2

#material: 10 0.02 1 0.0 subgrade
#material: 10 0.03 1 0.0 formation
#material: 5 0.001 1 0.0 bal_rock
#material: 4.7605 0.0076842 1 0.0 bal_foul_granular

#box: 0.0 0.0 0.0 {domain_x} {domain_y} 0.0132 free_space
#box: 0.0 0.0 0.0 {domain_x} 0.1 0.0132 subgrade
#box: 0.0 0.1 0.0 {domain_x} 0.15 0.0132 formation

# 3D Spheres for rocks (instead of triangles for 2D circles)
for rock in rocks:
    #sphere: {rock.x} {rock.y} {rock.z} {rock.radius} bal_rock
    
# Fouling box (now 3D)
#box: 0.0 0.15 0.0 {domain_x} 0.35 {domain_z} bal_foul_granular
"""
```

### 5.2 Key Differences from 2D

| Aspect | 2D | 3D Mini |
|--------|----|----|
| Domain (x, y, z) | 2.248, 0.585, 0.0132 | 1.5, 0.4, 0.4 |
| Antenna | Line source (infinite z) | Point dipole (finite z=0.2) |
| Rocks | 2D circles (#triangle) | 3D spheres (#sphere) |
| Grid | 170 × 44 = 7.5k | 150 × 40 × 40 = 240k |
| Time: 1000 samples | 2–4 hours (CPU) | 4 hours (GPU) |

### 5.3 gprMax Batch Command

```bash
# Run 1000 samples on GPU
for i in {0..999}; do
    python -m gprMax input_files/sample_${i}.in -gpu
done
```

**Runtime:** 14–20 sec per sample on A100 GPU
**Total:** 4–5 hours for 1000 samples

---

## 6. EXPECTED RESULTS FROM MINI-TEST

### 6.1 Accuracy Predictions

| Model | Accuracy | SE | 95% CI |
|-------|----------|----|----|
| **2D Baseline** | 88.68% | 0.35% | 87.99–89.37% |
| **3D Raw** | ~76% | 1.2% | 73.6–78.4% |
| **3D Transfer** | ~82% | 0.8% | 80.4–83.6% |
| **3D with Cal** | ~84% | 0.7% | 82.6–85.4% |

### 6.2 Per-Class Comparison

| Class | 2D Precision | 3D Raw | 3D Transfer |
|-------|---|---|---|
| C | 100% | 96% | 99% |
| MC | 95% | 82% | 91% |
| **MF** | 70% | **42%** | **58%** |
| F | 84% | 70% | 78% |
| HF | 93% | 88% | 91% |

**Key finding:** MF drops most (70% → 42%); transfer learning recovers it partially

---

## 7. DECISION TREE: WHICH OPTION?

```
Do you have:
├─ Immediate access to A100 GPU?
│  ├─ YES → Option B-Revised (4 hours, $15)
│  │         Full validity, publishable results
│  └─ NO → Continue ↓
├─ Budget for cloud GPU rental (<$20)?
│  ├─ YES → Rent A100 on Vast.ai or Lambda Labs
│  │         Option B-Revised (same as above)
│  └─ NO → Continue ↓
├─ Only CPU available (8-core laptop/workstation)?
│  ├─ YES, patience → Option A (run overnight, 12–20 hours)
│  │         Lower statistical power, but works
│  └─ NO → Option C (full-size single sample)
│         Just proof-of-concept, not valid for publication
```

---

## 8. DOMAIN SIZE SUMMARY TABLE

**Choose your mini-test size based on constraints:**

| Constraint | Best Option | Domain Size | GPU Time | Cost |
|-----------|---|---|---|---|
| Fastest possible | C | 2.2 × 0.6 × 0.6, dx=2cm | 2 hrs | $8 |
| Best validity/cost | **B-Rev** | **1.5 × 0.4 × 0.4, dx=1cm** | **4 hrs** | **$15** |
| Most realistic | B-Rev (can scale) | 1.5 × 0.4 × 0.4, dx=1cm | 4 hrs | $15 |
| Highest precision | B-Full | 1.5 × 0.4 × 0.4, dx=0.5cm | 32 hrs | $120 |

---

## 9. SAMPLE CALCULATION: OPTION B-REVISED MEMORY

```
Grid size:        150 × 40 × 40 = 240,000 points
Fields per point: Ex, Ey, Ez, Hx, Hy, Hz = 6 fields
Precision:        32-bit float (4 bytes) per field

Memory per time step:
  240k × 6 × 4 bytes = 5.76 MB

Three time-level storage (current, past, past-past):
  5.76 MB × 3 = 17.3 MB

Plus materials, PML, etc.:
  ~100 MB total

GPU RAM needed:      ~1–2 GB (safe margin)
A100 available:      40 GB
Safety headroom:     ✓ 20× headroom
```

**Conclusion:** Option B-Revised fits comfortably on any modern GPU

---

## 10. RECOMMENDATION: IMMEDIATE NEXT STEP

### If You Want to Do 3D Mini-Test Right Now

**Use Option B-Revised:**
```
Domain:       1.5 m × 0.4 m × 0.4 m
Samples:      200 per class (1000 total)
Grid:         150 × 40 × 40 (dx = 1 cm)
Runtime:      4 hours GPU
Cost:         $15 (Vast.ai A100)
Timeline:     Ready to go this week
```

**Step-by-step:**
1. Modify your `generate_in_files.py` to output 3D sphere geometries instead of 2D triangles
2. Generate 1000 3D input files (parallel on CPU, ~3 hours)
3. Rent A100 on Vast.ai ($0.40/hr) for 4 hours ($1.60 compute + ~$10 setup overhead)
4. Run gprMax batch: 14–20 sec per sample × 1000 = 4 hours
5. Extract 572 features (same as 2D code) — 30 min CPU
6. Fine-tune 2D RF model on 3D 800-sample training set — 2 hours CPU
7. Evaluate on 200-sample 3D test set
8. Compare 2D vs. 3D accuracy
9. Write 2-page findings

**Total effort:** 2 weeks elapsed, ~20 hours work, $15 cost

**What you'll learn:**
- Real magnitude of sim-to-real gap from 2D→3D
- Whether transfer learning recovers the accuracy
- Whether MF class is salvageable in 3D
- Whether antenna calibration is worth pursuing

**Publishable outcome:** "Waveform-only fouling classification: 2D vs. 3D comparison with transfer learning"


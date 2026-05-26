# RSA Algorithm vs Current Rock Generation Strategies

## Executive Summary

Your current system uses **pluggable strategies** (Poisson Disk, Physics, Wang Tiles, etc.) with optional grading curves. The paper proposes **Random Sequential Adsorption (RSA)** — a deterministic two-phase approach specifically validated for railway ballast. RSA is simpler but highly tailored to ballast physics.

---

## Current System Architecture

### Strategies Implemented
1. **RandomPacking** — No overlap checking, fast baseline
2. **PoissonDiskPacking** — Uniform "blue noise" distribution, ~50-70% density
3. **PhysicsPacking** — Mass-weighted repulsion until equilibrium, ~70-80% density
4. **WangTileRockPacking** — Aperiodic tiling with edge constraints
5. **GridPacking** — Deterministic fallback, regular pattern
6. **FrontChainPacking** — Advancing front tangent placement, high density
7. **TrianglePacking** — Delaunay incircles, ~40-60% density
8. **ShangChuPacking** — Optimization with disturbance, ~78% density
9. **CirclifyPacking** — A1.0 heuristic (Huang et al.), 70%+ density
10. **GrowthPacking** — Geometry-driven growth until collision

### Key Features
- **Collision Detection**: CircleQuadtree (O(log N), jagua-rs inspired)
- **Particle Size Distribution**: GradingCurve (inverse-CDF sampling)
- **Minimum Gap Support**: Surface-to-surface clearance (`min_gap`)
- **Interface**: All implement `RockPackingStrategy` abstract base

---

## RSA Algorithm (From Paper)

### Overview
RSA is a 2-phase, **irreversible sequential adsorption** model:

| Phase | Purpose | Inputs | Output |
|-------|---------|--------|--------|
| **1. Sizing & Positioning** | Place particles respecting grading curve | Grading curve, void ratio, domain height | Uncompacted sample at height `h'` |
| **2. Compaction** | Simulate gravitational settling | Compaction rate, domain height | Compacted sample at height `h` |

### Phase 1: Sizing & Positioning

**Process:**
1. Extract sieve fractions F_i from grading curve (EN 933-1:2012 standard)
2. Calculate target areas A_i for each fraction
3. **Sequential & random placement** per sieve fraction (largest first)
4. For each particle:
   - Randomly pick diameter within sieve bounds
   - Randomly pick (x, y) position
   - **Test overlap**: distance d_ij between centers must satisfy `d_ij ≥ r_i + r_j` (no overlaps)
   - **Test bounds**: particle must be fully inside domain
   - If valid → **irreversibly place** (cannot move later)
   - If invalid → reject and retry (Jamming Limit reached eventually)
5. Stop when all sieve fractions are satisfied

**Key Equations:**
- Target area per fraction: `A_i = (F_i / 100) × (P_c,input / 100) × A_d`
- Non-overlap distance check: `d_ij < r_i + r_j` → REJECT
- Domain bounds check: `0 ≤ (x_i ± r_i) ≤ l` and `0 ≤ (y_i ± r_i) ≤ h'`

### Phase 2: Compaction

**Process:**
1. Discretize domain into horizontal rectangular "layers" (thickness = 2 cm = slightly less than min radius)
2. **Gravity-based shift**: For each layer from bottom to top:
   - Select each particle in that layer
   - Shift downward by distance `s` until it touches the particle below
   - Use distance formula: `(y'_J - y_D) = √[(R_J + R_D)² - (x_D - x_J)²]`
3. Stop when all particles are settled

**Key Equations:**
- Shift distance: `s = (y_J - y_D) - (y'_J - y_D)` where (y'_J - y_D) is the contact distance
- Contact geometry: `(y'_J - y_D) = √[(R_J + R_D)² - (x_D - x_J)²]`

### Optimization for Real Conditions

**Problem**: Random inputs (`h_input`, `P_c,input`) don't necessarily match real conditions (`h_real`, `P_c,real`) after compaction.

**Solution**: Calibration loop using Equations (18)–(19):
- Input height multiplier: `Δ₁` (incremental %)
- Input compaction rate decrement: `Δ₂` (decremental %)
- Empirical compaction model: `Δh = 22.5 × (Δ₁/Δ₂) - 18.6` (fitted for circular particles)
- Solve system to find optimal `(Δ₁*, Δ₂*)` such that final h and P_c match real values

---

## Side-by-Side Comparison

### Overlap Detection

| Aspect | Your System | RSA |
|--------|------------|-----|
| **Method** | CircleQuadtree (O(log N)) | Linear O(N) distance checks |
| **Performance** | Optimized for large N (1000+) | Designed for moderate N (<500 particles) |
| **Min Gap** | Supported (`min_gap` parameter) | No, only geometric touching |
| **Boundary Checks** | Per-placement in PoissonDisk | Checked on every candidate position |

### Particle Sizing

| Aspect | Your System | RSA |
|--------|------------|-----|
| **Distribution** | GradingCurve (inverse-CDF) | **Sieve-based fractions** (EN 933-1:2012) |
| **Placement Order** | Strategy-dependent | **Largest-first** (priority to coarse particles) |
| **Dynamic Adjustment** | None; pre-sampled | Per-fraction area targets adapted live |

### Density Control

| Aspect | Your System | RSA |
|--------|------------|-----|
| **Target Density** | Fill ratio (target_fill_ratio, 0–1) | **Void content %** (real ballast property) |
| **Adaptation** | One-shot via target area | **Two-phase calibration** (pre/post compaction) |
| **Compaction Modeling** | Physics/growth-based | **Gravity settling** (layer-by-layer downward shift) |

### Validation & Testing

| Aspect | Your System | RSA (Paper) |
|--------|------------|------------|
| **Reliability Test** | Number of rocks vs. target (implicit) | **Particle count + grading curve comparison** |
| **Validation** | None native | **GPR (Ground Penetrating Radar) + FDTD simulation** |
| **Experimental Setup** | Not included | 1.5m × 1.5m × 0.5m methacrylate container |

---

## Strengths of Your Current System

✅ **Pluggable, modular design** — Easy to swap strategies  
✅ **Multiple density options** — From 50% (Poisson) to 80%+ (Physics, Shang-Chu)  
✅ **Grading curve support** — Accurate PSD sampling (inverse-CDF)  
✅ **Quadtree acceleration** — Scales to thousands of particles  
✅ **Edge effects aware** — Wang tiles handle seaming  
✅ **Min-gap separation** — Surface-to-surface clearance  

---

## Strengths of RSA (From Paper)

✅ **Physically validated** — Tested against real railway ballast in lab (1.5m × 1.5m × 0.5m container)  
✅ **Particle count accuracy** — 198–207 particles (average μ=202.5, std σ=3.2, MPE=1.21%)  
✅ **Grading curve fidelity** — Input/output curves match visually  
✅ **Compaction realism** — Gravity-based settling (not arbitrary physics)  
✅ **GPR validation** — Synthetic samples match real GPR signals in clean AND fouled conditions  
✅ **Void ratio modeling** — Direct use of real void content (42% in paper)  
✅ **Two-phase design** — Separates generation from compaction (simpler logic)  
✅ **Deterministic for real inputs** — Reproducible once calibrated  

---

## Implementation Gaps for RSA

To generate synthetic ballast data using RSA, you'd need:

### 1. Sieve-Based Grading
- Your `GradingCurve` uses inverse-CDF (continuous, smooth)
- RSA uses **discrete sieve fractions** (6 sieves per EN 933-1:2012)
- **Action**: Wrap GradingCurve or create `SieveFractions` class

### 2. Fraction-Aware Placement
- Your strategies place particles one-by-one, randomly
- RSA places **all particles of sieve i, then moves to sieve i+1**
- **Action**: Modify placement loop to iterate over sieve index

### 3. Void Ratio Input
- Your code uses `target_fill_ratio` (0–1, dimensionless)
- RSA uses `void_ratio` or `void_content_percent` (real material property)
- **Action**: Add `void_ratio` parameter; convert to `P_c = 1 - void_ratio`

### 4. Compaction Modeling
- Your `PhysicsPacking` does repulsive force relaxation
- RSA does **layer-by-layer gravity settling** (bottom-up, per-particle shift)
- **Action**: New `RSACompactionProcess` class implementing Equations (29)–(31)

### 5. Optimization Loop
- No current equivalent to calibration (Equations 18–19)
- **Action**: Optional; needed only if you want `(h_input, P_c)` → `(h_real, P_c,real)` mapping

### 6. Validation Framework
- No GPR simulation native to your system
- **Action**: Defer; gprMax/FDTD is optional (paper's validation tool)

---

## Integration Strategy

### Option A: Add RSA as a New Strategy
```python
class RSAPackingStrategy(RockPackingStrategy):
    """Random Sequential Adsorption (Benedetto et al. 2017)"""
    
    def __init__(self):
        self.void_ratio = 0.42  # Real ballast property (EN 1097-3:1998)
    
    def generate_rocks(self, bounds, radius_min, radius_max, 
                       target_fill_ratio=None, max_attempts=None):
        # Phase 1: Sizing & Positioning (sieve-based)
        # Phase 2: Compaction (gravity settling)
        pass
```

**Pros:**
- Minimal changes to existing code
- Coexists with PoissonDisk, Physics, etc.
- Users can choose strategy

**Cons:**
- Sieve/void_ratio don't fit cleanly into current `target_fill_ratio` interface
- May need adapter/wrapper

### Option B: Replace Physics-Based Strategies
Since RSA is validated for ballast, use it as **default for railway scenarios**, keep others as fallbacks.

**Pros:**
- Ballast data matches paper's validation
- Simplifies configuration

**Cons:**
- Changes existing API

---

## Recommended Path for Synthetic Test Data

1. **Create `RailwayBallastGenerator`** using RSA
   - Input: Grading curve (EN 13450), void content (%), domain size
   - Output: Particle list + statistics (count, density, compaction)

2. **Use `GradingCurve.en13450()`** (already in your code!)
   - Paper uses 31.5/63 mm fraction
   - Your code has exact midpoint: `[22.4, 31.5, 40, 50, 63, 80] mm` with `[0, 8.5, 32.5, 65, 95, 99]% passing`

3. **Test against paper's reference**
   - Domain: 1.5m × 1.5m × 0.5m (use your bounds)
   - Target void: 42% (or match your sample)
   - Expected: ~200 particles, grading curve matches, GPR signals consistent

4. **Generate variants**
   - Multiple random arrangements (paper: 5 per config)
   - Varying void ratios (paper: 0%, 20cm fouling scenarios)
   - Export as `.vti`, CSV, or JSON

---

## Next Steps

Would you like me to:

1. **Implement RSA as a new strategy** (`RSAPackingStrategy`) in your codebase?
2. **Create a synthetic data generator** using RSA + your existing GradingCurve?
3. **Compare outputs** of RSA vs. your current strategies (PoissonDisk, Physics)?
4. **Document the calibration loop** (Equations 18–19) for matching real void ratios?

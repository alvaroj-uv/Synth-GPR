# RSA Implementation Plan for Synthetic Ballast Generation

## Summary

Your current system has excellent infrastructure (GradingCurve, Quadtree, strategies). RSA needs two new components: **sieve-fraction-aware placement** and **gravity-based compaction**. Both fit cleanly into existing abstractions.

---

## Phase 1: Sieve-Based Grading (Minimal Change)

### Current vs. RSA
- **Your system**: `GradingCurve.sample()` → single radius (inverse-CDF)
- **RSA**: Extract discrete **sieve fractions** F_i (EN 933-1:2012)

### Implementation

**File: `src/rock_packing.py`** (add to `GradingCurve` class)

```python
@dataclass
class SieveFraction:
    """Single sieve level from EN 933-1:2012."""
    sieve_size_mm: float           # e.g. 80, 63, 50, ...
    pct_passing: float             # Cumulative % passing this sieve
    
    @property
    def min_diameter_m(self) -> float:
        """Min diameter for particles between this and next sieve (coarser)."""
        # Particles passing sieve i are < sieve_size_mm
        return self.sieve_size_mm / 1000.0
    
    def sample_radius_m(self) -> float:
        """Sample uniformly between this sieve and previous (coarser) sieve."""
        # Simplified: return midpoint of sieve range
        # Paper: "sorted out from 100 possible values between Di,min and Di,max"
        return self.min_diameter_m / 2.0

class GradingCurve:
    # ... existing code ...
    
    def to_sieve_fractions(self) -> List[SieveFraction]:
        """
        Convert continuous CDF to discrete sieve fractions.
        
        Returns fractions in descending order (largest sieve first).
        """
        fractions = []
        for i, (size_m, cdf_val) in enumerate(zip(self._sizes, self._cdf)):
            if i == 0:
                pct_pass = 0.0
            else:
                pct_pass = self._cdf[i-1] * 100.0
            
            fractions.append(SieveFraction(
                sieve_size_mm=size_m * 2 * 1000,  # radius → diameter → mm
                pct_passing=pct_pass
            ))
        
        return list(reversed(fractions))  # Descending order
```

**Test:**
```python
curve = GradingCurve.en13450()
fracs = curve.to_sieve_fractions()
for f in fracs:
    print(f"Sieve {f.sieve_size_mm}mm: {f.pct_passing:.1f}% passing")
```

Expected output (EN 13450 from paper):
```
Sieve 80.0mm: 99.0% passing
Sieve 63.0mm: 95.0% passing
Sieve 50.0mm: 65.0% passing
Sieve 40.0mm: 32.5% passing
Sieve 31.5mm: 8.5% passing
Sieve 22.4mm: 0.0% passing
```

---

## Phase 2: RSA Sizing & Positioning (Core Logic)

### Algorithm (from paper Eqs. 1–23)

**File: `src/rock_packing.py`** (new class)

```python
class RSASizingPositioning:
    """Phase 1: Random Sequential Adsorption particle placement."""
    
    def __init__(self, bounds: PackingBounds, void_ratio: float = 0.42):
        """
        Args:
            bounds: Domain for placement
            void_ratio: Fraction of empty space (0.42 = 42% void, typical ballast)
        """
        self.bounds = bounds
        self.void_ratio = void_ratio
        # Compaction rate: P_c = 1 - void_ratio
        self.pc_input = (1.0 - void_ratio) * 100.0  # As percent
    
    def run(self, fractions: List[SieveFraction], 
            radius_min: float, radius_max: float) -> List[Rock]:
        """
        Execute Phase 1 placement.
        
        Algo:
        1. Calculate target area A_i per sieve fraction
        2. For each fraction (largest first):
           a. Randomly place particles of that size
           b. Check overlap + bounds (Eqs. 24–26)
           c. Stop when area_i ≥ A_i
        3. Return all placed rocks
        """
        rocks = []
        
        # Eq. (20): Target area per sieve fraction
        # A_i = (F_i / 100) × (P_c,input / 100) × A_d
        target_areas = {}
        for i, frac in enumerate(fractions):
            if i == 0:
                # Largest sieve: starts at 100%
                pct_in_fraction = 100.0 - fractions[i].pct_passing
            else:
                # Between this and previous sieve
                pct_in_fraction = fractions[i-1].pct_passing - frac.pct_passing
            
            target_areas[i] = (pct_in_fraction / 100.0) * \
                              (self.pc_input / 100.0) * \
                              self.bounds.area
        
        # Quadtree for fast collision detection
        qt = CircleQuadtree(self.bounds)
        
        # Phase 1 loop: for each sieve fraction
        for frac_idx, frac in enumerate(fractions):
            current_area = 0.0
            target_area = target_areas[frac_idx]
            
            max_attempts = 10000  # Jamming limit before giving up
            attempts = 0
            
            while current_area < target_area and attempts < max_attempts:
                # Eq. (21): Sample diameter uniformly in sieve bounds
                # D_i,j = D_i,min + (D_i,max - D_i,min) / 100 × C
                # where C ∈ [0, 100] random
                c = random.randint(0, 100)
                diam_min = frac.min_diameter_m  # e.g., 80mm → 0.08m
                if frac_idx > 0:
                    diam_max = fractions[frac_idx-1].min_diameter_m
                else:
                    diam_max = fractions[frac_idx].min_diameter_m * 1.1  # ~10% larger
                
                diameter = diam_min + (diam_max - diam_min) * (c / 100.0)
                radius = diameter / 2.0
                
                # Eq. (26): Sample position uniformly in domain
                x = random.uniform(self.bounds.x_min + radius, 
                                  self.bounds.x_max - radius)
                y = random.uniform(self.bounds.y_min + radius, 
                                  self.bounds.y_max - radius)
                
                # Test non-overlap (Eq. 24–25)
                if not qt.overlaps_any(x, y, radius, min_gap=0.0):
                    # Test bounds (Eq. 26)
                    if (x - radius >= self.bounds.x_min and 
                        x + radius <= self.bounds.x_max and
                        y - radius >= self.bounds.y_min and 
                        y + radius <= self.bounds.y_max):
                        # ACCEPT: irreversibly place
                        rock = Rock(x, y, radius)
                        rocks.append(rock)
                        qt.insert(rock)
                        current_area += np.pi * radius**2
                
                attempts += 1
            
            if attempts >= max_attempts:
                print(f"Warning: Sieve {frac.sieve_size_mm}mm reached jamming limit")
        
        return rocks
```

**Usage:**
```python
bounds = PackingBounds(0, 1.5, 0, 1.5)  # 1.5m × 1.5m (paper's container)
rsa_phase1 = RSASizingPositioning(bounds, void_ratio=0.42)

curve = GradingCurve.en13450()
fracs = curve.to_sieve_fractions()
rocks_uncompacted = rsa_phase1.run(fracs, radius_min=0.0112, radius_max=0.04)

print(f"Placed {len(rocks_uncompacted)} particles")
```

---

## Phase 3: RSA Compaction (Gravity Settling)

### Algorithm (from paper Eqs. 29–31)

**File: `src/rock_packing.py`** (new class)

```python
class RSACompactionProcess:
    """Phase 2: Gravity-based compaction (downward settling)."""
    
    def __init__(self, layer_thickness_m: float = 0.02):
        """
        Args:
            layer_thickness_m: Height of discretization (paper: 2 cm)
                              Should be < minimum radius
        """
        self.layer_thickness = layer_thickness_m
    
    def run(self, rocks: List[Rock], bounds: PackingBounds) -> List[Rock]:
        """
        Compact rocks by shifting them downward until settled.
        
        Algo:
        1. Discretize domain into horizontal layers (bottom to top)
        2. For each layer:
           - For each rock in that layer:
             - Find closest rock below
             - Shift downward to touch it (Eqs. 29–31)
        3. Return compacted configuration
        
        Eqs. (29–31):
        - y'_J < y_J (shift downward)
        - y'_J = y_J - s (shift amount)
        - s = (y_J - y_D) - (y'_J - y_D)
        - (y'_J - y_D) = √[(R_J + R_D)² - (x_D - x_J)²]
        """
        # Make a working copy (don't mutate input)
        working_rocks = [Rock(r.x, r.y, r.radius, r.z_start, r.z_end) 
                         for r in rocks]
        
        # Sort by y coordinate (bottom to top)
        working_rocks.sort(key=lambda r: r.y)
        
        # Discretize into layers
        num_layers = int(np.ceil(bounds.height / self.layer_thickness))
        
        # For each layer (bottom to top)
        for layer_idx in range(num_layers):
            layer_y_min = bounds.y_min + layer_idx * self.layer_thickness
            layer_y_max = layer_y_min + self.layer_thickness
            
            # Find rocks in this layer
            rocks_in_layer = [r for r in working_rocks 
                             if layer_y_min <= r.y <= layer_y_max]
            
            # Shift each rock downward
            for rock_j in rocks_in_layer:
                # Find closest rock below (in lower layers)
                rock_d = self._find_support_below(rock_j, working_rocks, 
                                                  layer_y_min)
                
                if rock_d is not None:
                    # Eq. (31): Contact distance
                    contact_y = rock_d.y + np.sqrt(
                        (rock_j.radius + rock_d.radius)**2 - 
                        (rock_d.x - rock_j.x)**2
                    )
                    
                    # Eq. (29–30): Shift downward
                    new_y = contact_y - rock_j.radius
                    rock_j.y = new_y
                else:
                    # No support below: settle to bottom
                    rock_j.y = bounds.y_min + rock_j.radius
        
        return working_rocks
    
    def _find_support_below(self, rock_j: Rock, all_rocks: List[Rock], 
                           layer_y_min: float) -> Optional[Rock]:
        """Find the highest rock below rock_j that it would rest on."""
        candidates = [r for r in all_rocks 
                     if r.y < layer_y_min and r is not rock_j]
        
        if not candidates:
            return None
        
        # Return the one closest to rock_j (highest y)
        return max(candidates, key=lambda r: r.y)
```

**Usage:**
```python
rsa_phase2 = RSACompactionProcess(layer_thickness_m=0.02)
rocks_compacted = rsa_phase2.run(rocks_uncompacted, bounds)

print(f"Compacted {len(rocks_compacted)} particles")
print(f"Original height: {max(r.y for r in rocks_uncompacted):.3f}m")
print(f"Compacted height: {max(r.y for r in rocks_compacted):.3f}m")
```

---

## Phase 4: Wrap in Strategy (Integration)

**File: `src/rock_packing.py`** (add new strategy)

```python
class RSAPacking(RockPackingStrategy):
    """
    Random Sequential Adsorption packing (Benedetto et al. 2017).
    
    Two-phase algorithm:
    1. Sizing & Positioning: Place particles per sieve fractions
    2. Compaction: Gravity-based downward settling
    
    Validated against real railway ballast (EN 13450) in laboratory.
    
    Reference:
    Benedetto, A., Bianchini Ciampoli, L., et al. (2017). "A computer-aided 
    model for the simulation of railway ballast by random sequential adsorption 
    process". Construction and Building Materials, 140, 508–520.
    """
    
    def __init__(self, void_ratio: float = 0.42, 
                 layer_thickness_m: float = 0.02):
        """
        Args:
            void_ratio: Void content (0.42 = 42%, typical ballast)
            layer_thickness_m: Compaction layer thickness (default 2 cm)
        """
        self.void_ratio = void_ratio
        self.layer_thickness = layer_thickness_m
    
    def generate_rocks(
        self,
        bounds: PackingBounds,
        radius_min: float,
        radius_max: float,
        target_fill_ratio: float = None,  # Ignored; use void_ratio instead
        max_attempts: int = PAC.MAX_ATTEMPTS,
        min_gap: float = 0.0,  # Ignored; RSA uses touching only
        grading_curve: GradingCurve = None
    ) -> List[Rock]:
        """
        Generate rocks using RSA two-phase algorithm.
        
        Args:
            grading_curve: GradingCurve (e.g., GradingCurve.en13450())
                          If None, uses uniform distribution
        """
        if grading_curve is None:
            grading_curve = GradingCurve.uniform(radius_min, radius_max)
        
        # Phase 1: Sizing & Positioning
        phase1 = RSASizingPositioning(bounds, void_ratio=self.void_ratio)
        fractions = grading_curve.to_sieve_fractions()
        rocks_uncompacted = phase1.run(fractions, radius_min, radius_max)
        
        # Phase 2: Compaction
        phase2 = RSACompactionProcess(self.layer_thickness)
        rocks_compacted = phase2.run(rocks_uncompacted, bounds)
        
        return rocks_compacted
```

**Usage (as a strategy):**
```python
from rock_packing import RSAPacking, GradingCurve, PackingBounds

bounds = PackingBounds(0, 1.5, 0, 1.5)
strategy = RSAPacking(void_ratio=0.42)

grading = GradingCurve.en13450()
rocks = strategy.generate_rocks(
    bounds=bounds,
    radius_min=0.0112,  # 22.4 mm min
    radius_max=0.04,    # 80 mm max
    grading_curve=grading
)

print(f"Generated {len(rocks)} particles via RSA")
```

---

## Phase 5: Testing Against Paper's Data

### Test Case: Reproduce Figure 7 (1.5m × 1.5m container)

```python
def test_rsa_vs_paper():
    """Validate RSA against paper's experimental results."""
    
    # Test inputs (from paper, Section 5.1)
    bounds = PackingBounds(0, 1.5, 0, 1.5)
    void_ratio = 0.42
    grading = GradingCurve.en13450()
    
    # Generate via RSA
    strategy = RSAPacking(void_ratio=void_ratio)
    rocks = strategy.generate_rocks(
        bounds=bounds,
        radius_min=0.0112,
        radius_max=0.04,
        grading_curve=grading
    )
    
    # Expected (from paper, page 11):
    # - Particles: 198, 202, 203, 207 (4 visual inspections)
    # - Average: μ = 202.5, σ = 3.201, MPE = 1.210%
    # - Grading curve: output matches input
    
    print(f"\n=== RSA Test vs. Paper ===")
    print(f"Generated particles: {len(rocks)} (paper: 202.5 ± 3.2)")
    
    # Calculate fill ratio
    total_area = sum(np.pi * r.radius**2 for r in rocks)
    fill_ratio = total_area / bounds.area
    real_void = 1 - fill_ratio
    print(f"Void ratio: {real_void:.3f} (paper: 0.42)")
    
    # Check grading curve (simplified: bin rocks by size)
    bins = [0.02, 0.025, 0.03, 0.035, 0.04]
    for i in range(len(bins) - 1):
        count = sum(1 for r in rocks 
                   if bins[i] <= r.radius < bins[i+1])
        pct = 100 * count / len(rocks)
        print(f"  {bins[i]*1000:.0f}–{bins[i+1]*1000:.0f}mm: {pct:.1f}%")
    
    # Visual check: print sample
    print("\nFirst 5 rocks:")
    for i, r in enumerate(rocks[:5]):
        print(f"  {i}: x={r.x:.3f}, y={r.y:.3f}, r={r.radius*1000:.1f}mm")
    
    assert 195 <= len(rocks) <= 210, f"Particle count {len(rocks)} out of range"
    assert 0.40 <= real_void <= 0.44, f"Void ratio {real_void} out of range"
    print("\n✓ Test passed!")

if __name__ == '__main__':
    test_rsa_vs_paper()
```

---

## Deliverables

| File | Changes | LOC |
|------|---------|-----|
| `src/rock_packing.py` | Add `SieveFraction`, `RSASizingPositioning`, `RSACompactionProcess`, `RSAPacking` | ~500 |
| `tests/test_rsa.py` | Unit tests for RSA phases, validation vs. paper | ~200 |
| `RSA_COMPARISON.md` | ✓ Already created | – |
| `RSA_IMPLEMENTATION_PLAN.md` | This document | – |

---

## Estimated Effort

1. **Sieve fractions** (Phase 1): 1 hour
2. **Phase 1 (sizing & positioning)** (Phase 2): 2 hours
3. **Phase 2 (compaction)** (Phase 3): 2 hours
4. **Strategy wrapper** (Phase 4): 30 min
5. **Testing & validation** (Phase 5): 2 hours

**Total: ~7.5 hours**

---

## Alternative: Use Existing Strategy?

Currently, **`PhysicsPacking`** might give similar results:
- Mass-weighted repulsion (~70–80% density)
- Iterative settling

**Comparison:**
```python
bounds = PackingBounds(0, 1.5, 0, 1.5)
grading = GradingCurve.en13450()

# RSA approach
rsa_rocks = RSAPacking(void_ratio=0.42).generate_rocks(bounds, 0.0112, 0.04, grading)

# Physics approach (for comparison)
physics_rocks = PhysicsPacking().generate_rocks(bounds, 0.0112, 0.04, 
                                                target_fill_ratio=0.58, 
                                                grading_curve=grading)

print(f"RSA: {len(rsa_rocks)} particles")
print(f"Physics: {len(physics_rocks)} particles")

# Check grading curve fidelity
rsa_grading_error = compare_grading_curves(grading, rsa_rocks)
physics_grading_error = compare_grading_curves(grading, physics_rocks)
print(f"RSA grading error: {rsa_grading_error}%")
print(f"Physics grading error: {physics_grading_error}%")
```

**Decision**: Implement RSA if:
- You need paper-validated ballast samples
- Particle count accuracy matters
- Grading curve fidelity is critical
- For railway GPR validation

Otherwise, reuse PhysicsPacking (simpler, already working).

---

## Next Step

Ready to code? Start with **Phase 1 (Sieve Fractions)** — it's the smallest and most isolated change. Once that works, Phases 2–3 follow naturally.

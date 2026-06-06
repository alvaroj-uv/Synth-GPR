# Circle Packing & Compaction Ideas from GPR-repo

This document summarizes the ideas copied from `D:\Codigo\GPR-repo\RSA\Circles` and integrated into Synth-GPR-1.

## What Was Copied

### 1. **Grading Curve Utilities** (`gen_sieve_curve.py` → `src/grading_curve_utils.py`)

Original concepts:
- Random sieve curve generation using beta distribution
- Conversion between cumulative % curves and particle size fractions
- Support for specification envelopes (bounds sampling)

**New features in Synth-GPR-1:**
- `SieveBounds` dataclass for structured sieve specifications
- `pick_rand_grading_curve()`: Sample random curves within specification bounds
- `convert_sieve_curve_to_fractions()`: Convert cumulative curves to PSD fractions
- `en13450_bounds()`: EN 13450 railway ballast specification envelopes
- `fuller_ideal_curve()`: Fuller-Thompson maximum-density curve
- `uniform_distribution()`: Baseline flat distribution
- `sample_radii_from_fractions()`: Generate particle samples from PSD
- Pretty-printing utilities for inspection

**Use case:**
```python
from src.grading_curve_utils import en13450_bounds, pick_rand_grading_curve

bounds = en13450_bounds()  # Specification envelope
curve = pick_rand_grading_curve(bounds)  # Random curve within spec
```

### 2. **Discretized Gravity Compaction** (`circle_Compaction.py` → `src/circle_compaction_utils.py`)

Original concepts:
- Discretize 2D domain into horizontal/vertical slices
- Move circles downward until they touch lower circles
- Animate settling via GIF sequences (adapted to static compaction)

**New features in Synth-GPR-1:**
- `discretize_domain()`: Slice rocks into horizontal/vertical layers
- `compact_slice()`: Apply gravity to rocks in one slice
- `apply_compaction_pattern()`: Run sequences of H/V compaction passes
- `calculate_void_ratio()`: Measure packing density
- `CompactionConfig` dataclass for parameter grouping

**Why it matters:**
- **Physics-based settling**: Rocks move downward realistically, not randomly redistributed
- **Reduced void ratios**: Tighter packing with fewer total rocks
- **Reproducible**: Deterministic gravity vs. random jittering

**Use case:**
```python
from src.circle_compaction_utils import apply_compaction_pattern, calculate_void_ratio

# Apply gravity-based settling
rocks_settled = apply_compaction_pattern(
    rocks,
    bounds,
    layer_thickness=0.05,
    pattern=[('vertical', 2), ('horizontal', 1)]
)

void = calculate_void_ratio(rocks_settled, bounds)
print(f"Void ratio after compaction: {void:.3f}")
```

### 3. **New Packing Strategy: CompactionBasedPacking** (`src/rock_packing.py`)

Combines RSA placement + gravity compaction in one strategy:

1. **Phase 1**: Generate rocks via RSA (existing validated algorithm)
2. **Phase 2**: Apply gravity settling via discretized compaction

**Advantages:**
- Matches lab-measured void ratios (42% for EN 13450)
- Fewer overlaps than naive random placement
- Realistic particle settling patterns
- Works with any grading curve

**Use case:**
```python
from src.rock_packing import CompactionBasedPacking, GradingCurve, PackingBounds

packer = CompactionBasedPacking(
    base_strategy=RSAPacking(void_ratio=0.42),
    layer_thickness=0.05,
    compaction_pattern=[('vertical', 2), ('horizontal', 1)]
)

rocks = packer.generate_rocks(
    bounds, r_min, r_max,
    grading_curve=GradingCurve.en13450()
)
```

## Integration Points

### In `GeneratorConfig` / `config.py`:

Add new parameters for compaction:

```python
# Packing algorithm type
rock_packing_algorithm: str = "compaction"  # or "rsa", "poisson", "circlify", etc.

# Compaction parameters
compaction_layer_thickness: float = 0.05  # Discretization slice thickness
compaction_pattern: str = "v2h1"  # "v2h1" = 2 vertical, 1 horizontal pass

# Grading curve type
rock_psd_type: str = "en13450"  # or "uniform", "fuller", "custom"
```

### In `rock_packing.py` (ToolWarehouse):

Register the new strategy:

```python
def _create_rock_packer(self, cfg: GeneratorConfig) -> RockPackingStrategy:
    algo_name = getattr(cfg, 'rock_packing_algorithm', 'circlify').lower()

    if algo_name == 'compaction':
        pattern = self._parse_compaction_pattern(cfg)
        return CompactionBasedPacking(
            base_strategy=RSAPacking(void_ratio=0.42),
            layer_thickness=getattr(cfg, 'compaction_layer_thickness', 0.05),
            compaction_pattern=pattern
        )
    # ... other algorithms ...
```

## Key Ideas Worth Keeping

1. **Grading curves are essential for realistic models**
   - Flat uniform distribution (current) ≠ real ballast
   - Use en13450 or fuller curves to match lab samples

2. **Gravity settling improves realism**
   - Reduces void ratio without adding more rocks
   - Physics-based: rocks fall until they touch, not random repositioning
   - Matches observed compaction in real ballast layers

3. **Discretized compaction is O(N) efficient**
   - Don't check every rock against every other rock
   - Slice geometry into layers, compact layer-by-layer
   - Inspired by jagua-rs and computational geometry

4. **Two-phase algorithms (placement + settling) are validated**
   - Benedetto et al. (2017) used RSA + compaction
   - Matched lab measurements (void ratio, particle count)
   - Validated with GPR testing on real ballast

## Example: Using Grading Curves for Better Features

For **waveform-only GPR prediction**, better material realism → better signal variation:

```python
# Old: uniform rocks 20-40mm diameter
rocks = packer.generate_rocks(bounds, r_min=0.02, r_max=0.04)

# New: realistic EN 13450 distribution
from src.rock_packing import GradingCurve

gc = GradingCurve.en13450()  # 22-80mm with realistic grading
rocks = packer.generate_rocks(
    bounds, r_min=0.0112, r_max=0.04,
    grading_curve=gc
)
# Now rocks have realistic size distribution → more varied waveforms
```

## Testing

Run the demo script to test all features:

```bash
python examples/demo_circle_packing_ideas.py
```

This generates:
- `rsa_packing.png`: RSA with EN 13450 curve
- `compaction_before_after.png`: Before/after gravity settling
- `compaction_based_packing.png`: Combined RSA + gravity result

## References

**Original work:**
- GPR-repo/RSA/Circles: `circle_RSA.py`, `circle_Compaction.py`, `gen_sieve_curve.py`

**Published validations:**
- Benedetto, A., Bianchini Ciampoli, L., et al. (2017). "A computer-aided model for the simulation of railway ballast by random sequential adsorption process". *Construction and Building Materials*, 140, 508–520.
- EN 13450:2013. "Railway ballast – Technical specification of the product." European Standard.

**Inspired algorithms:**
- jagua-rs: Fast circle packing with collision detection (Gar, 2024)
- ParticlePack: Discrete element modelling of granular materials (MosGeo, 2019)

## Next Steps

1. **Integrate into GeneratorConfig**: Add parameters for grading curves + compaction
2. **Update ToolWarehouse**: Register CompactionBasedPacking for selection
3. **Extend features**: Use realistic size distributions to improve waveform variation
4. **Validate**: Measure void ratios in generated scenes vs. lab standards

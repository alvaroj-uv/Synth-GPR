# Rock Packing Algorithms

This document describes the 12 available rock packing algorithms in the Synth-GPR system and their characteristics.

## Overview

Rock packing algorithms are used by `GranularMatrixWorker` to distribute rock particles (circles in 2D cross-section) throughout the ballast layer. Each algorithm has different performance characteristics, output quality, and computational cost.

All 12 algorithms now conform to a unified API:
```python
generate_rocks(
    bounds: PackingBounds,
    radius_min: float,
    radius_max: float,
    target_fill_ratio: float = 0.6,
    max_attempts: int = 1000,
    min_gap: float = 0.0,
    grading_curve: Any = None
) -> List[Rock]
```

## Algorithm Categories

### Ultra-Fast (< 1 second per sample)

| Algorithm | Exec Time | Quality | Use Case |
|-----------|-----------|---------|----------|
| **RSA** | 0.2s | Low (FI~42) | Rapid prototyping, testing |
| **Grid** | 0.3s | Low (FI~45) | Fallback, deterministic |
| **PoissonDisk** | 0.6s | Medium (FI~35) | Development builds |
| **Random** | 0.8s | Low (FI~40) | Baseline comparisons |

### Medium Speed (1-10 seconds)

| Algorithm | Exec Time | Quality | Use Case |
|-----------|-----------|---------|----------|
| **Circlify** | 7.1s | Medium (FI~28) | Development |
| **SimulatedAnnealing** | 8.0s | Fallback to Random | Testing |

### Production Quality (15-30+ seconds)

| Algorithm | Exec Time | Quality | Use Case |
|-----------|-----------|---------|----------|
| **Growth** | 15.3s | High (FI~33) | Validation builds |
| **ShangChu** | 16.0s | Best (FI~24) | Production datasets |

### Slow/Limited (experimental or with dependencies)

| Algorithm | Status | Notes |
|-----------|--------|-------|
| **WangTile** | Working | Slow initialization (~2-3s), specialized tiling |
| **FrontChain** | Working | Slow with high target_fill (~5-10s) |
| **Physics** | Working | Very slow O(N²) physics simulation, use cautiously |
| **Triangle** | Fallback | Requires scipy; falls back to Random if not installed |

## Recommended Configurations

### Development (fastest iteration)
```python
rock_packing_algorithm = "rsa"  # 0.2s per sample
```

### Testing/Validation
```python
rock_packing_algorithm = "poisson_disk"  # 0.6s, decent quality
```

### Production
```python
rock_packing_algorithm = "shang_chu"  # 16s, best quality (FI~24)
```

### Hybrid (fastest for 100 samples)
```
Phase 1 (Development):  RSA (20.7s for 100 samples)
Phase 2 (Validation):   Poisson Disk (26.3s for 100 samples)
Phase 3 (Production):   Growth or ShangChu (1530s for 100 samples)
Total: 8.9x faster than pure ShangChu
```

## API Compatibility Note

**Date Fixed:** 2026-05-27

Previously, 7 algorithms were missing `min_gap` and `grading_curve` parameters, causing `TypeError` when called from `GranularMatrixWorker`. All algorithms have been unified to accept the full parameter set. Most algorithms ignore these parameters (they're primarily used by ShangChu's grading curve feature), but they accept them for API compatibility.

**Commit:** c43fd64

## Algorithm Implementation Details

### ShangChu (Shang Chu Circle Packing)
- **Author:** Adapted from Shang Chu's algorithm
- **Method:** Quasi-physical relaxation with grading curve support
- **Strengths:** Highest quality output, realistic rock distributions
- **Weaknesses:** Slowest algorithm, requires tuning
- **Parameters Used:** `grading_curve` (particle size distribution)
- **Location:** `src/rock_packing.py::ShangChuPacking`

### Growth (Circle Growth Algorithm)
- **Method:** Iteratively grow circles from min to max radius
- **Strengths:** Good quality-to-speed ratio, no overlaps guaranteed
- **Weaknesses:** Slower than fast algorithms, lower density than ShangChu
- **Location:** `src/rock_packing.py::GrowthPacking`

### RSA (Random Sequential Adsorption)
- **Method:** Randomly place circles, reject overlaps
- **Strengths:** Extremely fast, guaranteed no overlaps
- **Weaknesses:** Lower packing density, poor fracture index scores
- **Location:** `src/rock_packing.py::RSAPacking`

### PoissonDisk (Bridson's Algorithm)
- **Method:** Maintain separation distance via spatial grid
- **Strengths:** Fast, uniform distribution, no overlaps
- **Weaknesses:** Regular patterns (less realistic), medium density
- **Location:** `src/rock_packing.py::PoissonDiskPacking`

### Grid
- **Method:** Deterministic grid-based placement
- **Strengths:** Guaranteed completion, deterministic, very fast
- **Weaknesses:** Artificial appearance, low density
- **Location:** `src/rock_packing.py::GridPacking`

### Others
See `src/rock_packing.py` for implementation details on WangTile, FrontChain, Physics (force-directed), Triangle (Delaunay), Circlify, SimulatedAnnealing, and Random algorithms.

## Configuration

Set algorithm via `GeneratorConfig`:
```python
config = GeneratorConfig.create_physically_perfect(
    rock_packing_algorithm="shang_chu",  # or any of the 12 algorithms
    ...
)
```

Or via command line:
```bash
python scripts/main/generate_in_files.py out/ --mode batch --packing shang_chu
```

## Troubleshooting

**Algorithm hung or very slow:**
- Physics, WangTile, and FrontChain can be slow depending on parameters
- Try RSA or Grid for quick tests
- Reduce `max_attempts` parameter

**Scipy dependency missing for Triangle:**
- Algorithm falls back to RandomPacking if scipy not available
- Install with: `pip install scipy`

**Low packing density:**
- Try ShangChu or Growth instead of RSA
- Increase `target_fill_ratio` (but may take longer)
- Verify domain size isn't too small for particle sizes

# Mbubia Scene Generation with Pymunk

Generate realistic two-layer Mbubia railway ballast scenes using pymunk physics engine.

## Overview

This generates synthetic GPR scenes based on the Mbubia et al. (2026) railway ballast configuration:
- **Two distinct layers:** clean ballast, fouled ballast, or subgrade soil
- **Realistic geometry:** Polygon rocks (6-12 sides) instead of circles
- **Physics-based:** Gravity compaction using pymunk 2D rigid-body dynamics
- **Compatible with gprMax:** Outputs .in files for electromagnetic simulation

## Scene Types

| Scene | Upper Layer | Lower Layer | Contrast | Use Case |
|-------|-------------|-------------|----------|----------|
| `clean_fouled` | Clean ballast (εr=4.10) | Fouled ballast (εr=4.23) | Small | Subtle fouling detection |
| `fouled_subgrade` | Fouled ballast (εr=4.23) | Subgrade soil (εr=5.50) | Medium | Typical railway profile |
| `clean_subgrade` | Clean ballast (εr=4.10) | Subgrade soil (εr=5.50) | Large | Best contrast |
| `highly_fouled` | Fouled ballast (εr=4.23) | Highly fouled (εr=4.35) | Very small | Difficult discrimination |

## Domain Configuration

```
Scan width (X):     4.0 m   (realistic for railway survey)
Depth (Y):          1.2 m   (includes ballast + subgrade)
Width (Z):          0.05 m  (2D simulation in 3D space)

Layer interface:    0.488 m (from bottom)
Grid resolution:    2 mm    (dx=dy=0.002m, dz=0.001m)
Antenna frequency:  1.4 GHz (Ricker pulse)
Antenna height:     0.30 m  (above surface)
```

## Quick Start

### Generate All Scenes

```bash
python examples/demo_mbubia_pymunk.py
```

Outputs:
- `output/mbubia_pymunk/mbubia_pymunk_*.in` — gprMax input files
- `output/mbubia_pymunk/mbubia_pymunk_*.json` — Rock geometry data
- `output/mbubia_pymunk/mbubia_pymunk_*.png` — Visualizations

### Generate Single Scene

```bash
python examples/demo_mbubia_pymunk.py \
    --scene clean_fouled \
    --runtime 3.0
```

### With Visualization (requires pygame)

```bash
python examples/demo_mbubia_pymunk.py \
    --scene clean_fouled \
    --display  # Show pygame window during simulation
```

## From Python

```python
from src.pymunk_packing import MbubiaPymunkSceneGenerator
from pathlib import Path

# Create generator
gen = MbubiaPymunkSceneGenerator(
    scene_name='clean_fouled',
    upper_material='clean_ballast',
    lower_material='fouled_ballast',
    output_dir=Path('output/mbubia_pymunk')
)

# Run physics simulation
gen.generate(running_time=3.0, display=False)

# Export results
gen.export_gprmax_in()    # .in file for gprMax
gen.export_json()         # Rock data as JSON
gen.export_png()          # Visualization
```

## Simulation Details

### Physics Engine

- **Engine:** pymunk (2D rigid-body dynamics with gravity)
- **Gravity:** 9.81 m/s² (Earth standard)
- **Time step:** 0.01 s (configurable)
- **Running time:** 2-3 s typical (allows settling)

### Rock Placement

**Phase 1: Random Sequential Adsorption (RSA)**
- Upper layer: ~300 polygon rocks (0.008-0.04 m radius)
- Lower layer: ~450 polygon rocks (0.008-0.04 m radius)
- Placement: Random x, y within layer bounds
- Overlap: Checked, rocks skipped if overlapping

**Phase 2: Gravity Compaction**
- Rocks settle under gravity
- Physics solver handles collisions
- Realistic void fractions (~44%)
- No material penetration

### Polygon Generation

Each rock is a random polygon with:
- Sides: 6-12 (randomly chosen)
- Shape: Regular polygon + small perturbations
- Vertices: Converted to pymunk for physics
- Material: Based on layer (clean/fouled/subgrade)

## Export Formats

### .in Format (gprMax)

```
#title: Mbubia Pymunk Scene - CLEAN_FOULED
#domain: 4.000 1.200 0.050
#dx_dy_dz: 0.002 0.002 0.001
#time_window: 20e-9

#material: 4.10 0.001 1.0 0.0 clean_ballast
#material: 4.23 0.005 1.0 0.0 fouled_ballast

#hertzian_dipole: z 2.00 0.30 0 myricker
#rx: 2.00 0.30 0
#waveform: ricker 1 1400000000 myricker

#box: 0 0 0 4.000 1.200 0.050 clean_ballast
#box: 0 0 0 4.000 0.488 0.050 fouled_ballast

#polygon: 8 x1 y1 z1 x2 y2 z2 ... material
...

#run_simulation
```

### JSON Format

```json
{
  "scene_name": "clean_fouled",
  "upper_material": "clean_ballast",
  "lower_material": "fouled_ballast",
  "layer_interface_y": 0.488,
  "domain": {"x": 4.0, "y": 1.2, "z": 0.05},
  "antenna_height": 0.30,
  "frequency_ghz": 1.4,
  "n_rocks": 745,
  "rocks": [
    {
      "x": 0.543,
      "y": 0.721,
      "vertices": [[x1, y1], [x2, y2], ...],
      "material": "clean_ballast",
      "n_sides": 8
    },
    ...
  ]
}
```

## Running gprMax Simulations

After generating scenes:

```bash
# Single simulation
python -m gprMax output/mbubia_pymunk/mbubia_pymunk_clean_fouled.in

# All scenes
for file in output/mbubia_pymunk/*.in; do
    python -m gprMax "$file"
done
```

Expected output:
- Simulation time: 10-30 minutes per scene (1.2M cells)
- Output file: ~50-100 MB per scene (HDF5 format)
- Files: `*.out` in same directory as .in

## Feature Extraction

After gprMax simulations:

```python
from src.feature_extraction import extract_features
import pandas as pd

# Extract from all simulations
features = extract_features('output/mbubia_pymunk')

# Expected output
print(features.shape)  # (n_aScans, 572)
print(features.columns)  # 572 waveform features
```

## Validation Workflow

```
1. Generate scenes (this script)
   ↓
2. Run gprMax simulations
   python -m gprMax *.in
   ↓
3. Extract features
   python scripts/pipeline/extract_features.py
   ↓
4. Test with RF model
   python scripts/validation/test_on_mbubia.py
   ↓
5. Compare with synthetic baseline
   Analyze frequency/geometry transfer
```

## Material Properties

### Clean Ballast
- Permittivity (εr): 4.10
- Conductivity (σ): 0.001 S/m
- Density: 2650 kg/m³
- Appearance: Coarse, well-graded
- Use: Undamaged track

### Fouled Ballast
- Permittivity (εr): 4.23
- Conductivity (σ): 0.005 S/m
- Density: 2500 kg/m³
- Appearance: Mixed rock + fines
- Use: Moderately fouled track

### Highly Fouled Ballast
- Permittivity (εr): 4.35
- Conductivity (σ): 0.008 S/m
- Density: 2400 kg/m³
- Appearance: Fine-dominated, clay-heavy
- Use: Severely fouled track

### Subgrade Soil
- Permittivity (εr): 5.50
- Conductivity (σ): 0.010 S/m
- Density: 2200 kg/m³
- Appearance: Clay/silt foundation
- Use: Below ballast layer

## Differences from Existing Synthetic

| Aspect | Synth-GPR Baseline | Mbubia Pymunk |
|--------|-------------------|---------------|
| Frequency | 400 MHz | 1.4 GHz (3.5× higher) |
| Domain size | 0.6×0.5 m | 4.0×1.2 m (6.7× larger) |
| Rock shapes | Circles/cylinders | Polygons (6-12 sides) |
| Layers | Single (homogeneous) | Two (clear interface) |
| Rock count | ~1000 | ~800-900 |
| Total cells | ~360k | ~1.2M (3.3×) |
| Purpose | Isolated layer study | Real railway geometry |

## Troubleshooting

### "pygame not found"
```bash
pip install pygame
```

### "matplotlib not found"
```bash
pip install matplotlib
```

### Slow simulation
- Reduce `--runtime` (e.g., 1.0 instead of 3.0)
- Reduce rock count in source code
- Use faster machine

### Export issues
- Check output directory exists
- Ensure write permissions

## Research Applications

### 1. Domain Gap Analysis
- Train RF on 400 MHz synthetic
- Test on 1.4 GHz Mbubia
- Measure frequency-generalization

### 2. Geometry Robustness
- Do polygon rocks cause different features?
- Compare scattering patterns (circle vs polygon)

### 3. Interface Detection
- Can RF detect layer boundaries?
- Are time-domain or frequency-domain features better?

### 4. Material Classification
- How well does RF discriminate clean vs fouled?
- Does frequency mismatch reduce accuracy?

## References

- **Mbubia et al. (2026):** "GPR and AI for Automated Railway Trackbed Stratigraphy and Fouling Assessment"
  - DOI: 10.1016/j.treng.2025.100415
  - Mask R-CNN + XGBoost approach
  - Real field validation

- **This implementation:**
  - Pymunk physics engine: https://www.pymunk.org/
  - RSA algorithm: Meagher et al., Physics of Fluids (1980)
  - Railway ballast: Selig & Waters, ASCE Manual (1994)

## Authors

Generated with Pymunk physics engine for Synth-GPR project.
Contact: alvaro.jeria.m@gmail.com

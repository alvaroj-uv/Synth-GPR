# Generating .in Files — Complete Guide

This document explains how to generate `.in` files (gprMax simulation inputs) for the Synth-GPR project using the unified `generate_in_files.py` script.

## Quick Start

**Batch generation** (50 files per fouling class):
```bash
python scripts/main/generate_in_files.py output/ --mode batch --labels CL MC MF -n 50
```

**Single file** (with visualization):
```bash
python scripts/main/generate_in_files.py test.in --mode single --pvc 25 --render
```

---

## Two Generation Modes

### 1. Batch Mode (`--mode batch`)

Generate multiple `.in` files organized by fouling class. Produces:
- `.in` files: `s_0000.in`, `s_0001.in`, ...
- Metadata: `metadata_CL.csv`, `metadata_MC.csv`, ... (per label)

**Typical usage:**
```bash
python scripts/main/generate_in_files.py output/ --mode batch \
    --labels CL MC MF F HF \
    -n 100 \
    --start-id 1000
```

**Result:**
- 500 total files (100 per class)
- Files named: `s_1000.in` through `s_1499.in`
- Each class has its own metadata CSV

### 2. Single Mode (`--mode single`)

Generate one `.in` file with specified parameters. Optionally render PNG visualization.

**Typical usage:**
```bash
python scripts/main/generate_in_files.py out.in --mode single --pvc 30 --moisture 0.08 --render
```

**Result:**
- One `.in` file: `out.in`
- Optional PNG: `out.png` (if `--render`)

### 3. Parameter-Based Replication

Regenerate files using parameters extracted from existing `.in` files. No special mode needed—just use `--mode single` with the `--params-from` flag.

**Why use parameter extraction?**
- You have an old `.in` file and want to generate more samples with identical configuration
- You want to verify reproducibility (same seed produces same geometry)
- You lost the metadata CSV but still have the .in file with embedded config
- You want to regenerate with mostly the same config but override one or two parameters

**Typical usage:**
```bash
# Regenerate exact copy
python scripts/main/generate_in_files.py replicated.in --mode single --params-from original.in

# Regenerate with parameter override
python scripts/main/generate_in_files.py modified.in --mode single --params-from original.in --pvc 35
```

**Result:**
- New `.in` file with identical config to original (or with specified overrides)
- Same random seed ensures identical rock packing geometry
- All config parameters (frequency, packing algorithm, rock shape, etc.) preserved

**How it works:**
1. Extracts `CONFIG_*` parameters from original .in file header
2. Uses extracted parameters for new generation
3. Command-line args override extracted parameters if provided
4. Regenerates geometry using same seed (produces identical rock positions)
5. Writes new .in file with embedded config

---

## Arguments Reference

### Positional Arguments

| Argument | Mode | Meaning |
|----------|------|---------|
| `output` | Both | Output directory (batch) or file path (single) |

### Mode Selection

| Flag | Values | Default | Meaning |
|------|--------|---------|---------|
| `--mode` | `batch`, `single` | `batch` | Which generation mode to use |

### Batch-Specific Options

| Flag | Type | Default | Meaning |
|------|------|---------|---------|
| `--labels` | space-separated | `CL MC MF F` | Fouling classes to generate. Valid: `CL`, `MC`, `MF`, `F`, `HF` |
| `-n, --num` | int | 50 | Samples per label |
| `--start-id` | int | 1000 | Starting ID for filenames (e.g., 1000 → s_1000.in) |
| `--moisture-max` | float (0–1) | 0.15 | Maximum volumetric moisture content |
| `--seed` | int | None | Random seed for reproducibility. If None, uses `start_id` |

### Single-Specific Options

| Flag | Type | Default | Meaning |
|------|------|---------|---------|
| `--pvc` | float (0–100) | None | PVC percentage. If None, sampled randomly |
| `--moisture` | float (0–1) | None | Moisture fraction. If None, sampled randomly |
| `--render` | flag | False | Generate PNG visualization of geometry |

### Parameter Extraction (Single Mode)

| Flag | Type | Default | Meaning |
|------|------|---------|---------|
| `--params-from` | str (path) | None | Extract generation parameters from existing .in file (single mode) |

### Common Options (All Modes)

| Flag | Type | Default | Meaning |
|------|------|---------|---------|
| `--freq` | float (Hz) | 1.5e9 | Center frequency (1.5e9 = 1.5 GHz, 400e6 = 400 MHz) |
| `--angular` | flag | False | Use polygonal rocks instead of cylinders |
| `--sides` | int | 6 | Number of sides for polygonal rocks (6 = hexagon, 8 = octagon) |
| `--packing-algo` | str | `circlify` | Rock packing algorithm. Options: `circlify`, `front_chain`, `rsa`, `shang_chu`, `random`, `poisson`, etc. |
| `--psd` | str | `uniform` | Particle size distribution: `uniform`, `en13450` (EN 13450 railway ballast), `fuller` (max density) |
| `--num-rx` | int | 1 | Number of receivers (1 = single offset, >1 = linear array) |
| `--rx-spacing` | float (m) | 0.05 | Distance between receivers (default 5 cm) |

---

## Fouling Classes & PVC Ranges

Railway ballast fouling is classified by Particle Volume Concentration (PVC):

| Class | Code | PVC Range | Description |
|-------|------|-----------|-------------|
| Clean | CL | 0–5% | Excellent drainage, good ballast condition |
| Moderately Clean | MC | 5–20% | Light fouling, acceptable drainage |
| Moderately Fouled | MF | 20–40% | Moderate fouling, degraded drainage |
| Fouled | F | 40–60% | Heavy fouling, poor drainage |
| Highly Fouled | HF | 60–100% | Severe fouling, very poor drainage |

In **batch mode**, each class is sampled uniformly within its PVC range, creating diverse training data.

In **single mode**, `--pvc` specifies an exact value (no sampling).

---

## Common Use Cases

### 1. Build Standard Dataset (1.5 GHz, Circular Rocks)

```bash
python scripts/main/generate_in_files.py data/standard_1p5ghz/ --mode batch \
    --labels CL MC MF F HF \
    -n 200 \
    --start-id 10000
```

**Output:**
- 1000 files (200 per class)
- 1.5 GHz center frequency
- Circular rock geometry
- Uniform PSD, circlify packing

---

### 2. Build 400 MHz Dataset with Angular Rocks

```bash
python scripts/main/generate_in_files.py data/angular_400mhz/ --mode batch \
    --labels CL MC MF F HF \
    -n 1000 \
    --freq 400e6 \
    --angular \
    --sides 6 \
    --packing-algo circlify \
    --start-id 0
```

**Output:**
- 5000 files (1000 per class)
- 400 MHz center frequency (automatically scales domain/resolution)
- Hexagonal rocks
- Repeatable with `--seed 42`

---

### 3. Quick Test: One File per Class

```bash
python scripts/main/generate_in_files.py test_data/ --mode batch \
    --labels CL MC MF F HF \
    -n 1
```

**Output:**
- 5 files total (one per class)
- Quick sanity check of the pipeline

---

### 4. Single File with Custom Parameters & Visualization

```bash
python scripts/main/generate_in_files.py my_ballast.in --mode single \
    --pvc 35 \
    --moisture 0.12 \
    --freq 400e6 \
    --angular \
    --sides 8 \
    --render
```

**Output:**
- `my_ballast.in` (gprMax input file)
- `my_ballast.png` (visualization of geometry)

Open the PNG in any image viewer to inspect rock placement, layer structure, antenna position.

---

### 5. Reproducible Generation (Seeded)

**Single file with seed:**
```bash
python scripts/main/generate_in_files.py my_ballast.in --mode single \
    --pvc 25 \
    --moisture 0.10 \
    --seed 42
```

**Reproduce from existing file:**
```bash
python scripts/main/generate_in_files.py copy.in --mode single --params-from my_ballast.in
```

**Note:** 
- Running with the same `--seed` generates identical files (rock placement is deterministic)
- Using `--params-from` extracts all parameters including seed for exact reproduction
- Useful for:
  - Verifying pipeline behavior
  - Sharing reproducible datasets
  - Benchmarking
  - Archiving files with full reproducibility metadata

---

## Output Files & Organization

### Batch Mode Outputs

```
output/
├── s_1000.in              # Sample 1000 (first CL)
├── s_1001.in              # Sample 1001 (second CL)
├── ...
├── s_1099.in              # Sample 1099 (last CL)
├── s_1100.in              # Sample 1100 (first MC)
├── ...
├── metadata_CL.csv        # CL class metadata (100 rows)
├── metadata_MC.csv        # MC class metadata (100 rows)
└── ... (other classes)
```

**Metadata CSV columns:**
- `sample_id`: Unique file identifier
- `pvc`: Particle volume concentration (%)
- `moisture`: Moisture fraction (0–1)
- `rock_count`: Number of rock cylinders/polygons in ballast
- `FI_class`: Fouling Index class (computed from PVC & moisture)
- `Lab_Class`: Laboratory-assigned class
- `Lab_FI`: Laboratory Fouling Index
- `Lab_LDCP_FI_est`: Virtual LDCP estimation
- `Lab_bulk_eps`: Bulk permittivity
- `Lab_clean_ballast_mm`: Clean ballast depth (mm)
- `center_freq`: Center frequency (Hz)
- `tx_x`, `rx_x`: Transmitter/receiver X positions (m)
- `antenna_clearance_above_ballast`: Height above ballast (m)

### Single Mode Outputs

```
out.in                     # Generated .in file
out.png                    # [Optional] Visualization
```

---

## Frequency Scaling & Domain

The script automatically scales the computational domain and grid resolution based on frequency, following IEEE 2025 guidelines (Khosravi Largani et al.):

| Frequency | Domain X | Domain Y | Cell Size (dx) | Notes |
|-----------|----------|----------|----------------|-------|
| 400 MHz | 1.5 m | ~2.2 m | 7.5 mm | Coarser grid, faster sims |
| 1.0 GHz | 0.9 m | ~2.0 m | 4.5 mm | Mid-range |
| 1.5 GHz | 0.6 m | ~1.5 m | 3.0 mm | Fine grid, physically perfect |
| 2.5 GHz | 0.36 m | ~1.2 m | 1.8 mm | Very fine, slow sims |

**Key principle:** Higher frequency → smaller domain + finer grid (more FDTD cells).

To verify domain settings for your frequency:
```bash
# Inspect first generated .in file
head -20 output/s_1000.in
```

Look for:
```
#domain: 0.6 1.5 0.003      # Domain size (m)
#dx_dy_dz: 0.003 0.003 0.003  # Cell size (m)
```

---

## Rock Packing Algorithms

The `--packing-algo` option controls how rocks are placed:

| Algorithm | Meaning | Notes |
|-----------|---------|-------|
| `circlify` | Force-based circle packing | Produces realistic random arrangements, slightly faster |
| `front_chain` | Front-growing algorithm | Deterministic, reproducible per seed |
| `shang_chu` | Shang-Chu algorithm | Better fill density than front_chain |
| `rsa` | Random Sequential Addition | Simple, fast, but lower density |
| `random` | Purely random placement | Very fast, may overlap |
| `poisson` | Poisson disc sampling | Uniform distribution, no clustering |

**Recommendation:** Start with `circlify` (default) for realistic ballast.

---

## Particle Size Distribution (PSD)

The `--psd` option controls how rock radii are sampled:

| PSD Type | Meaning | Use Case |
|----------|---------|----------|
| `uniform` | Flat distribution (min–max radius) | Default, simple |
| `en13450` | EN 13450 railway ballast spec | Realistic UK/EU ballast size gradation |
| `fuller` | Fuller grading curve (max packing) | Denser packing, less void space |

---

## Antenna Configuration

By default, the script places antennas in **bistatic** configuration (separate TX/RX):
- TX: Center of domain
- RX: 5 cm offset from TX

To use **monostatic** (co-located) or **multi-offset** arrays, use `--num-rx`:

```bash
# Single bistatic (default)
python scripts/main/generate_in_files.py out/ --mode batch -n 50

# 3-channel array (TX + 2 RX at 5cm spacing)
python scripts/main/generate_in_files.py out/ --mode batch -n 50 \
    --num-rx 3 \
    --rx-spacing 0.05
```

---

## Replicating Exact .in Files

Each generated `.in` file contains its complete configuration parameters embedded in the header as `CONFIG_*` comments. This enables exact replication of geometries.

### View Embedded Configuration

```bash
# Display all CONFIG_ parameters
head -50 s_0100.in | grep CONFIG_

# Or get a formatted summary
python -c "from src.file_reader import get_config_summary; print(get_config_summary('s_0100.in'))"
```

**Output example:**
```
Frequency: 1500 MHz
Rocks: Circular
Packing: circlify (uniform PSD)
Receivers: 1
Seed: 100
```

### Replicate a File

Generate an exact copy using the embedded config. Just use `--mode single --params-from`:

```bash
# Basic replication
python scripts/main/generate_in_files.py replicated.in --mode single --params-from s_0100.in

# The replicated file will have:
# - Identical configuration (frequency, rock algorithm, PSD, etc.)
# - Identical random seed → identical rock positions
# - Same layer geometry
```

### Use Cases

1. **Lost metadata, have .in file?**
   ```bash
   python scripts/main/generate_in_files.py duplicate.in --mode single --params-from archival_file.in
   ```

2. **Verify reproducibility:**
   ```bash
   python scripts/main/generate_in_files.py test1.in --mode single --pvc 25 --seed 42
   python scripts/main/generate_in_files.py test2.in --mode single --params-from test1.in
   # test1.in and test2.in will have identical geometry (rock positions, layer heights, etc.)
   ```

3. **Share configuration details:**
   Files are self-documenting. Anyone with an `.in` file can see exactly how it was generated:
   ```bash
   grep "CONFIG_" simulation_result.in
   ```

---

## Troubleshooting

### Error: "Unknown fouling class 'XX'"

Valid classes are: `CL`, `MC`, `MF`, `F`, `HF`. Check spelling and case.

```bash
# ✗ Wrong
python scripts/main/generate_in_files.py out/ --mode batch --labels clean

# ✓ Correct
python scripts/main/generate_in_files.py out/ --mode batch --labels CL
```

### Error: "Domain height insufficient"

Your frequency is too high for the default domain height. Try:
1. Lower frequency: `--freq 1e9` instead of `2.5e9`
2. Or the script will auto-scale; just rerun

### PNG Visualization Fails

The visualization requires additional dependencies. Install with:
```bash
pip install matplotlib seaborn
```

Or generate without visualization:
```bash
python scripts/main/generate_in_files.py out.in --mode single --pvc 25
# (no --render flag)
```

### Files Generated but Look Wrong

Check the .in file header:
```bash
head -30 s_1000.in | grep -E "^#(domain|dx_dy_dz|time_window|pml)"
```

Ensure:
- `#domain`: Reasonable size for your frequency
- `#dx_dy_dz`: Matches domain (cubic cells)
- `#pml_cells`: `10 10 0 10 10 0` for 2D TMz
- All material definitions appear before geometry

### Slow Generation

- Reduce `-n` (samples per label) for quicker tests
- Use higher frequency for finer control (smaller domain = faster)
- Try simpler `--packing-algo` (rsa, random) vs. circlify

---

## Legacy Scripts (Backward Compatibility)

The old scripts still work but are deprecated. They delegate to `generate_in_files.py`:

```bash
# Old style (still works, shows deprecation warning)
python scripts/main/generate_dataset.py output/ --labels CL MC -n 50

# New style (recommended)
python scripts/main/generate_in_files.py output/ --mode batch --labels CL MC -n 50
```

---

## Advanced: Custom Configurations

For maximum control, use Python directly:

```python
from src.config import GeneratorConfig
from src.dataset_generator import DatasetGenerator
from pathlib import Path

# Create frequency-scaled config
config = GeneratorConfig.create_physically_perfect(
    center_freq_hz=400e6,
    angular_rocks=True,
    rock_sides=8,
    pvc_min=20.0,
    pvc_max=40.0,
)

# Generate samples
gen = DatasetGenerator(config)
files, metadata = gen.generate_samples(
    output_dir=Path("output/custom"),
    n_samples=100,
    start_id=5000,
)

print(f"Generated {len(files)} files")
```

---

## Next Steps

Once you've generated `.in` files:

1. **Run simulations:**
   ```bash
   python scripts/main/run_simulations.py output/
   ```

2. **Extract features:**
   ```bash
   python scripts/main/create_feature_dataset.py output/
   ```

3. **Train ML models:**
   ```bash
   python ml/train_model.py
   ```

See the main [README.md](../README.md) for the full pipeline.

---

## Questions?

For detailed architecture and implementation, see:
- [docs/LLM_AGENT_GUIDELINES.md](LLM_AGENT_GUIDELINES.md) — Code patterns and conventions
- [src/fouling.py](../src/fouling.py) — Fouling class definitions
- [src/config.py](../src/config.py) — Configuration system
- [src/dataset_generator.py](../src/dataset_generator.py) — Generation pipeline

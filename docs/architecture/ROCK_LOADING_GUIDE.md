# Rock Loading Feature Guide

## Overview

The rock loading feature allows you to **reuse rock configurations from existing .in files** instead of regenerating them with packing algorithms. This enables:

- **Frequency comparison studies** — same rock geometry at different frequencies
- **Antenna testing** — same rocks with different TX/RX configurations
- **Parameter studies** — same geometry with varying PVC/material properties
- **Reproducibility** — exact replication of rock configurations

## How It Works

### Normal Mode (Default)
```
GeneratorConfig
    ↓
[GranularMatrixWorker runs packing algorithm]
    ↓
[Generates ~300 rocks with gravity settling & fouling]
    ↓
[LabWorker calculates material properties]
    ↓
✓ Rocks generated + metadata calculated
```

### Rock Loading Mode
```
GeneratorConfig + rock_source_file
    ↓
[GranularMatrixWorker loads rocks from file]
    ↓
[Applies gravity settling & fouling to loaded rocks]
    ↓
[LabWorker calculates material properties]
    ↓
✓ Rocks loaded + metadata calculated (same pipeline!)
```

## Using the Rock Loading Script

### Basic Usage

Load rocks from a reference file at a different frequency:

```bash
python scripts/main/generate_from_rocks.py \
  --source reference.in \
  --freq 900e6 \
  output_900mhz.in
```

### With Parameters

Specify target PVC and moisture fraction:

```bash
python scripts/main/generate_from_rocks.py \
  --source reference.in \
  --freq 400e6 \
  --pvc 35 \
  --moisture 0.15 \
  output_400mhz_35pvc.in
```

### Full Example Workflow

```bash
# Step 1: Create reference configuration at 1.5 GHz
python scripts/main/generate_in_files.py reference.in \
  --mode single \
  --freq 1.5e9 \
  --packing-algo shang_chu \
  --pvc 30 \
  --seed 42

# Step 2: Create variants at different frequencies using the same rocks
python scripts/main/generate_from_rocks.py \
  --source reference.in \
  --freq 400e6 \
  reference_400mhz.in

python scripts/main/generate_from_rocks.py \
  --source reference.in \
  --freq 900e6 \
  reference_900mhz.in

python scripts/main/generate_from_rocks.py \
  --source reference.in \
  --freq 2.0e9 \
  reference_2000mhz.in

# Step 3: Run GPR simulations on all three files
# Compare results to isolate frequency effects with identical rock geometry
```

## API Usage (Python)

### Enable Rock Loading in Your Code

```python
from src.config import GeneratorConfig
from src.production_line import ProductionLine
from src.work_order import WorkOrder, WorkOrderSystem
from src.file_writer import GPRMaxFileWriter

# Create config with rock loading enabled
config = GeneratorConfig.create_physically_perfect(
    center_freq_hz=900e6,
    rock_source_file="/path/to/reference.in"  # Load from this file instead of packing
)

# Create work order with optional parameters
params = {'pvc': 35.0, 'moisture': 0.15}
work_order = WorkOrder.from_sampled_params(1, params)
wos = WorkOrderSystem(work_order)

# Run production line (loads rocks + calculates material properties)
line = ProductionLine(config)
checkpoint = line.run(wos)

# Save to file
writer = GPRMaxFileWriter()
output_path = writer.save_scene_checkpoint(
    checkpoint,
    output_path="output.in",
    scenario_type="Sim",
    config=config
)
```

## What Happens During Rock Loading

1. **Load phase** — Extract rock geometries from source .in file
2. **Filter phase** — Keep only rocks within ballast layer bounds
3. **Settling phase** — Apply gravity settling to loaded rocks (same as packing mode)
4. **Fouling phase** — Calculate fouling layer based on target PVC
5. **Material analysis** — LabWorker runs sieve analysis and calculates metrics:
   - Fouling Index (FI)
   - Particle size distribution
   - Rock/fouling fractions
   - Material properties

**All metadata is calculated from the loaded geometry**, ensuring material properties are accurate.

## Key Differences from Rock Extraction Tools

### Rock Loading (Current Feature)
- ✓ **Full pipeline execution** — Fouling and material analysis still run
- ✓ **Parameter flexibility** — Can change PVC, moisture, frequency
- ✓ **Metadata calculated** — All properties computed from loaded geometry
- ✓ **Single-step process** — No separate extraction/reuse step
- ✓ Built into main generation workflow

### Rock Extraction Tools (scripts/tools/)
- ✗ Simple file-to-file conversion
- ✗ Creates new .in file from rocks alone
- ✗ No material analysis (rocks only)
- ✗ Requires separate tool invocation
- ✗ Useful for legacy file modernization

**Use rock loading** for scientific studies. Use extraction tools for modernizing old files.

## Verifying Rock Loading

Check that rocks were loaded correctly:

```bash
# View loaded rock count
grep "^#cylinder:" output.in | wc -l

# Compare rock counts between source and output
echo "Source:" && grep "^#cylinder:" reference.in | wc -l
echo "Output:" && grep "^#cylinder:" output.in | wc -l

# Inspect metadata
head -50 output.in | grep "^##" | grep -E "Lab_|CONFIG_"
```

## Performance Notes

- **Packing algorithm**: ~15-20 seconds (generates ~300-400 rocks)
- **Rock loading**: ~0.5 seconds (loads rocks from file)
- **Gravity settling**: ~1-2 seconds (both modes)
- **Material analysis**: ~1-2 seconds (both modes)

**Total time saved**: ~14-18 seconds per file by skipping packing.

## Troubleshooting

### "No rocks found in ballast layer from SOURCE.in"
The source file's rocks don't fall within the current configuration's ballast layer bounds. This can happen if:
- Source file uses different layer thickness
- Domain dimensions are scaled differently

**Solution**: Check LayerStack boundaries in src/domain/coordinates.py

### "Cannot find source file"
The `--source` path is incorrect or file doesn't exist.

**Solution**: Use absolute paths or paths relative to repo root. Verify with:
```bash
ls -la /path/to/source.in
```

### Rock count mismatch between source and output
Some rocks are filtered out because they fall outside the ballast layer bounds. This is expected behavior.

**Expected range**: 60-80% of source rocks (depending on layer bounds).

## Under the Hood: Rock Loading Code

### Key Components

**src/rock_loader.py**
- `RockLoader.extract_rocks_from_file()` — Parse #cylinder/#triangle commands
- `LoadedRock` dataclass — Represents loaded rocks with x, y, z, radius
- `LoadedRock.to_rock()` — Convert to Rock objects for pipeline

**src/granular_worker.py** (Modified)
- `execute()` method checks `config.rock_source_file`
- If set: loads rocks via RockLoader
- If not set: runs packing algorithm (default)
- Both paths feed into gravity settling and fouling calculation

**src/config.py** (Extended)
- Added `rock_source_file: Optional[str] = None` parameter
- Pass to `GeneratorConfig.create_physically_perfect()`

**scripts/main/generate_from_rocks.py** (New)
- Command-line wrapper for rock loading feature
- Handles frequency, PVC, moisture parameters
- Saves with full metadata

## What's Embedded in Generated Files

Each .in file created with rock loading includes:

```
## CONFIG_center_freq_hz: 900000000.0
## CONFIG_rock_packing_algorithm: loaded
## CONFIG_angular_rocks: False
## CONFIG_rock_sides: 6
## CONFIG_packing_psd_type: uniform
## CONFIG_num_receivers: 1
## CONFIG_receiver_spacing: 0.05
```

These CONFIG_* parameters allow exact replication of the configuration.

## See Also

- [scripts/tools/ROCK_REUSE_README.md](../scripts/tools/ROCK_REUSE_README.md) — Legacy rock extraction tools
- [src/granular_worker.py](../src/granular_worker.py) — Worker that implements rock loading
- [src/rock_loader.py](../src/rock_loader.py) — Rock parsing and loading
- [IN_FILE_GENERATION.md](./IN_FILE_GENERATION.md) — Complete .in file generation guide

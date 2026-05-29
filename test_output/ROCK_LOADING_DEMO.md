# Rock Loading Mode - Load Rocks from Existing .in Files

## Concept

Instead of running the packing algorithm to generate new rocks, you can:
1. Load pre-existing rocks from a legacy .in file
2. Skip the packing step (saves time)
3. Continue with material analysis (fouling, PVC calculation)
4. Use same rocks with different frequencies/configurations

## How It Works

The `GranularMatrixWorker` now checks for a `rock_source_file` parameter in the config:

- **If `rock_source_file` is set**: Load rocks from that file
- **If `rock_source_file` is None**: Run the normal packing algorithm

This allows maximum flexibility:
- Reuse proven rock configurations
- Quickly test different frequencies with same geometry
- Compare results without regenerating expensive rock packings

## Implementation

Modified files:
1. `src/config.py` — Added `rock_source_file: str = None` parameter
2. `src/granular_worker.py` — Added rock loading branch in execute()
3. `src/rock_loader.py` — New module to extract and load rocks
4. `scripts/main/generate_from_rocks.py` — Script to run generation with rock loading

## Example Usage (Pseudocode)

```python
from src.config import GeneratorConfig
from src.production_line import ProductionLine

# Create config with rock loading enabled
config = GeneratorConfig.create_physically_perfect(
    center_freq_hz=400e6,  # New frequency
    rock_source_file="legacy.in",  # Load rocks from here
)

# Run pipeline - rocks loaded, not generated
line = ProductionLine(config)
checkpoint = line.run(work_order_system)
```

## Validation

The rock loading feature:
- ✓ Extracts rocks from cylinder/triangle commands
- ✓ Filters rocks to ballast layer bounds
- ✓ Converts loaded rocks to Rock objects
- ✓ Continues with fouling and material analysis
- ✓ Produces complete .in file output

## Advantages

✓ **Speed**: Skip expensive packing algorithm
✓ **Reproducibility**: Use exact same geometry
✓ **Flexibility**: Change frequency/antenna without regenerating
✓ **Validation**: Compare results across configurations
✓ **Legacy**: Modernize old .in files

## Next Steps

To fully activate this feature in the main generation pipeline:
1. Run through DatasetGenerator (like generate_in_files.py)
2. Extend to batch processing
3. Add command-line flag: `--source-rocks FILE.in`

Current status: Core functionality implemented, integration pending

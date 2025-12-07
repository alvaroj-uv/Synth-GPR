# Script CLI Arguments Reference

Quick reference for correct command-line arguments for each script.

## Main Scripts

### generate_dataset.py
```batch
python scripts/main/generate_dataset.py <output_dir> --labels CL MF -n 10 --start_id 0
```
**Arguments:**
- `output_dir` - Output directory (positional)
- `--labels` - Fouling labels (space-separated)
- `-n, --samples` - Samples per label
- `--start_id` - Starting sample ID
- `--moisture_max` - Maximum moisture (optional)

---

### run_simulations.py
```batch
python scripts/main/run_simulations.py <input_folder> -j 4
```
**Arguments:**
- `input_folder` - Folder with .in files (positional)
- `-j, --jobs` - Number of parallel jobs (default: 4)
- `--gpu` - GPU device IDs (optional)

```
**Arguments:**
- `input_dir` - Input directory (positional)
- `output_csv` - Output CSV (positional)
- `--config` - Config file (optional)

---

## Visualization Scripts

### visualize_gprmax_blueprint.py
```batch
python scripts/tools/visualization/visualize_gprmax_blueprint.py <input_file> -o <output_file> --no-show
```
**Arguments:**
- `input_file` - .in file to visualize (positional)
- `-o, --output` - Output image file
- `--no-show` - Don't display plot
- `--dpi` - Image resolution (default: 150)

---

## Data Management Scripts

### validate_dataset.py
```batch
python scripts/tools/data_management/validate_dataset.py <dataset_dir>
```
**Arguments:**
- `dataset_dir` - Dataset directory (positional)

---

### merge_datasets.py
```batch
python scripts/tools/data_management/merge_datasets.py <input_files> -o <output_file>
```
**Arguments:**
- `input_files` - Input CSV files (positional, multiple)
- `-o, --output` - Output merged CSV

---

### update_hdf5_titles.py
```batch
python scripts/tools/data_management/update_hdf5_titles.py <csv_file>
```
**Arguments:**
- `csv_file` - CSV mapping file (positional)

---

## Common Mistakes

❌ **WRONG**: `--num-processes 4`  
✓ **CORRECT**: `-j 4`

❌ **WRONG**: `--output-dir path`  
✓ **CORRECT**: `path` (positional argument)

❌ **WRONG**: `--input path`  
✓ **CORRECT**: `path` (positional argument)

---

## Quick Test Commands

```batch
# Generate 2 samples
python scripts/main/generate_dataset.py d:/Data/Test --labels CL -n 2 --start_id 0

# Run simulations (4 parallel)
python scripts/main/run_simulations.py d:/Data/Test -j 4

# Create blueprint
python scripts/tools/visualization/visualize_gprmax_blueprint.py d:/Data/Test/s_00000.in -o blueprint.png --no-show

# Extract features
python scripts/main/batch_extract_features.py d:/Data/Test features.csv
```

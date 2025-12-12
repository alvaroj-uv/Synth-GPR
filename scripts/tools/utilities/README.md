# Utility Scripts

This directory contains helper utility scripts for maintenance and fixes.

## Scripts

### `create_run_scripts.sh`
**Purpose**: Auto-generates helper scripts for pipeline execution in output directories.

**Usage**:
```bash
./create_run_scripts.sh <output_directory>
```

**Example**:
```bash
./create_run_scripts.sh output/pipeline_run/20251212_093000
```

**What it creates**:
- `run_gprmax.sh` - Runs gprMax simulations
- `extract_features.sh` - Extracts features from .out files  
- `create_blueprints.sh` - Creates visualization blueprints
- `README.txt` - Usage instructions

---

### `fix_metadata.py`
**Purpose**: Adds FI_Class column to metadata.csv based on PVC values using Selig & Waters classification.

**Usage**:
```bash
python fix_metadata.py <path/to/metadata.csv>
```

**Example**:
```bash
python fix_metadata.py output/dataset_001/metadata.csv
```

**What it does**:
- Reads PVC column from metadata
- Calculates FI_Class (C, MC, MF, F, HF)
- Adds FI_Class column to CSV
- Overwrites original file

---

### `fix_out_names.sh`
**Purpose**: Fixes gprMax output file naming issues when using `-n` parallel flag.

**Background**: gprMax with `-n` flag sometimes creates files like `s_00011.out` instead of `s_0001.out` (duplicate last digit).

**Usage**:
```bash
cd <directory_with_out_files>
bash ../../scripts/tools/utilities/fix_out_names.sh
```

**What it does**:
- Detects files with duplicate digit pattern
- Renames to correct format
- Reports number of files fixed

---

## When to Use These Scripts

| Script | When to Use |
|--------|-------------|
| `create_run_scripts.sh` | After generating .in files, to create convenience scripts for the output directory |
| `fix_metadata.py` | When metadata.csv is missing FI_Class column or needs recalculation |
| `fix_out_names.sh` | After running gprMax with `-n` parallel flag and encountering naming issues |

# GPR Data Pipeline Scripts

This directory contains shell scripts to run the complete GPR (Ground Penetrating Radar) data generation and analysis pipeline.

## Quick Start

### Option 1: Run Complete Pipeline (All Steps)

Run everything in one command:

```bash
./pipeline.sh
```

With custom options:

```bash
./pipeline.sh -n 10 -p 4 -o my_dataset
```

### Option 2: Run Individual Steps

Run each step separately for more control:

```bash
# Step 1: Generate .in files
./1_generate_inputs.sh -n 10 -o output/my_dataset

# Step 2: Run gprMax simulations (user runs this manually)
./2_run_gprmax.sh -i output/my_dataset/20241210_141500 -p 4

# Step 3: Extract features
./3_extract_features.sh -i output/my_dataset/20241210_141500

# Step 4: Create blueprints
./4_create_blueprints.sh -i output/my_dataset/20241210_141500
```

## Pipeline Steps

### 1. Generate Input Files (`1_generate_inputs.sh`)

Creates `.in` files (gprMax input files) with varying ballast fouling levels.

**Options:**
- `-n, --num-samples N` - Number of samples per class (default: 2)
- `-o, --output DIR` - Output directory (default: output/generated)

**Output:**
- `.in` files in timestamped directory
- `metadata.csv` with sample information

**Example:**
```bash
./1_generate_inputs.sh -n 20 -o output/dataset_2024
```

### 2. Run Simulations (`2_run_gprmax.sh`)

Runs gprMax electromagnetic simulations on all `.in` files.

**Options:**
- `-i, --input DIR` - Input directory with .in files (required)
- `-p, --parallel N` - Number of parallel processes (default: 1)
- `-f, --force` - Force re-run even if .out files exist

**Output:**
- `.out` files (HDF5 format) with electromagnetic field data

**Example:**
```bash
./2_run_gprmax.sh -i output/dataset_2024/20241210_141500 -p 8
```

**Note:** This step can take significant time depending on:
- Number of samples
- Domain size
- Time window
- Number of parallel processes

### 3. Extract Features (`3_extract_features.sh`)

Extracts signal features from `.out` files for machine learning.

**Options:**
- `-i, --input DIR` - Input directory with .out files (required)
- `-o, --output FILE` - Output CSV file (default: `<input_dir>/features.csv`)

**Output:**
- `features.csv` with extracted features and labels

**Features extracted:**
- Statistical features (mean, std, skewness, kurtosis)
- Hilbert transform features (envelope, instantaneous frequency)
- FFT features (dominant frequency, spectral centroid)
- Wavelet features (CWT coefficients)
- Time-domain features (zero crossings, peak count)

**Example:**
```bash
./3_extract_features.sh -i output/dataset_2024/20241210_141500
```

### 4. Create Blueprints (`4_create_blueprints.sh`)

Creates visual blueprints showing geometry and signal analysis.

**Options:**
- `-i, --input DIR` - Input directory with .in files (required)
- `-f, --force` - Force re-creation even if blueprints exist
- `-s, --show` - Show blueprints after creation

**Output:**
- `*_blueprint.png` files with visualizations

**Visualizations include:**
- Geometry cross-section (materials, layers, antennas)
- A-scan signals (if .out file available)
- Analytic signal overlay
- Hilbert envelope
- CWT scalogram
- Spectrogram
- Hodogram

**Example:**
```bash
./4_create_blueprints.sh -i output/dataset_2024/20241210_141500
```

## Complete Pipeline Script

The `pipeline.sh` script runs all 4 steps automatically:

**Options:**
- `-n, --num-samples N` - Number of samples per class (default: 2)
- `-o, --output DIR` - Output directory (default: output/pipeline_run)
- `-s, --start-id ID` - Starting sample ID (default: 0)
- `-p, --parallel N` - Number of parallel processes for gprMax (default: 1)

**Example:**
```bash
# Quick test with 2 samples per class
./pipeline.sh

# Production run with 100 samples per class, 8 parallel processes
./pipeline.sh -n 100 -p 8 -o output/production_dataset
```

## Output Structure

After running the pipeline, your output directory will contain:

```
output/
└── pipeline_run/
    └── 20241210_141500/          # Timestamped run directory
        ├── metadata.csv           # Sample metadata
        ├── features.csv           # Extracted features
        ├── pipeline.log           # Generation log
        ├── s0000.in               # Input files
        ├── s0000.out              # Simulation outputs
        ├── s0000_blueprint.png    # Visualizations
        ├── s0001.in
        ├── s0001.out
        ├── s0001_blueprint.png
        └── ...
```

## Fouling Classes

The pipeline generates samples across 5 fouling classes based on Selig & Waters classification:

| Class | FI Range (%) | Description |
|-------|--------------|-------------|
| C     | 0-1          | Clean       |
| MC    | 1-10         | Moderately Clean |
| MF    | 10-20        | Moderately Fouled |
| F     | 20-40        | Fouled |
| HF    | 40-50        | Highly Fouled |

## Tips

1. **Start small**: Test with `-n 2` first to verify everything works
2. **Use parallel processing**: Set `-p` to number of CPU cores for faster simulations
3. **Monitor disk space**: Each .out file can be 10-50 MB
4. **Check logs**: Review `pipeline.log` in output directory for details
5. **Resume failed runs**: Scripts skip existing files by default

## Troubleshooting

**No .out files created:**
- Check if gprMax is installed: `python -m gprMax --help`
- Check for errors in individual .in files
- Try running one file manually: `python -m gprMax output/path/s0000.in`

**Feature extraction fails:**
- Ensure .out files exist and are not corrupted
- Check that metadata.csv exists in the input directory
- Verify Python dependencies are installed

**Blueprints not created:**
- Check that visualization script exists: `scripts/tools/visualization/visualize_gprmax_blueprint.py`
- Ensure matplotlib is installed
- Try creating one manually: `python scripts/tools/visualization/visualize_gprmax_blueprint.py input.in`

## Next Steps

After running the pipeline:

1. **Review the data:**
   ```bash
   # View features
   head -20 output/pipeline_run/20241210_141500/features.csv
   
   # View blueprints
   open output/pipeline_run/20241210_141500/*_blueprint.png
   ```

2. **Train ML model:**
   ```bash
   python ml/train_model.py --input output/pipeline_run/20241210_141500/features.csv
   ```

3. **Analyze results:**
   - Feature importance plots
   - Confusion matrices
   - Classification reports

## Requirements

- Python 3.7+
- gprMax
- numpy
- pandas
- matplotlib
- scipy
- h5py
- tqdm

Install dependencies:
```bash
pip install -r requirements.txt
```

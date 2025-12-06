# Synth-GPR Scripts

This directory contains the executable scripts for the Synthetic GPR pipeline.

## Directory Structure

### `main/` - Core Pipeline Scripts
Primary scripts for generating data, running simulations, and extracting features.
- **`generate_dataset.py`**: Unified generator for synthetic GPR data. Supports single class, stratified, and custom fouling ranges.
- **`run_simulations.py`**: Batch runner for executing `gprMax` on multiple `.in` files.
- **`create_feature_dataset.py`**: The main extraction tool; converts `.out` files to a features CSV.
- **`consolidate_dataset.py`**: Merges and renames datasets from multiple sources into a canonical format.
- **`batch_extract_features.py`**: (Legacy) Lower-level batch extractor using OS-based iteration.

### `tools/` - Utilities & Helpers
Helper tools for visualization, validation, and asset generation.
- **`visualize_gprmax_blueprint.py`**: Generates high-quality blueprints (PNG) of `.in` file geometry.
- **`generate_master_pattern.py`**: Generates the RSA (Random Sequential Adsorption) master circle patterns used for ballast.
- **`validate_dataset.py`**: Checks a dataset folder for consistency (missing inputs/outputs).
- **`merge_datasets.py`**: Merges multiple feature CSV files into one.
- **`update_hdf5_titles.py`**: Updates internal HDF5 Title attributes based on a metadata CSV.
- **`read_gprmax_output.py`**: Helper functions for reading gprMax HDF5 outputs.
- **`analyze_selected_pdfs.py`**: Text extraction tool for literature review.
- **`test_data_generator.py`**: Quick test for the generator pipeline.

## Usage

**Always run scripts from the project root directory** (`d:\Codigo\Synth-GPR`) to ensure Python can resolve the `src` module imports.

### Examples

**Generating Data:**
```bash
# Generate 50 samples of Clean(CL), Moderately Clean(MC), etc.
python scripts/main/generate_dataset.py d:/Codigo/Synth-Data/Batch1 --labels CL MC MF F HF -n 50
```

**Running Simulations:**
```bash
python scripts/main/run_simulations.py d:/Codigo/Synth-Data/Batch1 --gpu 0
```

**Extracting Features:**
```bash
python scripts/main/create_feature_dataset.py d:/Codigo/Synth-Data/Batch1 -o features_batch1.csv
```

**Visualizing Geometry:**
```bash
python scripts/tools/visualize_gprmax_blueprint.py d:/Codigo/Synth-Data/Batch1/s_00000.in
```

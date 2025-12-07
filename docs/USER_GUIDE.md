# Synth-GPR User Guide

This guide provides detailed instructions on using the Synth-GPR framework for generating synthetic Ground Penetrating Radar (GPR) data, running simulations with gprMax, and extracting features for Machine Learning analysis.

## 1. Environment Setup

The project relies on a specific Conda environment (usually named `gprMax`) to handle the electromagnetic simulation dependencies.

### Activating the Environment
Always activate the environment before running scripts:
```bash
conda activate gprMax
```
Or run commands directly using `conda run`:
```bash
conda run -n gprMax python scripts/main/generate_dataset.py ...
```

For a step-by-step checklist to ensure your setup is working, see **[VERIFICATION.md](VERIFICATION.md)**.


## 2. Workflow Overview

The standard pipeline consists of four main stages:

1.  **Generation**: Create `.in` geometry files representing different ballast fouling scenarios.
2.  **Simulation**: Execute `gprMax` on these files to produce `.out` (HDF5) data.
3.  **Extraction**: Process the raw A-Scans to calculate statistical and frequency-domain features.
4.  **Analysis/ML**: Train and test classifiers on the extracted features.

---

## 3. Step 1: Synthetic Data Generation

Use `scripts/main/generate_dataset.py` to create gprMax input files.

**Basic Usage:**
```bash
# Generate 50 'Clean' (CL) samples
python scripts/main/generate_dataset.py output_folder --labels CL -n 50
```

**Advanced Usage (Granular Mode):**
To use the high-fidelity granular physics model (random aggregate packing):
```bash
# Enable granular mode in config or ensure config.ini has granular_mode=True
python scripts/main/generate_dataset.py output_folder --labels CL MC -n 25 --granular
```

**Arguments:**
*   `output_dir`: Target folder for `.in` files.
*   `--labels`: List of classes to generate (`CL`, `MC`, `MF`, `F`, `HF`).
*   `-n`, `--n_samples`: Number of samples per label.
*   `--start_id`: Starting integer ID for filenames (e.g., `s_0100`).
*   `--config`: Path to custom `.ini` configuration (default: `simulation_config.ini`).

---

## 4. Step 2: Running Simulations

Once `.in` files are generated, run the electromagnetic simulation.

**Single File:**
```bash
python -m gprMax output_folder/s_0100.in
```

**Batch Execution:**
Use the `run_simulations.py` script to process an entire directory.
```bash
python scripts/main/run_simulations.py output_folder --gpu 0
```
*   `--gpu`: Specify GPU ID (if CUDA is available) to speed up FDTD solving.

---

## 5. Step 3: Feature Extraction

Convert raw HDF5 outputs into a CSV dataset suitable for Machine Learning.

**Usage:**
```bash
python scripts/main/create_feature_dataset.py output_folder -o features_batch1.csv
```
This script will:
1.  Read every `.out` file in the folder.
2.  Extract time-domain, frequency-domain (FFT/STFT), and statistical features.
3.  Save the result as a pandas DataFrame in CSV format.

For a complete list of extracted statistics (Time-Domain, Frequency, STFT, etc.), see the **[Feature Extraction Reference](FEATURE_EXTRACTION.md)**.

---

## 6. Tool Reference

The `scripts/tools/` directory contains helper utilities categorised by function:

### Visualization (`scripts/tools/visualization/`)
*   **`visualize_gprmax_blueprint.py`**: Creates a PNG image of the simulation geometry.
    ```bash
    python scripts/tools/visualization/visualize_gprmax_blueprint.py sample.in -o blueprint.png
    ```
    See the **[Blueprint Interpretation Guide](BLUEPRINT_GUIDE.md)** for details.
*   **`read_gprmax_output.py`**: Helper library for inspecting `.out` files.

### Data Management (`scripts/tools/data_management/`)
*   **`merge_datasets.py`**: Combines multiple feature CSVs.
    ```bash
    python scripts/tools/data_management/merge_datasets.py batch1.csv batch2.csv -o combined.csv
    ```
*   **`validate_dataset.py`**: Checks a dataset folder for consistency (missing inputs/outputs).
    ```bash
    python scripts/tools/data_management/validate_dataset.py output_folder
    ```
*   **`update_hdf5_titles.py`**: Fixes internal metadata if needed.

### Generation (`scripts/tools/generation/`)
*   **`generate_master_pattern.py`**: Generates the "Master Pattern" of rocks using Random Sequential Adsorption. Used by the granular generator to speed up aggregate placement.

### Research (`scripts/tools/research/`)
*   **`analyze_selected_pdfs.py`**: Utility to extracting text from specific academic papers for review.

---

## 7. Configuration (`simulation_config.ini`)

The behavior of the generator is controlled by `simulation_config.ini`. Key sections:

*   **[Geometry]**: Domain size (`domain_x`, `domain_y`, `domain_z`) and spatial resolution (`dx`, `dy`, `dz`).
*   **[Materials]**: Dielectric properties (`eps`, `sigma`) for ballast, fouling, subgrade, etc.
*   **[Granular]**: Parameters for the physics-based aggregate generator (radius ranges, filling strategies).

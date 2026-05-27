# Synth-GPR

Synth-GPR is a project designed for processing, simulating, and analyzing Ground Penetrating Radar (GPR) data, specifically focused on railway ballast condition assessment (fouling). It integrates **gprMax** for electromagnetic simulations with Machine Learning (Random Forest, XGBoost) pipelines for fouling classification.

## Project Structure

The codebase is organized as follows:

- **`ml/`**: Machine Learning pipelines.
  - `train_classifier.ipynb`: Jupyter notebook for training classifiers.
  - `train_model.py`: Script to train ML models.

- **`scripts/`**: Utility scripts for data management, visualization, and pipeline execution.
  - `main/`: Core pipeline scripts including `generate_dataset.py`, `run_simulations.py`, `create_feature_dataset.py`.
  - `tools/`: Helper utilities organized by category (data_management, visualization, generation, tests, research).
  - Shell scripts: `1_generate_inputs.sh`, `2_run_gprmax.sh`, `3_extract_features.sh`, `4_create_blueprints.sh` for automated pipeline execution.

- **`src/`**: Core libraries and modules.
  - Core modules: `config.py`, `constants.py`, `data_loader.py`, `dataset_generator.py`, `feature_extraction.py`, `physics.py`, etc.
  - Domain logic: `domain/` and `patterns/` subdirectories.
  - Workers and production: `worker.py`, `workers.py`, `production_line.py`, `work_order.py`.
  - Repositories and data management: `repositories/`, `warehouses.py`, `warehouse_keeper.py`.
  - Visualization: `visualization/` subdirectory.

- **`output/`**: Generated GPR data and simulation results.
  - `single_test/`: Individual test runs and experiments.
  - `test/`: Batch test outputs and validation data.

- **`output_test/`**: Test examples and sample outputs for documentation.

- **`scratch/`**: Temporary files and experimental code.

- **`docs/`**: Detailed documentation including user guides, technical reports, and troubleshooting.

- **`.claude/`**: AI-generated temporary files and analysis artifacts.

## Output File Organization

For consistent file placement across the project, see:
- **[Output File Placement Rules](docs/OUTPUT_FILE_PLACEMENT_RULES.md)**: Comprehensive guidelines
- **[Quick Reference](docs/OUTPUT_PLACEMENT_QUICKREF.md)**: Fast lookup guide

**Key Locations:**
- Generated GPR data (`.in`, `.out`): `output/{experiment_name}/`
- Feature datasets: Same directory as source data
- Visualizations: Same directory as input files
- ML models: `ml/models/`
- Reports: `docs/reports/`
- Temporary files: `scratch/`

## For AI/LLM Code Agents

If you're an AI assistant working on this codebase, please follow:
- **[LLM Agent Guidelines](docs/LLM_AGENT_GUIDELINES.md)**: Coding standards, file placement, and project conventions
- Use the `scripts/tools/output_resolver.py` utility for consistent output file placement

## Getting Started

For full detailed usage instructions, please refer to the **[User Guide](docs/USER_GUIDE.md)**.

### Prerequisites

Ensure you have Python 3.8+ installed. Key dependencies include:
- `numpy` (for numerical computations)
- `pandas` (for data manipulation)
- `matplotlib` (for plotting)
- `scikit-learn` (for machine learning)
- `scipy` (for scientific computing)
- `seaborn` (for statistical visualization)
- `h5py` (for reading gprMax `.out` files)
- `tqdm` (for progress bars)
- `pypdf` (for PDF processing)

Testing dependencies:
- `pytest` (for running tests)
- `hypothesis` (for property-based testing)
- `pytest-benchmark` (for performance testing)
- `freezegun` (for time mocking in tests)

### Key Workflows

#### 1. Generate Synthetic GPR Data (`.in` files)

The unified generator supports batch and single-file modes with full frequency and geometry flexibility:

**Batch generation** — 50 files per fouling class (1.5 GHz):
```bash
python scripts/main/generate_in_files.py output/ --mode batch --labels CL MC MF F HF -n 50
```

**Batch generation** — 1000 files per class, 400 MHz, angular rocks:
```bash
python scripts/main/generate_in_files.py output/ --mode batch --labels CL MC MF F HF \
    -n 1000 --freq 400e6 --angular --packing-algo circlify
```

**Single file** — Custom parameters, with PNG visualization:
```bash
python scripts/main/generate_in_files.py test.in --mode single --pvc 25 --moisture 0.10 --render
```

**Single file** — 400 MHz, octagonal rocks:
```bash
python scripts/main/generate_in_files.py out.in --mode single --freq 400e6 --pvc 50 \
    --angular --sides 8 --render
```

**Replicate an existing file** — Extract config and regenerate with same geometry:
```bash
python scripts/main/generate_in_files.py replicated.in --mode replicate --source original.in
```

**Note on reproducibility:** Each generated `.in` file embeds its configuration parameters as `CONFIG_*` comments in the header. This makes files self-documenting and enables exact replication using the `--mode replicate` command. For full documentation on generation options and config persistence, see [docs/IN_FILE_GENERATION.md](docs/IN_FILE_GENERATION.md).

#### 2. Running Simulations
To run gprMax simulations on generated input files:
```bash
python scripts/main/run_simulations.py input_folder
```

#### 3. Feature Extraction
To extract features from GPR simulation outputs (`.out` files):
```bash
python scripts/main/extract_features.py input_folder output.csv
```

#### 4. Visualization
To visualize a gprMax input file (`.in`):
```bash
python scripts/tools/visualization/visualize_gprmax_blueprint.py path/to/input.in
```

#### 5. ML Training
To train a classifier on extracted features:
```bash
python ml/train_model.py
```

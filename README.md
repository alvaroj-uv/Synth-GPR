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

- **`tests/`**: Comprehensive test suite with pytest configuration.

- **`docs/`**: Detailed documentation including user guides, technical reports, and troubleshooting.

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

#### 1. Data Generation
To generate synthetic GPR input files (`.in`):
```bash
python scripts/main/generate_dataset.py output_folder --labels CL MC MF F HF -n 50
```

#### 2. Running Simulations
To run gprMax simulations on generated input files:
```bash
python scripts/main/run_simulations.py input_folder
```

#### 3. Feature Extraction
To extract features from GPR simulation outputs (`.out` files):
```bash
python scripts/main/create_feature_dataset.py input_folder
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

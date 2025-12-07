# Synth-GPR

Synth-GPR is a project designed for processing, simulating, and analyzing Ground Penetrating Radar (GPR) data, specifically focused on railway ballast condition assessment (fouling). It integrates **gprMax** for electromagnetic simulations with Machine Learning (Random Forest, XGBoost) pipelines for fouling classification.

## Project Structure

The codebase is organized as follows:

- **`ml/`**: Machine Learning pipelines.
  - `rf_prediction_pipeline.py`: Main script for loading data, running predictions using a trained Random Forest/XGBoost model, and comparing with Pandoscope (Ground Truth) data.
  - `train_and_test_rf.py`: Script to train and evaluate the Random Forest model.

- **`scripts/`**: Utility scripts for data management and visualization.
  - `visualize_gprmax_blueprint.py`: Visualizes `.in` input files for gprMax, showing geometry and layers.
  - `create_feature_dataset.py`: Extracts features from GPR data to build datasets for ML.
  - `update_hdf5_titles.py`: Utilities to manage HDF5 file metadata.

- **`src/`**: Core libraries and modules.
  - `feature_extraction.py`: Functions for extracting time-domain and frequency-domain features from GPR traces.
  - `synthetic_data_generator.py`: Generators for synthetic fouling scenarios.
  - `data_loader.py`: Utilities for loading `.out` and `.in` files.

- **`notebooks/`**: Jupyter notebooks for exploratory data analysis (EDA) and prototyping.

## Getting Started

For full detailed usage instructions, please refer to the **[User Guide](docs/USER_GUIDE.md)**.

### Prerequisites

Ensure you have Python 3.8+ installed. Key dependencies include:
- `numpy`
- `pandas`
- `matplotlib`
- `scikit-learn`
- `xgboost`
- `h5py` (for reading gprMax `.out` files)

### Key Workflows

#### 1. Visualization
To visualize a gprMax input file (`.in`):
```bash
python scripts/visualize_gprmax_blueprint.py path/to/input.in
```

#### 2. ML Prediction Pipeline
To run the prediction pipeline (comparative analysis between Model and Ground Truth):
```bash
python ml/rf_prediction_pipeline.py
```
*Note: Ensure paths to your datasets and models are correctly configured in the script.*

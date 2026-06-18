# Synth-GPR: Synthetic Ground Penetrating Radar Dataset & ML Pipeline

[![Python 3.8+](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Code style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

## Overview

**Synth-GPR** is a comprehensive framework for generating synthetic Ground Penetrating Radar (GPR) datasets and training machine learning classifiers to assess railway ballast fouling conditions. The project combines electromagnetic simulations (via **gprMax**) with advanced signal processing and machine learning to create production-ready fouling classification models.

### Key Innovation: Waveform-Only Features

The core innovation is **predicting fouling class from GPR Ez waveform features alone** — without relying on metadata (material composition, density, moisture). This is critical because:
- Metadata is unavailable in real-world GPR field deployments
- Waveform features (572-dimensional: time-domain, Hilbert, frequency, STFT, grid) are extracted directly from the received signal
- The goal is a classifier that works on field data where only the A-scan waveform is available

**Baseline performance**: 70.83% balanced accuracy on 30,000 samples using Random Forest with 572 waveform features.

---

## What This Project Does

### 1. **Synthetic Data Generation**
- Generates realistic GPR `.in` geometry files with configurable:
  - Fouling levels (5 classes: Clean → Highly Fouled)
  - Rock packing algorithms (12 variants, from fast to high-quality)
  - Antenna configurations (bistatic, frequency-selectable)
  - Material properties (permittivity, conductivity, moisture)

### 2. **Electromagnetic Simulation**
- Runs gprMax FDTD simulations on generated geometries
- Produces Ez (vertical electric field) time-domain signals
- Uses 400 MHz Ricker wavelet (production standard) or custom frequencies

### 3. **Feature Extraction**
- Extracts **572-dimensional** feature vectors from raw A-scan waveforms:
  - **Time-domain statistics**: mean, RMS, std, skewness, kurtosis, peak values, area
  - **Hilbert envelope**: energy envelope capturing pulse shape
  - **Frequency domain**: FFT-based features (peak, bandwidth, entropy, spectral flatness)
  - **Time-frequency (STFT)**: energy in three depth bands (low/mid/high)
  - **Spatial-temporal grid**: 16×10 discretized grid with 3 channels per point
  - **Slice statistics**: 14 temporal segments with mean/std per slice

### 4. **Machine Learning**
- Trains Random Forest and XGBoost classifiers for multi-class fouling prediction
- Supports class balancing, hyperparameter tuning, and cross-validation
- Includes model evaluation, feature importance analysis, and confusion matrices

### 5. **Visualization**
- Generates high-resolution blueprint diagrams of simulated geometries
- A-scan visualization with physical GPR signal interpretation
- 6-panel analysis plots (raw signal, Hilbert envelope, FFT, STFT, grid overlay, physics)

---

## Project Structure

```
Synth-GPR/
├── src/                           # Core library modules
│   ├── config.py                  # Configuration management
│   ├── constants.py               # Project constants
│   ├── feature_extraction.py      # Signal feature extraction
│   ├── physics.py                 # Electromagnetic and material calculations
│   ├── rock_packing.py            # 12 rock packing algorithms
│   ├── rock_loader.py             # Load rocks from existing files
│   ├── production_line.py          # Main generation pipeline
│   ├── lab_worker.py              # Fouling index & metadata calculation
│   ├── gpr_commands.py            # gprMax command generation
│   ├── data_loader.py             # Dataset I/O
│   ├── file_reader.py, file_writer.py  # File utilities
│   ├── visualization/             # Plotting & visualization utilities
│   ├── repositories/              # Data access layer
│   └── domain/                    # Domain models (Layer, Fouling, etc.)
│
├── scripts/                       # Executable scripts
│   ├── pipeline/                  # Core pipeline scripts
│   │   ├── generate_gprmax_scenes.py   # Generate .in geometry files
│   │   ├── run_simulations.py     # Execute gprMax simulations
│   │   ├── extract_features.py    # Extract features from .out files
│   │   ├── build_parquet.py       # Consolidate features into Parquet
│   │   └── train_rf*.py           # Train Random Forest classifiers
│   ├── analysis/                  # Validation & sim-to-real studies
│   ├── experiments/               # Research experiments (transient)
│   ├── tools/                     # Maintenance & debugging utilities
│   └── visualization/             # Plotting & rendering scripts
│
├── docs/                          # Comprehensive documentation
│   ├── setup/                     # Installation & configuration
│   │   ├── README.md              # Setup overview
│   │   ├── USER_GUIDE.md          # Detailed user guide
│   │   └── TROUBLESHOOTING.md     # Common issues
│   ├── architecture/              # Technical architecture
│   │   ├── GENERATION_PROCESS.md  # Full generation pipeline
│   │   ├── DATASET_STRUCTURE.md   # Data organization
│   │   └── SINGLE_SOURCE_OF_TRUTH.md  # Design principles
│   ├── algorithms/                # Algorithm documentation
│   │   └── PACKING_ALGORITHMS.md  # 12 packing variants
│   ├── coordinate-systems/        # Coordinate system definitions
│   ├── research/                  # Research papers & analyses
│   ├── operations/                # Operational procedures
│   ├── reports/                   # CLI references, evaluation reports
│   └── archived/                  # Historical documentation
│
├── tests/                         # Test suite (pytest, flat layout)
│
├── output/                        # Generated simulation outputs
│
├── requirements.txt               # Python dependencies
├── .gitignore                     # Git exclusions
└── .claude/CLAUDE.md              # Development guidelines for AI agents

```

---

## Installation

### Prerequisites

- **Python 3.8+** (tested on 3.8–3.12)
- **gprMax** (for electromagnetic simulations; see [setup guide](docs/setup/README.md))
- **pip** or **conda** for package management

### Setup

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd Synth-GPR
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Verify gprMax installation:**
   Ensure gprMax is installed and accessible from your PATH. See [setup guide](docs/setup/README.md) for detailed instructions.

5. **Run tests to verify setup:**
   ```bash
   pytest tests/ -v
   ```

---

## Quick Start

### 1. Generate Synthetic GPR Geometries

Generate 50 samples per fouling class with angular rocks:
```bash
python scripts/pipeline/generate_gprmax_scenes.py output/ \
  --mode batch \
  --labels CL MC MF F HF \
  -n 50 \
  --freq 400e6 \
  --angular
```

**Output:** `.in` files in `output/` directory with embedded configuration metadata.

### 2. Run Electromagnetic Simulations

Execute gprMax FDTD simulations (requires gprMax installed):
```bash
python scripts/pipeline/run_simulations.py output/ -j 4
```

**Output:** `.out` HDF5 files with Ez waveform recordings.

### 3. Extract Features

Extract 572-dimensional feature vectors from simulation outputs:
```bash
python scripts/pipeline/extract_features.py output/ --output features.csv
```

**Output:** `features.csv` with 612 columns (572 features + 40 metadata columns).

### 4. Train ML Classifier

Train a Random Forest classifier on waveform features only (production approach):
```bash
python scripts/pipeline/train_rf_waveform_only.py
```

### 5. Visualize Results

Render diagrams of simulated geometries and A-scans:
```bash
python scripts/visualization/unified_visualizer.py output/s_00000.in
```

---

## Key Features

### Rock Packing Algorithms

The framework provides **12 configurable packing algorithms** with different speed/quality tradeoffs:

| Algorithm | Speed | Quality | Use Case |
|-----------|-------|---------|----------|
| **RSA** (Random Sequential Addition) | <1s | Low | Fast prototyping |
| **Grid** | <1s | Low | Regular patterns |
| **Random** | <1s | Low | Quick tests |
| **Circlify** | 1-5s | Medium | Testing |
| **Simulated Annealing** | 5-10s | Medium | Balanced |
| **PoissonDisk** | 2-3s | Medium | Spatial distribution |
| **ShangChu** (Recommended) | 15-20s | High | Production datasets |
| **HybridShang** | 15-20s | High+ | Enhanced quality |
| **Growth**, **GrowthBalanced**, **SimplePacking**, **Gravity** | Variable | Variable | Specialized uses |

**Recommendation:** Use `--angular` with Shang-Chu for production datasets. Use Grid or RSA for rapid prototyping.

### Feature Groups

The extraction pipeline produces features organized into logical groups:

| Group | Count | Description |
|-------|-------|-------------|
| Time-domain stats | ~25 | Basic signal statistics |
| Hilbert envelope | ~25 | Energy envelope metrics |
| FFT features | 8 | Frequency domain analysis |
| STFT features | 7 | Time-frequency energy in depth bands |
| Slice statistics | 28 | 14 temporal segments × 2 metrics |
| Grid features | 480 | 16×10 spatial-temporal grid × 3 channels |
| **Total waveform features** | **572** | All extracted from raw A-scan |
| Metadata | ~40 | PVC, moisture, density, FI, layer coordinates |

### Fouling Classification

Five fouling classes defined by **Fouling Index (FI)** and **Percentage Void Contamination (PVC)**:

| Class | Label | FI Range | Description |
|-------|-------|----------|-------------|
| **C** | Clean | 0.0–0.2 | No fouling material in voids |
| **MC** | Moderately Clean | 0.2–0.4 | Minimal fouling |
| **MF** | Mixed Fouling | 0.4–0.6 | Partial void contamination |
| **F** | Fouled | 0.6–0.8 | Significant fouling |
| **HF** | Highly Fouled | 0.8–1.0 | Voids mostly filled with fines |

---

## Data Pipeline

```
┌──────────────────┐
│ Generate .in     │  Rock packing algorithm, material properties,
│ geometry files   │  antenna config → configurable parameters
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ gprMax FDTD      │  400 MHz Ricker wavelet, 20 ns time window,
│ simulation       │  10 cell PML boundary → Hz time-domain waveform
│ (GPU)            │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Extract features │  Time, Hilbert, FFT, STFT, grid
│ from .out file   │  → 572-dimensional feature vector
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ ML training      │  RF, XGBoost, SVM
│ (sklearn)        │  → fouling class prediction model
└──────────────────┘
```

---

## Command Reference

### Main Scripts

**Generate Synthetic Geometries:**
```bash
python scripts/pipeline/generate_gprmax_scenes.py <output_file|output_dir> \
  --mode batch|single|layers \
  --labels CL MC MF F HF \
  -n <samples_per_class> \
  --freq <frequency_hz> \
  --angular \
  --packing-algo shang-chu
```

**Load Rocks from Existing File:**
```bash
python scripts/main/generate_from_rocks.py \
  --source reference.in \
  --freq 400e6 \
  --pvc 35 \
  output.in
```

**Run Simulations:**
```bash
python scripts/main/run_simulations.py <input_folder> \
  -j <num_jobs> \
  --gpu <device_ids>
```

**Extract Features:**
```bash
python scripts/main/extract_features.py <input_folder> <output_csv>
```

**Visualize Geometry:**
```bash
python scripts/tools/visualization/visualize_gprmax_blueprint.py \
  <input_file.in> \
  -o <output_image.png> \
  --dpi 150
```

### Additional Utilities

**Validate Dataset Consistency:**
```bash
python scripts/tools/data_management/validate_dataset.py <dataset_dir>
```

**Merge Multiple Feature Datasets:**
```bash
python scripts/tools/data_management/merge_datasets.py \
  <input1.csv> <input2.csv> ... \
  -o <output.csv>
```

---

## Development Guidelines

### Before Creating New Scripts

**Always check existing code first:**
1. Search for similar functionality in `src/` and `scripts/`
2. Review existing implementations to understand patterns
3. Reuse, extend, or modify existing code rather than recreating
4. Only write new scripts when existing code doesn't serve the purpose

This prevents duplication and maintains consistency.

### Code Conventions

- Run all scripts from the **project root directory** (ensures `src` imports work)
- Follow [CLAUDE.md](/.claude/CLAUDE.md) guidelines for AI-assisted development
- Use type hints in core library code
- Add docstrings to public functions
- Write unit tests for new modules
- Use configuration files (`.json`, `.yaml`) for parameterization, not hardcoded values

### File Placement

- **Generated data**: `output/{experiment_name}/`
- **Feature datasets**: Same directory as source data
- **Visualizations**: Same directory as input files
- **ML models**: `ml/models/`
- **Reports**: `docs/reports/`
- **Temporary files**: `scratch/`

See [Output File Placement Rules](docs/architecture/DATASET_STRUCTURE.md) for detailed guidelines.

---

## Testing

Run the comprehensive test suite:

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Run specific test category
pytest tests/unit/ -v          # Unit tests
pytest tests/integration/ -v   # Integration tests
pytest tests/performance/ -v   # Benchmarks
```

**Test structure:**
- `tests/unit/` — Tests for individual modules
- `tests/integration/` — End-to-end pipeline tests
- `tests/performance/` — Benchmarking and speed tests
- `tests/fixtures/` — Shared test data and mocks

---

## Documentation

The project includes comprehensive documentation:

- **[User Guide](docs/setup/USER_GUIDE.md)** — Step-by-step usage guide
- **[Setup Guide](docs/setup/README.md)** — Installation and configuration
- **[Troubleshooting](docs/setup/TROUBLESHOOTING.md)** — Common issues and solutions
- **[Generation Process](docs/architecture/GENERATION_PROCESS.md)** — How `.in` files are created
- **[Dataset Structure](docs/architecture/DATASET_STRUCTURE.md)** — Data organization
- **[Packing Algorithms](docs/algorithms/PACKING_ALGORITHMS.md)** — Algorithm comparison and selection
- **[Rock Loading Guide](docs/algorithms/ROCK_LOADING_GUIDE.md)** — Reusing rock geometries
- **[CLI Reference](docs/reports/CLI_REFERENCE.md)** — Command-line argument reference
- **[Fouling Documentation](Fouling.md)** — Physics and fouling classification details

Browse the [docs/](docs/) directory for complete technical documentation.

---

## Research Context

### The Dataset Problem

Existing ballast fouling assessment relies on:
1. **Lab measurements** — Expensive, limited samples
2. **Metadata-based models** — Require lab inputs (permittivity, density, moisture)
3. **Hand-engineered features** — No generalization to field data

### Synth-GPR Solution

Synth-GPR solves this by:
1. **Generating synthetic data at scale** — 10k+ samples with full geometric control
2. **Extracting waveform-only features** — 572 features from A-scan alone
3. **Training production models** — Baseline 70.83% balanced accuracy
4. **Enabling field deployment** — Only Ez waveform needed (no metadata)

### Current Baseline

| Metric | Value |
|--------|-------|
| Dataset size | 50,000 samples |
| Feature dimension | 572 (waveform only) |
| Model type | Random Forest |
| Balanced accuracy | 70.83% |
| Training time | ~30 minutes |

---

## Future Work

- [ ] Multi-antenna configurations (synthetic aperture radar)
- [ ] Transfer learning from synthetic to field data
- [ ] Real-time inference optimization
- [ ] 3D FDTD simulations
- [ ] Novel waveform features (wavelet decomposition, sparse coding)
- [ ] Active learning for targeted data generation
- [ ] Uncertainty quantification in predictions

---

## Contributing

Contributions are welcome! Please:
1. Check [Development Guidelines](#development-guidelines) above
2. Follow [CLAUDE.md](/.claude/CLAUDE.md) for coding standards
3. Add tests for new functionality
4. Update documentation
5. Submit a pull request

---

## License

This project is licensed under the **MIT License** — see LICENSE file for details.

---

## Contact

**Project Author:** Álvaro Jería  
**Email:** alvaro.jeria.m@gmail.com

For questions, issues, or collaboration inquiries, please open an issue or contact the author.

---

## Acknowledgments

- **gprMax** team for the FDTD simulation framework
- **scikit-learn** for the ML toolkit
- Railway engineering research community for domain guidance

---

## Citation

If you use this project in research, please cite:

```bibtex
@software{synthgpr2024,
  author = {Jería, Álvaro},
  title = {Synth-GPR: Synthetic GPR Dataset and Fouling Classification Pipeline},
  year = {2024},
  url = {https://github.com/alvarojeria/Synth-GPR}
}
```

---

**Last updated:** June 2024  
**Maintainer:** Álvaro Jería

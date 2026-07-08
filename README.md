# Synth-GPR: Synthetic Ground Penetrating Radar Dataset & ML Pipeline

[![Python 3.8+](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Code style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![CI](https://github.com/alvaroj-uv/Synth-GPR/actions/workflows/ci.yml/badge.svg)](https://github.com/alvaroj-uv/Synth-GPR/actions/workflows/ci.yml)

## Overview

**Synth-GPR** is a comprehensive framework for generating synthetic Ground Penetrating Radar (GPR) datasets and training machine learning classifiers to assess railway ballast fouling conditions. The project combines electromagnetic simulations (via **gprMax**) with advanced signal processing and machine learning to create production-ready fouling classification models.

### Key Innovation: Waveform-Only Features

The core innovation is **predicting fouling class from GPR Ez waveform features alone** — without relying on metadata (material composition, density, moisture). This is critical because:
- Metadata is unavailable in real-world GPR field deployments
- Waveform features (572-dimensional: time-domain, Hilbert, frequency, STFT, grid) are extracted directly from the received signal
- The goal is a classifier that works on field data where only the A-scan waveform is available

**Baseline status**: a prior pipeline reported 70.83% balanced accuracy (synthetic-only), but that training code is not in this repo and the figure does not transfer to field data — see [docs/reports/HISTORICAL_BASELINE.md](docs/reports/HISTORICAL_BASELINE.md). The repo currently rebuilds the dataset assembler and sim↔real comparison toward re-establishing a reportable baseline.

---

## ✅ What's Currently Operational

This project provides a **fully functional pipeline** for:

1. **🟢 Generate synthetic GPR geometries** — `scripts/pipeline/generate_gprmax_scenes.py` (TOML-driven, configurable fouling levels & rock packing)
2. **🟢 Extract waveform features** — `scripts/pipeline/extract_features.py` (572-dimensional feature extraction from simulations)
3. **🟢 Comprehensive visualization** — `unified_visualizer.py` + 8 specialized plotting tools
4. **🟢 Antenna analysis** — Radiation patterns, mode diagrams, antenna signals visualization

For the **gprMax electromagnetic simulation step**, you'll need gprMax installed separately. Once `.out` files are generated (via `gprmax` command directly or your own simulation runner), feature extraction and visualization work immediately.

**ML status** — the repo does **not** ship a training pipeline. It ships the pieces upstream of training: the dataset assembler (`scripts/pipeline/assemble_dataset.py`), canonical sim↔real metrics (`src/sim_real_comparison.py`), and inference of a pre-trained Rojas-Vivanco XGBoost (`src/vivanco_pipeline.py`). A training/evaluation harness is in progress — see [docs/reports/HISTORICAL_BASELINE.md](docs/reports/HISTORICAL_BASELINE.md).

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
│   │   ├── generate_gprmax_scenes.py   # 🟢 Generate .in geometry files (TOML-driven)
│   │   └── extract_features.py    # 🟢 Extract 572-dim features from .out files
│   ├── visualization/             # 🟢 Plotting & rendering scripts
│   │   ├── unified_visualizer.py              # Main multi-purpose visualizer
│   │   ├── plot_coda_energy_vs_fi.py          # Coda energy analysis
│   │   ├── plot_fouling_classes.py            # Per-class A-scan stacks
│   │   ├── plot_window_energy_features.py     # Windowed feature plots
│   │   ├── visualize_ascan.py                 # A-scan from .out file
│   │   ├── visualize_antenna_signals.py       # Antenna mode signals
│   │   ├── antenna_radiation_pattern.py       # Antenna pattern diagram
│   │   └── antenna_mode_diagram.py            # Mode distribution diagram
│   ├── analysis/                  # (Reserved for validation studies)
│   ├── experiments/               # (Reserved for research experiments)
│   ├── tools/                     # (Reserved for utilities)
│   └── convert_snapshots.py       # EM field snapshot conversion
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

Generate `.in` geometry files using TOML configuration:
```bash
# Generate a single sample
python scripts/pipeline/generate_gprmax_scenes.py config.toml -o output.in

# Generate a batch dataset (50 samples per fouling class)
python scripts/pipeline/generate_gprmax_scenes.py batch_config.toml -o output_dir/
```

**Output:** `.in` files with embedded configuration metadata.
**Note:** Configuration is TOML-driven (the sole source of truth). See `docs/setup/USER_GUIDE.md` for TOML format.

### 2. Run Electromagnetic Simulations

Execute gprMax FDTD simulations (requires gprMax installed):
```bash
# Manual simulation of a single file
gprmax output.in

# Or use the batch runner (when available)
python scripts/pipeline/run_simulations.py output_dir/
```

**Output:** `.out` HDF5 files with Ez electric field time-domain waveforms.

### 3. Extract Features

Extract 572-dimensional feature vectors from simulation outputs:
```bash
python scripts/pipeline/extract_features.py output_dir/ --output features.csv
```

**Output:** `features.csv` with 572 waveform features + 40 metadata columns.
**Requirements:** Output directory must contain:
- `.in` and `.out` files
- `metadata.csv` with FI_class labels

### 4. Visualize Results

Visualize geometries and A-scan signals:

**Geometry only (from `.in` file):**
```bash
python scripts/visualization/unified_visualizer.py test.in --geometry
```

**A-scan + spectrum (from `.out` file):**
```bash
python scripts/visualization/unified_visualizer.py test.out --ascan
```

**Full dashboard (geometry + signals):**
```bash
python scripts/visualization/unified_visualizer.py test.in --dashboard
```

**Generate all visualizations:**
```bash
python scripts/visualization/unified_visualizer.py test.in --all
```

### 5. Advanced Analysis & Visualization

**Coda energy vs. Fouling Index scatter plot:**
```bash
python scripts/visualization/plot_coda_energy_vs_fi.py --dir output_dir/
```

**Stacked A-scans per fouling class:**
```bash
python scripts/visualization/plot_fouling_classes.py --dir output_dir/ --class-field FI_class
```

**Windowed energy features visualization:**
```bash
python scripts/visualization/plot_window_energy_features.py --out output.png
```

**Single A-scan from .out file:**
```bash
python scripts/visualization/visualize_ascan.py test.out --component Ez
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
│ Assemble dataset │  features + meta (anti-circular)
│ + sim↔real cmp   │  → training harness (in progress)
└──────────────────┘
```

---

## Command Reference

### Core Pipeline Scripts

**Generate Synthetic Geometries (TOML-driven):**
```bash
# Single file generation
python scripts/pipeline/generate_gprmax_scenes.py config.toml -o output.in

# Batch dataset generation
python scripts/pipeline/generate_gprmax_scenes.py config.toml -o output_dir/

# Get help and TOML format info
python scripts/pipeline/generate_gprmax_scenes.py --help
```

**Extract Features from Simulations:**
```bash
python scripts/pipeline/extract_features.py <data_dir> --output features.csv
```

### Visualization Scripts

**Unified Visualizer (geometry + A-scan + dashboard):**
```bash
# Geometry only
python scripts/visualization/unified_visualizer.py test.in --geometry

# A-scan + spectrum
python scripts/visualization/unified_visualizer.py test.out --ascan

# Full 4-panel dashboard
python scripts/visualization/unified_visualizer.py test.in --dashboard

# All three visualizations
python scripts/visualization/unified_visualizer.py test.in --all

# Custom output path
python scripts/visualization/unified_visualizer.py test.in -o custom_output.png

# Additional options
python scripts/visualization/unified_visualizer.py test.out \
  --component Ez \
  --title "My Custom Title" \
  --dpi 150 \
  --gain exp \
  --no-show
```

**Analysis Visualizations:**
```bash
# Coda energy vs. Fouling Index
python scripts/visualization/plot_coda_energy_vs_fi.py --dir output_dir/ --limit 1000

# Stacked A-scans per fouling class
python scripts/visualization/plot_fouling_classes.py --dir output_dir/ --class-field FI_class

# Windowed energy features
python scripts/visualization/plot_window_energy_features.py --out features_plot.png

# Single A-scan from .out file
python scripts/visualization/visualize_ascan.py test.out --component Ez

# Antenna signals visualization
python scripts/visualization/visualize_antenna_signals.py test.out

# Antenna radiation pattern
python scripts/visualization/antenna_radiation_pattern.py --freq 400e6

# Antenna mode diagram
python scripts/visualization/antenna_mode_diagram.py --freq 400e6
```

### Utility Scripts

**Convert EM Field Snapshots:**
```bash
python scripts/convert_snapshots.py <input_snapshot> <output_hdf5>
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
3. **Training production models** — in progress (the prior 70.83% synthetic-only figure is not reproduced here; see HISTORICAL_BASELINE.md)
4. **Enabling field deployment** — Only Ez waveform needed (no metadata)

### Baseline status

There is no live training pipeline in this repo, so **no current performance
number is claimed here**. The historical (pre-refactor, synthetic-only) figure —
70.83% balanced accuracy with a Random Forest on 572 waveform features — and why
it is not advertised are documented in
[docs/reports/HISTORICAL_BASELINE.md](docs/reports/HISTORICAL_BASELINE.md).

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

# Scripts Organization Guide

All standalone Python scripts are organized by purpose in the `scripts/` directory and `tests/` folder.

## Directory Structure

### `tests/` (31 files)
Unit and integration tests for the codebase. Located at project root.

**Key test categories:**
- `test_coordinate*.py` — Coordinate system validation
- `test_layer*.py` — Layer stack and configuration
- `test_generation*.py` — Data generation pipeline
- `test_packing*.py` — Rock packing algorithms
- `test_fi_calculation.py` — Fouling index calculations
- `test_workers.py` — Worker class tests
- `test_production.py` — Production code validation

**Running tests:**
```bash
pytest tests/
pytest tests/test_coordinate_trace.py  # Single test
```

---

### `scripts/pipeline/` (18 files)
Core dataset generation, feature extraction, and model training scripts.

**Key scripts:**
- `generate_in_files.py` — Generate GPR input files (.in format)
- `generate_3d_inputs.py` — Create 3D simulation inputs
- `generate_fouling_variants.py` — Generate fouling variation datasets
- `extract_features.py` — Extract waveform features from simulations
- `build_parquet.py` — Consolidate data into Parquet format
- `train_rf.py` — Train random forest models
- `run_rf_pipeline.py` — End-to-end RF pipeline execution
- `run_simulations.py` — Execute GPR simulations

**Usage:**
```bash
python scripts/pipeline/generate_in_files.py --config config.yaml
python scripts/pipeline/train_rf.py --data dataset.parquet
```

---

### `scripts/experiments/` (14 files)
A/B tests, research experiments, and one-off analyses.

**Status:** Research/exploratory — can be archived after publication

**Key experiments:**
- `antenna_twin_ab.py` — Antenna comparison testing
- `hetero_fouling_ab.py` — Heterogeneous fouling variants
- `debye_experiment.py` — Debye model studies
- `waveform_ab.py` — Waveform feature comparison
- `phantom_*.py` — Phantom rock recovery experiments

**Note:** These are transient. Consider archiving completed experiments.

---

### `scripts/analysis/` (10 files)
Post-training analysis, validation, and comparative studies.

**Key scripts:**
- `validate_real.py` — Validate models on real data
- `diagnose_real.py` — Diagnose real-world performance
- `sim2real_gap.py` — Analyze simulation-to-reality gap
- `domain_adapt.py` — Domain adaptation analysis
- `spearman_real.py` — Correlation analysis on real data
- `rock_vs_homog_rigorous.py` — Rock vs. homogeneous comparison

**Usage:**
```bash
python scripts/analysis/validate_real.py --model model.pkl --data real_data.csv
```

---

### `scripts/tools/` (10 files)
Maintenance utilities, code quality checks, and debugging tools.

**Key tools:**
- `audit_codebase.py` — Code quality audit
- `verify_production_imports.py` — Validate import paths
- `regression_check.py` — Regression testing
- `convert_snapshots.py` — EM field snapshot conversion
- `run_packing_single.py` — Single-case packing test
- `test_circlify.py` — Circlify algorithm validation
- `generate_fake_output.py` — Create test data

**Usage:**
```bash
python scripts/tools/audit_codebase.py
python scripts/tools/verify_production_imports.py
```

---

### `scripts/visualization/` (8 files)
Plotting, rendering, and visual analysis scripts.

**Key visualizers:**
- `unified_visualizer.py` — Main visualizer (geometry, A-scan, dashboard; auto-detects 2D/3D)
- `plot_fouling_classes.py` — Fouling classification plots
- `visualize_ascan.py` — A-scan signal visualization
- `render_3d_in_file.py` — 3D domain rendering engine (used by `unified_visualizer.py`)

**Usage:**
```bash
python scripts/visualization/unified_visualizer.py --input data.parquet
python scripts/visualization/plot_fouling_classes.py --model model.pkl
```

---

### `scripts/streamlit/` (3 files)
Interactive web-based dashboards and tools.

**Components:**
- `layer_editor.py` — Interactive layer configuration
- `utils.py` — Streamlit utilities

**Usage:**
```bash
streamlit run scripts/streamlit/layer_editor.py
```

---

## Organization Rationale

| Directory | Purpose | Status | Archival |
|-----------|---------|--------|----------|
| `tests/` | Unit & integration tests | Active | No |
| `pipeline/` | Dataset & model generation | Core | No |
| `experiments/` | Research & A/B tests | Transient | Yes (when done) |
| `analysis/` | Validation & analysis | Supporting | No |
| `tools/` | Code maintenance & debugging | Utility | As-needed |
| `visualization/` | Plotting & rendering | Supporting | No |
| `streamlit/` | Interactive dashboards | Supporting | No |

---

## Adding New Scripts

1. **Determine category** based on purpose:
   - Core data/model work → `pipeline/`
   - Research/experimentation → `experiments/`
   - Validation/post-training → `analysis/`
   - Code quality → `tools/`
   - Plots/visuals → `visualization/`
   - Interactive UI → `streamlit/`

2. **Add docstring** to the script explaining purpose and usage

3. **Place in appropriate folder**

4. **Document in this guide** if it becomes frequently used

---

## Moving Experiments to Archive

When an experiment is complete and published:

```bash
mkdir -p scripts/archived/experiments
mv scripts/experiments/completed_ab.py scripts/archived/experiments/
```

---

## Script Dependencies

- **Pipeline scripts** depend on: `src/` (core functionality)
- **Analysis scripts** depend on: trained models, datasets
- **Visualization scripts** depend on: plotly, matplotlib, data files
- **Streamlit scripts** depend on: streamlit, src/

No circular dependencies between script directories.

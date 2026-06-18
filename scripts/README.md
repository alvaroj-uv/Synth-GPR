# Synth-GPR Scripts

Executable scripts for the Synthetic GPR pipeline, organized by purpose.

For the full organization guide (rationale, archival policy, adding new scripts), see
[docs/operations/SCRIPTS_GUIDE.md](../docs/operations/SCRIPTS_GUIDE.md).
For the packer API used by the generation scripts, see
[docs/SCRIPTS_AND_PACKER.md](../docs/SCRIPTS_AND_PACKER.md).

## Directory Structure

### `pipeline/` — Core Pipeline
Dataset generation, simulation, feature extraction, and model training.

- **`generate_gprmax_scenes.py`** — Generate gprMax `.in` geometry files (dataset or single sample)
- **`run_simulations.py`** — Batch runner for executing gprMax on multiple `.in` files
- **`extract_features.py`** — Extract waveform features from `.out` files (`extract_features_real.py` / `extract_features_rojas.py` for real data)
- **`build_parquet.py`** — Consolidate features into Parquet format (`build_parquet_merged.py`, `build_parquet_coda_aligned.py` variants)
- **`consolidate_dataset.py`** — Merge and rename datasets from multiple sources
- **`train_rf.py`** / **`train_rf_waveform_only.py`** — Train Random Forest classifiers (waveform-only is the production approach)
- **`run_rf_pipeline.py`** — End-to-end RF pipeline execution

### `analysis/` — Validation & Sim-to-Real Studies
- **`validate_real.py`** — Validate models on real GPR data
- **`sim2real_gap.py`** / **`sim2real_regularized.py`** — Simulation-to-reality gap analysis
- **`diagnose_real.py`**, **`spearman_real.py`** — Real-data diagnostics and correlation analysis
- **`domain_adapt.py`** — Domain adaptation analysis
- **`rock_vs_homog_rigorous.py`** — Rock vs. homogeneous medium comparison

### `experiments/` — Research Experiments (transient)
- **`antenna_experiment.py`**, **`verify_antenna_mode.py`** — Antenna configuration studies
- **`homog_debye_slope.py`** — Debye model studies
- **`phantom_domain_shift.py`** — Phantom rock domain-shift experiments
- **`test_ldcp_variants.py`** — LDCP feature variant testing

### `tools/` — Maintenance & Debugging Utilities
- **`audit_codebase.py`** — Code quality audit
- **`verify_production_imports.py`** — Validate import paths
- **`regression_check.py`** — Regression testing
- **`run_packing_single.py`**, **`visualize_packing_strategies.py`** — Packing algorithm testing
- **`generate_test_in_files.py`**, **`generate_fake_output.py`** — Test data generation

### `visualization/` — Plotting & Rendering
- **`unified_visualizer.py`** — Main visualizer (geometry, A-scan, dashboard; auto-detects 2D/3D; `--title`/`--metadata` annotations)
- **`visualize_gprmax_ascans.py`**, **`plot_fouling_classes.py`** — Signal and classification plots

### Root-level
- **`convert_gprmax_snapshots.py`** — EM field snapshot conversion

## Usage

**Always run scripts from the project root directory** so Python can resolve `src` module imports.

```bash
# Generate .in files
python scripts/pipeline/generate_gprmax_scenes.py --help

# Run simulations
python scripts/pipeline/run_simulations.py <dataset_dir>

# Extract features
python scripts/pipeline/extract_features.py <dataset_dir>

# Train the waveform-only classifier (production approach)
python scripts/pipeline/train_rf_waveform_only.py --data dataset.parquet
```

# Output File Placement Rules for Synth-GPR Project

## Overview
This document defines standardized rules for where LLM code agents should place output files in the Synth-GPR project. Following these rules ensures consistency, prevents conflicts, and maintains clean project organization.

## Directory Structure

```
Synth-GPR/
├── output/                    # Main generated data outputs
│   ├── single_test/          # Individual test runs
│   └── test/                 # Batch test outputs
├── output_test/              # Test examples and validation data
├── scratch/                  # Temporary/experimental files
├── docs/reports/             # Analysis reports and documentation
├── ml/                       # Machine learning outputs
│   └── models/              # Trained models (if created)
└── .claude/                  # AI-generated temporary files
```

## Output File Placement Rules

### 1. Generated GPR Data Files (`.in`, `.out`, `.csv`)

**Location:** `output/` subdirectories

**Rules:**
- `.in` files (gprMax input): `output/{experiment_name}/` or `output/single_test/`
- `.out` files (gprMax output): Same directory as corresponding `.in` files
- `metadata.csv`: Same directory as `.in` files
- `features_dataset.csv`: Same directory as `.out` files or `output/{experiment_name}/`

**Examples:**
```
output/my_experiment/
├── s_0001.in
├── s_0001.out
├── s_0002.in
├── s_0002.out
├── metadata_CL.csv
└── features_dataset.csv
```

### 2. Visualization Outputs (`.png`, `.jpg`, `.svg`)

**Location:** Same directory as input data, or `output_test/` for examples

**Rules:**
- Blueprint visualizations: Same directory as `.in`/`.out` files
- Test/example plots: `output_test/` directory
- Analysis plots: `docs/reports/` or same directory as analyzed data

**Examples:**
```
# Blueprint for generated data
output/my_experiment/s_0001.png

# Test examples
output_test/angular_rocks_400MHz.png
output_test/clean_400MHz_ascan.png
```

### 3. Machine Learning Outputs

**Location:** `ml/` subdirectories

**Rules:**
- Trained models: `ml/models/`
- Training logs: `ml/training_logs/`
- Evaluation results: `ml/evaluation_results/`
- Feature datasets: `output/{experiment_name}/` (not in ml/)

**Examples:**
```
ml/
├── models/
│   ├── rf_model_2026.pkl
│   └── xgboost_model_2026.pkl
├── training_logs/
│   └── training_2026_05_10.log
└── evaluation_results/
    └── validation_metrics.json
```

### 4. Analysis Reports and Documentation

**Location:** `docs/reports/`

**Rules:**
- Code analysis reports: `docs/reports/`
- Performance benchmarks: `docs/reports/`
- Validation summaries: `docs/reports/`
- Keep existing reports like `CODE_AUDIT_REPORT.md`, `vulture_report.txt`

**Examples:**
```
docs/reports/
├── CODE_AUDIT_REPORT.md
├── FINAL_SYSTEM_SUMMARY.md
├── vulture_report.txt
└── performance_benchmark_2026.json
```

### 5. Temporary and Scratch Files

**Location:** `scratch/` directory

**Rules:**
- Experimental code: `scratch/`
- Temporary data files: `scratch/`
- Debug outputs: `scratch/`
- Files that might be deleted later

**Examples:**
```
scratch/
├── experimental_feature.py
├── debug_output.csv
└── temp_visualization.png
```

### 6. Test Outputs

**Location:** `output_test/` for examples, `tests/` for test artifacts

**Rules:**
- Example outputs for documentation: `output_test/`
- Unit test artifacts: `tests/` (usually cleaned up)
- Integration test outputs: `output/test/`

**Examples:**
```
# Example data for docs
output_test/
├── angular_rocks_400MHz.in
├── angular_rocks_400MHz.out
└── angular_rocks_400MHz.png

# Test artifacts (if kept)
tests/
└── test_output/
    └── sample_data.csv
```

### 7. AI/LLM Generated Files

**Location:** `.claude/` directory

**Rules:**
- Temporary files created during AI assistance: `.claude/`
- Draft code snippets: `.claude/`
- Analysis artifacts: `.claude/`

**Examples:**
```
.claude/
├── analysis_notes.md
├── code_drafts.py
└── temp_analysis.json
```

## File Naming Conventions

### Timestamped Outputs
```
{experiment_name}_{YYYYMMDD_HHMMSS}/
├── s_{id}.in
├── s_{id}.out
└── metadata_{label}.csv
```

### Feature Datasets
```
features_dataset.csv
features_{experiment_name}.csv
features_{timestamp}.csv
```

### Visualization Files
```
{input_filename}.png
{input_filename}_blueprint.png
{input_filename}_{component}_features.png
```

## Priority Order for Output Locations

When deciding where to place outputs:

1. **Same directory as inputs** - For transformations of existing files
2. **Experiment-specific subdirectories** - For new data generation
3. **Purpose-specific directories** - ML outputs in `ml/`, reports in `docs/reports/`
4. **Scratch for temporary** - Files that might be discarded
5. **Test directories** - For validation and examples

## Special Cases

### Large Files
- GPR `.out` files can be large (>50MB)
- Consider using `output/` subdirectories to organize by experiment
- Avoid committing large files to git (already in `.gitignore`)

### Batch Processing
- Create timestamped subdirectories: `output/batch_{YYYYMMDD_HHMMSS}/`
- Include metadata and logs in the same directory
- Use descriptive names: `output/granular_mode_test_20260510/`

### Configuration Files
- User configs: Project root (e.g., `config.ini`)
- Generated configs: Same directory as outputs
- Template configs: `docs/` or project root

## Validation Checklist

Before creating outputs, ask:
- [ ] Is this a temporary file? → `scratch/`
- [ ] Is this test/example data? → `output_test/`
- [ ] Is this ML-related? → `ml/` subdirectories
- [ ] Is this documentation/analysis? → `docs/reports/`
- [ ] Is this generated data? → `output/{experiment}/`
- [ ] Does it belong with existing inputs? → Same directory as inputs

## Examples in Action

### Generating Synthetic GPR Data
```python
# Output location: output/my_gpr_experiment/
output_dir = "output/my_gpr_experiment"
# Creates: s_0001.in, s_0001.out, metadata_CL.csv, features_dataset.csv
```

### Creating Visualization
```python
# Output location: Same as input or output_test/
input_file = "output/my_experiment/s_0001.in"
output_file = "output/my_experiment/s_0001_blueprint.png"
```

### ML Model Training
```python
# Output location: ml/models/ and ml/evaluation_results/
model_path = "ml/models/rf_model.pkl"
results_path = "ml/evaluation_results/validation_metrics.json"
```

### Analysis Report
```python
# Output location: docs/reports/
report_path = "docs/reports/code_analysis_2026.md"
```</content>
<parameter name="filePath">d:\Codigo\Synth-GPR.bck\Synth-GPR-1\docs\OUTPUT_FILE_PLACEMENT_RULES.md
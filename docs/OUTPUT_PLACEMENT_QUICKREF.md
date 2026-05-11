# Output File Placement - Quick Reference

## Synth-GPR Output Directory Rules

| File Type | Primary Location | Examples | Notes |
|-----------|------------------|----------|-------|
| **GPR Data** (`.in`, `.out`, `.csv`) | `output/{experiment}/` | `output/my_test/s_0001.in` | Group by experiment/timestamp |
| **Features CSV** | Same as `.out` files | `output/my_test/features_dataset.csv` | Keep with source data |
| **Visualizations** (`.png`) | Same as input data | `output/my_test/s_0001.png` | Or `output_test/` for examples |
| **ML Models** | `ml/models/` | `ml/models/rf_model.pkl` | Separate from data |
| **ML Results** | `ml/evaluation_results/` | `ml/evaluation_results/metrics.json` | Keep evaluation separate |
| **Reports/Analysis** | `docs/reports/` | `docs/reports/analysis.md` | Documentation outputs |
| **Temporary Files** | `scratch/` | `scratch/temp_analysis.py` | May be deleted |
| **Test Examples** | `output_test/` | `output_test/sample.in` | For documentation/examples |
| **AI Temp Files** | `.claude/` | `.claude/draft.py` | AI-generated temporaries |

## Quick Decision Tree

```
New data generation?
├── Yes → output/{experiment_name}/
└── No → Transform of existing data?
    ├── Yes → Same directory as input
    └── No → What type?
        ├── ML → ml/{subdirectory}/
        ├── Report → docs/reports/
        ├── Test → output_test/
        └── Temp → scratch/
```

## Naming Patterns

- **Experiments**: `output/{experiment}_{YYYYMMDD}/`
- **Features**: `features_dataset.csv` or `features_{experiment}.csv`
- **Visualizations**: `{input_name}.png` or `{input_name}_blueprint.png`
- **Models**: `{model_type}_model_{date}.pkl`
- **Reports**: `{topic}_{date}.md` or `{topic}_{date}.json`

## Key Principles

1. **Group related files together** - Keep `.in`, `.out`, and analysis in same directory
2. **Separate concerns** - ML models ≠ data, reports ≠ code
3. **Use descriptive names** - Include experiment names and timestamps
4. **Avoid root directory clutter** - Use appropriate subdirectories
5. **Follow existing patterns** - Match current project conventions</content>
<parameter name="filePath">d:\Codigo\Synth-GPR.bck\Synth-GPR-1\docs\OUTPUT_PLACEMENT_QUICKREF.md
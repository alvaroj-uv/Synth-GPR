# Synth-GPR Codebase Inventory

## Overview
This document provides a comprehensive inventory of the Synth-GPR codebase structure, key components, and file organization.

## Root Directory Structure
```
Synth-GPR/
├── .claude/                  # Claude AI configuration
├── .github/                  # GitHub configuration files
├── .hypothesis/              # Hypothesis testing configuration
├── .vscode/                  # VSCode workspace settings
├── attic/                    # Archived/deprecated code
├── calibration/              # Calibration scripts and data
├── docs/                     # Documentation
├── examples/                 # Example scripts and notebooks
├── experiments/              # Experimental code and tests
├── external/                 # External dependencies/libraries
├── output/                   # Output files (images, results)
├── scripts/                  # Utility and processing scripts
├── src/                      # Main source code
├── tests/                    # Test suite
├── .gitignore
├── pytest.ini
├── README.md
├── requirements.txt
├── Synth-GPR.code-workspace
└── TODO_claude_code.md
```

## Key Directories Analysis

### 1. src/ - Main Source Code (100+ files)
The core implementation organized into:
- **Root level modules** (70+ .py files): Core functionality
- **data_access/** - Data I/O and access patterns
- **domain/** - Domain models and value objects  
- **repositories/** - Data repository implementations
- **visualization/** - Visualization components

**Key modules identified:**
- `vivanco_pipeline.py` - Main processing pipeline
- `rock_packing.py`, `rock_voxelizer.py` - Rock modeling
- `gprmax_runner.py` - GPR simulation interface
- `signal_processing.py` - Signal processing utilities
- `feature_extraction.py` - Feature extraction algorithms
- `packing_verifier.py` - Packing validation

### 2. scripts/ - Utility Scripts (50+ files)
Organized into subdirectories:
- **calibration/** - Calibration utilities
- **pipeline/** - Data pipeline scripts  
- **visualization/** - Visualization tools

**Notable scripts:**
- `generate_and_organize_datasets.py`
- `render_gprmax_scenes.py`
- `process_signal_vivanco_method.py`
- `generate_test_fixtures.py`

### 3. tests/ - Test Suite
- **40+ test files** covering core functionality
- **fixtures/** directory with test data
  - Golden features and traces
  - Real and simulated scene data
  - Ground truth references

### 4. calibration/ - Calibration Module
- Calibration algorithms and validation scripts
- Integration with real-world data

### 5. experiments/ - Experimental Code
- Research and development workspace
- Prototyping new features

## File Type Distribution
- **Python files (.py)**: 200+ (core implementation)
- **Configuration files**: pytest.ini, requirements.txt
- **Documentation**: README.md, various .md files
- **Data files**: .npy, .json, .csv in test fixtures
- **Image outputs**: .png files in output/

## Key Technical Components

### Domain Model
- `src/domain/` - Core domain entities
- Value objects, coordinates, scene parameters

### Data Access Layer
- `src/data_access/` - Repository pattern implementation
- Readers and writers for various data formats

### Visualization System
- `src/visualization/` - 3D rendering and plotting
- Dashboard and publication figure generation

### Processing Pipeline
- Signal processing chain
- Feature extraction workflow
- Calibration and validation

## Build and Test Infrastructure
- pytest configuration with comprehensive test coverage
- Hypothesis property-based testing
- Golden master testing approach
- Continuous integration ready

## External Dependencies
- GPRMax integration (GPR simulation)
- NumPy, SciPy for scientific computing
- Matplotlib, Plotly for visualization
- PyTest for testing framework

## Development Workflow
- Git-based version control
- Branch: `refactor/voxel-crim-module-split`
- Recent commits focus on calibration and validation
- Active development with 19 uncommitted changes

## Notable Features
1. **Rock Packing System**: Multiple packing algorithms (pymunk, rcpgenerator)
2. **Signal Processing Pipeline**: Vivanco method implementation
3. **3D Visualization**: Rock models and scene rendering
4. **Calibration Framework**: Real-world data integration
5. **Comprehensive Testing**: Unit, integration, and regression tests

## File Count Summary
- **Python source files**: ~200
- **Test files**: ~40
- **Script files**: ~50
- **Configuration files**: ~5
- **Documentation files**: ~10

## Recommendations
1. The codebase shows good separation of concerns with domain/repositories/visualization layers
2. Comprehensive test coverage suggests mature development practices
3. The calibration module indicates real-world validation focus
4. Multiple packing algorithms suggest research-oriented development
5. Consider documenting the relationship between key modules for new contributors
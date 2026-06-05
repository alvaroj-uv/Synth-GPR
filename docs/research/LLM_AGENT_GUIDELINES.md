# LLM Code Agent Guidelines for Synth-GPR

## Overview
This document provides guidelines for LLM code agents working on the Synth-GPR project. It ensures consistent file placement, coding standards, and project organization.

## 1. Output File Placement

### Primary Reference
- **[Output File Placement Rules](../architecture/OUTPUT_FILE_PLACEMENT_RULES.md)**: Comprehensive guidelines
- **[Documentation Index](../INDEX.md)**: Find docs by category

### Automated Resolution
Use the output resolver utility for consistent file placement:

```python
from scripts.tools.output_resolver import resolve_output_path

# Example: Feature dataset
features_path = resolve_output_path(
    "features_dataset.csv",
    input_dir="output/my_experiment"
)

# Example: ML model
model_path = resolve_output_path(
    "rf_model.pkl",
    file_type="ml_model"
)

# Example: Visualization
viz_path = resolve_output_path(
    "blueprint.png",
    input_dir="output/my_experiment"
)
```

### Key Rules Summary
- **GPR Data** (`.in`, `.out`, `.csv`): `output/{experiment_name}/`
- **Features**: Same directory as source `.out` files
- **Visualizations**: Same directory as input files
- **ML Models**: `ml/models/`
- **Reports**: `docs/reports/`
- **Temporary**: `scratch/`
- **AI Files**: `.claude/`

## 2. Code Organization

### Import Order
```python
# Standard library
import os
import sys
from pathlib import Path

# Third-party
import numpy as np
import pandas as pd

# Project imports (absolute)
from src.config import GeneratorConfig
from src.data_loader import read_gprmax_hdf5
```

### Error Handling
```python
try:
    # Operation that might fail
    result = process_data(data)
except Exception as e:
    logger.error(f"Failed to process data: {e}")
    raise  # Re-raise with context
```

### Logging
```python
import logging
logger = logging.getLogger(__name__)

logger.info("Starting data generation")
logger.warning("Potential issue detected")
logger.error("Critical error occurred")
```

## 3. Testing

### Test File Location
- Unit tests: `tests/test_*.py`
- Integration tests: `tests/test_*_integration.py`
- Fixtures: `tests/conftest.py`

### Test Structure
```python
import pytest
from src.my_module import MyClass

class TestMyClass:
    def test_initialization(self):
        """Test basic initialization."""
        obj = MyClass()
        assert obj is not None

    def test_with_fixture(self, sample_data):
        """Test using pytest fixtures."""
        result = process_sample_data(sample_data)
        assert result is not None
```

## 4. Documentation

### Code Documentation
```python
def generate_synthetic_data(
    output_dir: str,
    num_samples: int = 100,
    labels: List[str] = None
) -> Dict[str, Any]:
    """
    Generate synthetic GPR data for machine learning.

    This function creates gprMax input files (.in) with varying ballast
    fouling conditions for training ML models.

    Args:
        output_dir: Directory to save generated files
        num_samples: Number of samples per fouling class
        labels: List of fouling labels (e.g., ['CL', 'MF', 'F'])

    Returns:
        Dictionary with file paths and metadata

    Raises:
        ValueError: If output_dir is invalid
        RuntimeError: If generation fails

    Example:
        >>> result = generate_synthetic_data("output/test", 50, ['CL', 'F'])
        >>> print(f"Generated {len(result['files'])} files")
    """
```

### File Headers
```python
"""
Module for GPR data processing and feature extraction.

This module provides utilities for loading, processing, and analyzing
Ground Penetrating Radar data from gprMax simulations.
"""
```

## 5. Code Quality

### Type Hints
```python
from typing import List, Dict, Optional, Union, Tuple
import numpy as np

def process_signal(
    signal: np.ndarray,
    sampling_rate: float,
    filter_cutoff: Optional[float] = None
) -> Tuple[np.ndarray, Dict[str, float]]:
    # Function implementation
    pass
```

### Constants
```python
# In src/constants.py or module constants
DEFAULT_SAMPLING_RATE = 1e9  # Hz
MAX_SIGNAL_LENGTH = 10000
FOULING_CLASSES = ['CL', 'MC', 'MF', 'F', 'HF']
```

### Naming Conventions
- **Functions**: `snake_case` (e.g., `generate_dataset`)
- **Classes**: `PascalCase` (e.g., `DatasetGenerator`)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `DEFAULT_SAMPLING_RATE`)
- **Files**: `snake_case.py` (e.g., `data_loader.py`)

## 6. Git and Version Control

### Commit Messages
```
feat: add multi-offset antenna support
fix: correct dielectric calculation for wet ballast
docs: update output file placement rules
refactor: simplify feature extraction pipeline
test: add validation for gprMax input files
```

### Branch Naming
- Features: `feature/multi-offset-antennas`
- Fixes: `fix/dielectric-calculation`
- Documentation: `docs/output-rules`

## 7. Performance Considerations

### Large Files
- GPR `.out` files can exceed 50MB
- Avoid committing large files to git
- Use `.gitignore` patterns for generated data

### Memory Usage
```python
# Process large datasets in chunks
def process_large_dataset(file_path: str, chunk_size: int = 1000):
    with pd.read_csv(file_path, chunksize=chunk_size) as reader:
        for chunk in reader:
            process_chunk(chunk)
```

### Parallel Processing
```python
from concurrent.futures import ThreadPoolExecutor
import multiprocessing

def process_files_parallel(file_list: List[str]) -> List[Dict]:
    num_workers = min(len(file_list), multiprocessing.cpu_count())
    with ThreadPoolExecutor(max_workers=num_workers) as executor:
        results = list(executor.map(process_single_file, file_list))
    return results
```

## 8. Error Messages and User Feedback

### Clear Error Messages
```python
if not Path(output_dir).exists():
    raise ValueError(
        f"Output directory does not exist: {output_dir}. "
        "Please create the directory or specify a valid path."
    )

if num_samples < 1:
    raise ValueError(
        f"Number of samples must be positive, got {num_samples}"
    )
```

### Progress Reporting
```python
from tqdm import tqdm

def process_files(file_list: List[str]) -> None:
    for file_path in tqdm(file_list, desc="Processing files"):
        process_single_file(file_path)
```

## 9. Configuration Management

### Configuration Approach
The system uses **CLI-driven configuration** via `GeneratorConfig` class:

```python
from src.config import GeneratorConfig

# Create configuration with frequency-aware scaling
config = GeneratorConfig.create_physically_perfect(
    center_freq_hz=400e6,  # 400 MHz
    rock_packing_algorithm="shang_chu",
    angular_rocks=True,
    base_seed=42
)
```

See [PACKING_ALGORITHMS.md](PACKING_ALGORITHMS.md) for algorithm options.

### Environment Variables
```python
import os

# Optional: override default output directory
DATA_DIR = os.getenv('SYNTH_GPR_DATA_DIR', 'output')

# Optional: gprMax installation path
GPRMAX_PATH = os.getenv('GPRMAX_PATH', 'gprmax')
```

## 10. Security and Data Handling

### File Path Validation
```python
def validate_output_path(path: str) -> Path:
    """Validate and resolve output path safely."""
    resolved = Path(path).resolve()

    # Ensure path is within project directory
    project_root = Path(__file__).parent.parent
    try:
        resolved.relative_to(project_root)
    except ValueError:
        raise ValueError(f"Output path must be within project directory: {path}")

    return resolved
```

### Sensitive Data
- Avoid hardcoding API keys or credentials
- Use environment variables for sensitive configuration
- Never commit test data containing real information

## Quick Checklist for Code Changes

- [ ] Output files placed according to rules
- [ ] Code follows import/type hint conventions
- [ ] Functions have docstrings with examples
- [ ] Error messages are clear and actionable
- [ ] Tests added for new functionality
- [ ] Documentation updated if needed
- [ ] No large files committed to git
- [ ] Code passes linting checks</content>
<parameter name="filePath">d:\Codigo\Synth-GPR.bck\Synth-GPR-1\docs\LLM_AGENT_GUIDELINES.md
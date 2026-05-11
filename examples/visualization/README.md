# Visualization Examples

This directory contains example scripts demonstrating the Synth-GPR visualization system.

## Scripts

### `test_node_model.py`
Demonstrates the node-based visualization system for creating complex figures programmatically.

**Features:**
- B-scan (2D raster) visualization
- A-scan (1D trace) with wiggle display
- Node-based composition system
- Synthetic GPR data generation

**Usage:**
```bash
python examples/visualization/test_node_model.py
```

**Output:** `node_model_test.webp` - Side-by-side B-scan and A-scan visualization

### `test_processing.py`
Demonstrates the signal processing pipeline with step-by-step visualization.

**Features:**
- Raw signal generation with noise and artifacts
- Dewow filtering
- Time zero correction with first break detection
- AGC gain application
- Spectrogram analysis
- Multi-panel processing visualization

**Usage:**
```bash
python examples/visualization/test_processing.py
```

**Output:** `test_processing_result.webp` - 4-panel processing pipeline visualization

## Architecture

These examples showcase the two main visualization approaches in Synth-GPR:

1. **Node-based system** (`src/visualization/nodes.py`, `renderer.py`) - Declarative figure composition
2. **Direct plotting** (`src/visualization/dashboard.py`, `panels.py`) - Imperative plotting functions

## Dependencies

- numpy
- matplotlib
- scipy
- Synth-GPR src modules (automatically added to path)</content>
<parameter name="filePath">d:\Codigo\Synth-GPR.bck\Synth-GPR-1\examples\visualization\README.md
# Feature Dataset Generator

Script to automatically create feature dataset CSV files from folders containing gprMax output files.

## Location
`scripts/create_feature_dataset.py`

## Usage

### Basic Usage
Process all `.out` files in a folder:
```bash
python scripts/create_feature_dataset.py <input_folder>
```

### Examples

**1. Process files from the samples folder:**
```bash
python scripts/create_feature_dataset.py samples/
```

**2. Specify custom output filename:**
```bash
python scripts/create_feature_dataset.py output/ -o my_features.csv
```

**3. Use metadata file for labeling:**
```bash
python scripts/create_feature_dataset.py samples/ -m metadata.csv -o features.csv
```

**4. Extract specific fields:**
```bash
python scripts/create_feature_dataset.py samples/ --fields Ez Ey Hx
```

**5. Quiet mode (suppress progress messages):**
```bash
python scripts/create_feature_dataset.py samples/ -q
```

## Command-Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `input_folder` | Folder containing `.out` files (required) | - |
| `-o, --output` | Output CSV filename | `features_dataset.csv` |
| `-m, --metadata` | Metadata CSV for labeling | None |
| `--fields` | Fields to extract (e.g., Ez, Ey, Hx) | `['Ez']` |
| `-q, --quiet` | Suppress progress messages | False |

## Metadata File Format

If you provide a metadata file with `-m`, it should be a CSV with these columns:
- `filename`: Name of the input/output file
- `FI_class` (or `Label`): Classification label

Example metadata.csv:
```csv
filename,FI_class
sample_0000_uniform.in,Clean
sample_0001_uniform.in,Clean
sample_0002_gradient.in,Moderate
```

## Output Format

The script generates a CSV file with:
- **Filename**: Source `.out` file
- **Label**: Classification label (from metadata or filename)
- **Signal**: Signal name (e.g., Ez_rx1)
- **Features**: All extracted features (722 columns)

## Features

✓ Processes all `.out` files in a directory
✓ Flexible labeling (via metadata file or filename parsing)
✓ Supports multiple field extraction
✓ Progress tracking with detailed output
✓ Error handling for individual files
✓ Clean, organized output CSV

## Related Scripts

- `batch_extract_features.py` - Lower-level batch extraction (used internally)
- `visualize_single_signal.py` - Visualize individual signals
- `batch_visualize.py` - Visualize multiple files

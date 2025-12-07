# Smart INI/CLI Usage Guide

## Overview

Scripts now support **smart configuration detection**:
1. **Default INI**: Looks for `<script_name>.ini` in current directory
2. **Explicit INI**: Accepts `.ini` file as argument
3. **CLI Fallback**: Falls back to command-line arguments if no INI found

## Priority Order

```
1. Explicit INI file:  python script.py custom_config.ini
2. Default INI file:   python script.py  (looks for script.ini)
3. CLI arguments:      python script.py output_dir --labels CL -n 10
```

---

## Usage Examples

### generate_dataset.py

**Option 1: Default INI (Easiest)**
```bash
# Create generate_dataset.ini in current directory
# Then just run:
python scripts/main/generate_dataset.py
```

**Option 2: Explicit INI**
```bash
python scripts/main/generate_dataset.py my_config.ini
```

**Option 3: CLI (Backward Compatible)**
```bash
python scripts/main/generate_dataset.py output_dir --labels CL MF -n 10 --start_id 0
```

---

## Default INI Files

Each script looks for its own default INI file:

| Script | Default INI File |
|--------|------------------|
| `generate_dataset.py` | `generate_dataset.ini` |
| `run_simulations.py` | `run_simulations.ini` |
| `batch_extract_features.py` | `batch_extract_features.ini` |
| `visualize_gprmax_blueprint.py` | `visualize_gprmax_blueprint.ini` |

---

## Creating Default INI Files

### For Dataset Generation

Create `generate_dataset.ini`:
```ini
[workflow]
output_dir = d:/Codigo/Synth-Data/MyDataset
labels = CL,MC,MF,F
samples_per_label = 10
start_id = 1000
```

Then simply run:
```bash
python scripts/main/generate_dataset.py
```

### For Simulations

Create `run_simulations.ini`:
```ini
[workflow]
num_jobs = 8
gpu_devices = 0,1
```

Then run:
```bash
python scripts/main/run_simulations.py input_folder
```

---

## Benefits

✅ **Convenience**: No arguments needed with default INI  
✅ **Flexibility**: Can override with explicit INI or CLI  
✅ **Backward Compatible**: Existing CLI commands still work  
✅ **Self-Documenting**: INI files show all available options  

---

## Migration Path

**Step 1**: Create default INI files for your common workflows
```bash
# Copy template
cp config_template.ini generate_dataset.ini

# Edit for your needs
notepad generate_dataset.ini
```

**Step 2**: Run without arguments
```bash
python scripts/main/generate_dataset.py
```

**Step 3**: Gradually phase out CLI usage

---

## Tips

**Tip 1**: Keep default INI files in your project root
```
Synth-GPR/
├── generate_dataset.ini      # Default config
├── config_pipeline_test.ini  # Test config
├── config_production.ini     # Production config
└── scripts/
```

**Tip 2**: Use different INI files for different scenarios
```bash
# Development
python generate_dataset.py config_dev.ini

# Testing
python generate_dataset.py config_test.ini

# Production
python generate_dataset.py config_prod.ini
```

**Tip 3**: Version control your INI files
```bash
git add *.ini
git commit -m "Add dataset generation configs"
```

---

## Troubleshooting

**Q: Script uses CLI even though I have an INI file**  
A: Make sure the INI file is named exactly `<script_name>.ini` and is in the current directory

**Q: How do I force CLI mode?**  
A: Rename or move the default INI file, or pass arguments that don't end in `.ini`

**Q: Can I use both INI and CLI?**  
A: No, it's either/or. INI takes priority if found.

---

## Complete Example

```bash
# 1. Create default config
cat > generate_dataset.ini << EOF
[workflow]
output_dir = d:/Data/Test
labels = CL,MF
samples_per_label = 5
start_id = 0
EOF

# 2. Run with default config
python scripts/main/generate_dataset.py

# 3. Or override with explicit config
python scripts/main/generate_dataset.py config_pipeline_test.ini

# 4. Or use CLI (no INI file needed)
python scripts/main/generate_dataset.py d:/Data/Test2 --labels CL -n 5
```

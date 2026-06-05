# File Handling Analysis: Synth-GPR vs Landmine Classifier

**Date:** 2026-06-04  
**Focus:** Data pipeline, I/O operations, and efficiency

---

## Current File Handling Architecture (Synth-GPR)

### Directory Structure
```
output/
├── dataset_variants/
│   ├── s_0000.in           ← gprMax input files
│   ├── s_0000.out          ← gprMax output (HDF5)
│   ├── metadata.csv        ← Scene metadata
│   └── ... (30k+ files)
│
├── dataset_80k_features.parquet  ← Feature dataset (573 cols)
└── dataset_coda_features.parquet ← Coda-aligned features
```

### File Handling Modules

| Module | Purpose | Status |
|--------|---------|--------|
| `data_loader.py` | Read HDF5 (.out files) | ✅ Works, but basic |
| `dataset_io.py` | Read/write parquet | ✅ Good (centralized) |
| `file_reader.py` | Extract config from .in files | ✅ Good (detailed parsing) |
| `filesystem_repository.py` | Scene persistence | ✅ Structured |

---

## Issues Found in Your File Handling

### 1. **Error Handling in `data_loader.py` is Silent**

Current code:
```python
def read_gprmax_hdf5(filename, fields=['E', 'H']):
    try:
        f = h5py.File(filename, 'r')
    except FileNotFoundError:
        print(f"Error: File {filename} not found.")
        return pd.DataFrame()  # ← Returns empty silently!
    except OSError:
        print(f"Error: Could not open file {filename}. It might be corrupted...")
        return pd.DataFrame()  # ← Returns empty silently!
```

**Problem:** Empty DataFrame returned without clear indication of failure
- Feature extraction pipeline continues with empty data
- Errors cascade downstream (you extract features from nothing)
- Hard to debug which file failed in a 30k-file pipeline

**Better approach:**
```python
def read_gprmax_hdf5(filename, fields=['E', 'H']):
    try:
        f = h5py.File(filename, 'r')
    except FileNotFoundError as e:
        raise FileNotFoundError(f"GPR file not found: {filename}") from e
    except OSError as e:
        raise OSError(f"Cannot read HDF5 file {filename} (corrupted or wrong format)") from e
    
    try:
        # ... processing ...
    except Exception as e:
        raise ValueError(f"Error processing {filename}: {e}") from e
    finally:
        f.close()
```

**Benefit:** Exceptions bubble up → you catch them with `try/except` in the caller

### 2. **Path Handling is Inconsistent**

Some code uses strings:
```python
# data_loader.py
def read_gprmax_hdf5(filename, fields=['E', 'H']):  # filename is string
    f = h5py.File(filename, 'r')
```

Some uses Path objects:
```python
# filesystem_repository.py
def __init__(self, output_dir: Path | str):
    self.output_dir = Path(output_dir)
    in_file_path = self.output_dir / f"{scene_id}.in"
```

**Inconsistency costs:**
- Different scripts expect different types
- Have to convert back-and-forth
- Type hints are sometimes wrong

**Better:**
```python
# Always convert to Path at entry point
from pathlib import Path

def read_gprmax_hdf5(filename: Path | str, fields=['E', 'H']):
    filename = Path(filename)  # Normalize
    
    if not filename.exists():
        raise FileNotFoundError(f"File not found: {filename}")
    if not filename.suffix == '.out':
        raise ValueError(f"Expected .out file, got {filename.suffix}")
```

### 3. **No Progress Tracking for Large Pipelines**

Your extraction scripts read 30k files but don't show progress:
```python
# build_parquet.py (current)
for out_path in out_files:
    m = re.search(r"s_(\d+)\.out$", out_path.name)
    # ... no progress bar ...
```

**Problem:** 30k files = 30+ minutes of processing. User doesn't know if it's hanging or working.

**Better:**
```python
from tqdm import tqdm

for out_path in tqdm(out_files, desc="Processing .out files", unit="file"):
    # ... same code ...
    # Shows: Processing: 15237/30000 [50%] ⏱️ ETA 15:23
```

### 4. **Memory Inefficiency: Loading Entire Datasets**

Current `load_features()`:
```python
def load_features(path, columns=None):
    return pd.read_parquet(path, columns=list(columns) if columns is not None else None)
```

**Problem with 30k samples × 573 features:**
- Entire dataset loaded into memory (~500 MB)
- Can't process datasets larger than available RAM
- No streaming/chunking support

**Better (for large datasets):**
```python
def load_features_chunked(path, chunksize=1000, columns=None):
    """Generator that yields chunks of data."""
    reader = pd.read_parquet(path, columns=columns)
    for i in range(0, len(reader), chunksize):
        yield reader.iloc[i:i+chunksize]

# Usage:
for chunk in load_features_chunked('big_dataset.parquet', chunksize=5000):
    process_chunk(chunk)  # Never have full dataset in memory
```

### 5. **No File Validation**

Code assumes files are correct:
```python
def read_gprmax_hdf5(filename, fields=['E', 'H']):
    f = h5py.File(filename, 'r')
    dt = f.attrs.get('dt', PC.DEFAULT_DT)  # Silent fallback if missing!
    iterations = f.attrs.get('Iterations', 0)  # Returns 0 if missing!
```

**Problem:** Missing attributes silently use defaults
- Bad HDF5 file with wrong dt → features are scaled wrong
- Missing Iterations → time array is empty
- Cascades to garbage features, garbage model

**Better:**
```python
def read_gprmax_hdf5(filename, fields=['E', 'H']):
    f = h5py.File(filename, 'r')
    
    if 'dt' not in f.attrs:
        raise ValueError(f"Missing 'dt' attribute in {filename}")
    if 'Iterations' not in f.attrs:
        raise ValueError(f"Missing 'Iterations' attribute in {filename}")
    
    dt = float(f.attrs['dt'])
    iterations = int(f.attrs['Iterations'])
    
    if dt <= 0 or iterations <= 0:
        raise ValueError(f"Invalid dt={dt} or iterations={iterations} in {filename}")
```

---

## Landmine Classifier Approach (Simpler)

They have a much simpler pipeline:

```python
# generate_synthetic_data.py
# 1. Generate .out files with gprMax

# process.py
# 2. Read .out files → normalize → resample to 300 samples → CSV

# train.py
# 3. Read CSV → AutoKeras trains on raw waveforms
```

**Their file structure:**
```
data/
├── synthetic/
│   ├── trace_0_target.npy     ← NumPy array of waveform
│   ├── trace_1_mixed.npy
│   └── ... (labels in filename)
│
└── synthetic_data.csv          ← Features + labels
```

**Why simpler is better:**
- ✅ Less metadata to manage
- ✅ Direct waveform arrays (no feature extraction)
- ✅ Single CSV for training
- ✅ Fewer failure points
- ❌ Can't inspect features
- ❌ Can't do post-hoc analysis

---

## Recommended Improvements (Priority Order)

### 🔴 Critical (Do These)

#### 1. **Better Error Handling**
```python
# In data_loader.py
def read_gprmax_hdf5(filename: Path | str, fields=['E', 'H']) -> pd.DataFrame:
    filename = Path(filename)
    
    if not filename.exists():
        raise FileNotFoundError(f"GPR file not found: {filename}")
    
    try:
        with h5py.File(filename, 'r') as f:
            # Validate required attributes
            if 'dt' not in f.attrs or 'Iterations' not in f.attrs:
                raise ValueError(f"Missing required HDF5 attributes in {filename}")
            
            # ... rest of reading ...
    except Exception as e:
        raise OSError(f"Failed to read {filename.name}: {e}") from e
```

**Time:** 1 hour  
**Impact:** Catch bugs early, easier debugging

#### 2. **Add Progress Bars to File Operations**
```python
# In build_parquet.py
from tqdm import tqdm

for out_path in tqdm(out_files, desc="Processing", unit="file"):
    m = re.search(r"s_(\d+)\.out$", out_path.name)
    if not m: continue
    # ... same processing ...
```

**Time:** 30 minutes  
**Impact:** See progress, know it's not hanging

### 🟡 Important (Nice-to-Have)

#### 3. **Consistent Path Handling**
```python
from pathlib import Path

def ensure_path(p: Path | str) -> Path:
    """Convert any path to Path object."""
    return Path(p)

# Use throughout codebase
filename = ensure_path(filename)
assert filename.exists(), f"File not found: {filename}"
```

**Time:** 2 hours  
**Impact:** Cleaner code, fewer type errors

#### 4. **File Validation Function**
```python
def validate_gprmax_file(filepath: Path) -> bool:
    """Check that HDF5 file has required structure."""
    try:
        with h5py.File(filepath, 'r') as f:
            assert 'dt' in f.attrs, "Missing dt"
            assert 'Iterations' in f.attrs, "Missing Iterations"
            assert 'rxs' in f, "Missing rxs group"
            assert float(f.attrs['dt']) > 0, "Invalid dt"
            assert int(f.attrs['Iterations']) > 0, "Invalid iterations"
        return True
    except Exception as e:
        print(f"Invalid: {filepath}: {e}")
        return False

# Use in pipeline:
valid_files = [f for f in all_files if validate_gprmax_file(f)]
print(f"Valid: {len(valid_files)}/{len(all_files)}")
```

**Time:** 1 hour  
**Impact:** Catch corrupt files before processing

### 🟢 Optional (Polish)

#### 5. **Streaming for Large Datasets**
If you ever process > 1 GB datasets:
```python
def load_features_chunked(path, chunksize=5000):
    """Memory-efficient loading for large parquets."""
    parquet_file = pq.ParquetFile(path)
    for batch in parquet_file.iter_batches(batch_size=chunksize):
        yield batch.to_pandas()
```

**Time:** 2 hours  
**Impact:** Scales to any dataset size

#### 6. **Dataset Checksum Validation**
```python
import hashlib

def file_checksum(filepath):
    """SHA256 of file for integrity checking."""
    sha256 = hashlib.sha256()
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            sha256.update(chunk)
    return sha256.hexdigest()

# Save with metadata:
checksums = {f: file_checksum(f) for f in all_files}
pd.Series(checksums).to_csv('checksums.csv')

# Later, verify:
for f in all_files:
    if file_checksum(f) != checksums[f.name]:
        print(f"File {f} is corrupted!")
```

**Time:** 1 hour  
**Impact:** Detect corruption/tampering

---

## Quick Fixes (Easy Wins)

### Fix 1: Add Progress Bars (5 minutes)
```python
# Change:
for out_path in out_files:
    # ...

# To:
from tqdm import tqdm
for out_path in tqdm(out_files, desc="Processing"):
    # ...
```

### Fix 2: Raise Instead of Silent Return (30 minutes)
```python
# In data_loader.py, change all:
except FileNotFoundError:
    print("Error...")
    return pd.DataFrame()  # ← Bad

# To:
except FileNotFoundError as e:
    raise FileNotFoundError(f"File not found: {filename}") from e
```

### Fix 3: Validate Files Before Processing (1 hour)
```python
def check_dataset(directory):
    """Validate all .out files in directory."""
    files = list(Path(directory).glob('*.out'))
    bad_files = []
    
    for f in tqdm(files):
        try:
            with h5py.File(f, 'r') as hf:
                if 'dt' not in hf.attrs:
                    bad_files.append(f)
        except:
            bad_files.append(f)
    
    if bad_files:
        print(f"⚠️  Found {len(bad_files)} bad files:")
        for f in bad_files[:10]:
            print(f"  {f}")
    else:
        print(f"✅ All {len(files)} files valid")
```

---

## Summary

### Your Current Approach
✅ Multiple modules (good separation of concerns)  
✅ CONFIG persistence (clever for replication)  
❌ Silent errors (bad for debugging)  
❌ No progress tracking (no feedback)  
❌ Inconsistent path handling  
❌ No file validation  

### Landmine Classifier
✅ Simple pipeline (fewer failure points)  
✅ Direct waveforms (no feature engineering)  
✅ Clear error handling  
❌ Less flexible (can't analyze features)  
❌ Can't replicate configurations  

### Top 3 Changes to Make
1. **Add error checking** (raise exceptions, not silent returns)
2. **Add progress bars** (tqdm to all loops)
3. **Validate files** (check dt, Iterations, structure before processing)

**Total time:** 2-3 hours for high-impact fixes


# Migration Guide: Adopting the Data Access Layer

This guide provides instructions for migrating existing Synth-GPR code to use the new data access layer.

## Current Status

### ✅ Completed
1. **Data Access Layer Created**: `src/data_access/` module with:
   - `readers.py`: 8 reader classes (FileReader, MemoryReader, TOMLReader, HDF5Reader, INFileReader, DZTReader, JSONReader, NumpyReader)
   - `writers.py`: 8 writer classes (FileWriter, MemoryWriter, INFileWriter, PNGWriter, JSONWriter, ParquetWriter, NumpyWriter, TOMLWriter)
   - Comprehensive logging added to all operations

2. **Logging Added**: All readers and writers now log operations at INFO/DEBUG levels

3. **Examples Created**: Working examples in `src/data_access/examples/basic_usage.py`

4. **Scripts Migrated**: High-priority scripts have been migrated to use the data access layer:
   - ✅ `scripts/pipeline/generate_in_files.py` - Uses TOMLReader and PNGWriter
   - ✅ `scripts/visualization/visualize_ascan.py` - Uses DZTReader, NumpyReader, INFileReader, PNGWriter
   - ✅ `scripts/render_in_files.py` - Already using INFileReader and PNGWriter

### 📋 Remaining
- [ ] Update src modules to use the data access layer (optional)
- [ ] Migrate additional scripts as needed

---

## Why Migrate?

### Benefits
1. **Decoupling**: Business logic doesn't depend on file system
2. **Testability**: Easy to test with MemoryReader/MemoryWriter
3. **Extensibility**: Add new storage backends (S3, database) without changing business logic
4. **Consistency**: Uniform error handling and logging
5. **Maintainability**: Centralized data access logic

---

## Migration Strategy

### Approach 1: Gradual Migration (Recommended)
Migrate scripts one at a time, ensuring each works correctly before moving to the next.

### Approach 2: Big Bang
Migrate all scripts at once. Higher risk, but faster if you have good test coverage.

### Approach 3: Wrapper Pattern (Safest)
Create wrapper functions that use the new layer internally, so existing code doesn't need to change.

---

## Migration Examples

### Example 1: Reading TOML Config

**Before:**
```python
# In generate_in_files.py (line 419-420)
with open(path, "rb") as fh:
    return tomllib.load(fh)
```

**After:**
```python
from src.data_access import TOMLReader
# Use the reader
reader = TOMLReader()
return reader.read(path)
```

Or even simpler with dependency injection:
```python
from src.data_access import DataReader

def some_function(reader: DataReader):
    config = reader.read("config.toml")
    # ... process config
    
# Can use any reader!
some_function(TOMLReader())
some_function(MemoryReader({...}))  # For testing
```

---

### Example 2: Writing .in Files

**Before:**
```python
# In file_writer.py (line 255-256)
with open(output_path, 'w') as f:
    f.write(content)
```

**After:**
```python
from src.data_access import INFileWriter

writer = INFileWriter()
writer.write(output_path, content)
```

---

### Example 3: Reading .out Files

**Before:**
```python
# In data_loader.py (line 20, 79)
with h5py.File(filename, 'r') as f:
    dt = float(f.attrs['dt'])
    signal = rx_group[component][:]
```

**After:**
```python
from src.data_access import HDF5Reader

reader = HDF5Reader()
data = reader.read(filename, component=component)
signal = data['signal']
dt = data['dt']
```

---

### Example 4: Rendering PNG

**Before:**
```python
# In render.py (line 74)
fig.savefig(out_path, dpi=dpi, bbox_inches="tight")
```

**After:**
```python
from src.data_access import PNGWriter

writer = PNGWriter()
writer.write(out_path, fig, dpi=dpi)
```

---

## Files to Migrate

### High Priority (Most Used)
| File | Current I/O | Migration Complexity | Notes |
|------|-------------|---------------------|-------|
| `scripts/pipeline/generate_in_files.py` | TOML read, .in write | Medium | Core script for generating scenes |
| `scripts/visualization/visualize_ascan.py` | .out read, .DZT read, .png write | Medium | Primary visualization tool |
| `scripts/render_in_files.py` | .in read, .png write | Low | Batch rendering |

### Medium Priority
| File | Current I/O | Migration Complexity | Notes |
|------|-------------|---------------------|-------|
| `src/data_loader.py` | .out (HDF5) read | Low | Already used by HDF5Reader |
| `src/file_reader.py` | .in read | Low | Already used by INFileReader |
| `src/file_writer.py` | .in write | Medium | Core writing functionality |
| `src/dzt_io.py` | .DZT read | Low | Already used by DZTReader |
| `src/layer_spec.py` | TOML read | Low | Already used by TOMLReader |
| `src/visualization/render.py` | .in read, .png write | Low | Rendering |

### Low Priority (Can wait)
| File | Current I/O | Migration Complexity | Notes |
|------|-------------|---------------------|-------|
| `src/exporter.py` | JSON write | Low | Export functionality |
| `src/dataset_io.py` | .parquet read/write | Low | Dataset I/O |
| `src/layer_scene_builder.py` | .in write | Medium | Scene building |

---

## Step-by-Step Migration

### Step 1: Update Imports
Add the data access layer to the imports:
```python
from src.data_access import (
    TOMLReader, HDF5Reader, INFileReader, DZTReader,
    INFileWriter, PNGWriter, JSONWriter, ParquetWriter
)
```

### Step 2: Replace Direct File Access
For each file I/O operation, replace with the appropriate reader/writer.

### Step 3: Add Logging (Optional)
The data access layer already logs operations. Configure logging in your script:
```python
import logging
logging.basicConfig(level=logging.INFO)
```

### Step 4: Test
Test each migrated script to ensure it works correctly.

---

## Migration Checklist

- [x] `scripts/pipeline/generate_in_files.py` - ✅ Migrated (TOMLReader, PNGWriter)
- [x] `scripts/visualization/visualize_ascan.py` - ✅ Migrated (DZTReader, NumpyReader, INFileReader, PNGWriter)
- [x] `scripts/render_in_files.py` - ✅ Already using data access layer (INFileReader, PNGWriter)
- [ ] `src/data_loader.py` - Already used by HDF5Reader
- [ ] `src/file_reader.py` - Already used by INFileReader
- [ ] `src/file_writer.py` - Already used by INFileWriter
- [ ] `src/dzt_io.py` - Already used by DZTReader
- [ ] `src/layer_spec.py` - Already used by TOMLReader
- [ ] `src/visualization/render.py` - Used by PNGWriter
- [ ] `src/exporter.py` - Optional migration
- [ ] `src/dataset_io.py` - Optional migration
- [ ] `src/layer_scene_builder.py` - Optional migration

---

## Testing Migrated Code

### Unit Testing
```python
from src.data_access import MemoryReader, MemoryWriter

# Test with memory backend
shared = {}
writer = MemoryWriter(shared)
reader = MemoryReader(shared)

# Write and read
writer.write("test", {"data": 123})
assert reader.read("test") == {"data": 123}
```

### Integration Testing
```python
from src.data_access import FileReader, FileWriter

# Test with file backend
reader = FileReader()
writer = FileWriter()

# Read, process, write
config = reader.read("input.toml")
# ... process config
writer.write("output.in", processed_config)
```

---

## Common Patterns

### Pattern 1: Simple File I/O
```python
from src.data_access import FileReader, FileWriter

reader = FileReader()
writer = FileWriter()

# Read any file
config = reader.read("config.toml")

# Write any file
writer.write("output.in", content)
```

### Pattern 2: Specialized I/O
```python
from src.data_access import TOMLReader, INFileWriter

# Read TOML
config = TOMLReader().read("config.toml")

# Write .in
INFileWriter().write("scene.in", scene_content)
```

### Pattern 3: Protocol-Based (Most Flexible)
```python
from src.data_access import DataReader, DataWriter

def process_data(reader: DataReader, writer: DataWriter):
    data = reader.read("input")
    # Process data...
    writer.write("output", processed_data)

# Works with ANY backend!
process_data(TOMLReader(), INFileWriter())  # Files
process_data(MemoryReader(), MemoryWriter())  # Memory (testing)
```

---

## Troubleshooting

### Issue: Module Not Found
**Error:** `ModuleNotFoundError: No module named 'src.data_access'`

**Solution:** Ensure the project root is in your Python path:
```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
```

### Issue: Logging Not Showing
**Error:** No log messages appearing

**Solution:** Configure logging level:
```python
import logging
logging.basicConfig(level=logging.INFO)  # or DEBUG for more detail
```

### Issue: MemoryReader Not Finding Data
**Error:** `KeyError: "key" not found in memory data store`

**Solution:** Ensure reader and writer share the same data_store:
```python
shared = {}
writer = MemoryWriter(shared)
reader = MemoryReader(shared)  # Same shared dict!
```

---

## Best Practices

1. **Use Protocols for Type Hints**: Always use `DataReader` and `DataWriter` in function signatures
2. **Dependency Injection**: Pass readers/writers to functions rather than creating them inside
3. **Error Handling**: The data access layer already handles common errors; let them bubble up
4. **Logging**: Use the built-in logging; don't add redundant print statements
5. **Testing**: Use MemoryReader/MemoryWriter for fast unit tests
6. **Documentation**: Document which reader/writer each function expects

---

## Next Steps

1. Start with **high-priority scripts** (generate_in_files.py, visualize_ascan.py)
2. Test each migration thoroughly
3. Commit changes incrementally
4. Update documentation as you go

Would you like me to:
- [ ] Migrate a specific script as an example?
- [ ] Migrate all scripts in one go?
- [ ] Create additional examples?
- [ ] Add more specialized readers/writers?

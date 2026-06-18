# Data Access Layer

This module provides an abstraction layer for reading and writing data in Synth-GPR, decoupling the data operations from the underlying storage mechanism (file system, memory, database, etc.).

## Overview

The data access layer implements the **Repository Pattern** to separate business logic from data access concerns. This makes the codebase more maintainable, testable, and extensible.

### Key Benefits:

1. **Decoupling**: Business logic doesn't need to know if data comes from files, memory, or a database
2. **Testability**: Easy to mock readers/writers for unit testing
3. **Extensibility**: Add new storage backends (e.g., S3, database) without changing business logic
4. **Consistency**: Uniform interface across all data operations

## Architecture

```
┌─────────────────────┐
│   Business Logic     │  ← Uses abstract interfaces
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│   Data Access Layer  │  ← Implements concrete readers/writers
│  (readers.py,        │
│   writers.py)       │
└──────────┬──────────┘
           │
    ┌──────▼──────┬───────────┬───────────┐
    ▼              ▼           ▼           ▼
┌────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐
│ File   │  │ Memory  │  │ Database│  │  S3/     │
│ System │  │         │  │         │  │  Cloud  │
└────────┘  └─────────┘  └─────────┘  └─────────┘
```

## Usage

### Basic Usage

```python
# Import the data access layer
from src.data_access import FileReader, FileWriter, MemoryReader, MemoryWriter

# Reading from file
file_reader = FileReader()
config_data = file_reader.read("path/to/config.toml")

# Writing to file
file_writer = FileWriter()
file_writer.write("path/to/output.in", scene_data)

# Reading from memory
memory_reader = MemoryReader({"scene1": scene_data})
scene = memory_reader.read("scene1")

# Writing to memory
memory_writer = MemoryWriter()
memory_writer.write("scene2", scene_data)
retrieved = memory_writer.get_data("scene2")
```

### Specialized Readers

```python
from src.data_access import TOMLReader, HDF5Reader, DZTReader, INFileReader

# Read TOML config
.toml_reader = TOMLReader()
config = toml_reader.read("config.toml")

# Read gprMax output (HDF5)
.hdf5_reader = HDF5Reader()
simulation_data = hdf5_reader.read("simulation.out", component="Ez")

# Read DZT field data
dzt_reader = DZTReader()
field_data = dzt_reader.read("field_data.DZT", trace_idx=50)

# Read .in file
in_reader = INFileReader()
in_content = in_reader.read("scene.in")
in_metadata = in_reader.read_metadata("scene.in")
```

### Specialized Writers

```python
from src.data_access import INFileWriter, PNGWriter, JSONWriter, ParquetWriter

# Write .in file
in_writer = INFileWriter()
in_writer.write("output.in", scene_definition)

# Write PNG
png_writer = PNGWriter()
png_writer.write("output.png", figure, dpi=300)

# Write JSON
json_writer = JSONWriter()
json_writer.write("config.json", config_dict, indent=4)

# Write Parquet
df_writer = ParquetWriter()
df_writer.write("features.parquet", dataframe, compression="gzip")
```

## File Formats Supported

| Format | Reader | Writer | Description |
|--------|--------|--------|-------------|
| TOML | `TOMLReader` | `TOMLWriter` | Configuration files |
| .in | `INFileReader` | `INFileWriter` | gprMax input files |
| .out | `HDF5Reader` | - | gprMax HDF5 output |
| .DZT | `DZTReader` | - | GSSI field data |
| .png | - | `PNGWriter` | Image output |
| .json | `JSONReader` | `JSONWriter` | JSON data |
| .npy | `NumpyReader` | `NumpyWriter` | NumPy arrays |
| .parquet | - | `ParquetWriter` | Feature datasets |

## Migration Guide

### Before (Direct File Access)

```python
# Reading TOML
with open("config.toml", "rb") as f:
    config = tomllib.load(f)

# Writing .in
with open("output.in", "w") as f:
    f.write(content)

# Reading HDF5
with h5py.File("sim.out", "r") as f:
    signal = f['rxs/rx1/Ez'][:]
```

### After (Using Data Access Layer)

```python
from src.data_access import TOMLReader, HDF5Reader, INFileWriter

# Reading TOML
config = TOMLReader().read("config.toml")

# Writing .in
INFileWriter().write("output.in", content)

# Reading HDF5
sim_data = HDF5Reader().read("sim.out", component="Ez")
signal = sim_data['signal']
```

## Protocol-Based Design

The data access layer uses Python's Protocol typing to define interfaces:

```python
from src.data_access import DataReader, DataWriter

# Any class implementing the read() method satisfies DataReader
class CustomReader:
    def read(self, source, **kwargs) -> Any:
        # Custom implementation
        ...

# Can be used anywhere expecting a DataReader
reader: DataReader = CustomReader()
data = reader.read("source")
```

## Extending the Layer

### Adding a New Reader

```python
from src.data_access.readers import DataReader

class DatabaseReader(DataReader):
    def __init__(self, connection_string):
        self.connection = create_connection(connection_string)
    
    def read(self, table_name, **kwargs):
        query = kwargs.get('query', f'SELECT * FROM {table_name}')
        return self.connection.execute(query).fetchall()

# Register with FileReader
file_reader = FileReader()
file_reader._readers['.db'] = DatabaseReader(connection_string)
```

### Adding a New Writer

```python
from src.data_access.writers import DataWriter

class DatabaseWriter(DataWriter):
    def __init__(self, connection_string):
        self.connection = create_connection(connection_string)
    
    def write(self, table_name, data, **kwargs):
        # Insert data into database
        self.connection.insert(table_name, data)
        return table_name
```

## Testing with Memory Backend

```python
from src.data_access import MemoryReader, MemoryWriter

# Setup
writer = MemoryWriter()
reader = MemoryReader()

# Write test data
writer.write("test_scene", {"layers": ["layer1", "layer2"]})

# Read it back
assert reader.read("test_scene") == {"layers": ["layer1", "layer2"]}

# Works with any code expecting DataReader/DataWriter
from src.data_access import DataReader, DataWriter

def process_scene(reader: DataReader, writer: DataWriter):
    data = reader.read("scene_key")
    # Process data...
    writer.write("processed_scene", processed_data)

process_scene(MemoryReader(), MemoryWriter())
process_scene(FileReader(), FileWriter())  # Same interface!
```

## Error Handling

All readers and writers follow consistent error handling:

- **FileNotFoundError**: When source doesn't exist
- **ValueError**: When data format is invalid
- **TypeError**: When data type is wrong
- **IOError**: When write fails

## Dependencies

- Python 3.8+
- `tomllib` (stdlib) - TOML reading
- `tomli_w` (optional) - TOML writing
- `h5py` - HDF5 reading
- `numpy` - NumPy array handling
- `pandas` - Parquet I/O
- `matplotlib` - PNG rendering

## Best Practices

1. **Use the generic FileReader/FileWriter** when the file type is dynamic
2. **Use specialized readers/writers** when you know the exact file type
3. **Use MemoryReader/MemoryWriter** for testing or caching
4. **Type hints**: Use `DataReader` and `DataWriter` protocols for function parameters
5. **Dependency injection**: Pass readers/writers to functions rather than creating them inside

## Examples in the Codebase

### Generating a Scene

```python
from src.data_access import TOMLReader, INFileWriter
from src.layer_scene_builder import write_scene, SceneParams

# Read config
config = TOMLReader().read("scene_config.toml")

# Build scene
params = SceneParams(**config['sim'])
layers = config['layers']

# Write .in file
INFileWriter().write("scene.in", write_scene(layers, params))
```

### Processing Simulation Output

```python
from src.data_access import HDF5Reader, PNGWriter

# Read simulation
sim_data = HDF5Reader().read("simulation.out")
signal = sim_data['signal']
t_ns = sim_data['t_ns']

# Create plot
import matplotlib.pyplot as plt
fig, ax = plt.subplots()
ax.plot(t_ns, signal)

# Save plot
PNGWriter().write("signal_plot.png", fig)
```

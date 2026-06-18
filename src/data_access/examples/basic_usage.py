#!/usr/bin/env python3
"""
Basic usage examples for the Synth-GPR Data Access Layer.

This script demonstrates how to use the decoupled reading and writing operations.
"""

from pathlib import Path
import sys

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.data_access import (
    FileReader, FileWriter,
    MemoryReader, MemoryWriter,
    TOMLReader, HDF5Reader, INFileReader,
    INFileWriter, PNGWriter, JSONWriter,
)


def example_1_basic_file_io():
    """Example 1: Basic file reading and writing."""
    print("\n" + "="*70)
    print("Example 1: Basic File I/O")
    print("="*70)
    
    # Create a test TOML file
    test_toml = Path(__file__).parent / "test_config.toml"
    test_toml.write_text("""
[sim]
freq_hz = 1500000000
antenna_mode = "bistatic"

[[layer]]
name = "layer_1"
thickness = 0.05
eps = 3.0
sigma = 0.0
""")
    
    # Read using generic FileReader
    reader = FileReader()
    config = reader.read(test_toml)
    print(f"[OK] Read config from {test_toml.name}")
    print(f"  Layers: {len(config.get('layer', []))}")
    
    # Read using specialized TOMLReader
    toml_reader = TOMLReader()
    config2 = toml_reader.read(test_toml)
    print(f"[OK] Read config using TOMLReader")
    
    # Write JSON using JSONWriter
    json_writer = JSONWriter()
    output_json = Path(__file__).parent / "output_config.json"
    json_writer.write(output_json, config)
    print(f"[OK] Wrote JSON to {output_json.name}")
    
    # Cleanup
    test_toml.unlink(missing_ok=True)
    output_json.unlink(missing_ok=True)


def example_2_memory_operations():
    """Example 2: Memory-based operations for testing."""
    print("\n" + "="*70)
    print("Example 2: Memory Operations")
    print("="*70)
    
    # Create memory writer and reader with shared data store
    shared_store = {}
    memory_writer = MemoryWriter(shared_store)
    memory_reader = MemoryReader(shared_store)
    
    # Write to memory
    test_data = {"scene_id": "test_001", "layers": ["air", "subgrade", "ballast"]}
    key = memory_writer.write("scene_1", test_data)
    print(f"[OK] Wrote data to memory with key: {key}")
    print(f"  Shared store has {len(shared_store)} items")
    
    # Read from memory
    retrieved = memory_reader.read("scene_1")
    print(f"[OK] Read data from memory")
    print(f"  Data: {retrieved}")
    
    # Verify they're the same
    assert retrieved == test_data, "Data mismatch!"
    print("[OK] Data integrity verified")


def example_3_in_file_operations():
    """Example 3: Reading and writing .in files."""
    print("\n" + "="*70)
    print("Example 3: .in File Operations")
    print("="*70)
    
    # Create a simple .in file content
    in_content = """# Simple test scene
#domain: 0.6 1.1 0.0025
#dx_dy_dz: 0.0025 0.0025 0.0025
#time_window: 2e-08

#material: 3 0.0 1 0.0 layer_1
#material: 5 0.0 1 0.0 layer_2

#box: 0 0 0 0.6 0.05 0.0025 layer_1
#box: 0 0.05 0 0.6 0.1 0.0025 layer_2

#hertzian_dipole: z 0.3 0.75 0.00125 the_wave
#waveform: gaussian 1 1.5e+09 the_wave
#rx: 0.35 0.75 0.00125
"""
    
    # Write .in file
    in_writer = INFileWriter()
    in_file = Path(__file__).parent / "test_scene.in"
    in_writer.write(in_file, in_content)
    print(f"[OK] Wrote .in file to {in_file.name}")
    
    # Read .in file
    in_reader = INFileReader()
    content = in_reader.read(in_file)
    print(f"[OK] Read .in file content ({len(content)} chars)")
    
    # Read metadata
    metadata = in_reader.read_metadata(in_file)
    print(f"[OK] Read .in file metadata: {list(metadata.keys())}")
    
    # Render to PNG
    try:
        png_writer = PNGWriter()
        png_file = Path(__file__).parent / "test_scene.png"
        png_writer.write(png_file, in_file)
        print(f"[OK] Rendered to {png_file.name}")
        png_file.unlink(missing_ok=True)
    except Exception as e:
        print(f"[WARN] PNG rendering skipped: {e}")
    
    # Cleanup
    in_file.unlink(missing_ok=True)


def example_4_specialized_readers():
    """Example 4: Using specialized readers."""
    print("\n" + "="*70)
    print("Example 4: Specialized Readers")
    print("="*70)
    
    # Check if we have any .out files to read
    out_files = list(Path().rglob("*.out"))
    if out_files:
        out_file = out_files[0]
        print(f"Found .out file: {out_file.name}")
        
        # Read with HDF5Reader
        hdf5_reader = HDF5Reader()
        try:
            data = hdf5_reader.read(out_file)
            print(f"[OK] Read HDF5 .out file")
            print(f"  Signal length: {len(data['signal'])}")
            print(f"  Component: {data['component']}")
            if 'metadata' in data:
                print(f"  Has metadata: {bool(data['metadata'])}")
        except Exception as e:
            print(f"[WARN] Could not read .out file: {e}")
    else:
        print("[WARN] No .out files found for HDF5 reading example")
    
    # Check for .in files
    in_files = list(Path().rglob("10layer*.in"))
    if in_files:
        in_file = in_files[0]
        print(f"\nFound .in file: {in_file.name}")
        
        in_reader = INFileReader()
        lines = in_reader.read(in_file, as_lines=True)
        print(f"[OK] Read {len(lines)} lines from .in file")
        
        metadata = in_reader.read_metadata(in_file)
        print(f"[OK] Metadata keys: {list(metadata.keys())[:5]}...")


def example_5_protocol_based():
    """Example 5: Using protocols for dependency injection."""
    print("\n" + "="*70)
    print("Example 5: Protocol-Based Usage")
    print("="*70)
    
    from src.data_access import DataReader, DataWriter
    from typing import Union
    
    # Function that works with any reader/writer
    def process_config(reader: DataReader, writer: DataWriter, 
                      input_path: str, output_path: str) -> None:
        """Process config from any source to any destination."""
        config = reader.read(input_path)
        # Simulate processing
        config['processed'] = True
        writer.write(output_path, config)
    
    # Create test config
    test_config = {"freq": 1500000000, "layers": ["air", "subgrade"]}
    
    # Use Memory backend with shared data store
    shared_store = {}
    mem_writer = MemoryWriter(shared_store)
    mem_reader = MemoryReader(shared_store)
    
    mem_writer.write("input_config", test_config)
    process_config(mem_reader, mem_writer, "input_config", "output_config")
    
    result = mem_reader.read("output_config")
    print(f"[OK] Processed config with Memory backend")
    print(f"  Result: {result}")
    
    # Use File backend (would need actual files)
    # process_config(FileReader(), FileWriter(), "config.toml", "processed.toml")


def main():
    """Run all examples."""
    print("\n" + "="*70)
    print("Synth-GPR Data Access Layer - Examples")
    print("="*70)
    
    try:
        example_1_basic_file_io()
    except Exception as e:
        print(f"[FAIL] Example 1 failed: {e}")
    
    try:
        example_2_memory_operations()
    except Exception as e:
        print(f"[FAIL] Example 2 failed: {e}")
    
    try:
        example_3_in_file_operations()
    except Exception as e:
        print(f"[FAIL] Example 3 failed: {e}")
    
    try:
        example_4_specialized_readers()
    except Exception as e:
        print(f"[FAIL] Example 4 failed: {e}")
    
    try:
        example_5_protocol_based()
    except Exception as e:
        print(f"[FAIL] Example 5 failed: {e}")
    
    print("\n" + "="*70)
    print("Examples Complete!")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()

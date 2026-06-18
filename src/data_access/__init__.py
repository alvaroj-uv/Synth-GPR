"""
Data Access Layer for Synth-GPR.

Provides abstracted readers and writers that decouple data operations
from the underlying storage mechanism (file system, memory, database).

This module implements the Repository pattern to separate business logic
from data access concerns.

Usage:
    # Reading from file
    reader = FileReader()
    data = reader.read("path/to/file.toml")
    
    # Reading from memory
    memory_reader = MemoryReader(in_memory_data)
    data = memory_reader.read("key")
    
    # Writing to file
    writer = FileWriter()
    writer.write("path/to/output.in", data)
    
    # Writing to memory
    memory_writer = MemoryWriter()
    memory_writer.write("key", data)
"""

from .readers import (
    DataReader,
    FileReader,
    MemoryReader,
    TOMLReader,
    HDF5Reader,
    INFileReader,
    DZTReader,
)
from .writers import (
    DataWriter,
    FileWriter,
    MemoryWriter,
    INFileWriter,
    PNGWriter,
    JSONWriter,
    ParquetWriter,
)

__all__ = [
    # Readers
    'DataReader',
    'FileReader', 
    'MemoryReader',
    'TOMLReader',
    'HDF5Reader',
    'INFileReader',
    'DZTReader',
    # Writers
    'DataWriter',
    'FileWriter',
    'MemoryWriter',
    'INFileWriter',
    'PNGWriter',
    'JSONWriter',
    'ParquetWriter',
]

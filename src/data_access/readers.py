"""
Data Readers - Abstracted reading operations for Synth-GPR.

Each reader implements the DataReader protocol and can read from
different sources (files, memory, databases) without the calling code
needing to know the implementation details.
"""

import abc
import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional, Union, Protocol, runtime_checkable

import h5py
import numpy as np
import tomllib

# Logger for data access operations
logger = logging.getLogger(__name__)


@runtime_checkable
class DataReader(Protocol):
    """Protocol defining the interface for all data readers."""
    
    @abc.abstractmethod
    def read(self, source: Union[str, Path], **kwargs) -> Any:
        """
        Read data from the given source.
        
        Args:
            source: Identifier for the data source (file path, key, URL, etc.)
            **kwargs: Additional reader-specific parameters
            
        Returns:
            The read data (structure depends on reader type)
        """
        pass


class FileReader(DataReader):
    """
    Generic file reader that delegates to specialized readers based on file extension.
    
    Supports: .toml, .in, .out, .DZT, .dzt, .json, .npy
    """
    
    def __init__(self):
        self._readers = {
            '.toml': TOMLReader(),
            '.in': INFileReader(),
            '.out': HDF5Reader(),
            '.DZT': DZTReader(),
            '.dzt': DZTReader(),
            '.json': JSONReader(),
            '.npy': NumpyReader(),
        }
    
    def read(self, source: Union[str, Path], **kwargs) -> Any:
        """Read from file based on extension."""
        path = Path(source)
        extension = path.suffix.lower()
        
        logger.debug(f"FileReader.read: source={source}, extension={extension}")
        
        if extension not in self._readers:
            # Try to determine from content or use generic
            if extension in ['', '.txt']:
                # Read as text
                logger.info(f"Reading text file: {path}")
                return path.read_text(encoding='utf-8')
            else:
                logger.error(f"Unsupported file extension: {extension}")
                raise ValueError(f"Unsupported file extension: {extension}")
        
        reader = self._readers[extension]
        logger.debug(f"Delegating to {reader.__class__.__name__}")
        return reader.read(source, **kwargs)


class MemoryReader(DataReader):
    """Read from in-memory data structures."""
    
    def __init__(self, data_store: Optional[Dict[str, Any]] = None):
        """
        Initialize with an optional data store dictionary.
        
        Args:
            data_store: Dictionary containing in-memory data
        """
        self.data_store = data_store if data_store is not None else {}
    
    def read(self, key: str, **kwargs) -> Any:
        """
        Read data from memory by key.
        
        Args:
            key: Key to look up in the data store
            **kwargs: Additional parameters (ignored)
            
        Returns:
            The data associated with the key
            
        Raises:
            KeyError: If key not found
        """
        logger.debug(f"MemoryReader.read: key={key}")
        if key not in self.data_store:
            logger.error(f"Key '{key}' not found in memory data store")
            raise KeyError(f"Key '{key}' not found in memory data store")
        logger.debug(f"MemoryReader.read: found key '{key}'")
        return self.data_store[key]
    
    def add_data(self, key: str, data: Any) -> None:
        """Add data to the memory store."""
        self.data_store[key] = data


# ============================================================================
# SPECIALIZED FILE READERS
# ============================================================================

class TOMLReader(DataReader):
    """Read TOML configuration files."""
    
    def read(self, source: Union[str, Path], **kwargs) -> Dict[str, Any]:
        """
        Read and parse a TOML file.
        
        Args:
            source: Path to .toml file
            **kwargs: Additional parameters (ignored)
            
        Returns:
            Dictionary containing the parsed TOML data
        """
        path = Path(source)
        logger.info(f"Reading TOML file: {path}")
        with open(path, "rb") as fh:
            data = tomllib.load(fh)
        logger.debug(f"TOML file loaded: {len(data)} top-level keys")
        return data


class INFileReader(DataReader):
    """Read gprMax .in input files."""
    
    def read(self, source: Union[str, Path], **kwargs) -> str:
        """
        Read a gprMax .in file as text.
        
        Args:
            source: Path to .in file
            **kwargs:
                - as_lines: If True, return list of lines (default: False)
            
        Returns:
            File content as string or list of lines
        """
        path = Path(source)
        as_lines = kwargs.get('as_lines', False)
        
        logger.info(f"Reading .in file: {path}")
        content = path.read_text(encoding='utf-8', errors='replace')
        if as_lines:
            logger.debug(f".in file has {len(content.splitlines())} lines")
            return content.splitlines()
        logger.debug(f".in file size: {len(content)} bytes")
        return content
    
    def read_metadata(self, source: Union[str, Path]) -> Dict[str, Any]:
        """
        Read metadata comments from .in file header.
        
        Args:
            source: Path to .in file
            
        Returns:
            Dictionary of metadata key-value pairs
        """
        import json
        from src.file_reader import parse_metadata_file
        return parse_metadata_file(Path(source))


class HDF5Reader(DataReader):
    """Read gprMax .out files (HDF5 format)."""
    
    def read(self, source: Union[str, Path], **kwargs) -> Dict[str, Any]:
        """
        Read a gprMax HDF5 .out file.
        
        Args:
            source: Path to .out file
            **kwargs:
                - component: Field component to extract (default: 'Ez')
                - include_metadata: Include file metadata (default: True)
            
        Returns:
            Dictionary containing signal, dt, t_ns, metadata, etc.
        """
        from src.data_loader import read_ascan
        
        component = kwargs.get('component', 'Ez')
        path = Path(source)
        logger.info(f"Reading HDF5 .out file: {path} (component={component})")
        
        data = read_ascan(path, component)
        
        # Flatten the result for easier access
        result = {
            'signal': data['signal'],
            'dt': data['dt'],
            't_ns': data['t_ns'],
            'iterations': data['iterations'],
            'rx_pos': data['rx_pos'],
            'ascan_idx': data['ascan_idx'],
            'component': data['component'],
            'available_components': data['available'],
        }
        
        logger.debug(f"HDF5 data loaded: signal length={len(result['signal'])}, dt={result['dt']}")
        
        # Add metadata from .in file if available
        in_path = path.with_suffix('.in')
        if in_path.exists():
            from src.file_reader import parse_metadata_file
            result['metadata'] = parse_metadata_file(in_path)
            logger.debug(f"Loaded metadata from companion .in file")
        
        return result
    
    def read_raw(self, source: Union[str, Path]) -> h5py.File:
        """
        Get raw HDF5 file handle for direct access.
        
        Args:
            source: Path to .out file
            
        Returns:
            Open HDF5 file object (caller must close)
        """
        return h5py.File(source, 'r')


class DZTReader(DataReader):
    """Read GSSI DZT field data files."""
    
    def read(self, source: Union[str, Path], **kwargs) -> Dict[str, Any]:
        """
        Read a DZT file.
        
        Args:
            source: Path to .DZT or .dzt file
            **kwargs:
                - trace_idx: Trace index to extract (default: 50)
                - channel: Channel index (default: 0)
            
        Returns:
            Dictionary containing trace data and metadata
        """
        from src.dzt_io import read_dzt_trace, get_dzt_metadata
        
        trace_idx = kwargs.get('trace_idx', 50)
        channel = kwargs.get('channel', 0)
        
        path = Path(source)
        logger.info(f"Reading DZT file: {path} (trace_idx={trace_idx}, channel={channel})")
        
        signal, dt_ns, metadata = read_dzt_trace(path, trace_idx)
        
        logger.debug(f"DZT trace loaded: signal length={len(signal)}, dt_ns={dt_ns}")
        
        return {
            'signal': signal,
            'dt_ns': dt_ns,
            'metadata': metadata,
            'trace_idx': trace_idx,
            'channel': channel,
        }
    
    def read_metadata(self, source: Union[str, Path]) -> Dict[str, Any]:
        """Read DZT file metadata without loading full data."""
        from src.dzt_io import get_dzt_metadata
        return get_dzt_metadata(Path(source))
    
    def read_traces(self, source: Union[str, Path], **kwargs) -> np.ndarray:
        """
        Read all traces from DZT file.
        
        Args:
            source: Path to .DZT or .dzt file
            **kwargs: See read_dzt_traces
            
        Returns:
            2D numpy array of traces
        """
        from src.dzt_io import read_dzt_traces
        traces, metadata = read_dzt_traces(Path(source), **kwargs)
        return traces


class JSONReader(DataReader):
    """Read JSON files."""
    
    def read(self, source: Union[str, Path], **kwargs) -> Dict[str, Any]:
        """Read and parse a JSON file."""
        path = Path(source)
        logger.info(f"Reading JSON file: {path}")
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        logger.debug(f"JSON loaded: {len(data)} top-level keys")
        return data


class NumpyReader(DataReader):
    """Read NumPy .npy files."""
    
    def read(self, source: Union[str, Path], **kwargs) -> np.ndarray:
        """Load a NumPy array from .npy file."""
        path = Path(source)
        logger.info(f"Reading NumPy file: {path}")
        data = np.load(source)
        logger.debug(f"NumPy array loaded: shape={data.shape}, dtype={data.dtype}")
        return data

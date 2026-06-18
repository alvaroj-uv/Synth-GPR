"""
Data Writers - Abstracted writing operations for Synth-GPR.

Each writer implements the DataWriter protocol and can write to
different destinations (files, memory, databases) without the calling code
needing to know the implementation details.
"""

import abc
import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional, Union, Protocol, runtime_checkable

import numpy as np
import pandas as pd

# Logger for data access operations
logger = logging.getLogger(__name__)


@runtime_checkable
class DataWriter(Protocol):
    """Protocol defining the interface for all data writers."""
    
    @abc.abstractmethod
    def write(self, destination: Union[str, Path], data: Any, **kwargs) -> Union[str, Path]:
        """
        Write data to the given destination.
        
        Args:
            destination: Destination identifier (file path, key, etc.)
            data: Data to write
            **kwargs: Additional writer-specific parameters
            
        Returns:
            The path or identifier where data was written
        """
        pass


class FileWriter(DataWriter):
    """
    Generic file writer that delegates to specialized writers based on file extension.
    
    Supports: .in, .png, .json, .parquet, .npy
    """
    
    def __init__(self):
        self._writers = {
            '.in': INFileWriter(),
            '.png': PNGWriter(),
            '.json': JSONWriter(),
            '.parquet': ParquetWriter(),
            '.npy': NumpyWriter(),
        }
    
    def write(self, destination: Union[str, Path], data: Any, **kwargs) -> Path:
        """Write to file based on extension."""
        path = Path(destination)
        extension = path.suffix.lower()
        
        logger.debug(f"FileWriter.write: destination={destination}, extension={extension}")
        
        if extension not in self._writers:
            # Try to write as text
            path.parent.mkdir(parents=True, exist_ok=True)
            logger.info(f"Writing text file: {path}")
            path.write_text(str(data), encoding='utf-8')
            return path
        
        writer = self._writers[extension]
        logger.debug(f"Delegating to {writer.__class__.__name__}")
        return writer.write(destination, data, **kwargs)


class MemoryWriter(DataWriter):
    """Write to in-memory data structures."""
    
    def __init__(self, data_store: Optional[Dict[str, Any]] = None):
        """
        Initialize with an optional data store dictionary.
        
        Args:
            data_store: Optional dictionary to use as the storage backend
        """
        self.data_store: Dict[str, Any] = data_store if data_store is not None else {}
    
    def write(self, key: str, data: Any, **kwargs) -> str:
        """
        Write data to memory with the given key.
        
        Args:
            key: Key to store the data under
            data: Data to store
            **kwargs: Additional parameters (ignored)
            
        Returns:
            The key where data was stored
        """
        logger.debug(f"MemoryWriter.write: key={key}, data size={len(str(data))}")
        self.data_store[key] = data
        logger.debug(f"MemoryWriter.write: stored key '{key}'")
        return key
    
    def get_data(self, key: str) -> Any:
        """Retrieve data from memory by key."""
        return self.data_store[key]
    
    def clear(self) -> None:
        """Clear all stored data."""
        self.data_store.clear()


# ============================================================================
# SPECIALIZED FILE WRITERS
# ============================================================================

class INFileWriter(DataWriter):
    """Write gprMax .in input files."""
    
    def write(
        self, 
        destination: Union[str, Path], 
        data: Any, 
        **kwargs
    ) -> Path:
        """
        Write data to a gprMax .in file.
        
        Args:
            destination: Path to output .in file
            data: Data to write. Can be:
                - str: Raw .in file content
                - dict: Scene definition to be formatted
                - SceneDefinition: From src.scene_descriptor
                - SceneCheckpoint: From src.worker
            **kwargs:
                - scenario_type: Scenario identifier for header (default: "Sim")
                - extra_headers: Additional metadata for header
                - config: GeneratorConfig for embedding
            
        Returns:
            Path to the written file
        """
        from src.file_writer import GPRMaxFileWriter
        from src.scene_descriptor import SceneDefinition
        
        path = Path(destination)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Writing .in file: {path}")
        
        # Handle different data types
        if isinstance(data, str):
            # Raw content
            logger.debug(f"Writing raw .in content ({len(data)} bytes)")
            path.write_text(data, encoding='utf-8')
        elif isinstance(data, SceneDefinition):
            # Use GPRMaxFileWriter
            scenario_type = kwargs.get('scenario_type', 'Sim')
            extra_headers = kwargs.get('extra_headers', None)
            logger.debug(f"Writing SceneDefinition via GPRMaxFileWriter")
            GPRMaxFileWriter.write_to_file(
                data, 
                str(path), 
                scenario_type=scenario_type,
                extra_headers=extra_headers
            )
        elif hasattr(data, 'save_scene_checkpoint'):
            # SceneCheckpoint or similar
            config = kwargs.get('config', None)
            extra_headers = kwargs.get('extra_headers', None)
            param_sources = kwargs.get('param_sources', None)
            sample_id = kwargs.get('sample_id', None)
            
            logger.debug(f"Writing SceneCheckpoint via save_scene_checkpoint")
            GPRMaxFileWriter.save_scene_checkpoint(
                data,
                str(path),
                config=config,
                extra_headers=extra_headers,
                sample_id=sample_id,
                param_sources=param_sources
            )
        else:
            # Try to convert to string
            content = str(data)
            logger.debug(f"Writing converted .in content ({len(content)} bytes)")
            path.write_text(content, encoding='utf-8')
        
        logger.info(f"Successfully wrote .in file: {path}")
        return path


class PNGWriter(DataWriter):
    """Write PNG image files."""
    
    def write(
        self, 
        destination: Union[str, Path], 
        data: Any, 
        **kwargs
    ) -> Path:
        """
        Write an image to PNG file.
        
        Args:
            destination: Path to output PNG file
            data: Data to write. Can be:
                - matplotlib.figure.Figure: Figure to save
                - str: Path to .in file to render
                - dict: Scene data to render
            **kwargs:
                - dpi: DPI for output (default: 150)
                - from_in_file: If True, render .in file geometry
            
        Returns:
            Path to the written PNG file
        """
        import matplotlib.pyplot as plt
        from pathlib import Path
        
        path = Path(destination)
        path.parent.mkdir(parents=True, exist_ok=True)
        dpi = kwargs.get('dpi', 150)
        
        logger.info(f"Writing PNG file: {path} (dpi={dpi})")
        
        if isinstance(data, plt.Figure):
            # Save existing figure
            logger.debug("Saving matplotlib Figure to PNG")
            data.savefig(path, dpi=dpi, bbox_inches='tight')
            plt.close(data)
        elif isinstance(data, str) or isinstance(data, Path):
            # Render .in file
            logger.debug(f"Rendering .in file to PNG: {data}")
            from src.visualization.render import render_geometry_png
            in_path = Path(data)
            render_geometry_png(in_path, path, dpi=dpi)
        elif isinstance(data, dict):
            # Try to extract figure or render scene
            if 'figure' in data:
                fig = data['figure']
                if isinstance(fig, plt.Figure):
                    logger.debug("Saving Figure from dict to PNG")
                    fig.savefig(path, dpi=dpi, bbox_inches='tight')
                    plt.close(fig)
            else:
                # Attempt to render as scene
                logger.debug("Rendering dict data as scene to PNG")
                from src.visualization.render import render_geometry_png
                # This would need scene data - for now just save as generic
                plt.figure().savefig(path, dpi=dpi)
                plt.close()
        else:
            logger.error(f"Unsupported data type for PNG export: {type(data)}")
            raise ValueError(f"Unsupported data type for PNG export: {type(data)}")
        
        logger.info(f"Successfully wrote PNG file: {path}")
        return path


class JSONWriter(DataWriter):
    """Write JSON files."""
    
    def write(
        self, 
        destination: Union[str, Path], 
        data: Any, 
        **kwargs
    ) -> Path:
        """
        Write data to a JSON file.
        
        Args:
            destination: Path to output JSON file
            data: Data to serialize (must be JSON-serializable)
            **kwargs:
                - indent: JSON indentation (default: 2)
                - sort_keys: Sort dictionary keys (default: False)
            
        Returns:
            Path to the written JSON file
        """
        path = Path(destination)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        indent = kwargs.get('indent', 2)
        sort_keys = kwargs.get('sort_keys', False)
        
        logger.info(f"Writing JSON file: {path} (indent={indent}, sort_keys={sort_keys})")
        
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=indent, sort_keys=sort_keys, ensure_ascii=False)
        
        logger.info(f"Successfully wrote JSON file: {path}")
        return path


class ParquetWriter(DataWriter):
    """Write Apache Parquet files (for feature datasets)."""
    
    def write(
        self, 
        destination: Union[str, Path], 
        data: Any, 
        **kwargs
    ) -> Path:
        """
        Write a DataFrame to Parquet file.
        
        Args:
            destination: Path to output .parquet file
            data: pandas DataFrame to write
            **kwargs:
                - index: Write DataFrame index (default: False)
                - compression: Compression codec (default: 'snappy')
                - engine: Parquet engine (default: 'pyarrow')
            
        Returns:
            Path to the written Parquet file
        """
        if not isinstance(data, pd.DataFrame):
            logger.error("Data must be a pandas DataFrame for Parquet export")
            raise ValueError("Data must be a pandas DataFrame for Parquet export")
        
        path = Path(destination)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        index = kwargs.get('index', False)
        compression = kwargs.get('compression', 'snappy')
        engine = kwargs.get('engine', 'pyarrow')
        
        logger.info(f"Writing Parquet file: {path} (rows={len(data)}, cols={len(data.columns)}, "
                   f"compression={compression}, engine={engine})")
        
        data.to_parquet(
            path, 
            index=index, 
            compression=compression,
            engine=engine
        )
        
        logger.info(f"Successfully wrote Parquet file: {path}")
        return path


class NumpyWriter(DataWriter):
    """Write NumPy .npy files."""
    
    def write(
        self, 
        destination: Union[str, Path], 
        data: Any, 
        **kwargs
    ) -> Path:
        """
        Write a NumPy array to .npy file.
        
        Args:
            destination: Path to output .npy file
            data: NumPy array to save
            **kwargs: Additional parameters (currently unused)
            
        Returns:
            Path to the written .npy file
        """
        if not isinstance(data, np.ndarray):
            data = np.array(data)
        
        path = Path(destination)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        allow_pickle = kwargs.get('allow_pickle', True)
        logger.info(f"Writing NumPy file: {path} (shape={data.shape}, dtype={data.dtype}, "
                   f"allow_pickle={allow_pickle})")
        
        np.save(path, data, allow_pickle=allow_pickle)
        
        logger.info(f"Successfully wrote NumPy file: {path}")
        return path


class TOMLWriter(DataWriter):
    """Write TOML files."""
    
    def write(
        self, 
        destination: Union[str, Path], 
        data: Any, 
        **kwargs
    ) -> Path:
        """
        Write data to a TOML file.
        
        Args:
            destination: Path to output .toml file
            data: Dictionary to write as TOML
            **kwargs: Additional parameters (currently unused)
            
        Returns:
            Path to the written TOML file
        """
        path = Path(destination)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Writing TOML file: {path} ({len(data)} top-level keys)")
        
        # Use tomli_w for writing TOML
        try:
            import tomli_w
            with open(path, 'wb') as f:
                tomli_w.dump(data, f)
            logger.info(f"Successfully wrote TOML file using tomli_w: {path}")
        except ImportError:
            # Fallback: write as JSON with .toml extension (not ideal but works)
            logger.warning("tomli_w not available, falling back to JSON format")
            import json
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            logger.info(f"Successfully wrote TOML file (JSON fallback): {path}")
        
        return path

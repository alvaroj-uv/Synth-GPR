"""
DZT file I/O using readgssi library.

Provides unified interface for reading GSSI DZT files and extracting traces
to parquet format with full sample preservation (no downsampling).

All traces are read as raw (unnormalized) 16-bit signed integers with full
time window (typically 22,652 samples at 0.1 ns intervals).
"""

import logging
from pathlib import Path
from typing import Dict, Tuple, List, Optional, Any
import numpy as np
import pandas as pd
from readgssi.dzt import readdzt
from readgssi.gps import readdzg
from .logging_config import get_logger


def get_dzt_metadata(dzt_path: Path) -> Dict[str, Any]:
    """
    Extract metadata from a DZT file without loading full data.

    Args:
        dzt_path: Path to the DZT file

    Returns:
        Dictionary with:
        - 'antenna_name': str (e.g., '400MHz')
        - 'antenna_freq': float (Hz, e.g., 400e6 for 400 MHz)
        - 'num_traces': int (number of scans/waves)
        - 'samples_per_trace': int (nsamp)
        - 'bits_per_sample': int (8, 16, or 32)
        - 'sampling_rate': float (Hz, derived from Nyquist)
        - 'time_window_ns': float (nanoseconds)
        - 'system': str (e.g., 'SIR 3000')
        - 'channels': int (number of channels)
    """
    header, _, _ = readdzt(str(dzt_path), verbose=False)

    sampling_rate = header['samp_freq']  # Hz, from readgssi calculation
    time_window_ns = (header['dzt_depth'] * 2) / (header['cr_true']) * 1e9  # ns

    return {
        'antenna_name': header['rh_antname'][0] if header['rh_antname'][0] else 'Unknown',
        'antenna_freq': header['antfreq'][0],  # Hz
        'num_traces': header['shape'][1],  # number of scans
        'samples_per_trace': header['rh_nsamp'],
        'bits_per_sample': header['rh_bits'],
        'sampling_rate': sampling_rate,
        'time_window_ns': time_window_ns,
        'system': header['rh_system'],
        'channels': header['rh_nchan'],
        'epsr': header['rhf_epsr'],  # relative permittivity used
        'depth_m': header['dzt_depth'],
    }


def read_dzt_traces(dzt_path: Path, channel: int = 0,
                   start_trace: int = 0, num_traces: Optional[int] = None) -> Tuple[np.ndarray, Dict[str, Any]]:
    """
    Read traces from a DZT file (raw data, no normalization).
    Simple binary parsing without dependency on readgssi reshape logic.

    Args:
        dzt_path: Path to the DZT file
        channel: Channel index (default 0)
        start_trace: Start trace index (default 0)
        num_traces: Number of traces to read; None = all

    Returns:
        Tuple of:
        - traces: numpy array of shape (num_traces, samples_per_trace), dtype float64
        - metadata: dictionary with file metadata (antenna, samples, etc.)
    """
    import struct

    dzt_path = Path(dzt_path)

    with open(dzt_path, 'rb') as f:
        # Read 1024-byte header
        header = f.read(1024)

        # Extract key header fields (GSSI DZT format)
        # Offsets from working extract_dzt_correct.py
        rh_nsamp = struct.unpack('<H', header[8:10])[0]  # samples per A-scan (offset 8)
        ntraces = struct.unpack('<H', header[18:20])[0]  # number of records/scans (offset 18)

        # Assume 16-bit signed samples (standard GSSI)
        dtype = np.int16
        bytes_per_sample = 2
        rh_bits = 16
        rh_nchan = 1  # Assume single channel unless proven otherwise

        # Verify file size
        file_size = dzt_path.stat().st_size
        data_size = file_size - 1024
        expected_data_size = ntraces * rh_nsamp * bytes_per_sample

        if abs(expected_data_size - data_size) > 100:
            # Size mismatch - recalculate
            ntraces = data_size // (rh_nsamp * bytes_per_sample)

        # Read all traces
        f.seek(1024)
        traces_list = []

        for trace_idx in range(ntraces):
            # Read one trace
            trace_data = f.read(rh_nsamp * bytes_per_sample)

            if len(trace_data) < rh_nsamp * bytes_per_sample:
                break

            # Unpack as signed 16-bit integers
            samples = struct.unpack(f'<{rh_nsamp}h', trace_data)
            traces_list.append(np.array(samples, dtype=np.float64))

        # Convert to 2D array (ntraces, rh_nsamp)
        traces = np.array(traces_list) if traces_list else np.array([])

        # Select subset if requested
        if start_trace > 0 or num_traces is not None:
            end_trace = start_trace + (num_traces if num_traces else traces.shape[0])
            traces = traces[start_trace:end_trace, :]

    metadata = {
        'antenna_name': 'Unknown',
        'antenna_freq': 400e6,  # Default to 400 MHz
        'samples_per_trace': rh_nsamp,
        'num_traces_in_file': ntraces,
        'bits_per_sample': rh_bits,
        'time_window_ns': rh_nsamp * 0.1,
        'sample_interval_ns': 0.1,
    }

    return traces, metadata


def read_multiple_dzt_files(dzt_files: List[Path], channel: int = 0) -> Tuple[np.ndarray, List[Dict[str, Any]]]:
    """
    Read traces from multiple DZT files.

    Args:
        dzt_files: List of paths to DZT files
        channel: Channel index (default 0)

    Returns:
        Tuple of:
        - traces: numpy array of all traces concatenated, shape (total_traces, samples_per_trace)
        - metadatas: list of metadata dicts, one per file
    """
    all_traces = []
    all_metadatas = []

    for dzt_file in dzt_files:
        traces, metadata = read_dzt_traces(Path(dzt_file), channel=channel)
        all_traces.append(traces)
        all_metadatas.append(metadata)

    combined_traces = np.vstack(all_traces)
    return combined_traces, all_metadatas


def extract_traces_to_parquet(dzt_files: List[Path], output_path: Path,
                             channel: int = 0, verbose: bool = True) -> None:
    """
    Extract traces from DZT files and save as parquet with full samples.

    Each row = one trace (wave)
    Each column = one Ez sample (or metadata)

    Args:
        dzt_files: List of paths to DZT files
        output_path: Output .parquet file path
        channel: Channel index (default 0)
        verbose: Print progress (default True)
    """
    logger = get_logger(__name__)
    dzt_files = sorted([Path(f) for f in dzt_files])

    if verbose:
        logger.info(f"Extracting {len(dzt_files)} DZT files to parquet (FULL SAMPLES)")
        logger.info("=" * 70)

    all_traces = []
    all_metadata = []
    trace_count = 0

    for file_idx, dzt_file in enumerate(dzt_files):
        if verbose:
            logger.info(f"[{file_idx+1}/{len(dzt_files)}] {dzt_file.name}")

        traces, metadata = read_dzt_traces(dzt_file, channel=channel)
        nsamp = metadata['samples_per_trace']

        if verbose:
            logger.info(f"      Traces: {len(traces)}, Samples/trace: {nsamp}")

        # Convert to DataFrame rows
        for trace_idx, trace in enumerate(traces):
            row = {f'sample_{i}': trace[i] for i in range(nsamp)}
            row['file'] = dzt_file.stem
            row['trace_idx'] = trace_idx
            row['peak_amplitude'] = np.max(np.abs(trace))
            row['rms'] = np.sqrt(np.mean(trace**2))

            all_traces.append(row)
            trace_count += 1

        if verbose and (file_idx + 1) % max(1, len(dzt_files) // 5) == 0:
            logger.info(f"      Progress: {trace_count} traces extracted")

    # Create DataFrame
    if verbose:
        logger.info("=" * 70)
        logger.info("Creating DataFrame and saving parquet...")

    df = pd.DataFrame(all_traces)

    logger.info(f"DataFrame shape: {df.shape}")
    logger.info(f"  Rows (traces): {len(df)}")
    logger.info(f"  Columns: {len(df.columns)}")
    logger.info(f"    - Sample columns: {nsamp}")
    logger.info(f"    - Metadata: 4 (file, trace_idx, peak_amplitude, rms)")

    # Data statistics
    peaks = df['peak_amplitude']
    logger.info(f"Data Statistics:")
    logger.info(f"  Peak amplitudes: {peaks.min():.2e} to {peaks.max():.2e}")
    logger.info(f"  Peak std dev: {peaks.std():.2e}")
    logger.info(f"  Peak variation: {peaks.std()/peaks.mean()*100:.1f}%")

    # Save parquet
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    df.to_parquet(output_path, index=False, engine='pyarrow', compression='snappy')

    if verbose:
        logger.info(f"Saved: {output_path}")
        logger.info(f"File size: {output_path.stat().st_size / 1e9:.3f} GB")

        logger.info("=" * 70)
        logger.info(f"SUCCESS: Created parquet with {len(df)} traces × {nsamp} full samples")
        logger.info(f"This retains 100% of original signal (no information loss)")
        logger.info(f"Time window: {nsamp * 0.1:.1f} ns ({nsamp * 0.1 / 1000:.2f} μs)")
        logger.info("=" * 70)

    return df

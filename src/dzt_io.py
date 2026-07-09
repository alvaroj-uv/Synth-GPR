"""
DZT file I/O using readgssi library.

Provides unified interface for reading GSSI DZT files and extracting traces
to parquet format with full sample preservation (no downsampling).

Puerto-Limache GSSI format (confirmed by file-size verification):
  - Header:          128 KiB  (131072 bytes)
  - Sample dtype:    int32    (4 bytes/sample)
  - Samples/trace:   512      (indices 0-1 are marker artefacts — dropped)
  - Usable samples:  510
  - dt:              50/511 ns ≈ 0.0978 ns
  - Time window:     ~49.8 ns
"""

import logging
from pathlib import Path
from typing import Dict, Tuple, List, Optional, Any
import numpy as np
import pandas as pd
from readgssi.dzt import readdzt
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


# Puerto-Limache GSSI DZT constants (confirmed via file-size arithmetic)
_DZT_HEADER_BYTES = 128 * 1024   # 131072 bytes
_DZT_NSAMP_RAW   = 512           # samples per raw trace (indices 0-1 are markers)
_DZT_DT_NS       = 50.0 / 511    # ≈ 0.0978 ns  (50 ns window / 511 intervals)


def read_dzt_traces(dzt_path: Path, channel: int = 0,
                    start_trace: int = 0, num_traces: Optional[int] = None) -> Tuple[np.ndarray, Dict[str, Any]]:
    """
    Read traces from a DZT file (raw data, no normalization).

    Format: 128 KiB header + int32 samples (4 bytes each).
    The first two samples of every trace are GSSI marker artefacts and are
    dropped automatically — the returned array has 510 usable samples per trace.

    Args:
        dzt_path:    Path to the DZT file
        channel:     Ignored (reserved for multi-channel files)
        start_trace: First trace index to return (default 0)
        num_traces:  How many traces to return; None = all

    Returns:
        - traces:   float64 array  (n_traces, 510)
        - metadata: dict with 'samples_per_trace', 'sample_interval_ns', etc.
    """
    import struct

    dzt_path = Path(dzt_path)
    file_size = dzt_path.stat().st_size
    data_bytes = file_size - _DZT_HEADER_BYTES

    with open(dzt_path, 'rb') as f:
        # Peek at offset 8 in the header for rh_nsamp (standard GSSI 1 KiB layout)
        header_peek = f.read(16)
        rh_nsamp_hdr = struct.unpack('<H', header_peek[8:10])[0]
        rh_nsamp = rh_nsamp_hdr if 32 < rh_nsamp_hdr <= 4096 else _DZT_NSAMP_RAW

        bytes_per_sample = 4  # int32
        total_traces = data_bytes // (rh_nsamp * bytes_per_sample)

        # Clamp the requested range
        if num_traces is None:
            end_trace = total_traces
        else:
            end_trace = min(start_trace + num_traces, total_traces)
        n_read = max(0, end_trace - start_trace)

        # Jump directly to the first requested trace — no loop overhead
        f.seek(_DZT_HEADER_BYTES + start_trace * rh_nsamp * bytes_per_sample)
        raw = np.frombuffer(f.read(n_read * rh_nsamp * bytes_per_sample), dtype=np.int32)

    traces = raw.reshape(n_read, rh_nsamp).astype(np.float64)
    # Drop GSSI marker artefacts at indices 0-1
    traces = traces[:, 2:]
    n_samples = traces.shape[1]  # 510

    metadata = {
        'antenna_name': 'Unknown',
        'antenna_freq': 400e6,
        'samples_per_trace': n_samples,
        'samples_raw': rh_nsamp,
        'num_traces_in_file': total_traces,
        'bits_per_sample': 32,
        'sample_interval_ns': _DZT_DT_NS,
        'time_window_ns': n_samples * _DZT_DT_NS,
    }

    return traces, metadata


def read_gain_curve(dzt_path: Path) -> Optional[np.ndarray]:
    """Read the GSSI range-gain breakpoints (dB) from a DZT header, or None.

    Standard GSSI RFH layout (confirmed on the Puerto-Limache files: rh_tag=255
    @0, rh_nsamp=512 @4, rh_bits=32 @6): the range gain is described by
      rh_rgain  (ushort @ offset 40) = byte offset to the range-gain block,
      rh_nrgain (ushort @ offset 42) = its size in BYTES.
    The block stores the time-varying gain the operator applied during
    acquisition. If that gain was baked into the stored samples, it biases every
    envelope / sigma / attenuation observable, so :func:`remove_gain` can divide
    it back out.

    Returns:
        1-D np.ndarray of gain breakpoints in dB (evenly spaced across the trace
        window), or None if the header declares no range gain, or the block does
        not decode to a plausible float dB curve.

    NOTE — Puerto-Limache EFE DZTs expose rh_rgain=8192, rh_nrgain=5: a tiny,
    non-float-aligned block that does NOT decode as a dB curve, so this returns
    None for them. In that case the stored samples' gain state is UNKNOWN and
    must not be assumed physical for sigma calibration (see memory
    'AGC Breaks Matching' / project sigma work).
    """
    import struct

    dzt_path = Path(dzt_path)
    logger = get_logger(__name__)
    with open(dzt_path, "rb") as f:
        hdr = f.read(64)
        if len(hdr) < 44:
            return None
        rh_rgain = struct.unpack("<H", hdr[40:42])[0]
        rh_nrgain = struct.unpack("<H", hdr[42:44])[0]
        if rh_rgain == 0 or rh_nrgain == 0:
            logger.info("read_gain_curve: no range gain declared (rh_nrgain=0).")
            return None
        if rh_nrgain % 4 != 0 or not (4 <= rh_nrgain <= 256):
            logger.info(
                "read_gain_curve: range-gain block rh_rgain=%d rh_nrgain=%d is "
                "not a decodable float32 dB curve -> treating gain as ABSENT/"
                "unknown.", rh_rgain, rh_nrgain)
            return None
        f.seek(rh_rgain)
        blob = f.read(rh_nrgain)

    curve = np.frombuffer(blob, dtype="<f4").astype(float)
    if (not np.all(np.isfinite(curve))) or curve.min() < -20.0 or curve.max() > 200.0:
        logger.info("read_gain_curve: decoded values out of plausible dB range "
                    "-> treating gain as ABSENT/unknown.")
        return None
    return curve


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
        dt_ns = _DZT_DT_NS
        logger.info(f"SUCCESS: Created parquet with {len(df)} traces × {nsamp} usable samples")
        logger.info(f"This retains 100% of original signal (no information loss)")
        logger.info(f"Time window: {nsamp * dt_ns:.1f} ns  (dt={dt_ns:.4f} ns)")
        logger.info("=" * 70)

    return df


# ── EFE archive lifecycle: stitch DZTs -> HDF5, AGC variant ──────────────────
# Moved from scripts/visualization/unified_visualizer.py (2026-07-02, debt D12:
# processing does not belong in the visualizer). The visualizer re-exports both
# names so its CLI and existing imports keep working.

def stitch_dzt_files(
    dzt_paths: list,
    out_h5: Path,
) -> dict:
    """Concatenate multiple DZT files into a single HDF5 archive.

    Reads every DZT file in *dzt_paths* (must be provided in spatial order),
    stacks all raw traces into one array, and saves to *out_h5* with segment
    metadata stored as HDF5 attributes and a companion dataset.

    The filename convention ``PKC<km_start>_PKF<km_end>`` is used to derive
    approximate metric positions for each trace.

    Args:
        dzt_paths: Ordered list of Path objects pointing to DZT files.
        out_h5:    Output HDF5 path (created or overwritten).

    Returns:
        dict with keys ``n_traces``, ``n_samples``, ``dt_ns``, ``segments``.

    Output HDF5 layout::

        /traces        float32 (n_total, n_samples) - raw ADC counts
        /pk_m          float32 (n_total,)           - km position in metres
        /segment_idx   int32   (n_total,)           - which DZT file (0-based)
        /segments      str     dataset              - DZT filenames in order
        attrs: dt_ns, n_traces, n_samples, created

    Example::

        paths = sorted(Path('D:/Codigo/Data').glob('*.DZT'))
        stitch_dzt_files(paths, Path('output/efe_full.h5'))
    """
    import re
    from datetime import datetime

    import h5py

    logger = get_logger(__name__)

    def _parse_pk(name: str):
        """Extract (pk_start_m, pk_end_m) from filename, or (None, None)."""
        m = re.search(r'PKC(\d+)_(\d+).*PKF(\d+)_(\d+)', name, re.IGNORECASE)
        if not m:
            return None, None
        km_start = int(m.group(1)) + int(m.group(2)) / 1000.0
        km_end   = int(m.group(3)) + int(m.group(4)) / 1000.0
        return km_start * 1e3, km_end * 1e3   # metres

    # ── First pass: collect metadata ─────────────────────────────────────────
    segments_meta = []
    dt_ns_ref = None
    n_samples_ref = None
    total_traces = 0

    for seg_idx, dzt_path in enumerate(dzt_paths):
        logger.info(f'Reading segment {seg_idx}: {dzt_path.name}')
        bscan, meta = read_dzt_traces(dzt_path)
        dt_ns = meta['sample_interval_ns']
        n_tr, n_samp = bscan.shape

        if dt_ns_ref is None:
            dt_ns_ref = dt_ns
            n_samples_ref = n_samp
        else:
            if abs(dt_ns - dt_ns_ref) > 1e-6:
                logger.warning(f'dt mismatch: {dzt_path.name} dt={dt_ns} vs {dt_ns_ref}')
            if n_samp != n_samples_ref:
                logger.warning(f'sample count mismatch: {dzt_path.name} {n_samp} vs {n_samples_ref}')

        pk_start_m, pk_end_m = _parse_pk(dzt_path.name)
        segments_meta.append({
            'name':       dzt_path.name,
            'seg_idx':    seg_idx,
            'n_traces':   n_tr,
            'trace_start': total_traces,
            'trace_end':   total_traces + n_tr,
            'pk_start_m':  pk_start_m,
            'pk_end_m':    pk_end_m,
            'bscan':       bscan,
        })
        total_traces += n_tr
        logger.info(f'  {n_tr} traces, pk {pk_start_m}-{pk_end_m} m')

    # ── Concatenate ──────────────────────────────────────────────────────────
    logger.info(f'Concatenating {total_traces} traces x {n_samples_ref} samples ...')
    all_traces   = np.empty((total_traces, n_samples_ref), dtype=np.float32)
    all_pk_m     = np.empty(total_traces, dtype=np.float32)
    all_seg_idx  = np.empty(total_traces, dtype=np.int32)

    for seg in segments_meta:
        s, e = seg['trace_start'], seg['trace_end']
        all_traces[s:e] = seg['bscan'].astype(np.float32)
        all_seg_idx[s:e] = seg['seg_idx']
        # interpolate pk positions linearly within segment
        if seg['pk_start_m'] is not None:
            all_pk_m[s:e] = np.linspace(seg['pk_start_m'], seg['pk_end_m'],
                                         seg['n_traces'], dtype=np.float32)
        else:
            all_pk_m[s:e] = np.arange(seg['n_traces'], dtype=np.float32)
        del seg['bscan']   # free memory

    # ── Write HDF5 ───────────────────────────────────────────────────────────
    out_h5 = Path(out_h5)
    out_h5.parent.mkdir(parents=True, exist_ok=True)
    logger.info(f'Writing HDF5: {out_h5}')

    seg_names = [s['name'] for s in segments_meta]
    with h5py.File(out_h5, 'w') as f:
        f.create_dataset('traces',      data=all_traces,   compression='gzip',
                         compression_opts=4, chunks=(512, n_samples_ref))
        f.create_dataset('pk_m',        data=all_pk_m,     compression='gzip')
        f.create_dataset('segment_idx', data=all_seg_idx,  compression='gzip')
        dt = h5py.special_dtype(vlen=str)
        ds = f.create_dataset('segments', (len(seg_names),), dtype=dt)
        ds[:] = seg_names
        f.attrs['dt_ns']      = float(dt_ns_ref)
        f.attrs['n_traces']   = total_traces
        f.attrs['n_samples']  = n_samples_ref
        f.attrs['created']    = datetime.now().isoformat()

    size_mb = out_h5.stat().st_size / 1e6
    logger.info(f'Saved {out_h5} ({size_mb:.1f} MB)')

    return {
        'n_traces':  total_traces,
        'n_samples': n_samples_ref,
        'dt_ns':     dt_ns_ref,
        'segments':  segments_meta,
    }


def apply_agc_to_h5(
    in_h5: Path,
    out_h5: Path,
    window_ns: float = 5.0,
    noise_gate: float = 1e-3,
    chunk_traces: int = 4000,
) -> None:
    """Apply Automatic Gain Control to every trace in an HDF5 B-scan archive.

    Reads the HDF5 produced by :func:`stitch_dzt_files`, applies AGC to each
    trace, and writes a new HDF5 with the same structure.  All non-trace
    datasets and attributes are copied verbatim; an ``agc_window_ns`` attribute
    is added to document the processing.

    WARNING (memory: AGC breaks matching): AGC output is DISPLAY-ONLY. Never
    match/stack/invert on AGC'd traces - the per-trace nonlinear gain destroys
    coda coherence (0.99 raw vs 0.02 AGC trace-to-trace r).

    AGC algorithm: each sample is divided by the RMS of its local time window::

        rms[i] = sqrt( mean( x[i-w : i+w]^2 ) )
        x_agc[i] = x[i] / max(rms[i], noise_gate)

    This equalises amplitude across depth so that deep interfaces (ballast base,
    subgrade) are as bright as the near-surface direct wave.

    Args:
        in_h5:        Path to the input HDF5 (output of stitch_dzt_files).
        out_h5:       Path for the AGC-corrected output HDF5.
        window_ns:    Half-length of the AGC sliding window in ns (default 5 ns,
                      roughly two 400 MHz wavelengths).
        noise_gate:   Minimum RMS value; prevents division by noise (default 1e-3).
        chunk_traces: Number of traces processed per iteration (memory budget).
    """
    import h5py

    from .bscan_processing import agc_bscan

    logger = get_logger(__name__)

    out_h5 = Path(out_h5)
    out_h5.parent.mkdir(parents=True, exist_ok=True)

    with h5py.File(in_h5, 'r') as fin, h5py.File(out_h5, 'w') as fout:
        dt_ns    = float(fin.attrs['dt_ns'])
        n_tr     = int(fin.attrs['n_traces'])
        n_samp   = int(fin.attrs['n_samples'])
        half_win = max(1, int(round(window_ns / dt_ns)))
        win_size = 2 * half_win + 1

        logger.info(
            f'AGC: {n_tr:,} traces, window={window_ns} ns '
            f'({win_size} samples), noise_gate={noise_gate}'
        )

        # ── Create output trace dataset ──────────────────────────────────────
        ds_out = fout.create_dataset(
            'traces', shape=(n_tr, n_samp), dtype=np.float32,
            compression='gzip', compression_opts=4,
            chunks=(min(512, n_tr), n_samp),
        )

        # ── Process in chunks using agc_bscan() ──────────────────────────────
        n_chunks = (n_tr + chunk_traces - 1) // chunk_traces
        for k in range(n_chunks):
            s = k * chunk_traces
            e = min(n_tr, s + chunk_traces)
            chunk = fin['traces'][s:e].astype(np.float32)   # (C, n_samp)
            chunk_agc = agc_bscan(chunk, dt_ns * 1e-9,
                                  window_ns=window_ns,
                                  noise_gate=noise_gate).astype(np.float32)
            ds_out[s:e] = chunk_agc
            if (k + 1) % 10 == 0 or k == n_chunks - 1:
                logger.info(f'  chunk {k+1}/{n_chunks}  ({e:,}/{n_tr:,} traces)')

        # ── Copy ancillary datasets and attributes verbatim ──────────────────
        for key in ('pk_m', 'segment_idx', 'segments'):
            if key in fin:
                fin.copy(key, fout)

        for attr_key, attr_val in fin.attrs.items():
            fout.attrs[attr_key] = attr_val
        fout.attrs['agc_applied']   = True
        fout.attrs['agc_window_ns'] = window_ns
        fout.attrs['agc_noise_gate'] = noise_gate

    size_mb = out_h5.stat().st_size / 1e6
    logger.info(f'AGC file saved -> {out_h5}  ({size_mb:.1f} MB)')

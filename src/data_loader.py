import logging
import os
import glob
import h5py
import numpy as np
import pandas as pd
from scipy.signal import hilbert
from src.signal_processing import preprocess_signal
from .logging_config import get_logger

logger = get_logger(__name__)

def read_gprmax_hdf5(filename, fields=None):
    """
    Read a gprMax HDF5 .out file into a DataFrame.

    Args:
        filename: Path to .out file.
        fields: List of component name prefixes to include. Matching is by
            *prefix*, so 'E' returns Ex+Ey+Ez, while 'Ez' returns only Ez.
            Examples:
              fields=['Ez']        → only Ez (recommended for z-dipole source)
              fields=['Ez', 'Hz']  → Ez and Hz
              fields=['E', 'H']    → all six components (default)
            Default: ['E', 'H'] (all components).

    Returns:
        DataFrame with columns ['Time', 'rx1_Ez', ...]. Time is in seconds.
        Returns empty DataFrame on file error.
    """
    if fields is None:
        fields = ['E', 'H']

    try:
        f = h5py.File(filename, 'r')
    except FileNotFoundError:
        logger.error(f"File {filename} not found.")
        return pd.DataFrame()
    except OSError:
        logger.error(f"Could not open file {filename}. It might be corrupted or not an HDF5 file.")
        return pd.DataFrame()

    if 'dt' not in f.attrs:
        f.close()
        raise ValueError(
            f"{filename}: HDF5 file has no 'dt' attribute — cannot determine "
            f"the time step. A silently-wrong default here previously mis-scaled "
            f"every downstream frequency feature by ~3.2x (the historic dt bug); "
            f"dt is now mandatory, read from the source, never assumed."
        )
    dt = float(f.attrs['dt'])
    iterations = f.attrs.get('Iterations', 0)
    time = np.arange(iterations) * dt
    data = {'Time': time}

    if 'rxs' in f:
        rxs_group = f['rxs']
        for rx_name in rxs_group:
            rx_group = rxs_group[rx_name]
            for dataset_name in rx_group:
                if any(dataset_name.startswith(field) for field in fields):
                    data[f"{rx_name}_{dataset_name}"] = np.array(rx_group[dataset_name])

    f.close()
    return pd.DataFrame(data)

def read_ascan(filename, component='Ez'):
    """
    Read a single A-scan trace plus timing/position metadata from a gprMax .out file.

    Shared low-level reader for the A-scan visualizers. For stepped-source
    (B-scan) outputs the middle trace is returned and ``ascan_idx`` is set to
    that trace index; otherwise ``ascan_idx`` is None.

    Args:
        filename: Path to the gprMax HDF5 .out file.
        component: Requested field component (e.g. 'Ez'). Falls back to 'Ez'
            then the first available component if the request is absent.

    Returns:
        dict with keys: signal, dt, iterations, t_ns (ns), component (resolved),
        available (list), rx_pos, ascan_idx.
    """
    with h5py.File(filename, 'r') as f:
        dt = float(f.attrs['dt'])
        iterations = int(f.attrs['Iterations'])
        rx_group = f['rxs/rx1']
        available = list(rx_group.keys())

        if component not in available:
            component = 'Ez' if 'Ez' in available else available[0]

        signal = rx_group[component][:]
        rx_pos = rx_group.attrs.get('Position', [None, None, None])

    # B-scan data is 2D (n_time, n_traces) when the source is stepped; pick the
    # middle trace as a representative A-scan for 1D plotting/FFT.
    ascan_idx = None
    if signal.ndim == 2:
        ascan_idx = signal.shape[1] // 2
        signal = signal[:, ascan_idx]

    t_ns = np.arange(iterations) * dt * 1e9

    return {
        'signal': signal,
        'dt': dt,
        'iterations': iterations,
        't_ns': t_ns,
        'component': component,
        'available': available,
        'rx_pos': rx_pos,
        'ascan_idx': ascan_idx,
    }

def read_rx_traces(filename, rx=None, fields=('Ex', 'Ey', 'Ez', 'Hx', 'Hy', 'Hz')):
    """
    Read every requested field-component trace for one receiver from a .out file.

    Use this when the caller must choose among components (e.g. picking the
    dominant-energy trace) rather than a single fixed component.

    Args:
        filename: Path to the gprMax HDF5 .out file.
        rx: Receiver group name (e.g. 'rx1'). Defaults to the first receiver.
        fields: Component names to read if present.

    Returns:
        (traces, dt): traces is a dict {component: 1-D np.array} preserving the
        order of ``fields``; dt is the time step in seconds.
    """
    with h5py.File(filename, 'r') as f:
        dt = float(f.attrs['dt'])
        rxs = f['rxs']
        rx_name = rx if rx is not None else list(rxs.keys())[0]
        rx_group = rxs[rx_name]
        traces = {c: rx_group[c][:] for c in fields if c in rx_group}
    return traces, dt

def write_rx_out(filename, traces, dt, position=(0.0, 0.0, 0.0),
                 title='Synthetic', gprmax='fake'):
    """
    Write a gprMax-style .out HDF5 file for a single receiver.

    Inverse of ``read_rx_traces`` / ``read_ascan`` — centralizes the on-disk
    layout (root attrs ``dt``/``Iterations`` + ``rxs/rx1`` group carrying
    ``Position`` and one dataset per field component). Used to synthesize test
    data so scripts never hand-roll the HDF5 structure.

    Args:
        filename: Output .out path.
        traces: dict {component: 1-D array}; all share length == Iterations.
        dt: Time step in seconds.
        position: Receiver (x, y, z).
        title, gprmax: Root attribute strings.
    """
    traces = {c: np.asarray(v) for c, v in traces.items()}
    if not traces:
        raise ValueError("traces must contain at least one component")
    iterations = len(next(iter(traces.values())))

    with h5py.File(filename, 'w') as f:
        f.attrs['dt'] = dt
        f.attrs['Iterations'] = iterations
        f.attrs['Title'] = title
        f.attrs['gprMax'] = gprmax

        rx = f.create_group('rxs/rx1')
        rx.attrs['Name'] = 'rx1'
        rx.attrs['Position'] = np.asarray(position, dtype=float)
        for comp, arr in traces.items():
            rx.create_dataset(comp, data=arr)

def load_batch_dataset(input_dir, field='Ez'):
    """
    Loads all .out files in input_dir and extracts signals.
    Returns dictionaries of stacked arrays for Raw, Treated, Analytical, and Fourier.
    """
    files = glob.glob(os.path.join(input_dir, '*.out'))
    if not files:
        logger.warning(f"No .out files found in {input_dir}")
        return None

    logger.info(f"Found {len(files)} files. Loading data...")

    raw_signals = []
    treated_signals = []
    analytical_signals = []
    fourier_spectra = []
    
    dt = None  # only ever used if every file in input_dir fails to load
    common_time = None
    common_freqs = None
    
    for filepath in files:
        try:
            df = read_gprmax_hdf5(filepath, fields=[field])
            if df.empty: continue
            
            # Find the column
            cols = [c for c in df.columns if c.endswith(f"_{field}")]
            if not cols: continue
            col_name = cols[0]
            
            raw = df[col_name].values
            
            if 'Time' in df.columns:
                time = df['Time'].values
                if len(time) > 1:
                    dt = time[1] - time[0]
                if common_time is None:
                    common_time = time
            
            # Preprocess
            treated, _ = preprocess_signal(raw, dt)
            
            # Analytical
            analytic = np.abs(hilbert(treated))
            
            # Fourier
            fft_vals = np.abs(np.fft.fft(treated))
            freqs = np.fft.fftfreq(len(treated), d=dt)
            pos_mask = freqs >= 0
            spectrum = fft_vals[pos_mask]
            valid_freqs = freqs[pos_mask]
            
            if common_freqs is None:
                common_freqs = valid_freqs

            # Ensure lengths match (simple check)
            if common_time is not None and len(raw) == len(common_time):
                raw_signals.append(raw)
            
            treated_signals.append(treated)
            analytical_signals.append(analytic)
            fourier_spectra.append(spectrum)
            
        except Exception as e:
            logger.error(f"Error processing {filepath}: {e}")

    return {
        'raw': raw_signals,
        'treated': treated_signals,
        'analytical': analytical_signals,
        'fourier': fourier_spectra,
        'time': common_time,
        'freqs': common_freqs,
        'dt': dt
    }

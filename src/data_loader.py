import os
import glob
import h5py
import numpy as np
import pandas as pd
from scipy.signal import hilbert
from src.signal_processing import preprocess_signal

def read_gprmax_hdf5(filename, fields=['E', 'H']):
    """
    Reads gprMax HDF5 output file.
    Returns a DataFrame with time and field components.
    """
    try:
        f = h5py.File(filename, 'r')
    except FileNotFoundError:
        print(f"Error: File {filename} not found.")
        return pd.DataFrame()
    except OSError:
        print(f"Error: Could not open file {filename}. It might be corrupted or not an HDF5 file.")
        return pd.DataFrame()

    # Extract Time
    # Usually 'rxs/rx1/Ez' has attributes 'dt'
    # Or root attributes
    dt = f.attrs.get('dt', 1e-10)
    iterations = f.attrs.get('Iterations', 0)
    
    # Create Time Array
    time = np.arange(iterations) * dt
    
    data = {'Time': time}
    
    # Iterate through receivers and fields
    # Structure: rxs -> rx1 -> Ez
    if 'rxs' in f:
        rxs_group = f['rxs']
        for rx_name in rxs_group:
            rx_group = rxs_group[rx_name]
            for dataset_name in rx_group:
                # Check if dataset name starts with any of the requested fields
                # e.g. 'Ez' starts with 'E'
                if any(dataset_name.startswith(field) for field in fields):
                    # Read dataset
                    dataset = rx_group[dataset_name]
                    signal = np.array(dataset)
                    
                    # Store in dictionary
                    col_name = f"{rx_name}_{dataset_name}"
                    data[col_name] = signal
                    
    f.close()
    
    df = pd.DataFrame(data)
    return df

def load_batch_dataset(input_dir, field='Ez'):
    """
    Loads all .out files in input_dir and extracts signals.
    Returns dictionaries of stacked arrays for Raw, Treated, Analytical, and Fourier.
    """
    files = glob.glob(os.path.join(input_dir, '*.out'))
    if not files:
        print(f"No .out files found in {input_dir}")
        return None

    print(f"Found {len(files)} files. Loading data...")

    raw_signals = []
    treated_signals = []
    analytical_signals = []
    fourier_spectra = []
    
    dt = 1e-10 # Default
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
            print(f"Error processing {filepath}: {e}")

    return {
        'raw': raw_signals,
        'treated': treated_signals,
        'analytical': analytical_signals,
        'fourier': fourier_spectra,
        'time': common_time,
        'freqs': common_freqs,
        'dt': dt
    }

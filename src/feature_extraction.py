# Third-party imports
import numpy as np
import pandas as pd
from scipy.signal import hilbert, stft, resample
from scipy.stats import skew, kurtosis

# Local imports
from src.constants import PC, SC
from src.signal_processing import calculate_instantaneous_attributes

def extract_features(df, dt=PC.DEFAULT_DT):
    """
    Extracts advanced time-domain, frequency-domain, and time-frequency features from GPR traces.
    
    Refactored for SRP: logic delegated to specialized helper functions.
    """
    if df.empty:
        print("DataFrame is empty. Cannot extract features.")
        return pd.DataFrame()

    features_list = []
    
    # Identify metadata columns
    metadata_cols = [col for col in df.columns if col in ['gprMax', 'Title', 'Iterations', 'nx_ny_nz', 'dx_dy_dz', 'dt', 'srcsteps', 'rxsteps', 'nsrc', 'nrx']]
    metadata_values = {col: df[col].iloc[0] for col in metadata_cols}
    
    for col in df.columns:
        if col == 'Time' or col in metadata_cols:
            continue
            
        signal = df[col].values
        
        # 1. Time Domain Stats
        time_feats = _extract_time_stats(signal)
        
        # 2. Hilbert Transform (Envelope) Stats
        hilbert_feats, analytic_signal = _extract_hilbert_stats(signal, dt)
        
        # 3. Frequency Domain
        freq_feats = _extract_frequency_features(signal, dt)
        
        # 4. STFT (Time-Frequency)
        stft_feats = _extract_stft_features(signal, dt)
        
        # 5. Slice Statistics
        slice_feats = _extract_slice_features(signal)
        
        # 6. Grid Features
        grid_feats = _extract_grid_features(signal, analytic_signal)
        
        # Combine
        features = {
            'Signal': col,
            **time_feats,
            **hilbert_feats,
            **freq_feats,
            **stft_feats,
            **slice_feats,
            **grid_feats
        }
        
        # Add metadata
        features.update(metadata_values)
        features_list.append(features)

    return pd.DataFrame(features_list)

def _extract_time_stats(signal: np.ndarray) -> dict:
    """Calculates basic statistical moments and quantiles."""
    from scipy.signal import find_peaks
    
    mean_val = np.mean(signal)
    rms_val = np.sqrt(np.mean(signal**2))
    
    # Peak Analysis (Namdari et al. 2025)
    # Using height threshold to ignore low-level noise
    peaks, properties = find_peaks(signal, height=np.std(signal)*0.5)
    peak_heights = properties['peak_heights']
    num_peaks = len(peaks)
    mean_peak_height = np.mean(peak_heights) if num_peaks > 0 else 0
    
    stats = {
        'mean': mean_val,
        'root_mean_square': rms_val,
        'standard_deviation': np.std(signal),
        'median': np.median(signal),
        'skewness': skew(signal),
        'kurtosis_value': kurtosis(signal),
        'percentile_25': np.percentile(signal, 25),
        'percentile_50': np.percentile(signal, 50),
        'percentile_75': np.percentile(signal, 75),
        'peak_max': np.max(signal),
        'peak_min': np.min(signal),
        'peak_count': num_peaks,
        'peak_mean_height': mean_peak_height,
        'crest_factor': (np.max(signal) / rms_val) if rms_val != 0 else 0,
        'number_zeros': len(np.where(np.diff(np.signbit(signal)))[0]),
        'area_signal': np.sum(np.abs(signal)),
        'second_derivative': len(np.where(np.diff(np.signbit(np.diff(signal, n=2))))[0])
    }
    
    # Deciles
    deciles = np.percentile(signal, np.arange(10, 100, 10))
    stats.update({f'decile_{i+1}0': d for i, d in enumerate(deciles)})
    
    return stats


def _extract_hilbert_stats(signal: np.ndarray, dt: float) -> tuple:
    """Calculates statistics on the signal envelope and returns analytic signal."""
    attrs = calculate_instantaneous_attributes(signal, dt, use_mirroring=True)
    envelope = attrs['envelope']
    analytic_signal = envelope * np.exp(1j * attrs['phase'])
    
    mean_val = np.mean(envelope)
    rms_val = np.sqrt(np.mean(envelope**2))
    
    stats = {
        'hilbert_mean': mean_val,
        'hilbert_root_mean_square': rms_val,
        'hilbert_standard_deviation': np.std(envelope),
        'hilbert_median': np.median(envelope),
        'hilbert_skewness': skew(envelope),
        'hilbert_kurtosis': kurtosis(envelope),
        'hilbert_percentile_25': np.percentile(envelope, 25),
        'hilbert_percentile_50': np.percentile(envelope, 50),
        'hilbert_percentile_75': np.percentile(envelope, 75),
        'hilbert_peak_max': np.max(envelope),
        'hilbert_peak_min': np.min(envelope),
        'hilbert_crest_factor': (np.max(envelope) / rms_val) if rms_val != 0 else 0,
        'area_hilbert': np.sum(envelope)
    }
    
    deciles = np.percentile(envelope, np.arange(10, 100, 10))
    stats.update({f'hilbert_decile_{i+1}0': d for i, d in enumerate(deciles)})
    
    return stats, analytic_signal

def _extract_frequency_features(signal: np.ndarray, dt: float) -> dict:
    """Calculates Fourier transform metrics."""
    fft_vals = np.fft.fft(signal)
    fft_spectrum = np.abs(fft_vals)
    freqs = np.fft.fftfreq(len(signal), d=dt)
    
    pos_mask = freqs >= 0
    fft_spectrum = fft_spectrum[pos_mask]
    freqs = freqs[pos_mask]
    
    area_fourier = np.sum(fft_spectrum)
    max_power = np.max(fft_spectrum)
    
    # Heuristics
    if area_fourier > 0:
        mean_freq = np.sum(freqs * fft_spectrum) / area_fourier
        cumulative = np.cumsum(fft_spectrum)
        median_idx = np.searchsorted(cumulative, area_fourier / 2)
        median_freq = freqs[min(median_idx, len(freqs)-1)]
    else:
        mean_freq, median_freq = 0, 0

    # Bandwidth
    threshold = max_power / np.sqrt(2)
    bw_mask = fft_spectrum >= threshold
    bandwidth = (freqs[bw_mask][-1] - freqs[bw_mask][0]) if np.any(bw_mask) else 0

    # Spectral Entropy & Flatness
    psd = fft_spectrum**2 / len(signal)
    psd_norm = psd / np.sum(psd) if np.sum(psd) > 0 else psd
    spectral_entropy = -np.sum(psd_norm * np.log(psd_norm + SC.LOG_EPSILON))
    
    g_mean = np.exp(np.mean(np.log(fft_spectrum + SC.LOG_EPSILON)))
    a_mean = np.mean(fft_spectrum)
    flatness = (g_mean / a_mean) if a_mean > 0 else 0
    
    return {
        'area_fourier': area_fourier,
        'fourier_peak_max': max_power,
        'fourier_standard_deviation': np.std(fft_spectrum),
        'dominant_frequency': freqs[np.argmax(fft_spectrum)],
        'bandwidth': bandwidth,
        'mean_frequency': mean_freq,
        'median_frequency': median_freq,
        'spectral_entropy': spectral_entropy,
        'spectral_flatness': flatness
    }


def _extract_stft_features(signal: np.ndarray, dt: float) -> dict:
    """Calculates Time-Frequency features using STFT."""
    f_stft, t_stft, Zxx = stft(signal, fs=1/dt, nperseg=SC.STFT_NPERSEG, noverlap=SC.STFT_NOVERLAP)
    stft_mag = np.abs(Zxx)
    
    mask_low = (f_stft < SC.FREQ_LOW_CUTOFF)
    mask_mid = (f_stft >= SC.FREQ_LOW_CUTOFF) & (f_stft < SC.FREQ_MID_CUTOFF)
    mask_high = (f_stft >= SC.FREQ_MID_CUTOFF)
    
    energy_low = np.sum(stft_mag[mask_low, :], axis=0)
    energy_mid = np.sum(stft_mag[mask_mid, :], axis=0)
    energy_high = np.sum(stft_mag[mask_high, :], axis=0)
    
    # Centroids over time
    centroids_t = []
    for t_idx in range(stft_mag.shape[1]):
        spec = stft_mag[:, t_idx]
        total = np.sum(spec)
        centroids_t.append(np.sum(f_stft * spec) / total if total > 0 else 0)
        
    return {
        'stft_energy_low_mean': np.mean(energy_low),
        'stft_energy_low_max': np.max(energy_low),
        'stft_energy_mid_mean': np.mean(energy_mid),
        'stft_energy_mid_max': np.max(energy_mid),
        'stft_energy_high_mean': np.mean(energy_high),
        'stft_energy_high_max': np.max(energy_high),
        'stft_centroid_std': np.std(centroids_t)
    }

def _extract_slice_features(signal: np.ndarray, num_slices: int = SC.DEFAULT_SLICE_COUNT) -> dict:
    """Segments signal into slices and calculates local variance."""
    slice_size = len(signal) // num_slices
    feats = {}
    for i in range(num_slices):
        start = i * slice_size
        end = (i + 1) * slice_size if i < num_slices - 1 else len(signal)
        chunk = signal[start:end]
        feats[f'stat_slice_{i}_mean'] = np.mean(chunk)
        feats[f'stat_slice_{i}_std'] = np.std(chunk)
    return feats

def _extract_grid_features(signal: np.ndarray, analytic_signal: np.ndarray, grid_size: int = SC.DEFAULT_GRID_SIZE) -> dict:
    """Resamples signal to a fixed grid for image-like features."""
    res_sig = resample(signal, grid_size)
    res_analytic = resample(analytic_signal, grid_size)
    res_env = np.abs(res_analytic)
    res_imag = np.imag(res_analytic)
    
    feats = {}
    # Map to 16x10 grid? Original code loop suggests 160 points mapped to 16x10 indices
    for i in range(SC.GRID_ROWS):
        for j in range(SC.GRID_COLS):
            idx = i * SC.GRID_COLS + j
            if idx < grid_size:
                feats[f'grid_signal_time_{i}_{j}'] = res_sig[idx]
                feats[f'grid_hilbert_envelope_{i}_{j}'] = res_env[idx]
                feats[f'grid_hilbert_imag_{i}_{j}'] = res_imag[idx]
    return feats

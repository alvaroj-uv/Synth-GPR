import numpy as np
import pandas as pd
from scipy.signal import hilbert, stft
from scipy.stats import skew, kurtosis

def extract_features(df, dt=1e-10):
    """
    Extracts advanced time-domain, frequency-domain, and time-frequency features from GPR traces.
    
    This function computes over 200 features per signal, including:
    - Statistical moments (mean, rms, skewness, kurtosis).
    - Hilbert Transform attributes (instantaneous amplitude/envelope).
    - Frequency domain metrics (FFT spectrum, bandwidth, spectral entropy).
    - Grid-based features (resampled low-res image of the trace).
    - Slice-based statistics (local variance).

    Args:
        df (pd.DataFrame): Input DataFrame containing GPR traces.
                           Columns: 'Time', 'Signal1', 'Signal2', ... and metadata.
        dt (float): Time step in seconds. Default 1e-10.

    Returns:
        pd.DataFrame: A DataFrame where each row corresponds to a signal column from the input.
                      Columns are the extracted features.
    """
    if df.empty:
        print("DataFrame is empty. Cannot extract features.")
        return pd.DataFrame()

    features_list = []
    
    # Identify metadata columns (constant columns from HDF5 attributes)
    metadata_cols = [col for col in df.columns if col in ['gprMax', 'Title', 'Iterations', 'nx_ny_nz', 'dx_dy_dz', 'dt', 'srcsteps', 'rxsteps', 'nsrc', 'nrx']]
    metadata_values = {col: df[col].iloc[0] for col in metadata_cols}
    
    # Iterate over columns, skipping 'Time' and metadata columns
    for col in df.columns:
        if col == 'Time' or col in metadata_cols:
            continue
            
        signal = df[col].values
        
        # --- 1. Statistical Features (Time Domain) ---
        # Basic statistical measures of the signal amplitude
        mean_val = np.mean(signal)
        rms_val = np.sqrt(np.mean(signal**2)) # Root Mean Square: measure of the magnitude
        std_val = np.std(signal) # Standard Deviation: measure of spread
        median_val = np.median(signal)
        skew_val = skew(signal) # Skewness: measure of asymmetry of the distribution
        kurtosis_val = kurtosis(signal) # Kurtosis: measure of the "tailedness"
        
        # Quantiles: values below which a certain percentage of data falls
        q1 = np.percentile(signal, 25) # 25th percentile
        q2 = np.percentile(signal, 50) # 50th percentile (Median)
        q3 = np.percentile(signal, 75) # 75th percentile
        
        # Deciles: similar to quantiles but dividing into 10 parts
        deciles = np.percentile(signal, np.arange(10, 100, 10))
        d_features = {f'decile_{i+1}0': d for i, d in enumerate(deciles)}
        
        peak_max = np.max(signal) # Maximum amplitude
        peak_min = np.min(signal) # Minimum amplitude
        # Crest Factor: ratio of peak value to RMS value, indicates how extreme the peaks are
        crest_factor = peak_max / rms_val if rms_val != 0 else 0
        
        # --- 2. Hilbert Transform Features ---
        # The Hilbert transform is used to compute the instantaneous amplitude (envelope) of the signal
        # Use mirroring to reduce edge effects
        signal_mirror = np.concatenate((signal[::-1], signal))
        analytic_signal_mirror = hilbert(signal_mirror)
        # Extract the part corresponding to the original signal (second half)
        analytic_signal = analytic_signal_mirror[len(signal):]
        amplitude_envelope = np.abs(analytic_signal)
        
        # Statistical features applied to the envelope of the signal
        mean_hilbert = np.mean(amplitude_envelope)
        rms_hilbert = np.sqrt(np.mean(amplitude_envelope**2))
        std_hilbert = np.std(amplitude_envelope)
        median_hilbert = np.median(amplitude_envelope)
        skew_hilbert = skew(amplitude_envelope)
        kurtosis_hilbert = kurtosis(amplitude_envelope)
        
        q1_hilbert = np.percentile(amplitude_envelope, 25)
        q2_hilbert = np.percentile(amplitude_envelope, 50)
        q3_hilbert = np.percentile(amplitude_envelope, 75)
        
        deciles_hilbert = np.percentile(amplitude_envelope, np.arange(10, 100, 10))
        d_features_hilbert = {f'hilbert_decile_{i+1}0': d for i, d in enumerate(deciles_hilbert)}
        
        peak_max_hilbert = np.max(amplitude_envelope)
        peak_min_hilbert = np.min(amplitude_envelope)
        crest_hilbert = peak_max_hilbert / rms_hilbert if rms_hilbert != 0 else 0
        
        # --- 3. Other Features ---
        # Number of Zeros (Zero Crossings): number of times the signal crosses the zero axis
        zero_crossings = np.where(np.diff(np.signbit(signal)))[0]
        number_zeros = len(zero_crossings)
        
        # Area of Signal (Integral): sum of absolute amplitudes
        area_signal = np.sum(np.abs(signal)) 
        
        # Points of Inflexion: number of times the concavity changes (zero crossings of 2nd derivative)
        d2 = np.diff(signal, n=2)
        inflexion_points = len(np.where(np.diff(np.signbit(d2)))[0])
        
        # Fourier Features: Analysis in the frequency domain
        fft_vals = np.fft.fft(signal)
        fft_spectrum = np.abs(fft_vals) # Magnitude spectrum
        freqs = np.fft.fftfreq(len(signal), d=dt)
        
        # Keep only positive frequencies for analysis
        pos_mask = freqs >= 0
        fft_spectrum = fft_spectrum[pos_mask]
        freqs = freqs[pos_mask]
        
        area_fourier = np.sum(fft_spectrum) # Total spectral energy
        fourier_peak_max = np.max(fft_spectrum) # Peak spectral magnitude
        
        # --- 6. Advanced Frequency Domain Features ---
        # Dominant Frequency: The frequency component with the highest magnitude
        dominant_freq = freqs[np.argmax(fft_spectrum)]
        
        # Bandwidth (-3dB): The width of the frequency range where power is above half the maximum (-3dB)
        max_power = np.max(fft_spectrum)
        threshold = max_power / np.sqrt(2) # -3dB corresponds to 1/sqrt(2) of amplitude
        bandwidth_mask = fft_spectrum >= threshold
        if np.any(bandwidth_mask):
            bandwidth = freqs[bandwidth_mask][-1] - freqs[bandwidth_mask][0]
        else:
            bandwidth = 0
            
        # Mean Frequency (Spectral Centroid): Center of mass of the spectrum
        if area_fourier > 0:
            mean_freq = np.sum(freqs * fft_spectrum) / area_fourier
        else:
            mean_freq = 0
            
        # Median Frequency: Frequency that divides the spectrum energy into two equal halves
        cumulative_spectrum = np.cumsum(fft_spectrum)
        if area_fourier > 0:
            median_freq_idx = np.searchsorted(cumulative_spectrum, area_fourier / 2)
            median_freq = freqs[min(median_freq_idx, len(freqs)-1)]
        else:
            median_freq = 0
            
        # Spectral Entropy: Measure of the complexity/randomness of the power spectrum
        psd = fft_spectrum**2 / len(signal) # Power Spectral Density estimate
        psd_norm = psd / np.sum(psd) if np.sum(psd) > 0 else psd
        spectral_entropy = -np.sum(psd_norm * np.log(psd_norm + 1e-12))
        
        # Spectral Flatness: Ratio of geometric mean to arithmetic mean of the spectrum. 
        # High flatness indicates noise-like signal; low flatness indicates tonal signal.
        gmean = np.exp(np.mean(np.log(fft_spectrum + 1e-12)))
        amean = np.mean(fft_spectrum)
        spectral_flatness = gmean / amean if amean > 0 else 0
        
        area_hilbert = np.sum(amplitude_envelope)

        # --- 6. STFT Features (Time-Frequency) ---
        # Short-Time Fourier Transform to analyze frequency content evolution over time (depth)
        # Using 64-point window with overlap
        f_stft, t_stft, Zxx = stft(signal, fs=1/dt, nperseg=64, noverlap=32)
        stft_mag = np.abs(Zxx)
        
        # Calculate energy in specific bands over time
        # E.g., Low (0-500 MHz), Mid (500-1500 MHz), High (>1500 MHz)
        # fs is huge (1/1e-10 = 10 GHz). f_stft goes up to 5 GHz.
        mask_low = (f_stft < 5e8)
        mask_mid = (f_stft >= 5e8) & (f_stft < 1.5e9)
        mask_high = (f_stft >= 1.5e9)
        
        energy_low = np.sum(stft_mag[mask_low, :], axis=0)
        energy_mid = np.sum(stft_mag[mask_mid, :], axis=0)
        energy_high = np.sum(stft_mag[mask_high, :], axis=0)
        
        # Features: Mean and Max energy in these bands
        stft_features = {
            'stft_energy_low_mean': np.mean(energy_low),
            'stft_energy_low_max': np.max(energy_low),
            'stft_energy_mid_mean': np.mean(energy_mid),
            'stft_energy_mid_max': np.max(energy_mid),
            'stft_energy_high_mean': np.mean(energy_high),
            'stft_energy_high_max': np.max(energy_high),
        }
        
        # Spectral Centroid Variance over time (Dispersion measure)
        # Centroid at each time step
        centroids_t = []
        for t_idx in range(stft_mag.shape[1]):
            spectrum_t = stft_mag[:, t_idx]
            sum_spec = np.sum(spectrum_t)
            if sum_spec > 0:
                 cent = np.sum(f_stft * spectrum_t) / sum_spec
                 centroids_t.append(cent)
            else:
                 centroids_t.append(0)
                 
        stft_features['stft_centroid_std'] = np.std(centroids_t)


        # --- 4. Slice Statistics (14 slices) ---
        # Divide the signal into 14 equal segments and calculate mean/std for each
        # Physical Meaning:
        # - Slices 0-3 (Surface/Shallow): Standard Deviation here measures "Surface Roughness/Texture".
        #   High Std = Large voids/rocks (Clean). Low Std = Smooth/Filled voids (Fouled).
        num_slices = 14
        slice_size = len(signal) // num_slices
        slice_features = {}
        for i in range(num_slices):
            start = i * slice_size
            end = (i + 1) * slice_size if i < num_slices - 1 else len(signal)
            slice_data = signal[start:end]
            slice_features[f'stat_slice_{i}_mean'] = np.mean(slice_data)
            slice_features[f'stat_slice_{i}_std'] = np.std(slice_data)

        # --- 5. Grid Features (16x10) ---
        # Resample signal to 160 points and reshape to 16x10 grid
        # This creates a low-resolution "image" of the signal
        from scipy.signal import resample
        
        grid_size = 160
        
        # We need the analytic signal of the resampled signal, or resample the analytic signal.
        # Resampling the complex analytic signal is better to keep phase info.
        resampled_signal = resample(signal, grid_size)
        resampled_analytic = resample(analytic_signal, grid_size)
        resampled_envelope = np.abs(resampled_analytic)
        resampled_imag = np.imag(resampled_analytic)

        grid_features = {}
        
        # Analysis note:
        # Indices 48-51 (grid portion 4_8 to 5_1) ~30% of time window.
        # This "Golden Zone" captures the energy reflection from the typical ballast bed depth.
        # High energy (Envelope) = Clean/Dry; Low energy = Fouled/Wet.
        
        for i in range(16):
            for j in range(10):
                idx = i * 10 + j
                grid_features[f'grid_signal_time_{i}_{j}'] = resampled_signal[idx]
                grid_features[f'grid_hilbert_envelope_{i}_{j}'] = resampled_envelope[idx]
                # 'grid_absolute_hilbert' removed (redundant alias)
                grid_features[f'grid_hilbert_imag_{i}_{j}'] = resampled_imag[idx] # The 'H' feature

        # Combine all features into a dictionary
        features = {
            'Signal': col,
            'mean': mean_val,
            'root_mean_square': rms_val,
            'standard_deviation': std_val,
            'median': median_val,
            'skewness': skew_val,
            'kurtosis_value': kurtosis_val,
            'percentile_25': q1,
            'percentile_50': q2,
            'percentile_75': q3,
            'peak_max': peak_max,
            'peak_min': peak_min,
            'crest_factor': crest_factor,
            
            'hilbert_mean': mean_hilbert,
            'hilbert_root_mean_square': rms_hilbert,
            'hilbert_standard_deviation': std_hilbert,
            'hilbert_median': median_hilbert,
            'hilbert_skewness': skew_hilbert,
            'hilbert_kurtosis': kurtosis_hilbert,
            'hilbert_percentile_25': q1_hilbert,
            'hilbert_percentile_50': q2_hilbert,
            'hilbert_percentile_75': q3_hilbert,
            'hilbert_peak_max': peak_max_hilbert,
            'hilbert_peak_min': peak_min_hilbert,
            'hilbert_crest_factor': crest_hilbert,
            
            'number_zeros': number_zeros,
            'area_signal': area_signal,
            'second_derivative': inflexion_points, # Renamed d2 to second_derivative (inflexion points count)
            'area_fourier': area_fourier,
            'fourier_peak_max': fourier_peak_max,
            'dominant_frequency': dominant_freq,
            'bandwidth': bandwidth,
            'mean_frequency': mean_freq,
            'median_frequency': median_freq,
            'spectral_entropy': spectral_entropy,
            'spectral_flatness': spectral_flatness,
            'area_hilbert': area_hilbert,
            
            **d_features,
            **d_features_hilbert,
            **slice_features,
            **grid_features,
            **stft_features
        }
        
        # Add metadata
        features.update(metadata_values)
        
        features_list.append(features)

    return pd.DataFrame(features_list)

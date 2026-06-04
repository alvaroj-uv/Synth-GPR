import numpy as np
from scipy.signal import butter, filtfilt, convolve, hilbert, spectrogram

def dewow(signal, window_size=50):
    """
    Removes low-frequency 'wow' noise (inductive bias) using a running mean subtraction.
    
    Args:
        signal (np.array): Input signal.
        window_size (int): Size of the running mean window in samples.
        
    Returns:
        np.array: Signal with low-frequency trend removed.
    """
    # Simple running mean implementation
    # Use 'reflect' mode to handle edges gracefully
    window = np.ones(window_size) / window_size
    low_freq = convolve(signal, window, mode='same')
    return signal - low_freq

def detect_first_break(signal, threshold_ratio=0.05):
    """
    Detects the first break (onset) of the signal.
    
    Args:
        signal (np.array): Input signal.
        threshold_ratio (float): Threshold as a ratio of maximum amplitude (default 0.05).
        
    Returns:
        int: Index of the first break.
    """
    # 1. Calculate absolute amplitude
    abs_sig = np.abs(signal)
    max_amp = np.max(abs_sig)
    
    if max_amp == 0:
        return 0
        
    # 2. Threshold
    threshold = max_amp * threshold_ratio
    
    # 3. Find first crossing
    # Use a simple STA/LTA or just first crossing of threshold?
    # RGPR simple method: first time > threshold
    idx_over = np.where(abs_sig > threshold)[0]
    
    if len(idx_over) > 0:
        first_idx = idx_over[0]
        # Optional: Backtrack to zero crossing for more precision?
        # For now, just the threshold crossing is robust enough for visual alignment.
        return first_idx
    return 0

def time_zero_correction(signal, first_break_idx):
    """
    Shifts the signal so that the first break is at index 0.
    Pads with zeros at the end to maintain length.
    
    Args:
        signal (np.array): Input signal.
        first_break_idx (int): Index to shift to 0.
        
    Returns:
        np.array: Shifted signal.
    """
    if first_break_idx <= 0:
        return signal
        
    n = len(signal)
    if first_break_idx >= n:
        return np.zeros_like(signal)
        
    # Shift left
    shifted = np.zeros_like(signal)
    shifted[:-first_break_idx] = signal[first_break_idx:]
    
    return shifted

def apply_gain(signal, dt, type='power', alpha=1.0, window_std=None):
    """
    Applies Time-Varying Gain (TVG) to compensate for attenuation.
    
    Args:
        signal (np.array): Input signal.
        dt (float): Time step in seconds.
        type (str): 'power', 'exp', or 'agc'.
        alpha (float): Exponent for power/exp gain. 
                      For 'power', gain = t^alpha.
                      For 'exp', gain = exp(alpha * t * 1e9) (alpha is per ns).
        window_std (int): Window size (std dev) for AGC.
        
    Returns:
        np.array: Signal with gain applied.
    """
    n = len(signal)
    time_ns = np.arange(n) * dt * 1e9 # Time in nanoseconds
    
    if type == 'power':
        # Power gain: t^alpha
        # Avoid log(0) issue, start gain from small epsilon time or just clamp
        # Standard: gain increases with time
        gain_curve = (time_ns + 1.0) ** alpha
        return signal * gain_curve
        
    elif type == 'exp':
        # Exponential gain: exp(alpha * t)
        gain_curve = np.exp(alpha * time_ns)
        return signal * gain_curve
        
    elif type == 'sec':
        # Spherical Exponential Compensation (SEC)
        # Compensates for geometric spreading (t) and attenuation (exp(alpha * t))
        gain_curve = (time_ns + 1.0) * np.exp(alpha * time_ns)
        return signal * gain_curve
        
    elif type == 'agc':
        # Automatic Gain Control (AGC)
        # Normalize by local RMS amplitude
        window_len = int(window_std) if window_std else 50
        window = np.ones(window_len) / window_len
        
        # Calculate local squared envelope
        sq_signal = signal**2
        mean_sq = convolve(sq_signal, window, mode='same')
        rms = np.sqrt(mean_sq)
        
        # Avoid division by zero
        epsilon = 1e-10
        rms[rms < epsilon] = epsilon
        
        # AGC scaling factor (target RMS = 1.0 roughly)
        gain_curve = 1.0 / rms
        
        # Cap extreme gains (optional, to avoid noise explosion)
        max_gain = 1e4
        gain_curve = np.clip(gain_curve, 0, max_gain)
        
        return signal * gain_curve
        
    else:
        print(f"Warning: Unknown gain type '{type}'. Returning original signal.")
        return signal

def preprocess_signal(signal, dt, use_dewow=True, use_gain=False, gain_params=None, use_time_zero=True):
    """
    Applies processing steps to the signal.
    
    Args:
        signal (np.array): Input trace.
        dt (float): Time step.
        use_dewow (bool): Whether to apply dewow.
        use_gain (bool): Whether to apply gain.
        gain_params (dict): Params for gain {'type': 'power', 'alpha': 1.0}.
        use_time_zero (bool): Whether to apply time-zero correction (shift to first break).
    
    Returns:
        treated_signal (np.array)
        start_idx (int): Index where the effective signal starts (Time-Zero).
    """
    treated_signal = signal.copy()
    
    # 1. Dewow (Low-frequency removal)
    # Often applied FIRST to remove DC drift/bias
    if use_dewow:
        treated_signal = dewow(treated_signal, window_size=50) # Standard default
    else:
        # Simple DC removal if no dewow
        treated_signal = treated_signal - np.mean(treated_signal)
    
    # 2. Time-Zero Correction (Find Zero)
    # RGPR Approach: First Break Picking
    fb_idx = detect_first_break(treated_signal)
    start_idx = fb_idx
    
    if use_time_zero:
        treated_signal = time_zero_correction(treated_signal, fb_idx)
        # After shift, effective start is 0
        
    
    # 3. Apply Gain (Compensate Attenuation)
    # Processing often applied BEFORE filtering or AFTER?
    # Usually Gain is last or before display. 
    # But bandpass should be on raw-ish data to avoid artifact ringing.
    # Let's Apply Gain BEFORE Bandpass? 
    # Standard: Dewow -> TimeZero -> Filter -> Gain
    
    # 4. Bandpass Filter (150 MHz - 800 MHz)
    # Nyquist frequency
    fs = 1 / dt
    nyquist = 0.5 * fs
    low = 150e6 / nyquist
    high = 800e6 / nyquist
    
    # Ensure valid filter bounds
    if low > 0 and high < 1 and low < high:
        b, a = butter(4, [low, high], btype='band')
        treated_signal = filtfilt(b, a, treated_signal)
    
    # 5. Apply Gain (After filtering noise)
    if use_gain and gain_params:
        g_type = gain_params.get('type', 'power')
        g_alpha = gain_params.get('alpha', 1.0)
        treated_signal = apply_gain(treated_signal, dt, type=g_type, alpha=g_alpha)
    
    # 6. Normalization (to max value)
    max_val = np.max(np.abs(treated_signal))
    if max_val > 0:
        treated_signal = treated_signal / max_val
        
    return treated_signal, start_idx

def compute_spectrum(signal, dt):
    """
    Computes the frequency spectrum (magnitude) of the signal.

    Args:
        signal (np.array): Input signal.
        dt (float): Time step in seconds.

    Returns:
        freqs (np.array): Frequency axis (Hz).
        spectrum (np.array): Magnitude spectrum.
    """
    # Compute FFT
    fft_vals = np.abs(np.fft.fft(signal))
    freqs = np.fft.fftfreq(len(signal), d=dt)

    # Keep only positive frequencies
    pos_mask = freqs >= 0
    return freqs[pos_mask], fft_vals[pos_mask]

def compute_padded_spectrum(signal, dt, pad_factor=2):
    """
    Magnitude spectrum via a zero-padded real FFT, plus the peak frequency.

    Zero-pads the signal to ``2 ** ceil(log2(N) + pad_factor)`` samples before
    the rFFT, giving finer frequency resolution for clean peak picking. This is
    the spectrum used by the A-scan visualizers.

    Args:
        signal (np.array): Input 1-D signal.
        dt (float): Time step in seconds.
        pad_factor (int): Extra power-of-two padding beyond the next power of two.

    Returns:
        freqs (np.array): Positive frequency axis (Hz).
        spectrum (np.array): Magnitude spectrum.
        peak (float): Frequency of the spectral peak (Hz).
    """
    n_fft = 2 ** int(np.ceil(np.log2(len(signal))) + pad_factor)
    spectrum = np.abs(np.fft.rfft(signal, n=n_fft))
    freqs = np.fft.rfftfreq(n_fft, d=dt)
    peak = freqs[np.argmax(spectrum)]
    return freqs, spectrum, peak

def calculate_instantaneous_attributes(signal, dt, use_mirroring=False):
    """
    Computes instantaneous attributes using the Hilbert Transform.
    
    Args:
        signal (np.array): Input signal.
        dt (float): Time step in seconds (required for frequency).
        use_mirroring (bool): If True, pads signal to reduce edge effects.
        
    Returns:
        dict: {
            'envelope': Instantaneous Amplitude,
            'phase': Instantaneous Phase (radians),
            'frequency': Instantaneous Frequency (Hz),
            'cosine_phase': Cosine of Instantaneous Phase (-1 to 1)
        }
    """
    # 1. Analytic Signal
    if use_mirroring:
        # Edge handling from feature_extraction.py
        sig_mirror = np.concatenate((signal[::-1], signal))
        analytic_mirror = hilbert(sig_mirror)
        analytic = analytic_mirror[len(signal):]
    else:
        analytic = hilbert(signal)
        
    # 2. Envelope (Amplitude)
    envelope = np.abs(analytic)
    
    # 3. Phase (Radians)
    phase = np.angle(analytic)
    
    # 4. Instantaneous Frequency (Hz)
    # Frequency is rate of change of phase: f = (1/2pi) * d(phi)/dt
    # Unwrap phase first to avoid discontinuities
    unwrapped_phase = np.unwrap(phase)
    # Diff divides by sample spacing (1 sample), so divide by dt to get per second
    inst_freq = np.diff(unwrapped_phase) / (2.0 * np.pi * dt)
    # Pad to maintain length
    inst_freq = np.append(inst_freq, inst_freq[-1])
    
    # 5. Cosine Phase (Normalized "Structure")
    cosine_phase = np.cos(phase)
    
    return {
        'envelope': envelope,
        'phase': phase,
        'frequency': inst_freq,
        'cosine_phase': cosine_phase
    }



def compute_spectrogram(signal, fs, nperseg=None, noverlap=None):
    """
    Computes the spectrogram (Short-Time Fourier Transform) of the signal.
    
    Args:
        signal (np.array): Input signal.
        fs (float): Sampling frequency (Hz).
        nperseg (int): Length of each segment (window size).
        noverlap (int): Number of points to overlap between segments.
        
    Returns:
        f (np.array): Array of sample frequencies.
        t (np.array): Array of segment times.
        Sxx (np.array): Spectrogram of x (2D array).
    """
    if nperseg is None:
        nperseg = 256
    
    f, t, Sxx = spectrogram(signal, fs=fs, nperseg=nperseg, noverlap=noverlap)
    return f, t, Sxx

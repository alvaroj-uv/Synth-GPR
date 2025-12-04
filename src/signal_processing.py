import numpy as np
from scipy.signal import butter, filtfilt

def preprocess_signal(signal, dt):
    """
    Applies processing steps to the signal:
    1. DC-Shift Removal
    2. Time-Zero Correction (Direct Wave Removal)
    3. Bandpass Filter (150 MHz - 800 MHz)
    4. Normalization
    
    Returns:
        treated_signal (np.array)
        new_time_axis (np.array) - adjusted time axis if signal length changes
    """
    
    # 1. DC-Shift Removal
    signal = signal - np.mean(signal)
    
    # 2. Time-Zero Correction
    # Find max peak (Direct Wave)
    # Use absolute value to find the strongest peak regardless of polarity
    direct_wave_idx = np.argmax(np.abs(signal))
    
    # New Zero = Max Peak Index + 30 samples
    start_idx = direct_wave_idx + 30
    
    if start_idx < len(signal):
        treated_signal = signal[start_idx:]
    else:
        # Fallback if signal is too short
        treated_signal = signal
        start_idx = 0
        
    # 3. Bandpass Filter (150 MHz - 800 MHz)
    # Nyquist frequency
    fs = 1 / dt
    nyquist = 0.5 * fs
    low = 150e6 / nyquist
    high = 800e6 / nyquist
    
    # Ensure valid filter bounds
    if low > 0 and high < 1 and low < high:
        b, a = butter(4, [low, high], btype='band')
        treated_signal = filtfilt(b, a, treated_signal)
    
    # 4. Normalization (to max value)
    max_val = np.max(np.abs(treated_signal))
    if max_val > 0:
        treated_signal = treated_signal / max_val
        
    return treated_signal, start_idx

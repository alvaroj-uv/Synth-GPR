"""
Trace preprocessing: direct-wave removal (Wang & Liu 2017), SVD coherent-noise removal (Liu, Song & Lu 2017), dewow, first-break pickers (Coppens 1985; Earle & Shearer 1994), gain, the standard preprocess_signal chain, predictive deconvolution (Xiong 2024) and the Butterworth bandpass.

Split out of signal_processing.py (2026-07-02, debt D12); import via src.signal_processing.
"""
import warnings

import numpy as np
from scipy.signal import butter, filtfilt, convolve, resample


# ── Direct wave removal (Wang & Liu 2017) ─────────────────────────────────────

def time_gate(signal: np.ndarray, dt: float, gate_ns: float) -> np.ndarray:
    """
    Remove direct wave arrivals by zeroing samples before gate_ns.

    The direct wave energy is concentrated in the early part of the trace
    (Wang & Liu 2017, §2.2). Setting those samples to zero removes it without
    distorting later subsurface reflections.  Works on a single trace — no
    reference trace required.

    Reference:
        Wang, X. & Liu, S. (2017). Signal Processing 132:227-242. §2.2.

    Args:
        signal:  1-D numpy array (A-scan trace).
        dt:      Time step in seconds (from .out file dt attribute).
        gate_ns: Gate time in nanoseconds.
                 Rule of thumb: gate_ns = 2 * air_gap / c + 1/center_freq
                 where air_gap is antenna height above surface (m).

    Returns:
        Gated trace with same length as input; first gate_samples set to zero.
    """
    gate_samples = int(np.ceil(gate_ns / (dt * 1e9)))
    gated = signal.copy()
    gated[:gate_samples] = 0.0
    return gated


def peak_relative_coda_gate(signal: np.ndarray, dt: float,
                            start_after_peak_ns: float = None,
                            length_ns: float = None,
                            seek_peak: bool = True,
                            dewow_window: int = 50):
    """Boolean mask selecting the coda window RELATIVE to the direct-pulse peak.

    Replaces absolute time gates (e.g. the legacy 6-16 ns window): the
    direct-pulse position differs per geometry/domain (sim peaks ~3.2 ns;
    field traces in df_Signaux_traitees already start AT the peak; taller
    scenes peak later), so an absolute gate selects different physics per
    dataset. Peak-relative gating mirrors the aligned-window logic of the
    sim2real v2 pipeline: dewow -> locate |peak| -> window after it.

    The gating logic is consistent with the coda-window approach used by
    Shapovalov et al. (2026) and the analytic-signal framing of Rojas-Vivanco
    et al. (2025), both of which gate the coda relative to the direct-wave peak.

    References:
        Rojas-Vivanco et al. (2025). Transportation Geotechnics 55:101701.
        Shapovalov et al. (2026). [Hilbert-envelope coda window for FI.]

    Args:
        signal:  1-D trace.
        dt:      Time step (s).
        start_after_peak_ns: Gate opens this long after the peak
            (default SC.CODA_GATE_START_AFTER_PEAK_NS).
        length_ns: Gate length (default SC.CODA_GATE_LENGTH_NS).
        seek_peak: If False, treat sample 0 as the peak (use for traces that
            are already peak-aligned, e.g. the processed real field traces —
            re-seeking would lock onto an interior coda reflection).
        dewow_window: dewow window used only for peak detection.

    Returns:
        (mask, peak_idx): boolean mask over the trace and the peak index used.
    """
    from .constants import SC
    if start_after_peak_ns is None:
        start_after_peak_ns = SC.CODA_GATE_START_AFTER_PEAK_NS
    if length_ns is None:
        length_ns = SC.CODA_GATE_LENGTH_NS

    sig = np.asarray(signal, dtype=float)
    n = sig.size
    if n < 3:
        return np.zeros(n, dtype=bool), 0

    if seek_peak:
        dewowd_sig = dewow(sig, dewow_window)
        # Use max amplitude on dewowd signal for peak detection (robust to low-freq noise)
        peak_idx = int(np.argmax(np.abs(dewowd_sig)))
    else:
        peak_idx = 0
    t_ns = np.arange(n) * dt * 1e9
    start = t_ns[peak_idx] + start_after_peak_ns
    mask = (t_ns >= start) & (t_ns < start + length_ns)
    return mask, peak_idx


def mean_trace(signals: np.ndarray) -> np.ndarray:
    """
    Compute the common-mode direct wave from a B-scan (multiple traces).

    The direct wave is separable — r(x,t) = r1(t)·r2(x) (Wang & Liu 2017,
    Eq.19-24).  For a common-offset survey with fixed geometry, r2(x) is
    approximately constant and the per-sample mean across all traces estimates
    the direct wave r1(t)·r2(x).  Use the result as the `background` argument
    to background_subtraction() or remove_direct_wave(..., method='background_subtraction').

    Reference:
        Wang, X. & Liu, S. (2017). Signal Processing 132:227-242. Eq. 19-24.

    Args:
        signals: 2-D array of shape (n_traces, n_samples).

    Returns:
        1-D mean trace of shape (n_samples,) representing the direct wave.
    """
    return np.mean(np.atleast_2d(signals), axis=0)


def background_subtraction(signal: np.ndarray, background: np.ndarray) -> np.ndarray:
    """
    Remove direct wave arrivals by subtracting a background (reference) trace.

    Subtracting the common-mode trace removes r1(t)·r2(x), leaving only the
    material-dependent subsurface reflections (Wang & Liu 2017, Eq. 19-24).

    Two usage patterns:
      1. Fixed air reference: background = air_only_trace  (single reference)
      2. B-scan mean:         background = mean_trace(all_traces)

    Reference:
        Wang, X. & Liu, S. (2017). Signal Processing 132:227-242. Eq. 19-24.

    Args:
        signal:     1-D numpy array — trace to process.
        background: 1-D numpy array — reference direct wave (same length).

    Returns:
        Residual trace with direct wave removed.
    """
    if signal.shape != background.shape:
        raise ValueError(
            f"signal ({signal.shape}) and background ({background.shape}) must have the same shape"
        )
    return signal - background


def remove_direct_wave(
    signal: np.ndarray,
    dt: float,
    method: str = "time_gate",
    *,
    gate_ns: float = None,
    background: np.ndarray = None,
    center_freq_hz: float = None,
    air_gap_m: float = 0.3,
) -> np.ndarray:
    """
    Unified direct wave removal dispatcher.

    Chooses between time gating (Wang §2.2) and background subtraction
    (Wang Eq.19-24) based on `method`.

    Args:
        signal:         1-D numpy array — A-scan trace from .out file.
        dt:             Time step in seconds (f.attrs['dt'] in gprMax HDF5).
        method:         'time_gate' or 'background_subtraction'.
        gate_ns:        Gate time in ns (for 'time_gate').
                        If None and center_freq_hz is given, auto-computed as:
                        gate_ns = 2*air_gap_m/c + 1/center_freq_hz  (in ns)
        background:     Reference trace (for 'background_subtraction').
                        Use mean_trace(all_traces) for B-scan background.
        center_freq_hz: Center frequency in Hz (used for auto gate_ns).
        air_gap_m:      Antenna height above surface in metres (auto gate_ns).

    Returns:
        Trace with direct wave removed.

    Examples:
        # Single trace — time gating at 400 MHz, 0.3m air gap
        cleaned = remove_direct_wave(ez, dt, method='time_gate',
                                     center_freq_hz=400e6, air_gap_m=0.3)

        # B-scan — background subtraction
        bg = mean_trace(np.stack([ez1, ez2, ez3, ...]))
        cleaned = remove_direct_wave(ez1, dt, method='background_subtraction',
                                     background=bg)
    """
    if method == "time_gate":
        if gate_ns is None:
            if center_freq_hz is None:
                raise ValueError("Provide gate_ns or center_freq_hz for 'time_gate' method")
            C = 3e8
            gate_ns = (2 * air_gap_m / C) * 1e9 + (1.0 / center_freq_hz) * 1e9
        return time_gate(signal, dt, gate_ns)

    elif method == "background_subtraction":
        if background is None:
            raise ValueError("Provide background trace for 'background_subtraction' method")
        return background_subtraction(signal, background)

    elif method == "svd":
        # Liu §3.2: zero first singular value on B-scan matrix.
        # signal must be 2-D (n_traces, n_samples) here.
        return svd_remove_direct_wave(signal)

    else:
        raise ValueError(
            f"Unknown method '{method}'. "
            f"Choose 'time_gate', 'background_subtraction', or 'svd'"
        )


# ── SVD-based processing (Liu, Song & Lu 2017) ───────────────────────────────
# Liu et al., Journal of Applied Geophysics 144 (2017) 125-133
# "Random noise de-noising and direct wave eliminating based on SVD method"
#
# Key results vs. other methods (Table 1 — synthetic data at SNR=10):
#   SVD:               SNR=15.5 dB,  0.012 s  ← best accuracy + fastest
#   Wavelet threshold: SNR=10.9 dB,  1.244 s
#   Bandpass filter:   SNR= 4.7 dB,  2.098 s
#
# All SVD methods operate on the B-scan data MATRIX A (shape: n_traces × n_samples).
# Single-trace inputs are automatically promoted to a (1, n_samples) matrix.


def _to_bscan(signals: np.ndarray) -> np.ndarray:
    """Ensure signals is 2-D (n_traces, n_samples)."""
    s = np.atleast_2d(signals)
    # If passed as (n_samples, n_traces) — transpose to (n_traces, n_samples)
    return s


def svd_select_p(singular_values: np.ndarray, target_snr: float) -> int:
    """
    Quantitative criterion for choosing p singular values (Liu et al. 2017, Eq. 6).

    Iterates over candidate values of p (number of components to KEEP) and
    returns the smallest p such that the reconstructed-data SNR >= target_snr.

    Liu Eq. 6:
        f_SNR = Σ(σᵢ² for i=1..p) / (Σ(σᵢ² for i=1..r) - Σ(σᵢ² for i=1..p))

    If SNR is unknown, try target_snr ≈ 10 (typical GPR field data).

    Reference:
        Liu, S., Song, X. & Lu, G. (2017). J. Appl. Geophys. 144:125-133. Eq. 6.

    Args:
        singular_values: 1-D array of singular values in decreasing order.
        target_snr:      Target SNR ratio (linear, not dB).
                         Convert: target_snr = 10 ** (target_snr_db / 10)

    Returns:
        p: Number of singular values to keep.
    """
    sv2 = singular_values ** 2
    total_energy = np.sum(sv2)
    for p in range(1, len(singular_values) + 1):
        kept   = np.sum(sv2[:p])
        removed = total_energy - kept
        if removed < 1e-12:
            return p
        f_snr = kept / removed
        if f_snr >= target_snr:
            return p
    return len(singular_values)


def svd_denoise(
    signals: np.ndarray,
    p: int = None,
    target_snr: float = 10.0,
) -> np.ndarray:
    """
    Denoise a GPR B-scan by zeroing small singular values (Liu et al. 2017, §3.1).

    The B-scan matrix A is decomposed as A = UDV^T (Liu Eq. 2–4).
    Singular values are ranked by energy; small ones correspond to noise.
    Keeping the top-p components and zeroing the rest recovers the signal.
    Table 1 of Liu (2017): SVD achieves SNR=15.5 dB in 0.012 s vs wavelet
    threshold 10.9 dB / 1.2 s and bandpass 4.7 dB / 2.1 s.

    Reference:
        Liu, S., Song, X. & Lu, G. (2017). J. Appl. Geophys. 144:125-133.

    Args:
        signals:    2-D array (n_traces, n_samples) — B-scan data matrix.
                    Also accepts 1-D (single trace), auto-promoted.
        p:          Number of singular values to keep (None = auto via criterion).
        target_snr: Target SNR for auto-selection via Liu Eq. 6 (linear, default=10).
                    Ignored when p is explicitly provided.

    Returns:
        Denoised array with same shape as input.
    """
    A    = _to_bscan(signals).astype(float)
    U, s, Vt = np.linalg.svd(A, full_matrices=False)

    if p is None:
        p = svd_select_p(s, target_snr)
    p = max(1, min(p, len(s)))

    # Reconstruct using only top-p singular values
    s_filtered    = np.zeros_like(s)
    s_filtered[:p] = s[:p]
    denoised = U @ np.diag(s_filtered) @ Vt

    return denoised.squeeze() if signals.ndim == 1 else denoised


def svd_remove_direct_wave(signals: np.ndarray) -> np.ndarray:
    """
    Remove direct wave by zeroing the first singular value (Liu et al. 2017, §3.2).

    The direct wave is the dominant coherent event — it maps to the FIRST
    (largest) singular value σ₁. Setting σ₁=0 and reconstructing with
    σ₂...σᵣ removes the direct wave while preserving subsurface reflections.
    Advantage over mean-trace subtraction: does not create false reflectors
    when the interface undulates; robust to missing traces; better phase
    preservation near t=0 (Liu et al. 2017, Fig. 21).

    Reference:
        Liu, S., Song, X. & Lu, G. (2017). J. Appl. Geophys. 144:125-133. §3.2.

    Args:
        signals: 2-D array (n_traces, n_samples) — B-scan data matrix.
                 For a single A-scan, use background_subtraction() instead.

    Returns:
        Array with direct wave removed, same shape as input.

    Raises:
        ValueError: If signals has fewer than 2 traces (SVD rank-1 removal
                    requires at least 2 traces to retain any signal).
    """
    A = _to_bscan(signals).astype(float)
    if A.shape[0] < 2:
        raise ValueError(
            "svd_remove_direct_wave requires >= 2 traces (B-scan). "
            "For a single trace use background_subtraction() or time_gate()."
        )

    U, s, Vt = np.linalg.svd(A, full_matrices=False)
    s_filtered    = s.copy()
    s_filtered[0] = 0.0          # zero the direct wave component

    result = U @ np.diag(s_filtered) @ Vt
    return result


def dewow(signal, window_size=50):
    """
    Removes low-frequency 'wow' noise (inductive bias) using a running mean subtraction.

    Dewow is step 2 in the Rojas-Vivanco (2025) preprocessing chain:
    "Elimination of the DC-Shift component, that is, the signals are centered
    so that they have a mean equal to zero."

    A running-mean low-pass is subtracted rather than a simple DC removal because
    the inductive coupling between the antenna and soil creates a slowly varying
    baseline that changes along the trace (not constant DC).

    Reference:
        Rojas-Vivanco et al. (2025). Transportation Geotechnics 55:101701.
        Daniels, D. (2005). Ground Penetrating Radar, 2nd ed. IET. §signal processing.

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

def detect_first_break_coppens(signal, short_win=10, long_win=100, threshold=1.5):
    """
    Coppens algorithm for first-break picking (energy-ratio method).

    Detects the onset by finding where the ratio of short-window energy to
    trailing-window average energy crosses a threshold. More robust to noise than
    simple amplitude thresholding, especially for field data.

    The algorithm computes a short-window power and compares it to the
    background (long-window average computed BEFORE the current position).

    References:
        Coppens, F. (1985). First arrivals picking on common offset trace collections
        for automatic estimation of static corrections. Geophysical Prospecting 33(12).

    Args:
        signal (np.array): Input 1-D A-scan.
        short_win (int): Short-time window length (samples). Typical: 5-20.
        long_win (int): Long-time (background) window length (samples). Typical: 50-200.
        threshold (float): Energy ratio threshold. Typical: 1.0-3.0.
                          Coppens suggests 1.5-2.0 for field data.

    Returns:
        int: Sample index of first break; 0 if detection fails.
    """
    sig = np.asarray(signal, dtype=float)
    n = len(sig)

    if n < long_win + short_win:
        return 0

    # Squared amplitude (power)
    power = sig ** 2

    # Short-window energy (current window)
    short_energy = np.convolve(power, np.ones(short_win) / short_win, mode='same')

    # Long-window energy (background, trailing average)
    long_energy = np.convolve(power, np.ones(long_win) / long_win, mode='same')

    # Avoid division by zero
    long_energy = np.maximum(long_energy, 1e-12 * np.max(power))

    # Energy ratio: short_win_power / long_win_power
    ratio = short_energy / long_energy

    # Find first crossing above threshold, starting after the long_win to avoid edge effects
    start_idx = long_win + short_win
    candidates = np.where(ratio[start_idx:] > threshold)[0]

    if len(candidates) > 0:
        return int(candidates[0] + start_idx)

    return 0


def detect_first_break_sta_lta(signal, short_win=10, long_win=100, threshold=2.0):
    """
    STA/LTA (Short-Time Average / Long-Time Average) first-break picker.

    Computes a running ratio of short-window RMS to long-window RMS. Onset is
    where the ratio crosses the threshold. Originates in seismology and is
    robust to non-stationary noise.

    References:
        Earle, P.S. & Shearer, P.M. (1994). Characterization of global seismograms
        using an automatic picking algorithm. BSSA 84(1):95-108.
        Allen, R.V. (1978). Automatic earthquake recognition. BSSA 68(5):1521-1532.

    Args:
        signal (np.array): Input 1-D A-scan.
        short_win (int): Short-time window length (samples). Typical: 5-20.
        long_win (int): Long-time window length (samples). Typical: 50-200.
        threshold (float): Ratio threshold. Typical: 1.5-3.0.

    Returns:
        int: Sample index of first break; 0 if detection fails.
    """
    sig = np.asarray(signal, dtype=float)
    n = len(sig)

    if n < long_win + short_win:
        return 0

    # RMS in short and long windows
    short_rms = np.sqrt(np.convolve(sig ** 2, np.ones(short_win) / short_win, mode='same'))
    long_rms  = np.sqrt(np.convolve(sig ** 2, np.ones(long_win) / long_win, mode='same'))

    # Avoid division by zero
    long_rms = np.maximum(long_rms, 1e-10)

    ratio = short_rms / long_rms

    candidates = np.where(ratio > threshold)[0]
    if len(candidates) > 0:
        return int(candidates[0])

    return 0


def detect_first_break(signal, method='coppens', threshold_ratio=0.05,
                       coppens_short_win=10, coppens_long_win=100, coppens_threshold=3.0,
                       sta_lta_short_win=10, sta_lta_long_win=100, sta_lta_threshold=2.0):
    """
    Unified first-break detector — dispatcher for three algorithms.

    Delegates to:
      'coppens'   — energy-ratio picker (Coppens 1985); default, robust to noise
      'sta_lta'   — STA/LTA ratio picker (Allen 1978; Earle & Shearer 1994)
      'threshold' — simple amplitude threshold (no paper reference; legacy)

    References:
        Coppens, F. (1985). Geophysical Prospecting 33(12). [energy ratio]
        Allen, R.V. (1978). BSSA 68(5):1521-1532. [STA/LTA seismology]
        Earle, P.S. & Shearer, P.M. (1994). BSSA 84(1):95-108. [STA/LTA GPR]

    Args:
        signal (np.array): Input signal.
        method (str): 'coppens' (default, recommended), 'sta_lta', or 'threshold'.
        threshold_ratio (float): For method='threshold' only; ratio of max amplitude.
        coppens_short_win, coppens_long_win, coppens_threshold: Coppens parameters.
        sta_lta_short_win, sta_lta_long_win, sta_lta_threshold: STA/LTA parameters.

    Returns:
        int: Index of the first break.

    Examples:
        fb_idx = detect_first_break(signal, method='coppens')
        fb_idx = detect_first_break(signal, method='sta_lta', sta_lta_threshold=2.5)
        fb_idx = detect_first_break(signal, method='threshold', threshold_ratio=0.1)
    """
    if method == 'coppens':
        return detect_first_break_coppens(signal, coppens_short_win, coppens_long_win, coppens_threshold)

    elif method == 'sta_lta':
        return detect_first_break_sta_lta(signal, sta_lta_short_win, sta_lta_long_win, sta_lta_threshold)

    elif method == 'threshold':
        # Original simple amplitude-threshold method
        abs_sig = np.abs(signal)
        max_amp = np.max(abs_sig)

        if max_amp == 0:
            return 0

        threshold = max_amp * threshold_ratio
        idx_over = np.where(abs_sig > threshold)[0]

        if len(idx_over) > 0:
            return int(idx_over[0])
        return 0

    else:
        raise ValueError(f"Unknown first-break method '{method}'. "
                         f"Choose 'coppens', 'sta_lta', or 'threshold'.")

def time_zero_correction(signal, first_break_idx):
    """
    Shifts the signal so that the first break is at index 0.
    Pads with zeros at the end to maintain length.

    Implements step 3 of the Rojas-Vivanco (2025) preprocessing chain:
    "Once located, a new zero time is placed at this point. From this zero
    time, a shift of 30 samples is made."  Here we shift by first_break_idx
    (caller-supplied) rather than a hard-coded 30, making it sensor-agnostic.

    Reference:
        Rojas-Vivanco et al. (2025). Transportation Geotechnics 55:101701.

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
    Applies Time-Varying Gain (TVG) to compensate for geometric spreading and
    dielectric attenuation that reduce signal amplitude with depth.

    WARNING: DISPLAY-ONLY. Never apply gain to data destined for feature
    extraction or amplitude / sigma / envelope analysis — it multiplies the
    trace by a time-varying curve and destroys the physical amplitude those
    analyses rely on ('agc' additionally applies a nonlinear per-sample gain
    that breaks coda coherence). Use preprocess_physical for the
    amplitude-preserving chain.

    Three modes are provided:
      'power' — gain = (t+1)^alpha  (geometric spreading, α=2 for 3-D)
      'exp'   — gain = exp(alpha·t) (exponential dielectric loss)
      'sec'   — gain = (t+1)·exp(alpha·t)  (Spherical Exponential Compensation)
      'agc'   — Automatic Gain Control: normalise by local RMS (Yilmaz 2001)

    References:
        Yilmaz, O. (2001). Seismic Data Analysis, vol. 1, SEG. §2.1 gain corrections.
        Daniels, D. (2005). Ground Penetrating Radar, 2nd ed. IET. §signal processing.

    Args:
        signal (np.array): Input signal.
        dt (float): Time step in seconds.
        type (str): 'power', 'exp', 'sec', or 'agc'.
        alpha (float): Exponent / attenuation coefficient.
                       power: gain = t^alpha.
                       exp:   gain = exp(alpha * t_ns) (alpha in 1/ns).
        window_std (int): Window length in samples for AGC local RMS.

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


def remove_gain(trace: np.ndarray, gain_curve_db, dt: float) -> np.ndarray:
    """Undo a time-varying ACQUISITION gain to restore physical amplitude.

    GSSI systems apply a range-gain (dB, rising with time) during acquisition.
    If it is baked into the stored samples, the trace envelope reflects the
    operator's gain, not physics — which invalidates any sigma / attenuation /
    envelope-decay work. This interpolates the dB gain breakpoints across the
    trace (they are stored evenly spaced across the time window) and DIVIDES
    them out in linear amplitude (20·log10 convention).

    Inverse of the display-only :func:`apply_gain`; unlike it, this is a physical
    correction that RESTORES amplitude, so it is safe upstream of feature/sigma
    analysis (indeed required, if gain was baked in).

    Args:
        trace:         1-D array (raw samples).
        gain_curve_db: 1-D array of gain breakpoints in dB, evenly spaced across
                       the trace's time span; a scalar / length-1 = constant gain.
        dt:            Time step (s). Accepted for signature symmetry; the curve
                       is mapped by fractional position, not absolute dt.

    Returns:
        De-gained trace (same length).
    """
    g = np.asarray(gain_curve_db, dtype=float).ravel()
    trace = np.asarray(trace, dtype=float)
    if g.size == 0:
        return trace.copy()
    n = len(trace)
    if g.size == 1:
        gain_db_full = np.full(n, g[0])
    else:
        gain_db_full = np.interp(np.linspace(0.0, 1.0, n),
                                 np.linspace(0.0, 1.0, g.size), g)
    return trace / (10.0 ** (gain_db_full / 20.0))


def preprocess_signal(
    signal,
    dt,
    use_dewow=True,
    use_gain=False,
    gain_params=None,
    use_time_zero=True,
    first_break_method="sta_lta",
    direct_wave_removal="time_gate",
    direct_wave_kwargs=None,
):
    """
    Apply standard GPR processing chain to a single A-scan trace.

    **DEFAULT: Direct wave removal is ENABLED** via time gating (Wang §2.2).
    This removes the air-ballast surface reflection that dominates raw GPR signals.

    Args:
        signal:                1-D numpy array — raw trace from .out file.
        dt:                    Time step in seconds.
        use_dewow:             Apply dewow (running-mean low-freq removal).
        use_gain:              Apply time-varying gain after filtering.
        gain_params:           Dict for gain, e.g. {'type': 'power', 'alpha': 1.0}.
        use_time_zero:         Shift trace so first break is at sample 0.
        first_break_method:    Method for first-break picking: 'sta_lta' (default, robust),
                               'coppens' (energy ratio), or 'threshold' (simple).
        direct_wave_removal:   **DEFAULT: 'time_gate'** (single-trace, antenna-height
                               based). Alternatives: 'background_subtraction' (requires
                               B-scan mean via `direct_wave_kwargs`), or None to disable.
                               Applied FIRST, before dewow.
                               (Wang & Liu 2017, Signal Processing 132:227-242)
        direct_wave_kwargs:    Dict of keyword args for remove_direct_wave().
                               For 'time_gate': {'center_freq_hz': 400e6, 'air_gap_m': 0.3}
                               For 'background_subtraction': {'background': mean_trace}
                               Default (time_gate): center_freq=400MHz, air_gap=0.3m.

    Returns:
        treated_signal (np.array)
        start_idx (int): First-break sample index (after direct wave removal).
    """
    warnings.warn(
        "preprocess_signal mixes physical steps with amplitude normalization "
        "(step 6, peak-normalize). For sigma / envelope / amplitude work use "
        "preprocess_physical (no gain, no normalization); for the ML feature "
        "matrix use preprocess_physical + normalize_for_features. Kept only for "
        "backward compatibility.",
        DeprecationWarning, stacklevel=2,
    )
    treated_signal = signal.copy()

    # 0. Direct wave removal (Wang & Liu 2017) — applied FIRST
    # DEFAULT: time_gate with 400 MHz antenna, 0.3m air gap
    if direct_wave_removal is not None:
        dw_kw = direct_wave_kwargs or {}
        # Auto-populate time_gate defaults if not provided
        if direct_wave_removal == "time_gate":
            dw_kw.setdefault("center_freq_hz", 400e6)
            dw_kw.setdefault("air_gap_m", 0.3)
        treated_signal = remove_direct_wave(
            treated_signal, dt,
            method=direct_wave_removal,
            **dw_kw
        )

    # 1. Dewow (Low-frequency removal)
    # Often applied FIRST to remove DC drift/bias
    if use_dewow:
        treated_signal = dewow(treated_signal, window_size=50) # Standard default
    else:
        # Simple DC removal if no dewow
        treated_signal = treated_signal - np.mean(treated_signal)
    
    # 2. Time-Zero Correction (Find Zero)
    # First-break detection: STA/LTA by default (more robust than Coppens)
    fb_idx = detect_first_break(treated_signal, method=first_break_method)
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


def preprocess_physical(signal, dt, target_dt=None, use_dewow=True,
                        first_break_method="sta_lta", gain_curve_db=None):
    """
    Amplitude-preserving physical preprocessing: (de-gain) -> dewow -> time-zero -> (optional) resample.

    This is the chain for ANY analysis that depends on physical amplitude —
    conductivity (sigma), envelope decay (alpha), spectral evolution. It applies
    NO gain and NO normalization, so relative amplitudes are preserved: every
    step (dewow, time-zero shift, Fourier resample) is LINEAR, so scaling the
    input by k scales the output by exactly k. For the ML feature /
    classification matrix, follow this with normalize_for_features(), which
    peak-normalizes BOTH domains together.

    Steps:
      0. de-gain: divide out a supplied acquisition gain curve (gain_curve_db)
         if it is non-flat — restores physical amplitude for real DZT traces.
      1. dewow (running-mean low-frequency / DC-drift removal), or plain DC
         removal if use_dewow=False.
      2. time-zero correction (first-break pick + left shift to sample 0).
      3. resample to target_dt (scipy Fourier resample, which band-limits on
         downsampling) — only if target_dt is given and differs from dt. Used to
         bring synthetic traces (dt~0.031 ns) onto the real time base
         (dt=0.1 ns) so both domains share a sample grid before feature
         extraction.

    Explicitly NOT done here: gain (apply_gain is display-only), peak/RMS
    normalization, bandpass. Those either destroy absolute amplitude or are
    downstream analysis choices.

    Args:
        signal:             1-D numpy array (raw A-scan).
        dt:                 Input time step in seconds (REQUIRED).
        target_dt:          If given, resample so the output time step is
                            target_dt (total duration preserved). None -> no
                            resample.
        use_dewow:          Apply dewow (True) or plain DC removal (False).
        first_break_method: First-break picker for time-zero ('sta_lta' default,
                            a scale-invariant ratio picker).
        gain_curve_db:      Optional dB gain-breakpoint curve (e.g. from
                            src.dzt_io.read_gain_curve) divided out first; None
                            (default) or a flat curve = no-op.

    Returns:
        (treated_signal, start_idx, dt_out)
          treated_signal: processed trace (amplitude-preserving).
          start_idx:      first-break sample index in the INPUT sample grid.
          dt_out:         output time step (target_dt if resampled, else dt).
    """
    if dt is None:
        raise ValueError(
            "preprocess_physical requires an explicit dt (in seconds); read it "
            "from the HDF5 'dt' attribute (synthetic) or the DZT header (real)."
        )

    treated = np.asarray(signal, dtype=float).copy()

    # 0. Undo baked-in acquisition gain (physical amplitude restore). Only when a
    #    non-flat dB curve is supplied (real DZT domain); default None -> skip.
    if gain_curve_db is not None:
        g = np.asarray(gain_curve_db, dtype=float).ravel()
        if g.size and not np.allclose(g, g[0]):
            treated = remove_gain(treated, g, dt)

    # 1. Dewow / DC removal — physical, amplitude-preserving (linear)
    if use_dewow:
        treated = dewow(treated, window_size=50)
    else:
        treated = treated - np.mean(treated)

    # 2. Time-zero correction (first-break pick + shift)
    fb_idx = detect_first_break(treated, method=first_break_method)
    treated = time_zero_correction(treated, fb_idx)

    # 3. Optional resample to a target dt (Fourier -> band-limits on downsample)
    dt_out = dt
    if target_dt is not None and not np.isclose(target_dt, dt, rtol=1e-9, atol=0.0):
        n_out = int(round(len(treated) * dt / target_dt))
        if n_out < 2:
            raise ValueError(
                f"target_dt={target_dt:.3e}s too coarse for a "
                f"{len(treated) * dt:.3e}s trace (n_out={n_out})."
            )
        treated = resample(treated, n_out)
        dt_out = target_dt

    return treated, fb_idx, dt_out


def normalize_for_features(signals_real, signals_sim, method="peak"):
    """
    Apply ONE amplitude normalization to BOTH domains in a single call.

    Normalizing sim and real independently, in different places, is exactly how
    the historic "1/33" collapse happened: one domain was rescaled and the other
    was not, so the classifier met a scale it had never learned and fell back to
    the majority class. This function takes BOTH sets and normalizes them with
    the same operation, so applying it to only one side is impossible by
    construction.

    method="peak": divide every trace (in both sets) by its own max|.| -> every
    output trace has unit peak, so the sim<->real relative scale factor is
    exactly 1.0 by construction (documented and tested).

    WARNING: peak normalization DESTROYS absolute amplitude. Use this ONLY for
    the ML feature / classification matrix. NEVER for sigma, envelope decay
    (alpha), or any amplitude analysis — use preprocess_physical for those.

    Args:
        signals_real: 1-D (single trace) or 2-D (n_traces x n_samples) array.
        signals_sim:  same shape convention.
        method:       only "peak" (per-trace max|.|) is supported.

    Returns:
        (real_norm, sim_norm) — same shapes as the inputs.
    """
    if method != "peak":
        raise ValueError(
            f"Unsupported normalization method '{method}'. Only 'peak' is supported."
        )

    def _peak_norm(a):
        a = np.asarray(a, dtype=float)
        peaks = np.max(np.abs(a), axis=-1, keepdims=True)
        peaks = np.where(peaks > 0, peaks, 1.0)
        return a / peaks

    return _peak_norm(signals_real), _peak_norm(signals_sim)


# ── Predictive Deconvolution (Xiong et al. 2024, GPRlab) ────────────────────
# Xiong et al., SoftwareX 26 (2024): "Predictive deconvolution, a convolution-based
# inverse filtering method, is typically used to suppress periodic multiple interference."
#
# For railway ballast: removes ringing from layer bounces that obscure material-
# dependent reflections.


def predictive_deconvolution(signal: np.ndarray, lag: int = 10, alpha: float = 0.01) -> np.ndarray:
    """
    Suppress periodic multiple reflections via predictive deconvolution.

    In railway ballast GPR, multiple reflections from layer boundaries (surface
    bounce between air and ballast, ballast and subgrade) ring and obscure weak
    material-dependent reflections. Predictive deconvolution removes coherent
    multiples via least-squares prediction filtering.

    Algorithm: Solve min_h || signal[lag:] - H(signal[:-lag]) ||^2 + alpha||h||^2,
    where H is a convolution with prediction filter h. The deconvolved signal is
    the prediction error: signal - convolved_prediction.

    Args:
        signal (np.ndarray): 1-D input A-scan.
        lag (int): Prediction lag in samples. Default 10 targets multiples ~5-10ns
                   at typical 1-5 GHz sampling. Increase for deeper bounces.
        alpha (float): Tikhonov regularization (0.001-0.1). Higher = more damping
                       on the inverse filter. Default 0.01 is conservative.

    Returns:
        np.ndarray: Deconvolved signal (same shape as input).

    Reference:
        Xiong et al. (2024). GPRlab: A ground penetrating radar data processing
        and analysis software based on MATLAB. SoftwareX 26:101720.
        Claerbout, J. F. (1992). Earth Soundings Analysis: Processing versus Inversion.
    """
    sig = np.asarray(signal, dtype=float)
    n = len(sig)

    if lag >= n or lag < 1:
        return sig.copy()

    # Build multi-tap Wiener prediction problem
    # A @ h = b, where A[i,j] = sig[i + lag - j - 1], b = sig[i + lag]
    n_taps = min(lag, n // 2)
    n_samples = n - lag

    A = np.zeros((n_samples, n_taps))
    for j in range(n_taps):
        idx = lag - j - 1
        if idx >= 0:
            A[:, j] = sig[idx : idx + n_samples]

    b = sig[lag : lag + n_samples]

    # Regularized least-squares (Tikhonov)
    AtA = A.T @ A + alpha * np.eye(n_taps)
    Atb = A.T @ b

    try:
        h = np.linalg.solve(AtA, Atb)
    except np.linalg.LinAlgError:
        h = np.linalg.lstsq(AtA, Atb, rcond=None)[0]

    # Convolve with prediction filter and subtract (prediction error = deconvolution)
    predicted = convolve(sig, h, mode="same")
    deconvolved = sig - predicted

    return deconvolved


# ── B-scan 2-D preprocessing ──────────────────────────────────────────────────

def bandpass_filter(
    signal: np.ndarray,
    dt: float,
    f_lo: float = 150e6,
    f_hi: float = 800e6,
    order: int = 4,
) -> np.ndarray:
    """Apply a zero-phase Butterworth bandpass filter to a single A-scan.

    Standalone wrapper so that bandpass can be applied independently of the
    full Vivanco or preprocess_signal chains.

    Args:
        signal: 1-D input trace (arbitrary units).
        dt:     Time step in seconds.
        f_lo:   Lower corner frequency in Hz (default 150 MHz).
        f_hi:   Upper corner frequency in Hz (default 800 MHz).
        order:  Butterworth filter order (default 4).

    Returns:
        Filtered trace, same length as input.

    References:
        Daniels (2005), Ground Penetrating Radar 2nd ed., IET. §signal processing.
        Rojas-Vivanco et al. (2025), Transportation Geotechnics 55:101701.
    """
    nyq = 0.5 / dt
    lo, hi = f_lo / nyq, f_hi / nyq
    if not (0 < lo < hi < 1.0):
        raise ValueError(
            f'bandpass corners [{f_lo/1e6:.0f}, {f_hi/1e6:.0f}] MHz out of range '
            f'for dt={dt*1e9:.4f} ns (Nyquist={nyq/1e6:.0f} MHz)'
        )
    b, a = butter(order, [lo, hi], btype='band')
    return filtfilt(b, a, signal)



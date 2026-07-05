"""
Spectral analysis (windows, FFT, STFT), instantaneous attributes via the analytic signal, and Matrix Pencil modal decomposition (Mbubia 2024).

Split out of signal_processing.py (2026-07-02, debt D12); import via src.signal_processing.
"""
import numpy as np
from scipy.signal import hilbert, spectrogram, get_window


def apply_window(signal, window="hann"):
    """
    Apply a taper window to a finite signal with coherent-gain correction.

    A finite-duration record has hard edges that smear the FFT (spectral
    leakage). Tapering with a smooth window (Hann/Hamming/Blackman) suppresses
    leakage at the cost of widening the main lobe.

    Coherent-gain correction divides by mean(window) so the amplitude of a
    sinusoid is preserved. A rectangular ("boxcar") window has mean 1, so it is
    a true no-op — making window=None / "boxcar" identical to the un-windowed FFT.

    Reference:
        Unpingco, J. (2014). Python for Signal Processing. Springer.
            §"Windowing": always window before the FFT; coherent gain correction.

    Args:
        signal (np.array): Input 1-D signal.
        window (str | None): scipy window name (e.g. "hann", "hamming",
            "blackman", "boxcar"). None means no window (rectangular).

    Returns:
        np.array: Windowed signal (same length), amplitude-corrected.
    """
    if window is None or window == "boxcar":
        return np.asarray(signal, dtype=float)
    w = get_window(window, len(signal), fftbins=True)
    coherent_gain = np.mean(w)           # Hann ≈ 0.5, Hamming ≈ 0.54, boxcar = 1
    return np.asarray(signal, dtype=float) * w / coherent_gain


def compute_spectrum(signal, dt, window=None):
    """
    Computes the frequency spectrum (magnitude) of the signal.

    Args:
        signal (np.array): Input signal.
        dt (float): Time step in seconds.
        window (str | None): Taper applied before the FFT to control spectral
            leakage (Unpingco). None (default) = rectangular = no leakage control,
            preserving the original behaviour. Use "hann" for clean peak picking.

    Returns:
        freqs (np.array): Frequency axis (Hz).
        spectrum (np.array): Magnitude spectrum.
    """
    windowed = apply_window(signal, window)
    fft_vals = np.abs(np.fft.fft(windowed))
    freqs = np.fft.fftfreq(len(windowed), d=dt)

    # Keep only positive frequencies
    pos_mask = freqs >= 0
    return freqs[pos_mask], fft_vals[pos_mask]

def compute_padded_spectrum(signal, dt, pad_factor=2, window=None):
    """
    Magnitude spectrum via a zero-padded real FFT, plus the peak frequency.

    Zero-pads the signal to ``2 ** ceil(log2(N) + pad_factor)`` samples before
    the rFFT, giving finer frequency resolution for clean peak picking. This is
    the spectrum used by the A-scan visualizers.

    Windowing (Unpingco) is applied to the ORIGINAL N samples BEFORE zero-padding
    — never to the padded zeros — so the taper acts only on real data while the
    padding still buys interpolated frequency resolution.

    Args:
        signal (np.array): Input 1-D signal.
        dt (float): Time step in seconds.
        pad_factor (int): Extra power-of-two padding beyond the next power of two.
        window (str | None): Taper applied before padding (e.g. "hann"). None
            (default) preserves the original un-windowed behaviour.

    Returns:
        freqs (np.array): Positive frequency axis (Hz).
        spectrum (np.array): Magnitude spectrum.
        peak (float): Frequency of the spectral peak (Hz).
    """
    windowed = apply_window(signal, window)   # taper the real samples first
    n_fft = 2 ** int(np.ceil(np.log2(len(windowed))) + pad_factor)
    spectrum = np.abs(np.fft.rfft(windowed, n=n_fft))  # rfft zero-pads to n_fft
    freqs = np.fft.rfftfreq(n_fft, d=dt)
    peak = freqs[np.argmax(spectrum)]
    return freqs, spectrum, peak

def calculate_instantaneous_attributes(signal, dt, use_mirroring=False):
    """
    Computes instantaneous attributes via the Hilbert (analytic signal) transform.

    The analytic signal Z(t) = signal(t) + j·H{signal}(t) yields four
    physically meaningful attributes used in GPR fouling analysis:

      Envelope = |Z(t)|     — instantaneous amplitude; Rojas-Vivanco (2025) shows
                              the Hilbert envelope separates fouling states better
                              than the raw trace and is their "group 3" feature set.
      Phase    = arg Z(t)   — instantaneous phase (radians)
      Freq     = d(phase)/dt / (2π)  — instantaneous frequency (Hz)
      Cosine   = cos(phase) — normalised "structure" attribute from seismics

    References:
        Braun, B., Ewins, L. & Rao, P. (2001). Signal processing for GPR.
            ICASSP 5:3013-3016. [envelope for GPR]
        Feldman, M. (2011). Hilbert transform in vibration analysis.
            Mech. Syst. Signal Process. 25(3):735-802.
        Rojas-Vivanco et al. (2025). Transportation Geotechnics 55:101701.
            §"Analytical signal" — envelope as key GPR feature for FI estimation.

    Args:
        signal (np.array): Input signal.
        dt (float): Time step in seconds (required for instantaneous frequency).
        use_mirroring (bool): Prepend a mirrored copy before the Hilbert transform
            to reduce edge ringing (useful for short windows).

    Returns:
        dict with keys:
            'envelope':    Instantaneous amplitude  |Z(t)|
            'phase':       Instantaneous phase      arg Z(t)  (radians)
            'frequency':   Instantaneous frequency  (Hz)
            'cosine_phase': cos(phase)              (dimensionless, -1 to 1)
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
    Computes the Short-Time Fourier Transform (STFT) spectrogram of the signal.

    The STFT divides the trace into overlapping windows and computes the FFT of
    each, producing a time-frequency representation.  Rojas-Vivanco (2025) use an
    STFT grid sampled at fixed (time, frequency) cells — ST_i_j, H_i_j, AH_i_j
    — as their "group 2/3" ML features (262 columns total).  Alzarrad et al. (2024)
    also use STFT for automatic GPR signal interpretation.

    References:
        Rojas-Vivanco et al. (2025). Transportation Geotechnics 55:101701.
            §"GPR parameterisation" Table 4 — STFT grid features.
        Alzarrad et al. (2024). CivilEng 5(2):378-394.

    Args:
        signal (np.array): Input signal.
        fs (float): Sampling frequency (Hz).
        nperseg (int): STFT window length in samples (default 256).
        noverlap (int): Overlap between windows in samples (default nperseg//2).

    Returns:
        f (np.array): Frequency axis (Hz).
        t (np.array): Time axis (s).
        Sxx (np.array): Power spectral density, shape (len(f), len(t)).
    """
    if nperseg is None:
        nperseg = 256

    f, t, Sxx = spectrogram(signal, fs=fs, nperseg=nperseg, noverlap=noverlap)
    return f, t, Sxx


# ── Matrix Pencil Method (Mbubia et al. 2024) ─────────────────────────────────

def mpm_decompose(segment: np.ndarray, dt_s: float,
                  L: int = None,
                  sv_threshold: float = 0.999,
                  max_poles: int = 30,
                  freq_lo_hz: float = 50e6,
                  freq_hi_hz: float = 900e6) -> dict:
    """Decompose a 1-D signal into damped complex exponentials via MPM.

    References:
        Sarkar, T.K. & Pereira, O. (1995). Using the Matrix Pencil Method to
            estimate the parameters of a sum of complex exponentials. IEEE Ant.
            Propag. Mag. 37(1):48-55.  [MPM algorithm]
        Mbubia et al. (2024). J. Phys. Conf. Ser. 2887:012047. —
            "Raw + MPM" SVM achieved Clean 92% / Fouled 100% on synthetic GPR data.
            Fouling raises sigma 1e-5→1e-2 S/m, increasing pole damping rate.

    Algorithm:
      1. Build Hankel data matrix Y of shape (N-L, L+1).
      2. SVD of Y1 = Y[:,:-1]; keep top-M singular values (energy threshold).
      3. A = pinv(Y1) @ Y2 — the matrix pencil.
      4. Eigenvalues of A give z-domain poles z_k.
      5. Continuous-time poles: s_k = ln(z_k) / dt_s.
      6. Residues R_k via least-squares: [z_k^n] @ R = y.

    Physical validity filter (z-domain):
      - |z_k| in (z_min, 1.0): decaying but not noise-floor artefacts.
        z_min = 0.05 → at most 95% decay per sample → keeps modes with
        time constants >= -dt_s / ln(0.05) ≈ 3 samples (physically: a mode
        that doesn't vanish within 3 samples).
      - freq in [freq_lo_hz, freq_hi_hz]: within GSSI 400 MHz passband.

    Args:
        segment:     1-D coda window (already windowed/tapered by caller).
        dt_s:        Sample interval in seconds.
        L:           Pencil parameter (default N//3, clamped to N//2).
        sv_threshold: Fraction of total SV energy kept for model order M.
        max_poles:   Hard cap on number of poles extracted.
        freq_lo_hz:  Lower frequency bound for valid poles (default 50 MHz).
        freq_hi_hz:  Upper frequency bound for valid poles (default 900 MHz).

    Returns dict with keys:
        poles_s    : complex array, s_k = alpha_k + j*omega_k  (rad/s)
        poles_z    : complex array, z_k = exp(s_k * dt_s)
        residues   : float array, |R_k| residue magnitudes
        freqs_hz   : float array, |Im(s_k)| / (2*pi)
        alphas_ns  : float array, Re(s_k) * 1e-9  (1/ns, negative = decaying)
        valid_mask : bool array, True for physically valid poles
    """
    y = np.asarray(segment, dtype=complex)
    N = len(y)
    if N < 10:
        empty = np.array([], dtype=complex)
        return dict(poles_s=empty, poles_z=empty, residues=np.array([]),
                    freqs_hz=np.array([]), alphas_ns=np.array([]),
                    valid_mask=np.array([], dtype=bool))

    if L is None:
        L = N // 3
    L = min(L, N // 2)

    # Hankel matrix via stride trick (read-only view, then copy for safety)
    Y = np.lib.stride_tricks.as_strided(
        y,
        shape=(N - L, L + 1),
        strides=(y.strides[0], y.strides[0]),
    ).copy()

    Y1, Y2 = Y[:, :-1], Y[:, 1:]

    U, S, Vh = np.linalg.svd(Y1, full_matrices=False)
    total = float(np.sum(S ** 2))
    if total == 0 or not np.isfinite(total):
        empty = np.array([], dtype=complex)
        return dict(poles_s=empty, poles_z=empty, residues=np.array([]),
                    freqs_hz=np.array([]), alphas_ns=np.array([]),
                    valid_mask=np.array([], dtype=bool))

    M = int(np.searchsorted(np.cumsum(S ** 2) / total, sv_threshold)) + 1
    M = max(1, min(M, max_poles, len(S)))

    # Drop near-zero singular values (noise floor guard)
    s_thresh = S[0] * 1e-10
    S_safe = np.where(S[:M] > s_thresh, S[:M], s_thresh)

    # Truncated pseudoinverse
    Y1_pinv = Vh[:M].conj().T @ np.diag(1.0 / S_safe) @ U[:, :M].conj().T
    try:
        z = np.linalg.eigvals(Y1_pinv @ Y2)
    except np.linalg.LinAlgError:
        empty = np.array([], dtype=complex)
        return dict(poles_s=empty, poles_z=empty, residues=np.array([]),
                    freqs_hz=np.array([]), alphas_ns=np.array([]),
                    valid_mask=np.array([], dtype=bool))

    # Continuous-time poles
    s = np.log(z + 1e-300) / dt_s

    # Physical validity (z-domain filter)
    z_mag = np.abs(z)
    freqs = np.abs(s.imag) / (2 * np.pi)
    valid = (z_mag > 0.05) & (z_mag < 1.0) & (freqs >= freq_lo_hz) & (freqs <= freq_hi_hz)

    # Residues via least-squares Vandermonde solve: Z @ R = y_real
    y_real = np.asarray(segment, dtype=float)
    n_arr  = np.arange(N, dtype=float)
    Z = (z[np.newaxis, :] ** n_arr[:, np.newaxis])
    R_complex, _, _, _ = np.linalg.lstsq(Z, y_real, rcond=None)
    residues_all = np.abs(R_complex)

    return dict(
        poles_s   = s,
        poles_z   = z,
        residues  = residues_all,
        freqs_hz  = freqs,
        alphas_ns = s.real * 1e-9,   # rad/s -> 1/ns
        valid_mask= valid,
    )



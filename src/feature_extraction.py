# Standard library
import logging
import warnings

# Third-party imports
import numpy as np
import pandas as pd
from scipy import signal as sp_signal
from scipy.fft import dct as _scipy_dct
from scipy.linalg import solve_toeplitz
from scipy.stats import skew, kurtosis

# Local imports
from src.constants import PC, SC
from src.signal_processing import (calculate_instantaneous_attributes,
                                   peak_relative_coda_gate, mpm_decompose)
from .logging_config import get_logger

def extract_features_from_signal(signal: np.ndarray, dt=None, signal_name: str = "sig",
                                 center_freq_hz=None, coda_seek_peak: bool = True,
                                 include_legacy_blocks: bool = False) -> pd.DataFrame:
    """Extract features directly from a 1D signal array."""
    if dt is None:
        _warn_default_dt()
        dt = PC.DEFAULT_DT
    time = np.arange(len(signal), dtype=float) * dt
    df = pd.DataFrame({"Time": time, signal_name: signal})
    return extract_features(df, dt=dt, center_freq_hz=center_freq_hz,
                            coda_seek_peak=coda_seek_peak,
                            include_legacy_blocks=include_legacy_blocks)


def _warn_default_dt():
    warnings.warn(
        f"extract_features called without dt — defaulting to {PC.DEFAULT_DT:.2e}s "
        f"(0.1 ns, the REAL-data time base). This is WRONG for synthetic .out "
        f"files (dt≈0.0311 ns) and mis-scales every frequency feature by ~3.2x. "
        f"Always pass dt read from the HDF5 'dt' attribute.",
        UserWarning, stacklevel=3,
    )


def extract_features(df, dt=None, center_freq_hz=None, coda_seek_peak: bool = True,
                     include_legacy_blocks: bool = False):
    """
    Extracts advanced time-domain, frequency-domain, and time-frequency features from GPR traces.

    v3 layout: a compact whole-trace block PLUS the full suite recomputed on the
    peak-normalized, peak-relative-gated CODA (``coda_*``) and an attenuation
    family (``att_*``). The coda is where the subsurface information lives —
    the direct pulse holds ~100% of trace energy and encodes the antenna, not
    the ground.

    Args:
        df: DataFrame with a 'Time' column and one column per trace.
        dt: Time step in seconds. ALWAYS pass it explicitly (read from the .out
            HDF5 'dt' attribute); the 0.1 ns fallback is only correct for the
            real field CSVs and a loud warning is emitted when it is used.
        center_freq_hz: Source centre frequency, used for the relative spectral
            band edges (SC.BAND_LOW_FRAC/BAND_HIGH_FRAC). If None it is
            estimated per-trace as the dominant spectral frequency.
        coda_seek_peak: Passed to the peak-relative coda gate. Use False for
            traces that already start at the direct-pulse peak (processed real
            field traces).
        include_legacy_blocks: Re-enable the legacy whole-trace grid (480),
            slice (28) and decile features. They are amplitude images of the
            direct pulse — high in-world signal, near-zero transfer value —
            kept only so the old baseline can be rebuilt for A/B comparison.

    Output includes meta_* provenance columns (meta_feature_version, meta_dt_ns,
    meta_center_freq_mhz, meta_includes_legacy). These are NOT waveform
    features — exclude any column starting with 'meta_' (and 'Signal') from
    training matrices.
    """
    logger = get_logger(__name__)
    
    if df.empty:
        logger.warning("DataFrame is empty. Cannot extract features.")
        return pd.DataFrame()

    if dt is None:
        _warn_default_dt()
        dt = PC.DEFAULT_DT

    features_list = []
    
    # Identify metadata columns
    metadata_cols = [col for col in df.columns if col in ['gprMax', 'Title', 'Iterations', 'nx_ny_nz', 'dx_dy_dz', 'dt', 'srcsteps', 'rxsteps', 'nsrc', 'nrx']]
    metadata_values = {col: df[col].iloc[0] for col in metadata_cols}
    
    for col in df.columns:
        if col == 'Time' or col in metadata_cols:
            continue
            
        signal = df[col].values

        # 1. Time Domain Stats (deciles are legacy: direct-pulse percentiles)
        time_feats = _extract_time_stats(signal, include_deciles=include_legacy_blocks)

        # 2. Hilbert Transform (Envelope) Stats
        hilbert_feats, analytic_signal = _extract_hilbert_stats(
            signal, dt, include_deciles=include_legacy_blocks)
        
        # 3. Frequency Domain (also resolves the centre frequency used for bands)
        freq_feats, fc_used = _extract_frequency_features(signal, dt, center_freq_hz)

        # 3.5 Wavelet / multiresolution (widths in physical ns, converted by dt)
        wavelet_feats = _extract_wavelet_features(signal, dt)

        # 4. STFT (Time-Frequency; window in physical ns, bands relative to fc)
        stft_feats = _extract_stft_features(signal, dt, fc_used)
        
        # 5./6. Legacy whole-trace slice + grid blocks (direct-pulse images)
        slice_feats = _extract_slice_features(signal) if include_legacy_blocks else {}
        grid_feats = (_extract_grid_features(signal, analytic_signal)
                      if include_legacy_blocks else {})

        # 7. Windowed (peak-relative coda gate) indicators — Li et al. (2023), Shapovalov et al. (2026)
        window_feats = _extract_window_features(signal, analytic_signal, dt,
                                                seek_peak=coda_seek_peak)

        # 8. Time-domain energy-integration curve — Li et al. (2023)
        energy_curve_feats = _extract_energy_curve_features(signal)

        # 9. Coda-first suite: full feature set on the peak-normalized gated
        #    coda (coda_*) + attenuation family (att_*) — Li (2025) S-transform
        #    decay, Mbubia (2024) damping direction.
        coda_feats = _extract_coda_suite(signal, dt, fc_used, seek_peak=coda_seek_peak)

        # 10. Real cepstrum + quefrency — Bogert et al. (1963); Oppenheim & Schafer (2010)
        cepstral_feats = _extract_cepstral_features(signal, dt)

        # 11. GPR filterbank / GPR-MFCC — Davis & Mermelstein (1980)
        filterbank_feats = _extract_filterbank_features(signal, dt, fc_used)

        # Combine
        features = {
            'Signal': col,
            **time_feats,
            **hilbert_feats,
            **freq_feats,
            **wavelet_feats,
            **stft_feats,
            **slice_feats,
            **grid_feats,
            **window_feats,
            **energy_curve_feats,
            **coda_feats,
            **cepstral_feats,
            **filterbank_feats,
        }

        # Provenance (meta_* = NOT features; exclude from training matrices)
        features.update({
            'meta_feature_version': SC.FEATURE_VERSION,
            'meta_dt_ns': dt * SC.NS_PER_SEC,
            'meta_center_freq_mhz': fc_used / 1e6,
            'meta_includes_legacy': bool(include_legacy_blocks),
        })

        # Add metadata
        features.update(metadata_values)
        features_list.append(features)

    return pd.DataFrame(features_list)

def _extract_time_stats(signal: np.ndarray, include_deciles: bool = True) -> dict:
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

    # Deciles (legacy whole-trace block — amplitude percentiles)
    if include_deciles:
        deciles = np.percentile(signal, np.arange(10, 100, 10))
        stats.update({f'decile_{i+1}0': d for i, d in enumerate(deciles)})

    return stats


def _extract_hilbert_stats(signal: np.ndarray, dt: float, include_deciles: bool = True) -> tuple:
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

    if include_deciles:
        deciles = np.percentile(envelope, np.arange(10, 100, 10))
        stats.update({f'hilbert_decile_{i+1}0': d for i, d in enumerate(deciles)})

    return stats, analytic_signal

def _extract_frequency_features(signal: np.ndarray, dt: float, center_freq_hz=None) -> tuple:
    """Calculates Fourier transform metrics.

    Band edges are RELATIVE to the centre frequency fc (given, or estimated as
    the dominant spectral frequency): low < BAND_LOW_FRAC*fc <= mid <
    BAND_HIGH_FRAC*fc <= high. The legacy absolute cutoffs (500 MHz / 1.5 GHz)
    were degenerate for 400 MHz data (all energy in "low").

    NOTE: mean_frequency / median_frequency / spectral_flatness definitions are
    intentionally UNCHANGED — they are the metrics behind the real-data
    median_freq-vs-FI result and must stay comparable across corpora.

    Returns:
        (features_dict, fc_used_hz)
    """
    fft_vals = np.fft.fft(signal)
    fft_spectrum = np.abs(fft_vals)
    freqs = np.fft.fftfreq(len(signal), d=dt)

    pos_mask = freqs >= 0
    fft_spectrum = fft_spectrum[pos_mask]
    freqs = freqs[pos_mask]

    area_fourier = np.sum(fft_spectrum)
    max_power = np.max(fft_spectrum)

    # Dominant frequency, excluding the DC bin (DC offset is not a "frequency")
    nz = freqs > 0
    if np.any(nz) and np.max(fft_spectrum[nz]) > 0:
        dominant_frequency = float(freqs[nz][np.argmax(fft_spectrum[nz])])
    else:
        dominant_frequency = 0.0

    # Centre frequency for the relative band edges
    fc = float(center_freq_hz) if center_freq_hz else dominant_frequency

    # Heuristics
    cumulative = np.cumsum(fft_spectrum)
    if area_fourier > 0:
        mean_freq = np.sum(freqs * fft_spectrum) / area_fourier
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

    # Relative band energies (fall back to legacy absolute cutoffs if fc=0)
    f_lo = SC.BAND_LOW_FRAC * fc if fc > 0 else SC.FREQ_LOW_CUTOFF
    f_hi = SC.BAND_HIGH_FRAC * fc if fc > 0 else SC.FREQ_MID_CUTOFF
    energy_low = np.sum(fft_spectrum[freqs < f_lo])
    energy_mid = np.sum(fft_spectrum[(freqs >= f_lo) & (freqs < f_hi)])
    energy_high = np.sum(fft_spectrum[freqs >= f_hi])

    high_low_energy_ratio = energy_high / energy_low if energy_low > 0 else 0
    high_mid_energy_ratio = energy_high / energy_mid if energy_mid > 0 else 0
    mid_low_energy_ratio = energy_mid / energy_low if energy_low > 0 else 0

    rolloff_threshold = 0.85 * area_fourier
    rolloff_idx = np.searchsorted(cumulative, rolloff_threshold)
    spectral_rolloff = freqs[min(rolloff_idx, len(freqs) - 1)]

    # Spectral slope: log-amplitude fit restricted to the OCCUPIED band
    # (5%-95% of cumulative spectral amplitude). The legacy fit spanned the
    # whole axis to Nyquist (16 GHz on sim traces), so it was dominated by the
    # empty noise floor. Units: dB-like decade change per Hz.
    spectral_slope = 0.0
    if area_fourier > 0 and len(freqs) > 3:
        i_lo = int(np.searchsorted(cumulative, 0.05 * area_fourier))
        i_hi = int(np.searchsorted(cumulative, 0.95 * area_fourier))
        if i_hi - i_lo >= 3:
            band_f = freqs[i_lo:i_hi]
            band_s = np.log10(fft_spectrum[i_lo:i_hi] + SC.LOG_EPSILON)
            spectral_slope = float(np.polyfit(band_f, band_s, 1)[0])

    spectral_skewness = skew(fft_spectrum)
    spectral_kurtosis = kurtosis(fft_spectrum)
    dominant_energy_fraction = max_power / (area_fourier + SC.LOG_EPSILON)

    feats = {
        'area_fourier': area_fourier,
        'fourier_peak_max': max_power,
        'fourier_standard_deviation': np.std(fft_spectrum),
        'dominant_frequency': dominant_frequency,
        'bandwidth': bandwidth,
        'mean_frequency': mean_freq,
        'median_frequency': median_freq,
        'spectral_entropy': spectral_entropy,
        'spectral_flatness': flatness,
        'dominant_energy_fraction': dominant_energy_fraction,
        'spectral_rolloff': spectral_rolloff,
        'spectral_slope': spectral_slope,
        'spectral_skewness': spectral_skewness,
        'spectral_kurtosis': spectral_kurtosis,
        'high_low_energy_ratio': high_low_energy_ratio,
        'high_mid_energy_ratio': high_mid_energy_ratio,
        'mid_low_energy_ratio': mid_low_energy_ratio
    }
    return feats, fc


def _ricker_wavelet(points: int, a: float) -> np.ndarray:
    """Generate a Ricker (Mexican hat) wavelet."""
    t = np.linspace(-(points - 1) / 2, (points - 1) / 2, points)
    return (1 - (t ** 2) / (a ** 2)) * np.exp(-(t ** 2) / (2 * a ** 2))


def _extract_wavelet_features(signal: np.ndarray, dt: float) -> dict:
    """Calculates multiresolution energy features using several Ricker wavelets.

    Widths are specified in PHYSICAL time (SC.WAVELET_WIDTHS_NS) and converted
    to samples by dt, so the same feature measures the same physical scale on
    any time base. (Legacy sample widths made a width-8 wavelet 0.25 ns on sim
    but 0.8 ns on real — an artificial domain shift.) wavelet_peak_scale is
    now reported in ns.
    """
    widths_ns = np.asarray(SC.WAVELET_WIDTHS_NS, dtype=float)
    widths = widths_ns * 1e-9 / dt  # ricker width parameter in samples (float)
    energy_per_scale = np.zeros(len(widths), dtype=float)

    if signal.size > 0:
        for idx, width in enumerate(widths):
            points = max(int(width * 8 + 1), 3)
            wavelet = _ricker_wavelet(points, float(width))
            response = sp_signal.fftconvolve(signal, wavelet, mode='same')
            energy_per_scale[idx] = np.sum(np.abs(response) ** 2)

    total_energy = np.sum(energy_per_scale)
    energy_probs = energy_per_scale / total_energy if total_energy > 0 else np.zeros_like(energy_per_scale)
    wavelet_entropy = -np.sum(energy_probs * np.log(energy_probs + SC.LOG_EPSILON))

    return {
        'wavelet_total_energy': total_energy,
        'wavelet_peak_scale': float(widths_ns[np.argmax(energy_per_scale)]) if energy_per_scale.size > 0 else 0,
        'wavelet_energy_mean': np.mean(energy_per_scale),
        'wavelet_energy_std': np.std(energy_per_scale),
        'wavelet_energy_skewness': skew(energy_per_scale),
        'wavelet_energy_kurtosis': kurtosis(energy_per_scale),
        'wavelet_entropy': wavelet_entropy,
        'wavelet_high_low_ratio': np.sum(energy_per_scale[3:]) / (np.sum(energy_per_scale[:3]) + SC.LOG_EPSILON)
    }


def _extract_stft_features(signal: np.ndarray, dt: float, center_freq_hz: float = 0.0) -> dict:
    """Calculates Time-Frequency features using STFT.

    The window is specified in PHYSICAL time (SC.STFT_NPERSEG_NS) and converted
    to samples by dt, so time-frequency resolution is identical across time
    bases (legacy 64 samples = 2 ns on sim vs 6.4 ns on real). Band edges are
    relative to the centre frequency, matching _extract_frequency_features.
    """
    nperseg = int(round(SC.STFT_NPERSEG_NS * 1e-9 / dt))
    nperseg = max(8, min(nperseg, len(signal)))
    noverlap = nperseg // 2
    f_stft, _, Zxx = sp_signal.stft(signal, fs=1/dt, nperseg=nperseg, noverlap=noverlap)
    stft_mag = np.abs(Zxx)

    fc = float(center_freq_hz)
    f_lo = SC.BAND_LOW_FRAC * fc if fc > 0 else SC.FREQ_LOW_CUTOFF
    f_hi = SC.BAND_HIGH_FRAC * fc if fc > 0 else SC.FREQ_MID_CUTOFF
    mask_low = (f_stft < f_lo)
    mask_mid = (f_stft >= f_lo) & (f_stft < f_hi)
    mask_high = (f_stft >= f_hi)
    
    energy_low = np.sum(stft_mag[mask_low, :], axis=0)
    energy_mid = np.sum(stft_mag[mask_mid, :], axis=0)
    energy_high = np.sum(stft_mag[mask_high, :], axis=0)
    
    total_low = np.sum(energy_low)
    total_mid = np.sum(energy_mid)
    total_high = np.sum(energy_high)
    total_energy = total_low + total_mid + total_high
    band_energy = np.array([total_low, total_mid, total_high], dtype=float)
    band_prob = band_energy / total_energy if total_energy > 0 else np.zeros_like(band_energy)
    stft_band_entropy = -np.sum(band_prob * np.log(band_prob + SC.LOG_EPSILON))

    # Centroids over time
    centroids_t = []
    for t_idx in range(stft_mag.shape[1]):
        spec = stft_mag[:, t_idx]
        total = np.sum(spec)
        centroids_t.append(np.sum(f_stft * spec) / total if total > 0 else 0)
        
    return {
        'stft_energy_low_mean': np.mean(energy_low),
        'stft_energy_low_std': np.std(energy_low),
        'stft_energy_low_max': np.max(energy_low),
        'stft_energy_low_skewness': skew(energy_low),
        'stft_energy_low_kurtosis': kurtosis(energy_low),
        'stft_energy_mid_mean': np.mean(energy_mid),
        'stft_energy_mid_std': np.std(energy_mid),
        'stft_energy_mid_max': np.max(energy_mid),
        'stft_energy_mid_skewness': skew(energy_mid),
        'stft_energy_mid_kurtosis': kurtosis(energy_mid),
        'stft_energy_high_mean': np.mean(energy_high),
        'stft_energy_high_std': np.std(energy_high),
        'stft_energy_high_max': np.max(energy_high),
        'stft_energy_high_skewness': skew(energy_high),
        'stft_energy_high_kurtosis': kurtosis(energy_high),
        'stft_high_low_energy_ratio': total_high / (total_low + SC.LOG_EPSILON),
        'stft_high_mid_energy_ratio': total_high / (total_mid + SC.LOG_EPSILON),
        'stft_mid_low_energy_ratio': total_mid / (total_low + SC.LOG_EPSILON),
        'stft_band_entropy': stft_band_entropy,
        'stft_centroid_mean': np.mean(centroids_t),
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

def _extract_window_features(signal: np.ndarray, analytic_signal: np.ndarray, dt: float,
                             seek_peak: bool = True) -> dict:
    """Literature indicators restricted to the ballast/coda time gate.

    Several ballast-fouling studies compute their discriminators over the ballast
    layer (a time gate) rather than the whole trace: integral of |amplitude| (StAb),
    Hilbert-envelope area, zero-crossing count (CrossNum) and inflection count
    (InflecNum). See Li et al. (2023), Remote Sens. 15, 3437; Shapovalov et al. (2026),
    IJTST 21, 286-305. These are the gated counterparts of the full-trace ``area_signal``,
    ``area_hilbert``, ``number_zeros`` and ``second_derivative`` features.

    The gate is PEAK-RELATIVE (signal_processing.peak_relative_coda_gate): it
    opens CODA_GATE_START_AFTER_PEAK_NS after the direct-pulse peak for
    CODA_GATE_LENGTH_NS, replacing the legacy absolute 6-16 ns window which
    selected different physics per geometry/domain. Use seek_peak=False for
    traces that already start at the peak (processed real field traces).
    """
    from scipy.signal import find_peaks

    keys = [
        'win_area_signal', 'win_area_hilbert', 'win_rms', 'win_std',
        'win_energy_fraction', 'win_number_zeros', 'win_inflection_count',
        'win_peak_count', 'win_hilbert_mean', 'win_hilbert_peak_max'
    ]

    n = len(signal)
    t_ns = np.arange(n) * dt * SC.NS_PER_SEC
    mask, _ = peak_relative_coda_gate(signal, dt, seek_peak=seek_peak)

    # Degenerate gate (trace too short / window out of range): return zeros, never crash.
    if np.count_nonzero(mask) < 3:
        return {k: 0.0 for k in keys}

    w = signal[mask]
    env = np.abs(analytic_signal)[mask]
    tw = t_ns[mask]

    total_energy = np.sum(signal ** 2)
    win_energy = np.sum(w ** 2)
    rms_val = np.sqrt(np.mean(w ** 2))

    if np.std(w) > 0:
        peaks, _ = find_peaks(w, height=np.std(w) * 0.5)
        peak_count = len(peaks)
    else:
        peak_count = 0

    inflections = int(np.count_nonzero(np.diff(np.signbit(np.diff(w, n=2))))) if w.size > 2 else 0

    return {
        'win_area_signal': float(np.sum(np.abs(w))),
        'win_area_hilbert': float(np.trapezoid(env, tw)),
        'win_rms': float(rms_val),
        'win_std': float(np.std(w)),
        'win_energy_fraction': float(win_energy / total_energy) if total_energy > 0 else 0.0,
        'win_number_zeros': int(np.count_nonzero(np.diff(np.signbit(w)))),
        'win_inflection_count': inflections,
        'win_peak_count': int(peak_count),
        'win_hilbert_mean': float(np.mean(env)),
        'win_hilbert_peak_max': float(np.max(env))
    }


def _extract_energy_curve_features(signal: np.ndarray,
                                   fractions: tuple = SC.ENERGY_CURVE_FRACTIONS) -> dict:
    """Time-domain cumulative-energy-curve descriptors (energy-integration curve).

    The normalized cumulative energy curve is the time-domain analogue of the FFT
    ``spectral_rolloff``: it encodes how quickly trace energy accumulates, which the
    ballast-fouling literature links to fouling-driven attenuation (heavier fouling →
    faster early decay → energy accumulates earlier). See Li et al. (2023), which uses a
    smoothed/normalized energy-integration curve as a primary fouling discriminator.

    Returned positions are normalized to [0, 1] over the trace length so they are
    comparable across traces of different length.
    """
    n = len(signal)
    keys = [f'energy_time_q{int(f * 100)}' for f in fractions] + \
           ['energy_centroid_time', 'early_late_energy_ratio', 'energy_curve_auc']

    if n < 2:
        return {k: 0.0 for k in keys}

    energy = signal ** 2
    total = np.sum(energy)
    if total <= 0:
        return {k: 0.0 for k in keys}

    cum_norm = np.cumsum(energy) / total

    feats = {}
    for f in fractions:
        idx = int(np.searchsorted(cum_norm, f))
        feats[f'energy_time_q{int(f * 100)}'] = float(min(idx, n - 1) / (n - 1))

    idx_arr = np.arange(n)
    feats['energy_centroid_time'] = float(np.sum(idx_arr * energy) / total / (n - 1))

    half = n // 2
    early = np.sum(energy[:half])
    late = np.sum(energy[half:])
    feats['early_late_energy_ratio'] = float(early / late) if late > 0 else 0.0

    # Area under the normalized cumulative-energy curve in [0, 1]:
    # high → energy concentrated early (fouled-like), low → energy concentrated late.
    feats['energy_curve_auc'] = float(np.mean(cum_norm))

    return feats


def _extract_grid_features(signal: np.ndarray, analytic_signal: np.ndarray, grid_size: int = SC.DEFAULT_GRID_SIZE) -> dict:
    """Resamples signal to a fixed grid for image-like features."""
    res_sig = sp_signal.resample(signal, grid_size)
    res_analytic = sp_signal.resample(analytic_signal, grid_size)
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


def _finite_or_zero(d: dict) -> dict:
    """Replace non-finite feature values with 0.0 (degenerate-input safety)."""
    out = {}
    for k, v in d.items():
        try:
            fv = float(v)
        except (TypeError, ValueError):
            out[k] = v
            continue
        out[k] = fv if np.isfinite(fv) else 0.0
    return out


def _extract_mpm_features(segment: np.ndarray, dt: float,
                          n_poles: int = 6,
                          freq_lo_hz: float = 50e6,
                          freq_hi_hz: float = 900e6) -> dict:
    """MPM pole features for the coda segment (Mbubia et al. 2024).

    Extracts the top-n_poles modes sorted by residue magnitude (most energetic
    first). Each mode contributes three features:
      mpm_pole_{k}_alpha_ns  : damping rate 1/ns (negative = decaying;
                               more negative = faster decay = higher sigma)
      mpm_pole_{k}_freq_mhz  : oscillation frequency MHz
      mpm_pole_{k}_residue   : normalized residue (energy weight, 0-1)

    Plus summary features:
      mpm_mean_alpha_ns      : residue-weighted mean alpha across all valid poles
      mpm_dominant_freq_mhz  : frequency of the highest-residue mode
      mpm_n_valid            : count of physically valid poles found

    Zero-padding is applied when fewer than n_poles valid poles are found so
    the feature vector length is always 3*n_poles + 3 = 21 (default n_poles=6).
    """
    keys_per_pole = [f'mpm_pole_{k}_{s}'
                     for k in range(n_poles)
                     for s in ('alpha_ns', 'freq_mhz', 'residue')]
    summary_keys  = ['mpm_mean_alpha_ns', 'mpm_dominant_freq_mhz', 'mpm_n_valid']
    zero_result   = {k: 0.0 for k in keys_per_pole + summary_keys}

    if len(segment) < 10:
        return zero_result

    # Taper to reduce edge leakage
    seg = segment * np.hanning(len(segment))
    dec = mpm_decompose(seg, dt, freq_lo_hz=freq_lo_hz, freq_hi_hz=freq_hi_hz)

    valid    = dec['valid_mask']
    n_valid  = int(np.sum(valid))
    if n_valid == 0:
        return {**zero_result, 'mpm_n_valid': 0.0}

    alphas   = dec['alphas_ns'][valid]       # 1/ns, negative
    freqs    = dec['freqs_hz'][valid] / 1e6  # MHz
    residues = dec['residues'][valid]

    # Normalise residues to [0, 1]
    res_sum  = float(np.sum(residues))
    res_norm = residues / res_sum if res_sum > 0 else residues

    # Sort by residue descending (most energetic mode first)
    order = np.argsort(res_norm)[::-1]
    alphas, freqs, res_norm = alphas[order], freqs[order], res_norm[order]

    # Summary
    feats = {}
    feats['mpm_n_valid']           = float(n_valid)
    feats['mpm_mean_alpha_ns']     = float(np.average(alphas, weights=res_norm))
    feats['mpm_dominant_freq_mhz'] = float(freqs[0])

    # Per-pole (zero-padded to n_poles)
    for k in range(n_poles):
        if k < n_valid:
            feats[f'mpm_pole_{k}_alpha_ns'] = float(alphas[k])
            feats[f'mpm_pole_{k}_freq_mhz'] = float(freqs[k])
            feats[f'mpm_pole_{k}_residue']  = float(res_norm[k])
        else:
            feats[f'mpm_pole_{k}_alpha_ns'] = 0.0
            feats[f'mpm_pole_{k}_freq_mhz'] = 0.0
            feats[f'mpm_pole_{k}_residue']  = 0.0

    return feats


def _extract_coda_suite(signal: np.ndarray, dt: float, center_freq_hz: float,
                        seek_peak: bool = True) -> dict:
    """Full feature suite on the peak-normalized, peak-relative-gated coda.

    The direct pulse holds ~100% of trace energy but encodes the antenna; the
    subsurface (fouling) information lives in the coda at <0.5% amplitude.
    This recomputes every feature block on the gated coda segment, normalized
    to its own peak so the features are amplitude-scale-invariant (sim and
    real differ by orders of magnitude in raw amplitude). Keys are prefixed
    ``coda_``; the attenuation family (``att_*``) is computed here too.

    The 160-point coda grid is the aligned-coda waveform itself: 16 ns
    resampled to 160 cells = the 0.1 ns common grid used by the aligned
    sim2real pipeline, with identical physical support on any time base.
    """
    mask, _ = peak_relative_coda_gate(signal, dt, seek_peak=seek_peak)
    segment = np.asarray(signal, dtype=float)[mask]
    if segment.size < 16:
        segment = np.zeros(64)  # degenerate: stable keys, all-zero values
    m = np.max(np.abs(segment))
    if m > 0:
        segment = segment / m

    time_feats = _extract_time_stats(segment)
    hil_feats, analytic = _extract_hilbert_stats(segment, dt)
    freq_feats, _ = _extract_frequency_features(segment, dt, center_freq_hz)
    wav_feats = _extract_wavelet_features(segment, dt)
    stft_feats = _extract_stft_features(segment, dt, center_freq_hz)
    slice_feats = _extract_slice_features(segment)
    grid_feats = _extract_grid_features(segment, analytic)
    energy_feats = _extract_energy_curve_features(segment)

    attrs = calculate_instantaneous_attributes(segment, dt, use_mirroring=True)
    att_feats = _extract_attenuation_features(segment, dt, center_freq_hz, attrs)
    mpm_feats = _extract_mpm_features(segment, dt)
    cep_feats = _extract_cepstral_features(segment, dt)
    fb_feats  = _extract_filterbank_features(segment, dt, center_freq_hz)
    lpc_feats = _extract_lpc_features(segment, dt)

    out = {}
    for d in (time_feats, hil_feats, freq_feats, wav_feats, stft_feats,
              slice_feats, grid_feats, energy_feats, cep_feats, fb_feats):
        out.update({f'coda_{k}': v for k, v in d.items()})
    out.update(att_feats)   # att_* already namespaced
    out.update(mpm_feats)   # mpm_* already namespaced
    out.update(lpc_feats)   # lpc_* already namespaced
    return _finite_or_zero(out)


def _extract_attenuation_features(segment: np.ndarray, dt: float,
                                  center_freq_hz: float, attrs: dict) -> dict:
    """Attenuation-rate family on the gated coda (``att_*``).

    Physics: fouling raises conductivity by orders of magnitude (Mbubia 2024:
    sigma 1e-5 -> 1e-2 S/m), so fouled beds attenuate faster — Li (2025) shows
    the high-frequency energy of heavily fouled ballast dies by ~6-8 ns vs
    ~12-14 ns for clean. These features measure that decay directly:

      att_env_decay_rate        log-envelope slope (1/ns; more negative = faster)
      att_instfreq_*            instantaneous-frequency stats over the coda
      att_band_{low,mid,high}_decay   log10 STFT band-energy slope vs time
      att_{low,mid,high}_die_time_ns  time after gate start when band energy
                                      first falls below 10% of its peak
      att_centroid_slope_mhz_ns spectral-centroid drift (MHz/ns; negative =
                                downshift over time, the attenuation signature)
    """
    keys = ['att_env_decay_rate', 'att_instfreq_mean_mhz', 'att_instfreq_std_mhz',
            'att_instfreq_slope_mhz_ns',
            'att_band_low_decay', 'att_band_mid_decay', 'att_band_high_decay',
            'att_low_die_time_ns', 'att_mid_die_time_ns', 'att_high_die_time_ns',
            'att_centroid_slope_mhz_ns']
    feats = dict.fromkeys(keys, 0.0)
    n = segment.size
    if n < 16:
        return feats
    t_ns = np.arange(n) * dt * SC.NS_PER_SEC

    env = attrs['envelope']
    emax = float(np.max(env))
    if emax > 0:
        valid = env > 0.02 * emax
        if np.count_nonzero(valid) >= 8:
            feats['att_env_decay_rate'] = float(np.polyfit(
                t_ns[valid], np.log(env[valid] / emax + SC.LOG_EPSILON), 1)[0])
        # Instantaneous frequency is only meaningful where the envelope is
        # well above the noise floor.
        good = env > 0.1 * emax
        if np.count_nonzero(good) >= 8:
            f_mhz = attrs['frequency'][good] / 1e6
            feats['att_instfreq_mean_mhz'] = float(np.mean(f_mhz))
            feats['att_instfreq_std_mhz'] = float(np.std(f_mhz))
            feats['att_instfreq_slope_mhz_ns'] = float(
                np.polyfit(t_ns[good], f_mhz, 1)[0])

    # STFT band decays, die-times and centroid drift
    nperseg = int(round(SC.STFT_NPERSEG_NS * 1e-9 / dt))
    nperseg = max(8, min(nperseg, n))
    f_st, tt, Zxx = sp_signal.stft(segment, fs=1/dt, nperseg=nperseg,
                                   noverlap=nperseg // 2)
    mag = np.abs(Zxx)
    tt_ns = tt * SC.NS_PER_SEC

    fc = float(center_freq_hz)
    f_lo = SC.BAND_LOW_FRAC * fc if fc > 0 else SC.FREQ_LOW_CUTOFF
    f_hi = SC.BAND_HIGH_FRAC * fc if fc > 0 else SC.FREQ_MID_CUTOFF
    bands = {'low': f_st < f_lo,
             'mid': (f_st >= f_lo) & (f_st < f_hi),
             'high': f_st >= f_hi}
    for name, bmask in bands.items():
        e_t = np.sum(mag[bmask, :], axis=0)
        if e_t.size >= 3 and np.max(e_t) > 0:
            feats[f'att_band_{name}_decay'] = float(np.polyfit(
                tt_ns, np.log10(e_t / np.max(e_t) + SC.LOG_EPSILON), 1)[0])
            pk = int(np.argmax(e_t))
            below = np.where(e_t[pk:] < 0.1 * e_t[pk])[0]
            feats[f'att_{name}_die_time_ns'] = (float(tt_ns[pk + below[0]])
                                                if below.size else float(tt_ns[-1]))

    tot = np.sum(mag, axis=0)
    if tt_ns.size >= 3 and np.max(tot) > 0:
        cent_mhz = (f_st @ mag) / (tot + SC.LOG_EPSILON) / 1e6
        feats['att_centroid_slope_mhz_ns'] = float(np.polyfit(tt_ns, cent_mhz, 1)[0])

    return _finite_or_zero(feats)


def _extract_cepstral_features(signal: np.ndarray, dt: float,
                                n_coef: int = 12) -> dict:
    """Real cepstrum + quefrency features.

    The real cepstrum c[q] = Re{IFFT(log|FFT(x)|)} lifts periodicity in the
    log-spectrum to the quefrency domain.  For a GPR trace the dominant
    quefrency peak in 1–10 ns encodes the two-way travel time to the first
    reflector (= layer spacing at the propagation velocity). This gives a
    physics-interpretable, amplitude-scale-invariant depth proxy.

    Reference:
        Bogert, Healy & Tukey (1963) Proc. Symp. Time Series Analysis.
        Oppenheim & Schafer (2010) Discrete-Time Signal Processing, §12.
        Claerbout (1985) Fundamentals of Geophysical Data Processing.
    """
    n = len(signal)
    keys = ([f'cep_{k}' for k in range(1, n_coef + 1)] +
            ['cep_quefrency_peak_ns', 'cep_quefrency_energy_fraction',
             'cep_rahmonic_ratio'])
    zeros = {k: 0.0 for k in keys}
    if n < 16:
        return zeros

    fft_mag = np.abs(np.fft.rfft(signal, n=n))
    log_spec = np.log(fft_mag + SC.LOG_EPSILON)
    # irfft of a real log-spectrum yields the real cepstrum; n= ensures exact length
    cepstrum = np.fft.irfft(log_spec, n=n)

    feats = {}
    for k in range(1, n_coef + 1):
        feats[f'cep_{k}'] = float(cepstrum[k]) if k < len(cepstrum) else 0.0

    quefrency_ns = np.arange(n) * dt * SC.NS_PER_SEC

    # Subsurface window: 1–10 ns = reflector depths ~0.15–1.5 m at ε=3.45
    sub_mask = (quefrency_ns >= 1.0) & (quefrency_ns <= 10.0)
    direct_mask = quefrency_ns < 1.0
    total_cep_energy = float(np.sum(cepstrum ** 2)) + SC.LOG_EPSILON
    if np.any(sub_mask):
        sub_abs = np.abs(cepstrum[sub_mask])
        sub_energy = float(np.sum(sub_abs ** 2))
        direct_energy = float(np.sum(cepstrum[direct_mask] ** 2)) if np.any(direct_mask) else 0.0
        feats['cep_quefrency_peak_ns'] = float(quefrency_ns[sub_mask][np.argmax(sub_abs)])
        feats['cep_quefrency_energy_fraction'] = sub_energy / total_cep_energy
        feats['cep_rahmonic_ratio'] = sub_energy / (direct_energy + SC.LOG_EPSILON)
    else:
        feats['cep_quefrency_peak_ns'] = 0.0
        feats['cep_quefrency_energy_fraction'] = 0.0
        feats['cep_rahmonic_ratio'] = 0.0

    return feats


def _extract_lpc_features(segment: np.ndarray, dt: float,
                           order: int = 8, n_par: int = 4) -> dict:
    """LPC residual features on the gated coda.

    Fits an order-p all-pole AR model (linear predictive coding) via the
    Yule-Walker equations and filters the signal through the predictor
    error filter A(z) = 1 + a1*z⁻¹ + … + ap*z⁻ᵖ.  The residual encodes
    the part of the coda that cannot be explained by linear autoregression —
    in GPR this is incoherent scatter from fines and voids. Heavy fouling
    adds unpredictable fine-scale heterogeneity → higher residual energy and
    kurtosis.

    Reference:
        Makhoul, J. (1975) Proc. IEEE 63(4), 561–580.
        Atal & Schroeder (1967) J. Acoust. Soc. Am. 42, 1373.
    """
    keys = ([f'lpc_par_{k}' for k in range(1, n_par + 1)] +
            ['lpc_residual_rms', 'lpc_residual_kurtosis',
             'lpc_residual_energy_frac', 'lpc_pred_error'])
    zeros = {k: 0.0 for k in keys}

    n = len(segment)
    if n < order + 4:
        return zeros

    peak = float(np.max(np.abs(segment)))
    if peak == 0.0:
        return zeros
    seg = segment / peak

    # Autocorrelation lags 0 … order
    corr = np.array([float(np.dot(seg[:n - k], seg[k:])) / n
                     for k in range(order + 1)])
    if corr[0] <= 0:
        return zeros

    # Solve Yule-Walker: Toeplitz(corr[0:p]) * a = -corr[1:p+1]
    try:
        a = solve_toeplitz(corr[:order], -corr[1:order + 1])
    except Exception:
        return zeros

    # Prediction error filter A(z) applied via causal IIR (all-zeros part only)
    A = np.concatenate([[1.0], a])
    residual = sp_signal.lfilter(A, [1.0], seg)

    total_energy = float(np.sum(seg ** 2))
    res_energy = float(np.sum(residual ** 2))

    feats = {
        'lpc_residual_rms': float(np.sqrt(np.mean(residual ** 2))),
        'lpc_residual_kurtosis': float(kurtosis(residual)),
        'lpc_residual_energy_frac': res_energy / (total_energy + SC.LOG_EPSILON),
        'lpc_pred_error': res_energy / (corr[0] * n + SC.LOG_EPSILON),
    }
    for k in range(n_par):
        feats[f'lpc_par_{k + 1}'] = float(a[k]) if k < len(a) else 0.0

    return feats


def _extract_filterbank_features(signal: np.ndarray, dt: float,
                                  center_freq_hz: float,
                                  n_filters: int = 12) -> dict:
    """Linear triangular filterbank + DCT (GPR-MFCC).

    Applies n_filters triangular bandpass filters uniformly spaced in
    frequency across the occupied GPR band (½·BAND_LOW_FRAC·fc to
    2·BAND_HIGH_FRAC·fc), log-compresses the filter energies, then applies
    a type-II DCT to yield compact cepstral coefficients (GPR-MFCC).
    Unlike speech MFCCs the frequency axis is LINEAR (not Mel) because GPR
    has no perceptual weighting requirement and propagation physics are
    linear in frequency.

    Returns:
        fb_energy_0 … fb_energy_{n-1}  : log filterbank energies
        gpr_mfcc_1  … gpr_mfcc_n       : DCT of log-filterbank (skip coef 0 = mean)

    Reference:
        Davis & Mermelstein (1980) IEEE Trans. ASSP 28(4), 357–366 (MFCCs).
        Adapted for GPR: linear frequency scale, no pre-emphasis.
    """
    keys = ([f'fb_energy_{k}' for k in range(n_filters)] +
            [f'gpr_mfcc_{k}' for k in range(1, n_filters + 1)])
    zeros = {k: 0.0 for k in keys}

    n = len(signal)
    if n < 16:
        return zeros

    fft_mag = np.abs(np.fft.rfft(signal, n=n))
    freqs = np.fft.rfftfreq(n, d=dt)

    fc = float(center_freq_hz) if center_freq_hz and center_freq_hz > 0 else 400e6
    f_min = max(SC.BAND_LOW_FRAC * 0.5 * fc, freqs[1] if len(freqs) > 1 else 1.0)
    f_max = min(SC.BAND_HIGH_FRAC * 2.0 * fc, freqs[-1])
    if f_min >= f_max:
        return zeros

    # n_filters+2 equally-spaced breakpoints → n_filters triangular filters
    centers = np.linspace(f_min, f_max, n_filters + 2)
    fb_energies = np.zeros(n_filters)
    for m in range(n_filters):
        f_lo, f_cen, f_hi = centers[m], centers[m + 1], centers[m + 2]
        H = np.zeros(len(freqs))
        rising = (freqs >= f_lo) & (freqs <= f_cen)
        falling = (freqs > f_cen) & (freqs <= f_hi)
        if f_cen > f_lo:
            H[rising] = (freqs[rising] - f_lo) / (f_cen - f_lo)
        if f_hi > f_cen:
            H[falling] = (f_hi - freqs[falling]) / (f_hi - f_cen)
        fb_energies[m] = float(np.sum((fft_mag * H) ** 2))

    log_fb = np.log(fb_energies + SC.LOG_EPSILON)
    mfcc_all = _scipy_dct(log_fb, type=2, norm='ortho')  # length n_filters

    feats = {}
    for k in range(n_filters):
        feats[f'fb_energy_{k}'] = float(log_fb[k])
    for k in range(n_filters):
        # Skip coefficient 0 (DC = mean log-energy, not discriminative)
        feats[f'gpr_mfcc_{k + 1}'] = float(mfcc_all[k])

    return feats

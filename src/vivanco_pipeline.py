"""
Rojas-Vivanco (2025) exact replication: 7-step A-scan pipeline, rolling-BGR B-scan wrapper, and the 262-feature extractor for the pre-trained XGBoost model.

Split out of signal_processing.py (2026-07-02, debt D12); import via src.signal_processing.
"""
import numpy as np
from scipy.signal import butter, filtfilt, hilbert

from .preprocessing import (
    bandpass_filter, dewow, detect_first_break, mean_trace,
)


def predict_dzt_fouling(
    dzt_path,
    model_pkl,
    n_bscan: int = 500,
    bgr_window: int = 100,
) -> dict:
    """Apply the pre-trained Rojas-Vivanco XGBoost fouling classifier to a DZT.

    Compute-only core (moved out of unified_visualizer 2026-07-02, debt D12):
    read DZT -> vivanco_preprocess_bscan -> 262-feature rows -> model.predict,
    plus label decoding via the known label-encoder filename patterns next to
    the model pickle. Plotting stays in the visualizer.

    Returns:
        dict: predictions (raw), labels (decoded str), feat_matrix (DataFrame),
              processed, envelopes, pre_bgr (arrays), dt (seconds).
    """
    import pickle
    import warnings

    import pandas as pd

    from .dzt_io import read_dzt_traces

    bscan_raw, meta = read_dzt_traces(dzt_path, num_traces=n_bscan)
    dt = meta['sample_interval_ns'] * 1e-9
    bscan = bscan_raw.astype(float)

    result = vivanco_preprocess_bscan(bscan, dt, bgr_window=bgr_window)
    processed = result['processed']
    envelopes = result['envelopes']
    pre_bgr   = result['pre_bgr']

    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        with open(model_pkl, 'rb') as f:
            model = pickle.load(f)
    feat_names = list(model.feature_names_in_)

    rows = []
    for i in range(len(bscan)):
        fd = vivanco_extract_features(processed[i], pre_bgr[i], feat_names)
        rows.append([fd.get(fn, 0.0) for fn in feat_names])
    X = pd.DataFrame(rows, columns=feat_names)
    preds = model.predict(X)

    le_candidates = [
        model_pkl.parent / 'label_encoder-accuracy.pkl',
        model_pkl.parent / 'label_encoderaccuracy-xgboost.pkl',
        model_pkl.parent / 'label_encoder_classes_xgboost.pkl',
    ]
    class_names = None
    for le_path in le_candidates:
        if le_path.exists():
            with warnings.catch_warnings():
                warnings.simplefilter('ignore')
                with open(le_path, 'rb') as f:
                    le = pickle.load(f)
            class_names = list(le) if not hasattr(le, 'classes_') else list(le.classes_)
            break
    if class_names is not None:
        labels = [class_names[int(p)] for p in preds]
    else:
        labels = list(preds.astype(str))

    return {'predictions': preds, 'labels': labels, 'feat_matrix': X,
            'processed': processed, 'envelopes': envelopes,
            'pre_bgr': pre_bgr, 'dt': dt}


# ── Rojas-Vivanco (2025) preprocessing pipeline ──────────────────────────────

def vivanco_preprocess(
    signal: np.ndarray,
    dt: float,
    f_lo: float = 150e6,
    f_hi: float = 800e6,
    time_shift_ns: float = 3.0,
    window_ns: float = 7.0,
    butter_order: int = 4,
    background: np.ndarray = None,
) -> dict:
    """Apply the Rojas-Vivanco (2025) single-trace preprocessing pipeline.

    Implements the seven steps documented in §"Description of the used data"
    (Rojas-Vivanco et al., Transportation Geotechnics 55, 2025, p.5):

    1. **Normalize to direct wave**: divide by the direct-wave peak amplitude.
    2. **Remove DC offset (dewow)**: center signal to zero mean.
    3. **Time zero at direct wave + shift**: find direct wave peak, advance
       ``time_shift_ns`` ns (paper: 30 samples × 0.1 ns = 3 ns); new sample 0
       is placed at the start of the ballast region.
    4. **Bandpass filter** ``f_lo``–``f_hi`` Hz (default 150–800 MHz).
    5. **Cut to window** of ``window_ns`` ns (default 7 ns; None = keep all).
    6. **BGR** (background removal): subtract ``background`` if provided.
       For full B-scan BGR use :func:`vivanco_preprocess_bscan`.
    7. **Hilbert envelope, normalize to max**: compute envelope, scale to 1.

    Args:
        signal:        Raw 1-D A-scan (arbitrary amplitude units).
        dt:            Time step in seconds (read from HDF5 or CSV header).
        f_lo:          Bandpass lower edge in Hz (default 150 MHz).
        f_hi:          Bandpass upper edge in Hz (default 800 MHz).
        time_shift_ns: Physical time shift past the direct-wave peak (ns).
                       Vivanco paper: 30 samples × 0.1 ns/sample = 3.0 ns.
        window_ns:     Length of the output window in ns.  ``None`` keeps the
                       full remaining trace.
        butter_order:  Butterworth filter order (default 4).
        background:    Optional precomputed BGR mean trace (same length as
                       ``signal``); subtracted before windowing (step 6).

    Returns:
        dict with keys:
          ``processed``       – filtered, windowed, DC-free signal (step 1–6)
          ``envelope``        – normalized Hilbert envelope (step 7)
          ``direct_peak_idx`` – sample index of the direct-wave peak (in the
                                original, un-shifted trace)
          ``time_zero_idx``   – sample index where the new t=0 was placed
          ``peak_amp``        – direct-wave peak amplitude before normalization
                                (use for physical amplitude recovery)

    Reference:
        Rojas-Vivanco et al. (2025) Transportation Geotechnics 55, 101701.
    """
    sig = np.asarray(signal, dtype=float).copy()
    n = len(sig)

    # ── 1. Normalize to direct wave ──────────────────────────────────────────
    # Normalize by the RAW SIGNAL maximum (not the Hilbert envelope peak) so
    # that the Hilbert envelope of the normalized signal can exceed 1.0 at the
    # direct-wave peak (as observed in Rojas-Vivanco Site CSVs: H_0_4 = 1.07).
    search_end = max(n // 2, 1)
    direct_peak_idx = int(np.argmax(np.abs(hilbert(sig)[:search_end])))
    peak_amp = float(np.max(np.abs(sig[:search_end])))

    if peak_amp > 0:
        sig = sig / peak_amp

    # ── 2. Remove DC offset (dewow) ─────────────────────────────────────────
    sig = dewow(sig)

    # ── 3. Time zero: direct-wave peak − time_shift_ns (BACKWARD shift) ─────
    # The paper shifts the window START backward so that the direct wave falls
    # inside the 7 ns window at position n_shift (not at the window boundary).
    # "Shifted 30 samples to the right" means the time-origin is at the direct
    # wave, so the window opens time_shift_ns BEFORE that origin.
    n_shift = int(round(time_shift_ns / (dt * 1e9)))   # samples
    time_zero_idx = max(0, direct_peak_idx - n_shift)   # clamp to trace start

    sig = sig[time_zero_idx:]                            # crop to new t=0

    # ── 4. Bandpass filter f_lo – f_hi ──────────────────────────────────────
    fs = 1.0 / dt
    nyq = 0.5 * fs
    lo_norm = f_lo / nyq
    hi_norm = f_hi / nyq
    if 0 < lo_norm < hi_norm < 1.0 and len(sig) > butter_order * 3:
        b, a = butter(butter_order, [lo_norm, hi_norm], btype='band')
        sig = filtfilt(b, a, sig)

    # ── 5. Cut to window_ns ──────────────────────────────────────────────────
    if window_ns is not None:
        n_win = int(round(window_ns / (dt * 1e9)))
        sig = sig[:n_win]
        # Zero-pad if the remaining trace is shorter than the window
        if len(sig) < n_win:
            sig = np.pad(sig, (0, n_win - len(sig)))

    # ── 6. BGR subtraction (optional, single-trace) ──────────────────────────
    pre_bgr = sig.copy()  # save windowed signal BEFORE BGR for H-grid features

    if background is not None:
        bg = np.asarray(background, dtype=float)
        bg_trimmed = bg[time_zero_idx: time_zero_idx + len(sig)]
        if len(bg_trimmed) == len(sig):
            # normalize background the same way (step 1 scale)
            bg_peak = float(np.max(np.abs(bg[:search_end])))
            if bg_peak > 0:
                bg_trimmed = bg_trimmed / bg_peak
            bg_trimmed = dewow(bg_trimmed)[:len(sig)]
            sig = sig - bg_trimmed

    processed = sig.copy()

    # ── 7. Hilbert envelope, normalize to max ────────────────────────────────
    env = np.abs(hilbert(processed))
    env_max = float(np.max(env))
    if env_max > 0:
        env = env / env_max

    return {
        'processed': processed,
        'envelope': env,
        'pre_bgr': pre_bgr,
        'direct_peak_idx': direct_peak_idx,
        'time_zero_idx': time_zero_idx,
        'peak_amp': peak_amp,
    }


def vivanco_preprocess_bscan(
    bscan: np.ndarray,
    dt: float,
    bgr_window: int = 1000,
    **kwargs,
) -> dict:
    """Apply the Vivanco pipeline to every trace of a B-scan, with BGR.

    Implements the full 7-step pipeline including step 6 (BGR, background
    removal over a running window of ``bgr_window`` traces).  All keyword
    arguments beyond ``dt`` are forwarded to :func:`vivanco_preprocess`.

    BGR is computed as: for each trace i, subtract the mean of traces
    max(0, i − bgr_window//2) … min(N, i + bgr_window//2).  This is the
    rolling-window mean subtraction described in Rojas-Vivanco (2025).

    Args:
        bscan:       2-D array (n_traces, n_samples) of raw traces.
        dt:          Time step in seconds.
        bgr_window:  Number of traces over which the running mean is computed
                     (paper: 1000).
        **kwargs:    Forwarded to :func:`vivanco_preprocess` (f_lo, f_hi,
                     time_shift_ns, window_ns, butter_order).

    Returns:
        dict with keys:
          ``processed``  – (n_traces, n_window_samples) processed signals
          ``envelopes``  – (n_traces, n_window_samples) normalized envelopes
          ``bgr_mean``   – (n_samples,) mean trace used for background removal

    Reference:
        Rojas-Vivanco et al. (2025) Transportation Geotechnics 55, 101701.
    """
    bscan = np.asarray(bscan, dtype=float)
    if bscan.ndim != 2:
        raise ValueError(f"bscan must be 2-D (n_traces, n_samples), got {bscan.shape}")

    n_traces, n_samples = bscan.shape

    # BGR: rolling mean across traces (step 6)
    half = bgr_window // 2
    bgr_mean = np.mean(bscan, axis=0)  # global mean fallback

    processed_list = []
    envelope_list  = []
    pre_bgr_list   = []

    for i in range(n_traces):
        i_lo = max(0, i - half)
        i_hi = min(n_traces, i + half)
        local_bg = np.mean(bscan[i_lo:i_hi], axis=0)
        result = vivanco_preprocess(bscan[i], dt, background=local_bg, **kwargs)
        processed_list.append(result['processed'])
        envelope_list.append(result['envelope'])
        pre_bgr_list.append(result['pre_bgr'])

    return {
        'processed': np.array(processed_list),
        'envelopes': np.array(envelope_list),
        'pre_bgr':   np.array(pre_bgr_list),
        'bgr_mean':  bgr_mean,
    }


# ── Rojas-Vivanco (2025) 262-feature extractor ───────────────────────────────

_VIVANCO_DROP_CELLS = frozenset([(0, 3), (0, 6), (0, 7), (1, 7)])


def _vivanco_resample(arr: np.ndarray, n_target: int) -> np.ndarray:
    """Linear resample arr to n_target samples."""
    if len(arr) == n_target:
        return arr
    x_old = np.linspace(0, 1, len(arr))
    x_new = np.linspace(0, 1, n_target)
    return np.interp(x_new, x_old, arr)


def vivanco_extract_features(
    processed: np.ndarray,
    pre_bgr: np.ndarray,
    feat_names: list,
    n_target: int = 70,
) -> dict:
    """Extract the 262 features expected by the Rojas-Vivanco (2025) XGBoost model.

    The Vivanco model was trained on French railway GPR data with the following
    feature schema (Table 4, Rojas-Vivanco et al., Transportation Geotechnics 55,
    2025):
      - 20 scalar stats on the post-BGR processed signal
      - 20 scalar stats on the Hilbert envelope of the post-BGR signal
      - 6 special params (zero-crossings, areas, dominant frequency)
      - 28 stat-slice features: 14 slices × {mean, std} on the pre-BGR envelope
      - 66 ST grid cells: post-BGR signal sampled on a 7×10 grid (4 cells removed)
      - 56 H  grid cells: pre-BGR envelope sampled on a 6×10 grid (4 cells removed)
      - 66 AH grid cells: post-BGR envelope sampled on a 7×10 grid (4 cells removed)

    NOTE on ``rms``: in the Vivanco feature schema, ``rms`` is defined as
    ``mean(signal)^2`` (square of the arithmetic mean), NOT root mean square.
    ``crest`` is then ``peak_max / rms``.  This matches the observed values in
    the Site CSV files.

    Args:
        processed:  1-D post-BGR processed signal (output of
                    :func:`vivanco_preprocess`).  Resampled internally to
                    ``n_target`` samples.
        pre_bgr:    1-D pre-BGR windowed signal (output of
                    :func:`vivanco_preprocess` key ``'pre_bgr'``).  Same length
                    as ``processed``.
        feat_names: Ordered list of the 262 feature names expected by the model
                    (``model.feature_names_in_``).
        n_target:   Target number of samples for the 7-ns window (default 70 for
                    dt = 0.1 ns).

    Returns:
        dict mapping each feature name to its computed value.

    Reference:
        Rojas-Vivanco et al. (2025) Transportation Geotechnics 55, 101701.
    """
    # ── Resample both signals to n_target ──────────────────────────────────────
    sig   = _vivanco_resample(np.asarray(processed, dtype=float), n_target)
    pre   = _vivanco_resample(np.asarray(pre_bgr,   dtype=float), n_target)

    # ── Derived signals ────────────────────────────────────────────────────────
    ah_env  = np.abs(hilbert(sig))    # post-BGR Hilbert envelope (AH source)
    pre_env = np.abs(hilbert(pre))    # pre-BGR Hilbert envelope (H + slice source)

    feat: dict = {}

    # ── Signal stats (20 features on post-BGR signal) ─────────────────────────
    def _stats(x: np.ndarray, suffix: str = '') -> None:
        m = float(np.mean(x))
        feat[f'mean{suffix}']       = m
        feat[f'rms{suffix}']        = m * m                          # Vivanco: mean^2
        # Signal uses French name 'ecart_type'; Hilbert uses English 'std'
        std_key = 'ecart_type' if suffix == '' else f'std{suffix}'
        feat[std_key] = float(np.std(x, ddof=0))
        feat[f'median{suffix}']     = float(np.median(x))
        n = len(x)
        if n > 2:
            mu, s = np.mean(x), np.std(x, ddof=0)
            feat[f'skew{suffix}']     = float(np.mean(((x - mu) / s) ** 3)) if s > 0 else 0.0
            feat[f'kurtosis{suffix}'] = float(np.mean(((x - mu) / s) ** 4) - 3) if s > 0 else 0.0
        else:
            feat[f'skew{suffix}']     = 0.0
            feat[f'kurtosis{suffix}'] = 0.0
        pct = np.percentile(x, [25, 50, 75, 10, 20, 30, 40, 60, 70, 80, 90])
        feat[f'q1{suffix}'] = float(pct[0])
        feat[f'q2{suffix}'] = float(pct[1])
        feat[f'q3{suffix}'] = float(pct[2])
        for i, dec in enumerate([1, 2, 3, 4, 6, 7, 8, 9]):
            feat[f'd{dec}{suffix}'] = float(pct[3 + i])
        pk_max = float(np.max(x))
        feat[f'peak_max{suffix}'] = pk_max
        feat[f'peak_min{suffix}'] = float(np.min(x))
        rms_val = feat[f'rms{suffix}']
        feat[f'crest{suffix}']    = float(pk_max / rms_val) if rms_val > 0 else 0.0

    _stats(sig)
    _stats(ah_env, '_hilbert')

    # ── Special params (6 features) ───────────────────────────────────────────
    # number_zeros: sign changes in post-BGR signal
    signs = np.sign(sig)
    feat['number_zeros'] = int(np.sum(np.abs(np.diff(signs[signs != 0])) > 0))

    # area_signal: sum of |pre-BGR signal| (full integral over window)
    feat['area_signal'] = float(np.sum(np.abs(pre)))

    # points_inflexion: sign changes of the second derivative
    d2 = np.diff(sig, n=2)
    s2 = np.sign(d2)
    feat['points_inflexion'] = int(np.sum(np.abs(np.diff(s2[s2 != 0])) > 0))

    # area_fourier: sum of FFT magnitude of post-BGR signal
    fft_mag = np.abs(np.fft.rfft(sig))
    feat['area_fourier']    = float(np.sum(fft_mag))
    feat['fourier_peak_max'] = float(np.max(fft_mag))

    # area_hilbert: sum of pre-BGR Hilbert envelope
    feat['area_hilbert'] = float(np.sum(pre_env))

    # ── Stat slices (28 features: 14 slices × 2 stats on pre-BGR envelope) ───
    n_slices = 14
    sl_size  = n_target // n_slices      # 5 samples per slice at n_target=70
    for k in range(n_slices):
        sl = pre_env[k * sl_size: (k + 1) * sl_size]
        feat[f'stat_slice_{k}_mean'] = float(np.mean(sl))
        feat[f'stat_slice_{k}_std']  = float(np.std(sl, ddof=0))

    # ── Grid features ─────────────────────────────────────────────────────────
    # ST (7×10): post-BGR signal; H (6×10): pre-BGR envelope; AH (7×10): post-BGR envelope
    # Cells (0,3), (0,6), (0,7), (1,7) were removed from all grids during training.
    def _grid(prefix: str, arr: np.ndarray, n_rows: int) -> None:
        for r in range(n_rows):
            for c in range(10):
                if (r, c) in _VIVANCO_DROP_CELLS:
                    continue
                feat[f'{prefix}_{r}_{c}'] = float(arr[r * 10 + c])

    _grid('ST', sig,                n_rows=7)
    _grid('H',  pre_env[:60],       n_rows=6)   # first 60 of 70
    _grid('AH', ah_env,             n_rows=7)

    # ── Return only the features the model expects, in order ──────────────────
    return {name: feat[name] for name in feat_names if name in feat}



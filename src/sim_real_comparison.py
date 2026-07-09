"""Canonical sim<->real A-scan comparison metrics.

ONE home for sim-vs-real comparison, replacing the ~44 ad-hoc root scripts
(compare_*, align_*, iterate_*, check_*, analyze_*) that each re-parsed DZT,
re-windowed, and re-normalized differently, so their numbers were never
traceable to a single pipeline. Rules baked in here:

  - every function takes an EXPLICIT dt (seconds) — no default (cf. T1);
  - NEVER raw-waveform correlation on the coda (raw coda is speckle) — all
    shape/timing comparisons run on the Hilbert ENVELOPE or the spectrum;
  - amplitude-preserving physical preprocessing via preprocess_physical (T2):
    dewow + time-zero, NO gain, NO normalization, so amplitude/sigma observables
    (envelope decay alpha) stay physical;
  - real traces are read only via src.dzt_io (in the CLI, scripts/pipeline/
    compare_sim_real.py) — this module works on plain arrays.

Primitives are reused from src.coda_objectives (_wasserstein_1d) rather than
re-derived.
"""
import numpy as np
from scipy.signal import hilbert, stft

from .preprocessing import preprocess_physical, bandpass_filter
from .coda_objectives import _wasserstein_1d


def _prep(sig: np.ndarray, dt: float, band: tuple | None = None) -> np.ndarray:
    """Amplitude-preserving cleanup: optional antenna-band bandpass, then
    dewow + time-zero (first break shifted to sample 0). No gain/normalization."""
    if band is not None:
        sig = bandpass_filter(sig, dt, band[0], band[1])
    proc, _fb, _dt = preprocess_physical(sig, dt, target_dt=None)
    return proc


def direct_wave_correlation(sim: np.ndarray, sim_dt: float,
                            real: np.ndarray, real_dt: float,
                            window_ns: tuple = (0.0, 5.0),
                            band: tuple | None = None) -> float:
    """Pearson r of the Hilbert ENVELOPES of the direct wave (~first 5 ns).

    The direct air/surface wave is the antenna signature; a good sim<->real
    match here means the excitation/coupling is right before we ever look at the
    subsurface coda. Envelope, never raw waveform. Both traces are dewowed +
    first-break aligned to t=0, enveloped, peak-normalized, and resampled onto a
    common ``window_ns`` grid before correlating.

    Returns:
        Pearson r in [-1, 1] (higher = better); -1.0 if a window is degenerate.
    """
    a = np.abs(hilbert(_prep(sim, sim_dt, band)))
    b = np.abs(hilbert(_prep(real, real_dt, band)))
    ta = np.arange(len(a)) * sim_dt * 1e9
    tb = np.arange(len(b)) * real_dt * 1e9
    grid = np.linspace(window_ns[0], window_ns[1], 200)
    ai = np.interp(grid, ta, a, left=0.0, right=0.0)
    bi = np.interp(grid, tb, b, left=0.0, right=0.0)
    ai = ai / (ai.max() + 1e-30)
    bi = bi / (bi.max() + 1e-30)
    if ai.std() < 1e-9 or bi.std() < 1e-9:
        return -1.0
    r = float(np.corrcoef(ai, bi)[0, 1])
    return r if np.isfinite(r) else -1.0


def envelope_alpha(trace: np.ndarray, dt: float,
                   t_start_ns: float, t_end_ns: float,
                   smooth_ns: float = 1.0,
                   band: tuple | None = None) -> float:
    """Hilbert-envelope decay rate alpha (1/ns) from a log-envelope linear fit.

    Models env(t) ~ A * exp(-alpha * t) and fits log(smoothed envelope) vs t (ns
    after first break) over [t_start_ns, t_end_ns]. alpha > 0 means decaying.
    The moving-average smoothing is a constant multiplicative factor on an
    exponential, so it does not bias the slope. alpha is an amplitude observable
    — this MUST run on amplitude-preserving data (never on gained/normalized
    traces), which _prep guarantees.

    Returns:
        alpha in 1/ns (NaN if the fit window has < 2 valid samples).
    """
    env = np.abs(hilbert(_prep(trace, dt, band)))
    dt_ns = dt * 1e9
    w = max(1, int(round(smooth_ns / dt_ns)))
    if w > 1:
        env = np.convolve(env, np.ones(w) / w, mode="same")
    t = np.arange(len(env)) * dt_ns
    sel = (t >= t_start_ns) & (t <= t_end_ns) & (env > 0)
    if sel.sum() < 2:
        return float("nan")
    slope, _intercept = np.polyfit(t[sel], np.log(env[sel]), 1)
    return float(-slope)


def spectral_evolution(trace: np.ndarray, dt: float,
                       win_ns: float = 2.0, hop_ns: float = 1.0,
                       band: tuple | None = None) -> dict:
    """Per-STFT-window spectral centroid and bandwidth.

    Tracks how the trace's dominant frequency and spread evolve through the
    coda (fouling/attenuation shift the spectral centroid down over depth).

    Returns:
        dict with 1-D arrays: 'time_ns', 'centroid_hz', 'bandwidth_hz'.
    """
    proc = _prep(trace, dt, band)
    fs = 1.0 / dt
    nperseg = max(8, int(round(win_ns * 1e-9 * fs)))
    nperseg = min(nperseg, len(proc))
    step = max(1, int(round(hop_ns * 1e-9 * fs)))
    noverlap = max(0, nperseg - step)
    f, tt, Z = stft(proc, fs=fs, nperseg=nperseg, noverlap=noverlap, boundary=None)
    S = np.abs(Z)
    denom = S.sum(axis=0) + 1e-30
    centroid = (f[:, None] * S).sum(axis=0) / denom
    bandwidth = np.sqrt(((f[:, None] - centroid[None, :]) ** 2 * S).sum(axis=0) / denom)
    return {"time_ns": tt * 1e9, "centroid_hz": centroid, "bandwidth_hz": bandwidth}


def spectral_distance(sim: np.ndarray, sim_dt: float,
                      real: np.ndarray, real_dt: float,
                      coda_ns: tuple = (4.0, 18.0),
                      n_freq: int = 256, f_max_hz: float | None = None,
                      band: tuple | None = None) -> float:
    """Quadratic Wasserstein-1D distance between the normalized coda SPECTRA.

    Each coda (ns after first break) is FFT'd; the two magnitude spectra are
    interpolated onto a common frequency grid, normalized to unit mass, and
    compared by the closed-form 1-D W distance (units: Hz; lower = closer).
    sim and real have different dt (different frequency resolution), so a common
    grid is mandatory — this is why the ad-hoc scripts disagreed.

    Returns:
        W distance in Hz (>= 0; inf if a coda window is empty).
    """
    def _coda_spectrum(sig, dt):
        proc = _prep(sig, dt, band)
        t = np.arange(len(proc)) * dt * 1e9
        seg = proc[(t >= coda_ns[0]) & (t <= coda_ns[1])]
        if seg.size < 4:
            return None, None
        return np.fft.rfftfreq(seg.size, d=dt), np.abs(np.fft.rfft(seg))

    fs, ss = _coda_spectrum(sim, sim_dt)
    fr, sr = _coda_spectrum(real, real_dt)
    if fs is None or fr is None:
        return float("inf")
    if f_max_hz is None:
        f_max_hz = float(min(fs.max(), fr.max()))
    grid = np.linspace(0.0, f_max_hz, n_freq)
    ps = np.interp(grid, fs, ss, left=0.0, right=0.0)
    pr = np.interp(grid, fr, sr, left=0.0, right=0.0)
    ps = ps / (ps.sum() + 1e-30)
    pr = pr / (pr.sum() + 1e-30)
    d = _wasserstein_1d(ps, pr, grid)
    return d if np.isfinite(d) else float("inf")

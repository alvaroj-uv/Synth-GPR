"""
Envelope-matching inversion objectives: coda envelope Pearson r, late/early coda energy ratio (attenuation observable), quadratic Wasserstein coda distance, and reflection amplitude ratio.

Split out of signal_processing.py (2026-07-02, debt D12); import via src.signal_processing.
"""
import numpy as np
from scipy.signal import hilbert

from .preprocessing import bandpass_filter


# ── Envelope-matching inversion objective ─────────────────────────────────────

def _first_break_sample(sig: np.ndarray, dt_ns: float, frac: float = 0.30,
                        search_ns: float = 10.0) -> int:
    """Index of the first sample whose |amplitude| exceeds ``frac`` of the peak
    |amplitude| within ``search_ns``. Consistent picking convention shared by
    synthetic and real traces (avoids peak-vs-first-break bias)."""
    n = int(min(search_ns / dt_ns, len(sig) - 1))
    seg = np.abs(sig[:n])
    if seg.max() <= 0:
        return 0
    return int(np.argmax(seg >= frac * seg.max()))


def coda_envelope_correlation(
    syn_sig: np.ndarray, syn_dt: float,
    real_sig: np.ndarray, real_dt: float,
    coda_lo_ns: float = 2.0,
    coda_hi_ns: float = 16.0,
    n_grid: int = 280,
    band: tuple | None = None,
) -> float:
    """Pearson r between synthetic and real Hilbert envelopes in a coda window.

    The inversion objective for envelope-matching layer calibration. Both traces
    are first-break aligned (consistent convention), Hilbert-enveloped,
    peak-normalised, and resampled onto a common time grid spanning
    ``[coda_lo_ns, coda_hi_ns]`` *after the first break* — the window where the
    buried-interface reflections live (the direct wave is excluded so it cannot
    dominate the fit). Envelopes are polarity-free, so no sign search is needed.

    Args:
        syn_sig, syn_dt:   Synthetic A-scan and its sample step (seconds).
        real_sig, real_dt: Real A-scan and its sample step (seconds).
        coda_lo_ns:        Window start, ns after first break (default 2).
        coda_hi_ns:        Window end,   ns after first break (default 16).
        n_grid:            Common-grid sample count for resampling (default 280).
        band:              Optional (f_lo_hz, f_hi_hz) bandpass applied to BOTH
                           traces first — use the antenna band (e.g. 150e6,800e6)
                           so out-of-band content (sim numerical HF, low drift)
                           cannot bias the comparison. Default None = no filter.

    Returns:
        Pearson correlation in [-1, 1]; higher = better envelope-shape match.
        Returns -1.0 if either windowed envelope is degenerate.
    """
    if band is not None:
        syn_sig  = bandpass_filter(syn_sig,  syn_dt,  band[0], band[1])
        real_sig = bandpass_filter(real_sig, real_dt, band[0], band[1])
    syn_dt_ns  = syn_dt  * 1e9
    real_dt_ns = real_dt * 1e9

    syn_fb_t  = _first_break_sample(syn_sig,  syn_dt_ns)  * syn_dt_ns
    real_fb_t = _first_break_sample(real_sig, real_dt_ns) * real_dt_ns

    syn_t  = np.arange(len(syn_sig))  * syn_dt_ns  - syn_fb_t
    real_t = np.arange(len(real_sig)) * real_dt_ns - real_fb_t

    syn_env  = np.abs(hilbert(syn_sig))
    real_env = np.abs(hilbert(real_sig))

    grid = np.linspace(coda_lo_ns, coda_hi_ns, n_grid)
    syn_i  = np.interp(grid, syn_t,  syn_env,  left=0.0, right=0.0)
    real_i = np.interp(grid, real_t, real_env, left=0.0, right=0.0)

    syn_i  = syn_i  / (syn_i.max()  + 1e-30)
    real_i = real_i / (real_i.max() + 1e-30)

    if syn_i.std() < 1e-9 or real_i.std() < 1e-9:
        return -1.0
    r = float(np.corrcoef(syn_i, real_i)[0, 1])
    return r if np.isfinite(r) else -1.0


def coda_energy_ratio(
    sig: np.ndarray, dt: float,
    coda_lo_ns: float = 4.0,
    coda_mid_ns: float = 11.0,
    coda_hi_ns: float = 18.0,
) -> float:
    """Late/early Hilbert-envelope energy ratio within one trace's coda.

    Attenuation observable, complementary to coda_envelope_correlation: the
    Pearson-r objective is scale-invariant and discards the amplitude decay
    that conductivity (hence pore water) imposes, so (f, S_w) mixes with equal
    eps_eff are indistinguishable by shape alone (see experiments/2026-07-01/
    crim_inversion_poc). This ratio is computed WITHIN a single trace, so the
    unknown absolute gain (DZT A/D scale, source strength, missing GSSI V_ref)
    cancels — it is safe on raw real traces. It is NOT immune to geometric
    spreading, which differs 2D vs 3D: when comparing a 2D synthetic against
    3D reality, calibrate the systematic offset once with a 3D run.

    Windows are ns AFTER the first break (same picking convention as
    coda_envelope_correlation): early = [coda_lo_ns, coda_mid_ns],
    late = (coda_mid_ns, coda_hi_ns].

    Returns:
        sum(env² late) / sum(env² early); 0.0 if the early window is empty.
    """
    dt_ns = dt * 1e9
    fb_t = _first_break_sample(sig, dt_ns) * dt_ns
    t = np.arange(len(sig)) * dt_ns - fb_t
    env2 = np.abs(hilbert(sig)) ** 2
    early = env2[(t >= coda_lo_ns) & (t <= coda_mid_ns)].sum()
    late  = env2[(t > coda_mid_ns) & (t <= coda_hi_ns)].sum()
    return float(late / early) if early > 0 else 0.0


def _wasserstein_1d(p: np.ndarray, q: np.ndarray, t: np.ndarray) -> float:
    """Quadratic 1-D Wasserstein distance W₂ between two distributions p, q on
    grid ``t`` (each non-negative, summing to 1). Closed form via inverse CDFs —
    no Sinkhorn needed in 1-D. Returns a distance in the units of ``t`` (ns).
    A pure time-shift τ between identical pulses yields W₂ = |τ| exactly."""
    Fp = np.cumsum(p); Fq = np.cumsum(q)
    n  = len(t)
    qs = (np.arange(n) + 0.5) / n                 # midpoint quantile grid
    Fp_inv = np.interp(qs, Fp, t)                 # quantile (inverse-CDF) functions
    Fq_inv = np.interp(qs, Fq, t)
    return float(np.sqrt(np.mean((Fp_inv - Fq_inv) ** 2)))


def coda_wasserstein_distance(
    syn_sig: np.ndarray, syn_dt: float,
    real_sig: np.ndarray, real_dt: float,
    coda_lo_ns: float = 4.0,
    coda_hi_ns: float = 18.0,
    n_grid: int = 300,
    softplus_b: float = 1.0,
    use_envelope: bool = False,
    band: tuple | None = None,
) -> float:
    """Optimal-transport misfit between synthetic and real coda (Lu et al. 2024).

    Drop-in alternative to :func:`coda_envelope_correlation`. Unlike envelope
    correlation (which discards phase), the quadratic Wasserstein distance keeps
    timing AND amplitude while staying convex in time-shift and noise-robust —
    the properties that help break the d–ε degeneracy. Both traces are
    first-break aligned, windowed to the coda, peak-normalised, mapped to a
    non-negative distribution (Softplus on the signed waveform, or the envelope
    directly), normalised to unit mass, then compared by the 1-D W₂ distance.

    Args:
        syn_sig, syn_dt:   Synthetic A-scan and sample step (s).
        real_sig, real_dt: Real A-scan and sample step (s).
        coda_lo_ns/hi_ns:  Coda window, ns after first break (start ≥4 ns to
                           exclude the direct-wave tail).
        n_grid:            Common-grid sample count.
        softplus_b:        Softplus sharpness b in log(e^{b·x}+1); larger b →
                           more convex but smoother near the minimum (Lu 2024).
        use_envelope:      If True, transport the (non-negative) Hilbert envelope
                           instead of the Softplus-mapped waveform. Default False
                           keeps phase/timing, the whole point of using W₂.

        band:              Optional (f_lo_hz, f_hi_hz) bandpass applied to BOTH
                           traces first (antenna band, e.g. 150e6,800e6) — keeps
                           out-of-band ringing from gaming the transport metric.

    Returns:
        W₂ distance in ns (LOWER = better match; 0 = identical). NaN-safe → inf.
    """
    if band is not None:
        syn_sig  = bandpass_filter(syn_sig,  syn_dt,  band[0], band[1])
        real_sig = bandpass_filter(real_sig, real_dt, band[0], band[1])
    syn_dt_ns  = syn_dt  * 1e9
    real_dt_ns = real_dt * 1e9

    syn_fb_t  = _first_break_sample(syn_sig,  syn_dt_ns)  * syn_dt_ns
    real_fb_t = _first_break_sample(real_sig, real_dt_ns) * real_dt_ns

    syn_t  = np.arange(len(syn_sig))  * syn_dt_ns  - syn_fb_t
    real_t = np.arange(len(real_sig)) * real_dt_ns - real_fb_t

    grid = np.linspace(coda_lo_ns, coda_hi_ns, n_grid)

    if use_envelope:
        syn_v  = np.interp(grid, syn_t,  np.abs(hilbert(syn_sig)),  left=0.0, right=0.0)
        real_v = np.interp(grid, real_t, np.abs(hilbert(real_sig)), left=0.0, right=0.0)
        syn_p  = syn_v  / (syn_v.max()  + 1e-30)
        real_p = real_v / (real_v.max() + 1e-30)
    else:
        syn_w  = np.interp(grid, syn_t,  syn_sig,  left=0.0, right=0.0)
        real_w = np.interp(grid, real_t, real_sig, left=0.0, right=0.0)
        # peak-normalise to [-1,1] so softplus_b is unit-agnostic (V/m vs ADC)
        syn_w  = syn_w  / (np.max(np.abs(syn_w))  + 1e-30)
        real_w = real_w / (np.max(np.abs(real_w)) + 1e-30)
        syn_p  = np.log1p(np.exp(softplus_b * syn_w))   # Softplus → non-negative
        real_p = np.log1p(np.exp(softplus_b * real_w))

    syn_p  = syn_p  / (syn_p.sum()  + 1e-30)            # unit mass (distribution)
    real_p = real_p / (real_p.sum() + 1e-30)

    w2 = _wasserstein_1d(syn_p, real_p, grid)
    return w2 if np.isfinite(w2) else np.inf


def coda_reflection_amplitude_ratio(
    sig: np.ndarray, dt: float,
    base_lo_ns: float = 4.0, base_hi_ns: float = 9.0,
    direct_lo_ns: float = -1.5, direct_hi_ns: float = 2.5,
    band: tuple | None = None,
) -> float:
    """Ratio of the ballast-base reflection envelope peak to the direct-wave
    envelope peak — the degeneracy-breaking amplitude measure (ray-amplitude
    principle, Xue 2021 / Forte 2014).

    Why this breaks the d–ε degeneracy that timing/shape cannot: two layer models
    with the same ballast-base *travel time* (the d·√ε ridge) produce the same
    arrival but DIFFERENT reflection *strengths* — the air/ballast and
    ballast/subgrade reflection coefficients depend on ε_b. Peak-normalised
    envelope/W₂ objectives discard this; the ratio keeps it.

    It is CALIBRATION-INDEPENDENT: synthetic (V/m) and real (ADC counts) are
    scaled by the same unknown factor, which cancels in the ratio. Both traces
    are band-limited (use the antenna band) and first-break aligned; the direct
    window straddles t=0, the base window brackets the ballast-base reflection.

    Returns:
        base_peak / direct_peak (dimensionless). Compare synthetic vs real.
    """
    if band is not None:
        sig = bandpass_filter(sig, dt, band[0], band[1])
    dt_ns = dt * 1e9
    fb = _first_break_sample(sig, dt_ns) * dt_ns
    t  = np.arange(len(sig)) * dt_ns - fb
    env = np.abs(hilbert(sig))
    d_sel = (t >= direct_lo_ns) & (t <= direct_hi_ns)
    b_sel = (t >= base_lo_ns)   & (t <= base_hi_ns)
    if not d_sel.any() or not b_sel.any():
        return np.nan
    d_amp = env[d_sel].max()
    b_amp = env[b_sel].max()
    return float(b_amp / (d_amp + 1e-30))



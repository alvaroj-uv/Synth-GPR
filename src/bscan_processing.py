"""
B-scan (2-D) processing: FastICA + WTMM multifractal denoising (Li 2022), vectorised AGC, F-K filtering and Kirchhoff migration.

Split out of signal_processing.py (2026-07-02, debt D12); import via src.signal_processing.
"""
import numpy as np
from scipy.signal import hilbert


# ── FastICA B-scan decomposition + Multifractal WTMM (Li et al. 2022) ──────────
# Li, R. et al. (2022). "FastICA and Multifractal Denoising for GPR Signal."
# Method: Decompose B-scan into N independent components via FastICA; identify
# and remove the noise component via its WTMM multifractal spectrum width Δh.
# Noise ~ monofractal (small Δh); signal components ~ multifractal (large Δh).


def _morlet_cwt(signal: np.ndarray, scales: np.ndarray,
                omega0: float = 6.0) -> np.ndarray:
    """Analytic Morlet CWT via FFT convolution.

    Args:
        signal: 1-D real array.
        scales: 1-D array of scales (in samples).
        omega0: Central frequency parameter (default 6.0 satisfies admissibility).

    Returns:
        Complex array of shape (len(scales), len(signal)).
    """
    n = len(signal)
    sig_fft = np.fft.fft(signal, n=n)
    # Angular frequencies in rad/sample
    omega = 2.0 * np.pi * np.fft.fftfreq(n)

    coeffs = np.zeros((len(scales), n), dtype=complex)
    norm = np.pi ** (-0.25)
    for i, a in enumerate(scales):
        # Morlet in frequency domain: ψ̂(aω) = π^(-1/4) * exp(-(aω - ω₀)² / 2)
        psi_hat = norm * np.exp(-0.5 * (a * omega - omega0) ** 2)
        psi_hat[omega < 0] = 0.0  # analytic (one-sided)
        # W(a,b) = IFFT{ sqrt(a) * F̂(ω) * ψ̂*(aω) }
        coeffs[i] = np.fft.ifft(np.sqrt(a) * sig_fft * psi_hat.conj())
    return coeffs


def multifractal_spectrum(
    signal: np.ndarray,
    n_scales: int = 20,
    q_min: float = -5.0,
    q_max: float = 5.0,
    n_q: int = 21,
    omega0: float = 6.0,
) -> dict:
    """Estimate the WTMM multifractal spectrum of a 1-D signal.

    Computes the partition function T(q,a) = <|W(a,b)|^q>_b from the Morlet CWT,
    fits the scaling exponent s(q) via log-log regression over scales, and derives
    the multifractal spectrum D(h) via Legendre transform.

    Key output features (Li 2022 discriminators):
      delta_h  = h_max - h_min  — width of the singularity spectrum (Hölder range)
      delta_D  = D_max - D_min  — height variation of D(h)
    Noise is monofractal (small delta_h); subsurface GPR signal is multifractal
    (large delta_h).  Li 2022 reports this criterion correctly separates direct
    wave / coherent noise from anomaly components in synthetic GPR benchmarks.

    References:
        Mallat, S. & Hwang, W.L. (1992). Singularity detection and processing
            with wavelets. IEEE Trans. Inf. Theory 38(2):617-643. [WTMM theory]
        Li et al. (2022). FastICA and Multifractal Denoising for GPR Signal.
            [delta_h as noise discriminator; N=3 ICA components]

    Args:
        signal:   1-D numpy array.
        n_scales: Number of log-spaced CWT scales (default 20).
        q_min, q_max: Range of moment orders q (default -5 to 5).
        n_q:      Number of q values (default 21).
        omega0:   Morlet central frequency parameter.

    Returns:
        dict with keys: q, s_q, h, D_h, delta_h, delta_D, h_min, h_max
    """
    n = len(signal)
    if n < 16:
        return dict(q=np.array([]), s_q=np.array([]), h=np.array([]),
                    D_h=np.array([]), delta_h=0.0, delta_D=0.0,
                    h_min=np.nan, h_max=np.nan)

    scales = np.logspace(np.log10(4), np.log10(max(n // 4, 8)), n_scales)
    q_vals = np.linspace(q_min, q_max, n_q)

    # CWT
    coeffs = _morlet_cwt(signal, scales, omega0=omega0)  # (n_scales, n)

    # Partition function T(q, a) = mean_b |W(a,b)|^q
    T_qa = np.full((n_q, n_scales), np.nan)
    for j in range(n_scales):
        W = np.abs(coeffs[j])
        W_pos = W[W > 0]
        if len(W_pos) == 0:
            continue
        for i, q in enumerate(q_vals):
            if q == 0:
                T_qa[i, j] = 1.0
            elif q > 0:
                T_qa[i, j] = float(np.mean(W_pos ** q))
            else:
                T_qa[i, j] = float(np.mean(W_pos ** q))

    # Scaling exponent s(q): T(q,a) ~ a^s(q)
    log_a = np.log2(scales)
    s_q = np.full(n_q, np.nan)
    for i in range(n_q):
        log_T = np.log2(np.maximum(T_qa[i], 1e-300))
        valid = np.isfinite(log_T)
        if valid.sum() > 2:
            s_q[i] = float(np.polyfit(log_a[valid], log_T[valid], 1)[0])

    # Legendre transform: h = ds/dq, D(h) = qh - s(q)
    valid_sq = np.isfinite(s_q)
    if valid_sq.sum() < 3:
        return dict(q=q_vals, s_q=s_q, h=np.full_like(q_vals, np.nan),
                    D_h=np.full_like(q_vals, np.nan),
                    delta_h=0.0, delta_D=0.0, h_min=np.nan, h_max=np.nan)

    h = np.gradient(s_q, q_vals)
    D_h = q_vals * h - s_q

    # Restrict to the physically meaningful region D(h) >= 0
    valid_D = np.isfinite(D_h) & (D_h >= -0.1)
    if valid_D.sum() > 0:
        h_v, D_v = h[valid_D], D_h[valid_D]
        delta_h = float(h_v.max() - h_v.min())
        delta_D = float(D_v.max() - D_v.min())
        h_min, h_max = float(h_v.min()), float(h_v.max())
    else:
        h_fin = h[np.isfinite(h)]
        delta_h = float(h_fin.max() - h_fin.min()) if len(h_fin) else 0.0
        delta_D = 0.0
        h_min = float(h_fin.min()) if len(h_fin) else np.nan
        h_max = float(h_fin.max()) if len(h_fin) else np.nan

    return dict(q=q_vals, s_q=s_q, h=h, D_h=D_h,
                delta_h=delta_h, delta_D=delta_D,
                h_min=h_min, h_max=h_max)


def ica_decompose_bscan(
    bscan: np.ndarray,
    n_components: int = 3,
    random_state: int = 42,
    max_iter: int = 500,
) -> dict:
    """Decompose a GPR B-scan into independent components via FastICA.

    Implements Li et al. (2022) §III-A: observed B-scan X = A·S, where A is the
    mixing matrix and S contains N independent source signals. For GPR trackbed:
    - Component with smallest delta_h → coherent noise / direct wave
    - Other components → background formation, subsurface anomaly

    Requires sklearn.decomposition.FastICA (part of scikit-learn).

    Args:
        bscan:        2D array (n_traces, n_samples) — B-scan data matrix.
        n_components: Number of independent components (Li 2022 uses 3).
        random_state: ICA random seed for reproducibility.
        max_iter:     Max ICA iterations (500 is safe for GPR data).

    Returns:
        dict with:
          components:    (n_components, n_samples) independent source signals
          mixing_matrix: (n_traces, n_components) mixing matrix A
          ica:           fitted FastICA object (call ica.inverse_transform for
                         reconstruction after zeroing components)

    Raises:
        ImportError: if scikit-learn is not installed.
        ValueError:  if bscan has fewer traces than n_components.
    """
    from sklearn.decomposition import FastICA

    A = np.atleast_2d(bscan).astype(float)
    n_traces, n_samples = A.shape
    if n_traces < 2:
        raise ValueError("ica_decompose_bscan requires >= 2 traces (B-scan). "
                         "For a single A-scan use svd_denoise() instead.")
    n_comp = min(n_components, n_traces)

    ica = FastICA(n_components=n_comp, random_state=random_state,
                  max_iter=max_iter, tol=1e-4, whiten="unit-variance")

    # FastICA: X.T is (n_samples, n_traces); each time-sample is an "observation"
    sources = ica.fit_transform(A.T)  # (n_samples, n_comp)

    return dict(
        components=sources.T,          # (n_comp, n_samples)
        mixing_matrix=ica.mixing_,     # (n_traces, n_comp)
        ica=ica,
    )


def ica_multifractal_denoise(
    bscan: np.ndarray,
    n_components: int = 3,
    noise_criterion: str = "min_delta_h",
    random_state: int = 42,
    multifractal_kw: dict = None,
) -> dict:
    """Denoise a GPR B-scan via FastICA + multifractal spectrum (Li et al. 2022, §III-B).

    Algorithm:
      1. FastICA separates B-scan into n_components independent signals.
      2. WTMM multifractal spectrum is computed for each component.
      3. The noise component is identified by the smallest delta_h
         (noise is monofractal; GPR signal is multifractal).
      4. That component is zeroed and the B-scan is reconstructed.

    Args:
        bscan:           2D array (n_traces, n_samples).
        n_components:    Number of ICA components (Li 2022 uses 3).
        noise_criterion: 'min_delta_h' (Li 2022, recommended) or
                         'min_energy' (faster fallback).
        random_state:    ICA seed.
        multifractal_kw: Extra kwargs forwarded to multifractal_spectrum().

    Returns:
        dict with:
          denoised:  (n_traces, n_samples) — B-scan with noise removed
          noise:     (n_traces, n_samples) — the isolated noise contribution
          noise_idx: int — which component was identified as noise
          delta_h:   array — delta_h per component (NaN if 'min_energy')
    """
    kw = multifractal_kw or {}
    result = ica_decompose_bscan(bscan, n_components=n_components,
                                  random_state=random_state)
    ica = result["ica"]
    components = result["components"]  # (n_comp, n_samples)
    n_comp = components.shape[0]

    if noise_criterion == "min_delta_h":
        delta_h = np.full(n_comp, np.nan)
        for k in range(n_comp):
            try:
                ms = multifractal_spectrum(components[k], **kw)
                delta_h[k] = ms["delta_h"]
            except Exception:
                delta_h[k] = np.inf
        noise_idx = int(np.nanargmin(delta_h))
    else:  # 'min_energy'
        energies = np.array([np.sqrt(np.mean(c ** 2)) for c in components])
        noise_idx = int(np.argmin(energies))
        delta_h = np.full(n_comp, np.nan)

    # Transform to source space, zero noise, invert
    A_f = np.atleast_2d(bscan).astype(float)
    sources = ica.transform(A_f.T)          # (n_samples, n_comp)

    sources_clean = sources.copy()
    sources_clean[:, noise_idx] = 0.0

    sources_noise_only = np.zeros_like(sources)
    sources_noise_only[:, noise_idx] = sources[:, noise_idx]

    denoised = ica.inverse_transform(sources_clean).T          # (n_traces, n_samples)
    noise    = ica.inverse_transform(sources_noise_only).T

    return dict(
        denoised=denoised,
        noise=noise,
        noise_idx=noise_idx,
        delta_h=delta_h,
    )


def agc_bscan(
    bscan: np.ndarray,
    dt: float,
    window_ns: float = 5.0,
    noise_gate: float = 1e-3,
) -> np.ndarray:
    """Apply Automatic Gain Control to every trace in a B-scan simultaneously.

    Each sample is divided by the RMS of its local time window, equalising
    amplitude across depth so that deep interfaces (ballast base, subgrade)
    are as bright as the near-surface direct wave.

    Vectorised 2-D implementation — roughly 100× faster than calling
    :func:`apply_gain` row-by-row because it uses ``uniform_filter1d`` on the
    whole array at once.

    Algorithm::

        rms[i] = sqrt( mean( x[i-w : i+w]^2 ) )   w = window_ns / dt / 2
        x_agc[i] = x[i] / max(rms[i], noise_gate)

    Args:
        bscan:      2-D array (n_traces, n_samples), any amplitude units.
        dt:         Time step in seconds.
        window_ns:  Half-length of the AGC sliding window in ns.  Roughly
                    one wavelength at 400 MHz ≈ 2.5 ns; default 5 ns gives
                    ~2 wavelengths, a good balance between resolution and
                    stability.
        noise_gate: Minimum RMS; prevents noise from being amplified when
                    the signal is absent (default 1e-3, relative to input
                    amplitude scale).

    Returns:
        AGC-corrected B-scan, same dtype and shape as input.

    References:
        Yilmaz, O. (2001). Seismic Data Analysis, vol. 1, SEG. §2.1.
        Daniels, D. (2005). Ground Penetrating Radar, 2nd ed. IET.
    """
    from scipy.ndimage import uniform_filter1d

    half_win = max(1, int(round(window_ns / (dt * 1e9))))
    win_size = 2 * half_win + 1

    bscan = np.asarray(bscan, dtype=np.float64)
    rms_sq = uniform_filter1d(bscan ** 2, size=win_size, axis=1)
    rms = np.sqrt(np.maximum(rms_sq, noise_gate ** 2))
    return (bscan / rms).astype(bscan.dtype)


def fk_filter(
    bscan: np.ndarray,
    dt: float,
    dx: float,
    zero_k_fraction: float = 0.02,
    v_min: float = None,
    v_max: float = None,
) -> np.ndarray:
    """Apply a frequency-wavenumber (F-K) filter to a GPR B-scan.

    Works in the 2-D Fourier domain where the axes are:

    * **f** (Hz)  — temporal frequency, along the *time* axis of the B-scan
    * **k** (1/m) — spatial frequency (wavenumber), along the *trace* axis

    The apparent velocity of any coherent event is ``v_app = f / k`` (m/s).

    Two independent masks can be combined:

    1. **Zero-k band** (``zero_k_fraction > 0``): zeroes the |k| < fraction×k_max
       strip, removing purely horizontal events — a stronger alternative to BGR
       that works in the Fourier domain (Claerbout 1992 §7).

    2. **Velocity pass-band** (``v_min`` / ``v_max``): keeps only events whose
       apparent velocity falls inside [v_min, v_max].  Useful for passing
       sub-surface reflections (v ≈ 1–2×10⁸ m/s) while rejecting air-coupled
       noise (v → ∞) or very slow coherent noise.

    Args:
        bscan:            2-D array (n_traces, n_samples).
        dt:               Time step in seconds.
        dx:               Trace spacing in metres.
        zero_k_fraction:  Fraction of the maximum wavenumber to zero out around
                          k=0 (default 0.02 = 2 %; set to 0 to disable).
        v_min:            Minimum apparent velocity to pass (m/s); set to e.g.
                          ``0.5e8`` to reject very slow coherent noise.
        v_max:            Maximum apparent velocity to pass (m/s); set to e.g.
                          ``2e8`` to reject air-wave / direct-wave energy
                          (travels at ~3×10⁸ m/s in air).

    Returns:
        Filtered B-scan (real part of IFFT), same shape as input.

    Notes:
        The filter is applied to the *full* B-scan at once; very large arrays
        (> 10⁵ traces) should be chunked to avoid memory spikes from the 2-D FFT.

    References:
        Claerbout, J.F. (1992). Earth Soundings Analysis. Blackwell. §7.
        Yilmaz, O. (2001). Seismic Data Analysis, vol. 1, SEG. §6.1.
        Daniels, D. (2005). Ground Penetrating Radar, 2nd ed. IET.
    """
    n_tr, n_samp = bscan.shape

    FK = np.fft.fft2(bscan.astype(float))

    k_ax = np.fft.fftfreq(n_tr,   d=dx)   # cycles/m
    f_ax = np.fft.fftfreq(n_samp, d=dt)   # Hz

    KK = k_ax[:, np.newaxis]   # (n_tr, 1)  → broadcasts to (n_tr, n_samp)
    FF = f_ax[np.newaxis, :]   # (1, n_samp)

    mask = np.ones((n_tr, n_samp), dtype=bool)

    # ── 1. Zero-k band (horizontal event removal) ─────────────────────────────
    if zero_k_fraction > 0:
        k_cutoff = zero_k_fraction * np.max(np.abs(k_ax))
        mask &= np.abs(KK) >= k_cutoff

    # ── 2. Apparent-velocity pass-band ────────────────────────────────────────
    if v_min is not None or v_max is not None:
        with np.errstate(divide='ignore', invalid='ignore'):
            v_app = np.where(KK != 0, np.abs(FF / KK), np.inf)
        if v_min is not None:
            mask &= v_app >= v_min
        if v_max is not None:
            mask &= (v_app <= v_max) | np.isinf(v_app)

    FK[~mask] = 0.0
    return np.fft.ifft2(FK).real.astype(bscan.dtype)


def kirchhoff_migration(
    bscan: np.ndarray,
    dt: float,
    dx: float,
    v: float = 1.6e8,
    max_aperture_m: float = 1.0,
) -> np.ndarray:
    """Aperture-limited diffraction-stack (Kirchhoff) zero-offset migration.

    For each output point (x₀, t₀) the algorithm sums input samples along the
    diffraction hyperbola defined by the medium velocity *v*:

    .. math::

        t_{\\text{diff}}(x) =
            \\sqrt{t_0^2 + \\left(\\frac{2(x - x_0)}{v}\\right)^2}

    Collapsing these hyperbolic tails refocuses point-scatterer energy (e.g.
    from ballast rocks, sleepers) back to its true sub-surface position and
    sharpens layer boundaries.

    Args:
        bscan:          2-D array (n_traces, n_samples).
        dt:             Time step in seconds (read from HDF5 attrs).
        dx:             Trace spacing in metres.
        v:              One-way EM velocity in m/s (default 1.6×10⁸ ≈ clean
                        ballast with ε=3.5).  Convert from ε: v = c/√ε.
        max_aperture_m: Maximum lateral distance from each output point to
                        include in the summation (metres).  Limits cost and
                        avoids including energy from distant scatterers.
                        Default 1.0 m.

    Returns:
        Migrated B-scan, same shape as input.

    Notes:
        Computational complexity is O(n_tr × n_samp × aperture/dx).  For the
        full 421 k-trace EFE dataset at dx≈0.1 m and aperture=1 m, this means
        ~4.2 × 10⁹ operations — use on short segments or downsampled B-scans.
        For production use on long surveys, chunked or GPU-accelerated
        implementations are recommended.

    References:
        Sheriff, R.E. & Geldart, L.P. (1995). Exploration Seismology, 2nd ed.
            Cambridge University Press. §4.7.
        Claerbout, J.F. (1992). Earth Soundings Analysis. Blackwell. §4.
        Daniels, D. (2005). Ground Penetrating Radar, 2nd ed. IET. §migration.
    """
    n_tr, n_samp = bscan.shape
    migrated = np.zeros_like(bscan, dtype=np.float64)

    half_ap = max(1, int(round(max_aperture_m / dx)))
    t_axis = np.arange(n_samp) * dt   # seconds

    for ix0 in range(n_tr):
        ix_lo = max(0,    ix0 - half_ap)
        ix_hi = min(n_tr, ix0 + half_ap + 1)
        offsets = (np.arange(ix_lo, ix_hi) - ix0) * dx   # metres

        for it0 in range(n_samp):
            t0 = t_axis[it0]
            # Two-way diffraction time from each aperture trace
            t_diff = np.sqrt(t0 ** 2 + (2.0 * offsets / v) ** 2)
            it_diff = np.round(t_diff / dt).astype(int)
            valid = (it_diff >= 0) & (it_diff < n_samp)
            ix_src = np.arange(ix_lo, ix_hi)[valid]
            it_src = it_diff[valid]
            if ix_src.size:
                migrated[ix0, it0] = bscan[ix_src, it_src].mean()

    return migrated.astype(bscan.dtype)

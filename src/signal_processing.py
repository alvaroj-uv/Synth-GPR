"""
signal_processing.py — GPR signal processing utilities for railway ballast.

Every function is tied to a published reference so that the thesis methods
chapter can cite each processing step directly.

─── 1. DIRECT WAVE REMOVAL ──────────────────────────────────────────────────
  Wang & Liu (2017), Signal Processing 132:227-242
  Rojas-Vivanco et al. (2025), Transportation Geotechnics 55:101701 §"Data"

  time_gate()               Wang §2.2 — zero early samples, single trace
  background_subtraction()  Wang Eq.19-24 — subtract common-mode reference
  mean_trace()              Estimate the common-mode direct wave from a B-scan
  remove_direct_wave()      Dispatcher: 'time_gate' | 'background_subtraction' | 'svd'

─── 2. B-SCAN COHERENT NOISE REMOVAL (SVD) ──────────────────────────────────
  Liu, Song & Lu (2017), J. Appl. Geophys. 144:125-133

  svd_select_p()            Liu Eq. 6 — quantitative rank selection
  svd_denoise()             Liu §3.1 — keep top-p singular values
  svd_remove_direct_wave()  Liu §3.2 — zero first singular value

─── 3. PREPROCESSING CHAIN ──────────────────────────────────────────────────
  Rojas-Vivanco et al. (2025): dewow → band-pass → time-zero → normalization
  Coppens (1985), Geophys. Prospect. 33:1212  [first-break energy ratio]
  Earle & Shearer (1994), BSSA 84(1):95       [STA/LTA seismology]

  dewow()                      Running-mean low-frequency removal
  detect_first_break_coppens() Coppens energy-ratio picker
  detect_first_break_sta_lta() STA/LTA ratio picker
  detect_first_break()         Dispatcher for the two pickers
  time_zero_correction()       Shift trace so first break is at index 0
  apply_gain()                 TVG / AGC amplitude compensation
  preprocess_signal()          Full chain: remove_direct_wave → dewow →
                               time_zero → band-pass → gain → normalise
  vivanco_preprocess()         Rojas-Vivanco (2025) exact 7-step pipeline
                               (single A-scan): normalize (raw-signal max) →
                               dewow → BACKWARD shift 30 samples (direct wave
                               at window[30]) → bandpass 150–800 MHz →
                               window 7 ns → BGR → Hilbert envelope.
                               Returns 'pre_bgr' (windowed pre-BGR signal) in
                               addition to the post-BGR 'processed' signal.
  vivanco_preprocess_bscan()   B-scan wrapper: rolling BGR over N traces
                               then vivanco_preprocess() on each trace.
                               Returns 'pre_bgr' array alongside 'processed'.
  vivanco_extract_features()   Extract the 262-feature schema expected by the
                               Rojas-Vivanco XGBoost model from (processed,
                               pre_bgr) pair; handles resampling to 70 samples.

─── 4. MULTIPLE SUPPRESSION ─────────────────────────────────────────────────
  Xiong et al. (2024), SoftwareX 26:101720 (GPRlab)
  Claerbout (1992), Earth Soundings Analysis

  predictive_deconvolution()   Wiener prediction-error filter, Tikhonov reg.

─── 5. SPECTRAL ANALYSIS ────────────────────────────────────────────────────
  Unpingco (2014), Python for Signal Processing [windowing]
  Rojas-Vivanco et al. (2025) §"GPR parameterisation" [STFT grid features]
  Silvast et al. (2006), 7th WCRR [area under Fourier curve for fouling]

  apply_window()               Taper + coherent-gain correction
  compute_spectrum()           Magnitude FFT
  compute_padded_spectrum()    Zero-padded rFFT with peak frequency
  compute_spectrogram()        Short-Time Fourier Transform (STFT)
  peak_relative_coda_gate()    Boolean coda mask aligned to direct-wave peak

─── 6. INSTANTANEOUS ATTRIBUTES (ANALYTIC SIGNAL) ───────────────────────────
  Braun, Ewins & Rao (2001), ICASSP 5:3013
  Feldman (2011), Mech. Syst. Signal Process. 25(3):735-802
  Rojas-Vivanco et al. (2025) §"Analytical signal" — Hilbert envelope for FI

  calculate_instantaneous_attributes()  Envelope, phase, inst. frequency,
                                         cosine phase via Hilbert transform

─── 7. MODAL DECOMPOSITION — MATRIX PENCIL METHOD ───────────────────────────
  Mbubia et al. (2024), J. Phys. Conf. Ser. 2887:012047
  Sarkar & Pereira (1995), IEEE Ant. Propag. Mag. 37(1):48-55 [MPM theory]

  mpm_decompose()              Hankel SVD → eigenvalue → damped-exponential poles

─── 8. PHYSICS-BASED REFLECTOR DEPTH & MODEL GENERATION ────────────────────
  Sussmann et al. (2000), TRB 2000 Annual Meeting — d = c·t_oneway/sqrt(eps)

  pick_reflector()             Hilbert-envelope peak detection, skip window
  reflector_to_depth()         Sussmann Eq. 1 travel-time to depth conversion
  picks_to_layer_toml()        Convert B-scan horizon picks → gprMax-ready TOML
                                 (layers mode); closes the real→synthetic loop

─── 9. B-SCAN 2-D PREPROCESSING ────────────────────────────────────────────
  Yilmaz (2001), Seismic Data Analysis §2.1          [AGC, F-K filtering]
  Claerbout (1992), Earth Soundings Analysis           [F-K, migration theory]
  Sheriff & Geldart (1995), Exploration Seismology    [Kirchhoff migration]
  Daniels (2005), Ground Penetrating Radar 2nd ed.    [GPR-specific guidance]

  bandpass_filter()             Standalone Butterworth bandpass (single trace)
  agc_bscan()                   Vectorised AGC over full (n_tr, n_samp) B-scan;
                                  uses uniform_filter1d for speed — equivalent to
                                  apply_gain(type='agc') but 2-D and ~100× faster
  fk_filter()                   F-K domain 2-D filter: optional zero-k band to
                                  kill horizontal events (direct wave, ringing),
                                  optional apparent-velocity pass-band to select
                                  dipping reflectors
  kirchhoff_migration()         Aperture-limited diffraction-stack (Kirchhoff)
                                  zero-offset migration; collapses hyperbolic
                                  tails from point scatterers into their true
                                  sub-surface positions

─── 11. FASTICA + MULTIFRACTAL DENOISING ────────────────────────────────────
  Li et al. (2022), "FastICA and Multifractal Denoising for GPR Signal"
  Mallat & Hwang (1992), IEEE Trans. Inf. Theory 38(2):617-643 [WTMM theory]

  _morlet_cwt()                Analytic Morlet CWT via FFT (internal)
  multifractal_spectrum()      WTMM partition function → Legendre D(h) spectrum;
                                key feature delta_h: noise is monofractal (small),
                                subsurface signal is multifractal (large)
  ica_decompose_bscan()        FastICA B-scan → N independent components
  ica_multifractal_denoise()   Full Li 2022: ICA → min-delta_h noise ID →
                                zero → reconstruct
"""

# Facade: implementations moved to focused modules (2026-07-02, debt
# D12 in docs/architecture/DEBT_REGISTER.md). All previous names keep
# importing from here; new code may import the focused module directly.
from .preprocessing import (  # noqa: F401
    time_gate,
    peak_relative_coda_gate,
    mean_trace,
    background_subtraction,
    remove_direct_wave,
    _to_bscan,
    svd_select_p,
    svd_denoise,
    svd_remove_direct_wave,
    dewow,
    detect_first_break_coppens,
    detect_first_break_sta_lta,
    detect_first_break,
    time_zero_correction,
    apply_gain,
    remove_gain,
    preprocess_signal,
    preprocess_physical,
    normalize_for_features,
    predictive_deconvolution,
    bandpass_filter,
)
from .vivanco_pipeline import (  # noqa: F401
    vivanco_preprocess,
    vivanco_preprocess_bscan,
    _VIVANCO_DROP_CELLS,
    _vivanco_resample,
    vivanco_extract_features,
)
from .spectral_attributes import (  # noqa: F401
    apply_window,
    compute_spectrum,
    compute_padded_spectrum,
    calculate_instantaneous_attributes,
    compute_spectrogram,
    mpm_decompose,
)
from .reflector_picking import (  # noqa: F401
    C_M_NS,
    pick_reflector,
    reflector_to_depth,
    picks_to_layer_toml,
)
from .bscan_processing import (  # noqa: F401
    _morlet_cwt,
    multifractal_spectrum,
    ica_decompose_bscan,
    ica_multifractal_denoise,
    agc_bscan,
    fk_filter,
    kirchhoff_migration,
)
from .coda_objectives import (  # noqa: F401
    _first_break_sample,
    coda_envelope_correlation,
    coda_energy_ratio,
    _wasserstein_1d,
    coda_wasserstein_distance,
    coda_reflection_amplitude_ratio,
)

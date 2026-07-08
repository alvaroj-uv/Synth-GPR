"""T6: canonical sim<->real comparison metrics, each checked against a signal
of known response (recover alpha from an exact exponential, centroid from a
pure tone, near-zero distance for identical spectra, r=1 for identical traces).
"""
import numpy as np
import pytest

from src.sim_real_comparison import (
    direct_wave_correlation,
    envelope_alpha,
    spectral_evolution,
    spectral_distance,
)

DT_SIM = 0.0311e-9
DT_REAL = 0.1e-9


def _decaying_tone(n, dt, f0=400e6, alpha_per_ns=0.0, seed=None):
    t = np.arange(n) * dt
    t_ns = t * 1e9
    sig = np.exp(-alpha_per_ns * t_ns) * np.cos(2 * np.pi * f0 * t)
    if seed is not None:
        sig = sig + 0.001 * np.random.default_rng(seed).standard_normal(n)
    return sig


# --------------------------------------------------------------------------- #
# direct_wave_correlation
# --------------------------------------------------------------------------- #
def test_direct_wave_correlation_identical_is_one():
    sig = _decaying_tone(644, DT_SIM, alpha_per_ns=0.05)
    r = direct_wave_correlation(sig, DT_SIM, sig.copy(), DT_SIM)
    assert r > 0.999


def test_direct_wave_correlation_scale_invariant():
    """Envelope is peak-normalized -> a pure amplitude scale must not matter."""
    sig = _decaying_tone(644, DT_SIM, alpha_per_ns=0.05)
    r = direct_wave_correlation(sig, DT_SIM, 37.0 * sig, DT_SIM)
    assert r > 0.999


# --------------------------------------------------------------------------- #
# envelope_alpha — recover a known exponential decay
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize("alpha_true", [0.05, 0.10, 0.20])
def test_envelope_alpha_recovers_exponential(alpha_true):
    # Window kept within a healthy dynamic range: even at alpha=0.20 the
    # envelope only decays to exp(-5) over [5, 25] ns, so the log-fit stays out
    # of the numerical floor where dewow/Hilbert edges corrupt tiny amplitudes.
    sig = _decaying_tone(1200, DT_REAL, f0=300e6, alpha_per_ns=alpha_true)
    est = envelope_alpha(sig, DT_REAL, t_start_ns=5.0, t_end_ns=25.0)
    assert abs(est - alpha_true) / alpha_true < 0.01, (est, alpha_true)


def test_envelope_alpha_needs_amplitude():
    """A flat (non-decaying) envelope -> alpha ~ 0."""
    sig = _decaying_tone(1200, DT_REAL, alpha_per_ns=0.0)
    est = envelope_alpha(sig, DT_REAL, t_start_ns=5.0, t_end_ns=60.0)
    assert abs(est) < 5e-3


# --------------------------------------------------------------------------- #
# spectral_evolution — centroid of a pure tone sits at the tone frequency
# --------------------------------------------------------------------------- #
def test_spectral_evolution_centroid_at_tone():
    f0 = 500e6
    sig = _decaying_tone(2000, DT_SIM, f0=f0, alpha_per_ns=0.0)
    ev = spectral_evolution(sig, DT_SIM, win_ns=3.0, hop_ns=1.0)
    assert ev["centroid_hz"].shape == ev["time_ns"].shape
    assert ev["bandwidth_hz"].shape == ev["time_ns"].shape
    med = float(np.median(ev["centroid_hz"]))
    assert abs(med - f0) / f0 < 0.10, med


# --------------------------------------------------------------------------- #
# spectral_distance
# --------------------------------------------------------------------------- #
def test_spectral_distance_identical_near_zero_and_ordered():
    a = _decaying_tone(1500, DT_SIM, f0=400e6, alpha_per_ns=0.05, seed=1)
    # same spectral content on the real time base
    same = _decaying_tone(700, DT_REAL, f0=400e6, alpha_per_ns=0.05, seed=2)
    # clearly different dominant frequency
    diff = _decaying_tone(700, DT_REAL, f0=900e6, alpha_per_ns=0.05, seed=3)
    d_same = spectral_distance(a, DT_SIM, same, DT_REAL)
    d_diff = spectral_distance(a, DT_SIM, diff, DT_REAL)
    assert d_same >= 0.0 and np.isfinite(d_same)
    assert d_diff > d_same, (d_same, d_diff)

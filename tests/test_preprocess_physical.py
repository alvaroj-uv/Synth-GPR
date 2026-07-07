"""T2: physical preprocessing vs feature normalization must stay separate.

preprocess_physical must preserve absolute amplitude (for sigma / envelope
work); normalize_for_features must apply the SAME peak normalization to both
domains in one call (guarding the historic "1/33" collapse where only one
domain was rescaled).
"""
import numpy as np
import pytest

from src.signal_processing import preprocess_physical, normalize_for_features

DT_SIM = 0.0311e-9
DT_REAL = 0.1e-9


def _trace(n=644, dt=DT_SIM, seed=0):
    """Decaying Ricker-ish pulse + noise + DC offset (exercises dewow)."""
    rng = np.random.default_rng(seed)
    t = np.arange(n) * dt
    tau = t - 3e-9
    arg = (np.pi * 400e6 * tau) ** 2
    pulse = (1.0 - 2.0 * arg) * np.exp(-arg)
    return pulse + 0.01 * rng.standard_normal(n) + 0.05


# --------------------------------------------------------------------------- #
# preprocess_physical — amplitude-preserving
# --------------------------------------------------------------------------- #
def test_preprocess_physical_is_amplitude_linear():
    """No gain, no normalization: scaling the input by k scales output by k."""
    sig = _trace()
    out1, _, dt1 = preprocess_physical(sig, DT_SIM)
    out2, _, dt2 = preprocess_physical(1000.0 * sig, DT_SIM)
    assert dt1 == DT_SIM and dt2 == DT_SIM
    assert np.allclose(out2, 1000.0 * out1, rtol=1e-9, atol=0.0), \
        "output not linear in input amplitude -> a gain/normalization leaked in"


def test_preprocess_physical_does_not_peak_normalize():
    """A 7.5x signal must not come out unit-peaked."""
    out, _, _ = preprocess_physical(7.5 * _trace(), DT_SIM, use_dewow=False)
    assert np.max(np.abs(out)) > 1.5


def test_preprocess_physical_requires_dt():
    with pytest.raises(ValueError, match="requires an explicit dt"):
        preprocess_physical(_trace(), None)


def test_preprocess_physical_resamples_to_target_dt():
    out, _, dt_out = preprocess_physical(_trace(n=644, dt=DT_SIM), DT_SIM,
                                         target_dt=DT_REAL)
    assert dt_out == DT_REAL
    assert len(out) == int(round(644 * DT_SIM / DT_REAL))


# --------------------------------------------------------------------------- #
# normalize_for_features — symmetric by construction
# --------------------------------------------------------------------------- #
def test_normalize_for_features_unit_peak_both_domains():
    real_n, sim_n = normalize_for_features(_trace(seed=1)[None, :],
                                           _trace(seed=2)[None, :])
    assert np.allclose(np.max(np.abs(real_n), axis=-1), 1.0)
    assert np.allclose(np.max(np.abs(sim_n), axis=-1), 1.0)


def test_normalize_for_features_erases_scale_mismatch():
    """The 1/33 guard: a constant scale gap between domains is removed
    identically because BOTH pass through the same call -> relative factor 1.0."""
    base = _trace(seed=3)
    real_n, sim_n = normalize_for_features(base[None, :], 33.0 * base[None, :])
    assert np.allclose(real_n, sim_n, atol=1e-9)


def test_normalize_for_features_handles_1d_and_2d():
    r1, s1 = normalize_for_features(_trace(seed=4), _trace(seed=5))
    assert r1.shape == (644,) and np.isclose(np.max(np.abs(r1)), 1.0)
    r2, s2 = normalize_for_features(np.stack([_trace(seed=6), _trace(seed=7)]),
                                    np.stack([_trace(seed=8), _trace(seed=9)]))
    assert r2.shape == (2, 644)
    assert np.allclose(np.max(np.abs(r2), axis=-1), 1.0)


def test_normalize_for_features_rejects_unknown_method():
    with pytest.raises(ValueError, match="Only 'peak'"):
        normalize_for_features(_trace(), _trace(), method="rms")

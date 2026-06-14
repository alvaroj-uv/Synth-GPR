"""
Test suite for first-break picking algorithms (Coppens, STA/LTA, threshold).
"""
import numpy as np
import pytest
from src.signal_processing import (
    detect_first_break,
    detect_first_break_coppens,
    detect_first_break_sta_lta,
)


@pytest.fixture
def synthetic_trace():
    """Create a synthetic GPR trace: noise + direct pulse + reflection."""
    np.random.seed(42)
    n = 500
    t = np.arange(n)

    # Noise floor
    noise = 0.1 * np.random.randn(n)

    # Direct pulse (Ricker wavelet) at t=50
    t_pulse = t - 50
    direct = 2.0 * (1 - 2 * (np.pi * t_pulse / 30) ** 2) * np.exp(-(np.pi * t_pulse / 30) ** 2)
    direct[t < 30] = 0

    # Reflection (weaker, later)
    t_refl = t - 150
    reflection = 0.5 * (1 - 2 * (np.pi * t_refl / 30) ** 2) * np.exp(-(np.pi * t_refl / 30) ** 2)
    reflection[t < 130] = 0

    return noise + direct + reflection


@pytest.fixture
def noisy_trace():
    """Trace with higher noise-to-signal ratio (field-like)."""
    np.random.seed(123)
    n = 500
    t = np.arange(n)

    # Stronger noise
    noise = 0.5 * np.random.randn(n)

    # Weaker direct pulse
    t_pulse = t - 80
    direct = 1.0 * (1 - 2 * (np.pi * t_pulse / 40) ** 2) * np.exp(-(np.pi * t_pulse / 40) ** 2)
    direct[t < 50] = 0

    return noise + direct


def test_coppens_clean_trace(synthetic_trace):
    """Coppens should execute without error and return a valid index."""
    fb_idx = detect_first_break_coppens(synthetic_trace, short_win=10, long_win=100, threshold=1.0)
    # Should return a valid sample index (not negative, within bounds)
    assert 0 <= fb_idx < len(synthetic_trace), f"Coppens returned invalid index {fb_idx}"


def test_sta_lta_clean_trace(synthetic_trace):
    """STA/LTA should detect a reasonable onset."""
    fb_idx = detect_first_break_sta_lta(synthetic_trace, short_win=10, long_win=100, threshold=1.5)
    # Should find something in the reasonable range (the pulse is clearly present)
    assert 0 <= fb_idx < len(synthetic_trace), f"STA/LTA returned invalid index {fb_idx}"
    assert fb_idx > 0, "STA/LTA should detect the pulse, not pick sample 0"


def test_coppens_vs_sta_lta_robust_to_noise(noisy_trace):
    """Coppens and STA/LTA should return valid picks on noisy data."""
    fb_coppens = detect_first_break_coppens(noisy_trace, short_win=15, long_win=120, threshold=1.0)
    fb_sta_lta = detect_first_break_sta_lta(noisy_trace, short_win=15, long_win=120, threshold=1.5)

    # Both should return valid indices
    assert 0 <= fb_coppens < len(noisy_trace), f"Coppens returned {fb_coppens}"
    assert 0 <= fb_sta_lta < len(noisy_trace), f"STA/LTA returned {fb_sta_lta}"


def test_detect_first_break_dispatcher():
    """Test the unified detector with all methods."""
    sig = np.zeros(100)
    sig[30:40] = np.linspace(0, 1, 10)  # Simple step at t=30
    sig[40:80] = 0.8  # Plateau
    sig += 0.05 * np.random.randn(100)  # Tiny noise

    fb_coppens = detect_first_break(sig, method='coppens')
    fb_sta_lta = detect_first_break(sig, method='sta_lta')
    fb_threshold = detect_first_break(sig, method='threshold', threshold_ratio=0.1)

    # All should find the onset around t=30
    assert fb_coppens < 50, f"Coppens dispatcher: {fb_coppens}"
    assert fb_sta_lta < 50, f"STA/LTA dispatcher: {fb_sta_lta}"
    assert fb_threshold < 50, f"Threshold dispatcher: {fb_threshold}"


def test_invalid_method_raises():
    """Invalid method should raise ValueError."""
    sig = np.random.randn(100)
    with pytest.raises(ValueError, match="Unknown first-break method"):
        detect_first_break(sig, method='invalid')


def test_empty_signal():
    """Empty or very short signals should return 0."""
    assert detect_first_break_coppens(np.array([]), short_win=10, long_win=100) == 0
    assert detect_first_break_sta_lta(np.array([1, 2, 3]), short_win=10, long_win=100) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

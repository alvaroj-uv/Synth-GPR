#!/usr/bin/env python3
"""
Unit tests for the windowed-indicator and energy-integration-curve feature blocks
added to src.feature_extraction:

  - _extract_window_features        (ballast/coda gated StAb / Hilbert / CrossNum / InflecNum)
  - _extract_energy_curve_features  (time-domain cumulative-energy descriptors)

Motivated by Li et al. (2023) and Shapovalov et al. (2026): fouling concentrates trace
energy earlier in time and changes gated waveform statistics. These tests check the
features are present, finite, well-bounded, monotone where expected, and degenerate-safe.
"""

import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.constants import SC
from src.feature_extraction import (
    extract_features_from_signal,
    _extract_window_features,
    _extract_energy_curve_features,
)
from src.signal_processing import calculate_instantaneous_attributes

DT = 1e-11  # 10 ps step → 1024 samples span ~10.24 ns... use more samples for the 6-16 ns gate
N = 4096    # 40.96 ns total at DT=1e-11, so the 6-16 ns gate is well populated


def _analytic(signal):
    attrs = calculate_instantaneous_attributes(signal, DT, use_mirroring=True)
    return attrs['envelope'] * np.exp(1j * attrs['phase'])


def _gaussian_pulse(center_ns, width_ns=1.0, n=N, dt=DT):
    """A Gaussian-enveloped tone centered at center_ns (energy localized in time)."""
    t_ns = np.arange(n) * dt * SC.NS_PER_SEC
    env = np.exp(-0.5 * ((t_ns - center_ns) / width_ns) ** 2)
    return env * np.sin(2 * np.pi * 1.0e9 * (t_ns - center_ns) * 1e-9)


EXPECTED_WINDOW_KEYS = {
    'win_area_signal', 'win_area_hilbert', 'win_rms', 'win_std',
    'win_energy_fraction', 'win_number_zeros', 'win_inflection_count',
    'win_peak_count', 'win_hilbert_mean', 'win_hilbert_peak_max',
}
EXPECTED_ENERGY_KEYS = {
    'energy_time_q25', 'energy_time_q50', 'energy_time_q75', 'energy_time_q85',
    'energy_centroid_time', 'early_late_energy_ratio', 'energy_curve_auc',
}


# --------------------------------------------------------------------------- #
# Presence + finiteness in the full pipeline
# --------------------------------------------------------------------------- #
def test_new_features_present_in_pipeline():
    sig = _gaussian_pulse(center_ns=10.0)
    df = extract_features_from_signal(sig, dt=DT)
    cols = set(df.columns)
    assert EXPECTED_WINDOW_KEYS <= cols, EXPECTED_WINDOW_KEYS - cols
    assert EXPECTED_ENERGY_KEYS <= cols, EXPECTED_ENERGY_KEYS - cols
    row = df.iloc[0]
    for k in EXPECTED_WINDOW_KEYS | EXPECTED_ENERGY_KEYS:
        assert np.isfinite(row[k]), f"{k} is not finite: {row[k]}"


# --------------------------------------------------------------------------- #
# Window features: bounds + correctness
# --------------------------------------------------------------------------- #
def test_window_energy_fraction_bounded():
    sig = _gaussian_pulse(center_ns=10.0)
    feats = _extract_window_features(sig, _analytic(sig), DT)
    assert 0.0 <= feats['win_energy_fraction'] <= 1.0


def test_window_captures_coda_after_peak():
    """Peak-relative gate: a trace with coda energy after the direct pulse scores
    higher gated energy than a bare direct pulse. The gate opens
    CODA_GATE_START_AFTER_PEAK_NS after the dominant peak."""
    pulse = _gaussian_pulse(center_ns=10.0)                       # direct pulse (peak ~10 ns)
    coda = 0.15 * _gaussian_pulse(center_ns=18.0, width_ns=2.0)   # subsurface energy inside gate
    with_coda = pulse + coda
    f_with = _extract_window_features(with_coda, _analytic(with_coda), DT)
    f_bare = _extract_window_features(pulse, _analytic(pulse), DT)
    assert f_with['win_energy_fraction'] > f_bare['win_energy_fraction']
    assert f_with['win_area_signal'] > f_bare['win_area_signal']
    assert f_with['win_hilbert_peak_max'] > f_bare['win_hilbert_peak_max']


def test_window_gate_is_peak_relative():
    """The same coda offset from its pulse scores the same regardless of WHERE the
    pulse sits in absolute time — the whole point of peak-relative gating."""
    def trace(pulse_ns):
        return _gaussian_pulse(center_ns=pulse_ns) + \
               0.15 * _gaussian_pulse(center_ns=pulse_ns + 8.0, width_ns=2.0)
    f_early = _extract_window_features(trace(6.0), _analytic(trace(6.0)), DT)
    f_late = _extract_window_features(trace(14.0), _analytic(trace(14.0)), DT)
    assert f_early['win_energy_fraction'] == pytest.approx(
        f_late['win_energy_fraction'], rel=0.15)


def test_window_degenerate_gate_is_safe():
    """Trace far too short to reach the gate → all-zero, no crash."""
    short = np.sin(np.linspace(0, 6 * np.pi, 16))  # ~0.16 ns total at DT
    feats = _extract_window_features(short, _analytic(short), DT)
    assert set(feats.keys()) == EXPECTED_WINDOW_KEYS
    assert all(v == 0.0 for v in feats.values())


# --------------------------------------------------------------------------- #
# Energy-curve features: bounds + ordering + physical monotonicity
# --------------------------------------------------------------------------- #
def test_energy_quantile_positions_monotone_and_bounded():
    sig = _gaussian_pulse(center_ns=12.0)
    feats = _extract_energy_curve_features(sig)
    q = [feats['energy_time_q25'], feats['energy_time_q50'],
         feats['energy_time_q75'], feats['energy_time_q85']]
    assert all(0.0 <= x <= 1.0 for x in q)
    assert q == sorted(q), f"quantile positions not nondecreasing: {q}"
    assert 0.0 <= feats['energy_curve_auc'] <= 1.0
    assert 0.0 <= feats['energy_centroid_time'] <= 1.0


def test_early_energy_gives_higher_auc_and_earlier_median():
    """
    Core physical check (Li 2023): energy concentrated EARLY (fouled-like, fast decay)
    → higher cumulative-curve AUC and earlier q50 than energy concentrated LATE.
    """
    early = _gaussian_pulse(center_ns=6.0)
    late = _gaussian_pulse(center_ns=34.0)
    fe = _extract_energy_curve_features(early)
    fl = _extract_energy_curve_features(late)
    assert fe['energy_curve_auc'] > fl['energy_curve_auc']
    assert fe['energy_time_q50'] < fl['energy_time_q50']
    assert fe['early_late_energy_ratio'] > fl['early_late_energy_ratio']


def test_energy_curve_zero_signal_is_safe():
    feats = _extract_energy_curve_features(np.zeros(N))
    assert set(feats.keys()) == EXPECTED_ENERGY_KEYS
    assert all(v == 0.0 for v in feats.values())


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))

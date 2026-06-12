#!/usr/bin/env python3
"""
Tests for feature-extraction v2 (physical units + peak-relative gating).

Key properties under test:
  - dt is mandatory in spirit: omitting it warns loudly (the 0.1 ns default
    silently mis-scaled all sim frequency features by 3.2x once already).
  - Physical-scale invariance: the SAME physical waveform sampled at the sim
    time base (dt~0.031 ns) and the real time base (dt=0.1 ns) produces the
    same wavelet scale and compatible spectral features.
  - Real-data continuity: at dt=0.1 ns the new ns-specified wavelet widths
    reduce exactly to the legacy sample widths (2,4,8,16,32), so the real
    corpus features are unchanged.
  - Band edges are relative to centre frequency (no degenerate bands at 400 MHz).
  - The coda gate is peak-relative, not absolute.
  - median_frequency (the metric behind the real +3.6 MHz/FI result) is
    definitionally unchanged: a pure tone's median frequency is the tone.
"""

import sys
import warnings
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.constants import SC
from src.feature_extraction import extract_features_from_signal
from src.signal_processing import peak_relative_coda_gate

DT_SIM = 3.11e-11   # synthetic .out time base (~0.0311 ns)
DT_REAL = 1.0e-10   # real field CSV time base (0.1 ns)
FC = 400e6          # 400 MHz centre frequency


def _trace(dt, n_ns=20.0, fc=FC, peak_ns=3.0, coda=True, seed=0):
    """Direct pulse (ricker-ish) + optional weak decaying coda, on any time base."""
    n = int(round(n_ns * 1e-9 / dt))
    t = np.arange(n) * dt
    tau = (t - peak_ns * 1e-9) * fc
    pulse = (1 - 2 * (np.pi * tau) ** 2) * np.exp(-(np.pi * tau) ** 2)  # ricker
    sig = 1000.0 * pulse
    if coda:
        rng = np.random.default_rng(seed)
        env = np.exp(-(t - peak_ns * 1e-9).clip(0) / 6e-9)
        band = np.cos(2 * np.pi * fc * 0.9 * t + rng.uniform(0, 2 * np.pi))
        sig = sig + 4.0 * env * band * (t > (peak_ns + 1.0) * 1e-9)
    return sig


# --------------------------------------------------------------------------- #
# dt guardrail
# --------------------------------------------------------------------------- #
def test_missing_dt_warns():
    sig = _trace(DT_REAL)
    with pytest.warns(UserWarning, match="without dt"):
        extract_features_from_signal(sig)


def test_explicit_dt_does_not_warn():
    sig = _trace(DT_REAL)
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        extract_features_from_signal(sig, dt=DT_REAL, center_freq_hz=FC)


# --------------------------------------------------------------------------- #
# Sanity: finiteness, determinism, provenance
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize("dt", [DT_SIM, DT_REAL])
def test_features_finite_and_deterministic(dt):
    sig = _trace(dt)
    df1 = extract_features_from_signal(sig, dt=dt, center_freq_hz=FC)
    df2 = extract_features_from_signal(sig, dt=dt, center_freq_hz=FC)
    num = df1.drop(columns=['Signal'])
    assert np.all(np.isfinite(num.values.astype(float))), "non-finite feature values"
    assert df1.equals(df2), "extraction is not deterministic"


def test_provenance_meta_columns():
    sig = _trace(DT_SIM)
    df = extract_features_from_signal(sig, dt=DT_SIM, center_freq_hz=FC)
    row = df.iloc[0]
    assert row['meta_feature_version'] == SC.FEATURE_VERSION
    assert row['meta_dt_ns'] == pytest.approx(DT_SIM * 1e9)
    assert row['meta_center_freq_mhz'] == pytest.approx(400.0)


# --------------------------------------------------------------------------- #
# Physical-scale invariance across time bases (THE v2 property)
# --------------------------------------------------------------------------- #
def test_physical_invariance_across_time_bases():
    """Same physical waveform at sim vs real dt -> same physical-scale features."""
    f_sim = extract_features_from_signal(_trace(DT_SIM), dt=DT_SIM, center_freq_hz=FC).iloc[0]
    f_real = extract_features_from_signal(_trace(DT_REAL), dt=DT_REAL, center_freq_hz=FC).iloc[0]

    # Wavelet peak scale is now in ns and must agree exactly (same scale grid)
    assert f_sim['wavelet_peak_scale'] == f_real['wavelet_peak_scale']

    # Spectral location features must agree (already dt-correct, regression guard)
    assert f_sim['dominant_frequency'] == pytest.approx(f_real['dominant_frequency'], rel=0.10)
    assert f_sim['mean_frequency'] == pytest.approx(f_real['mean_frequency'], rel=0.15)

    # Relative band split must be comparable across time bases
    assert f_sim['mid_low_energy_ratio'] == pytest.approx(
        f_real['mid_low_energy_ratio'], rel=0.35)


def test_real_dt_wavelet_widths_match_legacy():
    """Continuity: at dt=0.1 ns the ns widths reduce to the legacy sample widths."""
    widths_samples = np.asarray(SC.WAVELET_WIDTHS_NS) * 1e-9 / DT_REAL
    assert np.allclose(widths_samples, [2, 4, 8, 16, 32])
    # and the legacy STFT window: 6.4 ns / 0.1 ns = 64 samples
    assert int(round(SC.STFT_NPERSEG_NS * 1e-9 / DT_REAL)) == 64


# --------------------------------------------------------------------------- #
# Relative band edges
# --------------------------------------------------------------------------- #
def test_band_edges_relative_not_degenerate_at_400mhz():
    """At 400 MHz with a high-frequency component present, the high band must
    see energy. (Legacy absolute edges put ALL 400 MHz energy in 'low'.)"""
    dt = DT_REAL
    n = 512
    t = np.arange(n) * dt
    win = np.hanning(n)
    sig = win * (np.sin(2 * np.pi * 400e6 * t) + 0.5 * np.sin(2 * np.pi * 900e6 * t))
    f = extract_features_from_signal(sig, dt=dt, center_freq_hz=400e6).iloc[0]
    # 900 MHz > 1.5*400 MHz = 600 MHz -> lands in the high band
    assert f['high_low_energy_ratio'] > 0.05
    # most energy still at/below fc
    assert f['mid_low_energy_ratio'] > 0


def test_median_frequency_definition_unchanged():
    """median_frequency must remain the amplitude-spectrum median: for a pure
    windowed tone it sits on the tone. Guards the real +3.6 MHz/FI metric."""
    dt = DT_REAL
    n = 1024
    t = np.arange(n) * dt
    sig = np.hanning(n) * np.sin(2 * np.pi * FC * t)
    f = extract_features_from_signal(sig, dt=dt, center_freq_hz=FC).iloc[0]
    assert f['median_frequency'] == pytest.approx(FC, rel=0.05)
    assert f['dominant_frequency'] == pytest.approx(FC, rel=0.05)


# --------------------------------------------------------------------------- #
# Peak-relative coda gate
# --------------------------------------------------------------------------- #
def test_gate_opens_after_peak():
    dt = DT_REAL
    sig = _trace(dt, peak_ns=5.0)
    mask, pk = peak_relative_coda_gate(sig, dt)
    t_ns = np.arange(len(sig)) * dt * 1e9
    assert t_ns[pk] == pytest.approx(5.0, abs=0.5)
    gate_t = t_ns[mask]
    assert gate_t[0] >= 5.0 + SC.CODA_GATE_START_AFTER_PEAK_NS - 0.2
    span = gate_t[-1] - gate_t[0]
    assert span <= SC.CODA_GATE_LENGTH_NS + 0.2


def test_gate_seek_peak_false_starts_at_zero():
    """For peak-aligned traces (real field data) the gate is relative to sample 0."""
    dt = DT_REAL
    sig = _trace(dt, peak_ns=5.0)
    mask, pk = peak_relative_coda_gate(sig, dt, seek_peak=False)
    assert pk == 0
    t_ns = np.arange(len(sig)) * dt * 1e9
    assert t_ns[mask][0] == pytest.approx(SC.CODA_GATE_START_AFTER_PEAK_NS, abs=0.2)


# --------------------------------------------------------------------------- #
# Phase 2: coda-first suite + attenuation family
# --------------------------------------------------------------------------- #
def _trace_with_tau(dt, tau_ns, n_ns=24.0, peak_ns=3.0, seed=1):
    """Direct pulse + coda whose envelope decays with time constant tau_ns."""
    n = int(round(n_ns * 1e-9 / dt))
    t = np.arange(n) * dt
    targ = (t - peak_ns * 1e-9) * FC
    pulse = 1000.0 * (1 - 2 * (np.pi * targ) ** 2) * np.exp(-(np.pi * targ) ** 2)
    rng = np.random.default_rng(seed)
    env = np.exp(-(t - peak_ns * 1e-9).clip(0) / (tau_ns * 1e-9))
    coda = 5.0 * env * np.cos(2 * np.pi * FC * t + rng.uniform(0, 2 * np.pi))
    return pulse + coda * (t > (peak_ns + 1.0) * 1e-9)


def test_coda_suite_present_and_finite():
    sig = _trace(DT_REAL)
    df = extract_features_from_signal(sig, dt=DT_REAL, center_freq_hz=FC)
    cols = list(df.columns)
    coda_cols = [c for c in cols if c.startswith('coda_')]
    att_cols = [c for c in cols if c.startswith('att_')]
    assert len(att_cols) == 11, att_cols
    # the coda suite includes the 480-cell aligned-coda grid
    assert sum(c.startswith('coda_grid_') for c in coda_cols) == 480
    row = df.iloc[0]
    vals = row[coda_cols + att_cols].astype(float).values
    assert np.all(np.isfinite(vals))
    # there IS coda energy in this trace -> gated features must be non-trivial
    assert row['coda_root_mean_square'] > 0


def test_attenuation_orders_decay_rate():
    """Faster-decaying coda (fouled-like) -> more negative envelope decay rate."""
    fast = _trace_with_tau(DT_REAL, tau_ns=2.0)
    slow = _trace_with_tau(DT_REAL, tau_ns=10.0)
    f_fast = extract_features_from_signal(fast, dt=DT_REAL, center_freq_hz=FC).iloc[0]
    f_slow = extract_features_from_signal(slow, dt=DT_REAL, center_freq_hz=FC).iloc[0]
    assert f_fast['att_env_decay_rate'] < f_slow['att_env_decay_rate'] < 0


def test_coda_features_scale_invariant():
    """Coda features are computed on the peak-normalized segment, so they must
    be identical under global amplitude scaling (sim vs real amplitude gap)."""
    sig = _trace(DT_REAL)
    f1 = extract_features_from_signal(sig, dt=DT_REAL, center_freq_hz=FC).iloc[0]
    f2 = extract_features_from_signal(100.0 * sig, dt=DT_REAL, center_freq_hz=FC).iloc[0]
    keys = [k for k in f1.index if k.startswith(('coda_', 'att_'))]
    v1 = f1[keys].astype(float).values
    v2 = f2[keys].astype(float).values
    np.testing.assert_allclose(v1, v2, rtol=1e-9, atol=1e-12)


def test_degenerate_no_coda_is_safe():
    """Trace too short for any coda after the peak -> zeros, never NaN/crash."""
    dt = DT_REAL
    sig = _trace(dt, n_ns=4.0, peak_ns=3.0, coda=False)  # ends 1 ns after peak
    df = extract_features_from_signal(sig, dt=dt, center_freq_hz=FC)
    row = df.iloc[0]
    keys = [k for k in df.columns if k.startswith(('coda_', 'att_'))]
    vals = row[keys].astype(float).values
    assert np.all(np.isfinite(vals))
    assert row['coda_root_mean_square'] == 0.0


def test_legacy_blocks_flag():
    sig = _trace(DT_REAL)
    df_new = extract_features_from_signal(sig, dt=DT_REAL, center_freq_hz=FC)
    df_old = extract_features_from_signal(sig, dt=DT_REAL, center_freq_hz=FC,
                                          include_legacy_blocks=True)
    new_cols, old_cols = set(df_new.columns), set(df_old.columns)
    # default drops the whole-trace direct-pulse blocks...
    for legacy in ('grid_signal_time_0_0', 'stat_slice_0_mean', 'decile_10',
                   'hilbert_decile_10'):
        assert legacy not in new_cols
        assert legacy in old_cols
    # ...but keeps them on the coda
    assert 'coda_grid_signal_time_0_0' in new_cols
    assert 'coda_stat_slice_0_mean' in new_cols
    assert bool(df_new.iloc[0]['meta_includes_legacy']) is False
    assert bool(df_old.iloc[0]['meta_includes_legacy']) is True


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))

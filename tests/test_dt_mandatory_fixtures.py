"""Block 3 / T1 on the known-truth fixtures: dt is mandatory and dt MATTERS.

Uses the real fixture batch (tests/fixtures/sim/*.out, dt=0.0311 ns from the
HDF5 attr; tests/fixtures/real/*.npy, dt=0.098 ns) to prove:
  1. extract_features refuses to run without an explicit dt (ValueError).
  2. The fixture dt read from the source matches ground_truth.json (never
     assumed).
  3. The same trace claimed at the WRONG time base mis-scales every Hz-valued
     frequency feature by ~the dt ratio (~3.2x) — the historic bug class.
  4. Positive control: the same physical signal on the two grids, each
     extracted with ITS OWN dt, agrees on frequency content (dt handled
     correctly end-to-end through the resampler).
"""
import json
from pathlib import Path

import h5py
import numpy as np
import pytest

from src.feature_extraction import extract_features_from_signal
from src.preprocessing import preprocess_physical

FIXTURES = Path(__file__).parent / "fixtures"
SIM_OUT = FIXTURES / "sim" / "scene_0001.out"
REAL_NPY = FIXTURES / "real" / "trace_0000.npy"
DT_REAL = 0.098e-9   # real fixture time base (see tests/validate_fixtures.py)
FC = 420e6

pytestmark = pytest.mark.skipif(
    not (SIM_OUT.exists() and REAL_NPY.exists()),
    reason="known-truth fixtures missing (tests/fixtures/)",
)


def _sim_trace():
    """Fixture trace + its dt read from the SOURCE (HDF5 attr), never assumed."""
    with h5py.File(SIM_OUT, "r") as f:
        return f["rxs/rx1/Ez"][:], float(f.attrs["dt"])


# --------------------------------------------------------------------------- #
# 1. dt is mandatory — on both fixture domains
# --------------------------------------------------------------------------- #
def test_dt_is_mandatory_on_fixture_traces():
    sim, _ = _sim_trace()
    with pytest.raises(ValueError, match="requires an explicit dt"):
        extract_features_from_signal(sim)
    real = np.load(REAL_NPY)
    with pytest.raises(ValueError, match="requires an explicit dt"):
        extract_features_from_signal(real)


# --------------------------------------------------------------------------- #
# 2. the source dt matches the embedded ground truth
# --------------------------------------------------------------------------- #
def test_fixture_sim_dt_matches_ground_truth():
    _, dt = _sim_trace()
    gt = json.load(open(FIXTURES / "ground_truth.json"))
    assert abs(dt * 1e9 - gt["sim/scene_0001"]["dt_ns"]) < 1e-3


# --------------------------------------------------------------------------- #
# 3. dt matters: wrong time base mis-scales frequency features by ~3.2x
# --------------------------------------------------------------------------- #
def test_wrong_dt_mis_scales_frequency_features():
    sim, dt_sim = _sim_trace()
    # Same trace, resampled onto the real grid...
    res, _, dt_out = preprocess_physical(sim, dt_sim, target_dt=DT_REAL)
    f_ok = extract_features_from_signal(res, dt=dt_out, center_freq_hz=FC).iloc[0]
    # ...but CLAIMED at the sim time base (the historic bug, in reverse):
    f_bad = extract_features_from_signal(res, dt=dt_sim, center_freq_hz=FC).iloc[0]

    ratio = f_bad["dominant_frequency"] / f_ok["dominant_frequency"]
    expected = DT_REAL / dt_sim          # ≈ 3.15 for 0.098/0.0311
    assert ratio == pytest.approx(expected, rel=0.05), (
        f"dominant_frequency should scale by the dt ratio; got {ratio:.2f}"
    )
    assert ratio > 2.5, "wrong dt must be a MATERIAL error, not a rounding one"


# --------------------------------------------------------------------------- #
# 4. positive control: correct dt on each grid -> consistent frequency content
# --------------------------------------------------------------------------- #
def test_correct_dt_survives_resampling():
    sim, dt_sim = _sim_trace()
    nat, _, _ = preprocess_physical(sim, dt_sim)                    # native grid
    res, _, dt_out = preprocess_physical(sim, dt_sim, target_dt=DT_REAL)
    f_nat = extract_features_from_signal(nat, dt=dt_sim, center_freq_hz=FC).iloc[0]
    f_res = extract_features_from_signal(res, dt=dt_out, center_freq_hz=FC).iloc[0]
    assert f_res["dominant_frequency"] == pytest.approx(
        f_nat["dominant_frequency"], rel=0.2
    ), "same signal, each grid with its own dt, must agree on dominant frequency"

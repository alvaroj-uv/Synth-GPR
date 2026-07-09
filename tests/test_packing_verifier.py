"""T9: packing verifier — 3 controls.

Control 1 (geometry) runs with no simulation. Control 2 (emergent eps from the
surface->base timing) is checked here on a synthetic trace with a reflection at
the exact TWT for a known (eps, thickness): the recovered eps must be within 5%.
The end-to-end gprMax check (a homogeneous slab of known eps) is exercised
separately as an integration run, not in this unit test.
"""
import numpy as np
import pytest

from src.packing_verifier import (
    emergent_eps_from_timing,
    verify_effective_eps,
    verify_geometry,
    verify_scene,
    calibrate_fill_for_eps,
)

_C = 299_792_458.0


def _two_reflection_trace(eps_true, thickness_m, dt=0.05e-9, n=3000,
                          t_direct_ns=3.0, base_amp=0.4, f0=400e6):
    """Direct wave + a base reflection at the TWT for (eps_true, thickness)."""
    twt_ns = (2.0 * thickness_m * np.sqrt(eps_true) / _C) * 1e9
    t_ns = np.arange(n) * dt * 1e9

    def ricker(tc_ns):
        tau = (t_ns - tc_ns) * 1e-9
        arg = (np.pi * f0 * tau) ** 2
        return (1.0 - 2.0 * arg) * np.exp(-arg)

    return ricker(t_direct_ns) + base_amp * ricker(t_direct_ns + twt_ns), dt, twt_ns


# --------------------------------------------------------------------------- #
# Control 2 — emergent eps from timing
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize("eps_true", [4.0, 6.0, 9.0])
def test_emergent_eps_recovers_known_slab(eps_true):
    thickness = 0.35
    sig, dt, _ = _two_reflection_trace(eps_true, thickness)
    eps, pick = emergent_eps_from_timing(sig, dt, thickness)
    assert pick["found"]
    assert abs(eps - eps_true) / eps_true < 0.05, (eps, eps_true)


def test_verify_effective_eps_pass_and_fail():
    thickness = 0.35
    sig, dt, _ = _two_reflection_trace(6.0, thickness)
    ok = verify_effective_eps(sig, dt, expected_eps=6.0, thickness_m=thickness)
    assert ok["pass"] and ok["rel_error"] < 0.05
    bad = verify_effective_eps(sig, dt, expected_eps=12.0, thickness_m=thickness)
    assert not bad["pass"]


# --------------------------------------------------------------------------- #
# Control 1 — geometry (no simulation)
# --------------------------------------------------------------------------- #
def test_verify_geometry_fill_and_grading():
    ok = verify_geometry(0.40, 0.42,
                         achieved_sieve_pct=[100, 80, 40, 10],
                         target_sieve_pct=[100, 75, 45, 12])
    assert ok["fill_pass"] and ok["grading_pass"]
    assert ok["grading_ks_pct"] == 5.0

    bad = verify_geometry(0.15, 0.42)          # far too dense
    assert not bad["fill_pass"]


# --------------------------------------------------------------------------- #
# Orchestrator
# --------------------------------------------------------------------------- #
def test_verify_scene_verdicts():
    geom_ok = verify_geometry(0.41, 0.42)
    geom_bad = verify_geometry(0.15, 0.42)
    coh_ok = {"pass": True, "emergent_eps": 6.0, "expected_eps": 6.0, "rel_error": 0.0}
    coh_bad = {"pass": False, "emergent_eps": 3.0, "expected_eps": 6.0, "rel_error": 0.5}

    assert verify_scene(geometry=geom_ok, coherent=coh_ok)["verdict"] == "PASS"
    assert verify_scene(geometry=geom_bad, coherent=coh_ok)["verdict"] == "ADJUST"
    assert verify_scene(geometry=geom_ok, coherent=coh_bad)["verdict"] == "REJECT"


# --------------------------------------------------------------------------- #
# 2-D fill -> emergent-eps calibration (monotonic bisection)
# --------------------------------------------------------------------------- #
def test_calibrate_fill_for_eps_bisection():
    # synthetic monotonic response: emergent_eps = 3 + 8*fill
    fill, eps, n = calibrate_fill_for_eps(
        target_eps=6.0, run_and_measure=lambda f: 3.0 + 8.0 * f,
        fill_lo=0.10, fill_hi=0.50, tol=0.02)
    assert abs(eps - 6.0) / 6.0 <= 0.02
    assert 0.10 <= fill <= 0.50

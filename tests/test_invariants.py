"""Invariants rescued from the old tests/verify/ scripts.

Most of tests/verify/ was archived to attic/tests_verify/ (T13): those scripts
were print-and-eyeball checks, several referenced APIs that drifted in the
refactor (e.g. WorkOrder(params=...)), and one imported a non-package path. The
one still-valid, dependency-light invariant is the FI<->PVC physics round-trip,
rescued here as real assertions.
"""
import pytest

from src.physics import convert_pvc_to_fi, inverse_convert_fi_to_pvc


@pytest.mark.parametrize("target_fi", [1.0, 5.0, 10.0, 20.0, 30.0])
def test_fi_pvc_round_trip_in_valid_range(target_fi):
    """FI -> PVC -> FI is exact below the mass-ratio saturation cap."""
    pvc = inverse_convert_fi_to_pvc(target_fi)
    back = convert_pvc_to_fi(pvc)
    assert abs(back - target_fi) < 1e-4, (target_fi, pvc, back)


def test_fi_mass_ratio_saturates_above_cap():
    """Documents the known limitation (memory 'Two FI Definitions'): the
    mass-ratio convert_pvc_to_fi saturates below ~40, so a high target FI cannot
    be reproduced by the round-trip. This guards anyone from assuming the
    round-trip is global (the old verify_physics_math sys.exit(1)'d on it)."""
    back = convert_pvc_to_fi(inverse_convert_fi_to_pvc(45.0))
    assert abs(back - 45.0) > 0.5, back      # did NOT reach 45 — saturated

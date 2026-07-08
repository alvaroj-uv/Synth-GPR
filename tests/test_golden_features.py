"""Golden regression for the full feature-extraction chain (~572 features).

Locks extract_features output for two frozen fixture traces (a synthetic
.out-scale trace and a synthetic stand-in for a real DZT trace) so that an
accidental change to the chain — a shifted constant, a reordered block, or a
class of bug like the historic 0.1 ns dt default or the 1/33 scale collapse —
fails loudly instead of silently corrupting every downstream result.

To intentionally update the baseline (and only then):
    python tests/regenerate_golden.py --yes
with a commit message that justifies why the feature outputs changed.
"""
import json
from pathlib import Path

import numpy as np
import pytest

from src.feature_extraction import extract_features_from_signal

FIXTURES = Path(__file__).parent / "fixtures"
CENTER_FREQ_HZ = 400e6      # must match regenerate_golden.py
RTOL = 1e-9

pytestmark = pytest.mark.skipif(
    not (FIXTURES / "golden_features.json").exists(),
    reason="golden fixtures missing — run: python tests/regenerate_golden.py --yes",
)


@pytest.fixture(scope="module")
def golden():
    traces = np.load(FIXTURES / "golden_traces.npz")
    with open(FIXTURES / "golden_features.json") as f:
        expected = json.load(f)
    return traces, expected


def _extract(sig, dt):
    df = extract_features_from_signal(sig, dt=dt, center_freq_hz=CENTER_FREQ_HZ)
    row = df.iloc[0].to_dict()
    got = {}
    for k, v in row.items():
        if k == "Signal":
            continue
        try:
            got[k] = float(v)
        except (TypeError, ValueError):
            continue
    return got


@pytest.mark.parametrize("name", ["sim", "real"])
def test_golden_features(golden, name):
    traces, expected = golden
    got = _extract(traces[name], float(traces[f"{name}_dt"]))
    exp = expected[name]

    # Structural: the exact feature set must match (adding/removing a feature
    # or renaming one is a regression too).
    assert set(got) == set(exp), (
        f"feature set drift for '{name}': "
        f"added={sorted(set(got) - set(exp))[:8]} "
        f"removed={sorted(set(exp) - set(got))[:8]}"
    )

    # Numeric: every feature within rtol of the frozen baseline.
    mismatches = [
        (k, got[k], exp[k])
        for k in exp
        if not np.isclose(got[k], exp[k], rtol=RTOL, atol=0.0, equal_nan=True)
    ]
    assert not mismatches, (
        f"{len(mismatches)} feature(s) drifted for '{name}' (rtol={RTOL}); "
        f"first few (name, got, expected): {mismatches[:5]}"
    )

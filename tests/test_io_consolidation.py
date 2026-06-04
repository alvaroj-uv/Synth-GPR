#!/usr/bin/env python3
"""
Phase 0 guardrails for the file-I/O consolidation (see
docs/architecture/IO_CONSOLIDATION_PLAN.md).

These characterization tests pin the behavior of the canonical `.out` readers
in `src.data_loader` against the exact raw-`h5py` patterns the scripts use
today, so the Phase 1 migration is provably faithful.

Two layers:
  * Synthetic HDF5 (always runs, committable) — exercises the reader contracts.
  * Real fixtures in tests/test_files/ (skipped when absent — gitignored) —
    proves byte-identity against the legacy inline reads on production data.
"""

import sys
from pathlib import Path

import h5py
import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data_loader import read_ascan, read_rx_traces, write_rx_out

FIXTURES = Path(__file__).parent / "test_files"
REAL_OUT = sorted(FIXTURES.glob("*.out"))[:1]
COMPONENTS = ("Ex", "Ey", "Ez", "Hx", "Hy", "Hz")


def _write_multicomp_out(path, n=256, dt=3.1e-11):
    """Synthetic gprMax-style .out with all six components on one receiver."""
    rng = np.random.default_rng(0)
    with h5py.File(path, "w") as f:
        f.attrs["dt"] = dt
        f.attrs["Iterations"] = n
        rx = f.create_group("rxs/rx1")
        rx.attrs["Position"] = [0.1, 0.2, 0.0]
        for i, c in enumerate(COMPONENTS):
            rx.create_dataset(c, data=(rng.standard_normal(n) * (i + 1)).astype(np.float32))


# ── Legacy patterns reproduced inline (the code being replaced) ───────────────

def _legacy_load_ez(p):
    """Pattern A: `np.array(f['rxs/rx1/Ez']).astype(float)`, raw dt."""
    f = h5py.File(p, "r")
    dt = f.attrs["dt"]
    ez = np.array(f["rxs/rx1/Ez"]).astype(float)
    f.close()
    return ez, dt


def _legacy_load_viz(p, component="Ez"):
    """Pattern B: viz read returning (t_ns, signal, comp, dt)."""
    with h5py.File(p, "r") as f:
        dt = float(f.attrs["dt"])
        iterations = int(f.attrs["Iterations"])
        rx = f["rxs/rx1"]
        comp = component if component in rx else ("Ez" if "Ez" in rx else list(rx.keys())[0])
        signal = rx[comp][:]
    t_ns = np.arange(iterations) * dt * 1e9
    return t_ns, signal, comp, dt


def _legacy_load_dominant(p):
    """Pattern C: dominant-by-energy component among Ex/Ey/Ez on first rx."""
    f = h5py.File(p, "r")
    dt = f.attrs["dt"]
    rxg = f["rxs"]
    rk = list(rxg.keys())[0]
    best, best_amp = None, -1.0
    for c in ("Ex", "Ey", "Ez"):
        if c in rxg[rk]:
            arr = np.array(rxg[rk][c]).astype(float)
            amp = np.abs(arr).max()
            if amp > best_amp:
                best, best_amp = c, amp
    f.close()
    return best, dt


# ── Synthetic equivalence (always runs) ───────────────────────────────────────

class TestReadAscanMatchesLegacy:
    def test_pattern_a_ez_and_dt(self, tmp_path):
        p = tmp_path / "syn.out"
        _write_multicomp_out(p)
        ez_old, dt_old = _legacy_load_ez(p)

        d = read_ascan(p)
        ez_new = d["signal"].astype(float)
        np.testing.assert_array_equal(ez_new, ez_old)
        assert float(d["dt"]) == float(dt_old)

    def test_pattern_b_viz_tuple(self, tmp_path):
        p = tmp_path / "syn.out"
        _write_multicomp_out(p)
        t_old, sig_old, comp_old, dt_old = _legacy_load_viz(p)

        d = read_ascan(p, "Ez")
        np.testing.assert_array_equal(d["t_ns"], t_old)
        np.testing.assert_array_equal(d["signal"], sig_old)
        assert d["component"] == comp_old
        assert d["dt"] == dt_old

    def test_pattern_b_missing_component_fallback(self, tmp_path):
        p = tmp_path / "syn.out"
        _write_multicomp_out(p)
        # request a component that is absent -> both fall back to Ez
        _, _, comp_old, _ = _legacy_load_viz(p, component="Foo")
        d = read_ascan(p, "Foo")
        assert d["component"] == comp_old == "Ez"


class TestReadRxTracesMatchesLegacy:
    def test_pattern_c_dominant_component(self, tmp_path):
        p = tmp_path / "syn.out"
        _write_multicomp_out(p)
        best_old, dt_old = _legacy_load_dominant(p)

        traces, dt_new = read_rx_traces(p)
        best_new = max(("Ex", "Ey", "Ez"),
                       key=lambda c: np.abs(traces[c].astype(float)).max())
        assert best_new == best_old
        assert dt_new == float(dt_old)
        # all six components present and 1-D
        assert set(traces) == set(COMPONENTS)
        assert all(v.ndim == 1 for v in traces.values())


class TestWriteRxOutRoundTrip:
    def test_write_then_read_back(self, tmp_path):
        n = 128
        rng = np.random.default_rng(1)
        traces = {c: rng.standard_normal(n).astype(np.float32) for c in COMPONENTS}
        p = tmp_path / "w.out"
        write_rx_out(p, traces, dt=2.5e-11, position=(0.3, 0.4, 0.0),
                     title="T", gprmax="g")

        d = read_ascan(p)
        assert d["iterations"] == n
        assert d["dt"] == pytest.approx(2.5e-11)
        assert list(d["rx_pos"]) == [0.3, 0.4, 0.0]
        np.testing.assert_array_equal(d["signal"], traces["Ez"])

        back, dt = read_rx_traces(p)
        assert set(back) == set(COMPONENTS)
        np.testing.assert_array_equal(back["Hx"], traces["Hx"])

    def test_empty_traces_rejected(self, tmp_path):
        with pytest.raises(ValueError):
            write_rx_out(tmp_path / "e.out", {}, dt=1e-11)


# ── Real-fixture byte-identity (skipped when fixtures absent) ──────────────────

@pytest.mark.skipif(not REAL_OUT, reason="no .out fixtures in tests/test_files/")
class TestRealFixtureByteIdentity:
    def test_read_ascan_identical_to_legacy(self):
        p = REAL_OUT[0]
        ez_old, dt_old = _legacy_load_ez(p)
        d = read_ascan(p)
        np.testing.assert_array_equal(d["signal"].astype(float), ez_old)
        assert float(d["dt"]) == float(dt_old)

    def test_read_rx_traces_identical_to_legacy(self):
        p = REAL_OUT[0]
        best_old, dt_old = _legacy_load_dominant(p)
        traces, dt_new = read_rx_traces(p)
        best_new = max(("Ex", "Ey", "Ez"),
                       key=lambda c: np.abs(traces[c].astype(float)).max())
        assert best_new == best_old
        assert dt_new == float(dt_old)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

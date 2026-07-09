"""Tier 2: read_gprmax_hdf5 must raise on a missing dt attr, never silently
default (the same historic bug class as T1 — a silently-wrong dt mis-scales
every downstream frequency feature by ~3.2x)."""
from pathlib import Path

import h5py
import numpy as np
import pytest

from src.data_loader import read_gprmax_hdf5, write_rx_out

_GOOD = Path(__file__).parent / "_tmp_data_loader_good.out"
_BAD = Path(__file__).parent / "_tmp_data_loader_no_dt.out"


def teardown_module(_module):
    _GOOD.unlink(missing_ok=True)
    _BAD.unlink(missing_ok=True)


def test_read_gprmax_hdf5_raises_without_dt_attr():
    with h5py.File(_BAD, "w") as f:
        f.attrs["Iterations"] = 10
        rx = f.create_group("rxs/rx1")
        rx.create_dataset("Ez", data=np.zeros(10))
    with pytest.raises(ValueError, match="no 'dt' attribute"):
        read_gprmax_hdf5(str(_BAD), fields=["Ez"])


def test_read_gprmax_hdf5_reads_real_dt_when_present():
    dt = 0.0311e-9
    write_rx_out(str(_GOOD), {"Ez": np.arange(10, dtype=float)}, dt=dt)
    df = read_gprmax_hdf5(str(_GOOD), fields=["Ez"])
    assert not df.empty
    got_dt = float(df["Time"].iloc[1] - df["Time"].iloc[0])
    assert got_dt == pytest.approx(dt, rel=1e-9)

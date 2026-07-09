"""T7: DZT acquisition-gain read + reversal.

remove_gain must invert a known dB gain curve to <0.1%; read_gain_curve must
decode the GSSI range-gain block or return None cleanly (the Puerto-Limache EFE
files declare a non-decodable block -> None, gain state unknown).
"""
from pathlib import Path

import numpy as np
import pytest

from src.signal_processing import remove_gain, preprocess_physical
from src.dzt_io import read_gain_curve

DT = 0.0978e-9


def _sig(n=510, seed=0):
    return np.random.default_rng(seed).standard_normal(n) + 0.1


def _apply_db_curve(sig, gain_db):
    n = len(sig)
    gfull = np.interp(np.linspace(0, 1, n),
                      np.linspace(0, 1, gain_db.size), gain_db)
    return sig * 10.0 ** (gfull / 20.0)


def test_remove_gain_roundtrip_under_0p1pct():
    sig = _sig()
    gain_db = np.array([0.0, 10.0, 20.0, 30.0, 40.0, 45.0])
    rec = remove_gain(_apply_db_curve(sig, gain_db), gain_db, DT)
    err = np.max(np.abs(rec - sig)) / np.max(np.abs(sig))
    assert err < 1e-3, err


def test_remove_gain_constant():
    sig = _sig()
    rec = remove_gain(sig * 10.0 ** (20.0 / 20.0), np.array([20.0]), DT)
    assert np.allclose(rec, sig, rtol=1e-9)


def test_remove_gain_empty_is_noop():
    sig = _sig()
    assert np.allclose(remove_gain(sig, np.array([]), DT), sig)


def test_preprocess_physical_applies_gain_curve():
    sig = _sig()
    gain_db = np.linspace(0.0, 40.0, 8)
    gained = _apply_db_curve(sig, gain_db)
    p_with, _, _ = preprocess_physical(gained, DT, gain_curve_db=gain_db,
                                       use_dewow=False)
    p_manual, _, _ = preprocess_physical(remove_gain(gained, gain_db, DT), DT,
                                         use_dewow=False)
    assert np.allclose(p_with, p_manual, rtol=1e-9)


def test_preprocess_physical_flat_gain_is_noop():
    sig = _sig()
    a, _, _ = preprocess_physical(sig, DT, gain_curve_db=np.array([15.0, 15.0, 15.0]),
                                  use_dewow=False)
    b, _, _ = preprocess_physical(sig, DT, use_dewow=False)
    assert np.allclose(a, b)


_DZT = Path(r"D:/Codigo/Data/"
            r"PUERTO-LIMACHE_20230726_EFE_V1_PKC000_588_PKF011_020_CENTRO_BRUTO.DZT")


@pytest.mark.skipif(not _DZT.exists(), reason="Puerto-Limache DZT not available")
def test_read_gain_curve_puerto_limache_is_none():
    # rh_nrgain=5 (non-float-aligned) -> gain not decodable -> None (absent).
    assert read_gain_curve(_DZT) is None

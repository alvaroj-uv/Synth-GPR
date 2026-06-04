#!/usr/bin/env python3
"""
Unit tests for the shared A-scan helpers used by the visualizers:
  - src.data_loader.read_ascan
  - src.signal_processing.compute_padded_spectrum

These replace FFT/HDF5-reading logic that was previously duplicated across
visualize_ascan.py and unified_visualizer.py.
"""

import sys
from pathlib import Path

import h5py
import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data_loader import read_ascan
from src.signal_processing import compute_padded_spectrum


DT = 1e-11          # 10 ps step
N = 1024
F0 = 4e8            # 400 MHz tone


def _write_out(path, signal, position=(0.1, 0.2, 0.0)):
    """Write a minimal gprMax-style HDF5 .out file."""
    with h5py.File(path, "w") as f:
        f.attrs["dt"] = DT
        f.attrs["Iterations"] = signal.shape[0]
        rx = f.create_group("rxs/rx1")
        rx.create_dataset("Ez", data=signal)
        rx.attrs["Position"] = list(position)


@pytest.fixture
def tone():
    t = np.arange(N) * DT
    return np.sin(2 * np.pi * F0 * t)


class TestReadAscan:
    def test_reads_1d_signal_and_metadata(self, tmp_path, tone):
        out = tmp_path / "ascan.out"
        _write_out(out, tone)

        data = read_ascan(out, component="Ez")
        assert data["signal"].shape == (N,)
        assert data["dt"] == pytest.approx(DT)
        assert data["iterations"] == N
        assert data["component"] == "Ez"
        assert data["ascan_idx"] is None
        assert data["t_ns"][1] == pytest.approx(DT * 1e9)
        assert list(data["rx_pos"]) == [0.1, 0.2, 0.0]

    def test_missing_component_falls_back(self, tmp_path, tone):
        out = tmp_path / "ascan.out"
        _write_out(out, tone)
        data = read_ascan(out, component="Hx")  # not present -> falls back to Ez
        assert data["component"] == "Ez"

    def test_bscan_picks_middle_trace(self, tmp_path):
        out = tmp_path / "bscan.out"
        bscan = np.tile(np.arange(N).reshape(-1, 1), (1, 5)).astype(float)
        bscan *= np.arange(1, 6)  # distinct columns; middle (idx 2) == base * 3
        _write_out(out, bscan)

        data = read_ascan(out, component="Ez")
        assert data["ascan_idx"] == 2
        assert data["signal"].shape == (N,)
        np.testing.assert_allclose(data["signal"], np.arange(N) * 3)


class TestPaddedSpectrum:
    def test_peak_at_tone_frequency(self, tone):
        freqs, spectrum, peak = compute_padded_spectrum(tone, DT)
        # Peak should land within one (coarse) bin of the input tone.
        assert peak == pytest.approx(F0, abs=2e7)
        assert spectrum.shape == freqs.shape

    def test_zero_padding_increases_resolution(self, tone):
        freqs, spectrum, _ = compute_padded_spectrum(tone, DT, pad_factor=2)
        # Padded length is a power of two >= 2**(ceil(log2 N)+2) -> finer grid.
        assert len(freqs) > N // 2
        assert np.all(spectrum >= 0)

    def test_freqs_in_hz_not_ghz(self, tone):
        freqs, _, peak = compute_padded_spectrum(tone, DT)
        assert freqs[-1] > 1e9   # Nyquist for 10 ps step is 50 GHz
        assert peak > 1e8


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

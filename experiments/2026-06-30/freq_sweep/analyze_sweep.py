#!/usr/bin/env python3
"""Peak-resolution analysis for the 100-2000 MHz frequency sweep.

For each .out, gate out the direct wave/surface pulse (t < 5 ns) and look for
local maxima in the Hilbert envelope within the window where the
ballast/formation (~6.3 ns RTT) and formation/subgrade (~8.4 ns RTT)
reflections are expected (see experiments/2026-06-30/README.md Run 3 for the
RTT derivation). Reports how many distinct peaks are resolved per frequency,
and saves a stacked-envelope comparison plot.
"""
from pathlib import Path

import h5py
import numpy as np
from scipy.signal import hilbert, find_peaks
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
GATE_START_NS = 5.0   # exclude the direct/surface pulse
GATE_END_NS = 15.0    # past this, only PML/edge noise expected


def load_trace(out_path: Path):
    with h5py.File(out_path, "r") as f:
        sig = f["rxs/rx1/Ez"][()]
        dt = f.attrs["dt"] * 1e9  # ns
    t = np.arange(len(sig)) * dt
    return t, sig


def _annotate(ax):
    ax.axvline(GATE_START_NS, color="gray", ls="--", lw=0.7)
    ax.axvline(6.3, color="green", ls=":", lw=0.7, label="expected ballast/formation RTT")
    ax.axvline(8.4, color="red", ls=":", lw=0.7, label="expected formation/subgrade RTT")
    ax.set_xlim(0, GATE_END_NS + 5)
    ax.set_xlabel("Time (ns)")
    ax.legend(loc="upper right", fontsize=8)


def main():
    freqs_mhz = list(range(100, 2001, 100))
    fig_env, ax_env = plt.subplots(figsize=(9, 12))
    fig_raw, ax_raw = plt.subplots(figsize=(9, 12))
    offset = 0.0
    rows = []

    for fm in freqs_mhz:
        out_path = HERE / f"three_layer_{fm:04d}mhz.out"
        if not out_path.exists():
            continue
        t, sig = load_trace(out_path)
        env = np.abs(hilbert(sig))
        env_n = env / env.max()
        sig_n = sig / np.abs(sig).max()  # raw oscillating waveform, no Hilbert

        # Locally renormalize WITHIN the gated coda window: the
        # formation/subgrade reflection (R~0.056) is ~4x weaker in amplitude
        # than the ballast/formation reflection (R~0.225) and gets lost under
        # a global-max threshold dominated by the huge direct-wave pulse.
        mask = (t >= GATE_START_NS) & (t <= GATE_END_NS)
        tg, eg = t[mask], env[mask]
        eg_local = eg / eg.max()
        dt_ns = t[1] - t[0]
        min_dist = max(1, int(round(0.5 / dt_ns)))  # peaks must be >=0.5 ns apart
        peaks, props = find_peaks(eg_local, height=0.15, prominence=0.08, distance=min_dist)
        n_peaks = len(peaks)
        peak_times = tg[peaks].tolist()
        rows.append((fm, n_peaks, peak_times))

        ax_env.plot(t, env_n + offset, lw=0.8)
        ax_env.text(GATE_END_NS + 0.3, offset + 0.05, f"{fm} MHz (n={n_peaks})", fontsize=7, va="bottom")

        ax_raw.plot(t, sig_n * 0.5 + offset, lw=0.6)
        ax_raw.text(GATE_END_NS + 0.3, offset + 0.05, f"{fm} MHz", fontsize=7, va="bottom")

        offset += 1.1

    _annotate(ax_env)
    ax_env.set_ylabel("Normalized envelope (stacked, offset per frequency)")
    ax_env.set_title("Coda envelope vs frequency: interface-reflection resolution")
    fig_env.tight_layout()
    out_png = HERE / "freq_sweep_envelope_comparison.png"
    fig_env.savefig(out_png, dpi=150)
    print(f"Saved {out_png}")

    _annotate(ax_raw)
    ax_raw.set_ylabel("Normalized raw Ez signal (stacked, offset per frequency)")
    ax_raw.set_title("Coda RAW WAVEFORM vs frequency (no Hilbert envelope)")
    fig_raw.tight_layout()
    out_png_raw = HERE / "freq_sweep_raw_comparison.png"
    fig_raw.savefig(out_png_raw, dpi=150)
    print(f"Saved {out_png_raw}")

    print("\nfreq_mhz  n_peaks  peak_times_ns")
    for fm, n_peaks, peak_times in rows:
        pt = ", ".join(f"{p:.2f}" for p in peak_times)
        print(f"{fm:8d}  {n_peaks:7d}  [{pt}]")


if __name__ == "__main__":
    main()

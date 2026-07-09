#!/usr/bin/env python3
"""Crop each frequency-sweep trace to the segment vivanco_preprocess() actually
uses for analysis: [time_zero_idx, time_zero_idx + window_ns] of the original
.out trace (default window_ns=7.0, the production value).

For each three_layer_NNNNmhz.out, saves a CSV with the cropped/processed
trace (post dewow/bandpass/BGR) and its Hilbert envelope, on the vivanco
local time axis (t=0 at time_zero_idx), plus a stacked comparison plot.
"""
import csv
import sys
from pathlib import Path

import h5py
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT))

from src.signal_processing import vivanco_preprocess  # noqa: E402

WINDOW_NS = 7.0  # production default


def load_trace(out_path: Path):
    with h5py.File(out_path, "r") as f:
        sig = f["rxs/rx1/Ez"][()]
        dt = f.attrs["dt"]  # seconds
    return sig, dt


def main():
    freqs_mhz = list(range(100, 2001, 100))
    fig, ax = plt.subplots(figsize=(9, 12))
    offset = 0.0

    for fm in freqs_mhz:
        out_path = HERE / f"three_layer_{fm:04d}mhz.out"
        if not out_path.exists():
            continue
        sig, dt = load_trace(out_path)
        dt_ns = dt * 1e9

        result = vivanco_preprocess(sig, dt, window_ns=WINDOW_NS)
        processed = result["processed"]
        envelope = result["envelope"]
        t_local = np.arange(len(processed)) * dt_ns

        csv_path = HERE / f"three_layer_{fm:04d}mhz_vivanco_crop.csv"
        with open(csv_path, "w", newline="") as fcsv:
            w = csv.writer(fcsv)
            w.writerow(["t_ns_local", "processed", "envelope"])
            for tt, pp, ee in zip(t_local, processed, envelope):
                w.writerow([f"{tt:.4f}", f"{pp:.6e}", f"{ee:.6e}"])

        proc_n = processed / np.abs(processed).max() if np.abs(processed).max() > 0 else processed
        ax.plot(t_local, proc_n * 0.5 + offset, lw=0.7)
        ax.text(WINDOW_NS + 0.2, offset + 0.1, f"{fm} MHz", fontsize=7, va="bottom")
        offset += 1.1

        print(f"{fm:5d} MHz -> {csv_path.name}  ({len(processed)} samples, "
              f"time_zero={result['time_zero_idx']*dt_ns:.2f}ns)")

    ax.set_xlabel("Time (ns), vivanco local axis (window start = time_zero)")
    ax.set_ylabel("Cropped/processed Ez (stacked, offset per frequency)")
    ax.set_title(f"Vivanco-window-cropped trace vs frequency (window_ns={WINDOW_NS:g})")
    fig.tight_layout()
    out_png = HERE / "freq_sweep_vivanco_crop_comparison.png"
    fig.savefig(out_png, dpi=150)
    print(f"\nSaved {out_png}")


if __name__ == "__main__":
    main()

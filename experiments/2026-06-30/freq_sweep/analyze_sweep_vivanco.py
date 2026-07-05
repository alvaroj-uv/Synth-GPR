#!/usr/bin/env python3
"""Same frequency-sweep comparison as analyze_sweep.py, but running each trace
through the REAL Rojas-Vivanco (2025) preprocessing pipeline
(src/signal_processing.py vivanco_preprocess) instead of a plain Hilbert
envelope on the raw signal.

vivanco_preprocess() is the exact 7-step chain used to process real
Puerto-Limache / French GPR data: normalize to direct wave -> dewow ->
time-zero shift (direct peak - 3 ns) -> bandpass 150-800 MHz -> cut to a 7 ns
window -> BGR -> Hilbert envelope (normalized to max). All defaults are tuned
to a real 420 MHz GSSI antenna and are deliberately left UNSCALED here (not
adapted per simulated frequency) -- the point of this run is to see what the
production pipeline, as-is, does when fed traces from other antenna
frequencies.
"""
import argparse
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

RTT_BALLAST_FORMATION_NS = 6.3
RTT_FORMATION_SUBGRADE_NS = 8.4


def load_trace(out_path: Path):
    with h5py.File(out_path, "r") as f:
        sig = f["rxs/rx1/Ez"][()]
        dt = f.attrs["dt"]  # seconds
    return sig, dt


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--window-ns", type=float, default=7.0,
                         help="vivanco_preprocess window_ns (default 7.0, the paper value)")
    args = parser.parse_args()
    window_arg = args.window_ns

    freqs_mhz = list(range(100, 2001, 100))
    fig, ax = plt.subplots(figsize=(9, 12))
    offset = 0.0
    rows = []

    for fm in freqs_mhz:
        out_path = HERE / f"three_layer_{fm:04d}mhz.out"
        if not out_path.exists():
            continue
        sig, dt = load_trace(out_path)
        dt_ns = dt * 1e9

        result = vivanco_preprocess(sig, dt, window_ns=window_arg)
        env = result["envelope"]
        t_local = np.arange(len(env)) * dt_ns  # ns, relative to vivanco's time-zero

        # Convert the original-trace RTT predictions into vivanco's shifted axis
        time_zero_ns = result["time_zero_idx"] * dt_ns
        rtt1_local = RTT_BALLAST_FORMATION_NS - time_zero_ns
        rtt2_local = RTT_FORMATION_SUBGRADE_NS - time_zero_ns
        window_ns = t_local[-1]
        rtt2_visible = 0 <= rtt2_local <= window_ns
        rows.append((fm, time_zero_ns, window_ns, rtt1_local, rtt2_local, rtt2_visible))

        ax.plot(t_local, env + offset, lw=0.8)
        if 0 <= rtt1_local <= window_ns:
            ax.axvline(rtt1_local, color="green", ls=":", lw=0.5, ymin=0, ymax=1)
        if 0 <= rtt2_local <= window_ns:
            ax.axvline(rtt2_local, color="red", ls=":", lw=0.5, ymin=0, ymax=1)
        ax.text(window_ns + 0.2, offset + 0.1, f"{fm} MHz", fontsize=7, va="bottom")
        offset += 1.1

    ax.set_xlabel(f"Time (ns), vivanco time-zero axis (direct peak - 3 ns)")
    ax.set_ylabel("Vivanco-pipeline Hilbert envelope (stacked, offset per frequency)")
    ax.set_title(f"Vivanco (2025) pipeline envelope vs frequency\n"
                  f"(fixed 150-800MHz bandpass + {window_arg:g}ns window, NOT scaled per frequency)\n"
                  f"green=ballast/formation RTT  red=formation/subgrade RTT")
    fig.tight_layout()
    tag = f"{window_arg:g}ns".replace(".", "p")
    out_png = HERE / f"freq_sweep_vivanco_envelope_comparison_{tag}.png"
    fig.savefig(out_png, dpi=150)
    print(f"Saved {out_png}")

    print(f"\n{'freq_mhz':>8s} {'time_zero_ns':>13s} {'window_ns':>10s} "
          f"{'rtt1_local':>11s} {'rtt2_local':>11s}  rtt2_in_window")
    for fm, tz, win, r1, r2, vis in rows:
        print(f"{fm:8d} {tz:13.2f} {win:10.2f} {r1:11.2f} {r2:11.2f}  {vis}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Compare the actual A-scan waveforms between the three rock_shape variants
(polygon/circle/square) -- same rock positions/sizes/eps, shape only differs.
Complements rock_shape_comparison.png (geometry renders) with the resulting
signals: raw waveform + Hilbert envelope, full trace and a coda-only zoom.
"""
from pathlib import Path

import h5py
import numpy as np
from scipy.signal import hilbert
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent

CONFIGS = [
    ("Polygon (default)", "three_layer_420mhz_eps3.out", "tab:blue"),
    ("Circle", "three_layer_420mhz_circle_rocks.out", "tab:orange"),
    ("Square", "three_layer_420mhz_square_rocks.out", "tab:green"),
]


def load_trace(out_path: Path):
    with h5py.File(out_path, "r") as f:
        sig = f["rxs/rx1/Ez"][()]
        dt = f.attrs["dt"] * 1e9
    t = np.arange(len(sig)) * dt
    return t, sig


def main():
    fig, axes = plt.subplots(2, 2, figsize=(13, 9))
    (ax_raw, ax_raw_coda), (ax_env, ax_env_coda) = axes

    for label, fname, color in CONFIGS:
        t, sig = load_trace(HERE / fname)
        sig_n = sig / np.abs(sig).max()
        env = np.abs(hilbert(sig))
        env_n = env / env.max()

        ax_raw.plot(t, sig_n, color=color, lw=1.0, label=label)
        ax_env.plot(t, env_n, color=color, lw=1.2, label=label)

        mask = t >= 5.0
        t_coda = t[mask]
        sig_coda = sig[mask]
        env_coda = env[mask]
        sig_coda_n = sig_coda / np.abs(sig_coda).max()
        env_coda_n = env_coda / env_coda.max()
        ax_raw_coda.plot(t_coda, sig_coda_n, color=color, lw=1.2, label=label)
        ax_env_coda.plot(t_coda, env_coda_n, color=color, lw=1.4, label=label)

    for ax in (ax_raw, ax_env):
        ax.axvline(5.0, color="gray", ls="--", lw=0.7)
        ax.set_xlim(0, 12)
        ax.legend(fontsize=8)
        ax.grid(True, alpha=0.25)

    for ax in (ax_raw_coda, ax_env_coda):
        ax.set_xlim(5, 12)
        ax.legend(fontsize=8)
        ax.grid(True, alpha=0.25)

    ax_raw.set_title("Raw waveform, full trace (normalized to own peak)")
    ax_raw.set_ylabel("Normalized Ez")
    ax_raw_coda.set_title("Raw waveform, coda only (5-12ns, local scale)")
    ax_env.set_title("Hilbert envelope, full trace")
    ax_env.set_ylabel("Normalized envelope")
    ax_env.set_xlabel("Time (ns)")
    ax_env_coda.set_title("Hilbert envelope, coda only (5-12ns, local scale)")
    ax_env_coda.set_xlabel("Time (ns)")
    ax_raw_coda.set_xlabel("Time (ns)")

    fig.suptitle("Rock shape comparison: A-scan waveforms\n(rock=6.1, matrix=3, 420 MHz — same rock positions/sizes, shape only differs)",
                 fontsize=12)
    fig.tight_layout(rect=[0, 0, 1, 0.94])
    out_png = HERE / "rock_shape_waveform_comparison.png"
    fig.savefig(out_png, dpi=150)
    print(f"Saved {out_png}")

    # Quantify: pairwise correlation, coda only
    print("\nPairwise coda correlation (raw signal, 5-12ns):")
    traces = {}
    for label, fname, _ in CONFIGS:
        t, sig = load_trace(HERE / fname)
        mask = t >= 5.0
        traces[label] = sig[mask]
    labels = list(traces.keys())
    for i in range(len(labels)):
        for j in range(i + 1, len(labels)):
            r = np.corrcoef(traces[labels[i]], traces[labels[j]])[0, 1]
            print(f"  {labels[i]:10s} vs {labels[j]:10s}: r = {r:.4f}")


if __name__ == "__main__":
    main()

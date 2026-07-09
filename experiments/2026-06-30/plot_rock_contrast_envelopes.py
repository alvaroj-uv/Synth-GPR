#!/usr/bin/env python3
"""Visualize the rock/matrix contrast comparison as Hilbert envelopes:
packed-rock trace (solid) vs its flat CRIM-equivalent counterpart (dashed),
for the three configs tested in README.md ("rock-contribution check" /
"Fix: raise rock_eps to 6.1" / "Follow-up: rock_eps=8").

The gap between solid and dashed lines in the coda (>5ns) IS the rocks'
distinctive contribution -- a big gap = rocks dominate the coda shape
(low correlation), a small gap = the flat layer already explains it (rocks
contribute little). This makes the coda-correlation numbers already in the
README directly visible.
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
    ("rock=4, matrix=1 (OLD baseline)",
     "three_layer_500mhz_matrix1_rocks_check.out",
     "three_layer_500mhz_matrix1_flat_check.out",
     "R=0.333, coda corr=0.097"),
    ("rock=6.1, matrix=3 (adopted fix, Brancadoro)",
     "three_layer_500mhz_rock6p1_check.out",
     "three_layer_500mhz_rock6p1_flat_check.out",
     "R=0.176, coda corr=0.208"),
    ("rock=8, matrix=3 (alternative, Harajchi)",
     "three_layer_500mhz_rock8_check.out",
     "three_layer_500mhz_rock8_flat_check.out",
     "R=0.240, coda corr=0.053"),
]


def load_env(path: Path):
    with h5py.File(path, "r") as f:
        sig = f["rxs/rx1/Ez"][()]
        dt = f.attrs["dt"] * 1e9
    t = np.arange(len(sig)) * dt
    env = np.abs(hilbert(sig))
    return t, env


def main():
    fig, axes = plt.subplots(len(CONFIGS), 2, figsize=(13, 10))

    for row, (label, rocks_file, flat_file, stats) in zip(axes, CONFIGS):
        ax_full, ax_coda = row
        t_r, env_r = load_env(HERE / rocks_file)
        t_f, env_f = load_env(HERE / flat_file)
        peak = max(env_r.max(), env_f.max())

        # Left: full trace, normalized to the direct-wave peak (shows alignment)
        ax_full.plot(t_r, env_r / peak, color="tab:blue", lw=1.3, label="packed rocks")
        ax_full.plot(t_f, env_f / peak, color="tab:orange", lw=1.3, ls="--", label="flat CRIM-equivalent")
        ax_full.axvline(5.0, color="gray", ls=":", lw=0.7)
        ax_full.set_ylabel("Normalized\nenvelope (full trace)")
        ax_full.set_title(f"{label}\n({stats})", fontsize=9)
        ax_full.legend(loc="upper right", fontsize=7)

        # Right: CODA ONLY (t>=5ns), each own local scale so the shape actually shows
        mask_r = t_r >= 5.0
        mask_f = t_f >= 5.0
        coda_peak = max(env_r[mask_r].max(), env_f[mask_f].max())
        ax_coda.plot(t_r[mask_r], env_r[mask_r] / coda_peak, color="tab:blue", lw=1.5, label="packed rocks")
        ax_coda.plot(t_f[mask_f], env_f[mask_f] / coda_peak, color="tab:orange", lw=1.5, ls="--",
                     label="flat CRIM-equivalent")
        ax_coda.fill_between(t_r[mask_r], env_r[mask_r] / coda_peak,
                              np.interp(t_r[mask_r], t_f[mask_f], env_f[mask_f] / coda_peak),
                              color="tab:blue", alpha=0.2)
        ax_coda.set_title("Coda only (5-12ns), local scale", fontsize=9)
        ax_coda.set_ylabel("Normalized\nenvelope (coda-local)")

    for ax in axes[-1]:
        ax.set_xlabel("Time (ns)")

    fig.suptitle("Rock/matrix contrast: packed-rock vs flat-equivalent envelope\n"
                 "Left = full trace (direct pulse dominates); Right = coda zoomed to its own scale "
                 "(shaded gap = what the discrete rocks actually add)",
                 fontsize=11)
    fig.tight_layout(rect=[0, 0, 1, 0.92])
    out_png = HERE / "rock_contrast_envelope_comparison.png"
    fig.savefig(out_png, dpi=150)
    print(f"Saved {out_png}")


if __name__ == "__main__":
    main()

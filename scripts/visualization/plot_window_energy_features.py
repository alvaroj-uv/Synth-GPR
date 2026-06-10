#!/usr/bin/env python3
"""
Visualize the windowed-indicator and energy-integration-curve features
(src.feature_extraction._extract_window_features / _extract_energy_curve_features).

It builds a controlled clean-vs-fouled A-scan pair that reproduces the physics the
ballast-fouling literature reports (Li et al. 2023, Remote Sens. 15, 3437):

  * fouled ballast → faster attenuation, so energy accumulates EARLIER in time, and
    denser scattering clutter inside the ballast/coda gate → larger gated Hilbert energy;
  * clean ballast → energy persists later, sparser coda.

The figure has three panels:
  (A) the two A-scans with the ballast/coda gate (SC.CODA_WINDOW_NS) shaded;
  (B) the normalized cumulative-energy curves with q50 markers and AUC labels;
  (C) grouped bars comparing selected new features (clean vs fouled),
      computed with the real feature functions.

Usage:
    python scripts/visualization/plot_window_energy_features.py
    python scripts/visualization/plot_window_energy_features.py --out some/dir/fig.png
"""
import argparse
import sys
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.constants import SC
from src.feature_extraction import (
    _extract_window_features,
    _extract_energy_curve_features,
)
from src.signal_processing import calculate_instantaneous_attributes

DT = 1e-11        # 10 ps
N = 4096          # ~40.96 ns
F0 = 1.5e9        # 1.5 GHz carrier


def _synth_ascan(decay_tau_ns: float, clutter_amp: float, seed: int,
                 deep_reflector_ns: float | None = None) -> np.ndarray:
    """A surface pulse + an exponentially-decaying coda with random scattering clutter.

    Faithful to Li et al. (2023): a fouled bed is modelled with dense scattering clutter
    in the ballast gate (denser/stronger Hilbert energy) and a fast decay (energy
    accumulates early). A clean bed has sparse clutter, a slow decay and an optional deep
    reflector so its energy persists later in time.
    """
    rng = np.random.default_rng(seed)
    t_ns = np.arange(N) * DT * SC.NS_PER_SEC

    # Surface reflection near 2 ns (same for both — the air/ballast interface).
    # Attenuated here to emulate partial direct-wave suppression; over the FULL raw trace
    # the direct wave dominates total energy, which is precisely why the gated/windowed
    # features (and direct-wave removal) are needed for fouling discrimination.
    surface = 0.3 * np.exp(-0.5 * ((t_ns - 2.0) / 0.5) ** 2) * np.sin(2 * np.pi * F0 * t_ns * 1e-9)

    # Coda: decays at decay_tau_ns; clutter only inside the ballast gate
    lo, hi = SC.CODA_WINDOW_NS
    coda_env = np.where(t_ns > 2.0, np.exp(-(t_ns - 2.0) / decay_tau_ns), 0.0)
    coda = 0.4 * coda_env * np.sin(2 * np.pi * F0 * t_ns * 1e-9)

    # Dense scattering clutter inside the ballast gate (fouling fines → more scattering).
    # Use a slow envelope inside the gate so the clutter does not vanish with fast decay.
    gate = (t_ns >= lo) & (t_ns <= hi)
    gate_env = np.exp(-(t_ns - lo) / max(decay_tau_ns * 2.0, 1.0))
    clutter = np.zeros_like(t_ns)
    clutter[gate] = clutter_amp * gate_env[gate] * rng.standard_normal(np.count_nonzero(gate))

    sig = surface + coda + clutter

    # Optional deep reflector (clean bed: energy persists later)
    if deep_reflector_ns is not None:
        sig = sig + 0.6 * np.exp(-0.5 * ((t_ns - deep_reflector_ns) / 0.7) ** 2) \
                  * np.sin(2 * np.pi * F0 * t_ns * 1e-9)
    return sig


def _envelope(sig: np.ndarray) -> np.ndarray:
    return calculate_instantaneous_attributes(sig, DT, use_mirroring=True)["envelope"]


def build_figure(out_path: Path) -> Path:
    t_ns = np.arange(N) * DT * SC.NS_PER_SEC
    lo, hi = SC.CODA_WINDOW_NS

    # Clean: slow decay, sparse clutter, a deep reflector so energy persists late.
    # Fouled: faster decay but dense ballast-gate scattering (denser Hilbert energy).
    clean = _synth_ascan(decay_tau_ns=10.0, clutter_amp=0.06, seed=1, deep_reflector_ns=20.0)
    fouled = _synth_ascan(decay_tau_ns=6.0, clutter_amp=0.55, seed=2)

    # Real feature values
    wc = _extract_window_features(clean, _envelope(clean) * np.exp(0j), DT)
    wf = _extract_window_features(fouled, _envelope(fouled) * np.exp(0j), DT)
    ec = _extract_energy_curve_features(clean)
    ef = _extract_energy_curve_features(fouled)

    cum_c = np.cumsum(clean ** 2); cum_c /= cum_c[-1]
    cum_f = np.cumsum(fouled ** 2); cum_f /= cum_f[-1]
    pos = np.arange(N) / (N - 1)

    fig, (axA, axB, axC) = plt.subplots(1, 3, figsize=(16, 4.6))
    fig.suptitle("Windowed + energy-integration-curve features  (clean vs fouled demo)",
                 fontsize=13, fontweight="bold")

    # ---- Panel A: A-scans with gate shaded ----
    axA.axvspan(lo, hi, color="gold", alpha=0.18, label=f"ballast gate {lo:.0f}-{hi:.0f} ns")
    axA.plot(t_ns, clean, color="#1f77b4", lw=0.8, label="clean")
    axA.plot(t_ns, fouled, color="#d62728", lw=0.8, alpha=0.85, label="fouled")
    axA.set_xlim(0, 25)
    axA.set_xlabel("time (ns)"); axA.set_ylabel("Ez (a.u.)")
    axA.set_title("(A) A-scans + ballast/coda gate")
    axA.legend(fontsize=8, loc="upper right")

    # ---- Panel B: normalized cumulative energy curves ----
    axB.plot(pos, cum_c, color="#1f77b4", lw=1.6, label="clean")
    axB.plot(pos, cum_f, color="#d62728", lw=1.6, label="fouled")
    for f, col, lab in [(ec, "#1f77b4", "clean"), (ef, "#d62728", "fouled")]:
        axB.axvline(f["energy_time_q50"], color=col, ls="--", lw=1.0)
    axB.axhline(0.5, color="grey", ls=":", lw=0.8)
    axB.set_xlabel("normalized time position [0,1]")
    axB.set_ylabel("cumulative energy (normalized)")
    axB.set_title("(B) energy-integration curve")
    axB.text(0.02, 0.92, f"AUC  clean={ec['energy_curve_auc']:.3f}\nAUC  fouled={ef['energy_curve_auc']:.3f}",
             transform=axB.transAxes, fontsize=8,
             bbox=dict(boxstyle="round", fc="white", ec="grey", alpha=0.8))
    axB.legend(fontsize=8, loc="lower right")

    # ---- Panel C: grouped bars of selected features ----
    feats = ["win_area_hilbert", "win_hilbert_mean", "win_energy_fraction",
             "energy_time_q50", "energy_curve_auc", "early_late_energy_ratio"]
    cvals, fvals = [], []
    for k in feats:
        src_c = wc if k.startswith("win_") else ec
        src_f = wf if k.startswith("win_") else ef
        cvals.append(src_c[k]); fvals.append(src_f[k])
    # Normalize each feature to its max across the pair so disparate scales share an axis
    cn, fn = [], []
    for c, f in zip(cvals, fvals):
        m = max(abs(c), abs(f), 1e-12)
        cn.append(c / m); fn.append(f / m)
    x = np.arange(len(feats)); w = 0.38
    axC.bar(x - w / 2, cn, w, color="#1f77b4", label="clean")
    axC.bar(x + w / 2, fn, w, color="#d62728", label="fouled")
    axC.set_xticks(x)
    axC.set_xticklabels(feats, rotation=35, ha="right", fontsize=7)
    axC.set_ylabel("value (per-feature max-normalized)")
    axC.set_title("(C) selected new features")
    axC.legend(fontsize=8)

    fig.tight_layout(rect=[0, 0, 1, 0.95])
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=140)
    plt.close(fig)

    # Console summary so the script is useful headless
    print(f"Saved figure → {out_path}")
    print("\nClean vs fouled (key new features):")
    for k in feats:
        src_c = wc if k.startswith("win_") else ec
        src_f = wf if k.startswith("win_") else ef
        print(f"  {k:24s}  clean={src_c[k]:.4f}   fouled={src_f[k]:.4f}")
    return out_path


def main():
    ap = argparse.ArgumentParser(description="Visualize windowed + energy-curve features")
    ap.add_argument("--out", type=Path,
                    default=Path("output/figures/window_energy_features_demo.png"),
                    help="output PNG path")
    args = ap.parse_args()
    build_figure(args.out)


if __name__ == "__main__":
    main()

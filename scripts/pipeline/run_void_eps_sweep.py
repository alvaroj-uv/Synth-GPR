"""
Run the 3D GSSI void-eps sweep: 6 matched-pair scenes, same rock geometry (seed=42),
void-fill eps stepping from 4.5 (eps_eff≈5.1, real clean ballast) to 9.5 (fouled).

Each scene: ~2 min GPU on RTX 2060.  Total: ~12 min.

Usage:
    PYTHONIOENCODING=utf-8 conda run -n gprMax python scripts/pipeline/run_void_eps_sweep.py
    python scripts/pipeline/run_void_eps_sweep.py --plot-only   (skip simulation, replot)
"""
import argparse
import subprocess
import sys
from pathlib import Path

import h5py
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from scripts.pipeline.generate_3d_scene import generate, SWEEP_STEPS, eps_eff
from src.config import resolve_gprmax_python

# (eps_void, sigma_void) pairs — defined in generate_3d_scene.py
SWEEP = SWEEP_STEPS   # [(4.5,0.001), (5.5,0.011), ..., (9.5,0.050)]

CODA_START_NS = 10.0
CODA_END_NS   = 28.0


def out_name(eps_v: float) -> str:
    return f"gssi_400_3d_rocks_veps{eps_v:.1f}"


def run_one(eps_v: float, sigma_v: float, skip_if_exists: bool = True) -> Path:
    name    = out_name(eps_v)
    in_path = ROOT / f"{name}.in"
    out_path = ROOT / f"{name}.out"

    if skip_if_exists and out_path.exists():
        print(f"[skip] {out_path.name} already exists")
        return out_path

    # Generate .in file
    generate(in_path, with_rocks=True, void_eps=eps_v, void_sigma=sigma_v)

    # Run gprMax on GPU
    print(f"[run ] {in_path.name} ...", flush=True)
    env_cmd = [
        resolve_gprmax_python(), "-m", "gprMax", str(in_path), "-gpu", "0",
    ]
    result = subprocess.run(
        env_cmd,
        cwd=str(ROOT),
        env={**__import__("os").environ, "PYTHONIOENCODING": "utf-8"},
        capture_output=False,
    )
    if result.returncode != 0:
        raise RuntimeError(f"gprMax failed for {in_path.name}")
    return out_path


def load_coda_rms(out_path: Path) -> tuple[float, float, np.ndarray, float]:
    with h5py.File(out_path, "r") as f:
        dt  = float(f.attrs["dt"])
        ey  = f["rxs"]["rx1"]["Ey"][:]
    t_ns = np.arange(len(ey)) * dt * 1e9
    mask = (t_ns >= CODA_START_NS) & (t_ns <= CODA_END_NS)
    rms  = float(np.sqrt(np.mean(ey[mask] ** 2)))
    peak = float(np.abs(ey).max())
    return rms, peak, ey, dt


def plot_sweep(results: list[dict], clean_out: Path) -> None:
    # Load homogeneous reference
    rms_homog, peak_homog, ey_homog, dt = load_coda_rms(clean_out)
    t_ns = np.arange(len(ey_homog)) * dt * 1e9

    eps_void_vals = [r["eps_void"] for r in results]
    eps_eff_vals  = [r["eps_eff"]  for r in results]
    coda_rms_vals = [r["coda_rms"] for r in results]

    fig = plt.figure(figsize=(14, 9))
    gs  = fig.add_gridspec(2, 2, hspace=0.38, wspace=0.30)

    # ── Top-left: all waveforms ──────────────────────────────────────────────
    ax1 = fig.add_subplot(gs[0, :])
    cmap = plt.cm.plasma(np.linspace(0.15, 0.85, len(results)))
    for r, col in zip(results, cmap):
        ax1.plot(t_ns, r["ey"], color=col, lw=0.9,
                 label=f'eps_void={r["eps_void"]:.1f}  eps_eff≈{r["eps_eff"]:.1f}')
    ax1.plot(t_ns, ey_homog, "b--", lw=1.2, label="Clean homog (eps=5.1, no rocks)")
    ax1.axvspan(CODA_START_NS, CODA_END_NS, alpha=0.07, color="green", label="Coda window")
    ax1.set_xlabel("Time (ns)")
    ax1.set_ylabel("Ey (V/m)")
    ax1.set_title("GSSI 400MHz 3D — Void-fill eps sweep (same 212 rocks, seed=42)")
    ax1.legend(fontsize=7.5, ncol=2)
    ax1.grid(True, alpha=0.3)
    ax1.set_xlim(0, 30)

    # ── Bottom-left: coda RMS vs eps_void ───────────────────────────────────
    ax2 = fig.add_subplot(gs[1, 0])
    ax2.plot(eps_void_vals, coda_rms_vals, "o-", color="darkorange", lw=1.5, ms=7)
    ax2.axhline(rms_homog, color="b", ls="--", lw=1, label=f"Clean homog ({rms_homog:.3f} V/m)")
    ax2.set_xlabel("Void-fill permittivity  eps_void")
    ax2.set_ylabel("Coda RMS (V/m)")
    ax2.set_title(f"Coda RMS vs void fill  ({CODA_START_NS:.0f}–{CODA_END_NS:.0f} ns)")
    ax2.legend(fontsize=8)
    ax2.grid(True, alpha=0.3)

    # ── Bottom-right: coda RMS vs eps_eff ───────────────────────────────────
    ax3 = fig.add_subplot(gs[1, 1])
    ax3.plot(eps_eff_vals, coda_rms_vals, "s-", color="crimson", lw=1.5, ms=7)
    ax3.axhline(rms_homog, color="b", ls="--", lw=1, label=f"Clean homog ({rms_homog:.3f} V/m)")
    ax3.axvline(5.1, color="b", ls=":", lw=0.8, alpha=0.6)
    for ev, rms in zip(eps_eff_vals, coda_rms_vals):
        ax3.annotate(f"{rms:.3f}", (ev, rms), textcoords="offset points",
                     xytext=(4, 4), fontsize=7.5)
    ax3.set_xlabel("Effective bulk permittivity  eps_eff (CRIM)")
    ax3.set_ylabel("Coda RMS (V/m)")
    ax3.set_title("Coda RMS vs eps_eff")
    ax3.legend(fontsize=8)
    ax3.grid(True, alpha=0.3)

    out_png = ROOT / "gssi_400_3d_void_eps_sweep.png"
    plt.savefig(out_png, dpi=150)
    print(f"[plot] {out_png}")

    # Print table
    print(f"\n{'eps_void':>10}  {'eps_eff':>8}  {'coda_RMS':>10}  {'peak_Ey':>10}")
    print(f"{'(homog)':>10}  {'5.10':>8}  {rms_homog:>10.4f}  {peak_homog:>10.3f}")
    for r in results:
        print(f"{r['eps_void']:>10.1f}  {r['eps_eff']:>8.2f}  "
              f"{r['coda_rms']:>10.4f}  {r['peak']:>10.3f}")


def plot_waveforms_grid() -> None:
    """Plot all raw Ey waveforms in a grid — no processing, shared y-axis."""
    files = [
        ("clean (homog)", ROOT / "gssi_400_3d_clean.out"),
        ("rocks veps=1.0 (air)", ROOT / "gssi_400_3d_rocks_veps1.0.out"),
    ] + [
        (f"rocks veps={ev:.1f}", ROOT / f"gssi_400_3d_rocks_veps{ev:.1f}.out")
        for ev, _ in SWEEP
    ]

    waves = []
    for label, path in files:
        if not path.exists():
            print(f"[skip] {path.name} not found")
            continue
        with h5py.File(path, "r") as f:
            dt  = float(f.attrs["dt"])
            ey  = f["rxs"]["rx1"]["Ey"][:]
        t_ns = np.arange(len(ey)) * dt * 1e9
        waves.append((label, t_ns, ey))

    n    = len(waves)
    ncol = 4
    nrow = (n + ncol - 1) // ncol
    fig, axes = plt.subplots(nrow, ncol, figsize=(ncol * 4, nrow * 3),
                             sharey=True, sharex=True)
    axes = axes.flatten()

    cmap = plt.cm.plasma(np.linspace(0.05, 0.95, n))
    for i, (label, t_ns, ey) in enumerate(waves):
        ax = axes[i]
        ax.plot(t_ns, ey, color=cmap[i], lw=0.8)
        ax.axhline(0, color="gray", lw=0.4, alpha=0.5)
        ax.set_title(label, fontsize=8)
        ax.grid(True, alpha=0.25)
        if i % ncol == 0:
            ax.set_ylabel("Ey (V/m)", fontsize=7)
        if i >= (nrow - 1) * ncol:
            ax.set_xlabel("Time (ns)", fontsize=7)

    for j in range(n, len(axes)):
        axes[j].set_visible(False)

    fig.suptitle("Raw Ey waveforms — GSSI 400 MHz 3D void-fill sweep", fontsize=11)
    plt.tight_layout()
    out_png = ROOT / "gssi_400_3d_raw_waveforms.png"
    plt.savefig(out_png, dpi=150)
    print(f"[plot] {out_png}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--plot-only", action="store_true",
                    help="Skip simulation, load existing .out files and replot")
    ap.add_argument("--waves", action="store_true",
                    help="Plot raw waveform grid (no processing) and exit")
    args = ap.parse_args()

    if args.waves:
        plot_waveforms_grid()
        return

    results = []
    for eps_v, sigma_v in SWEEP:
        out_path = run_one(eps_v, sigma_v, skip_if_exists=args.plot_only or True)
        rms, peak, ey, dt = load_coda_rms(out_path)
        results.append({
            "eps_void": eps_v,
            "eps_eff":  eps_eff(eps_v),
            "coda_rms": rms,
            "peak":     peak,
            "ey":       ey,
        })
        print(f"  eps_void={eps_v:.1f}  eps_eff≈{eps_eff(eps_v):.2f}  "
              f"coda_RMS={rms:.4f} V/m  peak={peak:.3f} V/m")

    clean_out = ROOT / "gssi_400_3d_clean.out"
    plot_sweep(results, clean_out)


if __name__ == "__main__":
    main()

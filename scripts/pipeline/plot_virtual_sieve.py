"""
Virtual sieve analysis + FI → coda RMS curve.

Produces two panels:
  1. Rock PSD (virtual sieve on the 212 granite spheres, EN 13450 sieves)
  2. Coda RMS vs FI (Selig) derived from the eps_void sweep + CRIM

Usage:
    python scripts/pipeline/plot_virtual_sieve.py
"""
import sys
from pathlib import Path

import h5py
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from src.virtual_sieve import (
    sieve_rocks, make_fi_coda_curve,
    EN13450_SIEVES, eps_void_to_fi, P4_FRAC,
)
from scripts.pipeline.generate_3d_scene import (
    inflation_spheres, SWEEP_STEPS,
)

CODA_START_NS = 10.0
CODA_END_NS   = 25.0
EPS_FINES     = 10.0   # fine particle eps (moist clay/silt)
PHI_ROCKS     = 0.39   # from inflation packing

# ── Load sweep results ────────────────────────────────────────────────────────
def load_coda_rms(path: Path) -> float:
    with h5py.File(path, "r") as f:
        dt = float(f.attrs["dt"])
        ey = f["rxs"]["rx1"]["Ey"][:]
    t_ns = np.arange(len(ey)) * dt * 1e9
    mask = (t_ns >= CODA_START_NS) & (t_ns <= CODA_END_NS)
    return float(np.sqrt(np.mean(ey[mask] ** 2)))


sweep_data = []
# include the veps1.0 run (truly dry/clean, PVC=0)
for eps_v, _ in [(1.0, 0.0)] + list(SWEEP_STEPS):
    name = f"gssi_400_3d_rocks_veps{eps_v:.1f}.out"
    path = ROOT / name
    if path.exists():
        rms = load_coda_rms(path)
        sweep_data.append({"eps_void": eps_v, "coda_rms": rms})
        print(f"  eps_void={eps_v:.1f}  coda_RMS={rms:.4f} V/m")

# ── Rock virtual sieve ────────────────────────────────────────────────────────
spheres = inflation_spheres()
sr = sieve_rocks(spheres, sieves_mm=EN13450_SIEVES)

print(f"\nRock PSD  (n={len(spheres)} spheres)")
print(f"  D10={sr.d10:.1f} mm  D50={sr.d50:.1f} mm  D60={sr.d60:.1f} mm  Cu={sr.cu:.2f}")
print(f"  EN 13450 grade: {sr.en13450_grade}")

# ── FI → coda RMS curve ───────────────────────────────────────────────────────
fi_pts, coda_pts = make_fi_coda_curve(sweep_data, eps_fines=EPS_FINES,
                                       phi_rocks=PHI_ROCKS)

# Smooth interpolation for the curve
if len(fi_pts) >= 2:
    fi_smooth  = np.linspace(fi_pts.min(), fi_pts.max(), 200)
    interp_fn  = interp1d(fi_pts, coda_pts, kind="cubic", fill_value="extrapolate")
    coda_smooth = interp_fn(fi_smooth)

print(f"\nFI → coda RMS mapping  (eps_fines={EPS_FINES}, P4_frac={P4_FRAC:.2f})")
print(f"{'FI':>6}  {'eps_void':>9}  {'PVC':>6}  {'coda_RMS':>10}")
for row in sweep_data:
    fi = float(eps_void_to_fi(row["eps_void"], eps_fines=EPS_FINES,
                               phi_rocks=PHI_ROCKS))
    pvc = (row["eps_void"] - 1.0) / (EPS_FINES - 1.0)
    print(f"{fi:6.1f}  {row['eps_void']:9.1f}  {pvc:6.3f}  {row['coda_rms']:10.4f}")

# ── Plot ──────────────────────────────────────────────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(13, 6))

# Left: Rock PSD
ax = axes[0]
d_plot = np.concatenate([[0], sr.sieves_mm])
p_plot = np.concatenate([[0], sr.pct_passing])
ax.semilogx(d_plot[1:], p_plot[1:], "bo-", ms=6, lw=1.5, label=f"n={len(spheres)} spheres")
ax.axvline(4,    color="r",  ls="--", lw=1, alpha=0.7, label="4 mm  (P4 sieve)")
ax.axvline(31.5, color="g",  ls="--", lw=1, alpha=0.7, label="31.5 mm")
ax.axvline(63,   color="purple", ls="--", lw=1, alpha=0.7, label="63 mm")
ax.axhline(50,   color="k",  ls=":",  lw=0.8, alpha=0.5)
ax.annotate(f"D50={sr.d50:.0f} mm", xy=(sr.d50, 50),
            xytext=(sr.d50*1.3, 45), fontsize=9,
            arrowprops=dict(arrowstyle="->", lw=0.8))
ax.set_xlabel("Sieve opening (mm)")
ax.set_ylabel("Cumulative passing (%)")
ax.set_title(f"Virtual sieve — ballast rocks\n"
             f"EN 13450 grade ≈ {sr.en13450_grade}   Cu={sr.cu:.2f}   D50={sr.d50:.0f} mm")
ax.set_xlim(1, 120)
ax.set_ylim(0, 105)
ax.legend(fontsize=8)
ax.grid(True, which="both", alpha=0.3)

# Right: coda RMS vs FI
ax2 = axes[1]
if len(fi_pts) >= 2:
    ax2.plot(fi_smooth, coda_smooth, "k-", lw=1.5, alpha=0.4, label="Interpolation")
ax2.scatter(fi_pts, coda_pts, c=fi_pts, cmap="plasma_r",
            s=80, zorder=5, edgecolors="k", lw=0.5)
for fi, rms, row in zip(fi_pts, coda_pts, sorted(sweep_data, key=lambda r: r["eps_void"])):
    ax2.annotate(f"eps_v={row['eps_void']:.1f}", (fi, rms),
                 textcoords="offset points", xytext=(5, 3), fontsize=7.5)

# FI class boundaries (0/10/20/30/40 bins)
for fi_lim in [10, 20, 30, 40]:
    ax2.axvline(fi_lim, color="gray", ls=":", lw=0.8, alpha=0.6)
ax2.set_xlabel("FI — Fouling Index (Selig)  [P4 + P200, %]")
ax2.set_ylabel("Coda RMS (V/m)   (10–25 ns window)")
ax2.set_title(f"Coda RMS vs FI\n"
              f"(same 212 rocks, seed=42;  eps_fines={EPS_FINES:.0f}, P4_frac={P4_FRAC:.2f})")
ax2.grid(True, alpha=0.3)
ax2.legend(fontsize=8)
for label, x in zip(["C", "LF", "MF", "HF", "VHF"],
                     [0, 10, 20, 30, 40]):
    ax2.text(x + 1, ax2.get_ylim()[0] if ax2.get_ylim()[0] > 0
             else coda_pts.min()*0.95, label, fontsize=8,
             color="gray", va="bottom")

plt.tight_layout()
out = ROOT / "gssi_400_3d_virtual_sieve.png"
plt.savefig(out, dpi=150)
print(f"\n[plot] {out}")

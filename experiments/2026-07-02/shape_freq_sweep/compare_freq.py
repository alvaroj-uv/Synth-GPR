"""Sphere vs polyhedron coda correlation across frequency.

Prediction: r(sphere, poly) ~ 1.0 at 420 MHz (Rayleigh, shape invisible) and
DROPS as frequency rises into the Mie regime (shape becomes visible). Ey.
"""
import sys
from pathlib import Path

import numpy as np
import h5py
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO))
from src.signal_processing import coda_envelope_correlation

HERE = Path(__file__).parent
FREQS = [420, 1000, 1500, 2400]      # MHz
CODA_LO, CODA_HI = 3.0, 16.0

def rd(name):
    with h5py.File(HERE / f"{name}.out") as f:
        return f["rxs/rx1/Ey"][:].astype(float), float(f.attrs["dt"])

print(f"{'freq':>7} {'x(size param)':>13} {'r(sphere,poly)':>16}")
rows = []
for fmhz in FREQS:
    sph, dt = rd(f"sphere_{fmhz}mhz")
    pol, _ = rd(f"poly_{fmhz}mhz")
    r = coda_envelope_correlation(sph, dt, pol, dt, CODA_LO, CODA_HI)
    lam = 3e8 / (fmhz * 1e6 * np.sqrt(5))
    x = 2 * np.pi * 0.025 / lam
    print(f"{fmhz:>5}MHz {x:>13.2f} {r:>16.6f}")
    rows.append((fmhz, x, r))

xs = [r[1] for r in rows]
rr = [r[2] for r in rows]
fig, ax = plt.subplots(figsize=(8, 5))
ax.plot([r[0]/1000 for r in rows], rr, "o-", lw=2, ms=9)
for fmhz, x, r in rows:
    ax.annotate(f"x={x:.1f}", (fmhz/1000, r), textcoords="offset points",
                xytext=(6, -12), fontsize=8)
ax.axhline(1.0, color="gray", ls=":", lw=1)
ax.axvspan(0, 0.6, alpha=0.06, color="green")   # rough Rayleigh band edge (x<~1)
ax.set_xlabel("frequency (GHz)")
ax.set_ylabel("r(sphere, polyhedron)  coda 3-16 ns")
ax.set_title("Shape visibility vs frequency (same volume-matched rocks)\n"
             "r~1 = shape invisible (Rayleigh); r<1 = shape visible (Mie)")
ax.grid(alpha=0.2)
fig.tight_layout()
fig.savefig(HERE / "shape_vs_frequency.png", dpi=140)
print("\nsaved shape_vs_frequency.png")
print("TREND:", "shape becomes visible with frequency (r drops)"
      if rr[-1] < rr[0] - 0.02 else "no clear trend")

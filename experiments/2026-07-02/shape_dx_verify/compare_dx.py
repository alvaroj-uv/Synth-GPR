"""Compare sphere-small vs polyhedron coda correlation at dx=2mm and dx=1mm.

If r(sphere, poly) stays ~1.0 at BOTH resolutions, shape invisibility is not a
grid artifact. Analyses Ey (the y-dipole co-pol component).
"""
import sys
from pathlib import Path

import numpy as np
import h5py

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO))
from src.signal_processing import coda_envelope_correlation, coda_energy_ratio

HERE = Path(__file__).parent
CODA_LO, CODA_HI = 3.0, 16.0


def rd(name):
    with h5py.File(HERE / f"{name}.out") as f:
        return f["rxs/rx1/Ey"][:].astype(float), float(f.attrs["dt"])


print(f"{'dx':>6} {'r(sphere,poly)':>16} {'ratio_sph':>10} {'ratio_poly':>11} "
      f"{'dt(ps)':>8} {'n':>6}")
rows = []
for dx_mm in (2, 1):
    sph, dt = rd(f"sphere_small_dx{dx_mm}mm")
    pol, _ = rd(f"polyhedron_dx{dx_mm}mm")
    r = coda_envelope_correlation(sph, dt, pol, dt, CODA_LO, CODA_HI)
    rs = coda_energy_ratio(sph, dt, CODA_LO, (CODA_LO + CODA_HI) / 2, CODA_HI)
    rp = coda_energy_ratio(pol, dt, CODA_LO, (CODA_LO + CODA_HI) / 2, CODA_HI)
    print(f"{dx_mm:>4}mm {r:>16.6f} {rs:>10.4f} {rp:>11.4f} "
          f"{dt*1e12:>8.2f} {sph.size:>6}")
    rows.append((dx_mm, r))

print()
print("VERDICT: shape invisibility is PHYSICAL (not a dx artifact)"
      if all(r > 0.999 for _, r in rows) else
      "shape distinguishable at some dx -> revisit")

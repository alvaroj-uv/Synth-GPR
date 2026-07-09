"""
Virtual sieve analysis for 3D sphere packings.

Two-layer model:
  Layer 1 — ballast rocks (40–66 mm spheres, explicit in gprMax)
  Layer 2 — fouling fines (sub-grid, modelled analytically as void fill)

Workflow:
  rock spheres   → virtual sieve → rock PSD / EN-13450 grade
  PVC (0→1)      → FI (Selig)   via CRIM volume fractions
  PVC            → eps_void      via linear mixing (air + fine material)
  eps_void       → coda RMS      via interpolation of FDTD sweep

FI (Selig) = P4 + P200
  P4   = % by volume passing 4 mm sieve
  P200 = % by volume passing 0.075 mm sieve (200 mesh)

Fine PSD assumed log-normal: d50=1.5 mm, σ_ln=0.8
  → P4   ≈ 89 %  of fine mass passes 4 mm
  → P200 ≈  0 %  of fine mass passes 0.075 mm (all fines > 0.5 mm)
"""
from __future__ import annotations

import numpy as np
from dataclasses import dataclass
from typing import Sequence
from scipy.stats import lognorm
from scipy.interpolate import interp1d

# EN 13450 standard sieve openings (mm)
EN13450_SIEVES = [4, 8, 11.2, 16, 22.4, 31.5, 40, 50, 63, 80, 100]

# Default fine PSD — log-normal, d50=1.5 mm, sigma_ln=0.8
_FINE_D50  = 1.5    # mm
_FINE_SLGN = 0.8   # log-normal shape (σ of ln(d))
_FINE_DIST = lognorm(s=_FINE_SLGN, scale=_FINE_D50)

# Fraction of fines passing key sieves (from log-normal CDF)
P4_FRAC   = float(_FINE_DIST.cdf(4.0))      # ≈ 0.89
P200_FRAC = float(_FINE_DIST.cdf(0.075))    # ≈ 0.00


@dataclass
class SieveResult:
    sieves_mm:      np.ndarray   # sieve openings (mm)
    pct_passing:    np.ndarray   # cumulative % passing by volume
    d10:            float        # mm
    d50:            float        # mm
    d60:            float        # mm
    cu:             float        # uniformity coefficient D60/D10
    en13450_grade:  str          # closest EN 13450 grade


def sieve_rocks(spheres, sieves_mm: Sequence[float] = EN13450_SIEVES) -> SieveResult:
    """
    Virtual sieve analysis on a list of PackedSphere objects.

    Uses sphere diameter as the equivalent sieve dimension (a sphere passes
    a square sieve opening equal to its diameter).
    """
    diams_mm = np.array([s.r * 2e3 for s in spheres])
    vols     = np.array([(4/3) * np.pi * s.r**3 for s in spheres])
    total_v  = vols.sum()

    sieves_mm = np.array(sorted(sieves_mm), dtype=float)
    pct = np.array([vols[diams_mm < d].sum() / total_v * 100 for d in sieves_mm])

    # Characteristic diameters by linear interpolation on cumulative curve
    d_vals = np.concatenate([[0], sieves_mm])
    p_vals = np.concatenate([[0], pct])
    interp = interp1d(p_vals, d_vals, bounds_error=False,
                      fill_value=(d_vals[0], d_vals[-1]))
    d10 = float(interp(10))
    d50 = float(interp(50))
    d60 = float(interp(60))
    cu  = d60 / d10 if d10 > 0 else np.nan

    # EN 13450 grade heuristic (by D50)
    if d50 < 40:
        grade = "< 31.5/40"
    elif d50 < 50:
        grade = "31.5/50"
    elif d50 < 63:
        grade = "40/63"
    else:
        grade = "> 50/63"

    return SieveResult(sieves_mm, pct, d10, d50, d60, cu, grade)


# ── FI / PVC / eps_void mapping ───────────────────────────────────────────────

def pvc_to_fi(pvc: float | np.ndarray, phi_rocks: float = 0.39) -> float | np.ndarray:
    """
    Convert Percent Void Contamination to Selig FI.

    phi_rocks: granite volume fraction from inflation packing (~0.39)
    phi_void  = 1 - phi_rocks  (void volume fraction)
    phi_fines = pvc × phi_void  (fine volume fraction)

    FI = (P4_frac + P200_frac) × phi_fines / (phi_rocks + phi_fines) × 100
    """
    phi_void  = 1.0 - phi_rocks
    phi_fines = pvc * phi_void
    fi = (P4_FRAC + P200_FRAC) * phi_fines / (phi_rocks + phi_fines) * 100
    return fi


def fi_to_pvc(fi: float | np.ndarray, phi_rocks: float = 0.39) -> float | np.ndarray:
    """Inverse of pvc_to_fi: given FI, return PVC."""
    p_tot    = P4_FRAC + P200_FRAC
    phi_void = 1.0 - phi_rocks
    # Derived analytically from pvc_to_fi equation
    pvc = (fi / 100 * phi_rocks) / (phi_void * (p_tot - fi / 100))
    return pvc


def pvc_to_eps_void(pvc: float | np.ndarray, eps_fines: float = 10.0) -> float | np.ndarray:
    """
    Linear CRIM mixing: void fill = air (eps=1) + fines (eps_fines).
    eps_void = (1 - pvc) × 1 + pvc × eps_fines
    """
    return 1.0 + pvc * (eps_fines - 1.0)


def eps_void_to_fi(eps_void: float | np.ndarray,
                   eps_fines: float = 10.0,
                   phi_rocks: float = 0.39) -> float | np.ndarray:
    """Convenience: eps_void → PVC → FI."""
    pvc = (eps_void - 1.0) / (eps_fines - 1.0)
    pvc = np.clip(pvc, 0, 1)
    return pvc_to_fi(pvc, phi_rocks)


def make_fi_coda_curve(
    sweep: list[dict],
    eps_fines: float = 10.0,
    phi_rocks: float = 0.39,
) -> tuple[np.ndarray, np.ndarray]:
    """
    Build a smooth FI vs coda_RMS curve from the eps_void sweep results.

    sweep: list of dicts with keys 'eps_void' and 'coda_rms'
    Returns: (fi_arr, coda_rms_arr) sorted by FI
    """
    eps_v  = np.array([r["eps_void"] for r in sweep])
    coda   = np.array([r["coda_rms"] for r in sweep])
    fi_pts = eps_void_to_fi(eps_v, eps_fines=eps_fines, phi_rocks=phi_rocks)

    order  = np.argsort(fi_pts)
    return fi_pts[order], coda[order]

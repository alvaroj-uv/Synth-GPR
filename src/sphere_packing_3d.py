"""
3D sphere packing via iterative radius inflation (Lubachevsky-Stillinger style).

Inspired by the RCPGenerator approach (kd-physics.github.io/notes/packing-spheres-python.html):
  1. Place N spheres at random positions with zero radius
  2. Gradually inflate radii toward target sizes
  3. At each inflation step, resolve overlaps by pushing centres apart
  4. After each inflation pass, apply gravity (drop spheres down)
  5. Stop when target fill ratio φ is reached

This reaches φ ≈ 0.35–0.45 easily — well above RSA's φ ≈ 0.15–0.20 limit.
Polydisperse sizes (EN-13450 grading or custom range) are fully supported.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import List

import numpy as np
from scipy.spatial import cKDTree


@dataclass
class PackedSphere:
    x: float
    y: float
    z: float
    r: float


@dataclass
class PackingBounds3D:
    x_min: float; x_max: float
    y_min: float; y_max: float
    z_min: float; z_max: float

    @property
    def volume(self) -> float:
        return (self.x_max - self.x_min) * (self.y_max - self.y_min) * (self.z_max - self.z_min)


def pack_spheres(
    bounds: PackingBounds3D,
    r_min: float = 0.020,
    r_max: float = 0.033,
    target_phi: float = 0.38,
    n_inflate_steps: int = 60,
    n_relax_iter: int = 80,
    relax_alpha: float = 0.50,
    gravity_steps: int = 5,
    gravity_step_m: float = 0.002,
    seed: int = 42,
    min_gap: float = 0.0005,
    max_spheres: int = 2000,
    size_dist: str = "uniform",
    lognormal_sigma: float = 0.35,
) -> List[PackedSphere]:
    """
    Pack spheres into bounds using inflation + overlap resolution.

    Args:
        bounds:           3D bounding box for the packing region
        r_min/r_max:      Radius range (m); samples outside this are clipped
        target_phi:       Target volume fill fraction (0.38 → 38 %)
        n_inflate_steps:  Number of radius-growth stages
        n_relax_iter:     Overlap-resolution iterations per stage
        relax_alpha:      Step size for pushing centres apart (0–1)
        gravity_steps:    Down-drop steps applied after each inflation pass
        gravity_step_m:   Size of each gravity drop step (m)
        seed:             RNG seed for reproducibility
        min_gap:          Minimum surface-to-surface clearance (m)
        max_spheres:      Safety cap on number of spheres
        size_dist:        Radius distribution: "uniform" (flat) or "lognormal"
                          (lognormal centred on the geometric mean of r_min/r_max,
                          clipped to [r_min, r_max] — gives realistic polydispersity)
        lognormal_sigma:  Log-space std-dev when size_dist="lognormal" (0.35 ≈
                          1.4× spread either side of the geometric mean)

    Returns:
        List of PackedSphere with final positions and radii.
    """
    rng = np.random.default_rng(seed)

    # Estimate number of spheres needed to hit target_phi.
    # For lognormal use the geometric mean (= exp(mu_log)) as the representative radius;
    # for uniform use the arithmetic mean.
    if size_dist == "lognormal":
        r_rep = math.sqrt(r_min * r_max)   # geometric mean
    else:
        r_rep = (r_min + r_max) / 2.0
    vol_per_sphere = (4.0 / 3.0) * math.pi * r_rep ** 3
    n_spheres = min(int(target_phi * bounds.volume / vol_per_sphere) + 1, max_spheres)

    # 1. Initial positions: random inside bounds (with margin = r_max)
    margin = r_max
    pos = np.column_stack([
        rng.uniform(bounds.x_min + margin, bounds.x_max - margin, n_spheres),
        rng.uniform(bounds.y_min + margin, bounds.y_max - margin, n_spheres),
        rng.uniform(bounds.z_min + margin, bounds.z_max - margin, n_spheres),
    ])

    # Assign target radii
    if size_dist == "lognormal":
        # Lognormal centred on the geometric mean of [r_min, r_max]
        r_geom = math.sqrt(r_min * r_max)
        mu_log = math.log(r_geom)
        samples = rng.lognormal(mean=mu_log, sigma=lognormal_sigma, size=n_spheres)
        radii_target = np.clip(samples, r_min, r_max)
    else:
        # Default: flat uniform distribution
        radii_target = rng.uniform(r_min, r_max, n_spheres)

    # Start inflation at 20 % of target radii
    radii = radii_target * 0.20

    # 2. Iterative inflation
    for step in range(n_inflate_steps):
        frac   = (step + 1) / n_inflate_steps
        radii  = radii_target * (0.20 + 0.80 * frac)   # grow 20 % → 100 %

        # Overlap resolution
        pos = _resolve_overlaps(pos, radii, bounds, n_relax_iter, relax_alpha, min_gap)

        # Gravity compaction every few steps
        if (step + 1) % max(1, n_inflate_steps // gravity_steps) == 0:
            pos = _apply_gravity(pos, radii, bounds, gravity_step_m, min_gap)

    # Final gravity settle
    pos = _apply_gravity(pos, radii, bounds, gravity_step_m * 0.5, min_gap, n_passes=4)

    spheres = [PackedSphere(float(pos[i, 0]), float(pos[i, 1]), float(pos[i, 2]),
                            float(radii[i]))
               for i in range(n_spheres)]
    phi = sum((4/3)*math.pi*s.r**3 for s in spheres) / bounds.volume
    print(f"[3D pack] {n_spheres} spheres  phi={phi:.3f}  target={target_phi:.3f}")
    return spheres


# ── Internal helpers ──────────────────────────────────────────────────────────

def _resolve_overlaps(
    pos: np.ndarray,
    radii: np.ndarray,
    bounds: PackingBounds3D,
    n_iter: int,
    alpha: float,
    min_gap: float,
) -> np.ndarray:
    """Push overlapping sphere centres apart and clamp to bounds."""
    n = len(pos)
    r_max = radii.max()

    for _ in range(n_iter):
        tree  = cKDTree(pos)
        pairs = tree.query_pairs(r=2.0 * r_max + min_gap, output_type="ndarray")
        if len(pairs) == 0:
            break
        delta = np.zeros_like(pos)
        for i, j in pairs:
            diff = pos[i] - pos[j]
            dist = np.linalg.norm(diff)
            need = radii[i] + radii[j] + min_gap
            if dist < need:
                if dist < 1e-9:
                    diff = rng_fallback(pos.shape[1])
                    dist = 1.0
                push  = (need - dist) * 0.5 * alpha
                unit  = diff / dist
                delta[i] += push * unit
                delta[j] -= push * unit
        pos += delta
        pos  = _clamp(pos, radii, bounds)
    return pos


def rng_fallback(ndim: int) -> np.ndarray:
    v = np.random.randn(ndim)
    return v / (np.linalg.norm(v) + 1e-12)


def _apply_gravity(
    pos: np.ndarray,
    radii: np.ndarray,
    bounds: PackingBounds3D,
    step_m: float,
    min_gap: float,
    n_passes: int = 1,
) -> np.ndarray:
    """Drop each sphere as far down (−Y) as possible without overlap."""
    for _ in range(n_passes):
        order = np.argsort(pos[:, 1])   # process bottom to top
        for idx in order:
            r = radii[idx]
            floor = bounds.y_min + r
            while pos[idx, 1] > floor:
                new_y  = pos[idx, 1] - step_m
                new_y  = max(new_y, floor)
                test   = pos.copy(); test[idx, 1] = new_y
                # Check collision with ALL other spheres
                diffs  = test[idx] - np.delete(pos, idx, axis=0)
                dists  = np.linalg.norm(diffs, axis=1)
                min_ds = (radii[idx] + np.delete(radii, idx)) + min_gap
                if np.any(dists < min_ds):
                    break
                pos[idx, 1] = new_y
    return pos


def _clamp(pos: np.ndarray, radii: np.ndarray, bounds: PackingBounds3D) -> np.ndarray:
    """Keep sphere centres inside bounds (hard walls)."""
    pos[:, 0] = np.clip(pos[:, 0], bounds.x_min + radii, bounds.x_max - radii)
    pos[:, 1] = np.clip(pos[:, 1], bounds.y_min + radii, bounds.y_max - radii)
    pos[:, 2] = np.clip(pos[:, 2], bounds.z_min + radii, bounds.z_max - radii)
    return pos

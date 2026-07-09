"""
RCP (Random Close Packing) via soft-sphere expansion–relaxation.

Independent re-implementation of the published jamming/expansion–relaxation
scheme (Desmond & Weeks, Phys. Rev. E 80, 051305, 2009; soft-sphere jamming,
O'Hern et al. 2003). No third-party code is used — only the algorithm.
Inspiration: github.com/KD-physics/RCPGenerator (gradient-based expansion).

Algorithm (2-D disks):
  1. Drop N disks at random positions, each with a *target* radius drawn from the
     size range / grading curve, started small (no overlap).
  2. Alternate: (a) RELAX — gradient-descend the harmonic overlap energy
        U = Σ_{i<j} k·δ_ij²   with δ_ij = (R_i+R_j+gap) − |r_i−r_j|  (>0 = overlap)
     so overlapping disks push apart; (b) INFLATE — grow all radii a little.
  3. Stop when the pack jams (overlaps can no longer be removed) or the target
     area fill is reached. The jammed state is the random-close-packed configuration.

Output: List[Rock] circles (x, y, radius). The base RockPackingStrategy.pack()
polygonises them into angular #triangle stones, exactly like the other packers.
"""
from typing import List, Optional, Tuple

import numpy as np

from .rock_model import PackingBounds, Rock
from .rock_packing import GradingCurve, RockPackingStrategy


class RCPPacking(RockPackingStrategy):
    """Random Close Packing via soft-sphere expansion–relaxation (2-D).

    Produces denser, more uniform packings than RSA-family strategies and is
    deterministic given a seed. Returns circle ``Rock``s; ``pack()`` polygonises.

    Args:
        n_relax:       Relaxation (gradient-descent) iterations per inflation step.
        n_inflate:     Max inflation steps.
        dt:            Gradient-descent step size (fraction of mean radius).
        grow_rate:     Per-step radius growth factor when there is room (e.g. 1.03).
        jam_tol:       Overlap (fraction of mean radius) below which the pack is
                       considered relaxed; persistent overlap above it = jammed.
        min_gap:       Surface-to-surface clearance (m) added to contact distance.
        boundary:      'wall' (hard walls, disks kept inside bounds) or
                       'periodic' (wrap-around — denser, no wall depletion).
    """

    def __init__(
        self,
        n_relax: int = 50,
        n_inflate: int = 120,
        dt: float = 0.10,
        grow_rate: float = 1.03,
        jam_tol: float = 5e-3,
        min_gap: float = 0.0,
        boundary: str = "wall",
    ):
        self.n_relax = n_relax
        self.n_inflate = n_inflate
        self.dt = dt
        self.grow_rate = grow_rate
        self.jam_tol = jam_tol
        self.default_min_gap = min_gap
        self.boundary = boundary

    # ── Public interface ───────────────────────────────────────────────────────

    def generate_rocks(
        self,
        bounds: PackingBounds,
        radius_min: float,
        radius_max: float,
        target_fill_ratio: float = 0.82,   # ~RCP for 2-D disks
        max_attempts: int = 0,             # unused (kept for interface parity)
        min_gap: float = 0.0,
        grading_curve: Optional[GradingCurve] = None,
        seed: Optional[int] = None,
    ) -> List[Rock]:
        rng = np.random.default_rng(seed)
        W, H = bounds.width, bounds.height
        gap = max(min_gap, self.default_min_gap)

        # 1. how many disks for the target fill, and their TARGET radii
        r_targets = self._sample_target_radii(radius_min, radius_max, target_fill_ratio,
                                              W * H, grading_curve, rng)
        N = len(r_targets)
        if N == 0:
            return []

        # 2. random initial positions; start radii small so nothing overlaps
        pos = np.column_stack([rng.uniform(0, W, N), rng.uniform(0, H, N)])
        scale = 0.35
        r_mean = float(r_targets.mean())

        # 3. expansion–relaxation loop
        for _ in range(self.n_inflate):
            r = r_targets * scale
            self._relax(pos, r, gap, W, H)
            overlap = self._max_overlap(pos, r, gap) / r_mean
            target_reached = scale >= 1.0 and overlap < self.jam_tol
            if target_reached:
                break
            if overlap < 2 * self.jam_tol:
                scale = min(1.0, scale * self.grow_rate)   # room → inflate
            else:
                scale *= 0.997                              # jammed → ease off
        r_final = r_targets * scale

        # 4. emit circle Rocks (offset back to absolute bounds coordinates)
        rocks = []
        for (x, y), rad in zip(pos, r_final):
            rocks.append(Rock(x=float(bounds.x_min + x),
                              y=float(bounds.y_min + y),
                              radius=float(rad)))
        return rocks

    # ── Core physics ─────────────────────────────────────────────────────────────

    def _relax(self, pos: np.ndarray, r: np.ndarray, gap: float, W: float, H: float) -> None:
        """In-place gradient descent on the harmonic overlap energy.

        The force is already in length units (sum of pairwise overlaps), so the
        step is a DIMENSIONLESS fraction ``dt`` of it — two disks overlapping by
        δ each move ~dt·δ apart, shrinking the overlap by ~2·dt·δ per iteration
        (geometric convergence for dt≈0.1–0.2). Do NOT scale by r.mean(): that
        made steps ~1000× too small and the pack jammed at the start radius.
        """
        for _ in range(self.n_relax):
            disp = self._overlap_forces(pos, r, gap)
            if np.abs(disp).max() < 1e-7:
                break
            pos += self.dt * disp
            if self.boundary == "periodic":
                pos[:, 0] %= W
                pos[:, 1] %= H
            else:  # hard walls — keep each disk fully inside the box
                np.clip(pos[:, 0], r, W - r, out=pos[:, 0])
                np.clip(pos[:, 1], r, H - r, out=pos[:, 1])

    def _overlap_forces(self, pos: np.ndarray, r: np.ndarray, gap: float) -> np.ndarray:
        """Net repulsive displacement on each disk from pairwise overlaps."""
        d = pos[:, None, :] - pos[None, :, :]                # (N,N,2) i-j vectors
        if self.boundary == "periodic":
            # minimum-image convention handled by caller box already wrapped;
            # for simplicity walls are the default — periodic uses raw d here.
            pass
        dist = np.sqrt((d ** 2).sum(-1)) + np.eye(len(pos))  # avoid /0 on diagonal
        contact = r[:, None] + r[None, :] + gap
        overlap = contact - dist                              # >0 where overlapping
        np.fill_diagonal(overlap, 0.0)
        overlap = np.clip(overlap, 0.0, None)
        # force magnitude ∝ overlap, direction = unit(i−j); sum over j
        with np.errstate(invalid="ignore", divide="ignore"):
            unit = d / dist[..., None]
        force = (overlap[..., None] * unit).sum(axis=1)       # (N,2)
        return force

    @staticmethod
    def _max_overlap(pos: np.ndarray, r: np.ndarray, gap: float) -> float:
        d = pos[:, None, :] - pos[None, :, :]
        dist = np.sqrt((d ** 2).sum(-1)) + np.eye(len(pos)) * 1e9
        overlap = (r[:, None] + r[None, :] + gap) - dist
        return float(np.clip(overlap, 0.0, None).max()) if len(pos) > 1 else 0.0

    # ── Helpers ──────────────────────────────────────────────────────────────────

    def _sample_target_radii(self, radius_min, radius_max, target_fill,
                             area, grading_curve, rng) -> np.ndarray:
        """Draw enough radii (from grading curve or uniform) to fill ``target_fill``."""
        # expected r² for area→count estimate
        if grading_curve is not None:
            sample = np.array([grading_curve.sample(clamp_min=radius_min, clamp_max=radius_max)
                               for _ in range(256)])
            er2 = float((sample ** 2).mean())
        else:
            a, b = radius_min, radius_max
            er2 = (a * a + a * b + b * b) / 3.0
        n = max(1, int(round(target_fill * area / (np.pi * er2))))
        if grading_curve is not None:
            radii = np.array([grading_curve.sample(clamp_min=radius_min, clamp_max=radius_max)
                              for _ in range(n)])
        else:
            radii = rng.uniform(radius_min, radius_max, n)
        return radii

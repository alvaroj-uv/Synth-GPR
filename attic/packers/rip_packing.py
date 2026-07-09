"""
RIP (Random Irregular Polygon) packing for Mbubia-style 1.4 GHz simulations.

Reference: Mbubia 2026 (Transportation Engineering), Li et al. 2023 [Ref 42].
Grain shape: vertex_i = center + (r_mean + δr_i) * [cos(θ_i), sin(θ_i)]
Size range: 36–60 mm diameter (18–30 mm radius), narrow coarse-only grading.
Packing: RSA (Random Sequential Adsorption), no gravity settling.
"""
import math
import random
from typing import List, Optional, Tuple

import numpy as np

from .rock_model import PackingBounds, Rock, rip_polygon_vertices
from .rock_packing import CircleQuadtree, GradingCurve, RockPackingStrategy


class RIPPacking(RockPackingStrategy):
    """
    Random Irregular Polygon (RIP) packing matching Mbubia 2026.

    Each grain is an n-gon whose vertices are:
        vertex_i = center + (r_mean + δr_i) × [cos(θ_i), sin(θ_i)]
    with random radial noise δr_i (±roughness fraction) and small angular jitter
    so grains are angularly irregular rather than regular polygons.

    Placement uses RSA (Random Sequential Adsorption): grains are placed one at a
    time at uniform-random positions; a placement is rejected if the bounding circle
    of the new grain overlaps any previously placed grain (surface-to-surface gap
    enforced via min_gap).

    Unlike pymunk_ballast, RIP requires no physics engine and no gravity settling.
    It directly produces polygon rocks ready for _stamp_polygon in granular_worker.

    Note:
        radius_min / radius_max passed to generate_rocks() are IGNORED when they
        fall outside [r_min, r_max] — RIP is purpose-built for the 36–60 mm coarse
        fraction (same as pymunk_ballast ignoring target_fill_ratio in favour of
        void_ratio).  To use a different size range, set r_min/r_max in __init__.

    Args:
        r_min:            Minimum grain radius (m). Default 0.018 m = 36 mm diameter.
        r_max:            Maximum grain radius (m). Default 0.030 m = 60 mm diameter.
        n_vertices_range: (min, max) polygon vertices per grain (default 8–12).
        roughness:        Amplitude of per-vertex radial noise as fraction of r_mean
                          (default 0.25 → ±25% radius variation per vertex).
        rsa_attempts:     Maximum RSA placement rejection attempts (default 20 000).
        min_gap:          Surface-to-surface clearance enforced by RSA (m, default 1 mm).
    """

    def __init__(
        self,
        r_min: float = 0.018,
        r_max: float = 0.030,
        n_vertices_range: Tuple[int, int] = (8, 12),
        roughness: float = 0.25,
        rsa_attempts: int = 20_000,
        min_gap: float = 0.001,
    ):
        self.r_min = r_min
        self.r_max = r_max
        self.n_vertices_range = n_vertices_range
        self.roughness = roughness
        self.rsa_attempts = rsa_attempts
        self.default_min_gap = min_gap

    # ── Public interface ───────────────────────────────────────────────────────

    def generate_rocks(
        self,
        bounds: PackingBounds,
        radius_min: float = None,
        radius_max: float = None,
        target_fill_ratio: float = 0.40,
        max_attempts: int = None,
        min_gap: float = None,
        grading_curve: Optional[GradingCurve] = None,
    ) -> List[Rock]:
        """Place RIP grains via RSA and return rocks with polygon vertices set."""
        # Honour caller radius limits only when they narrow the RIP range.
        r_min = self.r_min if radius_min is None else max(self.r_min, radius_min)
        r_max = self.r_max if radius_max is None else min(self.r_max, radius_max)
        if r_min > r_max:
            r_min, r_max = self.r_min, self.r_max  # fallback to class defaults

        if max_attempts is None:
            max_attempts = self.rsa_attempts
        if min_gap is None:
            min_gap = self.default_min_gap

        rng = np.random.default_rng()
        qt = CircleQuadtree(bounds, max_depth=7)
        rocks: List[Rock] = []
        current_fill = 0.0
        attempts = 0

        while current_fill < target_fill_ratio and attempts < max_attempts:
            attempts += 1

            r_mean = random.uniform(r_min, r_max)
            # Use r_mean for both RSA collision check and Rock.radius so the Qt
            # is self-consistent (bounding circle of each grain = r_mean circle).
            # Polygon corners extend up to r_mean*(1+roughness), so adjacent grains
            # may touch at corners — physically correct for dense coarse ballast.
            bounding_r = r_mean * (1.0 + self.roughness)

            # Clamp centre so entire bounding circle stays inside domain.
            if bounding_r * 2.0 > bounds.width or bounding_r * 2.0 > bounds.height:
                continue
            cx = random.uniform(bounds.x_min + bounding_r, bounds.x_max - bounding_r)
            cy = random.uniform(bounds.y_min + bounding_r, bounds.y_max - bounding_r)

            # RSA rejection on mean circles (r_mean), not bounding circles, so
            # corners may overlap but centres stay separated by 2*r_mean + gap.
            if qt.overlaps_any(cx, cy, r_mean, min_gap=min_gap):
                continue

            verts = self._rip_polygon(cx, cy, r_mean, rng)
            # Store r_mean as radius (used by Qt and compaction).
            rock = Rock(x=cx, y=cy, radius=r_mean, vertices=verts)
            rocks.append(rock)
            qt.insert(rock)
            current_fill += math.pi * r_mean ** 2 / bounds.area

        # Gravity compaction: drop each rock to its lowest non-overlapping position.
        rocks = self._compact(rocks, bounds)
        return rocks

    def _compact(self, rocks: List[Rock], bounds: PackingBounds) -> List[Rock]:
        """Drop each rock under gravity to the lowest non-overlapping y position.

        Uses 5 mm drop steps and O(N²) pair checks — fast enough for ~300 grains.
        Polygon vertices are shifted by the same dy as the centre so geometry
        stays consistent with the settled Rock.x / Rock.y fields.
        """
        drop_step = 0.005  # 5 mm per iteration — fast settle, still fine-grained enough
        rocks.sort(key=lambda r: r.y)  # process bottom to top

        settled: List[Rock] = []
        for rock in rocks:
            r = rock.radius  # = r_mean
            orig_cy = sum(v[1] for v in rock.vertices) / len(rock.vertices)

            # Drop until the bounding circle hits the floor or another rock.
            while rock.y - r * (1.0 + self.roughness) > bounds.y_min:
                new_y = rock.y - drop_step
                floor = new_y - r * (1.0 + self.roughness)
                if floor < bounds.y_min:
                    new_y = bounds.y_min + r * (1.0 + self.roughness)
                    rock.y = new_y
                    break
                if any(math.hypot(rock.x - s.x, new_y - s.y) < r + s.radius
                       for s in settled):
                    break
                rock.y = new_y

            # Shift polygon vertices by the same displacement as the centre.
            dy = rock.y - orig_cy
            rock.vertices = [(vx, vy + dy) for vx, vy in rock.vertices]
            settled.append(rock)

        return settled

    def polygonize(self, rocks: List[Rock], **_) -> List[Rock]:
        """No-op: RIP rocks already have polygon vertices from generate_rocks."""
        return rocks

    # ── Private helpers ────────────────────────────────────────────────────────

    def _rip_polygon(
        self,
        cx: float,
        cy: float,
        r_mean: float,
        rng: np.random.Generator,
    ) -> List[Tuple[float, float]]:
        """Build one RIP polygon centred at (cx, cy) with mean radius r_mean.

        Following Li et al. 2023 (Ref [42] in Mbubia 2026). Delegates to the
        shape-only helper in rock_model so any packer can produce the same
        polygon style — see rock_model.rip_polygon_vertices.
        """
        return rip_polygon_vertices(
            cx, cy, r_mean, rng,
            n_vertices_range=self.n_vertices_range,
            roughness=self.roughness,
        )

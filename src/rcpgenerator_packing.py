"""
RCPGeneratorPacking — wraps the real RCPGenerator C++ engine.

Source: KD-physics/RCPGenerator (MIT License). The Python package wraps a
validated C++ optimization-inflation Random-Close-Packing engine (Desmond &
Weeks, Phys. Rev. E 80, 051305, 2009) via pybind11.

Install (built from the vendored clone with MSVC + CMake):
    pip install external/RCPGenerator/python_code/python

This is the *authoritative* RCP packer. For a dependency-free pure-Python
alternative implementing the same algorithm class, see rcp_packing.RCPPacking.

How the engine maps to our interface
------------------------------------
* ``dist`` diameters are RELATIVE; the engine scales them to absolute box units
  so that N particles reach the target packing fraction. We therefore choose N
  from the desired mean radius and target fill, pass a flat ratio
  (d_max/d_min), and ``relax(target_phi=…)`` to the requested fill — which
  reproduces the requested [radius_min, radius_max] range exactly (verified).
* ``walls=[1,1]`` = hard walls → every disk stays inside ``bounds``.
"""
from typing import List, Optional

import numpy as np

from .rock_model import PackingBounds, Rock
from .rock_packing import GradingCurve, RockPackingStrategy


class RCPGeneratorPacking(RockPackingStrategy):
    """Random Close Packing via the RCPGenerator C++ engine (2-D disks).

    Returns circle ``Rock``s; the base ``pack()`` polygonises them, exactly like
    every other strategy. Deterministic given a seed.

    Args:
        start_phi:  Initial (low) packing fraction for placement before
                    inflation; must be loose enough to seat N particles without
                    overlap (default 0.15).
        n_steps:    Relaxation step budget for reaching the target fill.
        verbose:    Forward the engine's progress output.

    Boundaries are hard walls on every axis (``walls=[1]*ndim``) so particles
    stay inside ``bounds``, in both 2-D and 3-D.
    """

    def __init__(
        self,
        start_phi: float = 0.15,
        n_steps: int = 4000,
        verbose: bool = False,
    ):
        self.start_phi = start_phi
        self.n_steps = n_steps
        self.verbose = verbose

    def generate_rocks(
        self,
        bounds: PackingBounds,
        radius_min: float,
        radius_max: float,
        target_fill_ratio: float = 0.78,
        max_attempts: int = 0,            # unused (interface parity)
        min_gap: float = 0.0,             # engine packs to contact; gap not used
        grading_curve: Optional[GradingCurve] = None,
        seed: Optional[int] = None,
    ) -> List[Rock]:
        try:
            import rcpgenerator
        except ImportError as exc:  # pragma: no cover - depends on local build
            raise ImportError(
                "RCPGeneratorPacking needs the 'rcpgenerator' package. Build it with:\n"
                "  pip install external/RCPGenerator/python_code/python\n"
                "(requires a C++ compiler + CMake; pybind11/scikit-build pulled "
                "automatically). Or use algo 'rcp' for the pure-Python equivalent."
            ) from exc

        # Dimension-agnostic: read ndim/spans/origins from the bounds. Works for
        # 2-D disks (PackingBounds) and 3-D spheres (z bounds set) — the engine
        # is N-D, so this wrapper is too.
        ndim = bounds.ndim
        lengths = bounds.lengths              # [W, H] or [W, H, D]
        mins = bounds.mins                    # [x_min, y_min] or +[z_min]
        r_mean = 0.5 * (radius_min + radius_max)
        if r_mean <= 0:
            return []
        # N so the target fill is reached at the requested mean radius
        vol = float(np.prod(lengths))
        unit = (np.pi * r_mean ** 2) if ndim == 2 else (4.0 / 3.0 * np.pi * r_mean ** 3)
        N = max(2, int(round(target_fill_ratio * vol / unit)))
        ratio = max(1.0, radius_max / max(radius_min, 1e-9))
        dist = ({"type": "mono", "d": 1.0} if ratio <= 1.001
                else {"type": "flat", "d_min": 1.0, "d_max": ratio})

        pk = rcpgenerator.Packing(
            phi=min(self.start_phi, 0.5 * target_fill_ratio),
            N=N, Ndim=ndim, box=[float(L) for L in lengths], walls=[1] * ndim,
            dist=dist, seed=(0 if seed is None else int(seed)),
            verbose=self.verbose,
        )
        pk.relax(n_steps=self.n_steps, target_phi=float(target_fill_ratio),
                 verbose=self.verbose)

        pos = np.asarray(pk.positions, dtype=float)   # (N, ndim)
        dia = np.asarray(pk.diameters, dtype=float)
        rocks: List[Rock] = []
        for p, d in zip(pos, dia):
            coords = [mins[k] + float(p[k]) for k in range(ndim)]
            if not all(mins[k] <= coords[k] <= mins[k] + lengths[k] for k in range(ndim)):
                continue
            if ndim == 2:
                rocks.append(Rock(x=coords[0], y=coords[1], radius=float(d) / 2.0))
            else:
                rocks.append(Rock(x=coords[0], y=coords[1], z=coords[2],
                                  radius=float(d) / 2.0))
        return rocks

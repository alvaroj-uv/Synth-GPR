"""
Curated library of pre-packed rock geometries for MATCHED-PAIR experiments.

Motivation
----------
Every A/B study so far (fouling heterogeneity, antenna, waveform) needed the SAME
rock skeleton across arms so that only the variable under test changed. Re-running
a packing algorithm per arm causes RNG drift -> different rocks -> confounded
comparison (we worked around this with fragile text-surgery). A rock library fixes
this at the source: pack ONCE, store it, and reuse the identical geometry across
as many fouling / material / frequency variants as needed.

This is the GOOD half of GPR-repo's "circles in a file" idea WITHOUT the fragile
half: each packing is a self-contained .in fragment of literal #cylinder lines
(read by the existing :class:`src.rock_loader.RockLoader`), and the generator bakes
those literals into each scene's .in at generation time — so output .in files stay
portable and statically renderable. No runtime relative-path file-reads.

Usage
-----
Build a library once::

    from src.rock_library import RockLibrary
    lib = RockLibrary()                       # default dir: output/rock_library
    lib.build(n_per_grading=3, width=1.5, height=0.4)

Use a packing for a matched-pair experiment::

    entry = lib.query(grading="en13450", index=0)[0]
    config.rock_source_file = entry.path      # granular_worker loads these rocks
    # ...now vary pvc/moisture/frequency freely; rocks are identical across runs.

The on-disk layout is::

    output/rock_library/
        manifest.json                  # queryable index
        clean_en13450_w1.5_s0.in       # #cylinder fragment + ## metadata
        ...
"""

from __future__ import annotations

import json
import math
import random
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List, Optional

from .rock_model import PackingBounds, Rock
from .rock_packing import GradingCurve, PoissonDiskPacking


# Default library location (relative to repo root).
DEFAULT_LIBRARY_DIR = Path("output") / "rock_library"


@dataclass
class RockLibraryEntry:
    """One curated packing in the library."""
    name: str                  # unique id / filename stem
    path: str                  # absolute path to the .in fragment
    grading: str               # "en13450" | "fuller" | "uniform"
    width: float               # packing bounds width (m)
    height: float              # packing bounds height (m)
    fill_ratio: float          # target fill used
    seed: int                  # RNG seed (reproducibility)
    n_rocks: int               # number of cylinders stored
    radius_min: float
    radius_max: float


class RockLibrary:
    """Manifest-backed collection of reusable rock packings.

    Each entry is a minimal gprMax .in fragment containing only ``#cylinder``
    lines plus ``##`` metadata headers — exactly what
    :meth:`src.rock_loader.RockLoader.extract_rocks_from_file` reads. Set an
    entry's ``path`` as ``config.rock_source_file`` and the existing
    ``GranularMatrixWorker`` reuses that identical geometry.
    """

    def __init__(self, library_dir: Path | str = DEFAULT_LIBRARY_DIR):
        self.dir = Path(library_dir)
        self.manifest_path = self.dir / "manifest.json"
        self._entries: List[RockLibraryEntry] = []
        if self.manifest_path.exists():
            self._load_manifest()

    # ── persistence ─────────────────────────────────────────────────────────
    def _load_manifest(self) -> None:
        data = json.loads(self.manifest_path.read_text(encoding="utf-8"))
        self._entries = [RockLibraryEntry(**e) for e in data]

    def _save_manifest(self) -> None:
        self.dir.mkdir(parents=True, exist_ok=True)
        self.manifest_path.write_text(
            json.dumps([asdict(e) for e in self._entries], indent=2),
            encoding="utf-8",
        )

    # ── building ────────────────────────────────────────────────────────────
    def build(self,
              n_per_grading: int = 3,
              gradings: Optional[List[str]] = None,
              width: float = 1.5,
              height: float = 0.4,
              radius_min: float = 0.008,
              radius_max: float = 0.0315,
              fill_ratio: float = 0.6,
              base_seed: int = 1000,
              overwrite: bool = False) -> List[RockLibraryEntry]:
        """Pack `n_per_grading` layouts for each grading curve and store them.

        Deterministic: the same arguments reproduce the same packings (seeds are
        derived from `base_seed`). Existing entries are kept unless `overwrite`.
        """
        gradings = gradings or ["en13450", "fuller", "uniform"]
        if overwrite:
            self._entries = []

        for gi, grading in enumerate(gradings):
            curve = self._make_curve(grading, radius_min, radius_max)
            for k in range(n_per_grading):
                seed = base_seed + gi * 1000 + k
                name = f"{grading}_w{width}_s{seed}"
                if any(e.name == name for e in self._entries):
                    continue
                rocks = self._pack(curve, width, height, radius_min, radius_max,
                                   fill_ratio, seed)
                path = self._write_fragment(name, rocks, grading, width, height,
                                            fill_ratio, seed, radius_min, radius_max)
                self._entries.append(RockLibraryEntry(
                    name=name, path=str(path.resolve()), grading=grading,
                    width=width, height=height, fill_ratio=fill_ratio, seed=seed,
                    n_rocks=len(rocks), radius_min=radius_min, radius_max=radius_max,
                ))
        self._save_manifest()
        return list(self._entries)

    @staticmethod
    def _make_curve(grading: str, r_min: float, r_max: float) -> GradingCurve:
        if grading == "en13450":
            return GradingCurve.en13450()
        if grading == "fuller":
            return GradingCurve.fuller(d_max=r_max * 2)
        return GradingCurve.uniform(r_min, r_max)

    @staticmethod
    def _pack(curve, width, height, r_min, r_max, fill, seed) -> List[Rock]:
        # Seed BOTH RNGs the packing strategy uses, so layouts are reproducible.
        random.seed(seed)
        try:
            import numpy as np
            np.random.seed(seed)
        except Exception:
            pass
        bounds = PackingBounds(0.0, width, 0.0, height)
        strat = PoissonDiskPacking()
        return strat.generate_rocks(bounds, r_min, r_max,
                                    target_fill_ratio=fill, grading_curve=curve)

    def _write_fragment(self, name, rocks, grading, width, height, fill, seed,
                        r_min, r_max) -> Path:
        self.dir.mkdir(parents=True, exist_ok=True)
        path = self.dir / f"{name}.in"
        lines = [
            f"## rock_library: {name}",
            f"## grading: {grading}",
            f"## width: {width}",
            f"## height: {height}",
            f"## fill_ratio: {fill}",
            f"## seed: {seed}",
            f"## n_rocks: {len(rocks)}",
            "## NOTE: #cylinder fragment for RockLoader; not a standalone .in",
        ]
        # z extrusion 0..0.002 (2D slab default); granular_worker re-extrudes.
        for r in rocks:
            lines.append(
                f"#cylinder: {r.x:.5f} {r.y:.5f} 0 {r.x:.5f} {r.y:.5f} 0.002 "
                f"{r.radius:.5f} bal_rock"
            )
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return path

    # ── querying ────────────────────────────────────────────────────────────
    def query(self,
              grading: Optional[str] = None,
              width: Optional[float] = None,
              index: Optional[int] = None) -> List[RockLibraryEntry]:
        """Return entries matching the given filters.

        `index` selects the Nth match (after filtering) — handy for picking one
        stable packing to reuse across all arms of a matched-pair experiment.
        """
        out = self._entries
        if grading is not None:
            out = [e for e in out if e.grading == grading]
        if width is not None:
            out = [e for e in out if math.isclose(e.width, width, abs_tol=1e-6)]
        if index is not None:
            out = out[index:index + 1] if 0 <= index < len(out) else []
        return list(out)

    def get_source_file(self, grading: str = "en13450", index: int = 0) -> str:
        """Return a packing path to assign to ``config.rock_source_file``.

        Raises if the library is empty / no match — call :meth:`build` first.
        """
        matches = self.query(grading=grading, index=index)
        if not matches:
            raise ValueError(
                f"No library entry for grading={grading!r} index={index}. "
                f"Build the library first: RockLibrary().build()."
            )
        return matches[0].path

    @property
    def entries(self) -> List[RockLibraryEntry]:
        return list(self._entries)

    def __len__(self) -> int:
        return len(self._entries)

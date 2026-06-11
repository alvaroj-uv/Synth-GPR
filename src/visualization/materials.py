"""
Single source of truth for material rendering styles.

Every renderer (2D ``scene.draw_geometry``, 3D ``scene_3d.render_3d_views``,
legends, dashboards) MUST resolve material appearance through this registry —
never define local color/label/hatch dicts. This guarantees a material looks
identical in every figure and that adding a material is a one-place edit.

To add a material: add one ``MaterialStyle`` entry to ``MATERIALS`` and, if it
should appear in 2D legends, one slug in ``LEGEND_ORDER``. Nothing else.

Style fields:
  color     — fill color (hex) used by flat rendering (boxes, 3D views, legend)
  hatch     — matplotlib hatch pattern for 2D boxes/legend (None = no hatch)
  label     — human-readable legend label
  base_hsv  — optional (h, s, v) base for per-particle color jitter. Materials
              with a ``base_hsv`` get a randomized per-rock tint via
              ``jitter_color`` instead of the flat ``color`` (used for
              fan-triangulated rocks and polygon particles so individual
              grains are visually distinguishable).
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Optional

import matplotlib.colors
import matplotlib.pyplot as plt
import numpy as np


@dataclass
class MaterialStyle:
    color: str
    hatch: Optional[str] = None
    label: str = ""
    base_hsv: Optional[tuple] = None


def _hsv_hex(hsv: tuple) -> str:
    """Flat fallback color for materials defined primarily by a base_hsv."""
    return matplotlib.colors.to_hex(matplotlib.colors.hsv_to_rgb(list(hsv)))


# ── The registry ──────────────────────────────────────────────────────────────

MATERIALS: dict[str, MaterialStyle] = {
    # Scene background / structure
    "free_space":        MaterialStyle("#F0F4F8", None, "Air"),
    "subgrade":          MaterialStyle("#2F4F4F", "-",  "Subgrade"),
    "formation":         MaterialStyle("#BDB76B", "+",  "Formation"),
    "concrete_sleeper":  MaterialStyle("#708090", "x",  "Sleeper"),
    "antenna":           MaterialStyle("#404040", None, "Antenna (GSSI)"),

    # Ballast rock (per-rock jittered tint when triangulated)
    "bal_rock":          MaterialStyle("#5A5A5A", "/",   "Ballast Rock", base_hsv=(0.08, 0.20, 0.62)),
    "bal_rock_L1":       MaterialStyle("#A1887F", "/",   "Rock L1",      base_hsv=(0.07, 0.22, 0.68)),
    "bal_rock_L2":       MaterialStyle("#8D6E63", "//",  "Rock L2",      base_hsv=(0.06, 0.25, 0.58)),
    "bal_rock_L3":       MaterialStyle("#6D4C41", "///", "Rock L3",      base_hsv=(0.05, 0.28, 0.48)),

    # Fouling
    "bal_foul":          MaterialStyle("#4B3621", ".",  "Fouling (dense)"),
    "bal_foul_granular": MaterialStyle("#C8A055", ".",  "Fouling"),
    "fouling":           MaterialStyle("#C8A055", ".",  "Fouling"),
    "foul_soil":         MaterialStyle("#B5651D", "xx", "Fouling (heterogeneous)"),

    # Mbubia-style material names (rocks fan-triangulated in the pipeline)
    "clean_ballast":         MaterialStyle(_hsv_hex((0.58, 0.45, 0.80)), None, "Clean Ballast",  base_hsv=(0.58, 0.45, 0.80)),
    "fouled_ballast":        MaterialStyle(_hsv_hex((0.06, 0.55, 0.70)), None, "Fouled Ballast", base_hsv=(0.06, 0.55, 0.70)),
    "highly_fouled_ballast": MaterialStyle(_hsv_hex((0.55, 0.40, 0.35)), None, "Highly Fouled",  base_hsv=(0.55, 0.40, 0.35)),
    "subgrade_soil":         MaterialStyle(_hsv_hex((0.09, 0.50, 0.62)), None, "Subgrade Soil",  base_hsv=(0.09, 0.50, 0.62)),
}

# Graded fouling layers (bal_foul_g1 … bal_foul_g9): generated, not hand-listed
for _i in range(1, 10):
    MATERIALS[f"bal_foul_g{_i}"] = MaterialStyle(
        color=matplotlib.colors.to_hex(plt.cm.YlOrBr(0.3 + _i * 0.07)),
        hatch="." * ((_i % 3) + 1),
        label=f"Foul L{_i}",
    )

# Order materials appear in 2D legends (only materials present in the scene
# are shown; slugs missing from this list never appear in a legend).
LEGEND_ORDER: list[str] = [
    "subgrade", "formation",
    "bal_rock", "bal_rock_L1", "bal_rock_L2", "bal_rock_L3",
    "bal_foul", "bal_foul_granular", "foul_soil",
    *[f"bal_foul_g{i}" for i in range(1, 10)],
    "concrete_sleeper",
]


# ── Lookup & jitter helpers ───────────────────────────────────────────────────

def _derived_color(name: str) -> str:
    """Deterministic muted color for a material not in the registry.

    Hashes the slug to a hue (fixed low saturation / high value) so distinct
    unregistered materials are visually distinguishable, render identically
    across runs, and stay subdued next to registered materials.
    """
    digest = hashlib.md5(name.encode("utf-8")).hexdigest()
    hue = int(digest[:8], 16) / 0xFFFFFFFF
    return matplotlib.colors.to_hex(matplotlib.colors.hsv_to_rgb([hue, 0.25, 0.75]))


def get_style(material: str) -> MaterialStyle:
    """Resolve a material slug to its style.

    Unknown materials degrade gracefully: a deterministic muted color derived
    from the slug (so different unregistered materials are distinguishable),
    no hatch, and the raw slug as label. Register the material in ``MATERIALS``
    to control its appearance.
    """
    style = MATERIALS.get(material)
    if style is not None:
        return style
    return MaterialStyle(_derived_color(material), None, material)


def jitter_color(material: str, rng: np.random.Generator) -> Optional[tuple]:
    """Per-particle tint: the material's ``base_hsv`` plus bounded random
    jitter, as an RGB tuple. Returns None when the material has no
    ``base_hsv`` (caller should fall back to the flat ``color``).

    One call per particle (rock / polygon grain) so each grain gets its own
    tint while staying recognisably the same material.
    """
    style = MATERIALS.get(material)
    if style is None or style.base_hsv is None:
        return None
    h, s, v = style.base_hsv
    return tuple(matplotlib.colors.hsv_to_rgb([
        float(np.clip(h + rng.uniform(-0.05, 0.05), 0, 1)),
        float(np.clip(s + rng.uniform(-0.12, 0.12), 0.05, 1)),
        float(np.clip(v + rng.uniform(-0.20, 0.20), 0.2, 1)),
    ]))

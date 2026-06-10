"""N-layer scene specification for the .in creator.

A :class:`Layer` is one horizontal stratum, ordered bottom -> top. Each layer is
either a flat homogeneous box, or a ``packed`` ballast layer filled with rocks of
a contrasting material sitting in a matrix/void material.

Materials may be given by NAME (resolved from the validated constants in
``MaterialConstants``) or explicitly as ``(eps, sigma)``.

Two input forms are supported (see ``parse_layers`` / ``parse_layers_file``):

  inline string :  "subgrade:0.20, formation:0.10, ballast:0.25:packed"
                   "clay:0.15:12:0.05, ballast:0.25:4:0.001:packed"
  TOML file     :  [[layer]]
                   name = "subgrade"
                   thickness = 0.20
                   [[layer]]
                   name = "ballast"
                   thickness = 0.25
                   packed = true

The ``packed`` flag marks the rock-packed layer: the NAMED material becomes the
ROCK material and the inter-rock matrix defaults to air (``free_space``). This
guarantees rock/matrix dielectric contrast (the painter's-algorithm safeguard:
a rock must never share its material with the box directly beneath it).
"""
from __future__ import annotations

import tomllib
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Tuple, Union

from .constants import MC

# Named material registry -> (eps, sigma). Single source of truth = MaterialConstants.
NAMED_MATERIALS: dict[str, Tuple[float, float]] = {
    "free_space":      MC.AIR_PROPS,
    "air":             MC.AIR_PROPS,
    "subgrade":        MC.SUBGRADE_SOIL_PROPS,
    "subgrade_soil":   MC.SUBGRADE_SOIL_PROPS,
    "formation":       MC.FORMATION_PROPS,
    "ballast":         MC.CLEAN_BALLAST_PROPS,
    "clean_ballast":   MC.CLEAN_BALLAST_PROPS,
    "fouled_ballast":  MC.FOULED_BALLAST_PROPS,
    "highly_fouled_ballast": MC.HF_BALLAST_PROPS,
    "fouling":         MC.FOULING_BASE_PROPS,
    "fouling_dense":   MC.FOULING_DENSE_PROPS,
}

# Default matrix (inter-rock voids) for a packed layer: clean dry ballast = stones
# in air. Override per-layer via TOML (matrix = "fouling") for fouled beds.
DEFAULT_PACKED_MATRIX = "free_space"


@dataclass
class Layer:
    """One horizontal stratum (bottom -> top order).

    For a flat layer ``(eps, sigma)`` is the box material. For a ``packed`` layer
    ``(eps, sigma)`` is the inter-rock MATRIX and ``(rock_eps, rock_sigma)`` is the
    rock/stone material.
    """
    name: str
    thickness: float
    eps: float
    sigma: float
    packed: bool = False
    rock_eps: Optional[float] = None
    rock_sigma: Optional[float] = None
    rock_name: str = "bal_rock"
    matrix_name: str = DEFAULT_PACKED_MATRIX

    def validate(self) -> None:
        if self.thickness <= 0:
            raise ValueError(f"layer '{self.name}': thickness must be > 0, got {self.thickness}")
        if self.eps < 1.0:
            raise ValueError(f"layer '{self.name}': eps must be >= 1, got {self.eps}")
        if self.sigma < 0:
            raise ValueError(f"layer '{self.name}': sigma must be >= 0, got {self.sigma}")
        if self.packed:
            if self.rock_eps is None or self.rock_sigma is None:
                raise ValueError(f"packed layer '{self.name}': rock material undefined")
            if self.rock_eps < 1.0:
                raise ValueError(f"packed layer '{self.name}': rock_eps must be >= 1")
            # Painter's-algorithm safeguard: a rock must contrast with the matrix
            # box drawn beneath it, else the rock is electromagnetically invisible.
            if (abs(self.rock_eps - self.eps) < 1e-9
                    and abs(self.rock_sigma - self.sigma) < 1e-9):
                raise ValueError(
                    f"packed layer '{self.name}': rock material "
                    f"(eps={self.rock_eps}, sigma={self.rock_sigma}) is identical to the "
                    f"matrix material (eps={self.eps}, sigma={self.sigma}). Rocks would have "
                    f"zero contrast and be invisible — give them different materials."
                )


def _resolve_named(name: str) -> Tuple[float, float]:
    key = name.strip().lower()
    if key not in NAMED_MATERIALS:
        raise ValueError(
            f"unknown material name '{name}'. Known: {', '.join(sorted(NAMED_MATERIALS))}. "
            f"Or give explicit eps:sigma."
        )
    return NAMED_MATERIALS[key]


def _layer_from_fields(name: str, thickness: float,
                       eps: Optional[float], sigma: Optional[float],
                       packed: bool, matrix: Optional[str] = None) -> Layer:
    """Build a Layer from already-parsed fields (shared by inline + TOML paths)."""
    if eps is None or sigma is None:
        reps, rsig = _resolve_named(name)
        eps = reps if eps is None else eps
        sigma = rsig if sigma is None else sigma

    if not packed:
        return Layer(name=name, thickness=thickness, eps=float(eps), sigma=float(sigma))

    # Packed: the named/explicit material is the ROCK; matrix defaults to air.
    matrix_name = (matrix or DEFAULT_PACKED_MATRIX).strip().lower()
    meps, msig = _resolve_named(matrix_name)
    return Layer(
        name=name, thickness=thickness,
        eps=float(meps), sigma=float(msig),          # matrix/voids
        packed=True,
        rock_eps=float(eps), rock_sigma=float(sigma), # rocks
        rock_name=f"{name}_rock" if name not in ("ballast", "bal_rock") else "bal_rock",
        matrix_name=matrix_name,
    )


def _parse_inline_token(token: str) -> Layer:
    """Parse one inline layer token: name:thickness[:eps:sigma][:packed]."""
    parts = [p.strip() for p in token.split(":") if p.strip() != ""]
    if len(parts) < 2:
        raise ValueError(f"layer token '{token}' needs at least name:thickness")

    packed = parts[-1].lower() == "packed"
    if packed:
        parts = parts[:-1]

    name = parts[0]
    thickness = float(parts[1])
    eps = sigma = None
    if len(parts) >= 4:
        eps, sigma = float(parts[2]), float(parts[3])
    elif len(parts) == 3:
        raise ValueError(
            f"layer token '{token}': give BOTH eps and sigma (name:thickness:eps:sigma), "
            f"or neither (use a named material)."
        )
    return _layer_from_fields(name, thickness, eps, sigma, packed)


def parse_layers(spec: str) -> List[Layer]:
    """Parse an inline layer spec string (comma-separated, bottom -> top)."""
    tokens = [t for t in spec.split(",") if t.strip() != ""]
    if not tokens:
        raise ValueError("empty layer spec")
    layers = [_parse_inline_token(t) for t in tokens]
    _validate_stack(layers)
    return layers


def parse_layers_file(path: Union[str, Path]) -> List[Layer]:
    """Parse a TOML layer file: an array of ``[[layer]]`` tables, bottom -> top."""
    with open(path, "rb") as fh:
        data = tomllib.load(fh)

    table = data.get("layer")
    if not isinstance(table, list) or not table:
        raise ValueError(
            "layer TOML must contain a non-empty array of [[layer]] tables"
        )

    layers: List[Layer] = []
    for i, obj in enumerate(table):
        if "name" not in obj or "thickness" not in obj:
            raise ValueError(f"[[layer]] #{i}: requires 'name' and 'thickness'")
        layers.append(_layer_from_fields(
            name=obj["name"],
            thickness=float(obj["thickness"]),
            eps=obj.get("eps"),
            sigma=obj.get("sigma"),
            packed=bool(obj.get("packed", False)),
            matrix=obj.get("matrix"),
        ))
    _validate_stack(layers)
    return layers


def _validate_stack(layers: List[Layer]) -> None:
    if not layers:
        raise ValueError("at least one layer is required")
    for layer in layers:
        layer.validate()

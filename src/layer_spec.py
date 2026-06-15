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
    # Per-layer rock packing algorithm (packed layers only). None -> fall back to
    # the scene-level [sim].rock_packing_algorithm / builder default.
    rock_packing_algorithm: Optional[str] = None

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


def _layer_from_table_obj(obj: dict, idx: int) -> Layer:
    """Build one Layer from a [[layer]] TOML table with full per-layer control.

    Recognised keys (all optional except name/thickness):
      name, thickness                         — required
      eps, sigma                              — flat layer: box material;
                                                packed layer: rock material if
                                                rock_eps/rock_sigma absent
      packed = true                           — fill the layer with rocks
      rock_eps, rock_sigma                    — explicit rock material (packed)
      matrix                                  — named matrix material (packed)
      matrix_eps, matrix_sigma               — explicit matrix material (packed)
      rock_packing_algorithm                  — per-layer packer (packed)

    Named materials (NAMED_MATERIALS) are used as fallbacks when a value is
    omitted, so terse specs keep working.
    """
    name = str(obj["name"])
    thickness = float(obj["thickness"])
    packed = bool(obj.get("packed", False))
    algo = obj.get("rock_packing_algorithm")
    algo = str(algo).lower() if algo else None

    if not packed:
        if algo is not None:
            raise ValueError(
                f"[[layer]] #{idx} '{name}': rock_packing_algorithm given on a "
                f"non-packed layer (add packed = true)."
            )
        eps, sigma = obj.get("eps"), obj.get("sigma")
        if eps is None or sigma is None:
            reps, rsig = _resolve_named(name)
            eps = reps if eps is None else float(eps)
            sigma = rsig if sigma is None else float(sigma)
        return Layer(name=name, thickness=thickness, eps=float(eps), sigma=float(sigma))

    # --- packed layer: resolve ROCK material then MATRIX material ---
    rock_eps = obj.get("rock_eps", obj.get("eps"))
    rock_sigma = obj.get("rock_sigma", obj.get("sigma"))
    if rock_eps is None or rock_sigma is None:
        reps, rsig = _resolve_named(name)
        rock_eps = reps if rock_eps is None else float(rock_eps)
        rock_sigma = rsig if rock_sigma is None else float(rock_sigma)

    if "matrix_eps" in obj or "matrix_sigma" in obj:
        meps = float(obj["matrix_eps"])
        msig = float(obj.get("matrix_sigma", 0.0))
        matrix_name = str(obj.get("matrix", f"{name}_matrix")).strip().lower()
    else:
        matrix_name = str(obj.get("matrix", DEFAULT_PACKED_MATRIX)).strip().lower()
        meps, msig = _resolve_named(matrix_name)

    return Layer(
        name=name, thickness=thickness,
        eps=float(meps), sigma=float(msig),               # matrix/voids
        packed=True,
        rock_eps=float(rock_eps), rock_sigma=float(rock_sigma),  # rocks
        rock_name=f"{name}_rock" if name not in ("ballast", "bal_rock") else "bal_rock",
        matrix_name=matrix_name,
        rock_packing_algorithm=algo,
    )


def _layers_from_table(table) -> List[Layer]:
    """Build + validate the layer stack from an array of [[layer]] tables."""
    if not isinstance(table, list) or not table:
        raise ValueError(
            "layer TOML must contain a non-empty array of [[layer]] tables"
        )
    layers: List[Layer] = []
    for i, obj in enumerate(table):
        if "name" not in obj or "thickness" not in obj:
            raise ValueError(f"[[layer]] #{i}: requires 'name' and 'thickness'")
        layers.append(_layer_from_table_obj(obj, i))
    _validate_stack(layers)
    return layers


def parse_layers_file(path: Union[str, Path]) -> List[Layer]:
    """Parse a TOML layer file: an array of ``[[layer]]`` tables, bottom -> top."""
    with open(path, "rb") as fh:
        data = tomllib.load(fh)
    return _layers_from_table(data.get("layer"))


@dataclass
class SceneConfig:
    """A complete scene config parsed from a TOML file.

    ``sim`` and ``source`` are the raw ``[sim]`` / ``[source]`` tables;
    ``lab`` is the ``[lab]`` ground-truth table (fouling_class, lab measurements, etc.);
    ``raw_commands`` are passthrough gprMax commands from ``[[command]]`` (raw=...);
    ``toml_text`` is the original file text for reproducibility.
    """
    layers: List[Layer]
    sim: dict = field(default_factory=dict)
    source: dict = field(default_factory=dict)
    lab: dict = field(default_factory=dict)
    raw_commands: List[str] = field(default_factory=list)
    toml_text: str = ""


def parse_config_file(path: Union[str, Path]) -> SceneConfig:
    """Parse a full scene-config TOML: [sim], [source], [lab], [[layer]], [[command]]."""
    path = Path(path)
    text = path.read_text()
    with open(path, "rb") as fh:
        data = tomllib.load(fh)

    layers = _layers_from_table(data.get("layer"))

    raw_commands: List[str] = []
    for i, cmd in enumerate(data.get("command", [])):
        if "raw" not in cmd:
            raise ValueError(f"[[command]] #{i}: requires a 'raw' string")
        raw_commands.append(str(cmd["raw"]))

    return SceneConfig(
        layers=layers,
        sim=data.get("sim", {}) or {},
        source=data.get("source", {}) or {},
        lab=dict(data.get("scenario", {})) if "scenario" in data else {},  # [scenario] → stored as lab for .in header
        raw_commands=raw_commands,
        toml_text=text,
    )


def _validate_stack(layers: List[Layer]) -> None:
    if not layers:
        raise ValueError("at least one layer is required")
    for layer in layers:
        layer.validate()

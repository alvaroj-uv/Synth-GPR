"""SceneModel: pure data representations for scenes and a TOML parser.

This module provides small dataclasses that represent the scene (layers, targets,
metadata) and a helper to parse existing TOML scene files into the SceneModel.
The goal is to centralize data validation and decouple parsing from builders
and exporters.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Any
import toml


@dataclass
class LayerSpec:
    name: str
    thickness: float
    permittivity: float
    conductivity: float = 0.0
    extra: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SceneModel:
    frequency: float
    layers: List[LayerSpec] = field(default_factory=list)
    targets: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


def parse_toml(path: str) -> SceneModel:
    """Load a TOML scene file and return a SceneModel instance.

    The parser is intentionally conservative: it extracts a few well-known
    fields (frequency, layers, targets) and preserves any extra keys in
    metadata for downstream components.
    """
    data = toml.load(path)

    freq = data.get("frequency") or data.get("f0") or data.get("f")
    if freq is None:
        raise ValueError(f"Scene TOML at {path} is missing a frequency field")

    raw_layers = data.get("layers", [])
    layers = []
    for i, l in enumerate(raw_layers):
        name = l.get("name") or f"layer_{i}"
        thickness = float(l.get("thickness", 0.0))
        perm = float(l.get("permittivity", l.get("epsr", 1.0)))
        cond = float(l.get("conductivity", 0.0))
        extra = {k: v for k, v in l.items() if k not in {"name", "thickness", "permittivity", "epsr", "conductivity"}}
        layers.append(LayerSpec(name=name, thickness=thickness, permittivity=perm, conductivity=cond, extra=extra))

    targets = data.get("targets", []) or []

    metadata = {k: v for k, v in data.items() if k not in {"frequency", "f0", "f", "layers", "targets"}}

    return SceneModel(frequency=float(freq), layers=layers, targets=targets, metadata=metadata)

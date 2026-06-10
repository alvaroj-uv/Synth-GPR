"""Exporter adapters for scene serialization.

Provides a simple Exporter interface and a JSONExporter that writes a
SceneModel to a JSON file. Real project exporters (for simulator inputs)
should implement the same interface.
"""
from typing import Protocol
import json
from dataclasses import asdict


class Exporter(Protocol):
    def export(self, scene, path: str) -> None:
        ...


class JSONExporter:
    def export(self, scene, path: str) -> None:
        # scene is expected to be dataclass-like; use asdict if possible
        try:
            payload = asdict(scene)
        except Exception:
            # Fallback: try to use __dict__
            payload = getattr(scene, "__dict__", scene)

        with open(path, "w") as fh:
            json.dump(payload, fh, indent=2)

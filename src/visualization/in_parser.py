from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional
import json


@dataclass
class BoxGeom:
    x1: float
    y1: float
    x2: float
    y2: float
    material: str


@dataclass
class CylinderGeom:
    x: float
    y: float
    radius: float
    material: str


@dataclass
class AntennaPos:
    x: float
    y: float


@dataclass
class SceneData:
    domain_x: float = 0.0
    domain_y: float = 0.0
    title: str = ""
    boxes: list = field(default_factory=list)        # list[BoxGeom]
    cylinders: list = field(default_factory=list)    # list[CylinderGeom]
    tx: Optional[AntennaPos] = None
    rx: Optional[AntennaPos] = None
    meta: dict = field(default_factory=dict)


def parse_in_file(path: Path) -> SceneData:
    """
    Parse a gprMax .in file and return structured SceneData.

    Handles:
      - #domain, #title, #box, #cylinder, #hertzian_dipole, #rx
      - ## key: value metadata comments (JSON-decoded when possible)
    """
    scene = SceneData()

    with open(path, encoding="utf-8", errors="replace") as fh:
        for raw in fh:
            line = raw.strip()
            if not line:
                continue

            # Metadata from "## key: value" header comments
            if line.startswith("## ") and ":" in line:
                key, _, val = line[3:].partition(":")
                k = key.strip()
                v = val.strip()
                try:
                    scene.meta[k] = json.loads(v)
                except (json.JSONDecodeError, ValueError):
                    scene.meta[k] = v
                continue

            if not line.startswith("#"):
                continue

            tokens = line.split()
            if not tokens:
                continue
            cmd = tokens[0]

            if cmd == "#title:":
                scene.title = " ".join(tokens[1:])

            elif cmd == "#domain:":
                scene.domain_x = float(tokens[1])
                scene.domain_y = float(tokens[2])

            elif cmd == "#box:":
                # #box: x1 y1 z1 x2 y2 z2 material
                scene.boxes.append(BoxGeom(
                    x1=float(tokens[1]), y1=float(tokens[2]),
                    x2=float(tokens[4]), y2=float(tokens[5]),
                    material=tokens[7],
                ))

            elif cmd == "#cylinder:":
                # #cylinder: x1 y1 z1 x2 y2 z2 radius material
                scene.cylinders.append(CylinderGeom(
                    x=float(tokens[1]), y=float(tokens[2]),
                    radius=float(tokens[7]),
                    material=tokens[8],
                ))

            elif cmd == "#hertzian_dipole:":
                # #hertzian_dipole: polarisation x y z waveform_id
                scene.tx = AntennaPos(x=float(tokens[2]), y=float(tokens[3]))

            elif cmd == "#rx:":
                # #rx: x y z
                scene.rx = AntennaPos(x=float(tokens[1]), y=float(tokens[2]))

    return scene

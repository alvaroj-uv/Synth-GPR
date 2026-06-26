"""
gprMax .in file parser → SceneData (single 2D + 3D geometry parser).

One handler per gprMax command (``_HANDLERS``). To support a new command, add
a ``_parse_<cmd>(scene, tokens)`` function and register it — do not extend a
monolithic if/elif chain. Any handler failure (bad token count, non-numeric
value) is re-raised as ``InFileParseError`` carrying ``{file}:{lineno}: {line}``
so a malformed .in file points at the offending line instead of a bare
IndexError deep in the stack.
"""

from __future__ import annotations

import re
from pathlib import Path

from ..file_reader import parse_metadata_comments
from ..data_access import INFileReader
from .model import (
    AntennaPos,
    BoxGeom,
    CylinderGeom,
    PolygonGeom,
    SceneData,
    SphereGeom,
    TriangleGeom,
)


class InFileParseError(ValueError):
    """A .in line could not be parsed. Message format: ``{file}:{lineno}: {line}``."""


# ── Per-command handlers ──────────────────────────────────────────────────────
# Each takes (scene, tokens) where tokens[0] is the command itself.

def _parse_title(scene: SceneData, tokens: list[str]) -> None:
    scene.title = " ".join(tokens[1:])


def _parse_domain(scene: SceneData, tokens: list[str]) -> None:
    scene.domain_x = float(tokens[1])
    scene.domain_y = float(tokens[2])
    if len(tokens) > 3:
        scene.domain_z = float(tokens[3])


def _parse_box(scene: SceneData, tokens: list[str]) -> None:
    # #box: x1 y1 z1 x2 y2 z2 material
    scene.boxes.append(BoxGeom(
        x1=float(tokens[1]), y1=float(tokens[2]), z1=float(tokens[3]),
        x2=float(tokens[4]), y2=float(tokens[5]), z2=float(tokens[6]),
        material=tokens[7],
    ))


def _parse_fractal_box(scene: SceneData, tokens: list[str]) -> None:
    # #fractal_box: x1 y1 z1 x2 y2 z2 frac_dim wx wy wz n_mat soil box_id [seed]
    # Rendered like a box of its soil material (heterogeneous fill).
    scene.boxes.append(BoxGeom(
        x1=float(tokens[1]), y1=float(tokens[2]), z1=float(tokens[3]),
        x2=float(tokens[4]), y2=float(tokens[5]), z2=float(tokens[6]),
        material=tokens[12],
    ))


def _parse_triangle(scene: SceneData, tokens: list[str]) -> None:
    # #triangle: x1 y1 z1 x2 y2 z2 x3 y3 z3 thickness material
    material = tokens[11] if len(tokens) > 11 else tokens[10]
    scene.triangles.append(TriangleGeom(
        x1=float(tokens[1]), y1=float(tokens[2]),
        x2=float(tokens[4]), y2=float(tokens[5]),
        x3=float(tokens[7]), y3=float(tokens[8]),
        material=material,
        z1=float(tokens[3]), z2=float(tokens[6]), z3=float(tokens[9]),
    ))


def _parse_sphere(scene: SceneData, tokens: list[str]) -> None:
    # #sphere: x y z radius material
    scene.spheres.append(SphereGeom(
        x=float(tokens[1]), y=float(tokens[2]), z=float(tokens[3]),
        radius=float(tokens[4]), material=tokens[5],
    ))


def _parse_cylinder(scene: SceneData, tokens: list[str]) -> None:
    # #cylinder: x1 y1 z1 x2 y2 z2 radius material
    scene.cylinders.append(CylinderGeom(
        x1=float(tokens[1]), y1=float(tokens[2]), z1=float(tokens[3]),
        x2=float(tokens[4]), y2=float(tokens[5]), z2=float(tokens[6]),
        radius=float(tokens[7]),
        material=tokens[8],
    ))


def _parse_polygon(scene: SceneData, tokens: list[str]) -> None:
    # #polygon: n_vertices x1 y1 z1 x2 y2 z2 ... material
    n = int(tokens[1])
    verts = [(float(tokens[2 + i*3]), float(tokens[3 + i*3])) for i in range(n)]
    material = tokens[2 + n*3]
    scene.polygons.append(PolygonGeom(vertices=verts, material=material))


def _parse_hertzian_dipole(scene: SceneData, tokens: list[str]) -> None:
    # #hertzian_dipole: polarisation x y z waveform_id
    scene.tx = AntennaPos(x=float(tokens[2]), y=float(tokens[3]),
                          z=float(tokens[4]))


def _parse_rx(scene: SceneData, tokens: list[str]) -> None:
    # #rx: x y z
    scene.receivers.append(AntennaPos(
        x=float(tokens[1]), y=float(tokens[2]), z=float(tokens[3]),
    ))


_HANDLERS = {
    "#title:":           _parse_title,
    "#domain:":          _parse_domain,
    "#box:":             _parse_box,
    "#fractal_box:":     _parse_fractal_box,
    "#triangle:":        _parse_triangle,
    "#sphere:":          _parse_sphere,
    "#cylinder:":        _parse_cylinder,
    "#polygon:":         _parse_polygon,
    "#hertzian_dipole:": _parse_hertzian_dipole,
    "#rx:":              _parse_rx,
}


def _parse_antenna_call(scene: SceneData, line: str) -> None:
    """Antenna inserted via a #python block: the ``antenna_like_GSSI(...)``
    call line does NOT start with '#'. Draw a stand-in case box + tx marker
    from the call args (used by the 3D views)."""
    args = re.findall(r"-?\d+\.?\d*(?:e-?\d+)?", line.split("(", 1)[1])
    if len(args) >= 3:
        cx, cy, zs = float(args[0]), float(args[1]), float(args[2])
        case = (0.300, 0.300, 0.178) if "400" in line else (0.170, 0.108, 0.045)
        scene.boxes.append(BoxGeom(
            x1=cx - case[0] / 2, y1=cy - case[1] / 2, z1=zs,
            x2=cx + case[0] / 2, y2=cy + case[1] / 2, z2=zs + case[2],
            material="antenna",
        ))
        scene.tx = AntennaPos(x=cx, y=cy, z=zs)


def parse_in_file(path: Path) -> SceneData:
    """Parse a gprMax .in file into SceneData.

    Handles: #domain, #title, #box, #fractal_box, #triangle, #cylinder,
    #sphere, #polygon, #hertzian_dipole, #rx, the ``antenna_like_GSSI(...)``
    python-call line, and ``## key: value`` metadata comments (JSON-decoded
    via ``file_reader.parse_metadata_comments``). Z-coordinates are captured
    so the same SceneData drives both the 2D projection and the 3D
    orthographic views.

    Raises:
        InFileParseError: a recognised command line is malformed; the message
            pinpoints it as ``{file}:{lineno}: {line}``.
    """
    scene = SceneData()
    lines = INFileReader().read(path, as_lines=True)

    scene.meta = parse_metadata_comments(lines)

    for lineno, raw in enumerate(lines, start=1):
        line = raw.strip()
        if not line:
            continue
        try:
            if line.startswith("antenna_like_GSSI"):
                _parse_antenna_call(scene, line)
                continue
            if not line.startswith("#"):
                continue
            tokens = line.split()
            handler = _HANDLERS.get(tokens[0])
            if handler is not None:
                handler(scene, tokens)
        except Exception as exc:
            raise InFileParseError(f"{path}:{lineno}: {line}") from exc

    return scene

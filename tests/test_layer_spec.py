#!/usr/bin/env python3
"""
Unit tests for the N-layer .in creator:
  - src.layer_spec        (Layer parsing: inline + JSON, named/explicit, validation)
  - src.layer_scene_builder (flat-layer .in assembly)

The packed-layer path runs the pymunk physics packer (slow, non-deterministic),
so it is exercised by the demo/integration script, not these fast unit tests.
"""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.constants import MC
from src.layer_spec import Layer, parse_layers, parse_layers_file
from src.layer_scene_builder import SceneParams, build_scene_commands


# --------------------------------------------------------------------------- #
# Parsing — inline
# --------------------------------------------------------------------------- #
def test_inline_named_layers():
    layers = parse_layers("subgrade:0.20, formation:0.10, ballast:0.25:packed")
    assert [l.name for l in layers] == ["subgrade", "formation", "ballast"]
    assert layers[0].thickness == 0.20 and not layers[0].packed
    assert layers[0].eps == MC.SUBGRADE_SOIL_PROPS[0]
    assert layers[1].eps == MC.FORMATION_PROPS[0]
    # packed ballast: named material becomes the ROCK; matrix defaults to air
    bal = layers[2]
    assert bal.packed
    assert bal.rock_eps == MC.CLEAN_BALLAST_PROPS[0]
    assert bal.eps == MC.AIR_PROPS[0]            # matrix = air
    assert bal.matrix_name == "free_space"


def test_inline_explicit_eps_sigma():
    layers = parse_layers("clay:0.15:12:0.05")
    assert layers[0].eps == 12.0 and layers[0].sigma == 0.05
    assert not layers[0].packed


def test_inline_explicit_packed():
    layers = parse_layers("ballast:0.25:4:0.001:packed")
    bal = layers[0]
    assert bal.packed and bal.rock_eps == 4.0 and bal.rock_sigma == 0.001
    assert bal.eps == MC.AIR_PROPS[0]            # matrix still air


# --------------------------------------------------------------------------- #
# Validation
# --------------------------------------------------------------------------- #
def test_same_material_under_rock_rejected():
    """Painter's-algorithm safeguard: rock material == matrix -> error."""
    with pytest.raises(ValueError, match="zero contrast|identical"):
        # rock = air(1,0), matrix = air -> identical
        parse_layers("air:0.25:1:0:packed")


def test_bad_thickness_rejected():
    with pytest.raises(ValueError, match="thickness"):
        parse_layers("subgrade:0")


def test_unknown_material_rejected():
    with pytest.raises(ValueError, match="unknown material"):
        parse_layers("unobtanium:0.20")


def test_three_field_token_rejected():
    with pytest.raises(ValueError, match="BOTH eps and sigma"):
        parse_layers("clay:0.15:12")


# --------------------------------------------------------------------------- #
# Parsing — TOML file
# --------------------------------------------------------------------------- #
def test_toml_file(tmp_path):
    toml = """
# a 3-layer stack (comments are exactly why we use TOML)
[[layer]]
name = "subgrade"
thickness = 0.2

[[layer]]
name = "clay"
thickness = 0.15
eps = 12
sigma = 0.05

[[layer]]
name = "ballast"
thickness = 0.25
packed = true
matrix = "fouling"
"""
    f = tmp_path / "layers.toml"
    f.write_text(toml)
    layers = parse_layers_file(f)
    assert len(layers) == 3
    assert layers[1].eps == 12.0
    bal = layers[2]
    assert bal.packed and bal.matrix_name == "fouling"
    assert bal.eps == MC.FOULING_BASE_PROPS[0]        # matrix = fouling
    assert bal.rock_eps == MC.CLEAN_BALLAST_PROPS[0]  # rock = ballast


def test_toml_missing_layer_array_rejected(tmp_path):
    f = tmp_path / "bad.toml"
    f.write_text('title = "no layers here"\n')
    with pytest.raises(ValueError, match="array of \\[\\[layer\\]\\]"):
        parse_layers_file(f)


# --------------------------------------------------------------------------- #
# Flat-layer builder (no pymunk)
# --------------------------------------------------------------------------- #
def test_flat_builder_structure():
    layers = parse_layers("subgrade:0.20, formation:0.10, sand:0.25:9:0.01")
    lines = build_scene_commands(layers, SceneParams(freq_hz=400e6, domain_x=1.0))
    text = "\n".join(lines)

    # exactly one source + one receiver (single monostatic dipole)
    assert text.count("#hertzian_dipole:") == 1
    assert text.count("#rx:") == 1
    assert text.count("#waveform:") == 1
    assert text.count("#domain:") == 1
    assert text.count("#dx_dy_dz:") == 1
    assert text.count("#time_window:") == 1

    # 3 distinct materials (free_space is built-in, not emitted)
    assert text.count("#material:") == 3
    # air box + one box per flat layer = 4
    assert text.count("#box:") == 4
    # no rocks for an all-flat scene
    assert text.count("#cylinder:") == 0


def test_flat_builder_domain_height():
    layers = parse_layers("subgrade:0.20, formation:0.10, ballast_box:0.25:4:0.001")
    params = SceneParams(freq_hz=400e6, domain_x=1.0, antenna_clearance=0.5, air_buffer=0.1)
    lines = build_scene_commands(layers, params)
    domain_line = next(l for l in lines if l.startswith("#domain:"))
    # subsurface 0.55 + clearance 0.5 + buffer 0.1 = 1.15 m tall
    y = float(domain_line.split()[2])
    assert abs(y - 1.15) < 1e-6


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))

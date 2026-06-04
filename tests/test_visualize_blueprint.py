#!/usr/bin/env python3
"""
Regression tests for the consolidated visualizer (`unified_visualizer.py`).

The old `visualize_gprmax_blueprint.py` monolith was refactored into the
`src/visualization/` package plus the `unified_visualizer.py` CLI, and the
2D/3D dispatch from the former `render_in_file.py` was merged into it. These
tests guard that 2D and 3D `.in` files both render a geometry PNG through the
single entry point.
"""

import sys
from pathlib import Path

import pytest
import matplotlib

matplotlib.use("Agg")

# Project root on path so `src.*` imports inside the visualizer resolve.
sys.path.insert(0, str(Path(__file__).parent.parent))
# Visualizer dir on path so it can import its sibling `render_3d_in_file`.
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts" / "visualization"))

from scripts.visualization import unified_visualizer as uv


SAMPLE_2D = """#title: Test 2D Scenario
#domain: 0.5 1.5 0.005
#material: 8 0.02 subgrade
#material: 10 0.03 formation
#box: 0.0 0.0 0.0 0.5 0.3 0.005 subgrade
#box: 0.0 0.3 0.0 0.5 0.4 0.005 formation
#waveform: ricker 1 4e+08 my_wave
#hertzian_dipole: z 0.3 1.434 0.0025 my_wave
#rx: 0.35 1.434 0.0025
## FI (%): 15.5
## FI_class: Clean
## Lab_Class: Clean
"""

SAMPLE_3D = """#title: Test 3D Scenario
#domain: 2.0 1.15 0.4
#box: 0.0 0.0 0.0 2.0 0.3 0.4 subgrade
#box: 0.0 0.3 0.0 2.0 0.5 0.4 formation
#sphere: 1.0 0.8 0.2 0.05 bal_rock
#sphere: 1.2 0.7 0.2 0.04 bal_rock
#hertzian_dipole: z 1.0 1.1 0.2 my_wave
#rx: 1.05 1.1 0.2
## Lab_Class: Fouled
"""


@pytest.fixture
def sample_2d(tmp_path):
    f = tmp_path / "scene_2d.in"
    f.write_text(SAMPLE_2D)
    return f


@pytest.fixture
def sample_3d(tmp_path):
    f = tmp_path / "scene_3d.in"
    f.write_text(SAMPLE_3D)
    return f


class TestDetect3D:
    def test_2d_not_detected_as_3d(self, sample_2d):
        assert uv.detect_3d_file(sample_2d) is False

    def test_3d_detected(self, sample_3d):
        assert uv.detect_3d_file(sample_3d) is True


class TestGeometryRendering:
    def test_render_2d_geometry(self, sample_2d, tmp_path):
        out_png = tmp_path / "out_2d.png"
        uv.visualize_geometry_only(sample_2d, out_png, dpi=80)
        assert out_png.exists() and out_png.stat().st_size > 0

    def test_render_3d_geometry_via_dispatch(self, sample_3d, tmp_path):
        out_png = tmp_path / "out_3d.png"
        # Goes through the merged 3D dispatch path.
        uv.visualize_geometry_only(sample_3d, out_png, dpi=80)
        assert out_png.exists() and out_png.stat().st_size > 0


class Test3DParser:
    def test_parser_reads_spheres_and_domain(self, sample_3d):
        from render_3d_in_file import parse_3d_in_file

        data = parse_3d_in_file(sample_3d)
        assert len(data["spheres"]) == 2
        assert data["domain"]["x"] == pytest.approx(2.0)
        assert data["domain"]["z"] == pytest.approx(0.4)
        assert data["metadata"]["Lab_Class"] == "Fouled"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

#!/usr/bin/env python3
"""
Phase 2 guardrails: one .in parser (src.visualization.parser.parse_in_file) for
both 2D and 3D, plus the shared metadata substrate
(src.file_reader.parse_metadata_comments). See
docs/architecture/IO_CONSOLIDATION_PLAN.md.
"""

import sys
from pathlib import Path

import pytest
import matplotlib
matplotlib.use("Agg")

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.file_reader import parse_metadata_comments, parse_metadata_file
from src.visualization.model import AbstractGeom, SceneData, SphereGeom
from src.visualization.parser import parse_in_file


SAMPLE_2D = """#title: 2D
#domain: 0.5 1.5 0.005
#box: 0.0 0.0 0.0 0.5 0.3 0.005 subgrade
#box: 0.0 0.3 0.0 0.5 0.4 0.005 formation
#cylinder: 0.25 0.6 0.0 0.25 0.6 0.005 0.03 bal_rock
#hertzian_dipole: z 0.3 1.434 0.0025 w
#rx: 0.35 1.434 0.0025
## pvc: 12.5
## Lab_Class: Clean
## FI (%): 8.0
"""

SAMPLE_3D = """#title: 3D
#domain: 2.0 1.15 0.4
#box: 0.0 0.0 0.0 2.0 0.3 0.4 subgrade
#sphere: 1.0 0.8 0.2 0.05 bal_rock
#sphere: 1.2 0.7 0.2 0.04 bal_rock
#rx: 1.05 1.1 0.2
## Lab_Class: Fouled
"""

# .in using the antenna_like_GSSI python-call line (no #hertzian_dipole)
SAMPLE_ANTENNA = """#domain: 1.0 1.0 0.4
#box: 0.0 0.0 0.0 1.0 0.3 0.4 subgrade
antenna_like_GSSI_400(0.5, 0.5, 0.002, resolution=0.001)
#rx: 0.6 0.5 0.002
## Lab_Class: Clean
"""


def _write(tmp_path, text, name="s.in"):
    p = tmp_path / name
    p.write_text(text)
    return p


class TestMetadataHelper:
    def test_json_decoding_and_strings(self):
        meta = parse_metadata_comments([
            "## pvc: 12.5", "## n: 3", "## flag: true",
            "## Lab_Class: Clean", "## FI (%): 8.0", "#box: ...",
        ])
        assert meta["pvc"] == 12.5
        assert meta["n"] == 3
        assert meta["flag"] is True
        assert meta["Lab_Class"] == "Clean"
        assert meta["FI (%)"] == 8.0
        assert "#box" not in meta

    def test_file_wrapper(self, tmp_path):
        p = _write(tmp_path, SAMPLE_2D)
        meta = parse_metadata_file(p)
        assert meta["Lab_Class"] == "Clean"
        assert meta["pvc"] == 12.5


class TestParse2D:
    def test_geometry_and_meta(self, tmp_path):
        s = parse_in_file(_write(tmp_path, SAMPLE_2D))
        assert isinstance(s, SceneData)
        assert (s.domain_x, s.domain_y, s.domain_z) == pytest.approx((0.5, 1.5, 0.005))
        assert len(s.boxes) == 2 and len(s.cylinders) == 1
        # z captured on boxes even for a 2D scene
        assert s.boxes[0].z2 == pytest.approx(0.005)
        assert all(isinstance(g, AbstractGeom) for g in s.geometries)
        assert all(hasattr(g, attr) for g in s.geometries for attr in ("x", "y", "z"))
        assert s.boxes[0].xyz == pytest.approx((0.25, 0.15, 0.0025))
        assert s.cylinders[0].xyz == pytest.approx((0.25, 0.6, 0.0025))
        assert s.tx.x == pytest.approx(0.3) and s.tx.z == pytest.approx(0.0025)
        assert len(s.receivers) == 1 and s.receivers[0].z == pytest.approx(0.0025)
        assert s.meta["pvc"] == 12.5 and not s.spheres


class TestParse3D:
    def test_spheres_boxes_meta(self, tmp_path):
        s = parse_in_file(_write(tmp_path, SAMPLE_3D))
        assert len(s.spheres) == 2
        assert all(isinstance(sp, SphereGeom) for sp in s.spheres)
        assert s.spheres[0].radius == pytest.approx(0.05)
        assert s.boxes[0].z2 == pytest.approx(0.4)
        assert s.domain_z == pytest.approx(0.4)
        assert s.meta["Lab_Class"] == "Fouled"

    def test_antenna_like_gssi(self, tmp_path):
        s = parse_in_file(_write(tmp_path, SAMPLE_ANTENNA))
        # stand-in antenna box + tx synthesized from the call args
        assert s.tx is not None
        assert s.tx.x == pytest.approx(0.5) and s.tx.z == pytest.approx(0.002)
        assert any(b.material == "antenna" for b in s.boxes)

    def test_renders_via_render_3d_views(self, tmp_path):
        from src.visualization.scene_3d import render_3d_views
        s = parse_in_file(_write(tmp_path, SAMPLE_3D))
        fig = render_3d_views(s, title="t", dpi=80)
        out = tmp_path / "v.png"
        fig.savefig(out)
        assert out.exists() and out.stat().st_size > 0


class TestRepositoryUsesHelper:
    def test_extract_metadata_fi_class(self, tmp_path):
        from src.repositories.filesystem_repository import FileSystemSceneRepository
        repo = FileSystemSceneRepository(tmp_path)
        md = repo._extract_metadata_from_in_file(
            "s_0001", "## FI (%): 10.5\n## FI_class: Moderately Fouled\n#box: x\n")
        assert md is not None
        assert md.fi == pytest.approx(10.5)
        assert md.classification == "Moderately Fouled"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

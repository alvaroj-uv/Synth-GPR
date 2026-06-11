"""
PNG output tests for the rendering facade (src.visualization.render).

Covers what test_visualize_blueprint.py does not:
  - title/metadata annotations on render_geometry_png
  - MC/LDCP research overlays (drawn + legend entry)
  - PNG file integrity (magic bytes)
  - the generate_in_files.py --render pipeline integration (TOML -> .in -> PNG)
"""

import subprocess
import sys
from pathlib import Path

import pytest
import matplotlib

matplotlib.use("Agg")

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.visualization.parser import parse_in_file
from src.visualization.render import render_geometry_png

PNG_MAGIC = b"\x89PNG\r\n\x1a\n"

SAMPLE_2D = """#title: PNG Test Scenario
#domain: 0.5 1.5 0.005
#material: 8 0.02 1 0 subgrade
#material: 5 0.001 1 0 bal_rock
#box: 0.0 0.0 0.0 0.5 0.3 0.005 subgrade
#triangle: 0.25 0.5 0.0 0.20 0.45 0.0 0.30 0.45 0.0 0.005 bal_rock
#waveform: ricker 1 4e+08 my_wave
#hertzian_dipole: z 0.3 1.434 0.0025 my_wave
#rx: 0.35 1.434 0.0025
## Lab_Class: Clean
"""


@pytest.fixture
def sample_in(tmp_path):
    f = tmp_path / "scene.in"
    f.write_text(SAMPLE_2D)
    return f


def _assert_valid_png(path: Path):
    assert path.exists(), f"PNG not written: {path}"
    data = path.read_bytes()
    assert data[:8] == PNG_MAGIC, "file is not a valid PNG"
    assert len(data) > 1000, "PNG suspiciously small"


class TestRenderGeometryPng:
    def test_basic_png_is_valid(self, sample_in, tmp_path):
        out = tmp_path / "basic.png"
        result = render_geometry_png(sample_in, out, dpi=80)
        assert result == out
        _assert_valid_png(out)

    def test_title_and_metadata_annotations(self, sample_in, tmp_path):
        out = tmp_path / "annotated.png"
        render_geometry_png(
            sample_in, out, dpi=80,
            title="Custom Title\nSecond Line",
            metadata="Freq: 400 MHz\nMonostatic",
        )
        _assert_valid_png(out)
        # The annotated figure must differ from the bare one
        bare = tmp_path / "bare.png"
        render_geometry_png(sample_in, bare, dpi=80)
        assert out.read_bytes() != bare.read_bytes()

    def test_creates_missing_output_dirs(self, sample_in, tmp_path):
        out = tmp_path / "nested" / "dirs" / "scene.png"
        render_geometry_png(sample_in, out, dpi=80)
        _assert_valid_png(out)


class TestResearchOverlays:
    def test_overlays_drawn_and_legend_extended(self, sample_in):
        import matplotlib.pyplot as plt
        from src.visualization.drawing import draw_geometry
        from src.visualization.overlays import draw_research_overlays

        scene = parse_in_file(sample_in)
        scene.meta.update({
            "mc_y_min": 0.35, "mc_y_max": 0.50,
            "ballast_bottom_y": 0.30, "ballast_top_y": 0.56,
            "ldcp_x": 0.25,
        })
        fig, ax = plt.subplots()
        draw_geometry(ax, scene)
        n_before = len(ax.patches)
        draw_research_overlays(ax, scene)
        # Two overlay rectangles added (sieve box + MC ballast box)
        assert len(ax.patches) == n_before + 2
        labels = [t.get_text() for t in ax.get_legend().get_texts()]
        assert "MC sampling box" in labels
        plt.close(fig)

    def test_overlays_noop_without_meta_keys(self, sample_in):
        import matplotlib.pyplot as plt
        from src.visualization.drawing import draw_geometry
        from src.visualization.overlays import draw_research_overlays

        scene = parse_in_file(sample_in)
        fig, ax = plt.subplots()
        draw_geometry(ax, scene)
        n_before = len(ax.patches)
        labels_before = [t.get_text() for t in ax.get_legend().get_texts()]
        draw_research_overlays(ax, scene)
        assert len(ax.patches) == n_before
        labels_after = [t.get_text() for t in ax.get_legend().get_texts()]
        assert labels_after == labels_before
        plt.close(fig)


class TestPipelineRenderFlag:
    """generate_in_files.py --render must produce a PNG next to the .in.

    Uses the minimal single-layer TOML (no packed layer) so the run is fast.
    """

    TOML = PROJECT_ROOT / "examples" / "scenes" / "test_minimal_single_layer.toml"

    def test_render_flag_produces_png(self, tmp_path):
        out_in = tmp_path / "minimal.in"
        result = subprocess.run(
            [sys.executable, "scripts/pipeline/generate_in_files.py",
             str(out_in), "--layers-file", str(self.TOML), "--render"],
            capture_output=True, text=True, cwd=str(PROJECT_ROOT),
            timeout=120,
        )
        assert result.returncode == 0, result.stderr
        assert out_in.exists(), "pipeline did not write the .in file"
        assert "[WARN] Could not render PNG" not in result.stdout, result.stdout
        _assert_valid_png(out_in.with_suffix(".png"))


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

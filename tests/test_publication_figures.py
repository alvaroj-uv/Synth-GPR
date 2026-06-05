"""
Tests for publication-quality figure export

Tests:
- High-quality figure saving (PNG, PDF, SVG)
- Scene cross-section generation
- Comparison figures
- Grid layouts
- Metadata formatting
"""

import tempfile
from pathlib import Path
import pytest

from src.visualization.publication_figures import (
    PublicationFigureGenerator,
    apply_publication_style,
    export_scene_as_pdf,
    export_scene_as_svg,
    _format_metadata_box,
)
from src.visualization.scene import parse_in_file


@pytest.fixture
def temp_output_dir():
    """Create temporary output directory for tests"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_in_file():
    """Provide path to a sample .in file for testing"""
    # This would normally be a fixture in conftest.py
    # For now, we'll skip if no sample exists
    sample_path = Path(__file__).parent.parent / "sample_data" / "sample_scene.in"
    if not sample_path.exists():
        pytest.skip("Sample .in file not found")
    return sample_path


class TestPublicationFigureGenerator:
    """Test suite for PublicationFigureGenerator"""

    def test_initialization(self):
        """Test that the class initializes correctly"""
        gen = PublicationFigureGenerator()
        assert gen is not None

    def test_apply_publication_style(self):
        """Test that publication style can be applied"""
        try:
            apply_publication_style()
            assert True
        except Exception as e:
            pytest.fail(f"apply_publication_style failed: {e}")

    def test_format_metadata_box_empty(self):
        """Test metadata formatting with empty dict"""
        result = _format_metadata_box({})
        assert result == ""

    def test_format_metadata_box_with_data(self):
        """Test metadata formatting with actual data"""
        meta = {
            "pvc": 50.0,
            "Lab_FI": 0.65,
            "Lab_Class": "F",
            "rock_count": 82,
        }
        result = _format_metadata_box(meta)
        assert "PVC: 50.0" in result
        assert "Lab FI: 0.65" in result
        assert "Class: F" in result
        assert "Rocks: 82" in result

    def test_format_metadata_box_partial(self):
        """Test metadata formatting with partial data"""
        meta = {"pvc": 25.0, "rock_count": 60}
        result = _format_metadata_box(meta)
        assert "PVC: 25.0" in result
        assert "Rocks: 60" in result

    def test_save_high_quality_figure(self, temp_output_dir):
        """Test saving a figure with high-quality settings"""
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots(figsize=(8, 6))
        ax.plot([1, 2, 3], [1, 2, 3], 'b-')
        ax.set_title('Test Figure')
        ax.set_xlabel('X')
        ax.set_ylabel('Y')

        output_path = temp_output_dir / "test_figure.png"

        result = PublicationFigureGenerator.save_high_quality_figure(
            fig, output_path, dpi=150
        )

        assert result.exists(), f"Figure not saved to {output_path}"
        assert result.suffix == ".png"
        plt.close(fig)

    def test_save_high_quality_figure_pdf(self, temp_output_dir):
        """Test saving figure as PDF"""
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots(figsize=(8, 6))
        ax.plot([1, 2, 3], [1, 4, 9], 'r-')
        ax.set_title('PDF Test')

        output_path = temp_output_dir / "test_figure.pdf"

        result = PublicationFigureGenerator.save_high_quality_figure(
            fig, output_path, dpi=300
        )

        assert result.exists(), f"PDF not saved to {output_path}"
        assert result.suffix == ".pdf"
        plt.close(fig)

    def test_save_high_quality_figure_transparent(self, temp_output_dir):
        """Test saving figure with transparent background"""
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots(figsize=(8, 6))
        ax.plot([1, 2, 3], [1, 2, 3], 'g-')
        ax.set_title('Transparent Test')

        output_path = temp_output_dir / "test_figure_transparent.png"

        result = PublicationFigureGenerator.save_high_quality_figure(
            fig, output_path, dpi=150, transparent=True
        )

        assert result.exists()
        plt.close(fig)


class TestSceneVisualization:
    """Test scene visualization functions"""

    @pytest.mark.skipif(not Path("sample_data/sample_scene.in").exists(),
                       reason="Sample scene not available")
    def test_save_scene_cross_section(self, temp_output_dir):
        """Test saving a scene cross-section"""
        sample_in = Path("sample_data/sample_scene.in")
        scene = parse_in_file(sample_in)

        output_path = temp_output_dir / "scene_cross_section.png"

        result = PublicationFigureGenerator.save_scene_cross_section(
            scene, output_path, title="Test Scene", dpi=150
        )

        assert result.exists(), f"Scene figure not saved to {output_path}"

    @pytest.mark.skipif(not Path("sample_data/sample_scene.in").exists(),
                       reason="Sample scene not available")
    def test_save_scene_cross_section_pdf(self, temp_output_dir):
        """Test saving scene as PDF"""
        sample_in = Path("sample_data/sample_scene.in")
        scene = parse_in_file(sample_in)

        output_path = temp_output_dir / "scene_cross_section.pdf"

        result = PublicationFigureGenerator.save_scene_cross_section(
            scene, output_path, dpi=300
        )

        assert result.exists()
        assert result.suffix == ".pdf"


class TestExportFunctions:
    """Test convenience export functions"""

    @pytest.mark.skipif(not Path("sample_data/sample_scene.in").exists(),
                       reason="Sample scene not available")
    def test_export_as_pdf(self, temp_output_dir):
        """Test PDF export convenience function"""
        sample_in = Path("sample_data/sample_scene.in")
        output_path = temp_output_dir / "export_test.pdf"

        result = export_scene_as_pdf(sample_in, output_path)

        assert result.exists()
        assert result.suffix == ".pdf"

    @pytest.mark.skipif(not Path("sample_data/sample_scene.in").exists(),
                       reason="Sample scene not available")
    def test_export_as_svg(self, temp_output_dir):
        """Test SVG export convenience function"""
        sample_in = Path("sample_data/sample_scene.in")
        output_path = temp_output_dir / "export_test.svg"

        result = export_scene_as_svg(sample_in, output_path)

        assert result.exists()
        assert result.suffix == ".svg"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

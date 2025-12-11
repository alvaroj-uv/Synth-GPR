#!/usr/bin/env python3
"""
Unit tests for visualize_gprmax_blueprint.py
Tests the refactored helper functions and rendering logic.
"""

import pytest
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.tools.visualization import visualize_gprmax_blueprint as vgb


class TestConstants:
    """Test that constants are properly defined"""
    
    def test_signal_threshold_exists(self):
        """Verify signal amplitude threshold constant exists"""
        assert hasattr(vgb, 'SIGNAL_AMPLITUDE_THRESHOLD')
        assert vgb.SIGNAL_AMPLITUDE_THRESHOLD == 1e-9
    
    def test_figure_sizes_exist(self):
        """Verify figure size constants exist"""
        assert hasattr(vgb, 'BLUEPRINT_FIGURE_SIZE')
        assert hasattr(vgb, 'SIGNAL_FIGURE_SIZE')
        assert vgb.BLUEPRINT_FIGURE_SIZE == (12, 8)
        assert vgb.SIGNAL_FIGURE_SIZE == (16, 8)
    
    def test_visual_constants_exist(self):
        """Verify visual styling constants exist"""
        assert hasattr(vgb, 'DEFAULT_LINE_WIDTH')
        assert hasattr(vgb, 'EDGE_COLOR')
        assert vgb.DEFAULT_LINE_WIDTH == 0.3
        assert vgb.EDGE_COLOR == '#404040'


class TestMaterialColors:
    """Test material color generation"""
    
    def test_generate_material_colors(self):
        """Test material colors dictionary generation"""
        colors = vgb.generate_material_colors()
        
        # Check base materials exist
        assert 'free_space' in colors
        assert 'bal_rock' in colors
        assert 'subgrade' in colors
        assert 'formation' in colors
        
        # Check gradient materials generated
        for i in range(1, 10):
            assert f'bal_foul_g{i}' in colors
    
    def test_material_colors_are_valid(self):
        """Test that all color values are valid"""
        colors = vgb.generate_material_colors()
        
        for material, color in colors.items():
            # Color should be string (hex) or tuple (RGBA)
            assert isinstance(color, (str, tuple, np.ndarray))


class TestHelperFunctions:
    """Test extracted helper functions"""
    
    def test_filter_cylinders(self):
        """Test cylinder filtering from objects list"""
        objects = [
            {'type': 'box', 'material': 'test'},
            {'type': 'cylinder', 'x': 0.1, 'y': 0.2, 'radius': 0.05},
            {'type': 'cylinder', 'x': 0.3, 'y': 0.4, 'radius': 0.03},
            {'type': 'box', 'material': 'test2'},
        ]
        
        cylinders = vgb.filter_cylinders(objects)
        assert len(cylinders) == 2
        assert all(obj['type'] == 'cylinder' for obj in cylinders)
    
    def test_filter_boxes(self):
        """Test box filtering from objects list"""
        objects = [
            {'type': 'box', 'material': 'test', 'y1': 0, 'y2': 1},
            {'type': 'cylinder', 'x': 0.1, 'y': 0.2},
            {'type': 'box', 'material': 'test2', 'y1': 1, 'y2': 2},
        ]
        
        boxes = vgb.filter_boxes(objects)
        assert len(boxes) == 2
        assert all(obj['type'] == 'box' for obj in boxes)
    
    def test_filter_boxes_exclude_material(self):
        """Test box filtering with material exclusion"""
        objects = [
            {'type': 'box', 'material': 'free_space', 'y1': 0, 'y2': 1},
            {'type': 'box', 'material': 'subgrade', 'y1': 0, 'y2': 0.3},
            {'type': 'box', 'material': 'free_space', 'y1': 1, 'y2': 2},
        ]
        
        boxes = vgb.filter_boxes(objects, exclude_material='free_space')
        assert len(boxes) == 1
        assert boxes[0]['material'] == 'subgrade'


class TestColorMapping:
    """Test color mapping functions"""
    
    def test_get_material_color_alpha_free_space(self):
        """Test free_space returns special color"""
        materials = {'free_space': {'eps': 1.0, 'sigma': 0}}
        color, alpha = vgb.get_material_color_alpha(
            'free_space', materials, min_eps=1, max_eps=10, cmap=plt.cm.YlOrBr
        )
        
        assert color == '#E8F4F8'
        assert alpha == 0.1
    
    def test_get_material_color_alpha_normal(self):
        """Test normal material returns colormap value"""
        materials = {'subgrade': {'eps': 8.0, 'sigma': 0.02}}
        color, alpha = vgb.get_material_color_alpha(
            'subgrade', materials, min_eps=1, max_eps=10, cmap=plt.cm.YlOrBr
        )
        
        # Should return a color tuple/string and alpha of 1.0
        assert color is not None
        assert alpha == 1.0
    
    def test_get_material_color_alpha_missing_material(self):
        """Test missing material uses default eps value"""
        materials = {}
        color, alpha = vgb.get_material_color_alpha(
            'unknown', materials, min_eps=1, max_eps=10, cmap=plt.cm.YlOrBr
        )
        
        # Should still return valid values
        assert color is not None
        assert alpha == 1.0


class TestParsingIntegration:
    """Integration tests for parsing .in files"""
    
    @pytest.fixture
    def sample_in_file(self, tmp_path):
        """Create a minimal sample .in file for testing"""
        content = """#title: Test Scenario
#domain: 0.5 1.5 0.005
#material: 8 0.02 subgrade
#material: 10 0.03 formation
#box: 0.0 0.0 0.0 0.5 0.3 0.005 subgrade
#box: 0.0 0.3 0.0 0.5 0.4 0.005 formation
#waveform: ricker 1 4e+08
#hertzian_dipole: z 0.3 1.434 0.0025 4e+08
#rx: 0.35 1.434 0.0025
## FI (%): 15.5
## FI_class: Clean
"""
        test_file = tmp_path / "test.in"
        test_file.write_text(content)
        return test_file
    
    def test_parse_sample_file(self, sample_in_file):
        """Test parsing a complete sample file"""
        data = vgb.parse_gprmax_input(str(sample_in_file))
        
        assert data['title'] == 'Test Scenario'
        assert data['domain']['x'] == 0.5
        assert data['domain']['y'] == 1.5
        assert data['domain']['z'] == 0.005
        
        assert 'subgrade' in data['materials']
        assert 'formation' in data['materials']
        
        assert len(data['objects']) == 2
        assert data['objects'][0]['type'] == 'box'
        
        assert data['source'] is not None
        assert data['receiver'] is not None
        
        assert data['metadata']['FI'] == '15.5'
        assert data['metadata']['FI_class'] == 'Clean'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

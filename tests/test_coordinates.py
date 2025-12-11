"""
Unit tests for Coordinate System.
"""
import pytest
from src.domain.coordinates import CoordinateSystem, LayerStack, Anchor
from src.domain import Point3D


class TestCoordinateSystem:
    
    @pytest.fixture
    def stack(self):
        return LayerStack(
            subgrade_thickness=0.5,
            formation_thickness=0.1,
            ballast_thickness=0.4,
            antenna_clearance=0.5,
            air_buffer=0.1
        )
        
    @pytest.fixture
    def coords(self, stack):
        return CoordinateSystem(stack, domain_x=2.0, domain_z=0.05)
        
    def test_anchor_levels(self, coords):
        """Verify absolute Y calculations."""
        assert coords.get_y(Anchor.BOTTOM) == 0.0
        assert coords.get_y(Anchor.SUBGRADE_TOP) == 0.5
        assert coords.get_y(Anchor.FORMATION_TOP) == 0.6  # 0.5 + 0.1
        assert coords.get_y(Anchor.BALLAST_TOP) == 1.0    # 0.6 + 0.4
        assert coords.get_y(Anchor.ANTENNA_LEVEL) == 1.5  # 1.0 + 0.5
        
    def test_layer_bounds(self, coords):
        """Verify layer boundaries."""
        # Subgrade
        ymin, ymax = coords.get_layer_bounds('subgrade')
        assert ymin == 0.0
        assert ymax == 0.5
        
        # Formation
        ymin, ymax = coords.get_layer_bounds('formation')
        assert ymin == 0.5
        assert ymax == 0.6
        
        # Ballast
        ymin, ymax = coords.get_layer_bounds('ballast')
        assert ymin == 0.6
        assert ymax == 1.0
        
    def test_unknown_layer_raises(self, coords):
        with pytest.raises(ValueError):
            coords.get_layer_bounds('magma_layer')
            
    def test_offsets(self, coords):
        """Verify offset calculation."""
        # 10cm above ballast top
        y = coords.get_y(Anchor.BALLAST_TOP, offset=0.1)
        assert y == 1.1
        
    def test_point_validation(self, coords):
        """Verify point bounds checking."""
        # Valid point
        p1 = Point3D(1.0, 0.5, 0.01)
        assert coords.validate_point(p1) is True
        
        # Invalid X
        p2 = Point3D(2.5, 0.5, 0.01) # domain_x is 2.0
        assert coords.validate_point(p2) is False
        
        # Invalid Y
        p3 = Point3D(1.0, 2.0, 0.01) # max y is 1.6 (1.5 + 0.1)
        assert coords.validate_point(p3) is False

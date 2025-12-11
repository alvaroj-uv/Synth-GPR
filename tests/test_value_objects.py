"""
Unit tests for domain value objects.

Tests the immutability, validation, and domain logic of value objects.
"""

import pytest
import math
from src.domain import (
    PercentageVoidContamination,
    Point2D,
    Point3D,
    Length,
)


class TestPercentageVoidContamination:
    """Tests for PVC value object."""
    
    def test_valid_pvc_creation(self):
        """PVC can be created with valid values."""
        pvc = PercentageVoidContamination(value=25.0)
        assert pvc.value == 25.0
    
    def test_pvc_validation_negative(self):
        """PVC rejects negative values."""
        with pytest.raises(ValueError, match="must be between 0-100%"):
            PercentageVoidContamination(value=-5.0)
    
    def test_pvc_validation_exceeds_100(self):
        """PVC rejects values > 100%."""
        with pytest.raises(ValueError, match="must be between 0-100%"):
            PercentageVoidContamination(value=105.0)
    
    def test_pvc_classification_clean(self):
        """PVC < 10% is classified as Clean."""
        pvc = PercentageVoidContamination(value=5.0)
        assert pvc.classification() == "Clean"
        assert pvc.is_clean() is True
        assert pvc.is_fouled() is False
    
    def test_pvc_classification_moderately_fouled(self):
        """PVC 10-20% is Moderately Fouled."""
        pvc = PercentageVoidContamination(value=15.0)
        assert pvc.classification() == "Moderately Fouled"
        assert pvc.is_clean() is False
        assert pvc.is_fouled() is False
    
    def test_pvc_classification_fouled(self):
        """PVC 20-40% is Fouled."""
        pvc = PercentageVoidContamination(value=30.0)
        assert pvc.classification() == "Fouled"
        assert pvc.is_fouled() is True
    
    def test_pvc_classification_highly_fouled(self):
        """PVC > 40% is Highly Fouled."""
        pvc = PercentageVoidContamination(value=50.0)
        assert pvc.classification() == "Highly Fouled"
        assert pvc.is_fouled() is True
    
    def test_pvc_to_fouling_index(self):
        """PVC converts to FI correctly."""
        pvc = PercentageVoidContamination(value=25.0)
        fi = pvc.to_fouling_index(porosity=0.4)
        assert fi == pytest.approx(10.0)  # 25 * 0.4 = 10
    
    def test_pvc_immutability(self):
        """PVC is immutable (frozen dataclass)."""
        pvc = PercentageVoidContamination(value=25.0)
        with pytest.raises(AttributeError):
            pvc.value = 30.0  # type: ignore
    
    def test_pvc_string_representation(self):
        """PVC has readable string representation."""
        pvc = PercentageVoidContamination(value=25.5)
        assert str(pvc) == "25.5%"


class TestPoint2D:
    """Tests for Point2D value object."""
    
    def test_point2d_creation(self):
        """Point2D can be created with coordinates."""
        p = Point2D(x=0.25, y=1.35)
        assert p.x == 0.25
        assert p.y == 1.35
    
    def test_point2d_distance(self):
        """Point2D calculates Euclidean distance correctly."""
        p1 = Point2D(x=0.0, y=0.0)
        p2 = Point2D(x=3.0, y=4.0)
        assert p1.distance_to(p2) == pytest.approx(5.0)
    
    def test_point2d_offset(self):
        """Point2D offset creates new point."""
        p1 = Point2D(x=1.0, y=2.0)
        p2 = p1.offset(dx=0.5, dy=0.3)
        assert p2.x == pytest.approx(1.5)
        assert p2.y == pytest.approx(2.3)
        # Original unchanged (immutability)
        assert p1.x == 1.0
        assert p1.y == 2.0
    
    def test_point2d_to_tuple(self):
        """Point2D converts to tuple."""
        p = Point2D(x=0.25, y=1.35)
        assert p.to_tuple() == (0.25, 1.35)
    
    def test_point2d_immutability(self):
        """Point2D is immutable."""
        p = Point2D(x=1.0, y=2.0)
        with pytest.raises(AttributeError):
            p.x = 3.0  # type: ignore
    
    def test_point2d_equality(self):
        """Point2D equality by value."""
        p1 = Point2D(x=0.5, y=1.0)
        p2 = Point2D(x=0.5, y=1.0)
        p3 = Point2D(x=0.5, y=1.1)
        assert p1 == p2
        assert p1 != p3


class TestPoint3D:
    """Tests for Point3D value object."""
    
    def test_point3d_creation(self):
        """Point3D can be created with 3D coordinates."""
        p = Point3D(x=0.25, y=1.35, z=0.0025)
        assert p.x == 0.25
        assert p.y == 1.35
        assert p.z == 0.0025
    
    def test_point3d_distance_3d(self):
        """Point3D calculates 3D distance correctly."""
        p1 = Point3D(x=0.0, y=0.0, z=0.0)
        p2 = Point3D(x=1.0, y=2.0, z=2.0)
        expected = math.sqrt(1**2 + 2**2 + 2**2)  # 3.0
        assert p1.distance_to(p2) == pytest.approx(expected)
    
    def test_point3d_distance_2d(self):
        """Point3D calculates 2D distance (ignoring Z)."""
        p1 = Point3D(x=0.0, y=0.0, z=0.0)
        p2 = Point3D(x=3.0, y=4.0, z=999.0)  # Z ignored
        assert p1.distance_2d(p2) == pytest.approx(5.0)
    
    def test_point3d_to_2d(self):
        """Point3D projects to 2D."""
        p3d = Point3D(x=0.25, y=1.35, z=0.0025)
        p2d = p3d.to_2d()
        assert isinstance(p2d, Point2D)
        assert p2d.x == 0.25
        assert p2d.y == 1.35
    
    def test_point3d_offset(self):
        """Point3D offset creates new point."""
        p1 = Point3D(x=1.0, y=2.0, z=3.0)
        p2 = p1.offset(dx=0.1, dy=0.2, dz=0.3)
        assert p2.x == pytest.approx(1.1)
        assert p2.y == pytest.approx(2.2)
        assert p2.z == pytest.approx(3.3)


class TestLength:
    """Tests for Length value object."""
    
    def test_length_creation(self):
        """Length can be created with value and unit."""
        length = Length(value=40, unit='cm')
        assert length.value == 40
        assert length.unit == 'cm'
    
    def test_length_to_meters(self):
        """Length converts to meters correctly."""
        assert Length(value=1.5, unit='m').to_meters() == 1.5
        assert Length(value=150, unit='cm').to_meters() == 1.5
        assert Length(value=1500, unit='mm').to_meters() == 1.5
    
    def test_length_to_centimeters(self):
        """Length converts to cm correctly."""
        length = Length(value=1.5, unit='m')
        assert length.to_centimeters() == 150.0
    
    def test_length_to_millimeters(self):
        """Length converts to mm correctly."""
        length = Length(value=1.5, unit='m')
        assert length.to_millimeters() == 1500.0
    
    def test_length_equality(self):
        """Lengths are equal if meter values match."""
        l1 = Length(value=1.5, unit='m')
        l2 = Length(value=150, unit='cm')
        l3 = Length(value=1500, unit='mm')
        assert l1 == l2
        assert l2 == l3
    
    def test_length_comparison(self):
        """Length comparison works across units."""
        l1 = Length(value=40, unit='cm')
        l2 = Length(value=300, unit='mm')
        assert l1 > l2  # 40cm > 30cm
        assert l2 < l1
    
    def test_length_addition(self):
        """Length addition works across units."""
        l1 = Length(value=1.0, unit='m')
        l2 = Length(value=50, unit='cm')
        result = l1 + l2
        assert result.to_meters() == pytest.approx(1.5)
        assert result.unit == 'm'  # Result in meters
    
    def test_length_subtraction(self):
        """Length subtraction works."""
        l1 = Length(value=1.0, unit='m')
        l2 = Length(value=30, unit='cm')
        result = l1 - l2
        assert result.to_meters() == pytest.approx(0.7)
    
    def test_length_multiplication(self):
        """Length can be multiplied by scalar."""
        l1 = Length(value=2.0, unit='m')
        l2 = l1 * 3
        assert l2.value == 6.0
        assert l2.unit == 'm'
    
    def test_length_immutability(self):
        """Length is immutable."""
        length = Length(value=1.5, unit='m')
        with pytest.raises(AttributeError):
            length.value = 2.0  # type: ignore

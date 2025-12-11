"""
Unit tests for Material value objects.
"""

import pytest
from src.domain import Material, Materials


class TestMaterial:
    """Tests for Material value object."""
    
    def test_material_creation(self):
        """Can create material with properties."""
        mat = Material(
            name="test_material",
            permittivity=5.0,
            conductivity=0.01
        )
        assert mat.name == "test_material"
        assert mat.permittivity == 5.0
        assert mat.conductivity == 0.01
        assert mat.permeability == 1.0  # default
    
    def test_material_immutability(self):
        """Material is immutable."""
        mat = Materials.SUBGRADE
        with pytest.raises(AttributeError):
            mat.permittivity = 10.0  # type: ignore
    
    def test_material_string_representation(self):
        """Material has readable string."""
        mat = Material("subgrade", permittivity=5.0, conductivity=0.01)
        assert "subgrade" in str(mat)
        assert "5.0" in str(mat)
        assert "0.010" in str(mat)
    
    def test_material_to_gprmax_command(self):
        """Material converts to gprMax command."""
        mat = Materials.BALLAST_ROCK
        cmd = mat.to_gprmax_command()
        
        assert cmd.eps == 4.0
        assert cmd.sigma == 0.001
        assert cmd.identifier == "bal_rock"


class TestMaterials:
    """Tests for Materials library."""
    
    def test_predefined_materials_exist(self):
        """Standard materials are defined."""
        assert Materials.FREE_SPACE.permittivity == 1.0
        assert Materials.SUBGRADE.permittivity == 5.0
        assert Materials.FORMATION.permittivity == 6.0
        assert Materials.BALLAST_ROCK.permittivity == 4.0
        assert Materials.FOULING_BASE.permittivity == 8.0
    
    def test_materials_get_by_name(self):
        """Can retrieve material by name."""
        mat = Materials.get("subgrade")
        assert mat.name == "subgrade"
        assert mat == Materials.SUBGRADE
    
    def test_materials_get_unknown_raises(self):
        """Getting unknown material raises error."""
        with pytest.raises(ValueError, match="Unknown material"):
            Materials.get("nonexistent")
    
    def test_materials_are_immutable(self):
        """Cannot modify standard materials."""
        with pytest.raises(AttributeError):
            Materials.SUBGRADE.permittivity = 10.0  # type: ignore

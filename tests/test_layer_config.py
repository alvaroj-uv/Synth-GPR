"""Tests for LayerStack configuration and layer definitions."""

import pytest

from src.layer_config import LayerStack, LayerDefinition


class TestLayerStack:
    """Verify LayerStack is properly configured."""

    def test_layers_exist(self):
        """Verify all expected layers exist."""
        assert hasattr(LayerStack, "SUBGRADE")
        assert hasattr(LayerStack, "FORMATION")
        assert hasattr(LayerStack, "BALLAST")
        assert hasattr(LayerStack, "ALL")

    def test_layers_are_valid(self):
        """Verify layer configuration passes validation."""
        errors = LayerStack.validate()
        assert errors == [], f"Invalid layers: {errors}"

    def test_layers_are_contiguous(self):
        """Verify no gaps between layers."""
        for i in range(len(LayerStack.ALL) - 1):
            current = LayerStack.ALL[i]
            next_layer = LayerStack.ALL[i + 1]
            assert current.y_top == next_layer.y_bottom, (
                f"Gap between {current.name} and {next_layer.name}: "
                f"{current.name} ends at {current.y_top}, "
                f"{next_layer.name} starts at {next_layer.y_bottom}"
            )

    def test_layers_have_positive_height(self):
        """Verify all layers have positive height."""
        for layer in LayerStack.ALL:
            assert layer.height > 0, f"Layer {layer.name} has non-positive height"

    def test_subgrade_bounds(self):
        """Verify subgrade layer properties."""
        subgrade = LayerStack.SUBGRADE
        assert subgrade.name == "subgrade"
        assert subgrade.y_bottom == 0.0
        assert subgrade.y_top == 0.2
        assert subgrade.height == 0.2

    def test_formation_bounds(self):
        """Verify formation layer properties."""
        formation = LayerStack.FORMATION
        assert formation.name == "formation"
        assert formation.y_bottom == 0.2
        assert formation.y_top == 0.3
        # Account for floating point precision
        assert abs(formation.height - 0.1) < 1e-9

    def test_ballast_bounds(self):
        """Verify ballast layer properties."""
        ballast = LayerStack.BALLAST
        assert ballast.name == "ballast"
        assert ballast.y_bottom == 0.3
        assert ballast.y_top == 0.55
        # Account for floating point precision
        assert abs(ballast.height - 0.25) < 1e-9


class TestLayerDefinition:
    """Verify LayerDefinition methods work correctly."""

    def test_contains_checks_membership(self):
        """Verify contains() method correctly identifies layer membership."""
        ballast = LayerStack.BALLAST

        # Inside layer
        assert ballast.contains(0.3)
        assert ballast.contains(0.4)
        assert ballast.contains(0.55)

        # Outside layer
        assert not ballast.contains(0.29)
        assert not ballast.contains(0.56)
        assert not ballast.contains(0.0)
        assert not ballast.contains(1.0)

    def test_bounds_generation(self):
        """Verify bounds() creates correct PackingBounds."""
        ballast = LayerStack.BALLAST
        bounds = ballast.bounds(domain_x=2.248)

        assert bounds.x_min == 0.0
        assert bounds.x_max == 2.248
        assert bounds.y_min == 0.3
        assert bounds.y_max == 0.55

    def test_bounds_different_widths(self):
        """Verify bounds() works with different domain widths."""
        formation = LayerStack.FORMATION

        # Test with different widths
        bounds_1 = formation.bounds(domain_x=1.0)
        assert bounds_1.x_max == 1.0
        assert bounds_1.y_min == formation.y_bottom
        assert bounds_1.y_max == formation.y_top

        bounds_2 = formation.bounds(domain_x=5.0)
        assert bounds_2.x_max == 5.0
        assert bounds_2.y_min == formation.y_bottom
        assert bounds_2.y_max == formation.y_top


class TestLayerStackOrdering:
    """Verify layers are properly ordered and non-overlapping."""

    def test_layers_ordered_by_height(self):
        """Verify layers are ordered from bottom to top."""
        for i in range(len(LayerStack.ALL) - 1):
            current = LayerStack.ALL[i]
            next_layer = LayerStack.ALL[i + 1]
            assert current.y_top <= next_layer.y_bottom, (
                f"Layer ordering violation: {current.name} overlaps with {next_layer.name}"
            )

    def test_no_overlapping_layers(self):
        """Verify no two layers overlap."""
        for i, layer1 in enumerate(LayerStack.ALL):
            for layer2 in LayerStack.ALL[i + 1 :]:
                # Layer1 should be entirely below layer2
                assert layer1.y_top <= layer2.y_bottom, (
                    f"Layers {layer1.name} and {layer2.name} overlap"
                )


class TestLayerStackMaterials:
    """Verify material codes are assigned."""

    def test_material_codes_assigned(self):
        """Verify all layers have material codes."""
        for layer in LayerStack.ALL:
            assert layer.material_code is not None
            assert len(layer.material_code) > 0

    def test_material_codes_unique(self):
        """Verify material codes are unique across layers."""
        material_codes = [layer.material_code for layer in LayerStack.ALL]
        assert len(material_codes) == len(set(material_codes)), (
            f"Duplicate material codes found: {material_codes}"
        )

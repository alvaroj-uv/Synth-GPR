"""Single source of truth for material layer coordinate definitions.

All workers reference LayerStack for layer boundaries instead of hardcoding values.
This ensures consistency and makes it safe to change layer coordinates in one place.
"""

from dataclasses import dataclass
from typing import List, Optional

from src.rock_model import PackingBounds


@dataclass
class LayerDefinition:
    """A material layer with absolute world coordinates."""

    name: str
    y_bottom: float
    y_top: float
    material_code: str

    @property
    def height(self) -> float:
        """Height of this layer in meters."""
        return self.y_top - self.y_bottom

    def contains(self, y: float) -> bool:
        """Check if a y-coordinate is within this layer."""
        return self.y_bottom <= y <= self.y_top

    def bounds(self, domain_x: float) -> PackingBounds:
        """Get PackingBounds for this layer given domain width."""
        return PackingBounds(
            x_min=0.0,
            x_max=domain_x,
            y_min=self.y_bottom,
            y_max=self.y_top,
        )


class LayerStack:
    """Single source of truth for layer coordinates and properties."""

    SUBGRADE = LayerDefinition(
        name="subgrade",
        y_bottom=0.0,
        y_top=0.2,
        material_code="subgrade",
    )

    FORMATION = LayerDefinition(
        name="formation",
        y_bottom=0.2,
        y_top=0.3,
        material_code="formation",
    )

    BALLAST = LayerDefinition(
        name="ballast",
        y_bottom=0.3,
        y_top=0.55,
        material_code="ballast_rock",
    )

    ALL = [SUBGRADE, FORMATION, BALLAST]

    @classmethod
    def validate(cls) -> List[str]:
        """Validate layer configuration for consistency.

        Returns:
            List of error messages if any validation fails, empty list if valid.
        """
        errors = []

        # Check that layers are contiguous (no gaps)
        for i in range(len(cls.ALL) - 1):
            current = cls.ALL[i]
            next_layer = cls.ALL[i + 1]
            if current.y_top != next_layer.y_bottom:
                errors.append(
                    f"Gap between layers {i} ({current.name}) and {i+1} ({next_layer.name}): "
                    f"{current.name} ends at {current.y_top}, but {next_layer.name} starts at {next_layer.y_bottom}"
                )

        # Check that each layer has positive height
        for layer in cls.ALL:
            if layer.height <= 0:
                errors.append(
                    f"Layer {layer.name} has non-positive height: {layer.height}"
                )

        return errors


# Validate on import to catch configuration errors early
_validation_errors = LayerStack.validate()
if _validation_errors:
    raise RuntimeError(f"Invalid layer configuration: {'; '.join(_validation_errors)}")

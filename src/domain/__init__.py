"""
Domain package: Domain-Driven Design value objects and domain concepts.

This package contains value objects that represent core domain concepts,
replacing primitive types to improve type safety and express domain knowledge.
"""

from .value_objects import (
    Point3D, Point2D, Length,
    PercentageVoidContamination
)
# NOTE: material EM properties live in constants.MC (single source of truth).
# The former domain.materials.Materials/Material table was dead, duplicated
# those values with conflicting numbers, and has been removed.
from .scene_parameters import SceneParameters
from .coordinates import Anchor, LayerStack, CoordinateSystem, Layer, LayerBounds

__all__ = [
    'Point3D', 'Point2D', 'Length',
    'PercentageVoidContamination',
    'SceneParameters',
    'Anchor', 'LayerStack', 'CoordinateSystem',
    'Layer', 'LayerBounds'
]

"""
EXAMPLE: Single Source of Truth for Layer Coordinates

This is what you'd add to the codebase. Simple, effective, eliminates coupling.
"""

from dataclasses import dataclass


@dataclass
class LayerDefinition:
    """A single material layer with absolute world coordinates."""
    
    name: str
    y_bottom: float
    y_top: float
    material_code: str
    
    @property
    def height(self) -> float:
        return self.y_top - self.y_bottom
    
    def contains(self, y: float) -> bool:
        """Is y-coordinate within this layer?"""
        return self.y_bottom <= y <= self.y_top


class LayerStack:
    """
    SINGLE SOURCE OF TRUTH for all layer coordinates.
    
    All workers reference this class instead of hardcoding values.
    
    Example usage:
        ballast = LayerStack.BALLAST
        bounds = ballast.bounds(domain_x)  # Get PackingBounds
        
        if ballast.contains(rock.y):  # Check if rock is in ballast
            # Process rock
    
    To change coordinates:
        1. Edit BALLAST = LayerDefinition(y_bottom=0.4, ...)
        2. ALL workers automatically use new value
        3. Zero risk of inconsistency
    """
    
    # Define all layers ONCE
    SUBGRADE = LayerDefinition(
        name="subgrade",
        y_bottom=0.0,
        y_top=0.2,
        material_code="subgrade"
    )
    
    FORMATION = LayerDefinition(
        name="formation",
        y_bottom=0.2,
        y_top=0.3,
        material_code="formation"
    )
    
    BALLAST = LayerDefinition(
        name="ballast",
        y_bottom=0.3,
        y_top=0.55,
        material_code="ballast_rock"
    )
    
    # All layers in order
    ALL = [SUBGRADE, FORMATION, BALLAST]
    
    @classmethod
    def validate(cls) -> list[str]:
        """Check that layers are properly defined."""
        errors = []
        
        # Check contiguity (no gaps or overlaps)
        for i in range(len(cls.ALL) - 1):
            curr = cls.ALL[i]
            next_layer = cls.ALL[i + 1]
            if curr.y_top != next_layer.y_bottom:
                errors.append(
                    f"Gap between {curr.name} (top={curr.y_top}) "
                    f"and {next_layer.name} (bottom={next_layer.y_bottom})"
                )
        
        # Check positive heights
        for layer in cls.ALL:
            if layer.height <= 0:
                errors.append(f"{layer.name}: invalid height {layer.height}")
        
        return errors


# Example: Change ballast thickness from 0.25 to 0.30
if __name__ == "__main__":
    print("BEFORE (Scattered Coordinates):")
    print("-" * 50)
    print("You would need to change:")
    print("  • workers.py: formation_top = 0.3")
    print("  • granular_worker.py: ballast_bottom = 0.3")
    print("  • granular_worker.py: ballast_thickness = 0.25")
    print("  • lab_worker.py: ballast_bottom = 0.3")
    print("  • lab_worker.py: ballast_top = 0.55")
    print("  Risk: Easy to miss one, causing bugs\n")
    
    print("AFTER (Single Source of Truth):")
    print("-" * 50)
    print("Change ONLY:")
    print("  LayerStack.BALLAST = LayerDefinition(")
    print("      y_bottom=0.3,  ← unchanged")
    print("      y_top=0.60,    ← changed from 0.55 to 0.60")
    print("      ...")
    print("  )")
    print("  All workers automatically use new value!")
    print("  Risk: Zero\n")
    
    # Show that it works
    print("Current Configuration:")
    print("-" * 50)
    for layer in LayerStack.ALL:
        print(f"  {layer.name:12} [{layer.y_bottom:.2f}, {layer.y_top:.2f}] "
              f"(height: {layer.height:.2f}m)")
    
    print("\nValidation:")
    errors = LayerStack.validate()
    if errors:
        print("  ✗ Errors found:")
        for error in errors:
            print(f"    - {error}")
    else:
        print("  ✓ All layers valid and contiguous")
    
    # Show usage
    print("\nUsage in Workers:")
    print("-" * 50)
    print("# workers.py - SubgradeWorker")
    print("subgrade = LayerStack.SUBGRADE")
    print("bounds = subgrade.bounds(domain_x)  # Get PackingBounds")
    print()
    print("# granular_worker.py - GranularMatrixWorker")
    print("ballast = LayerStack.BALLAST")
    print("bounds = ballast.bounds(domain_x)  # Single source!")
    print()
    print("# lab_worker.py - LabWorker")
    print("ballast = LayerStack.BALLAST")
    print("if ballast.contains(rock.y):  # Use layer method")
    print("    samples.append(rock)")

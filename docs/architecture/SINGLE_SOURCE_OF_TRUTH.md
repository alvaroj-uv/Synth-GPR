# Single Source of Truth: Layer Coordinate Architecture

## The Problem

Currently, absolute coordinates are scattered throughout the codebase:

```
workers.py:          subgrade_top = 0.2
workers.py:          formation_bottom = 0.2
workers.py:          formation_top = 0.3
granular_worker.py:  ballast_bottom = 0.3
granular_worker.py:  ballast_thickness = 0.25
lab_worker.py:       ballast_bottom = 0.3
lab_worker.py:       ballast_top = 0.55
rock_packing.py:     strip_height = 3.2
test files:          hardcoded values

If you change 0.3 → 0.4, you must update MULTIPLE FILES.
Risk: Easy to miss one, creating coordinate misalignment.
```

## The Solution: Centralized Layer Definition

Create a single module that defines all layer coordinates, and all workers reference it:

---

## Approach 1: Simple Configuration Module (Recommended)

### File: `src/layer_config.py`

```python
"""
Single source of truth for all layer coordinate definitions.

All workers reference this module, eliminating scattered hardcoded values.
Change coordinates in ONE place, all workers automatically use new values.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class LayerDefinition:
    """Definition of a single material layer with absolute coordinates."""
    
    name: str                    # e.g., "ballast", "subgrade"
    y_bottom: float              # Absolute y-coordinate of layer bottom
    y_top: float                 # Absolute y-coordinate of layer top
    material_code: str           # e.g., MC.BALLAST_ROCK
    description: str             # Human-readable description
    
    @property
    def height(self) -> float:
        """Height of this layer."""
        return self.y_top - self.y_bottom
    
    def contains(self, y: float) -> bool:
        """Check if y-coordinate is within this layer."""
        return self.y_bottom <= y <= self.y_top
    
    def bounds(self, domain_x: float) -> 'PackingBounds':
        """Get absolute coordinates as PackingBounds."""
        from .rock_model import PackingBounds
        return PackingBounds(
            x_min=0.0,
            x_max=domain_x,
            y_min=self.y_bottom,
            y_max=self.y_top
        )
    
    def local_bounds(self, domain_x: float) -> 'PackingBounds':
        """Get bounds in local (relative to layer) coordinates."""
        from .rock_model import PackingBounds
        return PackingBounds(
            x_min=0.0,
            x_max=domain_x,
            y_min=0.0,
            y_max=self.height
        )


class LayerStack:
    """Complete definition of all material layers in world space.
    
    SINGLE SOURCE OF TRUTH for all layer coordinates.
    
    Any worker that needs layer coordinates references this class.
    If layer coordinates change, only this file needs updating.
    """
    
    # Define all layers once here
    SUBGRADE = LayerDefinition(
        name="subgrade",
        y_bottom=0.0,
        y_top=0.2,
        material_code="subgrade",
        description="Foundation layer"
    )
    
    FORMATION = LayerDefinition(
        name="formation",
        y_bottom=0.2,
        y_top=0.3,
        material_code="formation",
        description="Transition layer"
    )
    
    BALLAST = LayerDefinition(
        name="ballast",
        y_bottom=0.3,
        y_top=0.55,
        material_code="bal_rock",
        description="Ballast layer containing rocks"
    )
    
    # Optional: Define layers as an ordered list
    LAYERS = [SUBGRADE, FORMATION, BALLAST]
    
    @classmethod
    def get_layer(cls, name: str) -> Optional[LayerDefinition]:
        """Get layer by name."""
        for layer in cls.LAYERS:
            if layer.name == name:
                return layer
        return None
    
    @classmethod
    def get_layer_by_coordinate(cls, y: float) -> Optional[LayerDefinition]:
        """Find which layer a y-coordinate belongs to."""
        for layer in cls.LAYERS:
            if layer.contains(y):
                return layer
        return None
    
    @classmethod
    def get_total_height(cls) -> float:
        """Total height of all layers stacked."""
        return cls.BALLAST.y_top  # Bottom of ballast (last layer)
    
    @classmethod
    def validate_consistency(cls) -> list[str]:
        """Validate that layers are properly defined (no gaps/overlaps).
        
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        
        # Check layers are sorted
        for i in range(len(cls.LAYERS) - 1):
            current = cls.LAYERS[i]
            next_layer = cls.LAYERS[i + 1]
            
            if current.y_top != next_layer.y_bottom:
                errors.append(
                    f"Gap or overlap between {current.name} and {next_layer.name}: "
                    f"{current.name} ends at {current.y_top}, "
                    f"{next_layer.name} starts at {next_layer.y_bottom}"
                )
        
        # Check no negative heights
        for layer in cls.LAYERS:
            if layer.height <= 0:
                errors.append(
                    f"{layer.name} has invalid height: {layer.height}"
                )
        
        return errors
```

### Usage in Workers

```python
# workers.py - SubgradeWorker
from src.layer_config import LayerStack

class SubgradeWorker(Worker):
    def execute(self, scene, params, materials, tools):
        subgrade = LayerStack.SUBGRADE  # ← Reference single source!
        
        scene.add_geometry(BoxCommand(
            0, subgrade.y_bottom, 0.0,
            domain_x, subgrade.y_top, domain_z,
            MC.SUBGRADE
        ))

# granular_worker.py - GranularMatrixWorker
from src.layer_config import LayerStack

class GranularMatrixWorker:
    def execute(self, scene, params, materials, tools):
        ballast = LayerStack.BALLAST  # ← Reference single source!
        
        bounds = ballast.bounds(domain_x)  # Get PackingBounds directly!
        packer = tools.get_tool("rock_packer")
        rocks = packer.generate_rocks(bounds, ...)

# lab_worker.py - LabWorker
from src.layer_config import LayerStack

class LabWorker:
    def execute(self, scene, params, materials, tools):
        ballast = LayerStack.BALLAST  # ← Reference single source!
        
        # Sample from ballast layer
        for rock in scene.rock_positions:
            if ballast.contains(rock.y):  # ← Use layer method!
                samples_in_ballast.append(rock)
```

---

## Approach 2: Configuration File (More Flexible)

For even more flexibility, load layer definitions from a config file:

### File: `config/layers.yaml`

```yaml
layers:
  subgrade:
    y_bottom: 0.0
    y_top: 0.2
    material: subgrade
    description: Foundation layer
  
  formation:
    y_bottom: 0.2
    y_top: 0.3
    material: formation
    description: Transition layer
  
  ballast:
    y_bottom: 0.3
    y_top: 0.55
    material: ballast
    description: Ballast layer with rocks
```

### File: `src/layer_config.py` (with YAML loading)

```python
import yaml
from pathlib import Path
from dataclasses import dataclass

@dataclass
class LayerDefinition:
    name: str
    y_bottom: float
    y_top: float
    material_code: str
    description: str
    
    @property
    def height(self) -> float:
        return self.y_top - self.y_bottom


class LayerStack:
    """Load layers from YAML configuration."""
    
    _layers = None
    
    @classmethod
    def _load_config(cls):
        """Load layer definitions from config file."""
        if cls._layers is None:
            config_path = Path(__file__).parent.parent / "config" / "layers.yaml"
            with open(config_path) as f:
                data = yaml.safe_load(f)
            
            cls._layers = {}
            for name, props in data["layers"].items():
                cls._layers[name] = LayerDefinition(
                    name=name,
                    y_bottom=props["y_bottom"],
                    y_top=props["y_top"],
                    material_code=props["material"],
                    description=props["description"]
                )
    
    @classmethod
    def get_layer(cls, name: str) -> LayerDefinition:
        """Get layer by name."""
        cls._load_config()
        return cls._layers[name]
    
    @classmethod
    def get_all_layers(cls) -> list[LayerDefinition]:
        """Get all layers in order."""
        cls._load_config()
        return list(cls._layers.values())
    
    # Convenience properties
    SUBGRADE = property(lambda self: self.get_layer("subgrade"))
    FORMATION = property(lambda self: self.get_layer("formation"))
    BALLAST = property(lambda self: self.get_layer("ballast"))
```

---

## Approach 3: Hybrid (Recommended)

Combine Python code with optional override capability:

```python
# src/layer_config.py

import os
from dataclasses import dataclass

@dataclass
class LayerDefinition:
    name: str
    y_bottom: float
    y_top: float
    material_code: str
    description: str
    
    @property
    def height(self) -> float:
        return self.y_top - self.y_bottom


class LayerStack:
    """Single source of truth for layer coordinates.
    
    Default values defined in code.
    Can be overridden by environment variables for testing.
    """
    
    # Default values (single source of truth)
    _DEFAULTS = {
        "subgrade_top": 0.2,
        "formation_bottom": 0.2,
        "formation_top": 0.3,
        "ballast_bottom": 0.3,
        "ballast_top": 0.55,
    }
    
    @classmethod
    def _get_value(cls, key: str, default: float) -> float:
        """Get layer coordinate value, with optional override."""
        env_key = f"LAYER_{key.upper()}"
        return float(os.getenv(env_key, default))
    
    @classmethod
    @property
    def SUBGRADE(cls) -> LayerDefinition:
        return LayerDefinition(
            name="subgrade",
            y_bottom=0.0,
            y_top=cls._get_value("subgrade_top", 0.2),
            material_code="subgrade",
            description="Foundation"
        )
    
    @classmethod
    @property
    def BALLAST(cls) -> LayerDefinition:
        return LayerDefinition(
            name="ballast",
            y_bottom=cls._get_value("ballast_bottom", 0.3),
            y_top=cls._get_value("ballast_top", 0.55),
            material_code="ballast",
            description="Ballast with rocks"
        )
```

Usage:
```python
# Normal operation
ballast = LayerStack.BALLAST  # Uses defaults: [0.3, 0.55]

# Testing with different coordinates
os.environ["LAYER_BALLAST_BOTTOM"] = "0.4"
ballast = LayerStack.BALLAST  # Now uses: [0.4, 0.55]
```

---

## Benefits of Single Source of Truth

### Before (Scattered Coordinates)
```python
# 6 different files with hardcoded values
# Change requires:
#   ✗ Find all hardcoded values
#   ✗ Update each file
#   ✗ Risk missing one
#   ✗ Risk creating inconsistency
```

### After (Single Source)
```python
# 1 file with all definitions
# Change requires:
#   ✓ Update LayerStack
#   ✓ All workers automatically use new value
#   ✓ No risk of inconsistency
#   ✓ Easy to test with different coordinates
```

---

## Validation

Add automatic validation to catch inconsistencies:

```python
class LayerStack:
    @classmethod
    def validate(cls) -> None:
        """Validate layer consistency.
        
        Raises:
            ValueError: If layers are invalid
        """
        errors = []
        layers = cls.get_all_layers()
        
        # Check layers are contiguous (no gaps)
        for i in range(len(layers) - 1):
            if layers[i].y_top != layers[i+1].y_bottom:
                errors.append(
                    f"Gap between {layers[i].name} and {layers[i+1].name}"
                )
        
        # Check positive heights
        for layer in layers:
            if layer.height <= 0:
                errors.append(f"{layer.name} has invalid height: {layer.height}")
        
        if errors:
            raise ValueError(f"Invalid layer configuration:\n" + "\n".join(errors))


# Run validation at startup
if __name__ == "__main__":
    LayerStack.validate()
    print("✓ Layer configuration is valid")
```

---

## Integration Strategy

### Phase 1: Add Layer Config Module (1 hour)
```python
# src/layer_config.py - New file with LayerStack
```

### Phase 2: Migrate Workers (2 hours)
```python
# Update each worker to use LayerStack instead of hardcoded values
# workers.py: SubgradeWorker
# workers.py: FormationWorker
# granular_worker.py: GranularMatrixWorker
# lab_worker.py: LabWorker
```

### Phase 3: Add Validation Tests (30 min)
```python
# tests/test_layer_config.py
# Test that layers are valid
# Test that changes propagate correctly
```

### Phase 4: Document (30 min)
```python
# Add to README/architecture docs
# Show how to change layer coordinates
# Show how to extend with more layers
```

---

## Example: Changing Layer Coordinates

### Before (Current)
```python
# Change ballast from [0.3, 0.55] to [0.4, 0.60]
# Step 1: granular_worker.py - Find and change hardcoded 0.3, 0.55
# Step 2: lab_worker.py - Find and change hardcoded 0.3, 0.55
# Step 3: workers.py - Check if formation needs updating
# Step 4: Verify no other files hardcode these values
# Step 5: Run tests to catch inconsistencies
# Risk: Easy to miss one, causing subtle bugs
```

### After (Single Source)
```python
# Change ballast from [0.3, 0.55] to [0.4, 0.60]
# Step 1: Edit src/layer_config.py:
#   BALLAST = LayerDefinition(
#       y_bottom=0.4,  # Changed
#       y_top=0.60,    # Changed
#   )
# Step 2: Done! All workers automatically use new values.
# Risk: Zero risk of inconsistency
```

---

## Testing with Different Coordinates

Single source of truth makes testing easy:

```python
import pytest
from src.layer_config import LayerStack

class TestStripPackingWithDifferentLayers:
    
    def test_with_default_ballast(self):
        """Test with default ballast layer [0.3, 0.55]"""
        ballast = LayerStack.BALLAST
        assert ballast.y_bottom == 0.3
        assert ballast.y_top == 0.55
        # Run packing test...
    
    def test_with_thick_ballast(self):
        """Test with thicker ballast [0.3, 0.7]"""
        # Temporarily override
        original_ballast = LayerStack.BALLAST
        try:
            LayerStack._overrides = {
                "ballast_top": 0.7
            }
            ballast = LayerStack.BALLAST
            assert ballast.y_top == 0.7
            # Run packing test...
        finally:
            LayerStack._overrides = {}
    
    def test_with_deep_ballast(self):
        """Test with deeper ballast [0.2, 0.6]"""
        # Different bottom coordinate
        # No changes to test code, just change LayerStack
```

---

## Comparison: Architecture Options

| Aspect | Scattered | Config File | LayerStack Class |
|--------|-----------|-------------|------------------|
| **Single source** | ✗ No | ✓ Yes | ✓ Yes |
| **Easy to change** | ✗ Hard | ✓ Very easy | ✓ Very easy |
| **Type safety** | ✗ None | ~ Loose | ✓ Strong |
| **IDE support** | ✗ None | ~ Limited | ✓ Full autocomplete |
| **Testing** | ✗ Hard | ✓ Easy | ✓ Easy |
| **No file I/O** | ✓ Fast | ✗ Slower | ✓ Fast |
| **Flexibility** | ✗ Low | ✓ High | ~ Medium |
| **Learning curve** | ✗ None | ✓ Minimal | ✓ Minimal |

**Recommendation: LayerStack class (Approach 1)**
- Simple Python code (no YAML/config files)
- Strong type safety
- Full IDE support
- All benefits of centralization
- Easy to understand
- Zero runtime overhead

---

## Implementation Example

Complete working implementation:

```python
# src/layer_config.py

from dataclasses import dataclass
from typing import Optional, List
from .rock_model import PackingBounds


@dataclass
class LayerDefinition:
    """Single material layer with absolute world coordinates."""
    
    name: str
    y_bottom: float
    y_top: float
    material_code: str
    description: str
    
    @property
    def height(self) -> float:
        """Height of this layer."""
        return self.y_top - self.y_bottom
    
    def contains(self, y: float) -> bool:
        """Check if y is within this layer."""
        return self.y_bottom <= y <= self.y_top
    
    def bounds(self, domain_x: float) -> PackingBounds:
        """Get layer bounds in world coordinates."""
        return PackingBounds(0, domain_x, self.y_bottom, self.y_top)
    
    def local_bounds(self, domain_x: float) -> PackingBounds:
        """Get layer bounds in local coordinates."""
        return PackingBounds(0, domain_x, 0, self.height)


class LayerStack:
    """SINGLE SOURCE OF TRUTH for all layer coordinates.
    
    All workers reference this class for layer definitions.
    Change coordinates in ONE place, all workers automatically use new values.
    """
    
    # Define all layers once
    SUBGRADE = LayerDefinition(
        name="subgrade",
        y_bottom=0.0,
        y_top=0.2,
        material_code="subgrade",
        description="Foundation layer"
    )
    
    FORMATION = LayerDefinition(
        name="formation",
        y_bottom=0.2,
        y_top=0.3,
        material_code="formation",
        description="Transition layer"
    )
    
    BALLAST = LayerDefinition(
        name="ballast",
        y_bottom=0.3,
        y_top=0.55,
        material_code="ballast_rock",
        description="Ballast layer containing rocks"
    )
    
    ALL_LAYERS = [SUBGRADE, FORMATION, BALLAST]
    
    @classmethod
    def get_layer(cls, name: str) -> Optional[LayerDefinition]:
        """Get layer by name."""
        for layer in cls.ALL_LAYERS:
            if layer.name == name:
                return layer
        return None
    
    @classmethod
    def find_layer_at(cls, y: float) -> Optional[LayerDefinition]:
        """Find which layer a y-coordinate is in."""
        for layer in cls.ALL_LAYERS:
            if layer.contains(y):
                return layer
        return None
    
    @classmethod
    def validate(cls) -> List[str]:
        """Validate layer configuration.
        
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        
        # Check contiguity
        for i in range(len(cls.ALL_LAYERS) - 1):
            curr = cls.ALL_LAYERS[i]
            next_layer = cls.ALL_LAYERS[i + 1]
            if curr.y_top != next_layer.y_bottom:
                errors.append(
                    f"Gap between {curr.name} ({curr.y_top}) "
                    f"and {next_layer.name} ({next_layer.y_bottom})"
                )
        
        # Check valid heights
        for layer in cls.ALL_LAYERS:
            if layer.height <= 0:
                errors.append(
                    f"{layer.name} has invalid height: {layer.height}"
                )
        
        return errors


# Validate at import time
_validation_errors = LayerStack.validate()
if _validation_errors:
    raise RuntimeError(
        f"Invalid layer configuration:\n" +
        "\n".join(_validation_errors)
    )
```

---

## Summary

**Single source of truth = LayerStack class**

All workers reference `LayerStack.BALLAST`, `LayerStack.SUBGRADE`, etc.

When you change a coordinate:
1. Edit one line in `src/layer_config.py`
2. All workers automatically use the new value
3. No risk of inconsistency
4. Easy to test with different configurations

This solves the tight coupling problem by providing:
- ✓ Centralized definition (one place to change)
- ✓ Easy validation (check consistency automatically)
- ✓ Type safety (IDE autocomplete)
- ✓ Loose coupling (workers don't know absolute values)
- ✓ Testing flexibility (override values for tests)

Next: Would you like me to implement this in the actual codebase?

# Migration Guide: Move to Single Source of Truth

## Overview

Current state: Coordinates scattered throughout codebase
Goal state: All coordinates in one `LayerStack` class

Effort: ~2-3 hours for full migration
Risk: Low (backward compatible, can migrate piece by piece)

---

## Phase 1: Add LayerStack Module (15 min)

### Create: `src/layer_config.py`

```python
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class LayerDefinition:
    """A material layer with absolute world coordinates."""
    
    name: str
    y_bottom: float
    y_top: float
    material_code: str
    
    @property
    def height(self) -> float:
        return self.y_top - self.y_bottom
    
    def contains(self, y: float) -> bool:
        return self.y_bottom <= y <= self.y_top
    
    def bounds(self, domain_x: float):
        from .rock_model import PackingBounds
        return PackingBounds(
            x_min=0.0, x_max=domain_x,
            y_min=self.y_bottom, y_max=self.y_top
        )


class LayerStack:
    """Single source of truth for layer coordinates."""
    
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
    
    ALL = [SUBGRADE, FORMATION, BALLAST]
    
    @classmethod
    def validate(cls) -> List[str]:
        """Validate layer configuration."""
        errors = []
        for i in range(len(cls.ALL) - 1):
            if cls.ALL[i].y_top != cls.ALL[i+1].y_bottom:
                errors.append(f"Gap between layers {i} and {i+1}")
        return errors


# Validate on import
_errors = LayerStack.validate()
if _errors:
    raise RuntimeError(f"Invalid layers: {_errors}")
```

---

## Phase 2: Migrate SubgradeWorker (10 min)

### Before
```python
# workers.py
class SubgradeWorker(Worker):
    def execute(self, scene, params, materials, tools):
        # Hardcoded value ✗
        subgrade_top = 0.2
        
        scene.add_geometry(BoxCommand(
            0, 0, 0.0,
            domain_x, subgrade_top, domain_z,
            MC.SUBGRADE
        ))
```

### After
```python
# workers.py
from src.layer_config import LayerStack

class SubgradeWorker(Worker):
    def execute(self, scene, params, materials, tools):
        # Reference single source ✓
        subgrade = LayerStack.SUBGRADE
        
        scene.add_geometry(BoxCommand(
            0, subgrade.y_bottom, 0.0,
            domain_x, subgrade.y_top, domain_z,
            MC.SUBGRADE
        ))
```

---

## Phase 3: Migrate FormationWorker (10 min)

### Before
```python
class FormationWorker(Worker):
    def execute(self, scene, params, materials, tools):
        formation_bottom = 0.2  # ✗ Hardcoded
        formation_top = 0.3     # ✗ Hardcoded
        
        scene.add_geometry(BoxCommand(
            0, formation_bottom, 0.0,
            domain_x, formation_top, domain_z,
            MC.FORMATION
        ))
```

### After
```python
from src.layer_config import LayerStack

class FormationWorker(Worker):
    def execute(self, scene, params, materials, tools):
        formation = LayerStack.FORMATION  # ✓ Single source
        
        scene.add_geometry(BoxCommand(
            0, formation.y_bottom, 0.0,
            domain_x, formation.y_top, domain_z,
            MC.FORMATION
        ))
```

---

## Phase 4: Migrate GranularMatrixWorker (20 min)

### Before
```python
# granular_worker.py
class GranularMatrixWorker(Worker):
    def execute(self, scene, params, materials, tools):
        # Multiple hardcoded values ✗
        start_y = scene.metadata.get('ballast_bottom_y', 0.5)
        ballast_thickness = scene.metadata.get('ballast_thickness', 0.4)
        top_y = start_y + ballast_thickness
        
        bounds = PackingBounds(0.0, domain_x, start_y, top_y)
        
        packer = tools.get_tool("rock_packer")
        rocks = packer.generate_rocks(bounds, ...)
```

### After
```python
# granular_worker.py
from src.layer_config import LayerStack

class GranularMatrixWorker(Worker):
    def execute(self, scene, params, materials, tools):
        # Reference single source ✓
        ballast = LayerStack.BALLAST
        bounds = ballast.bounds(domain_x)  # Get bounds directly!
        
        packer = tools.get_tool("rock_packer")
        rocks = packer.generate_rocks(bounds, ...)
        
        # Store in work_order for other workers
        scene.work_order.set('ballast_bottom_y', ballast.y_bottom, self.name)
        scene.work_order.set('ballast_top_y', ballast.y_top, self.name)
```

---

## Phase 5: Migrate LabWorker (15 min)

### Before
```python
# lab_worker.py
class LabWorker(Worker):
    def execute(self, scene, params, materials, tools):
        # Hardcoded sampling region ✗
        ballast_bottom = scene.metadata.get('ballast_bottom_y', 0.5)
        ballast_top = scene.metadata.get('ballast_top_y', 0.9)
        
        for rock in scene.rock_positions:
            if ballast_bottom <= rock.y <= ballast_top:
                samples_in_ballast.append(rock)
```

### After
```python
# lab_worker.py
from src.layer_config import LayerStack

class LabWorker(Worker):
    def execute(self, scene, params, materials, tools):
        # Reference single source ✓
        ballast = LayerStack.BALLAST
        
        for rock in scene.rock_positions:
            if ballast.contains(rock.y):  # Use layer method!
                samples_in_ballast.append(rock)
```

---

## Phase 6: Update Tests (30 min)

### Add validation tests
```python
# tests/test_layer_config.py

import pytest
from src.layer_config import LayerStack


class TestLayerStack:
    
    def test_layers_are_valid(self):
        """Verify layer configuration is valid."""
        errors = LayerStack.validate()
        assert errors == [], f"Invalid layers: {errors}"
    
    def test_layers_are_contiguous(self):
        """Verify no gaps between layers."""
        for i in range(len(LayerStack.ALL) - 1):
            curr = LayerStack.ALL[i]
            next_layer = LayerStack.ALL[i + 1]
            assert curr.y_top == next_layer.y_bottom, \
                f"Gap between {curr.name} and {next_layer.name}"
    
    def test_ballast_contains_check(self):
        """Verify contains() method works."""
        ballast = LayerStack.BALLAST
        assert ballast.contains(0.4)  # Inside
        assert not ballast.contains(0.2)  # Below
        assert not ballast.contains(0.6)  # Above
    
    def test_bounds_generation(self):
        """Verify bounds() creates correct PackingBounds."""
        ballast = LayerStack.BALLAST
        bounds = ballast.bounds(domain_x=2.248)
        
        assert bounds.x_min == 0.0
        assert bounds.x_max == 2.248
        assert bounds.y_min == 0.3
        assert bounds.y_max == 0.55
```

### Add integration test
```python
# tests/test_strip_packing_coordinates.py

from src.layer_config import LayerStack
from src.rock_packing import StripPackingStrategy


def test_strip_packing_respects_layer_bounds():
    """Verify strip packing uses LayerStack coordinates."""
    ballast = LayerStack.BALLAST
    bounds = ballast.bounds(domain_x=2.248)
    
    packer = StripPackingStrategy()
    rocks = packer.generate_rocks(bounds, ...)
    
    # Verify all rocks are within ballast layer
    for rock in rocks:
        assert ballast.contains(rock.y), \
            f"Rock at y={rock.y} outside ballast [{ballast.y_bottom}, {ballast.y_top}]"
```

---

## Phase 7: Update Documentation (30 min)

### Add to README.md
```markdown
## Layer Coordinates

All layer coordinates are defined in a single place: `src/layer_config.py`

This ensures consistency across the codebase. To change layer boundaries:

1. Edit `src/layer_config.py`:
   ```python
   BALLAST = LayerDefinition(
       y_bottom=0.3,    # Change here
       y_top=0.55,      # Or here
       ...
   )
   ```

2. All workers automatically use new values
3. No other files need updating

### Validation

Layer configuration is validated at import time:
```bash
python -c "from src.layer_config import LayerStack; print('✓ Valid')"
```

### Usage

```python
from src.layer_config import LayerStack

ballast = LayerStack.BALLAST
print(f"Ballast layer: [{ballast.y_bottom}, {ballast.y_top}]m")
print(f"Height: {ballast.height}m")

if ballast.contains(rock.y):
    print("Rock is in ballast layer")

bounds = ballast.bounds(domain_x=2.248)
packer.generate_rocks(bounds, ...)
```
```

---

## Summary: Before vs After

### Before (Scattered)
```
workers.py:              subgrade_top = 0.2
workers.py:              formation_bottom = 0.2
workers.py:              formation_top = 0.3
granular_worker.py:      ballast_bottom = 0.3
granular_worker.py:      ballast_thickness = 0.25
lab_worker.py:           ballast_bottom = 0.3
lab_worker.py:           ballast_top = 0.55
rock_packing.py:         strip_height = 3.2
test files:              hardcoded 0.3, 0.55

Change 0.3 → 0.4:  UPDATE 4+ FILES  (Easy to miss one)
```

### After (Single Source)
```
src/layer_config.py:     LayerStack.BALLAST.y_bottom = 0.3

Change 0.3 → 0.4:  UPDATE 1 LINE   (Can't miss it)
```

---

## Migration Checklist

- [ ] Phase 1: Create `src/layer_config.py`
- [ ] Phase 2: Migrate SubgradeWorker
- [ ] Phase 3: Migrate FormationWorker
- [ ] Phase 4: Migrate GranularMatrixWorker
- [ ] Phase 5: Migrate LabWorker
- [ ] Phase 6: Add/update tests
- [ ] Phase 7: Update documentation
- [ ] Verify: Run full pipeline test
- [ ] Cleanup: Remove any remaining hardcoded values

---

## Rollback Plan

If anything breaks, it's easy to revert:

```bash
git revert HEAD~7  # Undo all migrations
# Or selectively revert individual files
```

Each phase is independent and can be reverted individually.

---

## Benefits

✓ **Single source of truth** - Change coordinates in one place
✓ **No more bugs** - Impossible to have inconsistent coordinates
✓ **Easy testing** - Override values for different scenarios
✓ **Type safety** - IDE autocomplete for LayerStack
✓ **Validation** - Automatic consistency checks
✓ **Loose coupling** - Workers don't know absolute coordinates
✓ **Backward compatible** - Gradual migration possible

---

## Estimated Timeline

| Phase | Task | Time |
|-------|------|------|
| 1 | Create LayerStack | 15 min |
| 2 | SubgradeWorker | 10 min |
| 3 | FormationWorker | 10 min |
| 4 | GranularMatrixWorker | 20 min |
| 5 | LabWorker | 15 min |
| 6 | Tests | 30 min |
| 7 | Documentation | 30 min |
| | **Total** | **2.5 hours** |

Plus verification and cleanup: ~30 min

**Total: ~3 hours for complete migration**

---

## Next Steps

Ready to implement? Start with Phase 1:
1. Create `src/layer_config.py` with LayerStack class
2. Add validation test
3. Migrate workers one by one
4. Run full test suite

This eliminates the tight coupling issue and makes the codebase more maintainable.

# Layer Management — Refactoring Action Plan

## Executive Summary

Remove the old static layer system (`layer_config.py`) and eliminate fallback code in workers. **Estimated time: 1 hour**

---

## Step-by-Step Refactoring

### Step 1: Update granular_worker.py

**File:** `src/granular_worker.py`

**Action:** Remove fallback pattern, use only new system

**Current Code (lines 1-50):**
```python
from .worker import Worker, SceneCheckpoint
from .gpr_commands import CylinderCommand, BoxCommand, SoilPeplinskiCommand, FractalBoxCommand
from .constants import MC, PC
from .physics import classify_pvc
from .rock_model import PackingBounds, Rock
from .layer_config import LayerStack              # ← DELETE THIS LINE
from .rock_loader import RockLoader
```

**After:**
```python
from .worker import Worker, SceneCheckpoint
from .gpr_commands import CylinderCommand, BoxCommand, SoilPeplinskiCommand, FractalBoxCommand
from .constants import MC, PC
from .physics import classify_pvc
from .rock_model import PackingBounds, Rock
from .rock_loader import RockLoader
# (no layer_config import)
```

**Current Code (lines 40-50):**
```python
        # 1. Resolve geometry bounds
        if scene.coordinate_system:
            from src.domain import Layer
            bounds_obj = scene.coordinate_system.bounds(Layer.BALLAST)
            start_y, top_y = bounds_obj.bottom, bounds_obj.top
        else:
            ballast = LayerStack.BALLAST
            start_y = scene.metadata.get('ballast_bottom_y', ballast.y_bottom)
            ballast_thickness = scene.metadata.get('ballast_thickness', ballast.height)
            top_y = start_y + ballast_thickness
```

**After:**
```python
        # 1. Resolve geometry bounds
        from src.domain import Layer
        bounds_obj = scene.coordinate_system.bounds(Layer.BALLAST)
        start_y, top_y = bounds_obj.bottom, bounds_obj.top
```

**Rationale:** 
- Remove 5 lines of fallback code
- Eliminate `if scene.coordinate_system:` check
- ProductionLine always initializes coordinate_system, so this is safe

---

### Step 2: Update lab_worker.py

**File:** `src/lab_worker.py`

**Action:** Remove old LayerStack import, use coordinate_system

**Current Code (lines 1-20):**
```python
import numpy as np
from typing import List, Dict, Any
from .worker import Worker, SceneCheckpoint
from .constants import PC, MC, PHC
from .physics import circle_strip_intersection, classify_fouling_index
from .layer_config import LayerStack              # ← DELETE THIS LINE
import math
import json
```

**After:**
```python
import numpy as np
from typing import List, Dict, Any
from .worker import Worker, SceneCheckpoint
from .constants import PC, MC, PHC
from .physics import circle_strip_intersection, classify_fouling_index
import math
import json
```

**Current Code (lines 30-50):**
```python
        # 1. Define Sampling Layer
        # BallastWorker writes ballast bounds to the work_order blackboard, not to
        # scene.metadata, so prefer the blackboard with scene.metadata as fallback.
        ballast = LayerStack.BALLAST
        ballast_bottom = scene.metadata.get('ballast_bottom_y', ballast.y_bottom)
        ballast_thickness = scene.metadata.get('ballast_thickness', ballast.height)
        if scene.work_order:
            ballast_bottom    = scene.work_order.get('ballast_bottom_y',  ballast_bottom)
            ballast_thickness = scene.work_order.get('ballast_thickness', ballast_thickness)
        ballast_top = ballast_bottom + ballast_thickness
```

**After:**
```python
        # 1. Define Sampling Layer
        # Use coordinate_system as single source of truth for layer geometry
        from src.domain import Layer
        ballast_bounds = scene.coordinate_system.bounds(Layer.BALLAST)
        ballast_bottom = ballast_bounds.bottom
        ballast_thickness = ballast_bounds.height
        ballast_top = ballast_bounds.top
        
        # Check work_order override (if present)
        if scene.work_order:
            wo_bottom = scene.work_order.get('ballast_bottom_y', None)
            wo_thickness = scene.work_order.get('ballast_thickness', None)
            if wo_bottom is not None:
                ballast_bottom = wo_bottom
            if wo_thickness is not None:
                ballast_thickness = wo_thickness
            wo_top = scene.work_order.get('ballast_top_y', None)
            if wo_top is not None:
                ballast_top = wo_top
```

**Rationale:**
- Use coordinate_system as primary (not fallback)
- Still support work_order overrides (for runtime customization)
- More explicit and maintainable

---

### Step 3: Add Validation to CoordinateSystem

**File:** `src/domain/coordinates.py`

**Current Code:**
```python
class CoordinateSystem:
    def __init__(self, layer_stack: LayerStack, domain_x: float = 1.0, domain_z: float = 0.005):
        self.stack = layer_stack
        self.domain_x = domain_x
        self.domain_z = domain_z
        
        # Precompute absolute Y levels
        self._y_levels: Dict[Anchor, float] = {}
        self._compute_levels()
```

**After:**
```python
class CoordinateSystem:
    def __init__(self, layer_stack: LayerStack, domain_x: float = 1.0, domain_z: float = 0.005):
        self.stack = layer_stack
        self.domain_x = domain_x
        self.domain_z = domain_z
        
        # Validate layer stack before computing levels
        errors = self._validate_layer_stack()
        if errors:
            raise ValueError(f"Invalid layer stack configuration:\n" + "\n".join(f"  - {e}" for e in errors))
        
        # Precompute absolute Y levels
        self._y_levels: Dict[Anchor, float] = {}
        self._compute_levels()
    
    def _validate_layer_stack(self) -> List[str]:
        """Validate layer configuration for consistency.
        
        Returns:
            List of error messages (empty if valid)
        """
        errors = []
        
        if self.stack.subgrade_thickness <= 0:
            errors.append(f"subgrade_thickness must be positive, got {self.stack.subgrade_thickness}")
        
        if self.stack.formation_thickness <= 0:
            errors.append(f"formation_thickness must be positive, got {self.stack.formation_thickness}")
        
        if self.stack.ballast_thickness <= 0:
            errors.append(f"ballast_thickness must be positive, got {self.stack.ballast_thickness}")
        
        if self.stack.antenna_clearance < 0:
            errors.append(f"antenna_clearance must be non-negative, got {self.stack.antenna_clearance}")
        
        if self.stack.air_buffer < 0:
            errors.append(f"air_buffer must be non-negative, got {self.stack.air_buffer}")
        
        # Check that total height doesn't exceed reasonable bounds
        total = self.stack.total_height
        if total > 10.0:  # More than 10 meters
            errors.append(f"total_height exceeds 10m: {total}m")
        
        if total < 0.5:  # Less than 50 cm
            errors.append(f"total_height below 50cm: {total}m")
        
        return errors
```

**Rationale:**
- Validate at construction time (fail fast)
- Explicit error messages
- Catches misconfigurations immediately

---

### Step 4: Ensure LayerBounds Has .height Property

**File:** `src/domain/coordinates.py`

**Current Code:**
```python
@dataclass(frozen=True)
class LayerBounds:
    bottom: float
    top: float
    
    @property
    def height(self) -> float:
        return self.top - self.bottom
    
    @property
    def center(self) -> float:
        return (self.top + self.bottom) / 2
```

**Verify this exists** — it should already be there. If not, add the `height` property above.

---

### Step 5: Delete layer_config.py

```bash
rm src/layer_config.py
```

**Verify it's gone:**
```bash
ls -la src/layer_config.py  # Should show "No such file"
```

---

### Step 6: Run Tests

```bash
# Run all tests
pytest tests/ -v

# Run specifically layer-related tests
pytest tests/unit/test_domain/ -v
pytest tests/integration/ -v

# Test key scenarios
pytest tests/integration/test_production_line.py -v
```

**Expected Results:**
- ✓ All tests pass
- ✓ No import errors
- ✓ No fallback code executed

---

## Verification Checklist

After completing all steps:

- [ ] Line 1: `from .layer_config import LayerStack` **removed** from `granular_worker.py`
- [ ] Line 16: `from .layer_config import LayerStack` **removed** from `lab_worker.py`
- [ ] Fallback code (5 lines) **removed** from `granular_worker.py` (lines 42-50)
- [ ] Old fallback code **removed** from `lab_worker.py` (lines 38-48)
- [ ] Validation method **added** to `CoordinateSystem._validate_layer_stack()`
- [ ] File `src/layer_config.py` **deleted**
- [ ] All tests pass: `pytest tests/ -v`
- [ ] Git diff shows only the intended changes: `git diff src/`

---

## Exact git Commands (If Using Version Control)

```bash
# 1. Remove imports
git checkout HEAD -- src/granular_worker.py
# (Edit granular_worker.py to remove layer_config import and fallback code)

git checkout HEAD -- src/lab_worker.py
# (Edit lab_worker.py to remove layer_config import and fallback code)

# 2. Add validation
git checkout HEAD -- src/domain/coordinates.py
# (Edit coordinates.py to add _validate_layer_stack method)

# 3. Delete old file
rm src/layer_config.py
git add -A

# 4. Verify changes
git status
git diff --cached

# 5. Run tests before committing
pytest tests/ -v

# 6. Commit
git commit -m "Refactor: Remove legacy layer_config.py, consolidate on CoordinateSystem

- Delete src/layer_config.py (legacy static layer system)
- Remove fallback code from granular_worker.py
- Remove fallback code from lab_worker.py  
- Add validation to CoordinateSystem._validate_layer_stack()
- Single source of truth: now only domain/coordinates.py LayerStack

Fixes potential coordinate drift and silent failures from dual systems."
```

---

## What Gets Simpler

### Before (Dual System)
```python
# granular_worker.py
if scene.coordinate_system:
    bounds = scene.coordinate_system.bounds(Layer.BALLAST)
else:
    ballast = LayerStack.BALLAST  # From layer_config.py
    bounds = (ballast.y_bottom, ballast.y_top)

# lab_worker.py
ballast = LayerStack.BALLAST  # From layer_config.py
ballast_bottom = scene.metadata.get('ballast_bottom_y', ballast.y_bottom)

# Maintenance
# - 2 files to update when changing layer thickness
# - layer_config.py and config.py must stay in sync
# - Easy to forget one
```

### After (Single System)
```python
# granular_worker.py
bounds = scene.coordinate_system.bounds(Layer.BALLAST)

# lab_worker.py
ballast_bounds = scene.coordinate_system.bounds(Layer.BALLAST)

# Maintenance
# - 1 file to update: config.py determines layer thicknesses
# - domain/coordinates.py computes from config
# - Always in sync, no manual synchronization needed
```

---

## Rollback Plan (If Needed)

If something breaks, you can revert:

```bash
# Option 1: Revert last commit
git revert HEAD

# Option 2: Restore specific files from last commit
git checkout HEAD~1 -- src/granular_worker.py
git checkout HEAD~1 -- src/lab_worker.py
git checkout HEAD~1 -- src/layer_config.py
```

---

## Expected Outcome

✅ **Single source of truth for layer geometry**
- Config defines thicknesses
- CoordinateSystem computes absolute coordinates
- All workers use CoordinateSystem
- No fallback code
- No silent failures

✅ **Simpler maintenance**
- Change layer thickness → update config.py only
- Automatic propagation to all workers
- No synchronization needed

✅ **Better error handling**
- Invalid layers caught at CoordinateSystem init
- Fail fast with clear error messages
- No mysterious coordinate mismatches

---

## Time Estimate

| Task | Time |
|------|------|
| Edit granular_worker.py | 5 min |
| Edit lab_worker.py | 5 min |
| Add validation to CoordinateSystem | 5 min |
| Run tests | 10 min |
| Git commit | 5 min |
| **Total** | **~30 min** |

Plus buffer for any issues: **1 hour total**


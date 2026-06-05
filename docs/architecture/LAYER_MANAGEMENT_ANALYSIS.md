# Layer Management Architecture — Analysis & Refactoring Guide

## Executive Summary

**Critical Finding:** The codebase has **TWO CONFLICTING layer management systems** in a transitional state:

1. **Old System** (`src/layer_config.py`) — Static, hardcoded layer coordinates
2. **New System** (`src/domain/coordinates.py`) — Dynamic, configurable layer thicknesses

**Status:** Partially refactored. New system is being used in core workers, but old system remains as fallback.

**Risk:** Potential inconsistencies if both systems are used simultaneously.

---

## Layer Management Systems

### System 1: Old — layer_config.py (Static, Hardcoded)

```python
# src/layer_config.py

@dataclass
class LayerDefinition:
    name: str
    y_bottom: float
    y_top: float
    material_code: str

class LayerStack:
    # HARDCODED ABSOLUTE COORDINATES
    SUBGRADE = LayerDefinition(
        name="subgrade",
        y_bottom=0.0,
        y_top=0.2,  # ← Fixed!
        material_code="subgrade"
    )
    
    FORMATION = LayerDefinition(
        name="formation",
        y_bottom=0.2,
        y_top=0.3,  # ← Fixed!
        material_code="formation"
    )
    
    BALLAST = LayerDefinition(
        name="ballast",
        y_bottom=0.3,
        y_top=0.55,  # ← Fixed!
        material_code="ballast_rock"
    )
    
    ALL = [SUBGRADE, FORMATION, BALLAST]
    
    @classmethod
    def validate(cls) -> List[str]:
        """Check for gaps, non-positive heights"""
        pass
```

**Problems:**
- ❌ Hardcoded absolute coordinates (0.2, 0.3, 0.55)
- ❌ Breaks if config changes layer thicknesses
- ❌ No flexibility for different domain heights
- ✓ Type-safe (LayerDefinition value objects)
- ✓ Validates on import

**Used By:**
- `src/granular_worker.py` (line 47) — fallback
- `src/lab_worker.py` (line 16, 38) — fallback

---

### System 2: New — domain/coordinates.py (Dynamic, Configurable)

```python
# src/domain/coordinates.py

@dataclass(frozen=True)
class LayerStack:
    # CONFIGURABLE THICKNESSES
    subgrade_thickness: float = 0.20
    formation_thickness: float = 0.10
    ballast_thickness: float = 0.25
    antenna_clearance: float = 0.5
    air_buffer: float = 0.1
    
    @property
    def total_height(self) -> float:
        """Computed: sum of all thicknesses"""
        return (self.subgrade_thickness + 
                self.formation_thickness + 
                self.ballast_thickness + 
                self.antenna_clearance + 
                self.air_buffer)

class CoordinateSystem:
    """Resolves semantic anchors to absolute coordinates"""
    
    def __init__(self, layer_stack: LayerStack, domain_x, domain_z):
        self.stack = layer_stack
        self._y_levels = {}  # Precomputed Anchor → float
        self._compute_levels()  # From LayerStack thicknesses
    
    def get_y(self, anchor: Anchor) -> float:
        """BALLAST_TOP → 0.55 (computed from thicknesses)"""
        return self._y_levels[anchor]
    
    def bounds(self, layer: Layer) -> LayerBounds:
        """Type-safe layer lookup"""
        # Layer.BALLAST → LayerBounds(0.30, 0.55)
        pass

class Layer(Enum):
    SUBGRADE = "subgrade"
    FORMATION = "formation"
    BALLAST = "ballast"
    AIR = "air"

class Anchor(Enum):
    BOTTOM = "bottom"
    SUBGRADE_TOP = "subgrade_top"
    FORMATION_TOP = "formation_top"
    BALLAST_BOTTOM = "ballast_bottom"
    BALLAST_TOP = "ballast_top"
    ANTENNA_LEVEL = "antenna_level"
    DOMAIN_TOP = "domain_top"
```

**Advantages:**
- ✓ Configurable thicknesses (parameter-driven)
- ✓ Single source of truth (LayerStack)
- ✓ Type-safe (Enum anchors, frozen dataclass)
- ✓ Extensible (add new anchors/layers)
- ✓ Immutable (frozen=True)

**Used By:**
- `src/workers.py` (main pattern)
- `src/production_line.py` (initialization)

---

## How They're Currently Used

### Pattern: Try New, Fall Back to Old

Both workers using the old system implement the same fallback pattern:

#### In granular_worker.py (lines 42-50):
```python
def execute(self, scene, params, materials, tools):
    # 1. RESOLVE GEOMETRY BOUNDS
    if scene.coordinate_system:
        # NEW SYSTEM: Use dynamic coordinates
        from src.domain import Layer
        bounds_obj = scene.coordinate_system.bounds(Layer.BALLAST)
        start_y, top_y = bounds_obj.bottom, bounds_obj.top
    else:
        # OLD SYSTEM: Use static fallback
        ballast = LayerStack.BALLAST  # ← From layer_config.py
        start_y = scene.metadata.get('ballast_bottom_y', ballast.y_bottom)
        ballast_thickness = scene.metadata.get('ballast_thickness', ballast.height)
        top_y = start_y + ballast_thickness
```

#### In lab_worker.py (lines 38-46):
```python
def execute(self, scene, params, materials, tools):
    # 1. DEFINE SAMPLING LAYER
    ballast = LayerStack.BALLAST  # ← From layer_config.py
    ballast_bottom = scene.metadata.get('ballast_bottom_y', ballast.y_bottom)
    ballast_thickness = scene.metadata.get('ballast_thickness', ballast.height)
    if scene.work_order:
        ballast_bottom = scene.work_order.get('ballast_bottom_y', ballast_bottom)
        ballast_thickness = scene.work_order.get('ballast_thickness', ballast_thickness)
    ballast_top = ballast_bottom + ballast_thickness
```

---

## The Refactoring Path

### Current State (Partial Refactoring)

```
┌─────────────────────────────────────────────────────┐
│                  PRODUCTION LINE                     │
├─────────────────────────────────────────────────────┤
│                                                     │
│ ✓ LayerStack (domain/coordinates.py) initialized   │
│ ✓ CoordinateSystem created from LayerStack         │
│ ✓ Attached to SceneCheckpoint                      │
│                                                     │
│ → Workers check: "Is coordinate_system available?"  │
│                                                     │
│   ✓ If YES (most workers):                         │
│     Use: scene.coordinate_system.bounds(Layer.X)   │
│     Source: NEW system (domain/coordinates.py)     │
│                                                     │
│   ✗ If NO (fallback for GranularMatrixWorker,     │
│     LabWorker):                                     │
│     Use: LayerStack.BALLAST.y_bottom              │
│     Source: OLD system (layer_config.py)           │
│                                                     │
└─────────────────────────────────────────────────────┘
```

### Why This Happened

1. **Initial Design** — Used static LayerStack (layer_config.py)
2. **Problem Identified** — Static coordinates too inflexible
3. **New System Created** — Dynamic CoordinateSystem (domain/coordinates.py)
4. **Migration Started** — Core pipeline refactored to new system
5. **Incomplete** — Some workers still have old fallback code

---

## Risks of Current State

### Risk 1: Coordinate Drift

If old and new systems configured differently:

```python
# OLD SYSTEM (layer_config.py)
BALLAST = LayerDefinition(y_bottom=0.3, y_top=0.55)

# NEW SYSTEM (domain/coordinates.py)
LayerStack(
    subgrade_thickness=0.20,      # 0.0 → 0.20
    formation_thickness=0.10,     # 0.20 → 0.30
    ballast_thickness=0.35,       # 0.30 → 0.65  ← DIFFERENT!
)
# BALLAST computed as: 0.30 → 0.65
```

**Result:** 
- New system: ballast_top = 0.65 m
- Old system: ballast_top = 0.55 m
- **Inconsistency: 10 cm difference!**

### Risk 2: Silent Failures

GranularMatrixWorker prefers new system, falls back to old if missing:

```python
if scene.coordinate_system:
    # Uses NEW system (e.g., ballast_top = 0.65)
    bounds_obj = scene.coordinate_system.bounds(Layer.BALLAST)
else:
    # Falls back to OLD system (e.g., ballast_top = 0.55)
    ballast = LayerStack.BALLAST
```

**If coordinate_system is accidentally missing:**
- Geometry generated using OLD coordinates
- Rocks and antennas positioned incorrectly
- No error raised (fallback silently activates)
- Bug is subtle and hard to find

### Risk 3: Maintenance Burden

Two systems to maintain and update:

- Change ballast thickness?
  - Update `config.py` (GeneratorConfig)
  - Update `domain/coordinates.py` (LayerStack dataclass)
  - Update `layer_config.py` (LayerStack class) ← Easy to forget!
  - Validate both systems match

---

## Current Usage by File

| File | Old System | New System | Pattern |
|------|-----------|-----------|---------|
| production_line.py | ❌ No | ✓ Yes | Primary |
| workers.py | ❌ No | ✓ Yes | Primary |
| granular_worker.py | ✓ Fallback | ✓ Primary | Try new, fall back to old |
| lab_worker.py | ✓ Fallback | ❌ No | Uses old + work_order/metadata |
| All other workers | ❌ No | ✓ Yes | Primary |

---

## Recommended Refactoring

### Phase 1: Eliminate Old System (Immediate)

**Goal:** Remove `layer_config.py`, use only new system everywhere.

**Steps:**

1. **Update granular_worker.py** (remove fallback):
```python
# BEFORE
if scene.coordinate_system:
    bounds_obj = scene.coordinate_system.bounds(Layer.BALLAST)
    start_y, top_y = bounds_obj.bottom, bounds_obj.top
else:
    ballast = LayerStack.BALLAST  # ← DELETE THIS
    start_y = ballast.y_bottom
    top_y = ballast.y_top

# AFTER
bounds_obj = scene.coordinate_system.bounds(Layer.BALLAST)
start_y, top_y = bounds_obj.bottom, bounds_obj.top
# Ensure coordinate_system is always set in ProductionLine.__init__
```

2. **Update lab_worker.py** (remove fallback):
```python
# BEFORE
ballast = LayerStack.BALLAST
ballast_bottom = scene.metadata.get('ballast_bottom_y', ballast.y_bottom)
ballast_thickness = scene.metadata.get('ballast_thickness', ballast.height)

# AFTER
bounds_obj = scene.coordinate_system.bounds(Layer.BALLAST)
ballast_bottom = bounds_obj.bottom
ballast_thickness = bounds_obj.height  # LayerBounds has .height property
```

3. **Delete `src/layer_config.py`:**
```bash
rm src/layer_config.py
```

4. **Remove import from granular_worker.py:**
```python
# DELETE THIS LINE
from .layer_config import LayerStack
```

5. **Remove import from lab_worker.py:**
```python
# DELETE THIS LINE
from .layer_config import LayerStack
```

6. **Update LayerBounds in domain/coordinates.py to ensure .height property:**
```python
@dataclass(frozen=True)
class LayerBounds:
    bottom: float
    top: float
    
    @property
    def height(self) -> float:
        return self.top - self.bottom
```

### Phase 2: Validate Layer Consistency (Follow-up)

**Goal:** Add runtime validation that layer thicknesses are sensible.

**Add to ProductionLine.__init__:**
```python
def __init__(self, config: GeneratorConfig):
    # ... existing code ...
    
    # Validate layer configuration
    layer_stack = LayerStack(
        subgrade_thickness=config.subgrade_thickness,
        formation_thickness=config.formation_thickness,
        ballast_thickness=config.max_ballast_thickness,
        antenna_clearance=config.antenna_clearance_above_ballast,
        air_buffer=0.1
    )
    
    # Check total height vs domain_y
    if config.domain_y < layer_stack.total_height:
        raise ValueError(
            f"Domain height {config.domain_y}m insufficient for "
            f"layer stack {layer_stack.total_height}m"
        )
```

### Phase 3: Centralize Layer Configuration (Nice-to-Have)

**Goal:** Single place to define all layer parameters.

**Option A: Migrate to config.py**
```python
# src/config.py
@dataclass
class GeneratorConfig:
    # Domain
    domain_x: float = 2.248
    domain_y: float = 3.199
    domain_z: float = 0.0132
    
    # Layer thicknesses (already here)
    subgrade_thickness: float = 0.20
    formation_thickness: float = 0.10
    max_ballast_thickness: float = 0.55
    
    # Antenna
    antenna_clearance_above_ballast: float = 0.5
    
    def get_layer_stack(self) -> LayerStack:
        """Create LayerStack from this config"""
        return LayerStack(
            subgrade_thickness=self.subgrade_thickness,
            formation_thickness=self.formation_thickness,
            ballast_thickness=self.max_ballast_thickness,
            antenna_clearance=self.antenna_clearance_above_ballast,
            air_buffer=0.1
        )
```

Then in ProductionLine:
```python
layer_stack = self.config.get_layer_stack()
coords = CoordinateSystem(layer_stack, self.config.domain_x, self.config.domain_z)
```

---

## Validation Approach

### For Old System (layer_config.py)

Validates on import (happens immediately):

```python
_validation_errors = LayerStack.validate()
if _validation_errors:
    raise RuntimeError(f"Invalid layer configuration: {_validation_errors}")
```

**Checks:**
- No gaps between layers (y_top[i] == y_bottom[i+1])
- All layers have positive height

### For New System (domain/coordinates.py)

No built-in validation! **Recommend adding:**

```python
class CoordinateSystem:
    def __init__(self, layer_stack: LayerStack, domain_x, domain_z):
        self.stack = layer_stack
        
        # Validate layer stack
        errors = self._validate_layer_stack()
        if errors:
            raise ValueError(f"Invalid layer stack: {errors}")
        
        self._y_levels = {}
        self._compute_levels()
    
    def _validate_layer_stack(self) -> List[str]:
        """Validate layer configuration"""
        errors = []
        
        if self.stack.subgrade_thickness <= 0:
            errors.append("subgrade_thickness must be positive")
        if self.stack.formation_thickness <= 0:
            errors.append("formation_thickness must be positive")
        if self.stack.ballast_thickness <= 0:
            errors.append("ballast_thickness must be positive")
        if self.stack.antenna_clearance < 0:
            errors.append("antenna_clearance must be non-negative")
        if self.stack.air_buffer < 0:
            errors.append("air_buffer must be non-negative")
        
        return errors
```

---

## Data Consistency Map

### What Updates When You Change LayerStack

| Change | Old System | New System | Workers See |
|--------|-----------|-----------|------------|
| Increase ballast_thickness | ❌ NO | ✓ YES | ✓ YES |
| Change subgrade_thickness | ❌ NO | ✓ YES | ✓ YES |
| Modify antenna_clearance | ❌ NO | ✓ YES | ✓ YES |

**Implication:** Only NEW system is dynamic. Old system requires manual update.

---

## Recommended Timeline

### Now (Immediate)
1. ✓ Understand the dual system (this document)
2. ✓ Add validation to CoordinateSystem
3. ✓ Remove fallback from granular_worker.py & lab_worker.py
4. ✓ Delete layer_config.py

### Next Sprint
1. Add comprehensive test for layer consistency
2. Document layer configuration in README
3. Consider Phase 3 (centralizing in config.py)

### Timeline Estimate
- **Phase 1:** 30 min (code changes)
- **Testing:** 1 hour (write tests, verify no regressions)
- **Phase 2:** 1 hour (add validation)
- **Phase 3:** 2 hours (centralize config)
- **Total:** 4–5 hours

---

## Testing Checklist

After refactoring:

- [ ] Remove `from .layer_config import LayerStack` from granular_worker.py
- [ ] Remove `from .layer_config import LayerStack` from lab_worker.py
- [ ] Delete `src/layer_config.py`
- [ ] Run all tests: `pytest tests/ -v`
- [ ] Test generation with default config
- [ ] Test generation with custom ballast_thickness
- [ ] Test generation with custom antenna_clearance
- [ ] Verify coordinate_system is always set before workers run
- [ ] Verify rocks are positioned correctly
- [ ] Verify antennas don't collide with rocks

---

## Summary

**Current State:**
- ❌ Two conflicting layer systems (one old, one new)
- ⚠️ Fallback pattern masks issues (silent failure risk)
- ✓ New system is better (dynamic, type-safe, immutable)

**Recommendation:**
1. Remove old system (layer_config.py)
2. Eliminate fallback code in workers
3. Add validation to new system
4. Ensure coordinate_system always initialized

**Benefit:** Single source of truth, eliminating inconsistencies and maintenance burden.


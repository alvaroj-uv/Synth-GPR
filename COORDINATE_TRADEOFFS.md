# Coordinate System Design: Absolute vs Relative & Coupling Analysis

## Overview

The codebase uses **absolute coordinates** throughout the pipeline. This section analyzes the design trade-offs and how tightly coupled (or decoupled) this is in the code.

---

## Absolute vs Relative Coordinate Systems

### What We Use: Absolute (World Space)

All positions are in **global coordinate space** with a fixed origin:

```
y
│
3.2m ├─ Air (antenna region)
│    │
0.55m├─ Ballast layer (rocks packed here)
│    │
0.3m ├─ Formation/Subgrade
│    │
0.0m ├─ Origin (ground level)
    └─────────────────────→ x
    0.0m          2.248m
```

Example: Rock at `(x=1.2, y=0.42)` is always at the same world-space position, regardless of context.

### Alternative: Relative (Local Space)

Coordinates relative to a **parent container** or origin point:

```
Container (Ballast Layer):
  origin_y = 0.3m
  
  Rock coordinates relative to container:
  (x=1.2, y=0.12)  ← Local
  
  World position = (x=1.2, y=0.3 + 0.12 = 0.42)  ← Converted to absolute
```

---

## Pros & Cons Comparison

### Absolute Coordinates

#### ✓ PROS

| Advantage | Why It Matters |
|-----------|----------------|
| **Simplicity** | No origin offset tracking, values = positions |
| **Direct debugging** | Print rock position, see exactly where it is |
| **Physics-friendly** | Gravity, collisions work naturally in world space |
| **Multi-region operations** | Extract windows from strip without translation |
| **Loose coupling** | Workers don't depend on containers/parents |
| **Performance** | No coordinate transformations needed |

#### ✗ CONS

| Drawback | Impact |
|----------|--------|
| **Hard to relocate groups** | Moving a region requires translating ALL rocks |
| **Tightly coupled layers** | All workers must agree on absolute scale (0.3m boundary) |
| **Wasteful for sparse regions** | Can't use relative local coordinates for efficiency |
| **No encapsulation** | Every worker needs to know full coordinate space |
| **No hierarchical structure** | Hard to have nested/modular regions |
| **Brittle to changes** | Adding/removing a layer shifts all absolute y-values |

---

### Relative Coordinates

#### ✓ PROS

| Advantage | Why It Matters |
|-----------|----------------|
| **Modular/Encapsulated** | Each region defines its own space |
| **Hierarchical** | Natural parent-child relationships |
| **Relocatable** | Move entire region by changing one origin |
| **Flexible** | Nest regions at any depth |
| **Decoupled layers** | Workers don't depend on absolute layer positions |
| **Future-proof** | Adding layers doesn't require code changes |

#### ✗ CONS

| Drawback | Impact |
|----------|--------|
| **Complexity** | Need to track origins, convert between spaces |
| **Error-prone** | Easy to forget translations, off-by-one bugs |
| **Harder debugging** | Values don't match what you see without context |
| **Overhead** | Constant coordinate transformations |
| **Confusion** | Rock at (1.2, 0.42) in local space is NOT at (1.2, 0.42) in world |

---

## Current Code: Tightly Coupled Absolute System

### How It Works

```
┌─ Layer 1: BallastWorker ──────────────────────────┐
│ Calculates: ballast_bottom = 0.3m (ABSOLUTE)      │
│ Stores in work_order: ballast_bottom_y = 0.3      │
│                       ballast_top_y = 0.55         │
└──────────────────────┬────────────────────────────┘
                       ↓ (expects these absolute values)
┌─ Layer 2: GranularMatrixWorker ───────────────────┐
│ Reads: ballast_bottom = 0.3 (from work_order)     │
│ Creates: bounds = [0, 2.248] × [0.3, 0.55]       │
│          (MUST use exact same absolute values!)    │
│ Calls: packer.generate_rocks(bounds, ...)         │
│ Packs rocks: y ∈ [0.3, 0.55] (ABSOLUTE)          │
└──────────────────────┬────────────────────────────┘
                       ↓ (rocks in specific y-range)
┌─ Layer 3: LabWorker ──────────────────────────────┐
│ Reads: ballast_bottom = 0.3, ballast_top = 0.55  │
│ Samples: rocks where y ∈ [0.3, 0.55]             │
│ Expected: ALL rocks in this y-range               │
│ Calculates: PVC from sampled rocks                │
└────────────────────────────────────────────────────┘
```

### The Coupling Problem

**All three workers MUST AGREE on absolute coordinates:**

```python
# BallastWorker
ballast_bottom = 0.3  # ← Worker 1 decides this

# GranularMatrixWorker
bounds = PackingBounds(..., y_min=0.3, ...)  # ← Must use EXACT same value!

# LabWorker
samples y ∈ [0.3, 0.55]  # ← Must use EXACT same range!
```

If ANY worker uses different values, the system breaks:

```
❌ BAD: StripPackingStrategy ignores bounds
   ballast_bottom = 0.3 (from BallastWorker)
   bounds passed to packer: y_min=0.3, y_max=0.55
   
   But StripPackingStrategy does:
   strip_bounds: y_min=0.0, y_max=3.2  ← DIFFERENT!
   
   Result: Rocks at [0, 3.2], but LabWorker samples [0.3, 0.55]
           → Misalignment!

✓ GOOD: StripPackingStrategy respects bounds
   ballast_bottom = 0.3 (from BallastWorker)
   bounds passed to packer: y_min=0.3, y_max=0.55
   
   StripPackingStrategy does:
   strip_bounds: y_min=0.3, y_max=0.55  ← SAME!
   
   Result: Rocks at [0.3, 0.55], LabWorker samples [0.3, 0.55]
           → Alignment! ✓
```

---

## Coupling Analysis: How Decoupled Is It?

### Current State: TIGHTLY COUPLED

**Coupling Points** (places where changes break things):

```
1. BallastWorker output → GranularMatrixWorker input
   ├─ If BallastWorker changes ballast_bottom from 0.3 → 0.4
   ├─ GranularMatrixWorker MUST be updated to use 0.4
   ├─ LabWorker MUST be updated to sample [0.4, ...]
   └─ All packing strategies MUST respect the new value

2. Layer thickness constants
   ├─ Subgrade: 0.2m (hardcoded in SubgradeWorker)
   ├─ Formation: 0.1m (hardcoded in FormationWorker)
   ├─ Ballast: 0.25m default (in BallastWorker)
   └─ If you change any, all dependent code breaks

3. Packing strategy bounds
   ├─ If bounds.y_min ≠ actual ballast_bottom → BUG
   ├─ If bounds.y_max ≠ actual ballast_top → BUG
   └─ Every packing strategy MUST respect bounds input
```

**Coupling Strength: STRONG**

```
            BallastWorker
                  │
          ┌───────┼───────┐
          │       │       │
          ↓       ↓       ↓
       SubgradeWorker  FormationWorker  GranularMatrixWorker
                                            │
                                    ┌───────┼───────┐
                                    │       │       │
                                    ↓       ↓       ↓
                           HybridShang  StripPacking  RSAPacking
                                    │       │       │
                                    └───────┼───────┘
                                            │
                                            ↓
                                        LabWorker

Legend: → = depends on (if upstream changes, downstream breaks)
```

---

## Why the Bug Happened

### Structural Vulnerability

Absolute coordinate system + tight coupling = **vulnerable to coordinate mismatch**

When `StripPackingStrategy` ignored the `bounds` parameter:

```python
def _pack_strip(self, bounds: PackingBounds, ...):
    # bounds.y_min = 0.3 (from BallastWorker)
    # bounds.y_max = 0.55
    
    # But this code ignores bounds!
    strip_bounds = PackingBounds(
        y_min=0.0,              # ← BREAKS CONTRACT!
        y_max=self.strip_height # ← Uses different coordinate system!
    )
```

The system had **no protection** against this:
- No type checking (bounds is just an object)
- No validation (no assertion that y_min was actually used)
- No testing at layer boundaries (would have caught it)

---

## How to Reduce Coupling

### Option 1: Add Validation (Easy, Local Fix)

```python
def _pack_strip(self, bounds: PackingBounds, ...):
    # Assert that bounds are being used
    assert bounds.y_min is not None, "bounds.y_min required"
    assert bounds.y_max is not None, "bounds.y_max required"
    
    strip_bounds = PackingBounds(
        y_min=bounds.y_min,  # MUST use input bounds
        y_max=bounds.y_max
    )
```

**Coupling reduction**: Minimal (prevents THIS bug, not root cause)

### Option 2: Extract Coupling to Config (Medium Effort)

```python
class BallastConfiguration:
    """Centralized ballast layer definition"""
    ballast_bottom: float = 0.3
    ballast_height: float = 0.25
    ballast_top: float = 0.55
    
    def bounds(self, domain_x: float) -> PackingBounds:
        return PackingBounds(
            x_min=0.0, x_max=domain_x,
            y_min=self.ballast_bottom,
            y_max=self.ballast_top
        )

# All workers reference same config
class GranularMatrixWorker:
    def execute(self, scene, config: BallastConfiguration, ...):
        bounds = config.bounds(scene.domain_x)  # Single source of truth
        ...
```

**Coupling reduction**: Moderate (centralize magic numbers)

### Option 3: Switch to Relative Coordinates (Major Refactor)

```python
class BallastLayer:
    """Encapsulated layer with local origin"""
    height: float = 0.55 - 0.3  # 0.25m
    
    def local_to_world(self, y_local: float) -> float:
        return 0.3 + y_local
    
    def world_to_local(self, y_world: float) -> float:
        return y_world - 0.3

# Workers operate on local coordinates
class GranularMatrixWorker:
    def execute(self, scene, ballast_layer: BallastLayer, ...):
        # Pack at local origin
        bounds = PackingBounds(
            y_min=0.0,  # Local space
            y_max=ballast_layer.height
        )
        rocks = packer.generate_rocks(bounds, ...)
        
        # Convert to world space before storing
        for rock in rocks:
            rock.y = ballast_layer.local_to_world(rock.y)
```

**Coupling reduction**: High (complete decoupling of layer positions)

---

## Current Best Practice

### The Sweet Spot: Absolute + Explicit Contracts

The current approach (after fix) is actually good:

```python
# 1. Pass bounds explicitly (contract)
def generate_rocks(self, bounds: PackingBounds, ...) -> List[Rock]:
    """
    Pack rocks within the specified bounds.
    
    Args:
        bounds: MUST respect bounds.y_min and bounds.y_max
                Rocks will be positioned within this range.
    
    Returns:
        Rocks with absolute coordinates in [bounds.y_min, bounds.y_max]
    """
    assert bounds.y_max > bounds.y_min, "Invalid bounds"
    # Pack at bounds.y_min to bounds.y_max
    ...

# 2. Respect the contract
class StripPackingStrategy:
    def _pack_strip(self, bounds: PackingBounds, ...):
        strip_bounds = PackingBounds(
            y_min=bounds.y_min,      # Explicit use
            y_max=bounds.y_max       # Explicit use
        )
        # Pack in specified y-range
```

**Advantages:**
- Simple (no coordinate translation overhead)
- Debuggable (values match what you see)
- Safe (explicit bounds + validation)
- Loose coupling through explicit contracts

---

## Summary Table

| Aspect | Absolute | Relative |
|--------|----------|----------|
| **Simplicity** | ✓✓✓ Simple | ✗ Complex |
| **Coupling** | ✗ Tight | ✓✓ Loose |
| **Debugging** | ✓✓✓ Easy | ✗ Hard |
| **Performance** | ✓✓✓ Fast | ✗ Overhead |
| **Modularity** | ✗ Low | ✓✓ High |
| **Physics** | ✓✓ Natural | ~ Awkward |
| **Refactoring** | ✗ Brittle | ✓ Safe |
| **Learning curve** | ✓ Gentle | ✗ Steep |

---

## Recommendations for This Project

### Current Approach ✓ GOOD

Keep absolute coordinates with:

1. **Explicit bounds contracts**
   ```python
   bounds: PackingBounds  # Tell packing where to pack
   ```

2. **Validation at boundaries**
   ```python
   assert bounds.y_min == expected_ballast_bottom
   ```

3. **Testing at layer interfaces**
   ```python
   # Test that worker respects bounds
   assert all(bounds.y_min <= rock.y <= bounds.y_max 
              for rock in rocks)
   ```

4. **Documentation of coordinate systems**
   - Which absolute scale is used
   - What bounds mean
   - How to debug coordinate mismatches

### Future: Consider Gradual Decoupling

If the codebase grows (more layers, more workers):

1. **Extract layer definitions to config**
   ```python
   layer_config = {
       'subgrade': {'height': 0.2, 'y_top': 0.2},
       'formation': {'height': 0.1, 'y_top': 0.3},
       'ballast': {'height': 0.25, 'y_top': 0.55},
   }
   ```

2. **Create layer wrapper classes**
   ```python
   class Layer:
       def local_bounds(self) -> PackingBounds:
           return PackingBounds(0, ..., 0, self.height)
   ```

3. **Gradually migrate workers to use config**
   ```python
   # Old: hardcoded absolute
   bounds = [0, domain_x, 0.3, 0.55]
   
   # New: from config
   bounds = config.get_layer('ballast').world_bounds(domain_x)
   ```

This gradual approach reduces coupling without full refactor.

---

## Conclusion

**The current absolute coordinate system is GOOD for this project because:**
1. Simplicity matches project maturity
2. Explicit bounds contracts provide safety
3. Physics operations (gravity) are natural
4. Multi-region extraction (strip packing) is straightforward
5. Easy to debug and validate

**The tight coupling is acceptable if:**
1. Layer definitions are stable (unlikely to change)
2. Workers respect input contracts (validate!)
3. Tests cover layer boundaries (unit + integration)
4. Documentation is clear (coordinate system guide exists now!)

**The risk was addressed by:**
1. Identifying the bounds contract violation
2. Fixing the code to respect bounds
3. Adding extensive documentation
4. Creating tests to catch mismatches

**Next risk to watch for:**
- Other packing strategies ignoring bounds
- New workers that don't respect coordinate system
- Hardcoded values that break when layer definitions change

Mitigation: Regular code reviews for coordinate handling + expand test coverage.

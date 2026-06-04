# Coupling in Action: Code Examples

## How Tight Coupling Shows Up in the Code

### Example 1: Hard-Coded Boundaries

```python
# workers.py - SubgradeWorker
class SubgradeWorker(Worker):
    def execute(self, scene, params, ...):
        # Hard-coded absolute y-value!
        subgrade_top = 0.2  # ← COUPLED to this value
        
        scene.add_geometry(BoxCommand(
            0, 0, 0.0,
            domain_x, subgrade_top, domain_z,
            MC.SUBGRADE
        ))

# workers.py - FormationWorker  
class FormationWorker(Worker):
    def execute(self, scene, params, ...):
        # Hard-coded absolute y-value!
        formation_bottom = 0.2  # ← MUST match SubgradeWorker!
        formation_top = 0.3     # ← COUPLED to this value
        
        scene.add_geometry(BoxCommand(
            0, formation_bottom, 0.0,
            domain_x, formation_top, domain_z,
            MC.FORMATION
        ))

# If you change SubgradeWorker from 0.2 to 0.4:
# ✗ FormationWorker will be broken (starts at 0.2, should start at 0.4)
# ✗ All downstream workers break
```

**Coupling: STRONG** - Change one worker, must change others

---

### Example 2: Bounds Contract Violation

```python
# granular_worker.py
class GranularMatrixWorker:
    def execute(self, scene, params, materials, tools):
        # Calculate ballast bounds
        start_y = scene.metadata.get('ballast_bottom_y', 0.3)
        thickness = scene.metadata.get('ballast_thickness', 0.25)
        top_y = start_y + thickness
        
        # Create bounds object with absolute coordinates
        bounds = PackingBounds(
            x_min=0.0,
            x_max=domain_x,
            y_min=start_y,      # 0.3
            y_max=top_y          # 0.55
        )
        
        # Call packing strategy with these bounds
        packer = tools.get_tool("rock_packer")
        all_circles = packer.generate_rocks(
            bounds=bounds,  # ← Pass contract: pack within these bounds!
            ...
        )
```

```python
# rock_packing.py - GOOD implementation
class HybridShangPacking:
    def generate_rocks(self, bounds: PackingBounds, ...):
        """Pack rocks within bounds.y_min to bounds.y_max"""
        # Respects contract
        rocks = self._pack_in_region(bounds.y_min, bounds.y_max)
        # Rocks are in [bounds.y_min, bounds.y_max] ✓
        return rocks

# rock_packing.py - BAD implementation (before fix)
class StripPackingStrategy:
    def generate_rocks(self, bounds: PackingBounds, ...):
        """Pack rocks within bounds.y_min to bounds.y_max"""
        # ✗ IGNORES CONTRACT!
        self._pack_strip(bounds, ...)  # Receives bounds
        
    def _pack_strip(self, bounds, ...):
        # Violates contract here
        strip_bounds = PackingBounds(
            y_min=0.0,              # ← Contract violation!
            y_max=self.strip_height  # ← Should be bounds.y_min/max
        )
        rocks = self.base_strategy.generate_rocks(strip_bounds, ...)
        # Rocks are in [0, 3.2] ✗ NOT in [0.3, 0.55]!
        return rocks
```

**Coupling: BROKEN** - When one worker doesn't follow contract

---

### Example 3: Downstream Dependency Chain

```python
# lab_worker.py
class LabWorker:
    def execute(self, scene, params, ...):
        # Read ballast bounds from scene metadata
        ballast_bottom = scene.metadata.get('ballast_bottom_y', 0.5)
        ballast_top = scene.metadata.get('ballast_top_y', 0.9)
        
        # Hardcoded defaults! COUPLED to these values
        ballast_bottom = scene.work_order.get('ballast_bottom_y', ballast_bottom)
        ballast_top = scene.work_order.get('ballast_top_y', ballast_top)
        
        # Sample from ballast layer
        for rock in scene.rock_positions:
            if ballast_bottom <= rock.y <= ballast_top:
                # Include in PVC calculation
                samples_in_ballast.append(rock)
        
        # If rocks are at y ∈ [0, 3.2] (from bad StripPacking)
        # and LabWorker samples [0.3, 0.55]
        # ✗ Mismatch! Only ~10 rocks found instead of all 279

# Dependency chain:
# BallastWorker sets ballast_bottom = 0.3
#     ↓
# GranularMatrixWorker expects bounds.y_min = 0.3
#     ↓
# StripPackingStrategy MUST use bounds.y_min = 0.3
#     ↓
# LabWorker searches y ∈ [0.3, 0.55]
#
# If ANY step breaks: ENTIRE CHAIN FAILS
```

**Coupling: TIGHT** - All steps must agree on coordinates

---

### Example 4: Refactoring Risk

```python
# Scenario: Change ballast thickness from 0.25m to 0.30m
# This means: ballast_top changes from 0.55m to 0.60m

# Changes needed:
# ✗ granular_worker.py - update expectation? No code change (reads from config)
# ✓ BallastWorker - change thickness parameter
# ✓ LabWorker - update sampling region? Actually reads from metadata
# ? HybridShang - no change needed (respects bounds)
# ? StripPacking - no change needed (respects bounds)
# ? All other workers - check if hardcoded values reference ballast_top

# With loose coupling, this would be ONE change
# With tight coupling, need to verify multiple files
```

**Coupling: RISKY** - Easy to miss a location that needs updating

---

### Example 5: How the Fix Maintains Tight Coupling

```python
# BEFORE (broken)
def _pack_strip(self, bounds: PackingBounds, ...):
    # Breaks contract - ignores bounds!
    strip_bounds = PackingBounds(
        y_min=0.0,              # ← Wrong coordinate system
        y_max=self.strip_height
    )
    rocks = self.base_strategy.generate_rocks(strip_bounds, ...)
    # Returns rocks at y ∈ [0, 3.2]
    # But LabWorker expects y ∈ [0.3, 0.55]
    # ✗ Contract violated

# AFTER (fixed)
def _pack_strip(self, bounds: PackingBounds, ...):
    # Respects contract - uses input bounds!
    strip_bounds = PackingBounds(
        y_min=bounds.y_min,      # ← Correct coordinate system!
        y_max=bounds.y_max
    )
    rocks = self.base_strategy.generate_rocks(strip_bounds, ...)
    # Returns rocks at y ∈ [0.3, 0.55]
    # LabWorker expects y ∈ [0.3, 0.55]
    # ✓ Contract maintained
```

**Coupling: MAINTAINED** - All workers still coupled, but properly aligned

---

## How Loose Coupling Would Work

### Refactored with Relative Coordinates

```python
# Define layers as encapsulated objects
class Layer:
    """Encapsulates a material layer with local coordinate system"""
    
    def __init__(self, height: float, world_y_bottom: float):
        self.height = height
        self.world_y_bottom = world_y_bottom
        self.world_y_top = world_y_bottom + height
    
    def local_bounds(self, domain_x: float) -> PackingBounds:
        """Get bounds in local coordinate system"""
        return PackingBounds(0, domain_x, 0, self.height)
    
    def world_bounds(self, domain_x: float) -> PackingBounds:
        """Get bounds in world coordinate system"""
        return PackingBounds(0, domain_x, self.world_y_bottom, self.world_y_top)
    
    def to_world_coords(self, rocks: List[Rock]) -> List[Rock]:
        """Convert rocks from local to world coordinates"""
        return [
            Rock(r.x, r.y + self.world_y_bottom, r.radius, ...)
            for r in rocks
        ]
    
    def to_local_coords(self, rocks: List[Rock]) -> List[Rock]:
        """Convert rocks from world to local coordinates"""
        return [
            Rock(r.x, r.y - self.world_y_bottom, r.radius, ...)
            for r in rocks
        ]


# Create layers with simple configuration
subgrade = Layer(height=0.2, world_y_bottom=0.0)
formation = Layer(height=0.1, world_y_bottom=0.2)
ballast = Layer(height=0.25, world_y_bottom=0.3)


# Workers use layer abstraction (DECOUPLED)
class GranularMatrixWorker:
    def execute(self, scene, ballast_layer: Layer, ...):
        # ✓ Don't need to know absolute coordinates!
        bounds = ballast_layer.local_bounds(domain_x)
        
        # Pack in local space [0, 0.25]
        rocks = packer.generate_rocks(bounds, ...)
        
        # Convert to world space for storage
        rocks_world = ballast_layer.to_world_coords(rocks)
        scene.add_rocks(rocks_world)


class LabWorker:
    def execute(self, scene, ballast_layer: Layer, ...):
        # ✓ Don't need to know absolute coordinates!
        world_bounds = ballast_layer.world_bounds(domain_x)
        
        # Sample rocks in ballast layer
        sampled = [
            r for r in scene.rock_positions
            if world_bounds.y_min <= r.y <= world_bounds.y_max
        ]
        # Calculate PVC...


# BENEFIT: Refactoring is now SAFE
# Change ballast from 0.3m to 0.4m:
ballast = Layer(height=0.25, world_y_bottom=0.4)  # ← ONLY change needed!
# No code changes required in GranularMatrixWorker or LabWorker!
# Loose coupling achieved! ✓
```

---

## Comparison: Coupling Strength

### Tight Coupling (Current)

```python
# Hard-coded absolute values everywhere
SUBGRADE_HEIGHT = 0.2          # File 1
FORMATION_BOTTOM = 0.2         # File 2
FORMATION_TOP = 0.3            # File 2
BALLAST_BOTTOM = 0.3           # File 3
BALLAST_TOP = 0.55             # File 3
BALLAST_SAMPLING_MIN = 0.3     # File 4
BALLAST_SAMPLING_MAX = 0.55    # File 4

# Change: 0.3 → 0.4 means updating:
# - SubgradeWorker
# - FormationWorker  
# - GranularMatrixWorker
# - LabWorker
# - Possibly test files
# - Documentation

# Risk: Miss one, entire system breaks
# Safety: Low
```

### Loose Coupling (Hypothetical)

```python
# Single configuration
LAYERS = {
    'subgrade': Layer(height=0.2, world_y=0.0),
    'formation': Layer(height=0.1, world_y=0.2),
    'ballast': Layer(height=0.25, world_y=0.3),  # ← One place!
}

# Change: 0.3 → 0.4 means:
ballast = Layer(height=0.25, world_y=0.4)  # ← ONLY change needed!

# All workers reference same layer object
# No code changes needed elsewhere
# Risk: Minimal
# Safety: High
```

---

## Summary: Coupling Trade-offs in This Codebase

| Aspect | Tight (Current) | Loose (Hypothetical) |
|--------|---|---|
| **Code Changes to Refactor** | 5+ files | 1 config |
| **Risk of Missing Something** | High | Low |
| **Performance Overhead** | None | Coordinate transforms |
| **Code Complexity** | Low | Medium |
| **Debugging Ease** | Easy | Hard |
| **When to Use** | Small, stable | Large, dynamic |

---

## Conclusion

The current **tight coupling is acceptable** because:
1. Layer definitions are stable (unlikely to change)
2. Performance is critical (no overhead)
3. Codebase is small (refactoring risk manageable)
4. Values are simple and explicit (easy to debug)

**If requirements change:**
- Multiple domain heights → Use loose coupling
- Nested extraction regions → Use loose coupling
- Dynamic layer reconfiguration → Use loose coupling
- Keep shipping with current approach → Maintain tight coupling + good testing

The fix (respecting bounds contract) keeps tight coupling working properly. To prevent future bugs:
- Validate contracts explicitly
- Test at layer boundaries
- Document coordinate system assumptions
- Consider loose coupling refactor if complexity grows

# Coordinate System Analysis: Your Code vs gprMax Specification

## Executive Summary

Your code implements a **Y-up Cartesian coordinate system** that is fundamentally correct for gprMax. However, there is a **critical inconsistency in the antenna height calculation** that could cause antenna placement errors.

---

## 1. gprMax Coordinate Convention

gprMax uses a **right-handed Cartesian coordinate system**:
- **X-axis**: Horizontal (left-right), range [0, domain_x]
- **Y-axis**: Vertical (bottom-to-top), range [0, domain_y]  
- **Z-axis**: Depth (into/out of page), range [0, domain_z]

### Domain Command Format
```
#domain: x_max y_max z_max
```
This defines the simulation extent as a rectangular box from (0,0,0) to (x_max, y_max, z_max).

### Geometry Command Format
```
#box: x1 y1 z1 x2 y2 z2 material
#cylinder: x1 y1 z1 x2 y2 z2 radius material
```
Constraints:
- `x1 ≤ x2`, `y1 ≤ y2`, `z1 ≤ z2`
- All coordinates must be within [0, domain_x] × [0, domain_y] × [0, domain_z]

---

## 2. Your Code's Coordinate System ✓ CORRECT

### Anchor System ([coordinates.py](src/domain/coordinates.py))
```python
BOTTOM = 0.0              # y = 0
SUBGRADE_TOP = varies     # y = subgrade_thickness
FORMATION_TOP = varies    # y = subgrade_thickness + formation_thickness
BALLAST_TOP = varies      # y = subgrade_thickness + formation_thickness + ballast_thickness
ANTENNA_LEVEL = varies    # y = ballast_top + antenna_clearance
DOMAIN_TOP = varies       # y = ballast_top + antenna_clearance + air_buffer
```

### Layer Stack Computation ([coordinates.py:99-124](src/domain/coordinates.py#L99-L124))
```python
current_y = 0.0
self._y_levels[Anchor.BOTTOM] = 0.0
current_y += subgrade_thickness         → SUBGRADE_TOP
current_y += formation_thickness        → FORMATION_TOP
current_y += ballast_thickness          → BALLAST_TOP
current_y += antenna_clearance          → ANTENNA_LEVEL
current_y += air_buffer                 → DOMAIN_TOP
```

**This is geometrically sound**: Layers stack bottom-up, matching gprMax's Y-up convention.

### Geometry Generation ([workers.py](src/workers.py))
**Air Layer** ([workers.py:34-38](src/workers.py#L34-L38)):
```python
BoxCommand(0, 0, 0, domain_x, domain_y, domain_z, "air")
```

**Subgrade** ([workers.py:72-76](src/workers.py#L72-L76)):
```python
BoxCommand(0, 0, 0, domain_x, subgrade_top, domain_z, "subgrade")
```

**Formation** ([workers.py:133-137](src/workers.py#L133-L137)):
```python
BoxCommand(0, start_y, 0, domain_x, top_y, domain_z, "formation")
```

**Rocks** ([workers.py:362-366](src/workers.py#L362-L366)):
```python
CylinderCommand(
    rock.x, rock.y, z_start,  # Bottom center
    rock.x, rock.y, z_end,    # Top center (vertical extrusion)
    rock.radius, material
)
```

**Antenna** ([workers.py:778, 800](src/workers.py#L778-L800)):
```python
HertzianDipoleCommand("z", tx_x, tx_rx_y, tx_rx_z, "ricker_src")
RxCommand(rx_x, rx_y, rx_z)
```

**All of these are correct Y-up placements.** ✓

---

## 3. CRITICAL ISSUE: Antenna Height Mismatch ⚠️

### The Discrepancy

There is a **conflict between two antenna height definitions**:

#### Definition 1: From Config (line 45)
```python
tx_rx_y: float = 1.4  # 65cm above ballast surface (y=0.75)
```
This hardcoded value assumes **ballast_top = 0.75 m**.

#### Definition 2: From CoordinateSystem  
Using default config values:
- `subgrade_thickness`: 0.20 m (line 173)
- `formation_thickness`: 0.10 m (line 172)  
- `max_ballast_thickness`: 0.55 m (line 167)
- `antenna_clearance_above_ballast`: 0.50 m (line 145)

Layer stack calculation:
```
ballast_top = 0.20 + 0.10 + 0.45 (typical) = 0.75 ✓
antenna_level = 0.75 + 0.50 = 1.25 m
```

But config specifies `tx_rx_y = 1.4 m`, which is **0.15 m higher** than the computed value.

### Where This Manifests

**In AntennaWorker** ([workers.py:731-741](src/workers.py#L731-L741)):
```python
if scene.coordinate_system:
    # Uses CoordinateSystem: antenna_level = ballast_top + antenna_clearance
    tx_rx_y = scene.coordinate_system.get_y(Anchor.ANTENNA_LEVEL)
else:
    # Fallback: uses hardcoded config.tx_rx_y
    tx_rx_y = scene.config.tx_rx_y
```

**Current behavior**: 
- If `coordinate_system` is provided → antenna at ~1.25 m
- If not → antenna at 1.4 m (hardcoded config)

### Impact

1. **Inconsistent antenna placement** between config-driven and coordinate-system-driven modes
2. **Antenna may be placed too low** relative to designer intent (config comment says 65cm above ballast)
3. **Variable coupling**: Changes to `antenna_clearance_above_ballast` won't affect `tx_rx_y` unless the coordinate system is used

---

## 4. Additional Configuration Ambiguities

### Issue: `subgrade_height` vs `subgrade_thickness`

**File**: [config.py](src/config.py)

```python
Line 165: subgrade_height: float = 0.3          # ← Unused?
Line 173: subgrade_thickness: float = 0.20      # ← Actually used in LayerStack
```

The `subgrade_height` is never referenced in the codebase:
```bash
$ grep -r "subgrade_height" src/
# Result: Only in config.py definition, never read
```

**Current behavior**: Code uses `subgrade_thickness` (0.20 m).

**Risk**: Confusion if someone updates `subgrade_height` thinking it controls the subgrade layer.

---

## 5. Validation Checklist

### ✓ Coordinate System Integrity
- [x] Y-up convention: Correct
- [x] Layer stacking order: Bottom-to-top (correct)
- [x] Box command format (x1,y1,z1,x2,y2,z2): Correct
- [x] Cylinder command (vertical extrusion): Correct
- [x] Domain bounds validation: Implemented

### ✓ Geometry Commands
- [x] All x1 ≤ x2: Yes
- [x] All y1 ≤ y2: Yes  
- [x] All z1 ≤ z2: Yes
- [x] All coordinates within domain: Yes (with domain validation in AntennaWorker)

### ⚠️ Antenna Placement
- [ ] Antenna height definition unified: **NO** (hardcoded vs computed)
- [ ] Config `tx_rx_y` synchronized with layer stack: **NO** (1.4 vs ~1.25)

---

## 6. Recommended Fixes

### Fix 1: Unify Antenna Height Definition

**Option A: Use CoordinateSystem Always** (Recommended)
```python
# In config.py: Remove hardcoded tx_rx_y
# Delete line 45: tx_rx_y: float = 1.4

# In AntennaWorker: Always compute from layers
if scene.coordinate_system:
    tx_rx_y = scene.coordinate_system.get_y(Anchor.ANTENNA_LEVEL)
else:
    raise RuntimeError("AntennaWorker requires CoordinateSystem")
```

**Rationale**: Single source of truth, consistent with LayerStack logic.

**Option B: Keep tx_rx_y, Validate Consistency** (If you need config flexibility)
```python
# In __post_init__:
def _validate_antenna_consistency(self):
    estimated_ballast_top = self.subgrade_thickness + self.formation_thickness + self.max_ballast_thickness
    estimated_antenna_y = estimated_ballast_top + self.antenna_clearance_above_ballast
    
    if abs(self.tx_rx_y - estimated_antenna_y) > 0.01:  # 1cm tolerance
        warnings.warn(
            f"tx_rx_y={self.tx_rx_y} inconsistent with layer stack "
            f"(expected ~{estimated_antenna_y:.2f}). "
            f"Consider using CoordinateSystem.get_y(Anchor.ANTENNA_LEVEL)."
        )
```

### Fix 2: Remove Unused `subgrade_height`

**In config.py**:
```python
# DELETE line 165:
# subgrade_height: float = 0.3  # Unused, redundant with subgrade_thickness

# UPDATE line 167 comment to reference the actual parameter:
max_ballast_thickness: float = 0.55  # Max: subgrade(0.2) + formation(0.1) + ballast(0.55) = 0.85m
```

### Fix 3: Document the Layer Heights

**Add to LayerStack docstring**:
```python
@dataclass(frozen=True)
class LayerStack:
    """
    Configuration for vertical layer thicknesses.
    
    Example (with defaults):
    - BOTTOM:          y = 0.00 m
    - SUBGRADE_TOP:    y = 0.20 m (thickness: 0.20)
    - FORMATION_TOP:   y = 0.30 m (thickness: 0.10)
    - BALLAST_TOP:     y = 0.75 m (thickness: 0.45)
    - ANTENNA_LEVEL:   y = 1.25 m (clearance: 0.50)
    - DOMAIN_TOP:      y = 1.35 m (buffer: 0.10)
    """
```

---

## 7. Coordinate System Correctness Summary

| Aspect | Status | Evidence |
|--------|--------|----------|
| **Y-up convention** | ✓ Correct | Layer computation (lines 99-124) |
| **Box command format** | ✓ Correct | All boxes use (x1,y1,z1,x2,y2,z2) |
| **Cylinder orientation** | ✓ Correct | Vertical cylinders with same (x,y) at both ends |
| **Domain bounds** | ✓ Correct | Validated in AntennaWorker, point validation in CoordinateSystem |
| **Layer stacking** | ✓ Correct | Bottom-to-top with no gaps or overlaps |
| **Antenna placement** | ⚠️ **Inconsistent** | Two definitions (config vs CoordinateSystem) |

---

## 8. Conclusion

**Your coordinate system implementation is fundamentally sound** for gprMax compatibility. The logic for layer generation, rock placement, and geometry commands all follow proper Cartesian conventions.

**However, the antenna height calculation has a critical ambiguity** that could lead to off-by-150mm placement errors depending on code path. This should be resolved before production use.

**Recommended action**: Adopt Fix 1 (Option A) to make CoordinateSystem the single source of truth for all layer heights, including antenna position.

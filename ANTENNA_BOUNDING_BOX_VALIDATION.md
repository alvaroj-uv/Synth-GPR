# Antenna Bounding Box Validation

## Overview

The antenna placement now includes **comprehensive validation** to ensure it never exceeds the simulation domain bounds (X, Y, Z).

## Validation Layers

### Layer 1: Pre-Flight Check (ProductionLine)
**Location**: [production_line.py:89-108](src/production_line.py#L89-L108)

Runs **before** any workers execute. Checks that `config.domain_y` is tall enough to accommodate the full layer stack:

```python
required_height = coords.get_y(Anchor.DOMAIN_TOP)
if self.config.domain_y < required_height:
    raise RuntimeError("Domain height insufficient...")
```

**What it checks:**
- ✓ Subgrade thickness
- ✓ Formation thickness  
- ✓ Ballast thickness
- ✓ Antenna clearance above ballast
- ✓ Air buffer above antenna

**Example output if domain is too small:**
```
Domain height insufficient for layer stack:
  Config domain_y: 1.20 m
  Required (computed): 1.35 m
  Deficit: 0.15 m
  Layer breakdown:
    - Subgrade: 0.20 m
    - Formation: 0.10 m
    - Ballast: 0.45 m
    - Antenna clearance: 0.50 m
    - Air buffer: 0.10 m
Fix: Increase config.domain_y to at least 1.35 m
```

### Layer 2: Antenna Y Validation (AntennaWorker)
**Location**: [workers.py:735-760](src/workers.py#L735-L760)

Explicit check that antenna Y coordinate doesn't exceed domain top:

```python
if tx_rx_y > domain_top:
    raise ValueError("Antenna Y exceeds domain...")
```

**What it checks:**
- ✓ Antenna Y ≤ domain_top
- ✓ Provides ballast height, antenna clearance, and deficit calculation
- ✓ Suggests specific fixes

### Layer 3: Full Position Validation (AntennaWorker)
**Location**: [workers.py:761-810](src/workers.py#L761-L810)

Uses `CoordinateSystem.validate_point()` to check TX and RX positions in all three dimensions:

```python
valid_tx = scene.coordinate_system.validate_point(tx_position)
valid_rx = scene.coordinate_system.validate_point(rx_position)
```

**What it validates:**
- ✓ TX X: `0 ≤ tx_x ≤ domain_x`
- ✓ TX Y: `0 ≤ tx_y ≤ domain_y` (computed from layers)
- ✓ TX Z: `0 ≤ tx_z ≤ domain_z`
- ✓ RX X: `0 ≤ rx_x ≤ domain_x`
- ✓ RX Y: `0 ≤ rx_y ≤ domain_y` (same as TX)
- ✓ RX Z: `0 ≤ rx_z ≤ domain_z`

**Example error output:**
```
AntennaWorker: RX Position invalid (outside domain bounds).
  RX position: (0.8500, 1.2500, 0.0050) m
  Domain bounds: [0, 0.6000] × [0, 1.3500] × [0, 0.0050] m
  Issue: X=0.8500 (valid: 0-0.6000)
```

### Layer 4: Multi-Receiver Array Validation
**Location**: [workers.py:769-783](src/workers.py#L769-L783)

For multi-receiver arrays (RX count > 1), validates each receiver:

```python
for i in range(num_rx):
    curr_rx_x = rx_x + (i * spacing)
    rx_pos = Point3D(curr_rx_x, tx_rx_y, tx_rx_z)
    
    if not scene.coordinate_system.validate_point(rx_pos):
        if i == 0:
            raise ValueError("Primary RX invalid")  # Fail on first RX
        else:
            print(f"Warning: RX_{i} outside domain. Skipping.")  # Skip later RXs
            continue
```

**Behavior:**
- **Primary RX (i=0)**: Fails if out of bounds (must have at least one receiver)
- **Additional RXs**: Skipped with warning if out of bounds (allows partial arrays)

---

## Validation Coordinate System

### Domain Bounds Definition

The domain is defined as a rectangular box:

```
[0, domain_x] × [0, domain_y] × [0, domain_z]
```

Where:
- `domain_x`: Horizontal extent (X-axis)
- `domain_y`: Vertical extent (Y-axis, computed from layer stack)
- `domain_z`: Depth extent (Z-axis)

### Layer Stack Y Coordinates

The antenna Y is computed as:

```
antenna_y = ballast_top + antenna_clearance
          = (subgrade_thickness + formation_thickness + ballast_thickness) + antenna_clearance
```

**Default example:**
```
antenna_y = (0.20 + 0.10 + 0.45) + 0.50 = 1.25 m
domain_y = antenna_y + air_buffer = 1.25 + 0.10 = 1.35 m
```

---

## Test Coverage

All validation paths tested:

### ✓ Test Results (see test_antenna_bounds.py)

| Test | Condition | Result |
|------|-----------|--------|
| Valid position | Antenna within domain | PASS |
| At domain edge | Antenna Y = domain_top | PASS |
| Exceeds Y | Antenna Y > domain_top | FAIL (as expected) |
| Exceeds X | Antenna X > domain_x | FAIL (as expected) |
| Exceeds Z | Antenna Z > domain_z | FAIL (as expected) |

---

## Error Handling

### Validation Failure → Immediate Halt

If any validation fails:

1. **Error raised immediately** (fail-fast)
2. **Diagnostic information provided:**
   - Actual position
   - Domain bounds
   - Which dimension(s) violated
   - How much the violation is (deficit)
3. **Specific remediation suggested**

### Example Fix Process

If antenna placement fails:

1. **Read error message:**
   ```
   Antenna Y (1.45) exceeds domain height (1.35)
   Deficit: 0.10 m
   ```

2. **Choose a fix:**
   - Decrease `antenna_clearance_above_ballast` by 0.10+ m, OR
   - Increase `domain_y` to 1.45+ m, OR
   - Reduce ballast thickness (indirectly reduces antenna height)

3. **Update config and retry**

---

## Configuration Parameters

Key parameters affecting antenna bounds:

| Parameter | Default | Notes |
|-----------|---------|-------|
| `domain_x` | 0.6 m | Horizontal extent - set for wavelength requirement |
| `domain_y` | 1.5 m | Vertical extent - **must accommodate full layer stack** |
| `domain_z` | 0.003 m | Depth extent - typically 1 cell for 2D simulations |
| `subgrade_thickness` | 0.20 m | Base soil layer |
| `formation_thickness` | 0.10 m | Transition layer |
| `max_ballast_thickness` | 0.55 m | Max ballast - antenna height depends on this |
| `antenna_clearance_above_ballast` | 0.50 m | **Antenna placement driver** |
| `air_buffer` | 0.10 m | Space above antenna to domain top |

### Quick Fix Reference

**"Antenna Y exceeds domain"** →
- Increase `domain_y`, or
- Decrease `antenna_clearance_above_ballast`, or
- Decrease `max_ballast_thickness`

**"Antenna X exceeds domain"** →
- Increase `domain_x`, or
- Move antenna closer to center (decrease `tx_x`, `rx_x`)

**"Antenna Z exceeds domain"** →
- Increase `domain_z` (usually only needed if not 2D simulation)

---

## Summary

✅ **Three-layer validation ensures antenna is always in bounds:**

1. **Pre-flight**: Domain tall enough? (ProductionLine)
2. **Antenna Y**: Computed height within domain? (AntennaWorker)
3. **Full position**: All X, Y, Z within bounds? (CoordinateSystem)

**Result**: No antenna placement errors, with clear diagnostics if configuration is invalid.

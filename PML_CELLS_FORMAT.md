# PML Cells Format - gprMax Specification

## Overview

Based on gprMax source code analysis (`input_cmds_singleuse.py`), the `#pml_cells` command format is strictly defined.

## Valid Formats

### Format 1: Single Parameter (Applies to All Sides)
```
#pml_cells: N
```

Applies **N cells** to all 6 boundaries:
- x0 (left), xmax (right)
- y0 (bottom), ymax (top)
- z0 (back), zmax (front)

**Example**:
```
#pml_cells: 10
```
→ All boundaries get 10 PML cells

### Format 2: Six Parameters (Individual Control)
```
#pml_cells: x0 y0 z0 xmax ymax zmax
```

Specifies PML thickness for each boundary individually:
- `x0`: Left boundary (x = 0)
- `xmax`: Right boundary (x = domain_x)
- `y0`: Bottom boundary (y = 0)
- `ymax`: Top boundary (y = domain_y)
- `z0`: Back boundary (z = 0)
- `zmax`: Front boundary (z = domain_z)

**Example** (2D TMz simulation):
```
#pml_cells: 10 10 0 10 10 0
```
→ 10 cells on X and Y boundaries, 0 cells on Z (for 2D)

## Invalid Formats

❌ **3 parameters** (what I had originally):
```
#pml_cells: 10 10 0    # ERROR: Requires either 1 or 6 parameters!
```

❌ **2 parameters**:
```
#pml_cells: 10 10      # ERROR!
```

❌ **4-5 parameters**:
```
#pml_cells: 10 10 10 10    # ERROR!
```

## gprMax Code Reference

From `input_cmds_singleuse.py` lines 234-247:

```python
# PML cells
cmd = '#pml_cells'
if singlecmds[cmd] is not None:
    tmp = singlecmds[cmd].split()
    if len(tmp) != 1 and len(tmp) != 6:
        raise CmdInputError(cmd + ' requires either one or six parameter(s)')
    if len(tmp) == 1:
        for key in G.pmlthickness.keys():
            G.pmlthickness[key] = int(tmp[0])
    else:
        G.pmlthickness['x0'] = int(tmp[0])
        G.pmlthickness['y0'] = int(tmp[1])
        G.pmlthickness['z0'] = int(tmp[2])
        G.pmlthickness['xmax'] = int(tmp[3])
        G.pmlthickness['ymax'] = int(tmp[4])
        G.pmlthickness['zmax'] = int(tmp[5])
```

The code explicitly checks: `if len(tmp) != 1 and len(tmp) != 6:`

## Domain Constraint

From lines 254-256:
```python
if 2 * G.pmlthickness['x0'] >= G.nx or 2 * G.pmlthickness['y0'] >= G.ny or \
   2 * G.pmlthickness['z0'] >= G.nz or 2 * G.pmlthickness['xmax'] >= G.nx or \
   2 * G.pmlthickness['ymax'] >= G.ny or 2 * G.pmlthickness['zmax'] >= G.nz:
    raise CmdInputError(cmd + ' has too many cells for the domain size')
```

**Constraint**: The total PML thickness on opposite sides cannot exceed the domain size:
- `2 × PML_x ≤ domain_cells_x`
- `2 × PML_y ≤ domain_cells_y`
- `2 × PML_z ≤ domain_cells_z`

## Examples

### 2D TMz Simulation (Z = 1 cell)
```
#domain: 2.248 2.0 0.0132
#dx_dy_dz: 0.0132 0.0132 0.0132
#pml_cells: 10 10 0 10 10 0
```

**Calculation**:
- Domain cells: (170 × 152 × 1)
- PML: x=(10,10), y=(10,10), z=(0,0)
- Constraint check: 2×10=20 < 170 ✓, 2×10=20 < 152 ✓, 2×0=0 < 1 ✓

### 3D Simulation (all dimensions)
```
#domain: 1.0 1.0 1.0
#dx_dy_dz: 0.01 0.01 0.01
#pml_cells: 10 10 10 10 10 10
```

**Calculation**:
- Domain cells: (100 × 100 × 100)
- PML: x=(10,10), y=(10,10), z=(10,10)
- Constraint check: 2×10=20 < 100 ✓ (all axes)

## Test File (Corrected)

My `test_400mhz.in` now correctly uses:
```
#pml_cells: 10 10 0 10 10 0
```

This specifies:
- **Left/Right boundaries**: 10 cells each (20 total)
- **Bottom/Top boundaries**: 10 cells each (20 total)
- **Front/Back boundaries**: 0 cells each (2D simulation)

## Validation

✅ **Correct format**: 6 parameters (or 1 for all sides)  
✅ **Domain constraint**: 2×10=20 < 170 (X), 2×10=20 < 152 (Y), 2×0=0 < 1 (Z)  
✅ **2D mode compatibility**: Z=0 is valid for 2D TMz simulations

## Summary

| Aspect | Status |
|--------|--------|
| Format | ✅ 6 parameters: x0, y0, z0, xmax, ymax, zmax |
| Domain constraint | ✅ Passes (20 < 170 and 20 < 152) |
| 2D compatibility | ✅ Z=0 valid for 2D |
| gprMax compliance | ✅ Matches exact source code |

**File corrected and ready for gprMax!**

# gprMax Validation Analysis & Recommendations

## Key Findings from gprMax

### 1. **gprMax Validation Philosophy**
gprMax validation is **split into two levels**:

- **Structural validation**: Command syntax, essential commands present (#domain, #dx_dy_dz, #time_window)
- **Semantic validation**: Parameter constraints (CFL condition, material poles > time step)
- **Missing**: Explicit spatial bounds checking for antennas/receivers

### 2. **gprMax Domain Bounds Rules**
From [gprMax Documentation](https://docs.gprmax.com/en/latest/gprmodelling.html):

**Critical Placement Rules:**
- **Sources & targets**: Keep at least **15 cells away** from PML boundaries
- **Free space above source**: Maintain **15-20 cells** of air above antenna
- **Never place antennas in PML cells**: "it is wrong to do so"
- **General rule**: More distance from boundaries = better results

**Coordinate System:**
- Origin **(0,0) fixed at lower left corner**
- All coordinates are absolute references

### 3. **What gprMax Does NOT Validate**
From examining [input_cmds_file.py](https://github.com/gprMax/gprMax/blob/master/gprMax/input_cmds_file.py):

- ✗ Domain bounds checking for antennas
- ✗ Coordinate range validation
- ✗ Antenna position vs. domain verification
- ✗ PML clearance validation

gprMax assumes **user responsibility** for spatial correctness.

### 4. **Interesting gprMax Design Choice**
From [input.rst](https://raw.githubusercontent.com/gprMax/gprMax/master/docs/source/input.rst):

> "Geometric objects are *permitted to extend outwith the model domain* if desired, however, only parts of object inside the domain will be created."

**Interpretation**: gprMax is permissive - it silently clips objects that exceed bounds rather than failing.

---

## Your Code vs. gprMax Best Practices

### Comparison Table

| Aspect | gprMax | Your Code |
|--------|--------|-----------|
| **Structural validation** | ✓ Present | ✓ Present |
| **Essential commands** | ✓ Checks | ✓ Domain settings enforced |
| **Antenna bounds checking** | ✗ None | ✓ **Three-layer validation** |
| **PML clearance** | Documented, not enforced | Not yet implemented |
| **Error messages** | Generic | ✓ Detailed diagnostics |
| **Fail strategy** | Silent clipping | ✓ Fail-fast with suggestions |

### Your Advantages

1. **Explicit validation** (vs. silent clipping)
2. **Diagnostic messages** with specific deficits
3. **PML-aware design** (planned: next enhancement)
4. **Fail-fast** prevents invalid simulations

---

## Recommended Enhancements Based on gprMax

### Enhancement 1: PML Clearance Validation ⭐ HIGH PRIORITY

gprMax requires antennas to be **15+ cells away from PML boundaries**.

**Implementation:**

```python
def validate_pml_clearance(self, antenna_pos: Point3D) -> bool:
    """
    Validate that antenna is outside PML boundary layer.
    gprMax rule: sources must be >= 15 cells from PML.
    
    PML is applied to domain edges (typically 10 cells thick).
    So sources should be at:
    - X: >= pml_cells * dx to < (domain_x - pml_cells * dx)
    - Y: >= pml_cells * dy to < (domain_y - pml_cells * dy)  
    - Z: >= pml_cells * dz to < (domain_z - pml_cells * dz)
    """
    pml_thickness_m = self.config.pml_layers * self.config.dx
    
    x_min = pml_thickness_m
    x_max = self.config.domain_x - pml_thickness_m
    y_min = pml_thickness_m  
    y_max = self.config.domain_y - pml_thickness_m
    z_min = pml_thickness_m
    z_max = self.config.domain_z - pml_thickness_m
    
    return (x_min <= antenna_pos.x <= x_max and
            y_min <= antenna_pos.y <= y_max and
            z_min <= antenna_pos.z <= z_max)
```

**Add to AntennaWorker validation** (after coordinate bounds check):

```python
# Check PML clearance (gprMax best practice)
pml_thickness = scene.config.pml_layers * scene.config.dx
pml_x_min = pml_thickness
pml_x_max = scene.config.domain_x - pml_thickness
pml_y_min = pml_thickness
pml_y_max = scene.config.domain_y - pml_thickness

for pos, name in [(tx_position, "TX"), (rx_position, "RX")]:
    if not (pml_x_min <= pos.x <= pml_x_max and
            pml_y_min <= pos.y <= pml_y_max):
        raise ValueError(
            f"{self.name}: {name} too close to PML boundary.\n"
            f"  Position: {pos}\n"
            f"  Safe region: [{pml_x_min:.4f}, {pml_x_max:.4f}] × "
            f"[{pml_y_min:.4f}, {pml_y_max:.4f}]\n"
            f"  PML thickness: {pml_thickness:.4f} m ({scene.config.pml_layers} cells)\n"
            f"Fix: Move antenna away from boundaries"
        )
```

### Enhancement 2: Free Space Above Antenna ⭐ MEDIUM PRIORITY

gprMax recommends **15-20 cells of free space above antenna**.

**Implementation:**

```python
def validate_free_space_above_antenna(antenna_y: float) -> bool:
    """Ensure sufficient free space above antenna (gprMax: 15-20 cells)."""
    min_cells_above = 15  # Conservative: 15 cells minimum
    free_space_required = min_cells_above * self.config.dy
    space_available = self.config.domain_y - antenna_y
    
    return space_available >= free_space_required
```

**Add to AntennaWorker** (diagnostic level):

```python
# Warn if insufficient free space above antenna (gprMax guideline)
min_free_space = 15 * scene.config.dy  # 15 cells recommended
actual_free_space = domain_top - tx_rx_y
if actual_free_space < min_free_space:
    import warnings
    warnings.warn(
        f"Insufficient free space above antenna (gprMax recommends 15-20 cells).\n"
        f"  Antenna Y: {tx_rx_y:.4f} m\n"
        f"  Domain top: {domain_top:.4f} m\n"
        f"  Available: {actual_free_space:.4f} m ({actual_free_space / scene.config.dy:.1f} cells)\n"
        f"  Recommended: {min_free_space:.4f} m (15 cells)\n"
        f"Consider increasing domain_y or reducing antenna_clearance_above_ballast.",
        category=UserWarning
    )
```

### Enhancement 3: Cell-Based Coordinate Reporting

gprMax internally converts to integer cell coordinates. Your code could report this:

```python
def get_antenna_cells(self, antenna_y: float) -> tuple:
    """Convert antenna position to FDTD cell coordinates."""
    tx_cell = int(antenna_y / self.config.dy + 0.5)  # Round to nearest
    return tx_cell

# In error messages:
tx_cell = int(tx_position.y / scene.config.dy + 0.5)
antenna_msg += f"\nCell coordinates: Y cell = {tx_cell}"
```

### Enhancement 4: Silent Clipping Option (Optional)

If you want gprMax-like permissive behavior, add a fallback mode:

```python
# In config.py
antenna_bounds_mode: str = "strict"  # "strict" or "clamp"

# In AntennaWorker
if scene.config.antenna_bounds_mode == "clamp":
    # Silently clip antenna to domain bounds (like gprMax)
    tx_position = Point3D(
        min(max(tx_x, 0), scene.config.domain_x),
        min(max(tx_rx_y, 0), domain_top),
        min(max(tx_rx_z, 0), scene.config.domain_z)
    )
    print(f"Warning: Antenna clamped to domain bounds")
elif scene.config.antenna_bounds_mode == "strict":
    # Fail on out-of-bounds (current behavior)
    ...
```

---

## Implementation Roadmap

### Priority 1 (Critical - Implement Now)
- [x] Domain bounds validation (already done)
- [ ] **PML clearance validation** (add Enhancement 1)
- [ ] Test PML validation

### Priority 2 (Important)
- [ ] **Free space warning** (add Enhancement 2 as warning, not error)
- [ ] Cell-based coordinate reporting (Enhancement 3)
- [ ] Documentation update

### Priority 3 (Nice-to-Have)
- [ ] Silent clipping mode (Enhancement 4, if use case needed)
- [ ] Integration tests with various domain configurations

---

## Key Takeaway

**gprMax is permissive** (silent clipping), **your code is strict** (fail-fast).

**Your approach is better for production** because:
1. Catches configuration errors early
2. Provides diagnostic information
3. Prevents invalid simulations from running

**Add PML validation** to align with gprMax best practices and ensure realistic simulations.

---

## References

- [gprMax Modeling Guidance](https://docs.gprmax.com/en/latest/gprmodelling.html)
- [gprMax Input Documentation](https://raw.githubusercontent.com/gprMax/gprMax/master/docs/source/input.rst)
- [gprMax Input Commands File](https://github.com/gprMax/gprMax/blob/master/gprMax/input_cmds_file.py)
- [gprMax Antenna Examples](https://github.com/gprMax/gprMax/blob/master/docs/source/examples_antennas.rst)

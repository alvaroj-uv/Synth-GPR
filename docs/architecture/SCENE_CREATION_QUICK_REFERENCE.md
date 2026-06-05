# Scene Creation Architecture — Quick Reference

## 30-Second Overview

```
GeneratorConfig
    ↓
LayerStack + CoordinateSystem (defines vertical geometry)
    ↓
SceneCheckpoint (mutable container with 4 composed components)
    ↓
Worker Pipeline (5 + 3 workers in sequence)
    ↓
Final SceneCheckpoint → Written as .in file
```

---

## Component Hierarchy

```
SceneCheckpoint
├── config: GeneratorConfig
├── coordinate_system: CoordinateSystem
│   └── layer_stack: LayerStack (Immutable!)
├── _geometry_collection: GeometryCollection
│   ├── materials: List[MaterialCommand]
│   └── geometry: List[GeometryCommand]
├── _antenna_config: AntennaConfiguration
│   ├── sources: List[SourceCommand]
│   └── receivers: List[ReceiverCommand]
├── _rock_collection: RockCollection
│   └── positions: List[Rock]
├── domain_settings: DomainSettings (Immutable!)
│   ├── domain_cmd
│   ├── dx_dy_dz_cmd
│   ├── time_window_cmd
│   └── absorbing_bc_cmd
└── metadata: Dict[str, Any]
    ├── pvc: float
    ├── achieved_density: float
    ├── FI_class: str
    ├── fouling_height: float
    └── ... 20+ more fields
```

---

## Worker Execution Order

```
┌─────────────────────────────────────────────────────────────┐
│                    PHASE 1: BASE CONSTRUCTION                │
├─────────────────────────────────────────────────────────────┤
│ 1. AirWorker              → Paints entire domain with air    │
│ 2. SubgradeWorker         → Adds base soil layer             │
│ 3. FormationWorker        → Adds subballast transition       │
│ 4. BallastWorker          → Sets ballast bounds              │
│ 5. GranularMatrixWorker   → Packs rocks + adds fouling       │
├─────────────────────────────────────────────────────────────┤
│              Result: Geometry + metadata complete             │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    PHASE 2: CHECKPOINT                        │
├─────────────────────────────────────────────────────────────┤
│ scene.clone() → Deep copy for variant antenna support        │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                  PHASE 3: FINALIZATION                        │
├─────────────────────────────────────────────────────────────┤
│ 6. AntennaWorker          → Adds TX waveform + RX            │
│ 7. AssemblerWorker        → Validates all components         │
│ 8. LabWorker              → Calculates advanced metadata      │
├─────────────────────────────────────────────────────────────┤
│           Result: Complete, validated scene ready             │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                PHASE 4: VALIDATION & LOGGING                  │
├─────────────────────────────────────────────────────────────┤
│ - Run comprehensive validation (domains, materials, etc.)    │
│ - Log statistics (rock count, domain size, etc.)             │
│ - Check for critical errors                                  │
├─────────────────────────────────────────────────────────────┤
│                 Result: Return SceneCheckpoint                │
└─────────────────────────────────────────────────────────────┘
```

---

## Coordinate System Anchor Map

```
                        DOMAIN_TOP
                            ↑ (y)
                    ┌───────────────────┐
                    │   Free Space      │  ← Air buffer
                    │   (antenna zone)  │
                    └───────────────────┘
                        ANTENNA_LEVEL ← Where antenna measures
                            ↑
                    ┌───────────────────┐
                    │   Free Space      │  ← Antenna clearance
                    │   (air above)     │
                    └───────────────────┘
                        BALLAST_TOP ↑
                    ┌───────────────────┐
                    │  Rocks + Fouling  │  ← Ballast thickness
                    │  (GranularMatrix) │
                    └───────────────────┘
                    FORMATION_TOP = BALLAST_BOTTOM
                    ┌───────────────────┐
                    │  Formation Layer  │  ← Formation thickness
                    │  (subballast)     │
                    └───────────────────┘
                    SUBGRADE_TOP
                    ┌───────────────────┐
                    │  Subgrade Layer   │  ← Subgrade thickness
                    │  (base soil)      │
                    └───────────────────┘
                        BOTTOM (y=0.0)
```

---

## LayerStack Values (Default)

| Layer | Default Thickness | Total Height |
|-------|-------------------|--------------|
| Subgrade | 0.20 m | 0.20 m |
| Formation | 0.10 m | 0.30 m |
| Ballast | 0.25 m | 0.55 m |
| Antenna Clearance | 0.50 m | 1.05 m |
| Air Buffer | 0.10 m | 1.15 m (DOMAIN_TOP) |

**Total domain_y must be ≥ 1.15 m**

---

## Worker Implementation Template

```python
class ExampleWorker(Worker):
    name = "ExampleWorker"
    
    def execute(self, scene: SceneCheckpoint, params: Dict, 
                materials: WarehouseKeeper, tools: WarehouseKeeper) -> None:
        """Modify scene state"""
        
        # 1. Get geometry bounds
        if scene.coordinate_system:
            bounds = scene.coordinate_system.bounds(Layer.BALLAST)
            y_bottom, y_top = bounds.bottom, bounds.top
        
        # 2. Add material
        mat = materials.get_material("my_material")
        scene.add_material(mat)
        
        # 3. Add geometry
        cmd = BoxCommand(0, y_bottom, 0, 
                        scene.config.domain_x, y_top,
                        scene.config.domain_z, "my_material")
        scene.add_geometry(cmd)
        
        # 4. Update metadata (if needed)
        scene.metadata['my_value'] = 42
    
    def quality_check(self, scene: SceneCheckpoint) -> List[str]:
        """Return validation errors"""
        errors = []
        
        # Check expected geometry exists
        if not any(cmd.material == "my_material" for cmd in scene.geometry):
            errors.append(f"{self.name}: Material 'my_material' not found")
        
        return errors
```

---

## GranularMatrixWorker Steps

```python
execute() {
    Step 1: Get ballast bounds
        ballast_bottom = coords.get_y(Anchor.FORMATION_TOP)
        ballast_top = coords.get_y(Anchor.BALLAST_TOP)
    
    Step 2: Run packing algorithm
        packer = tools.get_packing_algorithm(config.rock_packing_algorithm)
        circles = packer.pack(domain_x, ballast_height, max_radius)
    
    Step 3: Classify circles
        rocks = [c for c in circles if c.radius >= min_rock_size]
    
    Step 4: Gravity settle
        for rock in rocks:
            rock.y = max(rock.y - rock.radius, ballast_bottom + rock.radius)
    
    Step 5: Add rock geometry
        for rock in rocks:
            triangles = _triangulate_rock(rock)
            scene.add_geometry(triangles)
        scene.add_rock(rock)  # Track position
    
    Step 6: Add fouling box
        fouling_height = _calculate_fouling_height(rocks, pvc_target)
        fouling_box = BoxCommand(..., fouling_height, ...)
        scene.add_geometry(fouling_box)
    
    Step 7: Calculate metadata
        scene.metadata['achieved_pvc'] = _measure_pvc(rocks, fouling_box)
        scene.metadata['achieved_density'] = _measure_density(rocks)
        scene.metadata['FI_class'] = _classify_fouling(pvc)
}

quality_check() {
    - Verify rock count in [10, 10000]
    - Verify packing density in reasonable range
    - Verify all rocks within ballast bounds
}
```

---

## Packing Algorithm Quick Selection

```
Need it NOW?  (< 1 second)
└─→ Use: Grid, Random, RSA
    Quality: Low (regular / random placement)

Need it SOON? (1–10 seconds)
└─→ Use: PoissonDisk, Circlify, SimulatedAnnealing
    Quality: Medium (balanced spatial distribution)

Need it RIGHT? (15–20 seconds)
└─→ Use: ShangChu (default)
    Quality: High (angular, realistic aggregate)

Need EVEN BETTER? (20 seconds, slight overhead)
└─→ Use: HybridShang
    Quality: High+ (ShangChu + refinement)
```

---

## Validation Checklist

```
After PHASE 1 (Base Construction):
  ✓ Geometry collection non-empty
  ✓ Materials defined (subgrade, formation, ballast, rock, fouling)
  ✓ Rocks in [10, 10000]
  ✓ Rock positions within ballast bounds
  ✓ Metadata: pvc, achieved_density, FI_class populated

After PHASE 3 (Finalization):
  ✓ Antennas configured (sources + receivers)
  ✓ Domain settings valid
  ✓ Assembly succeeded (assembled != None)
  ✓ All components pass validation
  ✓ No critical errors in issue log

Before writing .in file:
  ✓ Total commands > 5
  ✓ No duplicate material names
  ✓ All geometry materials referenced
  ✓ Domain fits computed height
  ✓ Cell size ≤ domain size
```

---

## SceneCheckpoint Delegation Methods

```python
# Geometry access
scene.add_material(cmd)
scene.add_geometry(cmd)
scene.materials        # → List[MaterialCommand]
scene.geometry         # → List[GeometryCommand]

# Antenna access
scene.add_source(cmd)
scene.add_receiver(cmd)
scene.sources          # → List[SourceCommand]
scene.receivers        # → List[ReceiverCommand]

# Rock access
scene.add_rock(rock)
scene.rocks            # → List[Rock]
scene.rock_count       # → int

# Domain access
scene.get_domain_params()  # → (domain_x, domain_y, domain_z)
scene.domain_settings      # → DomainSettings

# Validation
scene.validate_all()   # → List[str] (errors)
```

---

## Common Errors & Fixes

| Error | Cause | Fix |
|-------|-------|-----|
| `Domain height insufficient` | domain_y < required height | Increase domain_y in config |
| `No materials defined` | Workers didn't add materials | Verify MaterialWarehouse |
| `Mismatch: N sources but M receivers` | TX/RX count mismatch | AntennaWorker should match |
| `Excessive rocks (>10k)` | Packing algorithm too aggressive | Reduce packing density or domain size |
| `Too few rocks (<10)` | Insufficient packing | Use higher-quality algorithm |
| `Scene failed assembly` | Missing critical components | Check worker quality_check() logs |

---

## Extending the Architecture

### Add a Custom Material Layer

```python
class MyLayerWorker(Worker):
    name = "MyLayerWorker"
    
    def execute(self, scene, params, materials, tools):
        my_mat = materials.get_material("my_custom")
        scene.add_material(my_mat)
        
        bounds = scene.coordinate_system.bounds(Layer.BALLAST)
        y = bounds.top + 0.05  # 5cm above ballast
        cmd = BoxCommand(0, y, 0, scene.config.domain_x, y + 0.10,
                        scene.config.domain_z, "my_custom")
        scene.add_geometry(cmd)
    
    def quality_check(self, scene) -> List[str]:
        return [] if scene.geometry else ["No geometry"]

# Insert into recipe
base_recipe = [..., GranularMatrixWorker, MyLayerWorker, ...]
```

### Switch Packing Algorithm at Runtime

```python
config = GeneratorConfig(rock_packing_algorithm="circlify")
# or
work_order.set('rock_packing_algorithm', 'grid')

# ProductionLine automatically picks correct packer via ToolWarehouse
```

### Add Custom Metadata Calculation

```python
class CustomLabWorker(Worker):
    name = "CustomLabWorker"
    
    def execute(self, scene, params, materials, tools):
        # Calculate custom property
        my_value = self._compute_something(scene.rocks)
        scene.metadata['custom_property'] = my_value
    
    def quality_check(self, scene) -> List[str]:
        if 'custom_property' not in scene.metadata:
            return ["Custom property not calculated"]
        return []
```

---

## Key Invariants to Maintain

1. **Workers execute in order** — Dependencies exist between them
2. **Geometry is painter's algorithm** — Later commands override earlier
3. **LayerStack is frozen** — Can't change after CoordinateSystem created
4. **Metadata is optional but recommended** — Used for analysis, not simulation
5. **Rocks must be classed** — Distinguish large rocks from fines
6. **Antenna clearance required** — Must be above ballast (no overlap)
7. **Material names unique** — gprMax command expects no duplicates

---

## Testing a Custom Worker

```python
def test_my_worker():
    config = GeneratorConfig()
    scene = SceneCheckpoint(config=config)
    from src.domain import CoordinateSystem, LayerStack
    scene.coordinate_system = CoordinateSystem(LayerStack())
    scene.domain_settings = DomainSettings.from_config(config)
    
    from src.warehouses import MaterialWarehouse, ToolWarehouse
    materials = MaterialWarehouse(config)
    tools = ToolWarehouse(config)
    
    worker = MyLayerWorker()
    worker.execute(scene, {}, materials, tools)
    
    errors = worker.quality_check(scene)
    assert len(errors) == 0, f"Quality check failed: {errors}"
    assert len(scene.geometry) > 0
```

---

## File I/O Flow

```
SceneCheckpoint (in-memory)
    ↓
AssemblerWorker: validate + create SceneDefinition
    ↓
SceneDefinition (validated, immutable)
    ↓
InFileWriter.write_in_file(scene_def, "output.in")
    ├─ Write header (## comments with metadata)
    ├─ Write domain commands (#domain, #dx_dy_dz, #time_window)
    ├─ Write materials (#material)
    ├─ Write geometry (#box, #triangle, etc.)
    └─ Write antennas (#waveform, #hertzian_dipole, #rx)
    ↓
.in file (text format, ~50–200 KB)
    ↓
gprMax simulation (runs on GPU)
    ↓
.out file (HDF5 binary, Ez waveform)
```

---

## Performance Notes

| Operation | Time | Bottleneck |
|-----------|------|-----------|
| LayerStack creation | <1 ms | Negligible |
| CoordinateSystem init | <1 ms | Negligible |
| Worker execution (except GranularMatrixWorker) | <100 ms | Fast |
| GranularMatrixWorker | 1–20 s | Packing algorithm |
| Scene validation | 10–50 ms | Geometry traversal |
| .in file write | 50–200 ms | File I/O |
| **Total (single file)** | **20–40 s** | **Packing algorithm** |

**To speed up:**
- Use Grid/Random/RSA packing (< 1s)
- Reduce domain size
- Reduce max_rock_radius
- Disable heterogeneous sublayers

---

## Further Reading

- **[Full Architecture](SCENE_CREATION_ARCHITECTURE.md)** — 11 detailed sections
- **[Domain Models](../coordinate-systems/)** — Layer, Anchor, Point3D definitions
- **[Worker Implementation](../../src/workers.py)** — Source code
- **[Configuration Reference](../../src/config.py)** — All tunable parameters


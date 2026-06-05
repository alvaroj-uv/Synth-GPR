# Scene Creation Architecture

## Overview

The scene creation system in Synth-GPR follows a **Factory Pattern** with a **Worker-based choreography** model. It transforms high-level configuration parameters into complete gprMax simulation geometry (`.in` files) through a series of specialized workers that build the scene incrementally.

### Key Design Principles

1. **Separation of Concerns** — Each worker handles one responsibility
2. **Composition over Inheritance** — Scene state uses composed components
3. **Single Source of Truth** — LayerStack defines all vertical geometry
4. **Type-Safe Coordinates** — Anchor enums replace magic numbers
5. **Immutable Configuration** — Config and domain settings frozen after initialization

---

## Architecture Layers

```
┌─────────────────────────────────────────────────────────────────┐
│                    USER INPUT                                   │
│         (GeneratorConfig, command-line args, WorkOrder)         │
└────────────────────────────┬────────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────────┐
│                  PRODUCTION LINE                                 │
│         (Orchestrator: manages execution phases)                │
└────────────────────────────┬────────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────────┐
│              COORDINATE SYSTEM                                   │
│  LayerStack → CoordinateSystem → Anchor-based geometry          │
└────────────────────────────┬────────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────────┐
│           SCENE CHECKPOINT (Mutable State)                       │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  _geometry_collection   (Materials + Geometry Commands) │   │
│  │  _antenna_config        (Sources + Receivers)           │   │
│  │  _rock_collection       (Rock positions)                │   │
│  │  domain_settings        (Domain parameters)             │   │
│  │  metadata               (PVC, FI, density, etc.)        │   │
│  └─────────────────────────────────────────────────────────┘   │
└────────────────────────────┬────────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────────┐
│            WORKER PIPELINE                                       │
│   Phase 1: Base Construction (5-8 workers)                      │
│   Phase 2: Checkpoint (clone for variants)                      │
│   Phase 3: Finalization (3-4 workers)                           │
└────────────────────────────┬────────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────────┐
│           SCENE DEFINITION                                       │
│   (Validated, immutable, ready for file writing)                │
└────────────────────────────┬────────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────────┐
│              OUTPUT                                              │
│  .in file (gprMax text format) + metadata JSON                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 1. Coordinate System Foundation

### LayerStack (Single Source of Truth for Geometry)

The **LayerStack** dataclass defines the **vertical layer thicknesses** that determine all Y-coordinates in the simulation:

```python
@dataclass(frozen=True)
class LayerStack:
    subgrade_thickness: float = 0.20       # Base soil layer (m)
    formation_thickness: float = 0.10      # Subballast/transition (m)
    ballast_thickness: float = 0.25        # Clean rock layer (m)
    antenna_clearance: float = 0.5         # Space above ballast (m)
    air_buffer: float = 0.1                # Extra air above domain (m)
    
    @property
    def total_height(self) -> float:
        """Total required domain height"""
        return sum of all thicknesses
```

**Why immutable (frozen=True)?** Once the layering strategy is defined, all workers depend on it. Immutability prevents accidental drift.

### Anchor Enum (Named Coordinate Levels)

Instead of magic numbers like `y = 0.5` or `y = 0.75`, the system uses semantic anchors:

```python
class Anchor(Enum):
    BOTTOM = "bottom"                # y = 0.0
    SUBGRADE_TOP = "subgrade_top"    # y = sum(subgrade)
    FORMATION_TOP = "formation_top"  # y = subgrade + formation
    BALLAST_BOTTOM = "ballast_bottom" # same as FORMATION_TOP
    BALLAST_TOP = "ballast_top"      # y = subgrade + formation + ballast
    ANTENNA_LEVEL = "antenna_level"  # y = ballast_top + antenna_clearance
    DOMAIN_TOP = "domain_top"        # y = total_height
```

### CoordinateSystem (Resolver)

The **CoordinateSystem** service translates semantic requests into absolute coordinates:

```python
class CoordinateSystem:
    def __init__(self, layer_stack: LayerStack, domain_x: float, domain_z: float):
        self.stack = layer_stack
        self._y_levels = {}  # Precomputed Anchor → float
        self._compute_levels()  # Populate from LayerStack
    
    def get_y(self, anchor: Anchor, offset: float = 0.0) -> float:
        """Get absolute Y for an anchor (e.g., BALLAST_TOP) + optional offset"""
        return self._y_levels[anchor] + offset
    
    def bounds(self, layer: Layer) -> LayerBounds:
        """Type-safe layer bounds lookup"""
        # Returns LayerBounds(bottom_y, top_y) for SUBGRADE, FORMATION, BALLAST, AIR
```

**Example Usage in Workers:**
```python
if scene.coordinate_system:
    bounds = scene.coordinate_system.bounds(Layer.BALLAST)
    ballast_bottom_y = bounds.bottom
    ballast_top_y = bounds.top
```

---

## 2. Scene State: SceneCheckpoint

The **SceneCheckpoint** is a mutable holder for scene geometry state. It uses **composition** instead of a God Object pattern:

```python
@dataclass
class SceneCheckpoint:
    config: GeneratorConfig
    work_order: Optional[WorkOrderSystem] = None
    coordinate_system: Optional[CoordinateSystem] = None
    
    # Composed components (focused responsibilities)
    _geometry_collection: GeometryCollection      # Materials + Geometry commands
    _antenna_config: AntennaConfiguration         # Sources + Receivers
    _rock_collection: RockCollection              # Rock positions
    domain_settings: Optional[DomainSettings] = None
    
    # Metadata
    metadata: Dict[str, Any]  # PVC, FI, density, layer coords, etc.
    assembled: Optional[SceneDefinition] = None   # Final validated scene
```

### Composed Components

#### 1. **GeometryCollection** (Materials + Geometry)
```python
@dataclass
class GeometryCollection:
    materials: List[MaterialCommand]       # #material commands
    geometry: List[GeometryCommand]        # #box, #triangle, #cylinder, etc.
    
    def add_material(cmd: MaterialCommand) -> None
    def add_geometry(cmd: GeometryCommand) -> None
    def validate() -> List[str]            # Check for duplicates, empty lists
    def clone() -> GeometryCollection      # Shallow copy (commands immutable)
```

#### 2. **AntennaConfiguration** (TX/RX)
```python
@dataclass
class AntennaConfiguration:
    sources: List[SourceCommand]           # #waveform + #hertzian_dipole
    receivers: List[ReceiverCommand]       # #rx commands
    
    def add_source(cmd: SourceCommand) -> None
    def add_receiver(cmd: ReceiverCommand) -> None
    def reset() -> None                    # Clear for variant generation
    def validate() -> List[str]            # Check counts, types
```

#### 3. **RockCollection** (Rock Positions)
```python
@dataclass
class RockCollection:
    positions: List[Rock]                  # Rock objects with (x, y, radius, ...)
    
    def add_rock(rock: Rock) -> None
    def validate() -> List[str]            # Check count (10–10k rocks)
    def calculate_density_monte_carlo() -> float
    def to_dataframe() / from_dataframe()  # Pandas interop
```

#### 4. **DomainSettings** (gprMax Config, Immutable)
```python
@dataclass(frozen=True)
class DomainSettings:
    domain_cmd: DomainCommand              # #domain x y z
    dx_dy_dz_cmd: DxDyDzCommand            # #dx_dy_dz dx dy dz
    time_window_cmd: TimeWindowCommand     # #time_window seconds
    absorbing_bc_cmd: AbsorbingBCCommand   # PML cells
    
    @classmethod
    def from_config(config) -> DomainSettings
    def validate() -> List[str]
    def get_domain_dimensions() -> (x, y, z)
    def get_discretization() -> (dx, dy, dz)
```

---

## 3. Production Line: Orchestrator

The **ProductionLine** class orchestrates the entire generation workflow across 4 phases:

```python
class ProductionLine:
    def __init__(self, config: GeneratorConfig):
        self.config = config
        self.material_warehouse = MaterialWarehouse(config)
        self.tool_warehouse = ToolWarehouse(config)
        self.keeper = WarehouseKeeper(...)  # Facade for workers
    
    def run(self, work_order_system: WorkOrderSystem) -> SceneCheckpoint:
        """Execute full pipeline: Base → Checkpoint → Finalization → Validate"""
```

### Execution Flow

#### **PHASE 1: Base Construction**
Builds the foundational layers and rock geometry.

```
AirWorker
    ├─ Paints entire domain with free_space (air)
    ├─ Executes first (Painter's algorithm)
    └─ Quality check: verifies air box covers domain

SubgradeWorker
    ├─ Adds subgrade material definition
    ├─ Creates subgrade layer geometry (0 → SUBGRADE_TOP)
    ├─ Optional: heterogeneous sublayers with fractal texture
    └─ Quality check: verifies subgrade box exists

FormationWorker
    ├─ Adds formation/subballast material
    ├─ Creates formation layer (SUBGRADE_TOP → FORMATION_TOP)
    ├─ Optional: fractal heterogeneity + surface roughness
    └─ Quality check: verifies formation box exists

BallastWorker
    ├─ Adds clean ballast material (for background/voids)
    ├─ Creates ballast bounding box (FORMATION_TOP → BALLAST_TOP)
    ├─ Only sets bounds; GranularMatrixWorker fills with rocks
    └─ Quality check: verifies ballast box exists

GranularMatrixWorker  ← MOST COMPLEX
    ├─ 1. Reads ballast extents from CoordinateSystem
    ├─ 2. Runs packing algorithm (12 variants available)
    │   └─ Generates circles in ballast volume
    ├─ 3. Classifies by size: rocks vs. fines
    ├─ 4. Gravity settles rocks
    ├─ 5. Adds rock geometry (triangulated aggregates)
    ├─ 6. Adds fouling as solid box (exact PVC via painter's)
    ├─ 7. Calculates metadata (density, FI, PVC, etc.)
    └─ Quality check: verifies rock count (10–10k), density
```

**Result after Phase 1:**
- Geometry: air + subgrade + formation + ballast + rocks + fouling
- Materials: free_space, subgrade, formation, ballast, rock, fouling
- Rocks: positioned and gravity-settled
- Metadata: PVC, Fouling Index, density measurements

#### **PHASE 2: Checkpoint (Cloning)**
```python
checkpoint = scene.clone()
```

Creates a deep copy for potential variant support:
- Geometry & rocks cloned (shared structure for variants)
- Antennas reset (to be configured by next workers)
- Metadata copied
- Enables antenna position variants without re-running packing

#### **PHASE 3: Finalization**
Adds antenna configuration and completes assembly.

```
AntennaWorker
    ├─ Adds waveform definition (e.g., Ricker 400 MHz)
    ├─ Adds transmitter (hertzian_dipole)
    ├─ Adds receiver(s) (rx at TX offset)
    ├─ Supports bistatic/monostatic configurations
    └─ Quality check: verifies source-receiver counts match

AssemblerWorker
    ├─ Validates all components (geometry, antennas, domain)
    ├─ Builds final SceneDefinition
    ├─ Sets assembled = SceneDefinition
    └─ Quality check: ensures assembly succeeded

LabWorker (Optional)
    ├─ Calculates advanced metadata
    ├─ Fouling Index (FI) — global & local
    ├─ Surface reflectivity coefficient
    ├─ Material fractions (rock, fouling, void)
    ├─ Attenuation at multiple frequencies
    └─ Quality check: validates FI range [0, 1]
```

**Result after Phase 3:**
- Geometry: complete with air, layers, rocks, fouling, antennas
- Antenna configuration: TX/RX positioned and validated
- Metadata: comprehensive (PVC, FI, density, attenuation, material fractions)
- Scene ready for file writing

#### **PHASE 4: Validation & Statistics**
```python
# Check assembly succeeded
if not checkpoint.assembled:
    raise RuntimeError("Scene assembly failed")

# Run comprehensive validation
validation_errors = checkpoint.validate_all()

# Log statistics
work_order_system.log(f"Materials: {len(checkpoint.materials)}")
work_order_system.log(f"Geometry Commands: {len(checkpoint.geometry)}")
work_order_system.log(f"Rocks: {checkpoint.rock_count}")
work_order_system.log(f"Domain: {x}×{y}×{z}m")
```

---

## 4. Worker Pattern

All workers follow the **Worker interface**:

```python
class Worker(ABC):
    name: str  # e.g., "AirWorker", "GranularMatrixWorker"
    
    @abstractmethod
    def execute(self, scene: SceneCheckpoint, params: Dict, 
                materials: WarehouseKeeper, tools: WarehouseKeeper) -> None:
        """Modify scene state (add geometry, materials, antennas)"""
        pass
    
    @abstractmethod
    def quality_check(self, scene: SceneCheckpoint) -> List[str]:
        """Return list of validation errors (empty if OK)"""
        pass
```

### Worker Chain (RecipeBook)

The **RecipeBook** defines ordered worker sequences:

```python
class RecipeBook:
    @staticmethod
    def get_base_recipe(config, product_type="standard") -> List[Worker]:
        """Returns: [AirWorker, SubgradeWorker, FormationWorker, 
                     BallastWorker, GranularMatrixWorker]"""
        pass
    
    @staticmethod
    def get_finalization_recipe() -> List[Worker]:
        """Returns: [AntennaWorker, AssemblerWorker, LabWorker]"""
        pass
```

Workers execute **sequentially** (order matters):
1. AirWorker must run first (Painter's algorithm)
2. Subgrade → Formation → Ballast (bottom-up)
3. GranularMatrixWorker assumes ballast bounds set
4. AntennaWorker runs after geometry complete
5. AssemblerWorker validates, LabWorker calculates

---

## 5. Key Algorithmic Components

### GranularMatrixWorker (Rock Packing & Fouling)

The most complex worker, with 7 steps:

```python
class GranularMatrixWorker(Worker):
    name = "GranularMatrixWorker"
    
    def execute(self, scene, params, materials, tools):
        # Step 1: Get ballast bounds from coordinate system
        ballast_bottom, ballast_top = scene.coordinate_system.bounds(Layer.BALLAST)
        
        # Step 2: Run packing algorithm (via ToolWarehouse)
        packing_algo = scene.config.rock_packing_algorithm  # e.g., "shang-chu"
        packer = tools.get_packing_algorithm(packing_algo)
        circles = packer.pack(domain_x, ballast_thickness, max_rock_radius)
        
        # Step 3: Classify circles by size
        rocks = [c for c in circles if c.radius >= fouling_particle_size_max]
        
        # Step 4: Gravity settle (move down until touching lower layer)
        self._settle_rocks(rocks, ballast_bottom)
        
        # Step 5: Add rock geometry (triangulated aggregates)
        for rock in rocks:
            rock_geom = self._triangulate_rock(rock)  # Generate triangles
            scene.add_geometry(rock_geom)
        
        # Step 6: Add fouling as solid box (exact PVC)
        fouling_height = self._calculate_fouling_height(rocks, pvc_target)
        fouling_box = BoxCommand(..., fouling_height, ..., MC.FOULING)
        scene.add_geometry(fouling_box)
        
        # Step 7: Calculate metadata
        achieved_pvc = self._measure_pvc(rocks, fouling_box)
        achieved_density = self._measure_density(rocks)
        fouling_index = self._calculate_fouling_index(achieved_pvc)
        scene.metadata['pvc'] = achieved_pvc
        scene.metadata['achieved_density'] = achieved_density
        scene.metadata['FI_class'] = fouling_index
```

### Packing Algorithms (12 Variants)

The system provides 12 rock packing algorithms with different speed/quality tradeoffs:

| Algorithm | Speed | Quality | Use |
|-----------|-------|---------|-----|
| Random | <1s | Low | Quick tests |
| Grid | <1s | Low | Regular patterns |
| RSA | <1s | Low | Fast prototyping |
| PoissonDisk | 2-3s | Medium | Spatial distribution |
| Circlify | 1-5s | Medium | Testing |
| SimulatedAnnealing | 5-10s | Medium | Balanced |
| **ShangChu** ⭐ | 15-20s | High | Production |
| HybridShang | 15-20s | High+ | Enhanced |
| Growth, GrowthBalanced, SimplePacking, Gravity | Variable | Variable | Specialized |

**Selection Logic (ToolWarehouse):**
```python
def get_packing_algorithm(name: str) -> PackingAlgorithm:
    algorithms = {
        "shang-chu": ShangChuPacking,
        "grid": GridPacking,
        "random": RandomPacking,
        # ... 9 more
    }
    return algorithms[name]()
```

### Material Properties (Physics)

Each layer has **Peplinski parameters** for material characterization:

```python
# peplinski = (s, c, bulk, spd, wlo, whi)
subgrade_peplinski = (0.001, 0.2, 0.15, 0.0, 0.4, 0.4)
formation_peplinski = (0.001, 0.2, 0.15, 0.0, 0.4, 0.4)

# Fouling dielectric varies with PVC + moisture
def calculate_fouling_er(pvc: float, moisture: float) -> float:
    # Mixing formula based on Peplinski model
    # Higher PVC/moisture → higher permittivity
    pass
```

---

## 6. Data Flow: From Config to .in File

### Input: GeneratorConfig

```python
@dataclass
class GeneratorConfig:
    # Domain
    domain_x: float = 2.248
    domain_y: float = 3.199
    domain_z: float = 0.0132
    dx: float = 0.0132  # λ/10 at 400 MHz
    dy: float = 0.0132
    dz: float = 0.0132
    
    # Layers
    subgrade_thickness: float = 0.20
    formation_thickness: float = 0.10
    max_ballast_thickness: float = 0.55
    
    # Antenna
    tx_frequency: float = 400e6
    antenna_separation: float = 0.05
    antenna_clearance_above_ballast: float = 0.5
    
    # Fouling
    pvc_target: float = 50.0
    moisture_content: float = 0.50
    
    # Packing
    rock_packing_algorithm: str = "shang-chu"
    max_rock_radius: float = 0.05
    
    # Physics
    heterogeneous_sublayers: bool = True
    layer_roughness_depth: float = 0.02
```

### Processing: ProductionLine

```
Config → LayerStack → CoordinateSystem
          ↓
    SceneCheckpoint (empty)
          ↓
    [Worker Pipeline: 5 + 3 workers]
          ↓
    SceneCheckpoint (filled)
          ↓
    SceneDefinition (validated, immutable)
```

### Output: .in File Format

```
## pvc: 50.0
## moisture: 0.50
## achieved_density: 0.43
## FI_class: F
## Lab_FI: 0.65
...
#domain 2.248 3.199 0.0132
#dx_dy_dz 0.0132 0.0132 0.0132
#time_window 2e-08
#pml_cells 10 10 0 10 10 0
#waveform ricker 1 4e+08 ricker_src
#hertzian_dipole z 0.5 0.75 0.00660 ricker_src
#rx 0.55 0.75 0.00660
#material 5 0 1 0 bal_rock
#material 10 0.01 1 0 subgrade
#box 0 0 0 2.248 0.20 0.0132 subgrade
#box 0 0.20 0 2.248 0.30 0.0132 formation
...
```

---

## 7. Quality Assurance & Validation

### Worker Quality Checks

Each worker validates its output:
```python
class AirWorker:
    def quality_check(self, scene) -> List[str]:
        if not scene.geometry:
            return ["No geometry added"]
        first = scene.geometry[0]
        if not isinstance(first, BoxCommand) or first.material != MC.AIR:
            return ["First command is not air box"]
        return []  # OK
```

### Scene Validation (SceneCheckpoint)

```python
def validate_all(self) -> List[str]:
    errors = []
    
    # Validate components
    errors.extend(self._geometry_collection.validate())
    errors.extend(self._antenna_config.validate())
    errors.extend(self._rock_collection.validate())
    errors.extend(self.domain_settings.validate())
    
    # Check counts
    if len(self.geometry) < 5:
        errors.append("Insufficient geometry commands")
    
    # Check coherence
    if not self.antennas_configured:
        errors.append("Antennas not configured")
    
    return errors
```

### Production Line Error Handling

```python
try:
    worker.execute(scene, {}, keeper, keeper)
    errors = worker.quality_check(scene)
    for err in errors:
        scene.log_issue(worker.name, "error", "high", err)
except Exception as e:
    # Log full traceback to stderr
    scene.log_issue(worker.name, "crash", "critical", f"Crash: {str(e)}\n{trace}")
    raise RuntimeError(f"Production line failed: {worker.name}")

# Check for critical errors before proceeding
if _has_critical_errors(work_order_system):
    raise RuntimeError("Critical errors detected")
```

---

## 8. Extension Points

### Adding a New Worker

To add a custom worker (e.g., water table layer):

```python
class WaterTableWorker(Worker):
    name = "WaterTableWorker"
    
    def execute(self, scene: SceneCheckpoint, params, materials, tools):
        # Add water layer at depth
        water_y = scene.coordinate_system.get_y(Anchor.BALLAST_TOP, -0.1)
        water_top = scene.coordinate_system.get_y(Anchor.BALLAST_TOP)
        scene.add_material(materials.get_material("water"))
        scene.add_geometry(BoxCommand(0, water_y, 0, 
                                      scene.config.domain_x, 
                                      water_top,
                                      scene.config.domain_z, "water"))
    
    def quality_check(self, scene) -> List[str]:
        # Verify water box exists
        return [] if any(cmd.material == "water" for cmd in scene.geometry) else ["No water"]

# Add to recipe
base_recipe = [AirWorker, SubgradeWorker, ..., WaterTableWorker, GranularMatrixWorker, ...]
```

### Replacing a Packing Algorithm

To use a different rock packing strategy:

```python
# In config:
config.rock_packing_algorithm = "circlify"  # or "grid", "random", etc.

# ToolWarehouse automatically selects:
packer = tools.get_packing_algorithm("circlify")
circles = packer.pack(domain_x, ballast_height, max_radius)
```

### Variant Generation

The checkpoint cloning enables variants with different antenna positions:

```python
# Phase 2 checkpoint created after base construction
checkpoint = scene.clone()  # Geometry & rocks shared

# AntennaWorker can be run with different parameters
# (antenna offset, frequency, etc.) on cloned checkpoint
```

---

## 9. Design Rationale

### Why Composition Over Inheritance?

**Problem:** SceneCheckpoint was a God Object with 50+ fields.
```python
# ❌ Old: Everything on one class
class SceneCheckpoint:
    materials = []
    geometry = []
    sources = []
    receivers = []
    rocks = []
    metadata = {}
    # ... 40 more fields
```

**Solution:** Delegate to focused components.
```python
# ✅ New: Composed components
class SceneCheckpoint:
    _geometry_collection: GeometryCollection      # Materials + Geometry
    _antenna_config: AntennaConfiguration         # TX/RX
    _rock_collection: RockCollection              # Rocks
    domain_settings: DomainSettings               # Domain config
```

**Benefits:**
- Each component has single responsibility
- Easier to test and validate independently
- Reduced cognitive load per class
- Natural delegation methods on SceneCheckpoint

### Why Immutable LayerStack + CoordinateSystem?

**Problem:** Workers hardcoded y-coordinates, causing inconsistencies.
```python
# ❌ Old: Magic numbers everywhere
y_ballast_top = 0.35
y_antenna = 0.85
y_domain_top = 0.95
```

**Solution:** Centralize in immutable LayerStack.
```python
# ✅ New: Single source of truth
layer_stack = LayerStack(
    subgrade=0.20,
    formation=0.10,
    ballast=0.25,
    antenna_clearance=0.5,
    air_buffer=0.1
)
coords = CoordinateSystem(layer_stack)
y_ballast_top = coords.get_y(Anchor.BALLAST_TOP)
```

**Benefits:**
- One place to change layer thicknesses
- Type-safe (Anchor enum vs. strings)
- Pre-computed for performance
- Frozen after initialization (immutable)

### Why Worker + RecipeBook Pattern?

**Problem:** Monolithic generation function with deep nesting.
```python
# ❌ Old: All logic in one function
def generate_scene(config):
    add_air()
    add_subgrade()
    add_formation()
    add_ballast()
    add_rocks()  # 200 lines
    add_fouling()
    add_antenna()
    validate()
```

**Solution:** Decoupled workers with choreography.
```python
# ✅ New: Ordered workers, each with single job
workers = [
    AirWorker,
    SubgradeWorker,
    FormationWorker,
    BallastWorker,
    GranularMatrixWorker,  # Single responsibility
    AntennaWorker,
]
for worker in workers:
    worker.execute(scene)
    errors = worker.quality_check(scene)
```

**Benefits:**
- Easy to add/remove/reorder workers
- Each worker testable independently
- Clear failure points (which worker failed?)
- Logging per-worker
- Recipe patterns enable variants

---

## 10. Key Invariants

1. **Domain must fit layer stack**
   ```
   domain_y ≥ subgrade + formation + ballast + antenna_clearance + air_buffer
   ```

2. **Rocks must be within ballast bounds**
   ```
   ballast_bottom ≤ rock.y ≤ ballast_top
   ```

3. **Antenna must be above ballast**
   ```
   antenna_y > ballast_top
   ```

4. **Material names must be unique**
   ```
   len(materials) == len(set(m.name for m in materials))
   ```

5. **Geometry commands must have valid materials**
   ```
   All geometry commands reference materials that exist
   ```

6. **PVC must be in [0, 1]**
   ```
   0.0 ≤ pvc ≤ 1.0
   ```

---

## 11. File Organization

```
src/
├── production_line.py        # Orchestrator (Phases 1-4)
├── worker.py                 # Worker base class, SceneCheckpoint
├── workers.py                # Concrete workers (Air, Subgrade, ..., Antenna)
├── granular_worker.py        # GranularMatrixWorker (rock packing + fouling)
├── scene_geometry.py         # Composed components (GeometryCollection, etc.)
├── scene_descriptor.py       # SceneDefinition (validated output)
├── domain/
│   ├── coordinates.py        # LayerStack, CoordinateSystem, Anchor
│   └── value_objects.py      # Point3D, LayerBounds, etc.
├── config.py                 # GeneratorConfig
├── gpr_commands.py           # GPR command classes (.in file primitives)
├── recipes.py                # RecipeBook (worker orderings)
├── warehouses.py             # Material & Tool warehouses
└── warehouse_keeper.py       # Keeper (facade for workers)
```

---

## Summary

The scene creation architecture achieves:
- **Modularity**: 5-8 independent workers
- **Clarity**: Named anchors instead of magic numbers
- **Extensibility**: Add workers without modifying existing ones
- **Testability**: Each component can be tested in isolation
- **Maintainability**: Single responsibilities, composition-based design
- **Robustness**: Validation at each phase, comprehensive error handling

This design enables robust, scalable generation of complex railway ballast geometries with precise control over every physical parameter.

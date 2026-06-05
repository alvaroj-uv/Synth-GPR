# Scene Creation Architecture — Sequence Diagrams

Visual representations of how components interact during scene generation.

---

## 1. Main Production Line Execution

```
User (GeneratorConfig) → ProductionLine → Workers → SceneCheckpoint → Output

┌──────────────────────────────────────────────────────────────────────────┐
│                      PRODUCTION LINE EXECUTION                            │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                            │
│  1. INITIALIZATION                                                        │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │ Input: GeneratorConfig (domain, layers, materials, packing)      │   │
│  │                                                                  │   │
│  │ ProductionLine.__init__(config)                                 │   │
│  │   ├─ material_warehouse = MaterialWarehouse(config)             │   │
│  │   ├─ tool_warehouse = ToolWarehouse(config)                     │   │
│  │   └─ keeper = WarehouseKeeper(material_warehouse, tool_warehouse)│  │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                            │
│  2. SETUP                                                                 │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │ ProductionLine.run(work_order_system)                            │   │
│  │                                                                  │   │
│  │   layer_stack = LayerStack(subgrade=0.2, formation=0.1, ...)    │   │
│  │   coords = CoordinateSystem(layer_stack, domain_x, domain_z)    │   │
│  │   scene = SceneCheckpoint(config, coordinate_system=coords)     │   │
│  │                                                                  │   │
│  │   [PRE-FLIGHT CHECK: domain_y ≥ total_height?]                  │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                            │
│  3. PHASE 1: BASE CONSTRUCTION (Sequential Worker Execution)             │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │ for worker in [Air, Subgrade, Formation, Ballast, Granular]:    │   │
│  │                                                                  │   │
│  │   worker.execute(scene, {}, keeper, keeper)                     │   │
│  │   │                                                             │   │
│  │   ├─ Add materials to scene._geometry_collection                │   │
│  │   ├─ Add geometry commands to scene._geometry_collection        │   │
│  │   ├─ Add rocks to scene._rock_collection (if applicable)        │   │
│  │   └─ Update scene.metadata (PVC, FI, density, etc.)             │   │
│  │                                                                  │   │
│  │   errors = worker.quality_check(scene)                          │   │
│  │   if errors:                                                    │   │
│  │       scene.log_issue(worker.name, "error", "high", err)        │   │
│  │                                                                  │   │
│  │   if scene has CRITICAL errors:                                 │   │
│  │       raise RuntimeError("Production line failed in Base Phase")│   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                            │
│  4. PHASE 2: CHECKPOINT (Cloning for Variant Support)                   │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │ checkpoint = scene.clone()                                       │   │
│  │                                                                  │   │
│  │   checkpoint._geometry_collection = scene._geometry_collection  │   │
│  │                                        .clone()                 │   │
│  │   checkpoint._antenna_config = AntennaConfiguration()  [RESET]  │   │
│  │   checkpoint._rock_collection = scene._rock_collection.clone()  │   │
│  │   checkpoint.metadata = copy(scene.metadata)                    │   │
│  │                                                                  │   │
│  │   [Now can run variant workers on checkpoint without re-packing]│   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                            │
│  5. PHASE 3: FINALIZATION (Antenna + Assembly + Lab)                    │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │ for worker in [Antenna, Assembler, Lab]:                        │   │
│  │                                                                  │   │
│  │   worker.execute(checkpoint, {}, keeper, keeper)                │   │
│  │   │                                                             │   │
│  │   ├─ AntennaWorker:                                             │   │
│  │   │   └─ Add sources + receivers to _antenna_config             │   │
│  │   │                                                             │   │
│  │   ├─ AssemblerWorker:                                           │   │
│  │   │   ├─ Validate all components                                │   │
│  │   │   └─ Create SceneDefinition (assembled = {...})             │   │
│  │   │                                                             │   │
│  │   └─ LabWorker:                                                 │   │
│  │       ├─ Calculate Fouling Index (FI)                           │   │
│  │       ├─ Calculate surface reflectivity                         │   │
│  │       ├─ Calculate attenuation at 400 MHz, 2 GHz                │   │
│  │       └─ Update checkpoint.metadata                             │   │
│  │                                                                  │   │
│  │   errors = worker.quality_check(checkpoint)                     │   │
│  │   if CRITICAL: raise RuntimeError("Finalization failed")        │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                            │
│  6. PHASE 4: VALIDATION & STATISTICS                                     │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │ if not checkpoint.assembled:                                    │   │
│  │     raise RuntimeError("Scene failed assembly validation")      │   │
│  │                                                                  │   │
│  │ validation_errors = checkpoint.validate_all()                   │   │
│  │                                                                  │   │
│  │ Log statistics:                                                 │   │
│  │   - Materials: {count}                                          │   │
│  │   - Geometry Commands: {count}                                  │   │
│  │   - Rocks: {count}                                              │   │
│  │   - Sources/Receivers: {count} each                             │   │
│  │   - Domain: {x}×{y}×{z}m, Resolution: {dx}×{dy}×{dz}m          │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                            │
│  7. RETURN                                                                │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │ return checkpoint  [Ready for persistence to .in file]          │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                            │
└──────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Worker Execution Detail (GranularMatrixWorker Example)

```
GranularMatrixWorker.execute() — Most complex worker

┌──────────────────────────────────────────────────────────────────────────┐
│                       GRANULAR MATRIX WORKER                              │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                            │
│  INPUT: scene (mutable checkpoint), keeper (warehouses)                   │
│                                                                            │
│  STEP 1: Determine Ballast Bounds                                         │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │ bounds = scene.coordinate_system.bounds(Layer.BALLAST)           │   │
│  │ ballast_bottom = bounds.bottom  (e.g., 0.30 m)                  │   │
│  │ ballast_top = bounds.top        (e.g., 0.55 m)                  │   │
│  │ ballast_height = 0.25 m                                          │   │
│  │ domain_x = scene.config.domain_x  (e.g., 2.248 m)               │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                            │
│  STEP 2: Get Packing Algorithm (via ToolWarehouse)                       │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │ algo_name = scene.config.rock_packing_algorithm  (e.g., "shang-chu")│
│  │ packer = keeper.get_packing_algorithm(algo_name)                 │   │
│  │                                                                  │   │
│  │ Available: Random, Grid, RSA, PoissonDisk, Circlify,            │   │
│  │            SimulatedAnnealing, ShangChu, HybridShang, Growth... │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                            │
│  STEP 3: Pack Rocks                                                       │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │ circles = packer.pack(                                           │   │
│  │     domain_x=2.248,                                              │   │
│  │     height=0.25,                                                 │   │
│  │     max_radius=0.05,                                             │   │
│  │     min_radius=0.005                                             │   │
│  │ )                                                                │   │
│  │                                                                  │   │
│  │ [Packing algorithm runs, returns list of Circle objects]         │   │
│  │ [Time: <1s (fast) to 20s (ShangChu)]                             │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                            │
│  STEP 4: Classify Circles (Rocks vs. Fines)                              │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │ min_rock_size = 2 × scene.config.fouling_particle_size_max       │   │
│  │                 (e.g., 2 × 0.002 = 0.004 m)                     │   │
│  │                                                                  │   │
│  │ rocks = []                                                       │   │
│  │ for circle in circles:                                           │   │
│  │     if circle.radius >= min_rock_size:                           │   │
│  │         rocks.append(circle)                                     │   │
│  │     else:                                                        │   │
│  │         # Discard fines (will be part of fouling)                │   │
│  │         pass                                                     │   │
│  │                                                                  │   │
│  │ Result: rocks = [50–200 large aggregates]                        │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                            │
│  STEP 5: Gravity Settle Rocks                                             │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │ for rock in rocks:                                               │   │
│  │     # Lower rock until it touches ballast bottom or another rock │   │
│  │     rock.y = max(rock.y - 100,  # Large downward shift          │   │
│  │                  ballast_bottom + rock.radius)  # Min position   │   │
│  │                                                                  │   │
│  │ [Simulates gravity without full dynamics]                        │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                            │
│  STEP 6: Add Rock Geometry Commands                                       │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │ for rock in rocks:                                               │   │
│  │     # Triangulate rock aggregate (convert circle to 3D triangles)│   │
│  │     triangles = triangulate_rock(rock.x, rock.y, rock.radius)   │   │
│  │                                                                  │   │
│  │     scene.add_geometry(triangles)  # Add to _geometry_collection│   │
│  │     scene.add_rock(rock)           # Track position             │   │
│  │                                                                  │   │
│  │ [Now scene contains ~50–200 rock triangles]                      │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                            │
│  STEP 7: Add Fouling Box (Exact PVC via Painter's Algorithm)             │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │ pvc_target = scene.config.pvc_target  (e.g., 50.0%)              │   │
│  │                                                                  │   │
│  │ fouling_height = calculate_fouling_height(rocks, pvc_target)    │   │
│  │                 (e.g., 0.10 m)                                  │   │
│  │                                                                  │   │
│  │ scene.add_material(fouling_material)                             │   │
│  │                                                                  │   │
│  │ fouling_box = BoxCommand(                                        │   │
│  │     x1=0,  y1=ballast_bottom,  z1=0,                            │   │
│  │     x2=domain_x,  y2=ballast_bottom + fouling_height,  z2=dz,   │   │
│  │     material='bal_foul_granular'                                 │   │
│  │ )                                                                │   │
│  │ scene.add_geometry(fouling_box)                                  │   │
│  │                                                                  │   │
│  │ [Painter's algorithm: later (fouling) commands override earlier │   │
│  │  (rock) geometry where they overlap]                            │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                            │
│  STEP 8: Calculate Metadata                                               │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │ # Measured PVC (actual void contamination)                       │   │
│  │ achieved_pvc = measure_pvc(rocks, fouling_box)                   │   │
│  │                                                                  │   │
│  │ # Packing density (volume fraction of solids)                    │   │
│  │ achieved_density = rocks.calculate_density_monte_carlo(...)      │   │
│  │                                                                  │   │
│  │ # Fouling Index classification (C, MC, MF, F, HF)               │   │
│  │ fi_class = classify_by_fouling_index(achieved_pvc)              │   │
│  │                                                                  │   │
│  │ scene.metadata.update({                                          │   │
│  │     'pvc': pvc_target,                                           │   │
│  │     'mc_pvc_measured': achieved_pvc,                             │   │
│  │     'achieved_density': achieved_density,                        │   │
│  │     'FI_class': fi_class,                                        │   │
│  │     'mc_y_min': ballast_bottom,                                  │   │
│  │     'mc_y_max': ballast_top,                                     │   │
│  │     'mc_y_local_max': ballast_top,                               │   │
│  │ })                                                               │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                            │
│  OUTPUT: scene (modified in-place)                                        │
│    - _geometry_collection: +rocks, +fouling box, +materials               │
│    - _rock_collection: +50–200 rocks                                      │
│    - metadata: +pvc, density, FI_class, coordinates                       │
│                                                                            │
└──────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Coordinate System Resolution

```
How semantic anchors become absolute Y coordinates

INPUT: LayerStack (frozen)

┌──────────────────────────────────────────────────────────────────────────┐
│                      LAYER STACK INITIALIZATION                           │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                            │
│  LayerStack(                                                              │
│      subgrade_thickness=0.20,                                             │
│      formation_thickness=0.10,                                            │
│      ballast_thickness=0.25,                                              │
│      antenna_clearance=0.5,                                               │
│      air_buffer=0.1                                                       │
│  )                                                                         │
│                                                                            │
│  ↓                                                                         │
│                                                                            │
│  CoordinateSystem(layer_stack, domain_x=2.248, domain_z=0.0132)          │
│                                                                            │
│    _compute_levels():                                                     │
│    ┌──────────────────────────────────────────────────────────────┐      │
│    │  current_y = 0.0                                             │      │
│    │                                                              │      │
│    │  BOTTOM                      → _y_levels[BOTTOM] = 0.0       │      │
│    │  current_y += 0.20           → current_y = 0.20              │      │
│    │  SUBGRADE_TOP                → _y_levels[SUBGRADE_TOP] = 0.20│     │
│    │  current_y += 0.10           → current_y = 0.30              │      │
│    │  FORMATION_TOP               → _y_levels[FORMATION_TOP] = 0.30│    │
│    │  BALLAST_BOTTOM (alias)      → _y_levels[BALLAST_BOTTOM] = 0.30│   │
│    │  current_y += 0.25           → current_y = 0.55              │      │
│    │  BALLAST_TOP                 → _y_levels[BALLAST_TOP] = 0.55│      │
│    │  current_y += 0.5            → current_y = 1.05              │      │
│    │  ANTENNA_LEVEL               → _y_levels[ANTENNA_LEVEL] = 1.05│    │
│    │  current_y += 0.1            → current_y = 1.15              │      │
│    │  DOMAIN_TOP                  → _y_levels[DOMAIN_TOP] = 1.15  │      │
│    └──────────────────────────────────────────────────────────────┘      │
│                                                                            │
└──────────────────────────────────────────────────────────────────────────┘

USAGE:

┌──────────────────────────────────────────────────────────────────────────┐
│                         ANCHOR → Y RESOLUTION                             │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                            │
│  In workers, instead of:                                                  │
│    y = 0.30  # What does 0.30 mean? Formation top? Ballast bottom?       │
│                                                                            │
│  Write:                                                                    │
│    y = coords.get_y(Anchor.FORMATION_TOP)  # Explicit: 0.30              │
│    y = coords.get_y(Anchor.BALLAST_TOP)    # Explicit: 0.55              │
│    y = coords.get_y(Anchor.ANTENNA_LEVEL, offset=0.05)  # 1.10          │
│                                                                            │
│  TYPE-SAFE LAYER BOUNDS:                                                  │
│    bounds = coords.bounds(Layer.BALLAST)                                  │
│    # returns LayerBounds(bottom=0.30, top=0.55)                           │
│    # instead of tuple (0.30, 0.55)                                        │
│                                                                            │
│  LEGACY STRING LOOKUP (deprecated):                                       │
│    y_bottom, y_top = coords.get_layer_bounds("ballast")                   │
│    # returns (0.30, 0.55)                                                 │
│                                                                            │
└──────────────────────────────────────────────────────────────────────────┘

RESULT: Single source of truth

  Change LayerStack → All workers automatically use new coordinates
  No hardcoded y values scattered across codebase
  Type-safe (Enum instead of magic strings)
```

---

## 4. SceneCheckpoint Composition

```
SceneCheckpoint delegates to composed components

┌──────────────────────────────────────────────────────────────────────────┐
│                      SCENE CHECKPOINT STRUCTURE                           │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                            │
│  SceneCheckpoint                                                          │
│  ├─ config: GeneratorConfig                                               │
│  ├─ work_order: WorkOrderSystem                                           │
│  ├─ coordinate_system: CoordinateSystem                                   │
│  │                                                                        │
│  ├─ _geometry_collection: GeometryCollection                              │
│  │  ├─ materials: [MaterialCommand, ...]                                  │
│  │  └─ geometry: [GeometryCommand, ...]                                   │
│  │      [Commands added by workers]                                       │
│  │                                                                        │
│  ├─ _antenna_config: AntennaConfiguration                                 │
│  │  ├─ sources: [SourceCommand, ...]                                      │
│  │  └─ receivers: [ReceiverCommand, ...]                                  │
│  │      [Configured by AntennaWorker]                                     │
│  │                                                                        │
│  ├─ _rock_collection: RockCollection                                      │
│  │  └─ positions: [Rock(x, y, radius), ...]                               │
│  │      [Tracked by GranularMatrixWorker]                                 │
│  │                                                                        │
│  ├─ domain_settings: DomainSettings (immutable)                            │
│  │  ├─ domain_cmd: DomainCommand                                          │
│  │  ├─ dx_dy_dz_cmd: DxDyDzCommand                                        │
│  │  ├─ time_window_cmd: TimeWindowCommand                                 │
│  │  └─ absorbing_bc_cmd: AbsorbingBCCommand                               │
│  │      [Created from config at __post_init__]                            │
│  │                                                                        │
│  ├─ metadata: Dict[str, Any]                                              │
│  │  ├─ pvc: float                                                         │
│  │  ├─ achieved_density: float                                            │
│  │  ├─ FI_class: str                                                      │
│  │  ├─ fouling_height: float                                              │
│  │  ├─ Lab_FI: float (global Fouling Index)                               │
│  │  ├─ Lab_FI_local: float (local near measurement point)                │
│  │  └─ ... 20+ more metadata fields                                       │
│  │      [Updated by workers, especially GranularMatrixWorker & LabWorker] │
│  │                                                                        │
│  └─ assembled: SceneDefinition (set by AssemblerWorker)                    │
│     └─ Final validated scene ready for .in file writing                    │
│                                                                            │
└──────────────────────────────────────────────────────────────────────────┘

DELEGATION PATTERN:

  scene.add_material(cmd)
    → delegates to _geometry_collection.add_material(cmd)

  scene.add_geometry(cmd)
    → delegates to _geometry_collection.add_geometry(cmd)

  scene.add_source(cmd)
    → delegates to _antenna_config.add_source(cmd)

  scene.add_receiver(cmd)
    → delegates to _antenna_config.add_receiver(cmd)

  scene.materials
    → property: returns _geometry_collection.materials

  scene.geometry
    → property: returns _geometry_collection.geometry

  BENEFITS:
  - Each component has focused responsibility
  - Easy to test components independently
  - Clear separation of concerns
  - Validation per-component possible
```

---

## 5. File Writing Flow

```
After Production Line returns SceneCheckpoint

┌──────────────────────────────────────────────────────────────────────────┐
│                         FROM SCENE TO FILE                                │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                            │
│  SceneCheckpoint (in-memory, mutable)                                     │
│  │                                                                        │
│  ├─ Contains: geometry, materials, antennas, rocks, metadata              │
│  │                                                                        │
│  └─ AssemblerWorker.execute():                                            │
│     └─ scene.assembled = SceneDefinition(...)                             │
│                                                                            │
│        SceneDefinition (validated, immutable)                             │
│        ├─ config: GeneratorConfig                                         │
│        ├─ domain_commands: [DomainCommand, DxDyDzCommand, ...]            │
│        ├─ material_commands: [MaterialCommand, ...]                       │
│        ├─ source_commands: [WaveformCommand, HertzianDipoleCommand, ...]  │
│        ├─ geometry_commands: [BoxCommand, TriangleCommand, ...]           │
│        ├─ python_blocks: [PythonCommand, ...]                             │
│        └─ metadata: Dict[str, Any]                                        │
│                                                                            │
│  User calls: InFileWriter.write_in_file(scene, "output.in")              │
│                                                                            │
│  InFileWriter.write_in_file():                                             │
│  │                                                                        │
│  ├─ Step 1: Open file "output.in" for writing                             │
│  │                                                                        │
│  ├─ Step 2: Write header (## metadata comments)                           │
│  │   ├─ ## pvc: 50.0                                                     │
│  │   ├─ ## moisture: 0.50                                                 │
│  │   ├─ ## achieved_density: 0.43                                         │
│  │   ├─ ## FI_class: F                                                    │
│  │   ├─ ## Lab_FI: 0.65                                                   │
│  │   └─ ... 20+ metadata lines                                            │
│  │                                                                        │
│  ├─ Step 3: Write domain commands                                         │
│  │   ├─ #domain 2.248 3.199 0.0132                                        │
│  │   ├─ #dx_dy_dz 0.0132 0.0132 0.0132                                    │
│  │   ├─ #time_window 2e-08                                                │
│  │   └─ #pml_cells 10 10 0 10 10 0                                        │
│  │                                                                        │
│  ├─ Step 4: Write materials                                               │
│  │   ├─ #material 5 0 1 0 bal_rock                                        │
│  │   ├─ #material 10 0.01 1 0 subgrade                                    │
│  │   ├─ #material 10 0.01 1 0 formation                                   │
│  │   └─ #material <er> <sigma> 1 0 bal_foul_granular                      │
│  │                                                                        │
│  ├─ Step 5: Write waveform                                                │
│  │   └─ #waveform ricker 1 4e+08 ricker_src                               │
│  │                                                                        │
│  ├─ Step 6: Write antenna (TX)                                            │
│  │   └─ #hertzian_dipole z 1.124 0.75 0.00660 ricker_src                  │
│  │                                                                        │
│  ├─ Step 7: Write antenna (RX)                                            │
│  │   └─ #rx 1.174 0.75 0.00660                                            │
│  │                                                                        │
│  ├─ Step 8: Write geometry commands (painter's order)                     │
│  │   ├─ #box 0 0 0 2.248 3.199 0.0132 free_space                          │
│  │   ├─ #box 0 0 0 2.248 0.20 0.0132 subgrade                             │
│  │   ├─ #box 0 0.20 0 2.248 0.30 0.0132 formation                         │
│  │   ├─ #box 0 0.30 0 2.248 0.55 0.0132 bal_rock                          │
│  │   ├─ #triangle ... (50–200 rock aggregates)                             │
│  │   └─ #box 0 0.30 0 2.248 0.40 0.0132 bal_foul_granular                 │
│  │                                                                        │
│  └─ Step 9: Close file                                                    │
│                                                                            │
│  OUTPUT: "output.in" (text file, ~50–200 KB)                              │
│                                                                            │
│  Now ready for:                                                            │
│  $ gprMax output.in  (runs FDTD simulation on GPU)                         │
│  → produces output.out (HDF5 binary with Ez waveform)                      │
│                                                                            │
└──────────────────────────────────────────────────────────────────────────┘
```

---

## 6. Error Handling & Validation

```
Quality checks at each stage

┌──────────────────────────────────────────────────────────────────────────┐
│                   WORKER EXECUTION & QC FLOW                              │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                            │
│  for worker in workers:                                                   │
│                                                                            │
│    try:                                                                    │
│      worker.execute(scene, {}, keeper, keeper)                            │
│      │                                                                    │
│      ├─ Worker modifies scene (add geometry, materials, etc.)             │
│      │                                                                    │
│      errors = worker.quality_check(scene)                                │
│      │                                                                    │
│      if errors:                                                           │
│          for error_msg in errors:                                         │
│              scene.log_issue(                                             │
│                  worker.name,                                             │
│                  severity="error",                                        │
│                  importance="high",                                       │
│                  message=error_msg                                        │
│              )                                                            │
│                                                                            │
│    except Exception as e:                                                 │
│      # Crash handling                                                     │
│      trace = traceback.format_exc()                                       │
│                                                                            │
│      scene.log_issue(                                                     │
│          worker.name,                                                     │
│          severity="crash",                                                │
│          importance="critical",                                           │
│          message=f"Exception: {str(e)}\n{trace}"                          │
│      )                                                                     │
│                                                                            │
│      # Print to stderr immediately                                        │
│      sys.stderr.write(                                                    │
│          f"[CRITICAL WORKER FAILURE]\n"                                   │
│          f"Worker: {worker.name}\n"                                       │
│          f"Error: {str(e)}\n"                                             │
│          f"{trace}\n"                                                     │
│      )                                                                     │
│                                                                            │
│      raise RuntimeError(f"Worker {worker.name} crashed")                  │
│                                                                            │
│  # Check for critical errors after each worker                            │
│  if _has_critical_errors(work_order_system):                              │
│      raise RuntimeError("Critical errors detected")                       │
│                                                                            │
└──────────────────────────────────────────────────────────────────────────┘

COMPONENT VALIDATION (Phase 4):

  scene.validate_all() → List[str] errors

  Delegates to:
  ├─ _geometry_collection.validate()
  │  ├─ Check: materials non-empty?
  │  ├─ Check: geometry non-empty?
  │  └─ Check: no duplicate material names?
  │
  ├─ _antenna_config.validate()
  │  ├─ Check: sources exist (exclude waveform defs)?
  │  ├─ Check: receivers exist?
  │  └─ Check: source count ≈ receiver count?
  │
  ├─ _rock_collection.validate()
  │  ├─ Check: rock count in [10, 10000]?
  │  └─ Check: rocks within ballast bounds?
  │
  └─ domain_settings.validate()
     ├─ Check: domain dimensions positive?
     ├─ Check: discretization positive?
     ├─ Check: discretization < domain size?
     └─ Check: time window > 0?
```

---

## 7. Cloning for Variant Support

```
Phase 2: Creating checkpoint for antenna variants

┌──────────────────────────────────────────────────────────────────────────┐
│                           CHECKPOINT CLONING                              │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                            │
│  After Phase 1 (base construction): scene is fully populated              │
│                                                                            │
│  scene =                                                                  │
│  ├─ geometry_collection:                                                  │
│  │  ├─ materials: [air, subgrade, formation, ballast, rock, fouling]      │
│  │  └─ geometry: [air_box, subgrade_box, formation_box, ballast_box,      │
│  │              ~100 rock_triangles, fouling_box]                         │
│  ├─ antenna_config:                                                       │
│  │  ├─ sources: []  (empty, not configured yet)                           │
│  │  └─ receivers: []  (empty)                                             │
│  ├─ rock_collection:                                                      │
│  │  └─ positions: [Rock(x=0.5, y=0.32, r=0.015), ...]  (50–200 rocks)    │
│  └─ metadata:                                                             │
│     ├─ pvc: 0.50                                                          │
│     ├─ achieved_density: 0.43                                             │
│     └─ FI_class: 'F'                                                      │
│                                                                            │
│  checkpoint = scene.clone()                                               │
│                                                                            │
│  Creates:                                                                 │
│  ├─ geometry_collection.clone()                                            │
│  │  ├─ materials: [same references, shallow copy of list]                 │
│  │  └─ geometry: [same references, shallow copy of list]                  │
│  │                                                                        │
│  ├─ antenna_config.clone_empty()                                          │
│  │  ├─ sources: []  ← RESET (empty for new antenna config)                │
│  │  └─ receivers: []  ← RESET                                             │
│  │                                                                        │
│  ├─ rock_collection.clone()                                               │
│  │  └─ positions: [Rock(...), ...]  (copy of list, same Rock objects)     │
│  │                                                                        │
│  └─ metadata: dict(scene.metadata)  (deep copy)                           │
│                                                                            │
│  result:                                                                  │
│  ├─ Geometry & rocks shared (same Circle/Triangle references)             │
│  ├─ Antenna config reset (can be reconfigured)                            │
│  ├─ Metadata copied (independent from original)                           │
│                                                                            │
│  Benefit:                                                                 │
│  ├─ Can run multiple antenna configurations WITHOUT re-packing            │
│  ├─ Geometry shared (memory efficient)                                    │
│  └─ Antennas independent (can vary position, frequency, etc.)             │
│                                                                            │
│  Future Use Case:                                                         │
│  ├─ For each antenna offset in [0.03, 0.05, 0.07]:                        │
│  │  ├─ variant = checkpoint.clone()                                       │
│  │  ├─ AntennaWorker.execute(variant, antenna_offset)                     │
│  │  └─ AssemblerWorker.execute(variant)                                   │
│  │  → variant becomes scene_at_offset_0.03.in                             │
│  └─ All variants share same rock geometry                                 │
│                                                                            │
└──────────────────────────────────────────────────────────────────────────┘
```

---

## 8. Material Property Resolution

```
How peplinski parameters become dielectric permittivity

┌──────────────────────────────────────────────────────────────────────────┐
│                         MATERIAL SYNTHESIS                                │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                            │
│  INPUT: GeneratorConfig + PVC + Moisture                                  │
│                                                                            │
│  For each layer (subgrade, formation, ballast, fouling):                  │
│                                                                            │
│  ┌────────────────────────────────────────────────────────────────┐      │
│  │  subgrade_peplinski = (s, c, bulk, spd, wlo, whi)             │      │
│  │                     = (0.001, 0.2, 0.15, 0.0, 0.4, 0.4)       │      │
│  │  formation_peplinski = (same)                                  │      │
│  │  ballast_peplinski = (0.001, 0.3, 0.15, 0.0, 0.5, 0.5)        │      │
│  └────────────────────────────────────────────────────────────────┘      │
│                                                                            │
│  HETEROGENEOUS SUBLAYERS (optional):                                      │
│  │  if config.heterogeneous_sublayers:                                    │
│  │      for each layer:                                                   │
│  │          emit #soil_peplinski + #fractal_box                           │
│  │      else:                                                             │
│  │          emit #material + #box                                         │
│  │                                                                        │
│  │  Benefits of heterogeneous:                                            │
│  │  - Realistic spatial variation                                         │
│  │  - Fractal texture matches real soil                                   │
│  │  - More realistic scattering in FDTD                                   │
│  │                                                                        │
│  │  Tradeoff:                                                             │
│  │  - More #fractal_box commands (slower gprMax)                          │
│  │  - More complex .in file                                               │
│  │  - Minimal effect on A-scan features (waveform unchanged)              │
│  └────────────────────────────────────────────────────────────────┘      │
│                                                                            │
│  FOULING MATERIAL (pvc-dependent):                                        │
│  │  pvc_target = config.pvc_target  (e.g., 0.50)                          │
│  │  moisture = config.moisture_content  (e.g., 0.50)                      │
│  │                                                                        │
│  │  er_fouling = calculate_fouling_er(pvc_target, moisture)               │
│  │                                                                        │
│  │  [Mixing formula based on Peplinski model]                             │
│  │  er_fouling = f(pvc, moisture, er_soil, er_water)                      │
│  │  typical range: [4, 20] depending on PVC + moisture                    │
│  │                                                                        │
│  │  [Higher PVC/moisture → higher permittivity → slower EM wave]          │
│  │  [Higher permittivity → more attenuation → wider pulse]                │
│  │                                                                        │
│  │  Output: #material <er_fouling> <sigma> 1 0 bal_foul_granular         │
│  └────────────────────────────────────────────────────────────────┘      │
│                                                                            │
│  CLEAN BALLAST AGGREGATE:                                                 │
│  │  #material 5 0 1 0 bal_rock                                             │
│  │  └─ er=5 (typical for angular rock aggregate)                          │
│  │  └─ conductivity=0 (lossless)                                          │
│  │  └─ size_of_box=1 (required gprMax format)                             │
│  │  └─ material_id=0 (required)                                           │
│  └────────────────────────────────────────────────────────────────┘      │
│                                                                            │
│  OUTPUT: Material commands → added to scene._geometry_collection         │
│                                                                            │
└──────────────────────────────────────────────────────────────────────────┘
```

---

## Summary: Data Flow End-to-End

```
CONFIG                 GENERATION              SCENE STATE             OUTPUT
─────────────────────────────────────────────────────────────────────────────

GeneratorConfig
  ├─ domain_x, y, z
  ├─ layers (subgrade, formation, ballast)
  ├─ rock packing algorithm
  ├─ pvc_target, moisture
  └─ antenna config
        │
        ├─ LayerStack (frozen)
        │   └─ thickness values
        │
        ├─ CoordinateSystem (frozen)
        │   └─ Anchor → Y mapping
        │
        └─ ProductionLine.run()
               │
               ├─ Phase 1: Base Construction
               │    ├─ AirWorker        → free_space box
               │    ├─ SubgradeWorker   → soil layer
               │    ├─ FormationWorker  → subballast
               │    ├─ BallastWorker    → ballast bounds
               │    └─ GranularMatrixWorker
               │         ├─ Pack rocks (15s+ using ShangChu)
               │         ├─ Add ~100 rock triangles
               │         ├─ Add fouling box
               │         └─ Update metadata (PVC, FI)
               │
               ├─ Phase 2: Checkpoint
               │    └─ clone() for antenna variants
               │
               ├─ Phase 3: Finalization
               │    ├─ AntennaWorker → TX/RX waveform
               │    ├─ AssemblerWorker → validate
               │    └─ LabWorker → advanced metadata
               │
               └─ Phase 4: Validation
                    └─ validate_all() + statistics
                         │
                         └─ SceneCheckpoint (final)
                              │
                              └─ InFileWriter.write_in_file()
                                   │
                                   └─ "output.in" (text file)
                                        │
                                        gprMax simulation (GPU)
                                        │
                                        └─ "output.out" (HDF5 waveform)
```


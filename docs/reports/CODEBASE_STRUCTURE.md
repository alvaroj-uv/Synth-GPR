# Synth-GPR Codebase Structure (Post-Refactoring)

## Current Production Code (`src/`)

### Core Factory Pattern
- **dataset_generator.py** - Public API wrapper for dataset generation
- **production_line.py** - Orchestrates worker pipeline execution
- **workers.py** - All worker implementations (Air, Subgrade, Formation, Ballast, Rock, Fouling, Antenna, Assembler)
- **worker.py** - Base worker interface and SceneCheckpoint
- **recipes.py** - Predefined worker recipes (standard, custom)

### Resource Management
- **warehouse_keeper.py** - Facade for material/tool access
- **warehouses.py** - MaterialWarehouse and ToolWarehouse implementations
- **work_order.py** - WorkOrder and WorkOrderSystem (blackboard pattern)

### Configuration & Domain
- **config.py** - GeneratorConfig dataclass with all parameters
- **quality_log.py** - Quality issue tracking and logging

### Scene & Commands
- **scene_descriptor.py** - SceneDefinition data structure
- **gpr_commands.py** - gprMax command objects (Box, Cylinder, Material, etc.)
- **file_writer.py** - GPRMaxFileWriter for .in file generation

### Algorithms & Utilities
- **rock_packing.py** - Poisson disk sampling and rock packing algorithms
- **rock_model.py** - Rock shape and material property models
- **rock_packing.py** - Packing strategies and algorithms
- **physics.py** - Electromagnetic and material physics calculations
- **signal_processing.py** - GPR signal processing utilities
- **sampling.py** - Parameter sampling and randomization
- **scene_geometry.py** - Geometric calculations and transformations
- **visualization/** - Visualization utilities
- **domain/** - Domain-specific logic
- **patterns/** - Design pattern implementations
- **repositories/** - Data persistence and access patterns

### Additional Core Modules
- **constants.py** - Project-wide constants
- **data_loader.py** - Data loading utilities for HDF5 and CSV files
- **feature_extraction.py** - Feature extraction from GPR signals
- **granular_worker.py** - Granular material simulation worker
- **lab_worker.py** - Laboratory-scale simulation worker
- **degradation_worker.py** - Material degradation simulation

## Key Architecture Patterns

**Factory Pattern Implementation**:
```
DatasetGenerator → ProductionLine → Workers → WarehouseKeeper → Warehouses
                                   ↓
                            WorkOrderSystem (Blackboard)
```

**Benefits**:
- ✅ Single Responsibility: Each worker handles one aspect
- ✅ Dependency Injection: Workers receive keeper, not direct dependencies
- ✅ Centralized Config: All parameters in GeneratorConfig
- ✅ Dynamic Placement: Antenna height calculated at runtime
- ✅ Literature-Based Limits: Domain height capped at 1.65m
- ✅ Testability: Workers can be tested independently
- ✅ Extensibility: New workers can be added without modifying existing code

**Domain-Driven Design**:
- **Entities**: Rock, Material, Antenna, Scene
- **Value Objects**: PVC, Moisture, DielectricProperties
- **Services**: Physics calculations, signal processing
- **Repositories**: Data persistence patterns
- **Factories**: Work order and scene creation

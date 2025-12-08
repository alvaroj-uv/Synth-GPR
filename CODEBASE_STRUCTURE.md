# Synth-GPR Codebase Structure (Post-Refactoring)

## Active Production Code (`src/`)

### Core Factory Pattern
- **dataset_generator.py** - Public API wrapper for dataset generation
- **production_line.py** - Orchestrates worker pipeline execution
- **workers.py** - All 8 worker implementations (Air, Subgrade, Formation, Ballast, Rock, Fouling, Antenna, Assembler)
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
- **wang_tiles.py** - Wang tiling for efficient pattern generation
- **patterns/** - Pattern generation utilities

## Legacy Code (`legacy/`)

### Old Generation System
- **synthetic_data_generator.py** - Legacy BallastScenarioGenerator
- **scene_builder.py** - Old scene construction
- **geometry_composer.py** - Old layer-based composition
- **granular_layers.py** - Old granular ballast logic
- **scenario_factory.py** - Old factory (replaced by ProductionLine)
- **scene_validator.py** - Old validation (now in workers)
- **generate_dataset.py** - Old generation script
- **generate_augmented_dataset.py** - Old augmentation script

### Old Utilities
- **ballast_stats.py** - Statistical utilities
- **gprmax_input_generator.py** - Old input generator
- **scene_graph.py** - Old scene graph structure
- **data_loader.py** - Old data loading
- **feature_extraction.py** - Old feature extraction
- **signal_processing.py** - Old signal processing

## Key Architecture Changes

**Before (Legacy)**:
```
BallastScenarioGenerator → SceneBuilder → GeometryComposer → Layers
```

**After (Factory Pattern)**:
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

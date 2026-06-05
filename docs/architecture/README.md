# Scene Creation Architecture Documentation

This directory contains comprehensive documentation of the Synth-GPR scene generation architecture, which transforms configuration parameters into complete GPR simulation geometries (`.in` files).

## Quick Navigation

Choose your document based on your goal:

### 🎯 **Just Getting Started?**
→ [**SCENE_CREATION_QUICK_REFERENCE.md**](SCENE_CREATION_QUICK_REFERENCE.md)
- 30-second overview
- Component hierarchy diagrams
- Worker execution order
- Coordinate system anchor map
- Quick error fixes
- **Read first — sets context**

### 📋 **Need the Big Picture?**
→ [**SCENE_CREATION_ARCHITECTURE.md**](SCENE_CREATION_ARCHITECTURE.md)
- 11 detailed sections
- Design patterns (Composition, Factory, Worker)
- Worker choreography (Phases 1-4)
- GranularMatrixWorker deep dive (7 steps)
- 12 packing algorithms comparison
- Quality assurance & validation
- Extension points for custom code
- **Read second — comprehensive reference**

### 🔄 **Learning How Components Interact?**
→ [**SCENE_CREATION_SEQUENCES.md**](SCENE_CREATION_SEQUENCES.md)
- 8 detailed sequence diagrams
- ProductionLine execution flow
- GranularMatrixWorker step-by-step
- Coordinate system resolution
- SceneCheckpoint composition
- File writing flow
- Error handling & validation
- Cloning for variants
- **Use as visual reference — see data flow**

---

## Document Details

### SCENE_CREATION_QUICK_REFERENCE.md
**Size:** ~15 KB | **Read time:** 10 min | **Diagrams:** 8

**Contains:**
- 30-second overview
- Component hierarchy
- Worker execution order
- Coordinate system map
- Layer stack values (defaults)
- Worker implementation template
- GranularMatrixWorker algorithm steps
- Packing algorithm selection guide
- Validation checklist
- Delegation methods
- Common errors & fixes
- Extension examples
- Invariants to maintain
- Testing template
- File I/O flow
- Performance notes
- Further reading links

**Best for:**
- Quick lookups
- Finding specific information
- Working examples
- Common errors

---

### SCENE_CREATION_ARCHITECTURE.md
**Size:** ~35 KB | **Read time:** 40 min | **Depth:** Expert

**Contains:**

**Section 1: Architecture Layers**
- Layered component diagram
- Overall data flow (Config → Workers → Output)

**Section 2: Coordinate System Foundation**
- LayerStack (frozen, immutable)
- Anchor enum (BOTTOM, SUBGRADE_TOP, ..., DOMAIN_TOP)
- CoordinateSystem service (resolver pattern)
- Type-safe layer bounds

**Section 3: Scene State: SceneCheckpoint**
- Composition pattern (4 focused components)
- GeometryCollection (materials + geometry)
- AntennaConfiguration (TX/RX)
- RockCollection (rock tracking)
- DomainSettings (gprMax config, immutable)

**Section 4: Production Line: Orchestrator**
- 4-phase execution model
- Phase 1: Base Construction (5 workers)
- Phase 2: Checkpoint (cloning)
- Phase 3: Finalization (3 workers)
- Phase 4: Validation (statistics, error checks)

**Section 5: Worker Pattern**
- Worker interface (execute + quality_check)
- RecipeBook choreography
- Sequential execution order
- Worker chain dependencies

**Section 6: Algorithmic Components**
- GranularMatrixWorker (7 steps)
- Packing algorithms (12 variants)
- Material properties (Peplinski parameters)

**Section 7: Data Flow (Config → .in File)**
- GeneratorConfig input
- ProcessingPipeline
- .in file format output

**Section 8: Quality Assurance**
- Worker quality checks
- Scene validation
- Production line error handling

**Section 9: Extension Points**
- Adding custom workers
- Replacing packing algorithms
- Variant generation

**Section 10: Design Rationale**
- Why Composition over Inheritance
- Why immutable LayerStack
- Why Worker + RecipeBook pattern

**Section 11: Key Invariants**
- Domain must fit layer stack
- Rocks within ballast bounds
- Antenna above ballast
- Material names unique
- Valid material references
- PVC in [0, 1]

**Best for:**
- Understanding design decisions
- Implementing new workers
- Debugging complex issues
- Comprehensive reference

---

### SCENE_CREATION_SEQUENCES.md
**Size:** ~25 KB | **Read time:** 30 min | **Diagrams:** 8 detailed

**Contains 8 Sequence Diagrams:**

**Diagram 1: Main Production Line Execution**
- Full 7-step flow (Init → Phase 1-4 → Return)
- Per-phase detail with code snippets

**Diagram 2: Worker Execution Detail (GranularMatrixWorker)**
- 8 steps in detail
- Input/output per step
- Time estimates

**Diagram 3: Coordinate System Resolution**
- LayerStack initialization
- Anchor computation
- Usage in workers
- Type-safe layer bounds

**Diagram 4: SceneCheckpoint Composition**
- Component hierarchy
- 4 composed components
- Delegation pattern
- Benefits

**Diagram 5: File Writing Flow**
- SceneCheckpoint → SceneDefinition → .in file
- 9 write steps
- Painter's algorithm in action

**Diagram 6: Error Handling & Validation**
- Worker execution QC flow
- Component validation
- Critical error detection
- Logging system

**Diagram 7: Cloning for Variants**
- Phase 2 checkpoint creation
- Geometry sharing
- Antenna reset
- Use cases

**Diagram 8: Material Property Resolution**
- Peplinski parameters
- Heterogeneous sublayers
- Fouling material synthesis
- Output material commands

**Best for:**
- Visual learners
- Understanding component interactions
- Tracing data flow
- Debugging execution order

---

## Key Concepts Across All Documents

### LayerStack (Immutable Foundation)
All geometry coordinates are derived from LayerStack:
```python
LayerStack(
    subgrade_thickness=0.20,
    formation_thickness=0.10,
    ballast_thickness=0.25,
    antenna_clearance=0.5,
    air_buffer=0.1
)
# Total height: 1.15 m
```
**Why:** Single source of truth. Change once, all workers adapt.

### CoordinateSystem (Resolver)
Translates semantic anchors to Y coordinates:
```python
y = coords.get_y(Anchor.BALLAST_TOP)  # Returns 0.55 m
bounds = coords.bounds(Layer.BALLAST)  # Returns LayerBounds(0.30, 0.55)
```
**Why:** Type-safe, avoids magic numbers.

### SceneCheckpoint (Mutable Container)
Holds scene state, composed of 4 focused components:
```python
scene._geometry_collection  # Materials + Geometry
scene._antenna_config       # TX/RX
scene._rock_collection      # Rock positions
scene.domain_settings       # gprMax config (immutable)
```
**Why:** Single responsibility per component, easy to test.

### Worker Pattern (Choreography)
Sequential workers, each modifies scene state:
```python
for worker in [Air, Subgrade, Formation, Ballast, GranularMatrix, ...]:
    worker.execute(scene)
    errors = worker.quality_check(scene)
    # If errors → log and potentially abort
```
**Why:** Decoupled, testable, extensible.

### GranularMatrixWorker (Most Complex)
7-step rock packing and fouling addition:
1. Get ballast bounds from CoordinateSystem
2. Run packing algorithm (12 variants available)
3. Classify circles (rocks vs. fines)
4. Gravity settle rocks
5. Add rock geometry (triangles)
6. Add fouling box (exact PVC)
7. Calculate metadata (PVC, FI, density)

**Time:** 1–20 seconds depending on packing algorithm

---

## Common Reading Paths

### Path 1: "I'm new to the codebase"
1. Read **QUICK_REFERENCE.md** (15 min)
2. Skim **ARCHITECTURE.md** sections 1-3 (10 min)
3. Look at **SEQUENCES.md** diagrams 1, 3, 4 (10 min)
4. Explore source: `src/production_line.py`, `src/workers.py`

**Time:** ~45 min

### Path 2: "I need to add a custom worker"
1. Read **QUICK_REFERENCE.md** sections "Worker Template", "Extending" (5 min)
2. Read **ARCHITECTURE.md** sections 4-5 (20 min)
3. Check **SEQUENCES.md** diagram 6 for error handling (10 min)
4. Copy template from **QUICK_REFERENCE.md**
5. Implement and test

**Time:** ~45 min + coding

### Path 3: "I'm debugging a complex issue"
1. Check **QUICK_REFERENCE.md** "Common Errors & Fixes" (5 min)
2. Trace flow in **SEQUENCES.md** diagram matching your issue (15 min)
3. Reference **ARCHITECTURE.md** section matching your issue (20 min)
4. Read source code with architecture context

**Time:** ~40 min

### Path 4: "I want to understand design decisions"
1. Read **ARCHITECTURE.md** sections 9-11 (20 min)
2. Examine source: `src/scene_geometry.py`, `src/worker.py` (15 min)
3. Compare old vs. new in git history if available

**Time:** ~35 min

---

## Using These Docs in Code Comments

When writing code, reference these docs:

```python
# See SCENE_CREATION_ARCHITECTURE.md Section 5: Worker Pattern
class MyWorker(Worker):
    name = "MyWorker"
    
    def execute(self, scene, params, materials, tools):
        # Reference QUICK_REFERENCE.md: Worker Implementation Template
        bounds = scene.coordinate_system.bounds(Layer.BALLAST)
        # See SCENE_CREATION_SEQUENCES.md Diagram 3: Coordinate Resolution
```

---

## File Cross-References

All three documents cross-reference each other:

- **QUICK_REFERENCE.md** → "Further Reading" links to ARCHITECTURE.md
- **ARCHITECTURE.md** → "Summary" section directs to SEQUENCES.md for visual understanding
- **SEQUENCES.md** → "Further Reading" references sections of ARCHITECTURE.md

---

## Related Documentation

Also see:

- **[GENERATION_PROCESS.md](GENERATION_PROCESS.md)** — Overview of generation phases
- **[coordinates.py](../../src/domain/coordinates.py)** — Source code for LayerStack, CoordinateSystem, Anchor
- **[worker.py](../../src/worker.py)** — Source code for SceneCheckpoint, Worker base class
- **[production_line.py](../../src/production_line.py)** — Source code for ProductionLine orchestrator
- **[workers.py](../../src/workers.py)** — Source code for concrete worker implementations
- **[granular_worker.py](../../src/granular_worker.py)** — Source code for GranularMatrixWorker

---

## Version Info

**Documentation Version:** 1.0 (June 2024)
**Architecture Revision:** Phase 1 Complete (Composition refactor)
**Tested on:** Python 3.8–3.12

---

## Quick Links

| Need | Go To |
|------|-------|
| Anchor values | QUICK_REF: Coordinate System Anchor Map |
| Layer stack defaults | QUICK_REF: LayerStack Values |
| Worker template | QUICK_REF: Worker Implementation Template |
| Packing algorithms | QUICK_REF: Packing Algorithm Selection |
| Common errors | QUICK_REF: Common Errors & Fixes |
| Design patterns | ARCH: Section 9 Design Rationale |
| Extension points | ARCH: Section 9 Extension Points |
| Full flow diagrams | SEQUENCES: All 8 diagrams |
| Execution order | SEQUENCES: Diagram 1 |
| Material synthesis | SEQUENCES: Diagram 8 |
| Error handling | SEQUENCES: Diagram 6 |

---

## Feedback

These documents are maintained alongside the codebase. If you find:
- **Gaps:** Missing important information
- **Errors:** Incorrect details
- **Confusion:** Unclear explanations

Please:
1. Open an issue with the problem
2. Suggest the specific document and section
3. Include the corrected/clarified text if possible

---

## Summary

| Document | Length | Time | Best For |
|----------|--------|------|----------|
| QUICK_REFERENCE.md | 15 KB | 10 min | Quick lookups, getting oriented |
| ARCHITECTURE.md | 35 KB | 40 min | Deep understanding, design details |
| SEQUENCES.md | 25 KB | 30 min | Visual learners, data flow tracing |

**Start here:** QUICK_REFERENCE.md (10 min)  
**Then read:** ARCHITECTURE.md (40 min)  
**Refer to:** SEQUENCES.md (as needed)  
**Total:** ~60 min for expert-level understanding


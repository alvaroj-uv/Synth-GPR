╔════════════════════════════════════════════════════════════════════════════════╗
║                  COUPLING ANALYSIS: Absolute Coordinate System                ║
╚════════════════════════════════════════════════════════════════════════════════╝

TIGHT COUPLING: Current State
═══════════════════════════════════════════════════════════════════════════════════

All workers depend on agreed-upon absolute coordinates:

    BallastWorker
    ├─ Calculates: ballast_bottom = 0.3m
    ├─ Calculates: ballast_top = 0.55m
    └─ Decision affects:
       ├─ SubgradeWorker (must stop at 0.3m)
       ├─ FormationWorker (must stop at 0.3m)
       ├─ GranularMatrixWorker (must pack at [0.3, 0.55])
       ├─ StripPackingStrategy (must pack at [0.3, 0.55])
       └─ LabWorker (must sample at [0.3, 0.55])

    Change cascade:
    
    IF ballast_bottom changes from 0.3 → 0.4:
    ├─ SubgradeWorker: update hardcoded 0.3 → 0.4
    ├─ FormationWorker: update hardcoded boundary
    ├─ GranularMatrixWorker: update expected bounds
    ├─ StripPackingStrategy: update strip origin
    ├─ LabWorker: update sampling region
    └─ ALL THESE CHANGES MUST BE COORDINATED!


DEPENDENCY GRAPH
═══════════════════════════════════════════════════════════════════════════════════

                          BallastWorker
                           (0.3, 0.55)
                                 │
                    ┌────────────┼────────────┐
                    │            │            │
                    ↓            ↓            ↓
            Subgrade     Formation      GranularMatrix
            (0, 0.2)     (0.2, 0.3)      (0.3, 0.55)
                                              │
                                    ┌─────────┼─────────┐
                                    │         │         │
                                    ↓         ↓         ↓
                            Hybrid    Strip      RSA
                            Packing   Packing    Packing
                                    │         │         │
                                    └─────────┼─────────┘
                                              │
                                              ↓
                                         LabWorker
                                      (samples 0.3-0.55)

Legend: → = depends on upstream
        (x, y) = absolute coordinate range used


WHAT HAPPENS WITH BUGS
═══════════════════════════════════════════════════════════════════════════════════

Good Bug: GranularMatrixWorker respects bounds
──────────────────────────────────────────────

    BallastWorker: ballast_bottom = 0.3
         │
         ↓
    GranularMatrixWorker:
    ├─ Receives: bounds.y_min = 0.3
    ├─ Respects: packs rocks at y ∈ [0.3, 0.55] ✓
    └─ Result: Rocks in expected range
         │
         ↓
    LabWorker:
    ├─ Searches: y ∈ [0.3, 0.55]
    ├─ Finds: ALL rocks ✓
    └─ Calculates: PVC correctly ✓


Bad Bug: StripPackingStrategy ignores bounds (BEFORE FIX)
────────────────────────────────────────────────────────

    BallastWorker: ballast_bottom = 0.3
         │
         ↓
    GranularMatrixWorker:
    ├─ Receives: bounds.y_min = 0.3, bounds.y_max = 0.55
    ├─ Calls: StripPackingStrategy(bounds)
    └─ StripPackingStrategy IGNORES bounds!
         │
         ├─ Does: strip_bounds.y_min = 0.0, y_max = 3.2 ✗
         ├─ Result: Packs rocks at y ∈ [0, 3.2] ✗
         └─ Returns: Rocks at wrong y position ✗
         │
         ↓
    LabWorker:
    ├─ Searches: y ∈ [0.3, 0.55]
    ├─ Finds: ~10 rocks (rest are at y > 0.55) ✗
    └─ Calculates: PVC from incomplete data → WRONG! ✗


Lesson: In tightly coupled system, ANY worker that breaks contract breaks entire flow


LOOSE COUPLING: With Relative Coordinates
═══════════════════════════════════════════════════════════════════════════════════

Each layer encapsulates its own coordinate space:

    BallastLayer (abstraction)
    ├─ local_origin = 0.3m (world space)
    ├─ local_height = 0.25m
    └─ Provides interface:
       ├─ local_bounds() → [0, 0.25] (local space)
       ├─ world_bounds(domain_x) → [0, domain_x, 0.3, 0.55]
       ├─ to_world(y_local) → y_world
       └─ to_local(y_world) → y_local

    GranularMatrixWorker:
    ├─ Gets: ballast_layer
    ├─ Calls: bounds = ballast_layer.local_bounds()
    │         (doesn't need to know 0.3m!)
    ├─ Packs: rocks in local space [0, 0.25]
    └─ Converts: rocks to world space before storing

    Benefit: If ballast origin changes from 0.3 → 0.4:
    ├─ Only change: BallastLayer.local_origin = 0.4
    ├─ No changes needed in: GranularMatrixWorker, LabWorker
    ├─ Loose coupling preserved!
    └─ Refactoring risk: LOW


COMPARISON: Coupling Strength
═══════════════════════════════════════════════════════════════════════════════════

Tight Coupling (Current Absolute):
    Change one coordinate boundary
         │
         ├─ Affects: ALL workers
         ├─ Requires: Multiple file edits
         ├─ Risk: Easy to miss one
         └─ Safety: Low

Loose Coupling (Relative):
    Change one coordinate boundary
         │
         ├─ Affects: Only layer definition
         ├─ Requires: One file edit
         ├─ Risk: Minimal
         └─ Safety: High


WHY THIS PROJECT USES TIGHT COUPLING
═══════════════════════════════════════════════════════════════════════════════════

Tradeoffs chosen:
    
    ✓ Tight Coupling Benefits:
    ├─ Simple: No abstraction layer needed
    ├─ Fast: No coordinate transformations
    ├─ Debuggable: Values match what you see
    └─ Sufficient: Layer definitions are stable

    ✗ Tight Coupling Costs:
    ├─ Refactoring risk: Hard to change layer positions
    ├─ Brittleness: Missing one update breaks everything
    └─ Scalability: More layers = more coupling

    When does loose coupling become necessary?
    ├─ Multiple domain heights (different ballast depths)
    ├─ Layered materials (sand + gravel + ballast)
    ├─ Nested extraction (windows within windows)
    └─ Dynamic layer reconfiguration


THE FIX & ITS COUPLING IMPLICATIONS
═══════════════════════════════════════════════════════════════════════════════════

Before fix:
    StripPackingStrategy had:
    ├─ Broken contract: ignored bounds parameter
    ├─ Independent coordinate system: [0, 3.2]
    ├─ Tight coupling violated
    └─ Result: System mismatch!

After fix:
    StripPackingStrategy now:
    ├─ Respects contract: uses bounds.y_min/y_max
    ├─ Same coordinate system: [0.3, 0.55]
    ├─ Tight coupling maintained
    └─ Result: System aligned! ✓

How to prevent similar bugs:
    1. Validate contracts at boundaries
    2. Add assertions checking bounds are used
    3. Test at layer interfaces
    4. Document expected contracts

═══════════════════════════════════════════════════════════════════════════════════

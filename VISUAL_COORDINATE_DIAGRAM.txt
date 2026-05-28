╔════════════════════════════════════════════════════════════════════════════════╗
║                    COORDINATE SYSTEM BUG: Visual Comparison                   ║
╚════════════════════════════════════════════════════════════════════════════════╝

BEFORE FIX (BROKEN)
═══════════════════════════════════════════════════════════════════════════════════

Domain View - Y-axis (height):

    3.2m ┌─────────────────────────┐
         │   (rocks positioned here!)
         │   y ∈ [0, 3.2]
         │
         │  ● ●  ●  ●
         │ ●   ●    ●
    1.6m │●      ●
         │  ●●  ●
         │  ●
    0.8m │  ●   ●
         │     ●
         │                      ← Problem: LabWorker searches here!
    0.55m├─────────────────────────
         │ [ballast layer]
    0.3m ├─────────────────────────
         │
    0.0m └─────────────────────────
         ↑ X

    Issue: Rocks are spread across entire 3.2m, but LabWorker only looks in [0.3, 0.55]!
           Result: PVC calculation uses only ~5% of rocks → PVC measured wrong!


AFTER FIX (CORRECT)
═══════════════════════════════════════════════════════════════════════════════════

Domain View - Y-axis (height):

    3.2m ┌─────────────────────────┐
         │ (empty - antenna region)
         │
         │
         │
    1.6m │
         │
         │
    0.8m │
         │
         │                      ← LabWorker searches here [0.3, 0.55]
    0.55m├─────────────────────────
         │  ●  ●   ●  ●          ← ALL rocks positioned here!
         │●    ●     ●           ← y ∈ [0.3, 0.55]
         │   ●   ●  ●  ●
         │
    0.3m ├─────────────────────────
         │
    0.0m └─────────────────────────
         ↑ X

    Result: All rocks in [0.3, 0.55], LabWorker finds all of them → PVC correct!


THE CODE CHANGE
═══════════════════════════════════════════════════════════════════════════════════

BEFORE:
─────────────────────────────────────────────────────────────────────────────────
    def _pack_strip(self, bounds: PackingBounds, ...):
        strip_bounds = PackingBounds(
            x_min=0.0,
            x_max=self.strip_width,
            y_min=0.0,              # ← IGNORED bounds!
            y_max=self.strip_height # ← HARDCODED VALUE
        )
        # Pack rocks at [0, 3.2] instead of ballast layer!


AFTER:
─────────────────────────────────────────────────────────────────────────────────
    def _pack_strip(self, bounds: PackingBounds, ...):
        strip_bounds = PackingBounds(
            x_min=0.0,
            x_max=self.strip_width,
            y_min=bounds.y_min,     # ← NOW RESPECTS bounds!
            y_max=bounds.y_max      # ← USE INPUT PARAMETER
        )
        # Pack rocks at [0.3, 0.55] = ballast layer ✓


PVC CALCULATION IMPACT
═══════════════════════════════════════════════════════════════════════════════════

BEFORE FIX:

    Individual domain:        Strip extraction:
    ────────────────          ─────────────────
    Rocks: 266                Rocks: 279
    In [0.3, 0.55]: 266/266   In [0.3, 0.55]: ???
    
    LabWorker samples [0.3, 0.55]:
    Individual: All 266 rocks found       → PVC = 30% ✓
    Strip:      ~10-50 rocks found       → PVC = 47% or 3.7% ✗
    
    Why? Most strip rocks are at y > 0.55, outside the search region!
         LabWorker calculates PVC from whatever few rocks it finds.


AFTER FIX:

    Individual domain:        Strip extraction:
    ────────────────          ─────────────────
    Rocks: 266                Rocks: 279
    In [0.3, 0.55]: 266/266   In [0.3, 0.55]: 279/279 ✓
    
    LabWorker samples [0.3, 0.55]:
    Individual: All 266 rocks found       → PVC = 30% ✓
    Strip:      All 279 rocks found       → PVC = 30% ✓
    
    Why? Now all strip rocks are at y ∈ [0.3, 0.55]!
         LabWorker calculates PVC from ALL rocks in both cases.


KEY PRINCIPLE
═══════════════════════════════════════════════════════════════════════════════════

    ┌─────────────────────────────────────────────────────────────────┐
    │ ABSOLUTE COORDINATES THROUGHOUT PIPELINE                         │
    │                                                                  │
    │ All rocks are in WORLD SPACE (absolute y-coordinates).          │
    │ Y-coordinates NEVER change between workers.                     │
    │ If bounds specifies y ∈ [0.3, 0.55], pack at [0.3, 0.55].     │
    │                                                                  │
    │ ✗ WRONG: Pack at origin, then translate (-0.3)                 │
    │ ✓ RIGHT: Pack directly at target coordinates                   │
    └─────────────────────────────────────────────────────────────────┘


DEBUGGING CHECKLIST
═══════════════════════════════════════════════════════════════════════════════════

If rocks are in wrong y-coordinate after packing:

    □ Check bounds parameter:     Are bounds.y_min/y_max set correctly?
    □ Check packing strategy:     Does it RESPECT bounds or IGNORE them?
    □ Check extraction:           Is y being translated (WRONG)?
    □ Check downstream workers:   Are they sampling correct y-range?
    □ Check PVC results:          Are they matching expected value?

If any of these fail, trace coordinates through each worker with debug output.

═══════════════════════════════════════════════════════════════════════════════════

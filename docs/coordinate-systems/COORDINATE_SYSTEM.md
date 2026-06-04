# Coordinate System Architecture

## Overview

The rock packing and scene generation pipeline uses **absolute coordinates** throughout. Understanding how coordinates flow through workers is critical for debugging issues like the strip packing bug.

## Domain Structure (Absolute Coordinates)

All coordinates are in **world space** measured from domain origin (0, 0, 0).

```
Z-axis (into gprMax grid)
│
├─ Material Layers (Y-axis from bottom to top):
│  ├─ Air (antenna region)        [Y: antenna_height to domain_y]
│  ├─ Ballast layer (rocks)       [Y: ballast_bottom to ballast_top]
│  ├─ Formation layer             [Y: formation_bottom to formation_top]
│  └─ Subgrade layer              [Y: 0 to subgrade_height]
│
└─ X-axis (horizontal span)
   [X: 0 to domain_x]
```

### Layer Configuration (Defaults)

| Layer | Y_min | Y_max | Height | Purpose |
|-------|-------|-------|--------|---------|
| Subgrade | 0.0m | 0.2m | 0.2m | Foundation |
| Formation | 0.2m | 0.3m | 0.1m | Transition |
| Ballast | 0.3m | 0.55m | 0.25m | Rock container |
| Air | 0.55m+ | 3.2m | 2.65m | Antenna region |

**Key**: Ballast layer is where rocks are packed and PVC calculated.

## Worker Pipeline & Coordinate Handling

### Phase 1: Base Construction (Sequential)

```
┌─────────────────────────────────────────────┐
│ 1. AirWorker                                │
│    Output: Air box [0, domain_x] × [y_top, domain_y]
│    Coordinates: Absolute (y_top = antenna_clearance + ballast_top)
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│ 2. SubgradeWorker                           │
│    Output: Subgrade box [0, domain_x] × [0, 0.2]
│    Coordinates: Absolute (0.0, 0.2)
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│ 3. FormationWorker                          │
│    Output: Formation box [0, domain_x] × [0.2, 0.3]
│    Coordinates: Absolute (0.2, 0.3)
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│ 4. BallastWorker                            │
│    ├─ Input: None (calculates from config)
│    ├─ Calculation:
│    │  ballast_bottom = 0.3 (top of formation)
│    │  ballast_thickness = max_ballast_height
│    │  ballast_top = ballast_bottom + ballast_thickness
│    ├─ Output: Ballast box [0, domain_x] × [0.3, 0.55]
│    └─ Stores in work_order: ballast_bottom_y, ballast_thickness
│        Coordinates: Absolute (0.3, 0.55)
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│ 5. GranularMatrixWorker (Rock Packing)      │
│    ├─ Input: ballast_bottom_y, ballast_thickness from work_order
│    ├─ Creates packing bounds:
│    │  bounds = [0, domain_x] × [ballast_bottom, ballast_top]
│    │  Example: [0, 2.248] × [0.3, 0.55]
│    ├─ Calls packer.generate_rocks(bounds, ...)
│    ├─ Output: Rocks with ABSOLUTE y-coordinates
│    │  Rock 1: x=1.2, y=0.42, r=0.015
│    │  Rock 2: x=0.8, y=0.48, r=0.018
│    │  (All y-values in [ballast_bottom, ballast_top])
│    ├─ Places fouling box [0, domain_x] × [ballast_bottom, fouling_top]
│    └─ Adds rocks to scene.rock_positions (with absolute y)
│        Coordinates: Absolute (y in [0.3, 0.55])
└─────────────────────────────────────────────┘
```

### Phase 2: Finalization (After Checkpoint)

```
┌─────────────────────────────────────────────┐
│ 6. AntennaWorker                            │
│    ├─ Input: ballast_top from metadata
│    ├─ Positions antennas above ballast:
│    │  tx_y = ballast_top + antenna_clearance
│    │  rx_y = tx_y
│    └─ Output: Source/Receiver commands
│        Coordinates: Absolute (y above ballast_top)
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│ 7. AssemblerWorker                          │
│    └─ No coordinate changes, just validation
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│ 8. LabWorker (Material Analysis)            │
│    ├─ Input: scene.rock_positions (absolute y)
│    ├─ Reads: ballast_bottom_y, ballast_thickness
│    ├─ Samples region: [ballast_bottom, ballast_top]
│    ├─ Algorithm:
│    │  for each rock in scene.rock_positions:
│    │    if rock.y in [ballast_bottom, ballast_top]:
│    │      include in PVC calculation
│    └─ Output: PVC, FI, class
│        Uses: Absolute y-coordinates from rocks
└─────────────────────────────────────────────┘
```

## Strip Packing Coordinate Flow (FIXED)

### Before Fix (BROKEN)

```
GranularMatrixWorker:
  bounds = [0, 2.248] × [0.3, 0.55]  ← ballast layer
  ↓
StripPackingStrategy.generate_rocks(bounds):
  ❌ IGNORED bounds.y_min/y_max
  strip_bounds = [0, 5.0] × [0, 3.2]  ← WRONG: hardcoded!
  ↓
  Rocks packed in [0, 3.2]
  ↓
_extract_window():
  rel_y = rock.y - bounds.y_min
  ❌ rock.y in [0, 3.2], minus 0.3 = [−0.3, 2.9]
  ↓
  ❌ Rocks in wrong y-range, LabWorker can't find them!
```

### After Fix (CORRECT)

```
GranularMatrixWorker:
  bounds = [0, 2.248] × [0.3, 0.55]  ← ballast layer
  ↓
StripPackingStrategy.generate_rocks(bounds):
  ✓ RESPECTS bounds.y_min/y_max
  strip_bounds = [0, 5.0] × [0.3, 0.55]  ← Uses ballast layer!
  ↓
  Rocks packed in [0.3, 0.55]
  ↓
_extract_window():
  rel_x = rock.x - bounds.x_min        (adjust x to window)
  keep absolute y = rock.y             (don't adjust y)
  ✓ rock.y in [0.3, 0.55], unchanged
  ↓
  ✓ Rocks in correct y-range, LabWorker finds them!
```

## Key Principles

### 1. **Absolute Coordinates Throughout**
- All rock positions are in world space
- NO relative/local coordinates (except for visualization)
- Y-coordinates are NEVER translated between workers

### 2. **Bounds Parameter is Sacred**
- When a packing strategy receives `bounds`, it MUST respect:
  - `bounds.x_min` to `bounds.x_max` → packing region width
  - `bounds.y_min` to `bounds.y_max` → packing region depth
- Do NOT ignore or override bounds with hardcoded values

### 3. **Ballast Layer is Invariant**
- Ballast layer bounds never change once set by BallastWorker
- All rocks must fit within ballast layer
- LabWorker samples only within ballast layer

### 4. **X and Y are Independent**
- X-coordinates can be adjusted (e.g., for extraction windows)
- Y-coordinates must be preserved (linked to ballast layer)

## Debugging Checklist

When coordinates go wrong, check:

```
□ Are rocks outside ballast layer bounds [ballast_bottom, ballast_top]?
  → Rock y-values are wrong
  → Check packing strategy's bounds handling

□ Are rocks at y=0 when they should be at y=0.3?
  → Bounds.y_min was ignored or stripped
  → Check for `rock.y - bounds.y_min` bugs

□ Does LabWorker report 0% PVC despite rocks being packed?
  → Rocks are outside the sampling region [ballast_bottom, ballast_top]
  → Check coordinate translation in extraction

□ Do different extraction windows have different PVC?
  → Rock distribution is correct but sampling window is wrong
  → Check bounds.y_min/y_max consistency

□ Does adding logging show rocks at different y before/after a worker?
  → A worker is translating coordinates (BUG!)
  → Rocks should have same y-coordinates through entire pipeline
```

## Examples

### Individual Domain Packing

```
Input bounds:  [0, 2.248] × [0.3, 0.55]
Packing:       HybridShang in [0, 2.248] × [0.3, 0.55]
Output rocks:  ~428 rocks
  Rock 1: x=0.234, y=0.315, r=0.012
  Rock 2: x=1.890, y=0.501, r=0.018
  ...
  Rock N: x=2.100, y=0.542, r=0.015

LabWorker samples [0.3, 0.55]:
  ✓ All rocks included
  ✓ PVC = 30% (correct)
```

### Strip Packing (Fixed)

```
Input bounds (first extraction):  [0, 2.248] × [0.3, 0.55]
Strip packing:
  Pack strip in [0, 5.0] × [0.3, 0.55]  ← ballast layer
  Extract window [0, 2.248]
Output rocks:  ~420 rocks (same distribution as individual)
  Rock 1: x=0.234, y=0.315, r=0.012
  Rock 2: x=1.890, y=0.501, r=0.018
  ...
  Rock N: x=2.100, y=0.542, r=0.015

Input bounds (second extraction):  [2.248, 4.496] × [0.3, 0.55]
Output rocks:  ~420 rocks
  Rock 1: x=0.234, y=0.315, r=0.012  ← adjusted x
  Rock 2: x=1.890, y=0.501, r=0.018  ← adjusted x
  ...
  Rock N: x=2.100, y=0.542, r=0.015  ← adjusted x
  (y-values UNCHANGED)

LabWorker samples [0.3, 0.55] for BOTH extractions:
  ✓ All rocks included
  ✓ PVC = 30% (correct, matches individual)
```

## Visual Diagram

```
Domain View (Front):
  
  3.2m │                    ← antenna_height (air)
       │  📡 TX    📡 RX    ← antenna region
       │
  0.55m├─────────────────  ← ballast_top (BallastWorker)
       │  ● ● ●            ← rocks (GranularMatrixWorker)
       │  ●   ● ●          ← rocks (y in [0.3, 0.55])
       │  ●●●● ● ●
  0.3m ├─────────────────  ← ballast_bottom (top of formation)
       │
  0.2m ├─────────────────  ← formation_top (FormationWorker)
       │ [formation]
  0.0m ├─────────────────  ← origin
       │ [subgrade]
         ↑                  ↑
         0                domain_x (2.248m)
```

## Related Issues & Fixes

- **Strip packing bug** (2026-05-28): Hardcoded [0, strip_height] instead of respecting bounds
  - Fix: Use bounds.y_min/y_max for packing
  - Impact: PVC calculations now match individual vs extracted packing

- **Ballast layer not adjusting to rocks**: LabWorker caps ballast_top to min(configured, physical_top)
  - Status: Working as intended (prevents sampling air above rocks)
  - May need review if rocks settle higher than expected

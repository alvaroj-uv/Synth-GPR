# Multi-Layer Painting System Architecture

## Overview

The gprMax input file generator is fundamentally a **multi-layer painting system**. Like a painter building up a canvas with successive coats of paint, we construct the railway ballast geometry by painting layers sequentially from bottom to top, where **later layers override earlier layers** in overlapping regions.

This is elegant because:
- ✅ **Simple**: Paint bottom-to-top, last layer wins
- ✅ **Intuitive**: Matches real-world layer deposition (gravity)
- ✅ **Composable**: Each layer can be added/removed independently
- ✅ **Efficient**: No need for complex CSG (Constructive Solid Geometry)

---

## The Painter's Algorithm

### Core Principle

```
"When two objects occupy the same space, the one painted later is visible"
```

### In gprMax Terms

```
#box 0 0 0 2.248 3.199 0.0132 free_space      ← Layer 1: Paint everything white
#box 0 0 0 2.248 0.2 0.0132 subgrade          ← Layer 2: Paint brown over bottom 0.2m
#box 0 0.2 0 2.248 0.3 0.0132 formation       ← Layer 3: Paint gray over next 0.1m
#box 0 0.3 0 2.248 0.55 0.0132 bal_rock       ← Layer 4: Paint tan over next 0.25m
#triangle ... rock_1 ...                       ← Layer 5: Paint individual rocks
#triangle ... rock_2 ...                       ← Layer 6: Paint more rocks
#box 0 0.3 0 2.248 0.4 0.0132 bal_foul_granular ← Layer 7: Paint fouling OVER rocks
```

### Visual Representation

```
FINAL RESULT (Side View):

y = 0.55 m ┌──────────────────────────────────────┐
           │  AIR (from Layer 1)                   │
           ├──────────────────────────────────────┤
y = 0.40 m │ FOULING (from Layer 7, covers rocks) │
           │         ◯  ◯  ◯  (rocks visible)    │
           ├──────────────────────────────────────┤
y = 0.30 m │  BALLAST / ROCKS (from Layers 4-6)   │
           │         ◯  ◯  ◯  ◯  ◯               │
           ├──────────────────────────────────────┤
y = 0.20 m │  FORMATION (from Layer 3)             │
           ├──────────────────────────────────────┤
y = 0.0 m  │  SUBGRADE (from Layer 2)              │
           │  FOUNDATION                          │
           └──────────────────────────────────────┘

THE PAINTING PROCESS:

Step 1: Paint entire domain white (air)
        ┌────────────────────┐
        │░░░░░░░░░░░░░░░░░░░░│  white
        └────────────────────┘

Step 2: Paint bottom 20cm brown (subgrade)
        ┌────────────────────┐
        │░░░░░░░░░░░░░░░░░░░░│  white
        │░░░░░░░░░░░░░░░░░░░░│  white
        │░░░░░░░░░░░░░░░░░░░░│  white
        ├════════════════════┤
        │████████████████████│  brown
        └────────────────────┘

Step 3: Paint next 10cm gray (formation)
        ┌────────────────────┐
        │░░░░░░░░░░░░░░░░░░░░│  white
        │░░░░░░░░░░░░░░░░░░░░│  white
        │░░░░░░░░░░░░░░░░░░░░│  white
        ├════════════════════┤
        │▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓│  gray
        ├════════════════════┤
        │████████████████████│  brown
        └────────────────────┘

Step 4: Paint next 25cm tan (ballast)
        ┌────────────────────┐
        │░░░░░░░░░░░░░░░░░░░░│  white
        ├════════════════════┤
        │▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒│  tan
        ├════════════════════┤
        │▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓│  gray
        ├════════════════════┤
        │████████████████████│  brown
        └────────────────────┘

Step 5-6: Paint individual rocks on top of tan ballast
        ┌────────────────────┐
        │░░░░░░░░░░░░░░░░░░░░│  white
        ├════════════════════┤
        │▒▒◯▒◯▒▒▒▒◯▒▒▒▒▒▒▒▒▒▒│  tan + rocks
        ├════════════════════┤
        │▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓│  gray
        ├════════════════════┤
        │████████████████████│  brown
        └────────────────────┘

Step 7: Paint fouling OVER rocks (covers them partially)
        ┌────────────────────┐
        │░░░░░░░░░░░░░░░░░░░░│  white
        ├════════════════════┤
        │●●◯●◯●●●●◯●●●●●●●●●│  fouling + visible rocks
        ├════════════════════┤
        │▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓│  gray
        ├════════════════════┤
        │████████████████████│  brown
        └────────────────────┘
```

---

## Layer Stack Definition

### What Defines a Layer?

Each layer in the painting system is defined by:

```python
@dataclass
class LayerBounds:
    bottom: float      # Where the layer starts (Y coordinate)
    top: float         # Where the layer ends (Y coordinate)
    height: float      # How thick it is (top - bottom)
```

### The Complete Layer Stack

```python
class LayerStack:
    """Immutable definition of all layers (bottom → top)"""
    
    subgrade_thickness = 0.20      # Y: 0.00 → 0.20 m
    formation_thickness = 0.10     # Y: 0.20 → 0.30 m
    ballast_thickness = 0.25       # Y: 0.30 → 0.55 m
    antenna_clearance = 0.50       # Y: 0.55 → 1.05 m
    air_buffer = 0.10              # Y: 1.05 → 1.15 m
```

### Visualization of Layer Boundaries

```
COORDINATE SYSTEM (Cross-Section):

1.15 m ──────────────────────────────── DOMAIN_TOP (air_buffer top)
       │
       │ ← air_buffer (0.10 m)
       │
1.05 m ──────────────────────────────── ANTENNA_LEVEL (antenna center)
       │
       │ ← antenna_clearance (0.50 m)
       │
0.55 m ──────────────────────────────── BALLAST_TOP
       │
       │
       │ ← ballast_thickness (0.25 m)
       │
       │  ◯  ◯  ◯  ◯ (rocks)
       │
0.30 m ──────────────────────────────── BALLAST_BOTTOM = FORMATION_TOP
       │
       │ ← formation_thickness (0.10 m)
       │
0.20 m ──────────────────────────────── FORMATION_TOP = SUBGRADE_TOP
       │
       │ ← subgrade_thickness (0.20 m)
       │
0.00 m ──────────────────────────────── BOTTOM (foundation)

X-AXIS: 0 → 2.248 m (domain_x)
Z-AXIS: 0 → 0.0132 m (domain_z, thin slice for 2D simulation)
```

---

## Layer Types and Their Roles

### 1. **Foundation Layer (Subgrade)**

```python
Layer: Subgrade
Bounds: Y = 0.00 → 0.20 m
Material: Soil (er ≈ 10)
Purpose: Represents natural ground layer
Properties:
  • Immutable (never changes)
  • Solid throughout
  • Provides EM baseline
```

### 2. **Transition Layer (Formation)**

```python
Layer: Formation
Bounds: Y = 0.20 → 0.30 m
Material: Subballast (er ≈ 10)
Purpose: Prevents mixing between subgrade and ballast
Properties:
  • Acts as interface
  • Can have texture/roughness
  • Separates soil from aggregate
```

### 3. **Main Layer (Ballast)**

```python
Layer: Ballast
Bounds: Y = 0.30 → 0.55 m
Material: 
  • Background: Clean ballast (er ≈ 5)
  • Rocks: Triangulated aggregates
  • Fouling: Material + moisture (er varies)
Purpose: Railway aggregate with rocks and fouling
Properties:
  • Most complex layer
  • Contains variable geometry (rocks)
  • Fouling covers rocks via painter's algorithm
```

### 4. **Air Layer (Free Space)**

```python
Layer: Air
Bounds: Y = 0.55 → 1.15 m
Material: Free space (er ≈ 1)
Purpose: Above-ground region
Properties:
  • Antenna mounted here
  • Propagates EM waves
  • EM energy received at this level
```

---

## How Each Worker Interacts with Layers

### Worker Execution Order (Painter's Sequence)

```
AirWorker (1st)
├─ Paint entire domain white (air)
├─ Establishes baseline
└─ Everything else overrides this

SubgradeWorker (2nd)
├─ Paint foundation brown (soil)
├─ Starts building layers
└─ Y: 0.00 → 0.20 m

FormationWorker (3rd)
├─ Paint transition layer gray
├─ Separates subgrade from ballast
└─ Y: 0.20 → 0.30 m

BallastWorker (4th)
├─ Paint ballast region tan
├─ Background material for rocks
└─ Y: 0.30 → 0.55 m

GranularMatrixWorker (5th) ← MOST COMPLEX
├─ Paint individual rocks (triangles)
│  └─ Only within ballast bounds (0.30–0.55 m)
├─ Paint fouling box (solid)
│  └─ Covers rocks where they overlap (painter's algorithm)
└─ Calculate metadata (PVC, FI, density)

AntennaWorker (6th)
├─ Add transmitter (hertzian_dipole)
├─ Add receiver (rx)
└─ Both in air layer (Y > 0.55 m)

AssemblerWorker (7th)
├─ Validate all layers
├─ Ensure no conflicts
└─ Prepare for file writing
```

### Spatial Constraints Enforced by CoordinateSystem

```python
# Each worker knows:

# SubgradeWorker:
bounds = coords.bounds(Layer.SUBGRADE)
# Paints: Y = 0.00 → 0.20 m

# FormationWorker:
bounds = coords.bounds(Layer.FORMATION)
# Paints: Y = 0.20 → 0.30 m

# BallastWorker:
bounds = coords.bounds(Layer.BALLAST)
# Paints: Y = 0.30 → 0.55 m

# GranularMatrixWorker:
bounds = coords.bounds(Layer.BALLAST)
# Packs rocks only in: Y = 0.30 → 0.55 m
# Fouling only covers: Y = 0.30 → 0.40 m (example)

# AntennaWorker:
antenna_y = coords.get_y(Anchor.ANTENNA_LEVEL)
# Places antenna at: Y = 1.05 m (above all layers)
```

---

## The Fouling Layer: Key Insight

### Why Fouling is a "Paint Over" Layer

```
CONCEPT: Fouling fills voids between rocks

IMPLEMENTATION: We use painter's algorithm
  1. Paint rocks first (triangles scattered in ballast region)
  2. Paint fouling box SECOND (solid box covering rocks)
  3. Result: Fouling covers rocks where they overlap

WHY THIS WORKS:
  ✓ Simulates real fouling filling voids
  ✓ No CSG needed (complex geometry algorithms)
  ✓ Simple to compute
  ✓ Gives exact PVC (percentage void contamination)
```

### Example: 50% Fouling

```
CLEAN BALLAST (no fouling):
Y = 0.30 → 0.55 m
├─ Rocks: ◯ ◯ ◯ ◯ ◯ (scattered)
└─ Voids: space between rocks

50% FOULED:
Y = 0.30 → 0.50 m (covers 50% of ballast height)
├─ Fouling box: ████████ (solid, covers bottom 50%)
│  └─ Rocks below 0.50m are hidden (overridden)
│  └─ Rocks above 0.50m still visible: ◯ ◯
└─ This gives exactly 50% contamination
```

### How PVC (Percentage Void Contamination) Works

```python
# In GranularMatrixWorker:

pvc_target = 50.0  # Want 50% fouling

# Calculate fouling height to achieve 50%:
fouling_height = calculate_fouling_height(rocks, pvc_target=50)
# Result: fouling_height = 0.20 m (for a 0.25m ballast)

# Paint fouling as solid box:
fouling_box = BoxCommand(
    x1=0,
    y1=0.30,           # ballast_bottom
    y2=0.30 + fouling_height,  # 0.30 + 0.20 = 0.50
    material='bal_foul_granular'
)

# Painter's algorithm takes over:
# Where fouling_box overlaps with rocks → fouling wins
# Void area covered = fouling_height × domain_x
# Void area total = ballast_height × domain_x
# PVC = (void_covered / void_total) × 100%
```

---

## Coordinate System as the Enabling Foundation

### Why We Unified on CoordinateSystem

**Before (Problematic):**
```
Workers had to know layer boundaries themselves:
  ❌ AirWorker: hardcode domain_y
  ❌ SubgradeWorker: hardcode 0.20
  ❌ FormationWorker: hardcode 0.30
  ❌ BallastWorker: hardcode 0.55
  ❌ Risk: Inconsistent (copy-paste errors)
```

**After (Clean):**
```
Single source of truth (CoordinateSystem):
  ✅ AirWorker: coords.bounds(Layer.AIR)
  ✅ SubgradeWorker: coords.bounds(Layer.SUBGRADE)
  ✅ FormationWorker: coords.bounds(Layer.FORMATION)
  ✅ BallastWorker: coords.bounds(Layer.BALLAST)
  ✅ Guarantee: All consistent, validated
```

### Validation Prevents Mistakes

```python
# CoordinateSystem validates:
✓ All thicknesses positive
✓ No gaps between layers
✓ Total height reasonable
✓ Layers don't exceed domain

# If misconfigured:
try:
    coords = CoordinateSystem(
        LayerStack(
            subgrade_thickness=-0.1,  # ❌ INVALID
            ...
        )
    )
except ValueError as e:
    print("Invalid configuration:")
    print("  - subgrade_thickness must be positive")
    # Fail fast, not silently later!
```

---

## Practical Example: Generating a Specific Configuration

### Scenario: Clean Ballast at 400 MHz

```python
# 1. USER SPECIFIES:
config = GeneratorConfig(
    domain_x=2.248,
    domain_y=3.199,
    domain_z=0.0132,
    subgrade_thickness=0.20,
    formation_thickness=0.10,
    max_ballast_thickness=0.55,
    antenna_clearance_above_ballast=0.50,
    tx_frequency=400e6,
    pvc_target=0.0,  # No fouling (clean)
)

# 2. COORDINATE SYSTEM COMPUTES:
layer_stack = LayerStack(
    subgrade_thickness=0.20,
    formation_thickness=0.10,
    ballast_thickness=0.55,
    antenna_clearance=0.50,
    air_buffer=0.1,
)
coords = CoordinateSystem(layer_stack)

# 3. LAYERS DEFINED:
Layer.SUBGRADE:    0.00 → 0.20 m
Layer.FORMATION:   0.20 → 0.30 m
Layer.BALLAST:     0.30 → 0.85 m  ← Note: increased to 0.55
Layer.AIR:         0.85 → 0.95 m
Antenna:           0.85 m (ANTENNA_LEVEL)

# 4. PAINTING PROCESS:
AirWorker:        Paint 0.00 → 0.95 m: air
SubgradeWorker:   Paint 0.00 → 0.20 m: subgrade
FormationWorker:  Paint 0.20 → 0.30 m: formation
BallastWorker:    Paint 0.30 → 0.85 m: clean ballast
GranularMatrixWorker:
  ├─ Pack rocks in 0.30 → 0.85 m
  ├─ PVC = 0%, so NO fouling box
  ├─ Rocks fully exposed
  └─ Signature: clean reflections
AntennaWorker:    Place TX/RX at 0.85 m
AssemblerWorker:  Validate all OK

# 5. GENERATED .in FILE:
#domain 2.248 3.199 0.0132
#dx_dy_dz 0.0132 0.0132 0.0132
#time_window 2e-08
## pvc: 0.0
## achieved_density: 0.43
## FI_class: C
...
#box 0 0 0 2.248 0.95 0.0132 free_space
#box 0 0 0 2.248 0.20 0.0132 subgrade
#box 0 0.20 0 2.248 0.30 0.0132 formation
#box 0 0.30 0 2.248 0.85 0.0132 bal_rock
#triangle ... rock_1 ...
#triangle ... rock_2 ...
... (no fouling box because PVC=0)
#hertzian_dipole z 1.124 0.85 0.00660 ricker_src
#rx 1.174 0.85 0.00660
```

---

## Benefits of the Painting System

### 1. **Clarity and Intuition**
```
Thinking in layers is natural:
"Paint air, then paint soil, then paint ballast, then paint rocks"
```

### 2. **Simplicity**
```
No complex geometry algorithms (CSG, boolean operations)
Just paint one thing after another
```

### 3. **Flexibility**
```
Add/remove layers easily:
  • Change PVC? Just change fouling box height
  • Change density? Just adjust rock packing
  • Change antenna height? Just change Anchor.ANTENNA_LEVEL
```

### 4. **Composability**
```
Each layer is independent:
  • Subgrade doesn't know about formation
  • Formation doesn't know about ballast
  • Ballast doesn't know about antenna
Each worker is focused on one job
```

### 5. **Validation**
```
CoordinateSystem validates:
  • All layers fit within domain
  • No overlaps or gaps
  • Thicknesses reasonable
```

---

## Edge Cases and Handling

### Case 1: Very Fouled (High PVC)

```
Input: PVC = 90% (highly fouled)

Fouling box covers 90% of ballast height:
Y = 0.30 → 0.525 m (0.90 × 0.25 = 0.225 m height)

Result:
├─ Rocks below 0.525 m: hidden (overridden by fouling)
├─ Rocks above 0.525 m: visible at top
└─ Signature: Attenuated response (fines absorb energy)
```

### Case 2: Custom Layer Thickness

```
Input: ballast_thickness = 0.40 m (instead of 0.25 m)

Layer adjustment:
LayerStack(
    subgrade_thickness=0.20,
    formation_thickness=0.10,
    ballast_thickness=0.40,  # ← Changed
    antenna_clearance=0.50,
    air_buffer=0.10,
)
# Total: 1.30 m

New bounds:
Layer.BALLAST: 0.30 → 0.70 m  ← Automatically adjusted
Layer.AIR:     0.70 → 1.20 m  ← Automatically adjusted
Antenna:       1.20 m         ← Automatically adjusted

All workers automatically use new bounds!
```

### Case 3: Antenna Too Close to Ballast

```
Input: antenna_clearance = 0.05 m (too close)

Validation catches it:
try:
    coords = CoordinateSystem(layer_stack)
except ValueError:
    "antenna_clearance may be too small (< 0.2m recommended)"
```

---

## Summary: The Elegance of Painter's Algorithm

The multi-layer painting system is elegant because:

| Aspect | Benefit |
|--------|---------|
| **Intuitive** | Build bottom-up, like natural sedimentation |
| **Simple** | No CSG, boolean operations, or complex geometry |
| **Composable** | Each layer independent, workers decoupled |
| **Flexible** | Change any layer without affecting others |
| **Validatable** | CoordinateSystem ensures consistency |
| **Debuggable** | Clear order of operations |
| **Scalable** | Easy to add new layers (water table, etc.) |

---

## Visual Summary: The Complete System

```
┌──────────────────────────────────────────────────────────────┐
│                  MULTI-LAYER PAINTING SYSTEM                 │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  INPUT: Config (layer thicknesses)                          │
│         └─→ LayerStack (immutable)                          │
│             └─→ CoordinateSystem (validates + resolves)    │
│                                                              │
│  LAYERS (painted bottom-to-top):                            │
│    1. Air (baseline)               Y: 0.0 → ∞              │
│    2. Subgrade (foundation)        Y: 0.0 → 0.2 m          │
│    3. Formation (transition)       Y: 0.2 → 0.3 m          │
│    4. Ballast (aggregate)          Y: 0.3 → 0.55 m         │
│    5. Rocks (triangles)            Y: 0.3 → 0.55 m         │
│    6. Fouling (covers rocks)       Y: 0.3 → 0.4 m          │
│    7. Antenna (sources/receivers)  Y: 0.85 m               │
│                                                              │
│  PAINTER'S ALGORITHM:                                       │
│    Later layers override earlier layers in overlaps         │
│    └─→ Fouling covers rocks                                 │
│    └─→ Antennas above all                                   │
│                                                              │
│  OUTPUT: .in file (gprMax input)                            │
│          └─→ Consistent, validated geometry                │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

---

This multi-layer painting system is the architectural foundation that makes the gprMax input file generator elegant, maintainable, and extensible. 🎨


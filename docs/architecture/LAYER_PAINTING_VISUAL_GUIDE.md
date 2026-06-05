# Multi-Layer Painting System — Visual Guide

## Quick Reference: Layer Painting Order

```
PAINTER'S CANVAS - gprMax INPUT FILE GENERATION

Step 1: BASE COAT (Air - Paint Everything White)
┌─────────────────────────────┐
│░░░░░░░░░░░░░░░░░░░░░░░░░░░░│ ← Free space (air)
│░░░░░░░░░░░░░░░░░░░░░░░░░░░░│
│░░░░░░░░░░░░░░░░░░░░░░░░░░░░│
└─────────────────────────────┘

Step 2: PAINT FOUNDATION (Subgrade - Brown)
┌─────────────────────────────┐
│░░░░░░░░░░░░░░░░░░░░░░░░░░░░│ ← Air remains white
│░░░░░░░░░░░░░░░░░░░░░░░░░░░░│
│░░░░░░░░░░░░░░░░░░░░░░░░░░░░│
├═════════════════════════════┤
│██████████████████████████████│ ← Brown subgrade layer
└─────────────────────────────┘

Step 3: PAINT TRANSITION (Formation - Gray)
┌─────────────────────────────┐
│░░░░░░░░░░░░░░░░░░░░░░░░░░░░│ ← Air
│░░░░░░░░░░░░░░░░░░░░░░░░░░░░│
│░░░░░░░░░░░░░░░░░░░░░░░░░░░░│
├═════════════════════════════┤
│▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓│ ← Gray formation
├═════════════════════════════┤
│██████████████████████████████│ ← Brown subgrade
└─────────────────────────────┘

Step 4: PAINT BALLAST BACKGROUND (Tan)
┌─────────────────────────────┐
│░░░░░░░░░░░░░░░░░░░░░░░░░░░░│ ← Air
│░░░░░░░░░░░░░░░░░░░░░░░░░░░░│
├═════════════════════════════┤
│▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒│ ← Tan ballast (background)
├═════════════════════════════┤
│▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓│ ← Gray formation
├═════════════════════════════┤
│██████████████████████████████│ ← Brown subgrade
└─────────────────────────────┘

Step 5: PAINT ROCKS (Individual Aggregates)
┌─────────────────────────────┐
│░░░░░░░░░░░░░░░░░░░░░░░░░░░░│
│░░░░░░░░░░░░░░░░░░░░░░░░░░░░│
├═════════════════════════════┤
│▒▒◯▒▒◯▒▒▒▒◯▒▒▒▒▒◯▒▒▒▒▒▒▒▒▒▒│ ← Rocks (◯) on tan ballast
├═════════════════════════════┤
│▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓│
├═════════════════════════════┤
│██████████████████████████████│
└─────────────────────────────┘

Step 6: PAINT FOULING (Covers Rocks - Painter's Algorithm)
┌─────────────────────────────┐
│░░░░░░░░░░░░░░░░░░░░░░░░░░░░│
│░░░░░░░░░░░░░░░░░░░░░░░░░░░░│ ← Air above fouling
├═════════════════════════════┤
│●●◯●◯●●●●◯●●●●●●●●●●●│  ← Fouling (●) COVERS rocks
├═════════════════════════════┤
│▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒│ ← Ballast below fouling
├═════════════════════════════┤
│▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓│
├═════════════════════════════┤
│██████████████████████████████│
└─────────────────────────────┘

Step 7: PLACE ANTENNA (Above Everything)
┌─────────────────────────────┐
│         TX    RX            │ ← Antenna (T, R)
├─────────────────────────────┤
│░░░░░░░░░░░░░░░░░░░░░░░░░░░░│ ← Air
│░░░░░░░░░░░░░░░░░░░░░░░░░░░░│
├═════════════════════════════┤
│●●◯●◯●●●●◯●●●●●●●●●●●│ ← Fouling
├═════════════════════════════┤
│▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒│ ← Ballast
├═════════════════════════════┤
│▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓│ ← Formation
├═════════════════════════════┤
│██████████████████████████████│ ← Subgrade
└─────────────────────────────┘
```

---

## Coordinate System: The Painter's Guide

### Y-Axis: Height Mapping

```
Absolute Y Coordinate System (Meters)

1.15 m ─────────────────── DOMAIN_TOP
       │
       │ 0.10 m air buffer
       │ 
1.05 m ─────────────────── ANTENNA_LEVEL (antenna center)
       │
       │ 0.50 m antenna clearance above ballast
       │
0.55 m ─────────────────── BALLAST_TOP
       │ ▲
       │ │ 0.25 m ballast thickness
       │ │ (contains rocks + fouling)
       │ ▼
0.30 m ─────────────────── BALLAST_BOTTOM = FORMATION_TOP
       │ ▲
       │ │ 0.10 m formation thickness
       │ ▼
0.20 m ─────────────────── FORMATION_TOP = SUBGRADE_TOP
       │ ▲
       │ │ 0.20 m subgrade thickness
       │ ▼
0.00 m ─────────────────── BOTTOM (foundation)
```

### Workers Know Their Bounds

```python
# Each worker paints within its assigned bounds:

AirWorker:
  Paints from Y = 0.00 → ∞ (all air everywhere initially)
  Material: free_space

SubgradeWorker:
  bounds = coords.bounds(Layer.SUBGRADE)
  Paints: Y = 0.00 → 0.20 m
  Material: subgrade (soil)

FormationWorker:
  bounds = coords.bounds(Layer.FORMATION)
  Paints: Y = 0.20 → 0.30 m
  Material: formation

BallastWorker:
  bounds = coords.bounds(Layer.BALLAST)
  Paints: Y = 0.30 → 0.55 m
  Material: ballast_rock (background)

GranularMatrixWorker:
  bounds = coords.bounds(Layer.BALLAST)
  ├─ Packs rocks in: Y = 0.30 → 0.55 m
  └─ Fouling covers: Y = 0.30 → 0.40 m (example, varies by PVC)

AntennaWorker:
  antenna_y = coords.get_y(Anchor.ANTENNA_LEVEL)
  Places TX/RX at: Y = 1.05 m
```

---

## PVC (Fouling): The Painting Height

### How Fouling Depth Determines PVC

```
CONCEPT: Fouling box height = percentage void contamination

0% FOULED (Clean):
┌─ 0.55 m
│
│ ◯  ◯  ◯  ◯  (all rocks visible)
│
│ ◯  ◯  ◯  ◯
│
└─ 0.30 m
Height of fouling box: 0 m → PVC = 0%

25% FOULED:
┌─ 0.55 m
│
│ ◯  ◯  ◯  ◯  (rocks above fouling still visible)
│ ─ ─ ─ ─ (fouling line at 0.4375 m)
│ ●  ◯  ●  ◯  (rocks below fouling are covered)
│
└─ 0.30 m
Height of fouling box: 0.25 × 0.25 = 0.0625 m → PVC = 25%

50% FOULED:
┌─ 0.55 m
│
│ ◯  ◯  ◯  ◯  (rocks above fouling visible)
│ ─ ─ ─ ─ (fouling line at 0.425 m)
│ ●  ●  ●  ●  (rocks below fouling covered)
│
└─ 0.30 m
Height of fouling box: 0.50 × 0.25 = 0.125 m → PVC = 50%

100% FOULED (Highly Fouled):
┌─ 0.55 m
│ ─ ─ ─ ─ (fouling line at 0.55 m - full height)
│ ●  ●  ●  ●  (all rocks covered by fouling)
│ ●  ●  ●  ●
│
└─ 0.30 m
Height of fouling box: 1.00 × 0.25 = 0.25 m → PVC = 100%

FORMULA:
  fouling_height = PVC% × ballast_height
  fouling_y_top = ballast_bottom + fouling_height
  
Example (50% PVC, 0.25m ballast):
  fouling_height = 0.50 × 0.25 = 0.125 m
  fouling_y_top = 0.30 + 0.125 = 0.425 m
```

---

## Rock Painting: Triangulation at Different Levels

### Cross-Section View (Side View)

```
ROCK DISTRIBUTION IN BALLAST LAYER:

Y = 0.55 m ┌──────────────────────────────────┐
           │ AIR (rocks don't extend here)   │
           │                                  │
Y = 0.50 m │ ◯  (rock near top)              │
           │      \●/  (fouling covers top)  │
           │       ∩                          │
Y = 0.40 m ├──────────────────────────────────┤
           │ FOULING BOX (50% PVC)           │
           │  ◯    ◯              (visible)  │
           │  
Y = 0.35 m │ ◯  ◯      ◯        (mostly covered)
           │    
Y = 0.30 m ├──────────────────────────────────┤
           │ BALLAST BACKGROUND              │
           
X-AXIS: 0 → 2.248 m (horizontal spread)
Z-AXIS: 0 → 0.0132 m (thin slice, 2D simulation)
```

### Top-Down View (What Antenna Sees)

```
LOOKING DOWN FROM ANTENNA AT Y = 1.05 m:

┌─────────────────────────────────────────┐
│                                         │  Upper rocks (visible)
│       ◯   ◯         ◯                   │
│                                         │
│   ◯           ◯                  ◯      │
│                                         │
│                 ◯      ◯                │  Fouling region
│       ◯                       ◯         │
│                                         │
│            ◯     ◯        ◯      ◯      │
│                                         │  Lower rocks
│  ◯                    ◯                 │  (mostly covered by
│                                         │   fouling paint)
└─────────────────────────────────────────┘
```

---

## The Painter's Algorithm: Key Insight

```
PRINCIPLE: Last Layer Wins in Overlaps

Layer Order in .in file:
  1. #box ... free_space    (white paint)
  2. #box ... subgrade      (brown paint)
  3. #box ... formation     (gray paint)
  4. #box ... ballast       (tan paint)
  5. #triangle ... rocks 1-100  (rock paint)
  6. #box ... fouling       (dark paint) ← PAINTS OVER ROCKS!

gprMax Rendering (Back-to-Front):
  ↑
  │
  ├─ Layer 6: Fouling box painted last
  │           └─ Where it overlaps rocks, fouling is visible
  │
  ├─ Layer 5: Rocks painted before fouling
  │           └─ Where rocks NOT covered by fouling, visible
  │
  ├─ Layer 4: Ballast background painted
  │           └─ Where no rocks/fouling, ballast visible
  │
  ├─ Layer 3: Formation visible below ballast
  │
  ├─ Layer 2: Subgrade visible below formation
  │
  └─ Layer 1: Air fills empty space

RESULT: Realistic fouling-filled-voids simulation
        without needing CSG or boolean operations!
```

---

## Coordinate System: Guarantee Structure

```
INPUT VALIDATION & TRANSFORMATION:

GeneratorConfig (user's wishes)
    ├─ domain_x: 2.248 m
    ├─ domain_y: 3.199 m
    ├─ subgrade_thickness: 0.20 m
    ├─ formation_thickness: 0.10 m
    ├─ ballast_thickness: 0.25 m
    ├─ antenna_clearance: 0.50 m
    └─ air_buffer: 0.10 m

    ↓

LayerStack (computed thicknesses)
    ├─ subgrade_thickness: 0.20 m
    ├─ formation_thickness: 0.10 m
    ├─ ballast_thickness: 0.25 m
    ├─ antenna_clearance: 0.50 m
    └─ air_buffer: 0.10 m
    
    total_height = 1.15 m

    ↓

CoordinateSystem (validated & resolved)
    
    VALIDATION CHECKS:
    ✓ All thicknesses > 0
    ✓ Total height in [0.5, 10.0] m
    ✓ No configuration errors

    PRECOMPUTED MAPPINGS:
    ✓ Anchor.BOTTOM         → Y = 0.00 m
    ✓ Anchor.SUBGRADE_TOP   → Y = 0.20 m
    ✓ Anchor.FORMATION_TOP  → Y = 0.30 m
    ✓ Anchor.BALLAST_TOP    → Y = 0.55 m
    ✓ Anchor.ANTENNA_LEVEL  → Y = 1.05 m
    ✓ Anchor.DOMAIN_TOP     → Y = 1.15 m

    LAYER BOUNDS:
    ✓ Layer.SUBGRADE:  [0.00, 0.20] m
    ✓ Layer.FORMATION: [0.20, 0.30] m
    ✓ Layer.BALLAST:   [0.30, 0.55] m
    ✓ Layer.AIR:       [0.55, 1.15] m

    ↓

Workers (guaranteed correct bounds)
    
    Each worker gets:
    • Explicit bounds: coords.bounds(Layer.X)
    • Guaranteed consistency
    • Automatic updates if config changes
    • Validation at init time
```

---

## Complete Workflow: Single Scenario

```
SCENARIO: Generate clean ballast at 400 MHz

INPUT:
  ConfigGeneratorConfig(
    pvc_target=0.0,        # No fouling
    tx_frequency=400e6,
    max_ballast_thickness=0.25,
  )

PROCESSING:
  
  Step 1: Create LayerStack
    └─ Compute all thickness sums
  
  Step 2: Create CoordinateSystem
    ├─ Validate all thicknesses
    ├─ Check total height fits in domain
    └─ Precompute all Y coordinates
  
  Step 3: Run Workers in Order
    
    AirWorker:
      └─ Paint entire domain white (air)
    
    SubgradeWorker:
      └─ Paint Y = 0.00 → 0.20 m (soil)
    
    FormationWorker:
      └─ Paint Y = 0.20 → 0.30 m (subballast)
    
    BallastWorker:
      └─ Paint Y = 0.30 → 0.55 m (ballast)
    
    GranularMatrixWorker:
      ├─ Get ballast bounds: Y = 0.30 → 0.55 m
      ├─ Pack rocks in this region
      ├─ PVC = 0% → NO fouling box
      └─ Metadata: FI_class = "C" (clean)
    
    AntennaWorker:
      ├─ Get antenna height: Y = 1.05 m
      ├─ Place TX at (1.124, 1.05, 0.0066)
      └─ Place RX at (1.174, 1.05, 0.0066)
    
    AssemblerWorker:
      └─ Validate: all OK ✓
  
  Step 4: Generate .in File
    └─ Output painting sequence as gprMax commands

OUTPUT:
  
  s_00000.in:
    ## pvc: 0.0
    ## FI_class: C
    ## achieved_density: 0.43
    
    #domain 2.248 3.199 0.0132
    #dx_dy_dz 0.0132 0.0132 0.0132
    
    #box ... free_space    (air)
    #box ... subgrade      (soil)
    #box ... formation     (subballast)
    #box ... ballast       (ballast background)
    #triangle ... (rocks)  (← no fouling here)
    #hertzian_dipole ...   (TX antenna)
    #rx ...                (RX antenna)

READY FOR SIMULATION!
  
  gprMax will:
  1. Parse .in file
  2. Set up FDTD grid (0.0132m cells)
  3. Place materials at each point
  4. Run 20 ns simulation
  5. Record antenna response → Ez waveform
  6. Output to s_00000.out (HDF5 file)
```

---

## Summary: Why This Architecture is Elegant

```
┌────────────────────────────────────────────────────────────┐
│                                                            │
│  🎨 MULTI-LAYER PAINTING SYSTEM                           │
│                                                            │
│  Paint bottom-to-top, like real geology                   │
│  Later layers naturally override earlier ones             │
│  No complex geometry algorithms needed                    │
│  Intuitive & composable                                  │
│                                                            │
│  ✓ Single coordinate system ensures consistency          │
│  ✓ Validation prevents mistakes at init time             │
│  ✓ Each worker independent (focused responsibility)      │
│  ✓ Easy to extend (add new layers, change parameters)    │
│  ✓ Scalable (works for simple and complex geometries)    │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

---

This visual guide makes the painter's algorithm concrete and shows why the architecture is both powerful and elegant. 🎨


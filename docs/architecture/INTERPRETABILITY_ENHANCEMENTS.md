# Interpretability Enhancements for Multi-Layer Painting System

## Overview

Interpretability means making the system's behavior, decisions, and outputs **transparent and understandable** to users, developers, and future maintainers. This document proposes enhancements across multiple dimensions.

---

## 1. Visual Interpretability Enhancements

### 1.1 Interactive Layer Visualization

**Current State:**
- ASCII diagrams in documentation
- Static visualizations

**Enhancement:**
Create an interactive visualization tool showing:

```python
class LayerVisualizer:
    """Interactive layer and coordinate visualization"""
    
    def visualize_coordinate_system(self, config: GeneratorConfig):
        """
        Generates an interactive HTML/SVG showing:
        - Layer stack with exact Y coordinates
        - Domain boundaries
        - Antenna position
        - Rock distribution (if applicable)
        - Fouling coverage area
        - Color-coded materials
        
        Output: Interactive dashboard
        - Hover to see exact coordinates
        - Click to inspect layer properties
        - Zoom/pan for detail
        """
        pass
    
    def show_execution_flow(self, checkpoint: SceneCheckpoint):
        """
        Shows how the scene was built:
        - Worker execution order (Gantt-style timeline)
        - What each worker added
        - Coordinate resolution step-by-step
        - Validation checks at each stage
        """
        pass
    
    def compare_configurations(self, config1, config2):
        """
        Side-by-side comparison of two configurations:
        - Layer thickness changes
        - Antenna position changes
        - Domain size implications
        - Highlights differences
        """
        pass
```

### 1.2 Generated .in File Annotated View

**Enhancement:**
Generate annotated `.in` files with explanatory comments:

```
## CONFIGURATION SUMMARY
## Layer Stack:
##   Subgrade:    Y = 0.00 → 0.20 m (soil foundation)
##   Formation:   Y = 0.20 → 0.30 m (subballast transition)
##   Ballast:     Y = 0.30 → 0.55 m (aggregate + fouling)
##   Air:         Y = 0.55 → 1.15 m (free space + antenna)
##
## Fouling:
##   PVC Target:  50.0%
##   Fouling Box: Y = 0.30 → 0.425 m (height = 0.125 m)
##   Rocks:       ~80 aggregates scattered in ballast zone
##
## Antenna:
##   TX Position: (1.124, 1.05, 0.00660) m
##   RX Position: (1.174, 1.05, 0.00660) m
##   Separation:  0.05 m (bistatic configuration)

## DOMAIN CONFIGURATION
#domain 2.248 3.199 0.0132
##  ↑ Domain size: 2.248m (x) × 3.199m (y) × 0.0132m (z)
##  ↑ Domain_y (3.199m) ≥ Required (1.15m) ✓ Valid

#dx_dy_dz 0.0132 0.0132 0.0132
##  ↑ Cell size: 13.2 mm = λ/10 at 400 MHz ✓ Compliant

#time_window 2e-08
##  ↑ Simulation duration: 20 ns (sufficient for deep reflections)

## MATERIAL DEFINITIONS
#material 10 0 1 0 subgrade
##  ↑ Subgrade: er=10 (typical soil), lossless

#material 5 0 1 0 ballast_rock
##  ↑ Clean ballast: er=5 (aggregate), lossless

#material 8.3 1.2 1 0 bal_foul_granular
##  ↑ Fouling mix: er=8.3 (50% PVC), σ=1.2 S/m (moisture)

## GEOMETRY DESCRIPTION
#box 0 0 0 2.248 3.199 0.0132 free_space
##  ↑ Base coat: Paint entire domain with air (painter's algorithm)

#box 0 0 0 2.248 0.20 0.0132 subgrade
##  ↑ Subgrade layer: Foundation soil (0.20 m thick)

#box 0 0.30 0 2.248 0.55 0.0132 ballast_rock
##  ↑ Ballast background: Clean aggregate zone (0.25 m thick)

## ROCK AGGREGATES (80 triangles, computed via Shang-Chu packing)
#triangle 0.234 0.342 0.001 0.268 0.378 0.008 0.195 0.356 0.004 ballast_rock
##  ↑ Rock 1: Centroid ~(0.23, 0.35), radius ~0.017 m

#triangle ...
##  ↑ Rock 2-80: Additional aggregates (see metadata for positions)

## FOULING LAYER (Painter's algorithm: covers rocks)
#box 0 0.30 0 2.248 0.425 0.0132 bal_foul_granular
##  ↑ Fouling covers: Bottom 50% of ballast (0.125 m height)
##  ↑ Painter's algorithm: Rocks below 0.425m are hidden
##  ↑ Rocks above 0.425m remain visible

## ANTENNA CONFIGURATION
#waveform ricker 1 4e+08 ricker_src
##  ↑ Ricker wavelet: 1 V amplitude, 400 MHz center frequency

#hertzian_dipole z 1.124 1.05 0.00660 ricker_src
##  ↑ TX antenna: Z-oriented dipole at (1.124, 1.05, 0.0066) m
##  ↑ Position: 0.50 m above ballast (antenna_clearance)

#rx 1.174 1.05 0.00660
##  ↑ RX antenna: Receiver at (1.174, 1.05, 0.0066) m
##  ↑ Offset: +0.05 m in X (bistatic TX-RX separation)
```

---

## 2. Code Interpretability Enhancements

### 2.1 Self-Documenting Code Structure

**Enhancement: Semantic Variable Naming**

```python
# BEFORE (less clear)
bounds = coords.bounds(Layer.BALLAST)
start_y, top_y = bounds.bottom, bounds.top
fouling_height = calculate_fouling_height(rocks, pvc_target)
top_y_fouling = start_y + fouling_height

# AFTER (more interpretable)
ballast_bounds = coords.bounds(Layer.BALLAST)
ballast_bottom_y = ballast_bounds.bottom
ballast_top_y = ballast_bounds.top

fouling_depth_meters = calculate_fouling_height(
    rocks=rocks,
    pvc_target_percent=pvc_target,
    ballast_height_meters=ballast_bounds.height
)
fouling_top_y = ballast_bottom_y + fouling_depth_meters

# The naming makes the physical meaning obvious!
```

### 2.2 Type Hints with Physical Units

```python
from dataclasses import dataclass
from typing import NewType

# Create semantic types for clarity
MetersY = NewType('MetersY', float)  # Y coordinate in meters
PercentagePVC = NewType('PercentagePVC', float)  # 0-100%
MetersDelta = NewType('MetersDelta', float)  # Distance in meters

@dataclass
class LayerBounds:
    """Physical bounds of a geological layer"""
    bottom: MetersY  # ← Clear unit and meaning
    top: MetersY    # ← Clear unit and meaning
    height: MetersDelta
    
    def __str__(self) -> str:
        return f"Layer Y={self.bottom:.2f}m → {self.top:.2f}m (h={self.height:.3f}m)"

def calculate_fouling_height(
    rocks: List[Rock],
    pvc_target_percent: PercentagePVC,
    ballast_height_meters: MetersDelta,
) -> MetersDelta:
    """
    Calculate how deep the fouling layer needs to be.
    
    Physical Interpretation:
      fouling_depth = (PVC% / 100) × ballast_height
      
      This height represents the depth of fine material that must
      fill void spaces to achieve the target PVC percentage.
      
    Args:
        rocks: Rock aggregates in ballast layer
        pvc_target_percent: Target PVC (0-100%)
        ballast_height_meters: Total ballast thickness
        
    Returns:
        Depth to paint fouling box (in meters)
        
    Example:
        For 50% PVC in 0.25m ballast:
        → fouling_height = 0.50 × 0.25 = 0.125 m
        → Paint fouling from y=0.30 → 0.425 m
    """
    fouling_height = (pvc_target_percent / 100.0) * ballast_height_meters
    return MetersDelta(fouling_height)
```

### 2.3 Decision Point Documentation

```python
class GranularMatrixWorker(Worker):
    """Paint rocks and fouling into ballast layer (via painter's algorithm)"""
    
    def execute(self, scene: SceneCheckpoint, params, materials, tools):
        """
        DECISION TREE: How to paint fouling
        
        Step 1: Get ballast bounds
            WHY: Constrains where rocks can be placed
            DECISION: Use CoordinateSystem (single source of truth)
            RISK: If bounds are wrong, rocks in wrong Y-range
        
        Step 2: Pack rocks
            WHY: Create aggregate distribution
            DECISION: Use config.rock_packing_algorithm
            TRADE-OFF: Shang-Chu (slow, high quality) vs Grid (fast, regular)
            RISK: Too many rocks → performance issue
                  Too few rocks → unrealistic density
        
        Step 3: Classify rocks
            WHY: Distinguish large rocks from fines
            DECISION: Use 2× fouling_particle_size as threshold
            RATIONALE: Rocks ≥ 4mm stay; smaller particles become fouling
            RISK: Threshold too low → rocks classified as fouling
                  Threshold too high → fines classified as rocks
        
        Step 4: Gravity settle
            WHY: Simulate realistic sedimentation
            DECISION: Move rocks down until touching surface
            ASSUMPTION: Linear gravity, no friction/interaction
            LIMITATION: Doesn't account for rock-rock interactions
        
        Step 5: Paint fouling box
            WHY: Represent void-filling material
            DECISION: Use painter's algorithm (later commands override)
            RATIONALE: Simple, physically interpretable
            LIMITATION: Fouling is a solid box, not scattered particles
            ASSUMPTION: Fouling fills voids uniformly
        
        Step 6: Calculate metadata
            WHY: Record what was actually generated
            DECISION: Measure achieved PVC from geometry
            IMPLICATION: Actual PVC ≠ target PVC (due to packing randomness)
        """
        pass
```

---

## 3. Configuration Interpretability Enhancements

### 3.1 Configuration Validation with Explanations

```python
class ConfigInterpreter:
    """Explain what a configuration means physically"""
    
    def interpret_config(self, config: GeneratorConfig) -> str:
        """
        Generate a human-readable interpretation of the configuration.
        
        Example output:
        ```
        === CONFIGURATION INTERPRETATION ===
        
        DOMAIN:
          - Size: 2.248m (x) × 3.199m (y) × 0.0132m (z)
          - Interpretation: ~2.2m wide, ~3.2m tall, thin 2D slice
          - Cell size: 13.2mm = λ/10 at 400 MHz ✓ FDTD compliant
        
        LAYER STACK (Bottom → Top):
          1. Subgrade (0.0 → 0.2m)
             - Represents: Natural ground/soil foundation
             - Material: ER=10 (typical soil)
             - Interpretation: Ground reflectivity baseline
        
          2. Formation (0.2 → 0.3m)  
             - Represents: Transition layer (subballast)
             - Material: ER=10 (similar to subgrade)
             - Interpretation: Interface, prevents mixing
        
          3. Ballast (0.3 → 0.55m)
             - Represents: Railway aggregate layer with fouling
             - Height: 0.25m (typical for railway track)
             - Composition: Rocks (ER=5) + Fouling (ER≈8)
             - PVC: 50% (medium fouling level)
             - Interpretation: Primary region of interest for GPR
        
          4. Air (0.55 → 1.15m)
             - Represents: Free space above ballast
             - Antenna position: 1.05m (0.5m above ballast)
             - Material: ER=1 (vacuum/air)
             - Interpretation: EM wave propagation medium
        
        ANTENNA CONFIGURATION:
          - Type: Bistatic (separate TX/RX)
          - Frequency: 400 MHz
          - TX-RX offset: 0.05m (horizontal separation)
          - Interpretation: Standard railway GPR setup
        
        PHYSICAL SCENARIO:
          - Simulates: Railway ballast fouling assessment
          - Fouling level: 50% (Medium - significant contamination)
          - Expected signature: Attenuated response, wide pulse
          - Application: Detect fouling via EM wave attenuation
        ```
        """
        pass
    
    def validate_with_explanations(self, config: GeneratorConfig) -> List[str]:
        """
        Validate configuration and explain why each check matters.
        
        Returns list of validation messages like:
        
        ✓ Domain height sufficient for layer stack
          Reason: Air layer and antenna need clearance
          
        ✓ Cell size adequate for frequency
          Reason: FDTD requires λ/10 rule for accuracy at 400 MHz
          
        ⚠ Ballast thickness at lower end (0.25m)
          Reason: Railway ballast typically 0.25-0.5m
          Recommendation: Consider 0.35-0.4m for standard track
          
        ❌ Domain width marginal for antenna
          Reason: gprMax recommends 1.5λ on each side
          Fix: Increase domain_x from 2.248m to 2.8m minimum
        """
        pass
```

### 3.2 What-If Analysis

```python
class ConfigExplorer:
    """Understand how parameters affect the scene"""
    
    def parameter_sensitivity(self, base_config: GeneratorConfig):
        """
        Show how changing each parameter affects the scene.
        
        Example:
        ┌─────────────────────────────────────────────────────────┐
        │ Parameter Sensitivity Analysis                          │
        ├─────────────────────────────────────────────────────────┤
        │                                                         │
        │ PVC (Percentage Void Contamination)                    │
        │ ──────────────────────────────────────────────────     │
        │  0% → Clean ballast, distinct reflections             │
        │       Fouling layer: none (no paint)                   │
        │       Signature: sharp peaks                           │
        │                                                         │
        │ 25% → Light fouling                                    │
        │       Fouling layer: 0.0625m thick (paint 25% height) │
        │       Signature: slightly attenuated                   │
        │                                                         │
        │ 50% → Moderate fouling (STANDARD)                      │
        │       Fouling layer: 0.125m thick (paint 50% height)  │
        │       Signature: noticeably attenuated                 │
        │                                                         │
        │ 75% → Heavy fouling                                    │
        │       Fouling layer: 0.1875m thick (paint 75%)        │
        │       Signature: very attenuated, broad pulse          │
        │                                                         │
        │ 100% → Fully fouled                                    │
        │       Fouling layer: 0.25m thick (entire ballast)     │
        │       Signature: minimal reflections                   │
        │                                                         │
        └─────────────────────────────────────────────────────────┘
        
        Ballast Thickness
        ──────────────────
         0.15m → Shallow ballast (industrial tracks)
         0.25m → Standard railway (this project default)
         0.40m → Deep ballast (high-speed tracks)
         0.60m → Very deep (tunnel/bridge ballast)
         
        Effect on antenna position:
          ↑ Ballast thickness → ↑ Antenna height → longer propagation path
        """
        pass
```

---

## 4. Validation & Error Message Interpretability

### 4.1 Rich Error Messages

```python
# BEFORE (generic)
raise ValueError("Invalid layer configuration")

# AFTER (interpretable)
raise ValueError("""
╔════════════════════════════════════════════════════════════╗
║ LAYER CONFIGURATION ERROR                                 ║
╠════════════════════════════════════════════════════════════╣
║                                                            ║
║ Problem: Domain height insufficient for layer stack       ║
║                                                            ║
║ Current configuration:                                    ║
║   ├─ Subgrade:    0.20m                                   ║
║   ├─ Formation:   0.10m                                   ║
║   ├─ Ballast:     0.30m (variable, you specified)        ║
║   ├─ Antenna cl:  0.50m (clearance above ballast)        ║
║   ├─ Air buffer:  0.10m (PML padding)                    ║
║   └─ Total:       1.20m ← Required                       ║
║                                                            ║
║ Your domain_y: 1.0m ← Available (TOO SMALL)              ║
║ Deficit: 0.20m                                            ║
║                                                            ║
║ Solution: Increase domain_y to at least 1.20m            ║
║                                                            ║
║ Physical interpretation:                                  ║
║   Antenna must be above free space, which must be above   ║
║   ballast. The minimum domain height is determined by     ║
║   these layering requirements.                            ║
║                                                            ║
║ Recommendation:                                           ║
║   Set domain_y = 1.50m (adds safety margin)              ║
║                                                            ║
╚════════════════════════════════════════════════════════════╝
""")
```

### 4.2 Validation Warnings with Context

```python
class ValidationExplainer:
    """Explain what validation warnings mean"""
    
    def validate_and_explain(self, config: GeneratorConfig):
        """
        Run validation and provide educational explanations.
        """
        warnings = []
        
        # ⚠️  Domain width marginal
        if config.domain_x < 3.0:
            warnings.append({
                'severity': 'warning',
                'code': 'DOMAIN_WIDTH_NARROW',
                'message': 'Domain width is on the narrow side',
                'technical': '''
                    gprMax FDTD requires sufficient lateral domain
                    to avoid reflections from boundaries.
                    
                    Recommended: domain_x ≥ 3.0m
                    Your setting: {config.domain_x}m
                    
                    Formula: domain_x ≥ 1.5λ_max on each side
                    At 400 MHz in free space: λ = 0.75m
                    Required: 1.5×0.75 × 2 = 2.25m
                ''',
                'impact': 'Artificial reflections from domain boundaries',
                'recommendation': f'Increase domain_x to 3.0-4.0m',
            })
        
        # ⚠️  Ballast thickness unusual
        if not (0.2 <= config.max_ballast_thickness <= 0.5):
            warnings.append({
                'severity': 'info',
                'code': 'BALLAST_THICKNESS_UNUSUAL',
                'message': 'Ballast thickness outside typical range',
                'technical': '''
                    Railway ballast depths vary by application:
                    - Industrial tracks: 0.15-0.20m
                    - Standard gauge: 0.25-0.35m (most common)
                    - High-speed: 0.35-0.50m
                    
                    Your setting: {config.max_ballast_thickness}m
                ''',
                'physical_meaning': '''
                    Ballast thickness affects:
                    1. EM wave propagation path length
                    2. Number of internal reflections
                    3. Total attenuation experienced
                ''',
                'recommendation': 'Use 0.25-0.35m for typical scenarios',
            })
```

---

## 5. Metadata & Output Interpretability

### 5.1 Rich Metadata Output

```python
# Generated .in file metadata (BEFORE)
## pvc: 50.0
## achieved_density: 0.43
## FI_class: F

# Generated .in file metadata (AFTER - Interpretable)
## INPUT PARAMETERS
## pvc_target: 50.0 (Target percentage void contamination)
## moisture: 0.10 (Fouling material moisture content)
##
## COMPUTED PROPERTIES (Measured from Geometry)
## achieved_pvc: 48.7 (Actual PVC after packing ≈ target ✓)
## achieved_density: 0.428 (Rock volume fraction in ballast)
##
## CLASSIFICATION (Selig & Waters, 1994)
## Lab_FI: 0.648 (Fouling Index = PVC × density)
## FI_class: F (Fouled: 0.6 < FI < 0.8)
##
## PHYSICAL INTERPRETATION
## Fouling_depth_m: 0.125 (Depth to paint fouling: 50% of 0.25m)
## Rocks_visible: 42 (Rocks above fouling plane, visible to EM)
## Rocks_covered: 38 (Rocks below fouling plane, covered)
## Clean_ballast_thickness_m: 0.125 (Above fouling)
##
## EXPECTED SIGNAL CHARACTERISTICS
## Signal_attenuation: Moderate (fines absorb high frequencies)
## Expected_bandwidth: Narrowed (high freq attenuated)
## Expected_pulse_width: Widened (dispersed propagation)
## Expected_reflections: Smeared (multiple scattering)
```

### 5.2 Generated Scene Report

```python
class SceneReport:
    """Generate human-readable report of generated scene"""
    
    def generate_html_report(self, checkpoint: SceneCheckpoint) -> str:
        """
        Generate interactive HTML report showing:
        
        1. Configuration Summary
           - Input parameters with physical units
           - Computed dimensions and positions
           - Validation results
        
        2. Layer Stack Visualization
           - Interactive diagram showing layer positions
           - Coordinate ruler (Y-axis)
           - Hover shows exact boundaries and material properties
        
        3. Material Distribution
           - Rock count and positions
           - Fouling coverage depth
           - Void space analysis
        
        4. Antenna Setup
           - TX/RX positions
           - Separation distance
           - Clearance from ballast
        
        5. Physics Summary
           - Expected signal characteristics
           - Attenuation estimates
           - Bandwidth effects
        
        6. Quality Metrics
           - Validation results
           - Layer contiguity check
           - Domain adequacy check
        
        7. Export Options
           - Download metadata as JSON
           - Export coordinates as CSV
           - Export .in file with annotations
        """
        pass
```

---

## 6. Development-Time Interpretability

### 6.1 Execution Tracing

```python
class ExecutionTracer:
    """Record and visualize execution flow"""
    
    def trace_execution(self, verbose=True):
        """
        Log each operation with timing and results.
        
        Example trace:
        
        ┌─ PRODUCTION LINE EXECUTION ─────────────────────────┐
        │                                                     │
        │ [1] Initialize                                      │
        │     ├─ Config loaded: domain=2.248×3.199×0.0132    │
        │     ├─ LayerStack created                          │
        │     │   ├─ subgrade: 0.20m                         │
        │     │   ├─ formation: 0.10m                        │
        │     │   ├─ ballast: 0.25m                          │
        │     │   └─ air: 0.6m (1.15m total)                │
        │     └─ CoordinateSystem initialized ✓              │
        │         Time: 2.3ms                                │
        │                                                     │
        │ [2] AirWorker (Paint baseline)                     │
        │     ├─ Action: Paint 0.00→3.199m with air        │
        │     ├─ Commands added: 1                          │
        │     └─ ✓ Complete (0.4ms)                          │
        │                                                     │
        │ [3] SubgradeWorker (Paint foundation)              │
        │     ├─ Bounds: Y=0.00→0.20m                       │
        │     ├─ Material: subgrade (ER=10)                  │
        │     ├─ Commands added: 2 (material + box)         │
        │     └─ ✓ Complete (1.2ms)                          │
        │                                                     │
        │ [4] FormationWorker (Paint transition)             │
        │     ├─ Bounds: Y=0.20→0.30m                       │
        │     ├─ Material: formation (ER=10)                 │
        │     ├─ Commands added: 2                          │
        │     └─ ✓ Complete (1.1ms)                          │
        │                                                     │
        │ [5] BallastWorker (Paint ballast)                  │
        │     ├─ Bounds: Y=0.30→0.55m                       │
        │     ├─ Material: ballast_rock (ER=5)              │
        │     ├─ Commands added: 2                          │
        │     └─ ✓ Complete (0.9ms)                          │
        │                                                     │
        │ [6] GranularMatrixWorker (Paint rocks+fouling)     │
        │     ├─ Ballast region: Y=0.30→0.55m              │
        │     ├─ Step 1: Pack rocks                         │
        │     │   ├─ Algorithm: shang-chu                    │
        │     │   ├─ Generated: 85 circles                   │
        │     │   └─ Time: 15.3s                             │
        │     ├─ Step 2: Classify rocks                     │
        │     │   ├─ Threshold: 4.0mm                        │
        │     │   ├─ Rocks: 82 (≥ 4mm)                       │
        │     │   └─ Fines: 3 (< 4mm)                        │
        │     ├─ Step 3: Gravity settle                     │
        │     │   └─ Time: 2.1ms                             │
        │     ├─ Step 4: Triangulate rocks                  │
        │     │   ├─ Triangles per rock: 18 avg             │
        │     │   ├─ Total triangles: 1476                   │
        │     │   └─ Time: 145ms                             │
        │     ├─ Step 5: Paint fouling                      │
        │     │   ├─ PVC target: 50%                         │
        │     │   ├─ Fouling height: 0.125m                 │
        │     │   ├─ Fouling Y: 0.30→0.425m                │
        │     │   └─ Time: 0.3ms                             │
        │     ├─ Step 6: Calculate metadata                 │
        │     │   ├─ Measured PVC: 49.8% ✓                  │
        │     │   ├─ Achieved density: 0.428                │
        │     │   ├─ FI_class: F                             │
        │     │   └─ Time: 12ms                              │
        │     └─ ✓ Complete (15.6s)                          │
        │                                                     │
        │ [7] AntennaWorker (Place antenna)                  │
        │     ├─ TX position: (1.124, 1.05, 0.00660)        │
        │     ├─ RX position: (1.174, 1.05, 0.00660)        │
        │     ├─ Frequency: 400 MHz                          │
        │     ├─ Commands added: 3                          │
        │     └─ ✓ Complete (0.5ms)                          │
        │                                                     │
        │ [8] AssemblerWorker (Validate)                     │
        │     ├─ Geometry commands: 1483                     │
        │     ├─ Material definitions: 5                     │
        │     ├─ Validation ✓                                │
        │     │   ├─ Materials unique: ✓                     │
        │     │   ├─ Geometry valid: ✓                       │
        │     │   ├─ Domain adequate: ✓                      │
        │     │   └─ No conflicts: ✓                         │
        │     └─ ✓ Complete (8ms)                            │
        │                                                     │
        │ ═══════════════════════════════════════════════    │
        │ TOTAL TIME: 15.8 seconds                          │
        │ Output: s_00000.in (2.3 KB, 1487 lines)           │
        │ Status: ✓ SUCCESS                                  │
        └─────────────────────────────────────────────────────┘
        """
        pass
```

---

## 7. Machine-Readable Metadata (JSON)

### 7.1 Detailed Scene Metadata

```json
{
  "scene_metadata": {
    "generation_timestamp": "2024-06-05T10:35:42Z",
    "generator_version": "1.2.0",
    "configuration": {
      "domain": {
        "x_meters": 2.248,
        "y_meters": 3.199,
        "z_meters": 0.0132,
        "units": "meters",
        "interpretation": "Domain dimensions for FDTD simulation"
      },
      "discretization": {
        "dx_meters": 0.0132,
        "dy_meters": 0.0132,
        "dz_meters": 0.0132,
        "wavelength_at_400mhz": 0.75,
        "lambda_over_10": 0.075,
        "compliance": "✓ FDTD Rule 1 satisfied (dx ≤ λ/10)"
      },
      "antenna": {
        "frequency_mhz": 400,
        "tx_position_meters": [1.124, 1.05, 0.00660],
        "rx_position_meters": [1.174, 1.05, 0.00660],
        "tx_rx_offset_meters": 0.05,
        "antenna_type": "bistatic"
      },
      "layers": {
        "subgrade": {
          "y_min_meters": 0.0,
          "y_max_meters": 0.2,
          "thickness_meters": 0.2,
          "material": "subgrade",
          "permittivity": 10.0,
          "interpretation": "Natural soil foundation"
        },
        "formation": {
          "y_min_meters": 0.2,
          "y_max_meters": 0.3,
          "thickness_meters": 0.1,
          "material": "formation",
          "permittivity": 10.0,
          "interpretation": "Transition/subballast layer"
        },
        "ballast": {
          "y_min_meters": 0.3,
          "y_max_meters": 0.55,
          "thickness_meters": 0.25,
          "material_background": "ballast_rock",
          "permittivity_background": 5.0,
          "interpretation": "Railway aggregate with fouling"
        },
        "air": {
          "y_min_meters": 0.55,
          "y_max_meters": 1.15,
          "thickness_meters": 0.6,
          "material": "free_space",
          "permittivity": 1.0,
          "interpretation": "Free space above ballast, antenna zone"
        }
      }
    },
    "fouling_parameters": {
      "pvc_target_percent": 50.0,
      "pvc_measured_percent": 48.7,
      "fouling_depth_meters": 0.125,
      "fouling_y_min_meters": 0.3,
      "fouling_y_max_meters": 0.425,
      "moisture_content": 0.1,
      "fouling_permittivity": 8.3,
      "fouling_conductivity_siemens_per_meter": 1.2,
      "interpretation": "50% of ballast voids filled with moisture-saturated fines"
    },
    "rock_distribution": {
      "total_rocks": 82,
      "rocks_above_fouling": 42,
      "rocks_below_fouling": 40,
      "packing_algorithm": "shang-chu",
      "packing_time_seconds": 15.3,
      "average_radius_meters": 0.018,
      "interpretation": "82 angular aggregates, bottom 40 covered by fouling paint"
    },
    "physical_interpretation": {
      "scenario": "Railway ballast fouling assessment",
      "fouling_level": "F (Fouled)",
      "expected_signal_characteristics": {
        "attenuation": "Moderate",
        "bandwidth": "Narrowed",
        "pulse_width": "Widened",
        "reflections": "Smeared"
      },
      "use_case": "Detect fouling via EM wave attenuation and dispersion"
    }
  }
}
```

---

## 8. Summary Table: Interpretability Enhancements

| Dimension | Current State | Proposed Enhancement | Impact |
|-----------|---------------|----------------------|--------|
| **Visual** | ASCII diagrams | Interactive HTML dashboard | Users understand geometry immediately |
| **Code** | Generic names | Semantic naming + type hints | Code is self-documenting |
| **Config** | Raw parameters | Semantic interpretation + what-if | Users understand implications |
| **Validation** | Generic errors | Rich, contextual messages | Users know how to fix issues |
| **Metadata** | Bare numbers | Physical interpretation + units | Results are meaningful |
| **Execution** | Silent run | Detailed trace log | Users understand what happened |
| **Output** | Raw .in file | Annotated .in + HTML report | Clear what each line means |

---

## Implementation Priority

1. **High Impact, Low Effort:**
   - Rich error messages ✓ Easy to implement
   - Semantic variable naming ✓ Refactor over time
   - Annotated .in files ✓ Template-based
   
2. **High Impact, Medium Effort:**
   - Execution tracing ✓ Add logging throughout
   - JSON metadata ✓ Serialize checkpoint
   - Configuration interpreter ✓ Analysis class

3. **Nice-to-Have:**
   - Interactive HTML dashboard ✓ Web UI project
   - Parameter sensitivity analysis ✓ Utility class

---

These enhancements would transform the system from a working tool into a **transparent, self-documenting, educational instrument** that helps users understand not just *what* the code does, but *why* and *what it means physically*. 🎨📚


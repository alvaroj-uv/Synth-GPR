"""
LabWorker: Simulates a physical laboratory analysis of the scene geometry.

Performs Sieve Analysis on the Granular Material (Ballast + Fouling)
to calculate the Selig & Waters Fouling Index (FI) from first principles.

References:
- Selig, E. T., & Waters, J. M. (1994). Track Geotechnology and Substructure Management.
"""

import numpy as np
from typing import List, Dict, Any
from .worker import Worker, SceneCheckpoint
from .constants import PC, MC
import math
import json

class LabWorker(Worker):
    name = "LabWorker"
    
    def execute(self, scene: SceneCheckpoint, params: Dict[str, Any], materials: Any, tools: Any) -> None:
        """
        Executes a Virtual Sieve Analysis on a specific horizontal layer (Horizontal Slice).
        
        1. Define Sampling Layer (default: Bottom 15cm where fouling settles).
        2. Collect Rock Area instersecting this layer.
        3. Calculate Local Porosity & Fouling.
        4. Simulates sieving (>4.75mm and <0.075mm).
        5. Calculates and logs FI.
        """
        print(f"[{self.name}] Starting Virtual Sieve Analysis (Horizontal Sampling)...")
        
        # 1. Define Sampling Layer
        # BallastWorker writes ballast bounds to the work_order blackboard, not to
        # scene.metadata, so prefer the blackboard with scene.metadata as fallback.
        ballast_bottom = scene.metadata.get('ballast_bottom_y', 0.5)
        ballast_thickness = scene.metadata.get('ballast_thickness', 0.4)
        if scene.work_order:
            ballast_bottom    = scene.work_order.get('ballast_bottom_y',  ballast_bottom)
            ballast_thickness = scene.work_order.get('ballast_thickness', ballast_thickness)
        ballast_top = ballast_bottom + ballast_thickness
        if scene.work_order:
            ballast_top = scene.work_order.get('ballast_top_y', ballast_top)
        
        #  1. Get Domain and Layer Info
        # Get domain_x with proper fallback
        domain_x = scene.config.domain_x
        if scene.work_order and hasattr(scene.work_order, '_work_order'):
            typed_params = scene.work_order._work_order.typed_params
            domain_x = typed_params.domain_x or domain_x
        elif scene.work_order and hasattr(scene.work_order, 'typed_params'):
            typed_params = scene.work_order.typed_params
            domain_x = typed_params.domain_x or domain_x
        
        # Get layer height
        layer_height = PC.STANDARD_LAYER_HEIGHT  # Default 15cm sampling layer
        if scene.work_order:
            layer_height = scene.work_order.get('lab_layer_height', layer_height)
             
        y_min = ballast_bottom
        y_max = ballast_bottom + layer_height
        
        layer_area_mm2 = (domain_x * PC.MM_TO_M) * (layer_height * PC.MM_TO_M)
        
        print(f"[{self.name}] Sampling Layer: Y=[{y_min:.3f}, {y_max:.3f}] (H={layer_height*100:.1f}cm)")

        # 2. Collect Rock Area Intersecting Layer
        if not scene.rock_positions:
            print(f"[{self.name}] No rocks found. FI=0.")
            scene.metadata['Lab_FI'] = 0.0
            scene.metadata['Lab_Class'] = "C"
            return

        total_rock_area_mm2 = 0.0
        
        # Vectorized intersection (or loop if simple circles)
        # Circle-Rectangle Intersection (Horizontal Strip)
        # Area of circle segment within strip.
        
        for rock in scene.rock_positions:
            # Circle Center (rx, ry), Radius r
            rock_center_x, rock_center_y = rock.x, rock.y
            radius = rock.radius
            
            # Quick Bounding Box Check
            if (rock_center_y + radius) < y_min or (rock_center_y - radius) > y_max:
                continue # Completely outside
                
            # It intersects or is inside.
            # Calculate intersection area with strip [y_min, y_max]
            area = self._circle_strip_intersection(rock_center_x, rock_center_y, radius, y_min, y_max)
            total_rock_area_mm2 += (area * 1e6) # m2 -> mm2

        # 3. Calculate Local Porosity
        if layer_area_mm2 <= 0:
            local_porosity = 1.0
        else:
            local_porosity = 1.0 - (total_rock_area_mm2 / layer_area_mm2)
            
        local_porosity = max(0.0, min(1.0, local_porosity))
        
        print(f"[{self.name}] Layer Stats: RockArea={total_rock_area_mm2/1e6:.4f}m2, Porosity={local_porosity:.3f}")

        # 4. Determine Fouling in this Layer
        # PVC is Global Volume Fraction. 
        # But FoulingWorker distributes it: Settled Layer (Bottom) + Dispersed (Top).
        # We need to know how much fouling is ACTUALLY in this layer.
        
        # Retrieve Fouling Parameters
        pvc = scene.metadata.get('pvc', 0.0)
        
        if pvc <= 0:
             scene.metadata['Lab_FI'] = 0.0
             scene.metadata['Lab_Class'] = "C"
             return

        # Fouling Logic Reconstruction (Simplify or Query?)
        # FoulingWorker uses: fouling_height = ballast_thickness * (pvc/100)
        # Settled Fraction = 0.7 * fouling_height (at bottom)
        # Dispersed = 0.3 * fouling_height (above settled)
        
        ballast_thickness = scene.metadata.get('ballast_thickness', 0.4)
        pvc_fraction = min(max(pvc, 0), 100) / 100.0
        fouling_height_total = ballast_thickness * pvc_fraction
        
        # Use config for settled fraction, default from constants
        settled_fraction = getattr(scene.config, 'fouling_settled_fraction', PC.FOULING_SETTLED_FRACTION)
        settled_h = fouling_height_total * settled_fraction
        
        # We assume Fouling Material fills 100% of VOIDS up to settled_h
        # And fills "dispersed" fraction of voids above that?
        # Actually FoulingWorker logic:
        # Settled Layer: Fills voids 100% from start_y to start_y + settled_h.
        # Dispersed: Fills partial voids above.
        
        # Calculate Fouling Area in the Strip
        # Intersection of Strip [y_min, y_max] with Settled Zone [ballast_bottom, ballast_bottom + settled_h]
        
        settled_top = ballast_bottom + settled_h
        
        # Intersection height between Strip and Settled Zone
        # Strip is [y_min, y_max]
        # Settled is [ballast_bottom, settled_top]
        hydro_min = max(y_min, ballast_bottom)
        hydro_max = min(y_max, settled_top)
        
        settled_overlap_h = max(0.0, hydro_max - hydro_min)
        
        # Fouling Area from Settled Part = Overlap_H * Width * LocalPorosity (Approx)
        # (Assuming porosity is uniform-ish verticaly, or we recount rock area just for this part?)
        # For simplicity, use Average Local Porosity of the strip for the whole strip calculation.
        
        fouling_area_settled = (settled_overlap_h * domain_x * 1000 * 1000) * local_porosity
        
        # Dispersed? (Ignored for "Sampling at Bottom" usually, or simplified)
        # If we sample only the bottom 15cm, and settled layer is often > 15cm for high PVC.
        # If PVC is low, settled layer < 15cm. Then we start seeing clean ballast above.
        # So Fouling Area is limited by the Settled Height.
        
        # Does Dispersed contribute?
        # Dispersed particles are "dust".
        # Let's count them if we want high precision, but Settled is the dominant mass.
        # Let's assume Dispersed adds negligible mass for Sieve Analysis compared to the "Mud/Sand" layer.
        # Or add if needed.
        
        total_fouling_area_mm2 = fouling_area_settled
        
        # Synthesize Fine Fraction using Standard PSD Curve
        standard_fouling_psd = [
            (PC.SIEVE_NO4, 100.0),   # 4.75mm
            (PC.SIEVE_NO10, 80.0),   # 2.00mm
            (PC.SIEVE_NO40, 50.0),   # 0.425mm
            (PC.SIEVE_NO200, 30.0),  # 0.075mm (Fines content)
            (0.002, 5.0)             # Clay fraction
        ]
        
        from src.physics import get_percent_passing
        
        # Calculate Fines Content of the *Fouling Phase* itself
        p200_fraction_foul = get_percent_passing(PC.SIEVE_NO200, standard_fouling_psd) / 100.0
        p4_fraction_foul = get_percent_passing(PC.SIEVE_NO4, standard_fouling_psd) / 100.0
        
        area_fines = total_fouling_area_mm2 * p200_fraction_foul
        
        # 6. Perform Sieve Logic (Selig & Waters FI)
        # Total Sample Area = Rock Area (in strip) + Fouling Area (in strip)
        total_sample_area = total_rock_area_mm2 + total_fouling_area_mm2
        
        if total_sample_area <= 0:
            P4, P200, FI = 0, 0, 0
        else:
            # P4: % < 4.75mm (All Fouling)
            # For fouling phase, this is determined by the PSD curve (usually 100%).
            # Rocks are assumed > 4.75mm (retained).
            p4_area = total_fouling_area_mm2 * p4_fraction_foul
            p200_area = area_fines
            
            P4 = (p4_area / total_sample_area) * 100.0
            P200 = (p200_area / total_sample_area) * 100.0
            FI = P4 + P200
        
        # 7. Log Results
        scene.metadata['Lab_P4'] = P4
        scene.metadata['Lab_P200'] = P200
        scene.metadata['Lab_FI'] = FI
        scene.metadata['Lab_Porosity'] = local_porosity
        
        # --- NEW: Calculate Full PSD Curve ---
        # Define standard sieve set (mm)
        sieves = [
            63.0, 53.0, 37.5, 26.5, 19.0, 13.2, 9.5, 4.75, # Coarse (Gravel/Rock)
            2.36, 1.18, 0.600, 0.425, 0.300, 0.150, 0.075, # Sand
            0.002 # Clay/Silt boundary (virtual)
        ]
        
        psd_data = [] # List of (size_mm, percent_passing)
        
        for size_mm in sieves:
            # 1. Calculate Mass Passing this sieve
            
            # Rock Contribution:
            # Assume rocks are single-size particles defined by their radius? 
            # Or use the generated rock sizes?
            # Ideally we check each rock's diameter (2*radius) against the sieve size.
            pass_rock_area = 0.0
            for rock in scene.rock_positions:
                 # Check if this rock is in the layer (reuse logic or simplify)
                rock_center_y = rock.y
                radius = rock.radius
                diameter = 2 * radius * 1000 # m -> mm
                
                # Check layer intersection (Basic check for speed)
                if (rock_center_y + radius) < y_min or (rock_center_y - radius) > y_max:
                    continue

                if diameter < size_mm:
                    # It passes!
                    # Calculate its area contribution to the strip
                    area = self._circle_strip_intersection(rock.x, rock.y, radius, y_min, y_max)
                    pass_rock_area += (area * 1e6)
            
            # Fouling Contribution:
            # Fouling is "fines" so we use its internal PSD
            # size_mm vs standard_fouling_psd
            percent_foul_passing = get_percent_passing(size_mm / 1000.0, [ (d, p) for d, p in standard_fouling_psd])
            pass_foul_area = total_fouling_area_mm2 * (percent_foul_passing / 100.0)
            
            total_passing = pass_rock_area + pass_foul_area
            percent_total_passing = (total_passing / total_sample_area) * 100.0 if total_sample_area > 0 else 100.0
            
            psd_data.append((size_mm, percent_total_passing))
            
        # Serialize to JSON string for metadata
        scene.metadata['Lab_PSD'] = json.dumps(psd_data)

        
        from src.physics import classify_fouling_index
        fi_class = classify_fouling_index(FI)
        scene.metadata['Lab_Class'] = fi_class

        fractions = self._compute_phase_fractions(scene, ballast_bottom, ballast_top, domain_x)
        scene.metadata.update(fractions)

        print(f"[{self.name}] Result (H={layer_height:.2f}m): FI={FI:.1f} (P4={P4:.1f}%, P200={P200:.1f}%) -> Class: {fi_class}")
        print(f"[{self.name}] MC Phase Fractions: Rock={fractions['mc_rock_fraction']:.3f}, "
              f"Fouling={fractions['mc_fouling_fraction']:.3f}, "
              f"Subgrade={fractions['mc_subgrade_fraction']:.3f}, "
              f"Formation={fractions['mc_formation_fraction']:.3f}, "
              f"Void={fractions['mc_void_fraction']:.3f} | "
              f"PVC_measured={fractions['mc_pvc_measured']:.1f}% (requested={pvc:.1f}%)")

    def _compute_phase_fractions(
        self,
        scene: SceneCheckpoint,
        ballast_bottom: float,
        ballast_top: float,
        domain_x: float,
        n_samples: int = 50_000,
    ) -> Dict[str, float]:
        """
        Monte Carlo estimation of phase fractions over the full solid domain.

        Samples n_samples random points uniformly in [0, domain_x] × [0, ballast_top]
        — the entire scene below the antenna air region. Each point is classified as:
          - rock       : inside a ballast rock cylinder
          - fouling    : inside a fouling box/cylinder, not rock
          - subgrade   : inside a subgrade box, not rock/fouling
          - formation  : inside a formation box, not rock/fouling/subgrade
          - void       : pore space (unoccupied by any solid)

        PVC is computed from ballast-layer samples only so it remains comparable
        to the requested PVC label:
            mc_pvc_measured = fouling_in_ballast / (fouling_in_ballast + void_in_ballast) × 100
        """
        from .gpr_commands import BoxCommand, CylinderCommand

        # Full solid domain: y ∈ [0, ballast_top] excludes the antenna air above ballast
        xs = np.random.uniform(0.0, domain_x, n_samples)
        ys = np.random.uniform(0.0, ballast_top, n_samples)

        # --- Rock phase (vectorized broadcast) ---
        in_rock = np.zeros(n_samples, dtype=bool)
        if scene.rock_positions:
            rx  = np.array([r.x      for r in scene.rock_positions])
            ry  = np.array([r.y      for r in scene.rock_positions])
            rr2 = np.array([r.radius for r in scene.rock_positions]) ** 2
            dx = xs[:, np.newaxis] - rx
            dy = ys[:, np.newaxis] - ry
            in_rock = np.any(dx**2 + dy**2 < rr2, axis=1)

        # --- Fouling phase ---
        fouling_cmds  = [c for c in scene.geometry
                         if getattr(c, 'material', None) == MC.FOULING]
        fouling_boxes = [c for c in fouling_cmds if isinstance(c, BoxCommand)]
        fouling_cyls  = [c for c in fouling_cmds if isinstance(c, CylinderCommand)]

        in_fouling = np.zeros(n_samples, dtype=bool)
        for box in fouling_boxes:
            in_fouling |= (xs >= box.x1) & (xs <= box.x2) & (ys >= box.y1) & (ys <= box.y2)
        if fouling_cyls:
            fx  = np.array([c.x1     for c in fouling_cyls])
            fy  = np.array([c.y1     for c in fouling_cyls])
            fr2 = np.array([c.radius for c in fouling_cyls]) ** 2
            dx = xs[:, np.newaxis] - fx
            dy = ys[:, np.newaxis] - fy
            in_fouling |= np.any(dx**2 + dy**2 < fr2, axis=1)
        in_fouling &= ~in_rock

        # --- Formation phase (placed after subgrade in gprMax, so takes priority over it) ---
        formation_boxes = [c for c in scene.geometry
                           if isinstance(c, BoxCommand) and getattr(c, 'material', None) == MC.FORMATION]
        in_formation = np.zeros(n_samples, dtype=bool)
        for box in formation_boxes:
            in_formation |= (xs >= box.x1) & (xs <= box.x2) & (ys >= box.y1) & (ys <= box.y2)
        in_formation &= ~in_rock & ~in_fouling

        # --- Subgrade phase (placed first, lowest priority — formation overwrites it) ---
        subgrade_boxes = [c for c in scene.geometry
                          if isinstance(c, BoxCommand) and getattr(c, 'material', None) == MC.SUBGRADE]
        in_subgrade = np.zeros(n_samples, dtype=bool)
        for box in subgrade_boxes:
            in_subgrade |= (xs >= box.x1) & (xs <= box.x2) & (ys >= box.y1) & (ys <= box.y2)
        in_subgrade &= ~in_rock & ~in_fouling & ~in_formation

        # --- Void (pore space not occupied by any solid) ---
        in_void = ~in_rock & ~in_fouling & ~in_subgrade & ~in_formation

        rock_frac      = float(np.mean(in_rock))
        fouling_frac   = float(np.mean(in_fouling))
        subgrade_frac  = float(np.mean(in_subgrade))
        formation_frac = float(np.mean(in_formation))
        void_frac      = float(np.mean(in_void))

        # PVC restricted to the ballast layer so it matches the requested PVC label
        in_ballast = (ys >= ballast_bottom) & (ys <= ballast_top)
        ballast_n = int(np.sum(in_ballast))
        if ballast_n > 0:
            fouling_in_ballast = float(np.sum(in_fouling & in_ballast)) / ballast_n
            void_in_ballast    = float(np.sum(in_void    & in_ballast)) / ballast_n
            void_total = fouling_in_ballast + void_in_ballast
            mc_pvc = (fouling_in_ballast / void_total * 100.0) if void_total > 0.0 else 0.0
        else:
            mc_pvc = 0.0

        return {
            'mc_rock_fraction':      rock_frac,
            'mc_fouling_fraction':   fouling_frac,
            'mc_subgrade_fraction':  subgrade_frac,
            'mc_formation_fraction': formation_frac,
            'mc_void_fraction':      void_frac,
            'mc_pvc_measured':       mc_pvc,
        }

    def _circle_strip_intersection(self, center_x: float, center_y: float, radius: float, y_min: float, y_max: float) -> float:
        """
        Calculate the area of a circle (center_x, center_y, radius) intersection with a horizontal strip y_min <= y <= y_max.
        """
        # Area = Area_below(y_max) - Area_below(y_min)
        return self._circular_segment_area_below(center_x, center_y, radius, y_max) - \
               self._circular_segment_area_below(center_x, center_y, radius, y_min)

    def _circular_segment_area_below(self, center_x: float, center_y: float, radius: float, horizontal_line_y: float) -> float:
        """
        Area of circle below horizontal line y = horizontal_line_y.
        """
        # Relative height from center
        vertical_distance = horizontal_line_y - center_y
        
        if vertical_distance >= radius:
            return math.pi * radius**2 # All of it
        if vertical_distance <= -radius:
            return 0.0 # None of it
            
        # Area = r^2 * (pi/2 + arcsin(d/r)) + d * sqrt(r^2 - d^2)
        
        angle_term = math.pi/2 + math.asin(vertical_distance/radius)
        linear_term = vertical_distance * math.sqrt(radius**2 - vertical_distance**2)
        return (radius**2) * angle_term + linear_term

    def quality_check(self, scene: SceneCheckpoint) -> List[str]:
        return []

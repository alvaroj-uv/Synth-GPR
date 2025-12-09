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
import math

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
        # Default: Bottom 15cm (0.15m) of ballast.
        ballast_bottom = scene.metadata.get('ballast_bottom_y', 0.5) # Default generic
        layer_height = params.get('sample_height', 0.15) # 15cm default
        
        y_min = ballast_bottom
        y_max = ballast_bottom + layer_height
        
        # Domain Width
        domain_x = scene.metadata.get('domain_x', 1.0) # Fallback
        # If not in metadata, try config/workorder
        if 'domain_x' not in scene.metadata and scene.work_order:
             domain_x = scene.work_order.get_input('domain_x', 1.0)
             
        layer_area_mm2 = (domain_x * 1000.0) * (layer_height * 1000.0)
        
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
            rx, ry = rock.x, rock.y
            r = rock.radius
            
            # Quick Bounding Box Check
            if (ry + r) < y_min or (ry - r) > y_max:
                continue # Completely outside
                
            # It intersects or is inside.
            # Calculate intersection area with strip [y_min, y_max]
            area = self._circle_strip_intersection(rx, ry, r, y_min, y_max)
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
        
        # Use config for settled fraction, default to 0.7 if not found
        settled_fraction = getattr(scene.config, 'fouling_settled_fraction', 0.7)
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
        
        # 5. Synthesize Fine Fraction (Silt vs Sand) -> Use Standard PSD Curve
        # Define Standard Fouling PSD (Moderately Fouled Ballast curve)
        # Pairs: (Diameter mm, Percent Passing %)
        # D=4.75mm (No.4): 100% passing (All fouling is <4.75mm by def)
        # D=2.00mm (No.10): 80%
        # D=0.425mm (No.40): 50%
        # D=0.075mm (No.200): 30% (Fines content)
        standard_fouling_psd = [
            (4.75, 100.0),
            (2.0, 80.0),
            (0.425, 50.0),
            (0.075, 30.0), # Matches original assumption
            (0.002, 5.0)   # Clay fraction
        ]
        
        from src.physics import get_percent_passing
        
        # Calculate Fines Content of the *Fouling Phase* itself
        # P200_foul = % of Fouling Material passing 0.075mm
        p200_fraction_foul = get_percent_passing(0.075, standard_fouling_psd) / 100.0
        
        # P4_foul = % of Fouling Material passing 4.75mm (Should be 100%)
        p4_fraction_foul = get_percent_passing(4.75, standard_fouling_psd) / 100.0
        
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
        
        from src.physics import classify_fouling_index
        fi_class = classify_fouling_index(FI)
        scene.metadata['Lab_Class'] = fi_class
        
        print(f"[{self.name}] Result (H={layer_height:.2f}m): FI={FI:.1f} (P4={P4:.1f}%, P200={P200:.1f}%) -> Class: {fi_class}")

    def _circle_strip_intersection(self, cx: float, cy: float, r: float, y_min: float, y_max: float) -> float:
        """
        Calculate the area of a circle (cx, cy, r) intersection with a horizontal strip y_min <= y <= y_max.
        """
        # Area = Area_below(y_max) - Area_below(y_min)
        return self._circular_segment_area_below(cx, cy, r, y_max) - \
               self._circular_segment_area_below(cx, cy, r, y_min)

    def _circular_segment_area_below(self, cx: float, cy: float, r: float, h_line: float) -> float:
        """
        Area of circle below horizontal line y = h_line.
        """
        # Relative height from center
        d = h_line - cy
        
        if d >= r:
            return math.pi * r**2 # All of it
        if d <= -r:
            return 0.0 # None of it
            
        # Area = r^2 * (pi/2 + arcsin(d/r)) + d * sqrt(r^2 - d^2)
        # Check: d=0 -> r^2 * pi/2. Correct (Half circle).
        # d=r -> r^2 * (pi/2 + pi/2) = pi*r^2. Correct.
        # d=-r -> r^2 * (pi/2 - pi/2) = 0. Correct.
        
        # Note: numpy usage
        # Use simple scalar math if single call, else np is fine.
        # Since loop is explicit, scalar math `math` is faster/safer inside loop than np broadcasting overhead for 1 item.
        
        msg_val = math.pi/2 + math.asin(d/r)
        term2 = d * math.sqrt(r**2 - d**2)
        return (r**2) * msg_val + term2

    def quality_check(self, scene: SceneCheckpoint) -> List[str]:
        return []

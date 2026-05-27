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
from .constants import PC, MC, PHC
from .physics import circle_strip_intersection
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
            
        # Dynamically adjust ballast_top to the highest settled rock to avoid 
        # sampling empty air above the gravity-settled structure.
        if scene.rock_positions:
            physical_top = max(r.y + r.radius for r in scene.rock_positions)
            ballast_top = min(ballast_top, physical_top)
        
        #  1. Get Domain and Layer Info
        # Get domain_x with proper fallback
        domain_x = scene.config.domain_x
        if scene.work_order and hasattr(scene.work_order, '_work_order'):
            typed_params = scene.work_order._work_order.typed_params
            domain_x = typed_params.domain_x or domain_x
        elif scene.work_order and hasattr(scene.work_order, 'typed_params'):
            typed_params = scene.work_order.typed_params
            domain_x = typed_params.domain_x or domain_x
        
        # Primary sieve: full ballast column (Selig & Waters bulk sample)
        y_min = ballast_bottom
        y_max = ballast_top

        layer_area_mm2 = (domain_x * PC.MM_TO_M) * ((y_max - y_min) * PC.MM_TO_M)

        # Secondary sieve: bottom 15 cm strip (local severity indicator)
        local_strip_top = ballast_bottom + PC.STANDARD_LAYER_HEIGHT

        print(f"[{self.name}] Sampling Layer: Y=[{y_min:.3f}, {y_max:.3f}] (full column, H={(y_max-y_min)*100:.1f}cm)")

        # 2. Collect Rock Area Intersecting Layer
        if not scene.rock_positions:
            print(f"[{self.name}] No rocks found. FI=0.")
            scene.metadata['Lab_FI'] = 0.0
            scene.metadata.update({'Lab_LDCP_FH': 0.0, 'Lab_LDCP_qs_mean': 0.0})
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
            area = circle_strip_intersection(rock_center_x, rock_center_y, radius, y_min, y_max)
            total_rock_area_mm2 += (area * 1e6) # m2 -> mm2

        # 3. Calculate Local Porosity
        if layer_area_mm2 <= 0:
            local_porosity = 1.0
        else:
            local_porosity = 1.0 - (total_rock_area_mm2 / layer_area_mm2)
            
        local_porosity = max(0.0, min(1.0, local_porosity))
        
        print(f"[{self.name}] Layer Stats: RockArea={total_rock_area_mm2/1e6:.4f}m2, Porosity={local_porosity:.3f}")

        # 4. Measure Fouling Area in Strip Directly from Placed Geometry
        from .gpr_commands import BoxCommand, CylinderCommand
        fouling_mats = {MC.FOULING, MC.FOULING_DENSE}
        fouling_boxes = [c for c in scene.geometry
                         if isinstance(c, BoxCommand) and getattr(c, 'material', None) in fouling_mats]
        fouling_cyls  = [c for c in scene.geometry
                         if isinstance(c, CylinderCommand) and getattr(c, 'material', None) in fouling_mats]

        if not fouling_boxes and not fouling_cyls:
            scene.metadata['Lab_FI'] = 0.0
            scene.metadata['Lab_FI_local'] = 0.0
            fractions = self._compute_phase_fractions(scene, ballast_bottom, ballast_top, domain_x)
            scene.metadata.update(fractions)
            scene.metadata['ballast_bottom_y'] = round(ballast_bottom, 3)
            scene.metadata['ballast_top_y'] = round(ballast_top, 3)
            self._run_ldcp_profiler(scene, ballast_bottom, ballast_top, domain_x)
            return

        pvc = scene.metadata.get('pvc', 0.0)

        # Box geometry: solid fills displaced by rocks → scale by local_porosity
        total_fouling_area_mm2 = 0.0
        for box in fouling_boxes:
            overlap_h = max(0.0, min(box.y2, y_max) - max(box.y1, y_min))
            total_fouling_area_mm2 += (overlap_h * domain_x * 1e6) * local_porosity

        # Cylinder geometry: placed in voids already → no porosity correction needed
        for cyl in fouling_cyls:
            area = circle_strip_intersection(cyl.x1, cyl.y1, cyl.radius, y_min, y_max)
            total_fouling_area_mm2 += area * 1e6
        
        # Fouling PSD: "standard" (coarser) or "a4" (Benedetto et al. 2016, silty A4 soil)
        psd_type = getattr(scene.config, 'fouling_psd_type', 'standard')
        if psd_type == 'a4':
            standard_fouling_psd = [
                (PC.SIEVE_NO4,   100.0),  # 4.75mm: 100%
                (PC.SIEVE_NO10,  99.6),   # 2.00mm: 99.6%
                (PC.SIEVE_NO40,  99.4),   # 0.425mm: 99.4%
                (PC.SIEVE_NO200, 84.7),   # 0.075mm: 84.7% (silty A4 material)
                (0.002,          15.0),   # Clay fraction (estimated)
            ]
        else:
            standard_fouling_psd = [
                (PC.SIEVE_NO4,   100.0),  # 4.75mm
                (PC.SIEVE_NO10,  80.0),   # 2.00mm
                (PC.SIEVE_NO40,  50.0),   # 0.425mm
                (PC.SIEVE_NO200, 30.0),   # 0.075mm (Fines content)
                (0.002,          5.0),    # Clay fraction
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

        # Secondary: bottom-strip FI (local severity at the most fouled zone)
        local_rock_area_mm2 = sum(
            circle_strip_intersection(r.x, r.y, r.radius, y_min, local_strip_top) * 1e6
            for r in scene.rock_positions
            if not ((r.y + r.radius) < y_min or (r.y - r.radius) > local_strip_top)
        )
        local_strip_porosity = max(0.0, min(1.0, 1.0 - local_rock_area_mm2 /
                                             max((domain_x * PC.MM_TO_M) * (PC.STANDARD_LAYER_HEIGHT * PC.MM_TO_M), 1.0)))
        local_foul_area_mm2 = 0.0
        for box in fouling_boxes:
            overlap_h = max(0.0, min(box.y2, local_strip_top) - max(box.y1, y_min))
            local_foul_area_mm2 += (overlap_h * domain_x * 1e6) * local_strip_porosity
        local_sample = local_rock_area_mm2 + local_foul_area_mm2
        if local_sample > 0:
            local_FI = (local_foul_area_mm2 * p4_fraction_foul / local_sample * 100.0 +
                        local_foul_area_mm2 * p200_fraction_foul / local_sample * 100.0)
        else:
            local_FI = 0.0
        scene.metadata['Lab_FI_local'] = round(local_FI, 2)
        
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
                    area = circle_strip_intersection(rock.x, rock.y, radius, y_min, y_max)
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

        

        # δ = radius / depth-from-ballast-surface (Xie et al. 2010)
        # Detectability threshold: δ < 0.08 → hyperbolic signature fades out
        deltas = []
        for rock in scene.rock_positions:
            depth = ballast_top - rock.y
            if depth > 0:
                deltas.append(rock.radius / depth)
        if deltas:
            scene.metadata['Lab_delta_min'] = round(min(deltas), 4)
            scene.metadata['Lab_delta_max'] = round(max(deltas), 4)
            scene.metadata['Lab_delta_frac_detectable'] = round(
                sum(1 for d in deltas if d >= 0.08) / len(deltas), 3
            )

        fractions = self._compute_phase_fractions(scene, ballast_bottom, ballast_top, domain_x)
        scene.metadata.update(fractions)

        # Log geometry reference bounds
        scene.metadata['ballast_bottom_y'] = round(ballast_bottom, 3)
        scene.metadata['ballast_top_y'] = round(ballast_top, 3)



        self._run_ldcp_profiler(scene, ballast_bottom, ballast_top, domain_x)

        print(f"[{self.name}] Result (full column): FI={FI:.1f} (P4={P4:.1f}%, P200={P200:.1f}%) "
              f"FI_local={local_FI:.1f}")
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

        # --- Fouling phase — painter's algorithm priority ---
        # gprMax render order (last command per voxel wins):
        #   priority-10 box:       FOULING solid box rendered first (background)
        #   priority-20 triangles: rock triangles stamped on top, overwriting fouling
        # Result: rocks override the fouling box in every voxel they occupy.
        _fouling_mats = {MC.FOULING, MC.FOULING_DENSE}
        fouling_cmds  = [c for c in scene.geometry
                         if getattr(c, 'material', None) in _fouling_mats]
        fouling_boxes = [c for c in fouling_cmds if isinstance(c, BoxCommand)]
        fouling_cyls  = [c for c in fouling_cmds if isinstance(c, CylinderCommand)]

        in_fouling_box = np.zeros(n_samples, dtype=bool)
        for box in fouling_boxes:
            in_fouling_box |= (xs >= box.x1) & (xs <= box.x2) & (ys >= box.y1) & (ys <= box.y2)

        in_fouling_cyl = np.zeros(n_samples, dtype=bool)
        if fouling_cyls:
            fx  = np.array([c.x1     for c in fouling_cyls])
            fy  = np.array([c.y1     for c in fouling_cyls])
            fr2 = np.array([c.radius for c in fouling_cyls]) ** 2
            dx  = xs[:, np.newaxis] - fx
            dy  = ys[:, np.newaxis] - fy
            in_fouling_cyl = np.any(dx**2 + dy**2 < fr2, axis=1)

        # Apply render priority:
        in_rock    = in_rock & ~in_fouling_cyl                      # fouling cyls paint over rocks
        in_fouling = in_fouling_cyl | (in_fouling_box & ~in_rock)   # boxes lose to rocks

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

    def _scan_ballast_column(
        self,
        scene: SceneCheckpoint,
        ballast_bottom: float,
        ballast_top: float,
        domain_x: float,
    ):
        """1-D painter's-algorithm scan along domain centreline (x = domain_x / 2).

        Returns (ys, material_labels) as numpy arrays. Same render priority as
        gprMax: boxes applied first, cylinders after; last writer wins per voxel.
        """
        from .gpr_commands import BoxCommand, CylinderCommand

        STEP = PHC.LDCP_STEP_M
        x_probe = domain_x / 2.0
        ys = np.arange(ballast_bottom + STEP / 2.0, ballast_top, STEP)
        n = len(ys)
        if n == 0:
            return ys, np.array([], dtype=object)

        material_labels = np.full(n, "void", dtype=object)
        for cmd in scene.geometry:
            mat = getattr(cmd, 'material', None)
            if mat is None:
                continue
            if isinstance(cmd, BoxCommand):
                if x_probe < cmd.x1 or x_probe > cmd.x2:
                    continue
                mask = (ys >= cmd.y1) & (ys <= cmd.y2)
                material_labels[mask] = mat
            elif isinstance(cmd, CylinderCommand):
                dx2 = (x_probe - cmd.x1) ** 2
                mask = dx2 + (ys - cmd.y1) ** 2 <= cmd.radius ** 2
                material_labels[mask] = mat

        return ys, material_labels

    def _run_ldcp_profiler(
        self,
        scene: SceneCheckpoint,
        ballast_bottom: float,
        ballast_top: float,
        domain_x: float,
    ) -> None:
        """
        Synthetic 1-D LDCP profiler along the domain centreline (x = domain_x / 2).

        Classifies each 1 mm step via the painter's algorithm, assigns a synthetic
        quasi-static point resistance (qs) per material and derives:

          Lab_LDCP_FH      – %FH: % of ballast depth classified as fouling material
          Lab_LDCP_qs_mean – mean synthetic qs across the ballast column (MPa)

        Also triggers clean-thickness computation.
        """
        ys, material_labels = self._scan_ballast_column(
            scene, ballast_bottom, ballast_top, domain_x
        )
        n = len(ys)

        if n == 0:
            scene.metadata.update({'Lab_LDCP_FH': 0.0, 'Lab_LDCP_qs_mean': 0.0})
            return

        is_rock    = np.array([m.startswith("bal_rock") for m in material_labels])
        is_fouling = np.array([m.startswith("bal_foul")  for m in material_labels])
        is_sub     = material_labels == MC.SUBGRADE
        is_form    = material_labels == MC.FORMATION

        qs = np.full(n, PHC.LDCP_QS_VOID)
        qs[is_rock]    = PHC.LDCP_QS_ROCK
        qs[is_fouling] = PHC.LDCP_QS_FOULING
        qs[is_sub]     = PHC.LDCP_QS_SUBGRADE
        qs[is_form]    = PHC.LDCP_QS_FORMATION

        fh_pct  = float(np.mean(is_fouling)) * 100.0
        qs_mean = float(np.mean(qs))

        scene.metadata['Lab_LDCP_FH']      = round(fh_pct, 2)
        scene.metadata['Lab_LDCP_qs_mean'] = round(qs_mean, 2)

        print(f"[{self.name}] LDCP Profile ({n} steps @ 1mm): FH={fh_pct:.1f}%  qs_mean={qs_mean:.1f} MPa")

        self._compute_crim_and_thickness(
            scene, ys, material_labels, ballast_bottom, ballast_top
        )

    def _compute_crim_and_thickness(
        self,
        scene: SceneCheckpoint,
        ys,
        material_labels,
        ballast_bottom: float,
        ballast_top: float,
    ) -> None:
        """Compute clean ballast thickness from 1-D column scan.

        Stores:
          Lab_clean_ballast_mm  – clean ballast thickness: surface to topmost fouling (mm)
        """
        n = len(ys)
        if n == 0:
            return

        is_fouling = np.array([m.startswith("bal_foul")  for m in material_labels])

        # Clean ballast thickness: from ballast_top down to topmost fouling encounter
        fouling_ys = ys[is_fouling]
        if len(fouling_ys) > 0:
            clean_mm = (ballast_top - float(np.max(fouling_ys))) * 1000.0
        else:
            clean_mm = (ballast_top - ballast_bottom) * 1000.0
        scene.metadata['Lab_clean_ballast_mm'] = round(max(0.0, clean_mm), 1)

        print(f"[{self.name}] Clean ballast: {scene.metadata['Lab_clean_ballast_mm']:.0f} mm")

    def quality_check(self, scene: SceneCheckpoint) -> List[str]:
        return []

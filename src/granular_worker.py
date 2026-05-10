from typing import Dict, Any, List
import random
import math

from .worker import Worker, SceneCheckpoint
from .gpr_commands import CylinderCommand, BoxCommand
from .constants import MC, PC
from .physics import classify_pvc
from .rock_model import Rock, PackingBounds
from .rock_packing import GrowthPacking

class GranularMatrixWorker(Worker):
    """
    Unified Mission-Based Granular Matrix generator.
    
    Replaces RockWorker and FoulingWorker when granular_mode=True.
    1. Generates a dense space-filling geometry using GrowthPacking.
    2. Sorts circles by size and position to assign "missions":
       - Rocks (r >= 15mm)
       - Fouling (leftovers, settled bottom-up)
       - Air (remaining leftovers)
    """
    
    name = "GranularMatrixWorker"

    def execute(self, scene: SceneCheckpoint, params: Dict[str, Any], materials: Any, tools: Any) -> None:
        # 1. Resolve geometry bounds
        if scene.coordinate_system:
            from src.domain import Layer
            bounds_obj = scene.coordinate_system.bounds(Layer.BALLAST)
            start_y, top_y = bounds_obj.bottom, bounds_obj.top
        else:
            start_y = scene.metadata.get('ballast_bottom_y', 0.5)
            ballast_thickness = scene.metadata.get('ballast_thickness', 0.4)
            top_y = start_y + ballast_thickness

        domain_x, _, domain_z = scene.get_domain_params()
        
        bounds = PackingBounds(0.0, domain_x, start_y, top_y)
        
        # 2. Get Targets
        if scene.work_order:
            pvc = scene.work_order.get_input('pvc', 0.0)
            moisture = scene.work_order.get_input('moisture', 0.0)
        else:
            pvc = params.get('pvc', 0.0)
            moisture = params.get('moisture', 0.0)

        scene.metadata['pvc'] = pvc
        scene.metadata['moisture'] = moisture

        target_rock_fill = scene.config.rock_packing_target_fill
        r_max = scene.config.rock_radius_max
        min_gap = getattr(scene.config, 'rock_min_gap', 0.0)

        # 3. Master Pack (Geometry Generation)
        # Grow circles from 1.0mm up to r_max to completely fill the space
        print(f"[{self.name}] Running Master GrowthPack...")
        packer = GrowthPacking(place_attempts=500, grow_step=0.001)
        all_circles = packer.generate_rocks(
            bounds=bounds,
            radius_min=0.001, # 1mm minimum grain size
            radius_max=r_max,
            target_fill_ratio=0.85, # Safely below max theoretical ~90%
            max_attempts=scene.config.rock_packing_max_attempts,
            min_gap=min_gap
        )
        
        if not all_circles:
            scene.log_issue(self.name, "packing_failure", "error", "Master pack generated 0 circles.")
            return

        # 4. Mission Assignment
        rock_mat = materials.get_material(MC.BALLAST_ROCK)
        foul_mat = materials.get_material(MC.FOULING, moisture=moisture)
        scene.add_material(rock_mat)
        scene.add_material(foul_mat)
        
        # Split initial pools based on a physical threshold for "rock" vs "fine"
        rock_threshold = getattr(scene.config, 'fouling_particle_size_max', 0.008) * 2 # say >16mm is rock
        
        rock_pool = [c for c in all_circles if c.radius >= rock_threshold]
        void_pool = [c for c in all_circles if c.radius < rock_threshold]

        # A. Assign Rocks
        # Sort largest first so we get big rocks forming the skeleton
        rock_pool.sort(key=lambda c: c.radius, reverse=True)
        
        assigned_rocks = []
        current_rock_area = 0.0
        target_rock_area = bounds.area * target_rock_fill
        
        for c in rock_pool:
            if current_rock_area < target_rock_area:
                assigned_rocks.append(c)
                current_rock_area += math.pi * c.radius**2
            else:
                # Demoted to void pool
                void_pool.append(c)
                
        achieved_density = current_rock_area / bounds.area
        porosity = 1.0 - achieved_density
        
        scene.metadata['achieved_density'] = achieved_density
        scene.metadata['porosity'] = porosity
        scene.metadata['FI_class'] = classify_pvc(pvc, porosity=porosity)

        # B. Assign Fouling
        pvc_fraction = min(max(pvc, 0.0), 100.0) / 100.0
        void_area = bounds.area - current_rock_area
        target_foul_area = void_area * pvc_fraction
        
        assigned_fouling = []
        current_foul_area = 0.0
        
        # Fouling settles to the bottom under gravity
        void_pool.sort(key=lambda c: c.y)
        
        for c in void_pool:
            if current_foul_area < target_foul_area:
                assigned_fouling.append(c)
                current_foul_area += math.pi * c.radius**2
                
        # C. Emit Geometry Commands
        # Instead of drawing thousands of tiny cylinders for the fouling (which causes
        # FDTD grid aliasing and slows down the simulation), we find the highest 
        # point the fouling settled to, draw a solid background box, and stamp the rocks on top.
        
        z_start = scene.config.rock_z_start
        z_end = scene.config.rock_z_end
        
        # Determine the top height of the settled fouling layer
        if assigned_fouling:
            fouling_top_y = max(f.y + f.radius for f in assigned_fouling)
            
            # Draw the homogenized background box for the fouling
            scene.add_geometry(BoxCommand(
                0, start_y, z_start,
                domain_x, fouling_top_y, z_end,
                MC.FOULING
            ))
            print(f"[{self.name}] Fouling settled up to Y = {fouling_top_y:.3f}m")
        
        # Stamp the structural rocks ON TOP of the background box (Painter's Algorithm)
        for r in assigned_rocks:
            scene.add_geometry(CylinderCommand(
                r.x, r.y, z_start, r.x, r.y, z_end,
                r.radius, MC.BALLAST_ROCK
            ))
            scene.add_rock(r) # For visualizer/lab worker
            
        print(f"[{self.name}] Master Pack: {len(all_circles)} total circles.")
        print(f"  -> Assigned Rocks   : {len(assigned_rocks)} (Density: {achieved_density:.3f})")
        print(f"  -> Assigned Fouling : {len(assigned_fouling)} (PVC: {pvc:.1f}%) [Rendered as Box]")
        print(f"  -> Assigned Air     : {len(void_pool) - len(assigned_fouling)}")

    def quality_check(self, scene: SceneCheckpoint) -> List[str]:
        return []

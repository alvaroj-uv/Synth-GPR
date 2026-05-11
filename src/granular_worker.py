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

        # Apply Gravity Settle to assigned rocks to prevent them from floating
        # where tiny "Air" circles used to support them.
        print(f"[{self.name}] Applying Gravity Settle to {len(assigned_rocks)} rocks...")
        assigned_rocks.sort(key=lambda r: r.y) # Sort bottom to top
        settled_rocks = []
        for r in assigned_rocks:
            # Drop until collision
            step = 0.002 # 2mm drop per step
            while r.y - r.radius > start_y:
                # Check collision with settled rocks
                collision = False
                for sr in settled_rocks:
                    dist_sq = (r.x - sr.x)**2 + (r.y - step - sr.y)**2
                    if dist_sq < (r.radius + sr.radius)**2:
                        collision = True
                        break
                if collision:
                    break
                r.y -= step
            settled_rocks.append(r)
            
        assigned_rocks = settled_rocks
                
        achieved_density = current_rock_area / bounds.area
        porosity = 1.0 - achieved_density
        
        scene.metadata['achieved_density'] = achieved_density
        scene.metadata['porosity'] = porosity
        scene.metadata['FI_class'] = classify_pvc(pvc, porosity=porosity)

        # C. Assign Fouling (AFTER Gravity Settle)
        # Because rocks settling reduces the overall volume of the track, 
        # we must recalculate the total available void area to get an accurate PVC.
        if assigned_rocks:
            physical_top = max(r.y + r.radius for r in assigned_rocks)
        else:
            physical_top = top_y
            
        settled_bounds_area = (physical_top - start_y) * domain_x
        settled_void_area = settled_bounds_area - current_rock_area
        
        pvc_fraction = min(max(pvc, 0.0), 100.0) / 100.0
        target_foul_area = settled_void_area * pvc_fraction
        
        z_start = scene.config.rock_z_start
        z_end = scene.config.rock_z_end

        # Determine the top height of the settled fouling layer using a solid box
        fouling_top_y = start_y
        if pvc > 0.0:
            def foul_area_at_y(y_test: float) -> float:
                box_area = (y_test - start_y) * domain_x
                from .physics import circle_strip_intersection
                rock_area_in_strip = 0.0
                for r in assigned_rocks:
                    if (r.y + r.radius) >= start_y and (r.y - r.radius) <= y_test:
                        rock_area_in_strip += circle_strip_intersection(r.x, r.y, r.radius, start_y, y_test)
                return box_area - rock_area_in_strip
                
            y_low = start_y
            y_high = physical_top
            for _ in range(30):
                y_mid = (y_low + y_high) / 2.0
                if foul_area_at_y(y_mid) < target_foul_area:
                    y_low = y_mid
                else:
                    y_high = y_mid
                    
            fouling_top_y = (y_low + y_high) / 2.0
            fouling_top_y = max(fouling_top_y, start_y + scene.config.dx)

            scene.add_geometry(BoxCommand(
                0, start_y, 0.0,
                domain_x, fouling_top_y, domain_z,
                MC.FOULING
            ))
            print(f"[{self.name}] Fouling settled up to Y = {fouling_top_y:.3f}m (Calculated for exact PVC)")
        
        # Stamp the structural rocks ON TOP of the background box (Painter's Algorithm)
        for r in assigned_rocks:
            if getattr(scene.config, 'angular_rocks', False):
                self._add_angular_rock(scene, r, z_start, z_end)
            else:
                scene.add_geometry(CylinderCommand(
                    r.x, r.y, z_start, r.x, r.y, z_end,
                    r.radius, MC.BALLAST_ROCK
                ))
            scene.add_rock(r) # For visualizer/lab worker
            
        print(f"[{self.name}] Master Pack: {len(all_circles)} total circles.")
        print(f"  -> Assigned Rocks   : {len(assigned_rocks)} (Density: {achieved_density:.3f})")
        print(f"  -> Fouling Mode     : Solid Box (Target PVC: {pvc:.1f}%)")
        print(f"  -> Physical Top     : {physical_top:.3f}m")

    def _add_angular_rock(self, scene: SceneCheckpoint, rock: Any, z_start: float, z_end: float) -> None:
        """Render a rock as a faceted polygon using gprMax #triangle commands."""
        import math
        import random
        from src.gpr_commands import TriangleCommand
        
        n_sides = getattr(scene.config, 'rock_sides', 6)
        cx, cy, r = rock.x, rock.y, rock.radius
        domain_x, domain_y, _ = scene.get_domain_params()

        random.seed(hash((cx, cy)))
        offset_angle = random.uniform(0, 2 * math.pi)
        vertices = []
        for i in range(n_sides):
            angle = offset_angle + (2 * math.pi * i / n_sides)
            vr = r * random.uniform(0.85, 1.1)
            vx = max(0.0, min(cx + vr * math.cos(angle), domain_x))
            vy = max(0.0, min(cy + vr * math.sin(angle), domain_y))
            vertices.append((vx, vy))
        
        random.seed(None) # Reset
            
        for i in range(n_sides):
            v1 = vertices[i]
            v2 = vertices[(i + 1) % n_sides]
            
            cmd = TriangleCommand(
                cx, cy, z_start,
                v1[0], v1[1], z_start,
                v2[0], v2[1], z_start,
                z_end - z_start,
                MC.BALLAST_ROCK
            )
            scene.add_geometry(cmd)

    def quality_check(self, scene: SceneCheckpoint) -> List[str]:
        return []

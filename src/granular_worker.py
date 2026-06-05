from typing import Dict, Any, List
import random
import math
from pathlib import Path

from .worker import Worker, SceneCheckpoint
from .gpr_commands import CylinderCommand, BoxCommand, SoilPeplinskiCommand, FractalBoxCommand
from .constants import MC, PC
from .physics import classify_pvc
from .rock_model import PackingBounds, Rock
from .rock_loader import RockLoader


class GranularMatrixWorker(Worker):
    """
    Unified rock + fouling worker.

    1. Packs the full ballast volume using the strategy selected by
       config.rock_packing_algorithm (via ToolWarehouse).
    2. Classifies circles by size into rocks vs. fines.
    3. Gravity-settles rocks.
    4. Places fouling as a solid box (painter's algorithm) for exact PVC.
    """
    
    name = "GranularMatrixWorker"

    def execute(self, scene: SceneCheckpoint, params: Dict[str, Any], materials: Any, tools: Any) -> None:
        """Fill the ballast volume with rocks and fouling.

        Steps:
          1. Read ballast extents from CoordinateSystem (set by BallastWorker).
          2. Run the packing strategy selected by config.rock_packing_algorithm
             (via ToolWarehouse) to generate a master set of circles (radius 1 mm → r_max).
          3. Classify circles: ≥ 2×fouling_particle_size_max → rock pool; rest discarded.
          4. Gravity-settle rocks: drop each 2 mm at a time until floor or collision.
          5. Place fouling: binary-search the y-height where void area below equals
             PVC% of total void; draw a single #box up to that height.
          6. Stamp rock geometry (#cylinder or #triangle) on top of the fouling box.
        """
        # 1. Resolve geometry bounds
        from src.domain import Layer
        bounds_obj = scene.coordinate_system.bounds(Layer.BALLAST)
        start_y, top_y = bounds_obj.bottom, bounds_obj.top

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
        # Check if rocks should be loaded from a source file instead of packing
        source_file = getattr(scene.config, 'rock_source_file', None)

        if source_file:
            # Load rocks from existing .in file
            algo = "loaded"
            print(f"[{self.name}] Loading rocks from {source_file}...")
            try:
                source_path = Path(source_file)
                loaded_rocks, source_meta = RockLoader.extract_rocks_from_file(source_path)

                # RockLibrary fragments are packed in y in [0, height] (0-based),
                # so shift them up to the scene's ballast bottom. Other source
                # files are assumed already in scene coordinates.
                if 'rock_library' in source_meta:
                    for r in loaded_rocks:
                        r.y += start_y

                # Filter rocks to ballast layer
                ballast_rocks = [r for r in loaded_rocks if start_y <= r.y <= top_y]

                if not ballast_rocks:
                    # Try loading all rocks in ballast range
                    ballast_rocks = [r for r in loaded_rocks if start_y <= r.y <= top_y + 0.5]

                print(f"[{self.name}] Loaded {len(ballast_rocks)} rocks from source file")

                # Convert loaded rocks to circle-like objects for processing
                all_circles = [r.to_rock() for r in ballast_rocks]

                if not all_circles:
                    scene.log_issue(self.name, "rock_loading_failure", "error",
                                   f"No rocks found in ballast layer from {source_file}")
                    return

            except Exception as e:
                scene.log_issue(self.name, "rock_loading_error", "error", str(e))
                return
        else:
            # Run packing algorithm
            algo = scene.config.rock_packing_algorithm
            packer = tools.get_tool("rock_packer")
            from .rock_packing import _grading_curve_from_config
            grading_curve = _grading_curve_from_config(scene.config)
            print(f"[{self.name}] Running Master Pack ({algo})...")
            all_circles = packer.generate_rocks(
                bounds=bounds,
                radius_min=0.001, # 1mm minimum grain size
                radius_max=r_max,
                target_fill_ratio=0.85, # Safely below max theoretical ~90%
                max_attempts=scene.config.rock_packing_max_attempts,
                min_gap=min_gap,
                grading_curve=grading_curve,
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
        try:
            from tqdm import tqdm as _tqdm
        except ImportError:
            _tqdm = None

        assigned_rocks.sort(key=lambda r: r.y) # Sort bottom to top
        settled_rocks = []
        rock_iter = (
            _tqdm(assigned_rocks, desc="  Gravity settle", unit="rock",
                  ncols=72, file=__import__('sys').stdout, leave=False)
            if _tqdm else assigned_rocks
        )
        for r in rock_iter:
            step = 0.002 # 2mm drop per step
            while r.y - r.radius > start_y:
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

            if getattr(scene.config, 'fouling_heterogeneous', False):
                self._add_heterogeneous_fouling(
                    scene, pvc, 0.0, start_y, fouling_top_y, domain_x, domain_z
                )
                print(f"[{self.name}] Fouling settled up to Y = {fouling_top_y:.3f}m "
                      f"(heterogeneous fractal_box, exact PVC)")
            else:
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
            
        print(f"[{self.name}] Master Pack ({algo}): {len(all_circles)} total circles.")
        print(f"  -> Assigned Rocks   : {len(assigned_rocks)} (Density: {achieved_density:.3f})")
        foul_mode = ("Heterogeneous fractal_box"
                     if getattr(scene.config, 'fouling_heterogeneous', False)
                     else "Solid Box")
        print(f"  -> Fouling Mode     : {foul_mode} (Target PVC: {pvc:.1f}%)")
        print(f"  -> Physical Top     : {physical_top:.3f}m")

    def _add_heterogeneous_fouling(self, scene: SceneCheckpoint, pvc: float,
                                   x_start: float, y_start: float, y_top: float,
                                   domain_x: float, domain_z: float) -> None:
        """Emit the fouling void-fill as a heterogeneous #soil_peplinski + #fractal_box.

        Gap A (PINN4GPR-inspired): the fouling fines are modeled with the
        Peplinski semi-empirical mixing model and distributed fractally so the
        layer has internal volumetric dielectric texture (volumetric scattering),
        unlike a single homogeneous #box. The rock skeleton is still stamped on
        top afterwards, preserving rock/fouling scattering interfaces.

        Volumetric water fraction rises with PVC (capillary retention of fines),
        so the dielectric dispersion tracks fouling.
        """
        cfg = scene.config
        wf = cfg.fouling_water_frac_base + cfg.fouling_water_frac_slope * (
            min(max(pvc, 0.0), 100.0) / 100.0
        )
        spread = cfg.fouling_water_frac_spread
        water_lo = max(0.001, wf - spread)
        water_hi = max(water_lo + 1e-3, wf + spread)

        soil_id = "foul_soil"
        scene.add_geometry(SoilPeplinskiCommand(
            cfg.fouling_peplinski_sand_frac,
            cfg.fouling_peplinski_clay_frac,
            cfg.fouling_peplinski_bulk_density,
            cfg.fouling_peplinski_sand_part_density,
            water_lo, water_hi, soil_id,
        ))

        seed = None
        if scene.work_order is not None:
            seed = scene.work_order.get_input('seed', None)
        if seed is not None:
            seed = int(seed) & 0x7FFFFFFF

        scene.add_geometry(FractalBoxCommand(
            x_start, y_start, 0.0,
            domain_x, y_top, domain_z,
            cfg.fouling_fractal_dimension,
            cfg.fouling_n_materials,
            soil_id, "foul_fb",
            seed=seed,
        ))

        # Roughen the fouling TOP (the fouling->ballast-air interface, the
        # strongest sub-ballast specular reflector). Safe: the ballast region
        # above is air + discrete rocks, so undulating the surface DOWN into the
        # fouling never creates voids. Rocks are stamped afterwards (higher
        # priority), so they still sit on top.
        if getattr(cfg, 'layer_surface_roughness', False):
            from .gpr_commands import AddSurfaceRoughnessCommand
            depth = getattr(cfg, 'layer_roughness_depth', 0.02)
            lower = max(y_start, y_top - depth)
            scene.add_geometry(AddSurfaceRoughnessCommand(
                x_start, y_top, 0.0, domain_x, y_top, domain_z,
                cfg.fouling_fractal_dimension, lower, y_top, "foul_fb", seed=seed,
            ))

    def _add_angular_rock(self, scene: SceneCheckpoint, rock: Any, z_start: float, z_end: float) -> None:
        """Render one rock as a faceted polygon extruded in z via gprMax #triangle commands.

        Shape generation (Al Ibrahim et al. 2019 + Kerimov 2018):
          Pass 1 — Multi-octave fractal harmonic noise perturbs each vertex radius.
                   lacunarity=2, persistence=0.5, golden-ratio phase offset per octave.
          Pass 2 — Area-preserving normalization: scale = sqrt(πr² / A_raw) so the
                   rendered EM cross-section equals the nominal circle area πr².
          Fan triangulation: n_sides triangles share the rock centre as apex.
        """
        import math
        import random
        from src.gpr_commands import TriangleCommand

        n_sides = getattr(scene.config, 'rock_sides', 6)
        cx, cy, r = rock.x, rock.y, rock.radius
        domain_x, domain_y, _ = scene.get_domain_params()

        sphericity  = getattr(scene.config, 'rock_sphericity', 0.8)
        irregularity = 1.0 - sphericity
        octaves     = getattr(scene.config, 'rock_noise_octaves', 3)

        base_n      = random.randint(2, 4)
        base_phase  = random.uniform(0, 2 * math.pi)
        offset_angle = random.uniform(0, 2 * math.pi)

        # Pass 1: multi-octave fractal harmonic radii
        # lacunarity=2, persistence=0.5, golden-ratio phase shift per octave
        delta_angle = 2 * math.pi / n_sides
        raw_radii = []
        for i in range(n_sides):
            angle = offset_angle + i * delta_angle
            perturbation = 0.0
            freq, amp = base_n, irregularity * 0.20
            for k in range(octaves):
                perturbation += amp * math.cos(freq * angle + base_phase + k * 1.618)
                freq *= 2
                amp  *= 0.5
            raw_radii.append(r * (1.0 + perturbation))

        # Pass 2: area-preserving normalization (Al Ibrahim et al. 2019)
        # A = 0.5 * sin(Δθ) * Σ r_i * r_{i+1}  →  scale = sqrt(πr² / A_raw)
        raw_area = 0.5 * math.sin(delta_angle) * sum(
            raw_radii[i] * raw_radii[(i + 1) % n_sides] for i in range(n_sides)
        )
        scale = math.sqrt(math.pi * r * r / raw_area) if raw_area > 0.0 else 1.0

        vertices = []
        for i in range(n_sides):
            angle = offset_angle + i * delta_angle
            vr = raw_radii[i] * scale
            vx = max(0.0, min(cx + vr * math.cos(angle), domain_x))
            vy = max(0.0, min(cy + vr * math.sin(angle), domain_y))
            vertices.append((vx, vy))

        # Fan triangulation from centre
        for i in range(n_sides):
            v1 = vertices[i]
            v2 = vertices[(i + 1) % n_sides]
            scene.add_geometry(TriangleCommand(
                cx, cy, z_start,
                v1[0], v1[1], z_start,
                v2[0], v2[1], z_start,
                z_end - z_start,
                MC.BALLAST_ROCK
            ))

    def quality_check(self, scene: SceneCheckpoint) -> List[str]:
        errors = []
        if not scene.rock_positions:
            errors.append("GranularMatrixWorker: no rocks placed")
        elif scene.rock_count < 5:
            errors.append(f"GranularMatrixWorker: suspiciously low rock count ({scene.rock_count})")
        return errors

"""
Concrete Worker implementations for the Factory Architecture.

Each worker handles a specific layer or component of the GPR scene.
"""
from typing import List, Dict, Any, TYPE_CHECKING, Optional
import random
from .worker import Worker, SceneCheckpoint
from .gpr_commands import BoxCommand, CylinderCommand, HertzianDipoleCommand, RxCommand, WaveformCommand
from .rock_packing import (
    PoissonDiskPacking, FrontChainPacking, PhysicsPacking,
    TrianglePacking, RandomPacking, PackingBounds, CirclifyPacking,
    GrowthPacking
)
from .physics import classify_pvc
from .constants import MC, PC

if TYPE_CHECKING:
    pass



class AirWorker(Worker):
    """
    Paints the background/medium with free_space (air).
    This is typically the first worker in the pipeline.
    """
    name = "AirWorker"
    
    def execute(self, scene: SceneCheckpoint, params: Dict[str, Any], materials: Any, tools: Any) -> None:
        # Prioritize WorkOrder (e.g., if a variant changes domain size)
        domain_x, domain_y, domain_z = scene.get_domain_params()

        scene.add_geometry(BoxCommand(
            0, 0, 0,
            domain_x, domain_y, domain_z,
            MC.AIR
        ))
        
    def quality_check(self, scene: SceneCheckpoint) -> List[str]:
        # Air should ideally be the first command and cover everything
        # But since we use Painter's algorithm, it just needs to exist
        if not scene.geometry:
             return ["AirWorker: No geometry added"]
        
        # Check if first command is air box
        first_cmd = scene.geometry[0]
        if not (isinstance(first_cmd, BoxCommand) and first_cmd.material == MC.AIR):
             return ["AirWorker: First command is not free_space box"]
             
        return []


class SubgradeWorker(Worker):
    """
    Lays the subgrade layer (base soil, 0-0.5m).
    Foundation for railway track - distributes loads to natural ground.
    """
    name = "SubgradeWorker"
    
    def execute(self, scene: SceneCheckpoint, params: Dict[str, Any], materials: Any, tools: Any) -> None:
        mat = materials.get_material(MC.SUBGRADE)
        scene.add_material(mat)
        
        domain_x, _, domain_z = scene.get_domain_params()
        subgrade_top = getattr(scene.config, 'subgrade_height', 0.5)

        if scene.work_order:
            subgrade_top = scene.work_order.get_input('subgrade_height', subgrade_top)
            scene.work_order.set('subgrade_top_y', subgrade_top, self.name)
        
        scene.add_geometry(BoxCommand(
            0, 0, 0,
            domain_x, subgrade_top, domain_z,
            MC.SUBGRADE
        ))
        
    def quality_check(self, scene: SceneCheckpoint) -> List[str]:
        found = False
        for cmd in scene.geometry:
            if hasattr(cmd, 'material') and cmd.material == MC.SUBGRADE:
                found = True
                break
        
        if not found:
            return ["SubgradeWorker: No subgrade geometry found"]
        return []


class FormationWorker(Worker):
    """
    Adds formation/subballast layer (0.5-0.6m, ~100mm thick).
    Transition layer between subgrade and ballast - prevents mixing.
    """
    name = "FormationWorker"
    
    def execute(self, scene: SceneCheckpoint, params: Dict[str, Any], materials: Any, tools: Any) -> None:
        from src.domain import Anchor
        
        # 1. Determine geometry bounds (Refactored)
        if scene.coordinate_system:
             # NEW: Use CoordinateSystem
             start_y, top_y = scene.coordinate_system.get_layer_bounds('formation')
             thickness = top_y - start_y
        else:
             # LEGACY: Fallback behavior
             # Prioritize WorkOrder output from previous worker
             start_y = 0.0
             if scene.work_order:
                  start_y = scene.work_order.get('subgrade_top_y', 0.0)
             else:
                 # Fallback for legacy support: scan geometry
                 start_y = scene.find_top_y_from_geometry(MC.AIR)
                     
             # Get thickness
             thickness = 0.10 # default
             if scene.work_order:
                  thickness = scene.work_order.get_input('formation_thickness', getattr(scene.config, 'formation_thickness', 0.10))
             else:
                  thickness = params.get('formation_thickness', getattr(scene.config, 'formation_thickness', 0.10))
             
             top_y = start_y + thickness
        
        mat = materials.get_material(MC.FORMATION)
        scene.add_material(mat)
        
        # Log for next worker
        if scene.work_order:
             scene.work_order.set('formation_top_y', top_y, self.name)

        domain_x, _, domain_z = scene.get_domain_params()

        scene.add_geometry(BoxCommand(
            0, start_y, 0,
            domain_x, top_y, domain_z,
            MC.FORMATION
        ))
        
    def quality_check(self, scene: SceneCheckpoint) -> List[str]:
        # Check if formation exists and is on top of subgrade
        formation_cmds = [
            c for c in scene.geometry 
            if isinstance(c, BoxCommand) and c.material == MC.FORMATION
        ]
        
        if not formation_cmds:
            return ["FormationWorker: No formation geometry found"]
            
        return []


class BallastWorker(Worker):
    """
    Defines the main ballast layer container.
    
    This worker defines the EXTENT and BACKGROUND MATERIAL of the ballast layer.
    It does NOT place individual rocks (that's the RockWorker's job).
    
    For clean ballast, the background is usually free_space (voids).
    For fouled ballast, the background might be fouling material.
    """
    name = "BallastWorker"
    
    def execute(self, scene: SceneCheckpoint, params: Dict[str, Any], materials: Any, tools: Any) -> None:
        from src.domain import Anchor
        
        # 1. Determine Geometry (Refactored)
        if scene.coordinate_system:
             # NEW: Use CoordinateSystem (Type-Safe)
             from src.domain import Layer
             bounds = scene.coordinate_system.bounds(Layer.BALLAST)
             start_y, top_y = bounds.bottom, bounds.top
             thickness = bounds.height
        else:
             # LEGACY: Fallback
             start_y = 0.0
             if scene.work_order:
                  start_y = scene.work_order.get('formation_top_y', 0.6)
             else:
                 # Legacy scan
                  start_y = scene.find_top_y_from_geometry(MC.AIR)

             # Thickness
             thickness = 0.4
             if scene.work_order:
                  thickness = scene.work_order.get_input('ballast_thickness', getattr(scene.config, 'max_ballast_thickness', 0.4))
             else:
                  thickness = params.get('ballast_thickness', getattr(scene.config, 'max_ballast_thickness', 0.4))
             
             top_y = start_y + thickness
        
        
        # Enforce Domain Restrictions (Ballast cannot exceed domain height)
        _, domain_y, _ = scene.get_domain_params()
            
        if top_y > domain_y:
            scene.log_issue(self.name, "domain_violation", "warning", 
                            f"Ballast top ({top_y:.3f}) exceeds domain height ({domain_y:.3f}). Clamping.")
            top_y = domain_y
            # Recalculate thickness to reflect clamping
            thickness = top_y - start_y
        
        # Sync with WorkOrder (Single Source of Truth)
        if scene.work_order:
            scene.work_order.set('ballast_bottom_y', start_y, self.name)
            scene.work_order.set('ballast_top_y', top_y, self.name)
            scene.work_order.set('ballast_thickness', thickness, self.name)
        else:
            scene.log_issue(self.name, "missing_dependency", "warning", "No WorkOrder attached. Outputs lost.")
        
    def quality_check(self, scene: SceneCheckpoint) -> List[str]:
        # Check WorkOrder instead of metadata
        if not scene.work_order:
            return ["BallastWorker: No WorkOrder attached"]
        
        if scene.work_order.get('ballast_top_y') is None:
            return ["BallastWorker: Output 'ballast_top_y' not found in WorkOrder"]
        return []


from .rock_model import Rock

class RockWorker(Worker):
    """
    Places rock aggregates within the ballast layer.
    
    Uses packing strategies (e.g., specific algorithms from ToolWarehouse)
    to fill the ballast volume with varied rocks.
    """
    name = "RockWorker"
    
    def execute(self, scene: SceneCheckpoint, params: Dict[str, Any], materials: Any, tools: Any) -> None:
        # ---------------------------------------------------------------------
        # 1. Determine Vertical Bounds (Refactored)
        # ---------------------------------------------------------------------
        if scene.coordinate_system:
             # NEW: Use CoordinateSystem (Type-Safe)
             from src.domain import Layer
             bounds = scene.coordinate_system.bounds(Layer.BALLAST)
             start_y, top_y = bounds.bottom, bounds.top
             ballast_bounds = (start_y, top_y)
        else:
             # LEGACY: Use helper method
             ballast_bounds = self._calculate_ballast_bounds(scene)
             
        if not ballast_bounds:
            return

        start_y, top_y = ballast_bounds
        
        # ---------------------------------------------------------------------
        # 2. Material Setup
        # ---------------------------------------------------------------------
        rock_mat = materials.get_material(MC.BALLAST_ROCK)
        scene.add_material(rock_mat)

        # ---------------------------------------------------------------------
        # 3. Select Packing Strategy
        # ---------------------------------------------------------------------
        if 'packing_strategy' in params:
            strategy = params['packing_strategy']
        else:
            algo_name = scene.config.rock_packing_algorithm.lower()
            if algo_name == 'front_chain':
                strategy = FrontChainPacking()
            elif algo_name == 'physics':
                strategy = PhysicsPacking()
            elif algo_name == 'triangle':
                strategy = TrianglePacking()
            elif algo_name == 'random':
                strategy = RandomPacking()
            elif algo_name == 'circlify':
                strategy = CirclifyPacking()
            elif algo_name == 'growth':
                strategy = GrowthPacking()
            else:
                strategy = PoissonDiskPacking()
                
        # No caching logic - always generate fresh
        print(f"[{self.name}] Generating fresh rocks (Strategy: {strategy.__class__.__name__})")

        total_rocks, highest_rock_y = self._pack_all_layers(
            scene, start_y, top_y, strategy
        )
        scene.metadata['packing_source'] = 'generated'
        scene.metadata['rock_count'] = total_rocks

        # ---------------------------------------------------------------------
        # 5. Serialization and Persistence
        # ---------------------------------------------------------------------
        self._store_results(scene, start_y, top_y, highest_rock_y)
        
    def _calculate_ballast_bounds(self, scene: SceneCheckpoint) -> tuple[float, float] | None:
        """Determines the vertical bounds of the ballast layer."""
        start_y = 0.5
        top_y = 0.9
        
        if scene.work_order:
            start_y = scene.work_order.get('ballast_bottom_y', start_y)
            top_y = scene.work_order.get('ballast_top_y', top_y)
            return start_y, top_y
        else:
            scene.log_issue(self.name, "missing_dependency", "error", "No WorkOrder found.")
            return None

    def _pack_all_layers(self, scene: SceneCheckpoint, start_y: float, top_y: float,
                         strategy: Any) -> tuple[int, float]:
        """Iterates through layers and packs rocks."""
        ballast_thickness = top_y - start_y
        n_layers = scene.config.rock_layers
        layer_height = ballast_thickness / n_layers
        
        # Use UNIFORM size distribution across all layers (literature-accurate)
        r_min = scene.config.rock_radius_min
        r_max = scene.config.rock_radius_max
        
        domain_x, _, _ = scene.get_domain_params()
             
        z_start = scene.config.rock_z_start
        z_end = scene.config.rock_z_end
        
        if scene.work_order:
            # Try to get from typed_params, use config defaults if None
            if hasattr(scene.work_order, '_work_order'):
                typed_params = scene.work_order._work_order.typed_params
                z_start = typed_params.rock_z_start or z_start
                z_end = typed_params.rock_z_end or z_end
            elif hasattr(scene.work_order, 'typed_params'):
                typed_params = scene.work_order.typed_params
                z_start = typed_params.rock_z_start or z_start
                z_end = typed_params.rock_z_end or z_end
             
        # Collect all rocks across all layers before emitting geometry.
        # Packing strategies are 2-D (x, y, r only); z is stamped here.
        all_rocks = []
        for i in range(n_layers):
            y_min = start_y + i * layer_height
            y_max = start_y + (i + 1) * layer_height
            bounds = PackingBounds(0.0, domain_x, y_min, y_max)
            rocks = self._generate_rocks_for_layer(
                scene, strategy, bounds, r_min, r_max, i
            )
            for rock in rocks:
                all_rocks.append(Rock(x=rock.x, y=rock.y, radius=rock.radius,
                                      z_start=z_start, z_end=z_end))

        # Gravity settlement: drop each rock to rest on floor or neighbours
        if getattr(scene.config, 'rock_gravity_settle', True) and all_rocks:
            self._settle_rocks(all_rocks, start_y)

        # Emit geometry
        total_rocks = 0
        highest_rock_y = start_y
        for rock in all_rocks:

            if getattr(scene.config, 'angular_rocks', False):



                self._add_angular_rock(scene, rock, z_start, z_end)
            else:
                cmd = CylinderCommand(
                    rock.x, rock.y, z_start,
                    rock.x, rock.y, z_end,
                    rock.radius, MC.BALLAST_ROCK
                )
                scene.add_geometry(cmd)
            
            scene.add_rock(rock)
            highest_rock_y = max(highest_rock_y, rock.y + rock.radius)
            total_rocks += 1

        return total_rocks, highest_rock_y

    def _add_angular_rock(self, scene: SceneCheckpoint, rock: Any, z_start: float, z_end: float) -> None:
        """Render a rock as a faceted polygon using gprMax #triangle commands."""
        import math
        from src.gpr_commands import TriangleCommand

        n_sides = getattr(scene.config, 'rock_sides', 6)
        cx, cy, r = rock.x, rock.y, rock.radius
        domain_x, domain_y, _ = scene.get_domain_params()

        offset_angle = random.uniform(0, 2 * math.pi)
        vertices = []
        for i in range(n_sides):
            angle = offset_angle + (2 * math.pi * i / n_sides)
            vr = r * random.uniform(0.85, 1.1)
            vx = max(0.0, min(cx + vr * math.cos(angle), domain_x))
            vy = max(0.0, min(cy + vr * math.sin(angle), domain_y))
            vertices.append((vx, vy))
            
        # Create triangles sharing the center point (Fan triangulation)
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


    def _settle_rocks(self, rocks: List[Any], floor_y: float) -> None:
        """Drop each rock under gravity until it rests on the floor or a lower rock.

        Rocks are processed lowest-first. Each rock's y is updated in-place.
        O(nÂ²) â€" acceptable for typical counts (~200 rocks, Benedetto et al. 2016).
        """
        import math
        rocks.sort(key=lambda r: r.y)
        settled: List[Any] = []
        for rock in rocks:
            best_y = floor_y + rock.radius  # resting on layer floor
            for s in settled:
                dx = abs(rock.x - s.x)
                gap = rock.radius + s.radius
                if dx < gap:  # horizontal overlap â†’ can stack
                    contact_y = s.y + math.sqrt(gap ** 2 - dx ** 2)
                    best_y = max(best_y, contact_y)
            rock.y = best_y
            settled.append(rock)

    def _generate_rocks_for_layer(self, scene: SceneCheckpoint, strategy: Any,
                                  bounds: PackingBounds, r_min: float, r_max: float,
                                  layer_idx: int) -> List[Any]:
        """Tries primary strategy, falls back to GridPacking if needed."""
        from .rock_packing import _grading_curve_from_config

        target_fill = scene.config.rock_packing_target_fill
        max_attempts = scene.config.rock_packing_max_attempts
        min_gap = getattr(scene.config, 'rock_min_gap', 0.0)
        grading_curve = _grading_curve_from_config(scene.config)

        rocks = strategy.generate_rocks(
            bounds, r_min, r_max, target_fill, max_attempts, min_gap, grading_curve
        )


        final_strategy_name = strategy.__class__.__name__

        if not rocks:
             scene.log_issue(self.name, "packing_failure", "warning",
                             f"Primary strategy failed for layer {layer_idx}. Switching to GridPacking.")
             from .rock_packing import GridPacking
             fallback = GridPacking()
             rocks = fallback.generate_rocks(bounds, r_min, r_max)
             final_strategy_name = "GridPacking"

        scene.metadata['packing_strategy'] = final_strategy_name
        return rocks

    def _store_results(self, scene: SceneCheckpoint, start_y: float, top_y: float,
                       highest_y: float) -> None:
        """Stores rock model in WorkOrder/DataFrame."""
        if not scene.work_order:
            return

        domain_x, _, _ = scene.get_domain_params()
        achieved_density = scene.rock_density_monte_carlo(domain_x, start_y, highest_y, samples=5000)
        porosity = max(0.0, 1.0 - achieved_density)

        scene.metadata['achieved_density'] = achieved_density
        scene.metadata['porosity'] = porosity
        scene.metadata['mc_y_min'] = start_y
        scene.metadata['mc_y_max'] = highest_y

        print(f"[{self.name}] Achieved Density: {achieved_density:.3f}, Porosity: {porosity:.3f}")

        z_start = scene.config.rock_z_start
        z_end   = scene.config.rock_z_end
        if hasattr(scene.work_order, '_work_order'):
            p = scene.work_order._work_order.typed_params
            z_start = p.rock_z_start or z_start
            z_end   = p.rock_z_end   or z_end
        elif hasattr(scene.work_order, 'typed_params'):
            p = scene.work_order.typed_params
            z_start = p.rock_z_start or z_start
            z_end   = p.rock_z_end   or z_end

        df = scene.rocks_to_dataframe(default_z_start=z_start, default_z_end=z_end)
        scene.work_order.set('rock_model', df, self.name)
        scene.work_order.set('highest_rock_y', highest_y, self.name)
        scene.work_order.set('porosity', porosity, self.name)
        
    def quality_check(self, scene: SceneCheckpoint) -> List[str]:
        if not scene.rock_positions:
            return ["RockWorker: No rocks placed"]
        if scene.metadata.get('rock_count', 0) < 10:
             return ["RockWorker: Suspiciously low rock count"]
        return []


class FoulingWorker(Worker):
    """
    Simulates ballast fouling: fine materials (soil, sand, coal) filling voids.
    controlled by PVC (Percentage Void Contamination).
    """
    name = "FoulingWorker"
    
    def execute(self, scene: SceneCheckpoint, params: Dict[str, Any], materials: Any, tools: Any) -> None:
        work_order = scene.work_order
        if not work_order:
            pvc = params.get('pvc', 0.0)
            moisture = params.get('moisture', 0.0)
            pvc_top = None
            pvc_bottom = None
        else:
            pvc = work_order.get_input('pvc', 0.0)
            moisture = work_order.get_input('moisture', 0.0)
            pvc_top    = work_order.get_input('pvc_top', None)
            pvc_bottom = work_order.get_input('pvc_bottom', None)

        scene.metadata['pvc'] = pvc
        scene.metadata['moisture'] = moisture

        porosity = scene.metadata.get('porosity', 0.4)
        if work_order and 'porosity' not in scene.metadata:
            porosity = work_order.get_input('porosity', 0.4)

        scene.metadata['used_porosity'] = porosity
        scene.metadata['FI_class'] = classify_pvc(pvc, porosity=porosity)

        # Resolve ballast bounds
        if scene.coordinate_system:
            from src.domain import Layer
            bounds = scene.coordinate_system.bounds(Layer.BALLAST)
            start_y, top_y = bounds.bottom, bounds.top
            ballast_thickness = bounds.height
        elif work_order:
            start_y = work_order.get('ballast_bottom_y', 0.5)
            ballast_thickness = work_order.get('ballast_thickness', 0.4)
            top_y = start_y + ballast_thickness
        else:
            start_y = scene.metadata.get('ballast_bottom_y', 0.5)
            ballast_thickness = scene.metadata.get('ballast_thickness', 0.4)
            top_y = start_y + ballast_thickness

        domain_x, _, domain_z = scene.get_domain_params()

        is_stratified = pvc_bottom is not None or pvc_top is not None
        any_fouling = is_stratified or pvc > 0

        if not any_fouling:
            print(f"[{self.name}] FI Class: {scene.metadata['FI_class']} (PVC={pvc}%, n={porosity:.3f})")
            return

        # Register materials once for both modes
        foul_mat = materials.get_material(MC.FOULING, moisture=moisture)
        scene.add_material(foul_mat)
        dense_mat = materials.get_material(MC.FOULING_DENSE, moisture=moisture)
        scene.add_material(dense_mat)

        if is_stratified:
            # Two independent fouling zones split at the ballast midpoint.
            # Bottom zone: full 3-zone gravity-settled model (dense block at y_start).
            # Top zone:    dispersed particles only — a dense block at mid_y would be
            #              physically impossible since fines always settle to the column base.
            mid_y = (start_y + top_y) / 2.0
            eff_pvc_bottom = pvc_bottom if pvc_bottom is not None else 0.0
            eff_pvc_top    = pvc_top    if pvc_top    is not None else 0.0

            print(f"[{self.name}] Stratified — bottom PVC={eff_pvc_bottom:.1f}%  top PVC={eff_pvc_top:.1f}%")
            scene.metadata['pvc_bottom'] = eff_pvc_bottom
            scene.metadata['pvc_top']    = eff_pvc_top

            if eff_pvc_bottom > 0:
                self._apply_fouling_zone(scene, start_y, mid_y, eff_pvc_bottom, domain_x, domain_z)
            if eff_pvc_top > 0:
                self._apply_dispersed_zone(scene, mid_y, top_y, eff_pvc_top, domain_x, domain_z)
        else:
            print(f"[{self.name}] FI Class: {scene.metadata['FI_class']} (PVC={pvc}%, n={porosity:.3f})")
            self._apply_fouling_zone(scene, start_y, top_y, pvc, domain_x, domain_z)

    def _apply_fouling_zone(self, scene: SceneCheckpoint, y_start: float, y_top: float,
                            pvc: float, domain_x: float, domain_z: float) -> None:
        """Apply 3-zone fouling model (Benedetto et al. 2016) to a vertical interval.

        Zone 1 — dense solid block at the base (bal_foul).
        Zone 2 — granular dispersed particles above zone 1 (bal_foul_granular).
        Zone 3 — sparse dispersed particles in remaining fouled height.
        """
        pvc_fraction = min(max(pvc, 0.0), 100.0) / 100.0
        zone_height   = y_top - y_start
        fouling_height = zone_height * pvc_fraction

        dense_frac    = getattr(scene.config, 'fouling_dense_fraction',    0.5)
        granular_frac = getattr(scene.config, 'fouling_granular_fraction', 0.3)

        z1_top = y_start + fouling_height * dense_frac
        z2_top = z1_top  + fouling_height * granular_frac
        z3_top = y_start + fouling_height

        if z1_top - y_start > 2e-3:
            self._generate_settled_layer(scene, y_start, z1_top, domain_x, domain_z,
                                         material=MC.FOULING_DENSE)
        self._generate_dispersed_particles(scene, z1_top, z2_top, pvc_fraction * 0.7,  domain_x, domain_z)
        self._generate_dispersed_particles(scene, z2_top, z3_top, pvc_fraction * 0.25, domain_x, domain_z)

    def _apply_dispersed_zone(self, scene: SceneCheckpoint, y_start: float, y_top: float,
                              pvc: float, domain_x: float, domain_z: float) -> None:
        """Uniformly dispersed fouling for the upper ballast zone (no settled block).

        Used for the top half in stratified mode: any fines in the upper zone are
        not yet gravity-settled (surface infiltration / recent contamination), so
        they appear as random granular particles throughout the zone rather than as
        a dense layer that would physically fall to the column base.
        """
        pvc_fraction = min(max(pvc, 0.0), 100.0) / 100.0
        self._generate_dispersed_particles(scene, y_start, y_top, pvc_fraction, domain_x, domain_z)

    def _generate_settled_layer(self, scene: SceneCheckpoint, y_start: float, y_end: float,
                                domain_x: float, domain_z: float,
                                material: str = MC.FOULING) -> None:
        """Generates the solid block of settled fouling material."""
        if y_end - y_start < scene.config.dx:
            return
        scene.add_geometry(BoxCommand(0, y_start, 0, domain_x, y_end, domain_z, material))

    def _generate_dispersed_particles(self, scene: SceneCheckpoint, y_min: float, y_max: float, 
                                     pvc_fraction: float, domain_x: float, domain_z: float) -> None:
        """Generates dispersed fouling particles using a Circle Growth algorithm (Quadtree optimized)."""
        if y_max <= y_min or pvc_fraction <= 0:
            return

        from .rock_packing import CircleQuadtree, PackingBounds, Rock
        import math

        bounds = PackingBounds(0, domain_x, y_min, y_max)
        qt = CircleQuadtree(bounds, max_depth=7)

        # 1. Insert existing rocks into the quadtree (they act as fixed obstacles)
        for rock in scene.rock_positions:
            # We only care about rocks that could intersect this zone
            if rock.y + rock.radius >= y_min and rock.y - rock.radius <= y_max:
                qt.insert(rock)

        # 2. Determine target area for fouling particles
        porosity = scene.metadata.get('used_porosity', 0.4)
        zone_area = domain_x * (y_max - y_min)
        void_area = zone_area * porosity
        
        # We try to fill a fraction of the void area equivalent to the requested PVC fraction
        # Note: 100% space-filling with circles is impossible (max is ~90%), so if PVC is very high
        # this will just pack as densely as it geometrically can.
        target_fill_area = void_area * pvc_fraction

        radius_min = scene.config.fouling_particle_size_min
        radius_max = scene.config.fouling_particle_size_max
        grow_step = 0.0005  # 0.5 mm growth increments
        min_gap = 0.0       # Fouling particles can touch

        def _collides(cx: float, cy: float, cr: float) -> bool:
            """Check if fouling particle overlaps bounds, rocks, or other fouling particles."""
            if (cx - cr < bounds.x_min or cx + cr > bounds.x_max or
                cy - cr < bounds.y_min or cy + cr > bounds.y_max):
                return True
            return qt.overlaps_any(cx, cy, cr, min_gap)

        current_area = 0.0
        placed = 0
        outer_tries = 0
        max_outer_tries = 2000
        place_attempts = 100

        while current_area < target_fill_area and outer_tries < max_outer_tries:
            outer_tries += 1
            placed_this_round = False

            for _ in range(place_attempts):
                # Random candidate position
                cx = random.uniform(bounds.x_min + radius_min, bounds.x_max - radius_min)
                cy = random.uniform(bounds.y_min + radius_min, bounds.y_max - radius_min)

                # Reject immediately if the minimum particle size overlaps something
                if _collides(cx, cy, radius_min):
                    continue

                # Grow the particle until it hits an obstacle or max radius
                r = radius_min
                while r + grow_step <= radius_max:
                    if _collides(cx, cy, r + grow_step):
                        break
                    r += grow_step

                # Place it at its maximum collision-free size
                particle = Rock(cx, cy, r)
                qt.insert(particle)
                
                scene.add_geometry(CylinderCommand(
                    cx, cy, 0, cx, cy, domain_z,
                    r, MC.FOULING
                ))
                
                current_area += math.pi * r * r
                placed += 1
                placed_this_round = True

                if current_area >= target_fill_area:
                    break

            # If the zone is completely saturated, stop early
            if not placed_this_round:
                break
                
        print(f"      -> Zone [{y_min:.2f}-{y_max:.2f}]: Grown {placed} organic fouling particles")

    def quality_check(self, scene: SceneCheckpoint) -> List[str]:
        return []


class AntennaWorker(Worker):
    """
    Places transmitter and receiver antenna.
    """
    name = "AntennaWorker"
    
    def execute(self, scene: SceneCheckpoint, params: Dict[str, Any], materials: Any, tools: Any) -> None:
        from src.domain import Point3D, Anchor
        
        # 1. Get Antenna Positions (Refactored to use CoordinateSystem)
        # Try WorkOrder first (for variant support), else config
        if scene.work_order:
            offset = scene.work_order.get_input('antenna_offset', 0.0)
        else:
            offset = params.get('antenna_offset', 0.0)
            
        # Determine Heights
        if scene.coordinate_system:
            # NEW: Use specific Anchor
            tx_rx_y = scene.coordinate_system.get_y(Anchor.ANTENNA_LEVEL)
        else:
            # LEGACY: Fallback logic
            if scene.work_order:
                start_height = scene.work_order.get('highest_rock_y', 0.9)
                clearance = scene.work_order.get_input('antenna_clearance_above_ballast', 0.05)
                tx_rx_y = start_height + clearance
            else:
                tx_rx_y = scene.config.tx_rx_y

        # Determine Horizontal Positions
        tx_x = scene.config.tx_x + offset
        rx_x = tx_x if scene.config.monostatic else scene.config.rx_x + offset
        tx_rx_z = scene.config.tx_rx_z
        
        # Create Point3D objects (fixing Primitive Obsession #2)
        tx_position = Point3D(tx_x, tx_rx_y, tx_rx_z)
        rx_position = Point3D(rx_x, tx_rx_y, tx_rx_z)
        
        # ENFORCE DOMAIN RESTRICTIONS (Fail Fast)
        if scene.coordinate_system:
             valid_tx = scene.coordinate_system.validate_point(tx_position)
             valid_rx = scene.coordinate_system.validate_point(rx_position)
             if not valid_tx:
                 raise ValueError(f"{self.name}: TX Position {tx_position} invalid (outside domain)")
             if not valid_rx:
                 raise ValueError(f"{self.name}: RX Position {rx_position} invalid (outside domain)")
        else:
             # Legacy checks
             domain_x, domain_y, domain_z = scene.get_domain_params()
             if not (0 <= tx_x <= domain_x): raise ValueError(f"TX X out of bounds") 
             # ... (simplified legacy checks)

        # 3. Add Waveform
        if scene.config.add_waveform:
            waveform_name = "ricker_src"
            freq_normalized = 1.0  # gprMax normalized time
            center_freq = scene.config.center_freq
            
            waveform = WaveformCommand("ricker", freq_normalized, center_freq, waveform_name)
            scene.add_source(waveform)
        
        # 4. Add Source
        if scene.config.add_source:
            # Use Point3D to_tuple()
            source = HertzianDipoleCommand("z", *tx_position.to_tuple(), "ricker_src")
            scene.add_source(source)
        
        # 5. Add Receiver(s) - Supporting Multi-Offset Array (Roncoroni et al. 2025)
        num_rx = scene.config.num_receivers
        spacing = scene.config.receiver_spacing
        
        for i in range(num_rx):
            curr_rx_x = rx_x + (i * spacing)
            rx_pos = Point3D(curr_rx_x, tx_rx_y, tx_rx_z)
            
            # Domain Validation
            if scene.coordinate_system:
                if not scene.coordinate_system.validate_point(rx_pos):
                    # For arrays, we might just skip the out-of-bounds receivers instead of crashing,
                    # but for now, let's log a warning or fail if the first one is bad.
                    if i == 0:
                        raise ValueError(f"{self.name}: Primary RX Position {rx_pos} invalid")
                    else:
                        print(f"Warning: RX_{i} at {curr_rx_x} is outside domain. Skipping.")
                        continue
            
            receiver = RxCommand(*rx_pos.to_tuple())
            scene.add_receiver(receiver)

        
    def quality_check(self, scene: SceneCheckpoint) -> List[str]:
        # Check if antennas were added
        if not scene.sources:
            return ["AntennaWorker: No source commands added"]
        return []


class AssemblerWorker(Worker):
    """
    Finalizes the scene after all layers are complete.
    
    Responsibilities:
    - Final quality checks (e.g., antenna placement vs geometry)
    - Mark scene as 'assembled'
    """
    name = "AssemblerWorker"
    
    def execute(self, scene: SceneCheckpoint, params: Dict[str, Any], materials: Any, tools: Any) -> None:
        # 1. Add Geometry View (for Paraview)
        # Covers entire domain
        domain_x, domain_y, domain_z = scene.get_domain_params()
             
        # Filename based on ID if possible
        filename = "geometry"
        if scene.work_order:
            filename = f"{scene.work_order.work_order.id}_geo"
            
        from .gpr_commands import GeometryViewCommand
        
        # Use fine resolution (same as sim) or slightly coarser?
        # Usually same as dx_dy_dz
        dx = scene.config.dx
        dy = scene.config.dy
        dz = scene.config.dz
        
        scene.add_geometry(GeometryViewCommand(
            0, 0, 0,
            domain_x, domain_y, domain_z,
            dx, dy, dz, 
            filename, 'n'
        ))

        # Mark as assembled
        scene.assembled = True
        
    def quality_check(self, scene: SceneCheckpoint) -> List[str]:
        errors = []
        
        # 1. Check if antenna is inside material
        # Extract antenna positions from source commands
        tx_pos = None
        rx_pos = None
        
        for cmd in scene.sources:
            if isinstance(cmd, HertzianDipoleCommand):
                tx_pos = (cmd.x, cmd.y, cmd.z)
                
        for cmd in scene.receivers:
            if isinstance(cmd, RxCommand):
                rx_pos = (cmd.x, cmd.y, cmd.z)
                
        if not tx_pos or not rx_pos:
            errors.append("AssemblerWorker: TX or RX position not found")
            return errors
            
        # 2. Check if antenna overlaps with rocks
        rocks_to_check = scene.rock_positions
        if scene.work_order and scene.work_order.get('rock_model') is not None:
             df = scene.work_order.get('rock_model')
             rocks_to_check = [
                 type('Rock', (), {'x': r.x, 'y': r.y, 'radius': r.radius}) 
                 for r in df.itertuples()
             ]
             
        for rock in rocks_to_check:
            # 2D distance check
            tx_dist = ((tx_pos[0] - rock.x)**2 + (tx_pos[1] - rock.y)**2)**0.5
            rx_dist = ((rx_pos[0] - rock.x)**2 + (rx_pos[1] - rock.y)**2)**0.5
            
            clearance = scene.config.antenna_rock_clearance
            
            if tx_dist < (rock.radius + clearance):
                 errors.append(f"AssemblerWorker: TX too close to rock at ({rock.x:.3f}, {rock.y:.3f})")
                 
            if rx_dist < (rock.radius + clearance):
                 errors.append(f"AssemblerWorker: RX too close to rock at ({rock.x:.3f}, {rock.y:.3f})")
                 
        return errors

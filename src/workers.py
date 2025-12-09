"""
Concrete Worker implementations for the Factory Architecture.

Each worker handles a specific layer or component of the GPR scene.
"""
from typing import List, Dict, Any, TYPE_CHECKING, Optional
import random
import pandas as pd
from .worker import Worker, SceneCheckpoint
from .gpr_commands import BoxCommand, CylinderCommand, HertzianDipoleCommand, RxCommand, WaveformCommand
from .rock_packing import (
    PoissonDiskPacking, FrontChainPacking, PhysicsPacking, 
    TrianglePacking, RandomPacking, PackingBounds
)
from .physics import classify_pvc

if TYPE_CHECKING:
    pass

def _get_domain_params(scene: SceneCheckpoint, work_order: Any = None) -> tuple[float, float, float]:
    """
    Helper to get domain dimensions from WorkOrder or Config.
    """
    domain_x = scene.config.domain_x
    domain_y = scene.config.domain_y
    domain_z = scene.config.domain_z
    
    wo = work_order or scene.work_order
    if wo:
        domain_x = wo.get_input('domain_x', domain_x)
        domain_y = wo.get_input('domain_y', domain_y)
        domain_z = wo.get_input('domain_z', domain_z)
        
    return domain_x, domain_y, domain_z


class AirWorker(Worker):
    """
    Paints the background/medium with free_space (air).
    This is typically the first worker in the pipeline.
    """
    name = "AirWorker"
    
    def execute(self, scene: SceneCheckpoint, params: Dict[str, Any], materials: Any, tools: Any) -> None:
        # 1. Determine Domain size
        # Prioritize WorkOrder (e.g., if a variant changes domain size)
        domain_x, domain_y, domain_z = _get_domain_params(scene)

        # 2. Add geometry covering entire domain
        # #box: 0 0 0 domain_x domain_y domain_z free_space
        scene.add_geometry(BoxCommand(
            0, 0, 0,
            domain_x, domain_y, domain_z,
            "free_space"
        ))
        
    def quality_check(self, scene: SceneCheckpoint) -> List[str]:
        # Air should ideally be the first command and cover everything
        # But since we use Painter's algorithm, it just needs to exist
        if not scene.geometry:
             return ["AirWorker: No geometry added"]
        
        # Check if first command is air box
        first_cmd = scene.geometry[0]
        if not (isinstance(first_cmd, BoxCommand) and first_cmd.material == "free_space"):
             return ["AirWorker: First command is not free_space box"]
             
        return []


class SubgradeWorker(Worker):
    """
    Lays the subgrade layer (base soil, 0-0.5m).
    Foundation for railway track - distributes loads to natural ground.
    """
    name = "SubgradeWorker"
    
    def execute(self, scene: SceneCheckpoint, params: Dict[str, Any], materials: Any, tools: Any) -> None:
        # 1. Get material
        mat = materials.get_material("subgrade")
        scene.add_material(mat)
        
        # 2. Add geometry
        # Prioritize WorkOrder
        domain_x, _, domain_z = _get_domain_params(scene)
        subgrade_top = getattr(scene.config, 'subgrade_height', 0.5)

        if scene.work_order:
            subgrade_top = scene.work_order.get_input('subgrade_height', subgrade_top)
            
            # Log output for next worker
            scene.work_order.set('subgrade_top_y', subgrade_top, self.name)
        
        scene.add_geometry(BoxCommand(
            0, 0, 0,
            domain_x, subgrade_top, domain_z,
            "subgrade"
        ))
        
    def quality_check(self, scene: SceneCheckpoint) -> List[str]:
        # Check if subgrade exists
        found = False
        for cmd in scene.geometry:
            if hasattr(cmd, 'material') and cmd.material == 'subgrade':
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
        # 1. Determine start height
        # Prioritize WorkOrder output from previous worker
        start_y = 0.0
        if scene.work_order:
             start_y = scene.work_order.get('subgrade_top_y', 0.0)
        else:
            # Fallback for legacy support: scan geometry
            for cmd in scene.geometry:
                if isinstance(cmd, BoxCommand) and hasattr(cmd, 'y2'):
                    if hasattr(cmd, 'material') and cmd.material == 'free_space':
                        continue
                    start_y = max(start_y, cmd.y2)
                
        # 2. Get thickness
        # Prioritize WorkOrder
        thickness = 0.10 # default
        if scene.work_order:
             thickness = scene.work_order.get_input('formation_thickness', getattr(scene.config, 'formation_thickness', 0.10))
        else:
             thickness = params.get('formation_thickness', getattr(scene.config, 'formation_thickness', 0.10))
        
        # 3. Add Material
        mat = materials.get_material("formation")
        scene.add_material(mat)
        
        # 4. Add Geometry
        top_y = start_y + thickness
        
        # Log for next worker
        if scene.work_order:
             scene.work_order.set('formation_top_y', top_y, self.name)

        domain_x, _, domain_z = _get_domain_params(scene)

        scene.add_geometry(BoxCommand(
            0, start_y, 0,
            domain_x, top_y, domain_z,
            "formation"
        ))
        
    def quality_check(self, scene: SceneCheckpoint) -> List[str]:
        # Check if formation exists and is on top of subgrade
        formation_cmds = [
            c for c in scene.geometry 
            if isinstance(c, BoxCommand) and c.material == "formation"
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
        # 1. Determine start height (top of formation)
        start_y = 0.0
        
        if scene.work_order:
             # Strict dependency on previous layer
             start_y = scene.work_order.get('formation_top_y', 0.0)
        else:
            # Fallback
            for cmd in scene.geometry:
                if hasattr(cmd, 'material') and cmd.material == 'free_space':
                    continue
                if hasattr(cmd, 'y2'):
                    start_y = max(start_y, cmd.y2)
                
        # 2. Get thickness
        thickness = 0.40
        if scene.work_order:
             thickness = scene.work_order.get_input('ballast_thickness', getattr(scene.config, 'max_ballast_thickness', 0.40))
        else:
             thickness = params.get('ballast_thickness', getattr(scene.config, 'max_ballast_thickness', 0.40))
        
        # 3. Determine Background Material
        top_y = start_y + thickness
        
        # Enforce Domain Restrictions (Ballast cannot exceed domain height)
        _, domain_y, _ = _get_domain_params(scene)
            
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


from .rock_model import RockCollection

class RockWorker(Worker):
    """
    Places rock aggregates within the ballast layer.
    
    Uses packing strategies (e.g., specific algorithms from ToolWarehouse)
    to fill the ballast volume with varied rocks.
    """
    name = "RockWorker"
    
    def execute(self, scene: SceneCheckpoint, params: Dict[str, Any], materials: Any, tools: Any) -> None:
        # ---------------------------------------------------------------------
        # 1. Determine Vertical Bounds
        # ---------------------------------------------------------------------
        ballast_bounds = self._calculate_ballast_bounds(scene)
        if not ballast_bounds:
            return

        start_y, top_y = ballast_bounds
        
        # ---------------------------------------------------------------------
        # 2. Material Setup
        # ---------------------------------------------------------------------
        rock_mat = materials.get_material("bal_rock")
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
            else:
                strategy = PoissonDiskPacking()
                
        # No caching logic - always generate fresh
        print(f"[{self.name}] Generating fresh rocks (Strategy: {strategy.__class__.__name__})")
        
        # Use RockCollection for domain logic
        rock_collection = RockCollection()
        
        total_rocks, highest_rock_y = self._pack_all_layers(
            scene, start_y, top_y, strategy, rock_collection
        )
        scene.metadata['packing_source'] = 'generated'
        scene.metadata['rock_count'] = total_rocks
        
        # ---------------------------------------------------------------------
        # 5. Serialization and Persistence
        # ---------------------------------------------------------------------
        self._store_results(scene, start_y, top_y, highest_rock_y, rock_collection)
        
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
                         strategy: Any, rock_collection: RockCollection) -> tuple[int, float]:
        """Iterates through layers and packs rocks."""
        ballast_thickness = top_y - start_y
        n_layers = scene.config.rock_layers
        layer_height = ballast_thickness / n_layers
        
        # Use UNIFORM size distribution across all layers (literature-accurate)
        # Fresh ballast has consistent grading throughout depth (20-60mm specification)
        # Degradation/segregation occurs over time, not as initial design
        r_min = scene.config.rock_radius_min
        r_max = scene.config.rock_radius_max
        
        domain_x, _, _ = _get_domain_params(scene)
             
        z_start = scene.config.rock_z_start
        z_end = scene.config.rock_z_end
        if scene.work_order:
             z_start = scene.work_order.get_input('rock_z_start', z_start)
             z_end = scene.work_order.get_input('rock_z_end', z_end)
             
        total_rocks = 0
        highest_rock_y = start_y

        for i in range(n_layers):
            # Non-overlapping layer boundaries (clean slicing for computational efficiency)
            y_min = start_y + i * layer_height
            y_max = start_y + (i + 1) * layer_height

            # UNIFORM radius range for all layers (no artificial grading)
            rad_min_i = r_min
            rad_max_i = r_max
            
            bounds = PackingBounds(0.0, domain_x, y_min, y_max)
            
            rocks = self._generate_rocks_for_layer(
                scene, strategy, bounds, rad_min_i, rad_max_i, i
            )
            
            for rock in rocks:
                # Store 3D extent in rock object for domain model completeness
                rock.z_start = z_start
                rock.z_end = z_end
                
                cmd = CylinderCommand(
                    rock.x, rock.y, z_start,
                    rock.x, rock.y, z_end,
                    rock.radius, "bal_rock"
                )
                scene.add_geometry(cmd)
                
                # Add to collection
                rock_collection.add(rock)
                
                # Keep legacy list for now just in case, but prefer collection
                scene.rock_positions.append(rock)
                
                highest_rock_y = max(highest_rock_y, rock.y + rock.radius)
                total_rocks += 1
                
        return total_rocks, highest_rock_y

    def _generate_rocks_for_layer(self, scene: SceneCheckpoint, strategy: Any, 
                                  bounds: PackingBounds, r_min: float, r_max: float, 
                                  layer_idx: int) -> List[Any]:
        """Tries primary strategy, falls back to GridPacking if needed."""
        target_fill = scene.config.rock_packing_target_fill
        max_attempts = scene.config.rock_packing_max_attempts
        
        rocks = strategy.generate_rocks(
            bounds, r_min, r_max, target_fill, max_attempts
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
                       highest_y: float, rock_collection: RockCollection) -> None:
        """Stores rock model in WorkOrder/DataFrame."""
        if not scene.work_order: return
        
        domain_x, _, _ = _get_domain_params(scene)

        # Use RockCollection to calculate density/porosity
        achieved_density = rock_collection.calculate_density_monte_carlo(
            domain_x, start_y, top_y, samples=5000
        )
            
        porosity = max(0.0, 1.0 - achieved_density)
        
        scene.metadata['achieved_density'] = achieved_density
        scene.metadata['porosity'] = porosity
        
        print(f"[{self.name}] Achieved Density: {achieved_density:.3f}, Porosity: {porosity:.3f}")
        
        # Store as DataFrame for backward compatibility and analysis
        # Also store the Collection itself if needed (but serializing objects can be tricky across boundaries)
        # For now, we stick to DataFrame as the "Output" contract
        
        z_start = scene.config.rock_z_start # Defaults
        z_end = scene.config.rock_z_end
        if scene.work_order:
             z_start = scene.work_order.get_input('rock_z_start', z_start)
             z_end = scene.work_order.get_input('rock_z_end', z_end)

        df = rock_collection.to_dataframe(default_z_start=z_start, default_z_end=z_end)
        
        scene.work_order.set('rock_model', df, self.name)
        # Also store the collection object for direct memory access by subsequent workers
        scene.work_order.set('rock_collection', rock_collection, self.name) 
        
        scene.work_order.set('highest_rock_y', highest_y, self.name)
        scene.work_order.set('porosity', porosity, self.name)
        
    # Remove _calculate_density_monte_carlo (moved to RockCollection)

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
        # 1. Check if fouling is needed
        work_order = scene.work_order
        if not work_order:
            pvc = params.get('pvc', 0.0)
            moisture = params.get('moisture', 0.0)
        else:
            pvc = work_order.get_input('pvc', 0.0)
            moisture = work_order.get_input('moisture', 0.0)
            
        scene.metadata['pvc'] = pvc
        scene.metadata['moisture'] = moisture
        
        porosity = scene.metadata.get('porosity', 0.4)
        if work_order and not 'porosity' in scene.metadata: 
            porosity = work_order.get_input('porosity', 0.4)
            
        scene.metadata['used_porosity'] = porosity 
        scene.metadata['FI_class'] = classify_pvc(pvc, porosity=porosity)
        
        print(f"[{self.name}] FI Class: {scene.metadata['FI_class']} (PVC={pvc}%, n={porosity:.3f})")
            
        if pvc <= 0:
            return 
            
        if work_order:
            start_y = work_order.get('ballast_bottom_y', 0.5)
            ballast_thickness = work_order.get('ballast_thickness', 0.4)
        else:
            start_y = scene.metadata.get('ballast_bottom_y', 0.5)
            ballast_thickness = scene.metadata.get('ballast_thickness', 0.4)

        domain_x, _, domain_z = _get_domain_params(scene, work_order)
            
        pvc_fraction = min(max(pvc, 0), 100) / 100.0
        fouling_height = ballast_thickness * pvc_fraction
        
        foul_mat = materials.get_material("bal_foul_granular", moisture=moisture)
        scene.add_material(foul_mat)
        
        # 4. Generate Settled Layer
        settled_fraction = scene.config.fouling_settled_fraction
        settled_h = fouling_height * settled_fraction
        
        if settled_h > 2e-3: 
            foul_horizon_y = start_y + settled_h
            self._generate_settled_layer(scene, start_y, foul_horizon_y, domain_x, domain_z)
            settled_top = foul_horizon_y
        else:
            settled_top = start_y
            
        # 5. Generate Dispersed Particles
        disp_top = start_y + fouling_height
        self._generate_dispersed_particles(
            scene, settled_top, disp_top, 
            pvc_fraction, domain_x, domain_z
        )

    def _generate_settled_layer(self, scene: SceneCheckpoint, y_start: float, y_end: float, 
                                domain_x: float, domain_z: float) -> None:
        """Generates the solid block of settled fouling material."""
        box_cmd = BoxCommand(
            0, y_start, 0,
            domain_x, y_end, domain_z,
            "bal_foul_granular"
        )
        scene.add_geometry(box_cmd)

    def _generate_dispersed_particles(self, scene: SceneCheckpoint, y_min: float, y_max: float, 
                                     pvc_fraction: float, domain_x: float, domain_z: float) -> None:
        """Generates dispersed fouling particles in the voids between rocks."""
        if y_max <= y_min:
            return

        target_count = int(200 * pvc_fraction)
        
        if target_count <= 0:
            return

        placed = 0
        max_attempts = target_count * 10
        
        # Retrieve RockCollection for efficient overlap checking
        rocks_collection = self._get_rock_collection(scene)
        # Fallback to list if collection not found
        rocks_list = rocks_collection.rocks if rocks_collection else scene.rock_positions
        
        for _ in range(max_attempts):
            if placed >= target_count: break
            
            x = random.uniform(0, domain_x)
            y = random.uniform(y_min, y_max)
            r = random.uniform(scene.config.fouling_particle_size_min, scene.config.fouling_particle_size_max)
            
            if self._is_in_void(x, y, r, rocks_list):
                scene.add_geometry(CylinderCommand(
                    x, y, 0, x, y, domain_z,
                    r, "bal_foul_granular"
                ))
                placed += 1

    def _get_rock_collection(self, scene: SceneCheckpoint) -> Optional[RockCollection]:
        """Retrieve RockCollection or reconstruct from DataFrame."""
        if scene.work_order:
             # Try direct object access first
             collection = scene.work_order.get('rock_collection')
             if collection: return collection
             
             # Fallback to DataFrame reconstruction
             df = scene.work_order.get('rock_model')
             if df is not None:
                 return RockCollection.from_dataframe(df)
                 
        return None

    def _is_in_void(self, x: float, y: float, r: float, rocks: List[Any]) -> bool:
        """Check if a particle at (x,y) with radius r overlaps any rock."""
        for rock in rocks:
            dist_sq = (x - rock.x)**2 + (y - rock.y)**2
            min_dist = rock.radius + r
            if dist_sq < min_dist**2:
                return False 
        return True
            
    def quality_check(self, scene: SceneCheckpoint) -> List[str]:
        return []


class AntennaWorker(Worker):
    """
    Places transmitter and receiver antenna.
    """
    name = "AntennaWorker"
    
    def execute(self, scene: SceneCheckpoint, params: Dict[str, Any], materials: Any, tools: Any) -> None:
        # 1. Get Antenna Positions (FIXED from config)
        # Try WorkOrder first (for variant support), else config
        if scene.work_order:
            offset = scene.work_order.get_input('antenna_offset', 0.0)
        else:
            offset = params.get('antenna_offset', 0.0)
        
        # Calculate X/Z positions
        tx_x = scene.config.tx_x + offset
        rx_x = scene.config.rx_x + offset
        tx_rx_z = scene.config.tx_rx_z
        
        # 2. Dynamic Height Calculation (New Logic)
        # Determine height based on highest rock to avoid collision
        if scene.work_order:
            highest_rock_y = scene.work_order.get('highest_rock_y', 0.9)
            clearance = scene.work_order.get_input('antenna_clearance_above_ballast', 
                                                   getattr(scene.config, 'antenna_clearance_above_ballast', 0.05))
            
            # Base height (minimum height e.g. if no rocks)
            min_height = getattr(scene.config, 'tx_rx_y', 0.9)
            
            # Dynamic height: ensure clearance above rocks
            tx_rx_y = max(min_height, highest_rock_y + clearance)
            
             # Log the final decision
            scene.work_order.set('tx_rx_y', tx_rx_y, self.name)
            
        else:
             # Legacy fallback
             tx_rx_y = scene.config.tx_rx_y
             
        # ENFORCE DOMAIN RESTRICTIONS (Fail Fast)
        domain_x, domain_y, domain_z = _get_domain_params(scene)
            
        # Check TX
        if not (0 <= tx_x <= domain_x):
            raise ValueError(f"{self.name}: TX X ({tx_x:.3f}) outside domain [0, {domain_x}]")
        if not (0 <= tx_rx_y <= domain_y):
            raise ValueError(f"{self.name}: TX Y ({tx_rx_y:.3f}) outside domain [0, {domain_y}]")
        if not (0 <= tx_rx_z <= domain_z):
            raise ValueError(f"{self.name}: TX Z ({tx_rx_z:.3f}) outside domain [0, {domain_z}]")
            
        # Check RX
        if not (0 <= rx_x <= domain_x):
            raise ValueError(f"{self.name}: RX X ({rx_x:.3f}) outside domain [0, {domain_x}]")
        
        # 3. Add Waveform
        if scene.config.add_waveform:
            waveform_name = "ricker_src"
            freq_normalized = 1.0  # gprMax normalized time
            center_freq = scene.config.center_freq
            
            waveform = WaveformCommand("ricker", freq_normalized, center_freq, waveform_name)
            scene.add_source(waveform)
        
        # 4. Add Source
        if scene.config.add_source:
            source = HertzianDipoleCommand("z", tx_x, tx_rx_y, tx_rx_z, "ricker_src")
            scene.add_source(source)
        
        # 5. Add Receiver
        receiver = RxCommand(rx_x, tx_rx_y, tx_rx_z)
        scene.add_source(receiver)
        
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
        domain_x, domain_y, domain_z = _get_domain_params(scene)
             
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
            elif isinstance(cmd, RxCommand):
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
                 
        # 3. Check domain bounds (TX, RX must be within domain)
        domain_x, domain_y, domain_z = _get_domain_params(scene)
        
        # Strict bounds checking
        if not (0 <= tx_pos[0] <= domain_x):
                 errors.append(f"AssemblerWorker: TX X ({tx_pos[0]:.3f}) outside domain [0, {domain_x}]")
        if not (0 <= tx_pos[1] <= domain_y):
                 errors.append(f"AssemblerWorker: TX Y ({tx_pos[1]:.3f}) outside domain [0, {domain_y}]")
        if not (0 <= tx_pos[2] <= domain_z):
                 errors.append(f"AssemblerWorker: TX Z ({tx_pos[2]:.3f}) outside domain [0, {domain_z}]")
                 
        if not (0 <= rx_pos[0] <= domain_x):
                 errors.append(f"AssemblerWorker: RX X ({rx_pos[0]:.3f}) outside domain [0, {domain_x}]")
        if not (0 <= rx_pos[1] <= domain_y):
                 errors.append(f"AssemblerWorker: RX Y ({rx_pos[1]:.3f}) outside domain [0, {domain_y}]")
        if not (0 <= rx_pos[2] <= domain_z):
                 errors.append(f"AssemblerWorker: RX Z ({rx_pos[2]:.3f}) outside domain [0, {domain_z}]")
        
        return errors

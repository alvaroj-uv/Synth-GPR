"""
Concrete Worker implementations for the Factory Architecture.

Each worker handles a specific layer or component of the GPR scene.
"""

from typing import List, Dict, Any, TYPE_CHECKING
import random
from .worker import Worker, SceneCheckpoint
from .gpr_commands import BoxCommand, MaterialCommand, CylinderCommand, HertzianDipoleCommand, RxCommand, WaveformCommand
from .rock_packing import PoissonDiskPacking, PackingBounds
from .config import topp_mixing_model

if TYPE_CHECKING:
    from .quality_log import QualityLog


class AirWorker(Worker):
    """
    Paints the background/medium with free_space (air).
    This is typically the first worker in the pipeline.
    """
    name = "AirWorker"
    
    def execute(self, scene: SceneCheckpoint, params: Dict[str, Any], materials: Any, tools: Any) -> None:
        # 1. Add material definition
        # For free_space, we rely on gprMax built-in, but we can explicit it
        # air_mat = materials.get_material("free_space")
        # scene.add_material(air_mat)
        
        # 2. Add geometry covering entire domain
        # #box: 0 0 0 domain_x domain_y domain_z free_space
        scene.add_geometry(BoxCommand(
            0, 0, 0,
            scene.config.domain_x, scene.config.domain_y, scene.config.domain_z,
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
        # mat = materials.get_material("subgrade")
        # scene.add_material(mat)
        
        # Get material from keeper
        mat = materials.get_material("subgrade")
        scene.add_material(mat)
        
        # 2. Add geometry
        # Box from y=0 to y_limit
        # y_limit depends on layer stack: domain_y - air_buffer - ballast - formation
        # But typically we build bottom-up or usage absolute coordinates from configuration
        
        # Simplified logic: Subgrade is the minimal base layer
        # In current logic: Subgrade fills everything below formation
        # Let's assume params provide 'subgrade_height'
        
        # For this example, let's look at how GranularBallastLayer calcualtes it:
        # It usually just fills the remaining space or is a fixed block.
        # Let's assume a "subgrade_depth" parameter or fixed coordinate.
        
        domain_x = scene.config.domain_x
        domain_z = scene.config.domain_z
        
        # Currently, 'subgrade' is often just the layer below formation. 
        # Let's use a fixed height for demonstration or derived from params.
        subgrade_top = scene.config.subgrade_height
        
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
        # 1. Determine start height (top of existing geometry)
        # Use simple max_y of existing solid boxes (ignore air)
        start_y = 0.0
        for cmd in scene.geometry:
            if isinstance(cmd, BoxCommand) and hasattr(cmd, 'y2'):
                # Ignore free_space/air background
                if hasattr(cmd, 'material') and cmd.material == 'free_space':
                    continue
                start_y = max(start_y, cmd.y2)
                
        # 2. Get thickness
        # Try WorkOrder first, then params, then config
        thickness = 0.10 # default
        if scene.work_order:
             thickness = scene.work_order.get_input('formation_thickness', thickness)
        else:
             thickness = params.get('formation_thickness', getattr(scene.config, 'formation_thickness', 0.10))
        
        # 3. Add Material
        # Get material from keeper
        mat = materials.get_material("formation")
        scene.add_material(mat)
        
        # 4. Add Geometry
        top_y = start_y + thickness
        scene.add_geometry(BoxCommand(
            0, start_y, 0,
            scene.config.domain_x, top_y, scene.config.domain_z,
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
            
        # Optional: Check overlap or gap?
        # For now, just existence.
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
        # Find highest point of formation (or generally non-air below)
        for cmd in scene.geometry:
            # Skip air
            if hasattr(cmd, 'material') and cmd.material == 'free_space':
                continue
            if hasattr(cmd, 'y2'):
                start_y = max(start_y, cmd.y2)
                
        # 2. Get thickness
        # Ballast thickness typically 0.3 - 0.5m
        thickness = 0.40
        if scene.work_order:
             thickness = scene.work_order.get_input('ballast_thickness', getattr(scene.config, 'max_ballast_thickness', 0.40))
        else:
             thickness = params.get('ballast_thickness', getattr(scene.config, 'max_ballast_thickness', 0.40))
        
        # 3. Determine Background Material
        # Let's assume for now we just define the BOUNDARIES for the RockWorker to use.
        top_y = start_y + thickness
        
        # Sync with WorkOrder (Single Source of Truth)
        if scene.work_order:
            scene.work_order.set('ballast_bottom_y', start_y, self.name)
            scene.work_order.set('ballast_top_y', top_y, self.name)
            scene.work_order.set('ballast_thickness', thickness, self.name)
        else:
            scene.log_issue(self.name, "missing_dependency", "warning", "No WorkOrder attached. Outputs lost.")
        
        # Optional: Add a comment or a bounding box for visualization/debug
        # scene.add_geometry(CommentCommand(f"Ballast Layer: {start_y:.3f} - {top_y:.3f}"))
        
    def quality_check(self, scene: SceneCheckpoint) -> List[str]:
        # Check WorkOrder instead of metadata
        if not scene.work_order:
            return ["BallastWorker: No WorkOrder attached"]
        
        if scene.work_order.get('ballast_top_y') is None:
            return ["BallastWorker: Output 'ballast_top_y' not found in WorkOrder"]
        return []


class RockWorker(Worker):
    """
    Places rock aggregates within the ballast layer.
    
    Uses packing strategies (e.g., specific algorithms from ToolWarehouse)
    to fill the ballast volume with varied rocks.
    """
    name = "RockWorker"
    
    def execute(self, scene: SceneCheckpoint, params: Dict[str, Any], materials: Any, tools: Any) -> None:
        # 1. Get Bounds (Strictly from WorkOrder)
        start_y = 0.5
        top_y = 0.9
        
        if scene.work_order:
            start_y = scene.work_order.get('ballast_bottom_y', start_y)
            top_y = scene.work_order.get('ballast_top_y', top_y)
        else:
            scene.log_issue(self.name, "missing_dependency", "error", "No WorkOrder found. Cannot determine ballast bounds.")
            return # Abort
            
        # Get rock material from keeper
        rock_mat = materials.get_material("bal_rock")
        scene.add_material(rock_mat)
            
        ballast_thickness = top_y - start_y
        
        # 2. Get Packing Strategy
        # In full factory key 'packing_strategy' might come from Recipe
        # Default to PoissonDisk if not provided
        strategy = params.get('packing_strategy', PoissonDiskPacking())
        
        # 3. Layered Generation Logic (Ported from GranularBallastLayer)
        n_layers = scene.config.rock_layers
        layer_height = ballast_thickness / n_layers
        
        # Grading: larger rocks at bottom, smaller at top?
        # Or mixed? Existing logic had grading.
        r_min = scene.config.rock_radius_min
        r_max = scene.config.rock_radius_max
        radius_step = (r_max - r_min) / n_layers
        
        target_fill = scene.config.rock_packing_target_fill
        max_attempts = scene.config.rock_packing_max_attempts
        
        total_rocks = 0
        highest_rock_y = start_y  # Track highest point
        removed_rocks = 0  # Track removed rocks
        
        # Calculate maximum allowed rock height
        # Antenna is at tx_rx_y (e.g., 0.904m)
        # Rocks must stay 50cm below antenna
        # max_rock_top = tx_rx_y - clearance
        max_allowed_rock_top = scene.config.tx_rx_y - scene.config.antenna_clearance_above_ballast
        
        for i in range(n_layers):
            y_min = start_y + i * layer_height
            y_max = start_y + (i + 1) * layer_height
            
            # Overlap for density
            if i > 0:
                y_min -= layer_height
                
            # Grading logic: i=0 is bottom
            rad_min_i = r_min + i * radius_step
            rad_max_i = rad_min_i + radius_step
            
            bounds = PackingBounds(0.0, scene.config.domain_x, y_min, y_max)
            
            rocks = strategy.generate_rocks(
                bounds, rad_min_i, rad_max_i,
                target_fill, max_attempts
            )
            
            for rock in rocks:
                # Check if rock would exceed domain limit
                rock_top = rock.y + rock.radius
                
                if rock_top > max_allowed_rock_top:
                    # Skip this rock - would make domain too tall
                    removed_rocks += 1
                    continue
                
                cmd = CylinderCommand(
                    rock.x, rock.y, 0.0,
                    rock.x, rock.y, scene.config.domain_z,
                    rock.radius, "bal_rock"
                )
                scene.add_geometry(cmd)
                
                # Register for Quality Checks
                scene.rock_positions.append(rock)
                
                # Track highest point (center + radius)
                highest_rock_y = max(highest_rock_y, rock_top)
                
                total_rocks += 1
            
        scene.metadata['rock_count'] = total_rocks
        
        # Log if rocks were removed
        if removed_rocks > 0 and scene.work_order:
            scene.work_order.log(
                f"Removed {removed_rocks} rocks to maintain domain height limit (max_domain_y={scene.config.max_domain_y}m)",
                self.name
            )
        
        # Store highest rock position for antenna placement
        if scene.work_order:
            scene.work_order.set('highest_rock_y', highest_rock_y, self.name)
        
    def quality_check(self, scene: SceneCheckpoint) -> List[str]:
        if not scene.rock_positions:
            return ["RockWorker: No rocks placed"]
        
        # Check for floating rocks
        # This is expensive, maybe sample check?
        # Or rely on SceneValidator/Assembler
        
        # Check if density met expectations (heuristic)
        if scene.metadata.get('rock_count', 0) < 10:
             return ["RockWorker: Suspiciously low rock count"]
             
        return []


class FoulingWorker(Worker):
    """
    Simulates ballast fouling: fine materials (soil, sand, coal) filling voids.
    Controlled by PVC (Percentage Void Contamination): 0%=clean, 100%=heavily fouled.
    Fouling reduces drainage/performance - critical for track condition assessment.
    
    Generates:
    1. Settled Fouling layer at the bottom.
    2. Dispersed Fouling particles in the upper voids.
    """
    name = "FoulingWorker"
    
    def execute(self, scene: SceneCheckpoint, params: Dict[str, Any], materials: Any, tools: Any) -> None:
        # 1. Check if fouling is needed
        # WorkOrder should contain 'pvc' (Percentage Void Contamination) or 'fouling_level'
        work_order = scene.work_order
        if not work_order:
            # Fallback
            pvc = params.get('pvc', 0.0)
            moisture = params.get('moisture', 0.0)
        else:
            pvc = work_order.get_input('pvc', 0.0)
            moisture = work_order.get_input('moisture', 0.0)
            
        # Log to metadata for file header
        scene.metadata['pvc'] = pvc
        scene.metadata['moisture'] = moisture
            
        if pvc <= 0:
            return # No fouling
            
        # 2. Get Geometry Bounds
        # We need ballast_bottom, ballast_thickness
        if work_order:
            start_y = work_order.get('ballast_bottom_y', 0.5)
            ballast_thickness = work_order.get('ballast_thickness', 0.4)
        else:
            start_y = scene.metadata.get('ballast_bottom_y', 0.5)
            ballast_thickness = scene.metadata.get('ballast_thickness', 0.4)
            
        # Calculate fouling properties
        pvc_fraction = min(max(pvc, 0), 100) / 100.0
        fouling_height = ballast_thickness * pvc_fraction
        
        # Get fouling material from keeper (dynamic based on moisture)
        foul_mat = materials.get_material("bal_foul_granular", moisture=moisture)
        scene.add_material(foul_mat)
        
        # 4. Generate Settled Layer (Bottom 70% of fouling height)
        settled_fraction = scene.config.fouling_settled_fraction
        settled_h = fouling_height * settled_fraction
        
        if settled_h > 2e-3: # Enforce 2mm min thickness to avoid geometry errors
            foul_horizon_y = start_y + settled_h
            scene.add_geometry(BoxCommand(
                0, start_y, 0,
                scene.config.domain_x, foul_horizon_y, scene.config.domain_z,
                "bal_foul_granular"
            ))
            
            # Log for Dispersed
            settled_top = foul_horizon_y
        else:
            settled_top = start_y
            
        # 5. Generate Dispersed Particles (Voids)
        # Range: settled_top to start_y + fouling_height
        disp_top = start_y + fouling_height
        
        # Count based on PVC
        # Legacy: BASE_PARTICLE_COUNT_PER_100_PVC * (pvc / 100)
        BASE_COUNT = 50 * 5 # Legacy scaling was a bit implicit, let's target specific density
        target_count = int(200 * pvc_fraction) # Simplified heuristic
        
        if target_count > 0 and disp_top > settled_top:
            placed = 0
            max_attempts = target_count * 10
            
            # Get rocks to check overlap
            # Rocks are cylinders (x, y, r)
            rocks = scene.rock_positions
            
            for _ in range(max_attempts):
                if placed >= target_count: break
                
                # Random pos
                x = random.uniform(0, scene.config.domain_x)
                y = random.uniform(settled_top, disp_top)
                
                # Small particle size
                r = random.uniform(scene.config.fouling_particle_size_min, scene.config.fouling_particle_size_max)
                
                # 2D overlap check (simple void check)
                in_void = True
                for rock in rocks:
                    # rock is simple object with x, y, radius
                    dist_sq = (x - rock.x)**2 + (y - rock.y)**2
                    min_dist = rock.radius + r
                    if dist_sq < min_dist**2:
                        in_void = False
                        break
                
                if in_void:
                    scene.add_geometry(CylinderCommand(
                        x, y, 0, x, y, scene.config.domain_z,
                        r, "bal_foul_granular"
                    ))
                    placed += 1
            
    def quality_check(self, scene: SceneCheckpoint) -> List[str]:
        # Optional: Check fouling integrity
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
            offset = scene.work_order.get('antenna_offset', 0.0)
        else:
            offset = params.get('antenna_offset', 0.0)
        
        # Use FIXED antenna height from config
        tx_x = scene.config.tx_x + offset
        rx_x = scene.config.rx_x + offset
        tx_rx_y = scene.config.tx_rx_y  # FIXED HEIGHT
        tx_rx_z = scene.config.tx_rx_z
        
        # 2. Add Waveform
        if scene.config.add_waveform:
            waveform_name = "ricker_src"
            freq_normalized = 1.0  # gprMax normalized time
            center_freq = scene.config.center_freq
            
            waveform = WaveformCommand("ricker", freq_normalized, center_freq, waveform_name)
            scene.add_source(waveform)
        
        # 3. Add Source
        if scene.config.add_source:
            source = HertzianDipoleCommand("z", tx_x, tx_rx_y, tx_rx_z, "ricker_src")
            scene.add_source(source)
        
        # 4. Add Receiver
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
        for rock in scene.rock_positions:
            # 2D distance check
            tx_dist = ((tx_pos[0] - rock.x)**2 + (tx_pos[1] - rock.y)**2)**0.5
            rx_dist = ((rx_pos[0] - rock.x)**2 + (rx_pos[1] - rock.y)**2)**0.5
            
            clearance = scene.config.antenna_rock_clearance
            
            if tx_dist < (rock.radius + clearance):
                 errors.append(f"AssemblerWorker: TX too close to rock at ({rock.x:.3f}, {rock.y:.3f})")
                 
            if rx_dist < (rock.radius + clearance):
                 errors.append(f"AssemblerWorker: RX too close to rock at ({rock.x:.3f}, {rock.y:.3f})")
                 
        # 3. Check domain bounds (TX, RX must be within domain)
        domain_x = scene.config.domain_x
        domain_y = scene.config.domain_y
        domain_z = scene.config.domain_z
        
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

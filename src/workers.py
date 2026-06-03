"""
Concrete Worker implementations for the Factory Architecture.

Each worker handles a specific layer or component of the GPR scene.
"""
from typing import List, Dict, Any
from .worker import Worker, SceneCheckpoint
from .gpr_commands import BoxCommand, HertzianDipoleCommand, RxCommand, WaveformCommand
from .constants import MC, PC




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

        if scene.coordinate_system:
            from src.domain import Layer
            bounds = scene.coordinate_system.bounds(Layer.SUBGRADE)
            subgrade_top = bounds.top
        else:
            subgrade_top = getattr(scene.config, 'subgrade_height', 0.5)
            if scene.work_order:
                subgrade_top = scene.work_order.get_input('subgrade_height', subgrade_top)

        if scene.work_order:
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
    Bookkeeping-only worker: computes ballast layer extents and publishes
    them to the WorkOrder (ballast_bottom_y, ballast_top_y, ballast_thickness).
    Emits no geometry — GranularMatrixWorker reads these values and fills the volume.
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



class AntennaWorker(Worker):
    """
    Places transmitter and receiver antenna.
    """
    name = "AntennaWorker"
    
    def execute(self, scene: SceneCheckpoint, params: Dict[str, Any], materials: Any, tools: Any) -> None:
        from src.domain import Point3D, Anchor

        # 1. Get Antenna Positions (using CoordinateSystem)
        # Antenna height is now always computed from LayerStack, not hardcoded
        if not scene.coordinate_system:
            raise RuntimeError("AntennaWorker requires CoordinateSystem to be initialized")

        # Get antenna offset (for variant support)
        if scene.work_order:
            offset = scene.work_order.get_input('antenna_offset', 0.0)
        else:
            offset = params.get('antenna_offset', 0.0)

        # Antenna Y is computed from layer stack: ballast_top + antenna_clearance
        tx_rx_y = scene.coordinate_system.get_y(Anchor.ANTENNA_LEVEL)
        domain_top = scene.coordinate_system.get_y(Anchor.DOMAIN_TOP)

        # Check if antenna Y exceeds domain bounds (CRITICAL)
        if tx_rx_y > domain_top:
            # Provide diagnostic info
            import warnings
            ballast_top = scene.coordinate_system.get_y(Anchor.BALLAST_TOP)
            ant_clearance = scene.config.antenna_clearance_above_ballast
            msg = (
                f"Antenna Y ({tx_rx_y:.4f}) exceeds domain height ({domain_top:.4f}).\n"
                f"  Ballast top:      {ballast_top:.4f} m\n"
                f"  Antenna clearance: {ant_clearance:.4f} m\n"
                f"  Computed antenna Y: {ballast_top:.4f} + {ant_clearance:.4f} = {tx_rx_y:.4f} m\n"
                f"  Domain height:     {domain_top:.4f} m\n"
                f"  Deficit:           {tx_rx_y - domain_top:.4f} m\n"
                f"Possible fixes:\n"
                f"  1. Increase antenna_clearance_above_ballast or\n"
                f"  2. Reduce antenna_clearance_above_ballast or\n"
                f"  3. Increase domain_y in config"
            )
            raise ValueError(f"{self.name}: {msg}")

        # Determine Horizontal Positions
        tx_x = scene.config.tx_x + offset
        rx_x = tx_x if scene.config.monostatic else scene.config.rx_x + offset
        tx_rx_z = scene.config.tx_rx_z

        # Create Point3D objects (fixing Primitive Obsession #2)
        tx_position = Point3D(tx_x, tx_rx_y, tx_rx_z)
        rx_position = Point3D(rx_x, tx_rx_y, tx_rx_z)

        # Validate TX/RX positions within domain (all dimensions)
        valid_tx = scene.coordinate_system.validate_point(tx_position)
        valid_rx = scene.coordinate_system.validate_point(rx_position)

        if not valid_tx:
            domain_x = scene.config.domain_x
            domain_z = scene.config.domain_z
            raise ValueError(
                f"{self.name}: TX Position invalid (outside domain bounds).\n"
                f"  TX position: ({tx_position.x:.4f}, {tx_position.y:.4f}, {tx_position.z:.4f}) m\n"
                f"  Domain bounds: [0, {domain_x:.4f}] Ã— [0, {domain_top:.4f}] Ã— [0, {domain_z:.4f}] m\n"
                f"  Issue: X={tx_position.x:.4f} (valid: 0-{domain_x:.4f})" if not (0 <= tx_x <= domain_x)
                else f"  Issue: Y={tx_position.y:.4f} (valid: 0-{domain_top:.4f})" if not (0 <= tx_rx_y <= domain_top)
                else f"  Issue: Z={tx_position.z:.4f} (valid: 0-{domain_z:.4f})"
            )

        if not valid_rx:
            domain_x = scene.config.domain_x
            domain_z = scene.config.domain_z
            raise ValueError(
                f"{self.name}: RX Position invalid (outside domain bounds).\n"
                f"  RX position: ({rx_position.x:.4f}, {rx_position.y:.4f}, {rx_position.z:.4f}) m\n"
                f"  Domain bounds: [0, {domain_x:.4f}] Ã— [0, {domain_top:.4f}] Ã— [0, {domain_z:.4f}] m\n"
                f"  Issue: X={rx_position.x:.4f} (valid: 0-{domain_x:.4f})" if not (0 <= rx_position.x <= domain_x)
                else f"  Issue: Y={rx_position.y:.4f} (valid: 0-{domain_top:.4f})" if not (0 <= rx_position.y <= domain_top)
                else f"  Issue: Z={rx_position.z:.4f} (valid: 0-{domain_z:.4f})"
            )

        # Layer 4: PML Clearance Validation (gprMax Best Practice)
        # Sources must be kept at least 15 cells away from PML boundaries
        # See: https://docs.gprmax.com/en/latest/gprmodelling.html
        pml_thickness = scene.config.pml_layers * scene.config.dx
        pml_x_min = pml_thickness
        pml_x_max = scene.config.domain_x - pml_thickness
        pml_y_min = pml_thickness
        pml_y_max = domain_top - pml_thickness

        for pos, name in [(tx_position, "TX"), (rx_position, "RX")]:
            if not (pml_x_min <= pos.x <= pml_x_max and pml_y_min <= pos.y <= pml_y_max):
                raise ValueError(
                    f"{self.name}: {name} too close to PML absorbing boundary.\n"
                    f"  Position: ({pos.x:.4f}, {pos.y:.4f}, {pos.z:.4f}) m\n"
                    f"  Safe region (outside PML): X=[{pml_x_min:.4f}, {pml_x_max:.4f}], "
                    f"Y=[{pml_y_min:.4f}, {pml_y_max:.4f}]\n"
                    f"  PML thickness: {pml_thickness:.4f} m ({scene.config.pml_layers} cells Ã— {scene.config.dx:.4f} m/cell)\n"
                    f"  Margin to PML: X_min={pos.x-pml_x_min:+.4f} m, X_max={pml_x_max-pos.x:+.4f} m, "
                    f"Y_min={pos.y-pml_y_min:+.4f} m, Y_max={pml_y_max-pos.y:+.4f} m\n"
                    f"Fix: Move antenna further from domain edges, or reduce pml_layers in config"
                )

        # Layer 5: Free Space Above Antenna (gprMax Best Practice - Warning)
        # gprMax recommends 15-20 cells of free space above antenna
        # See: https://docs.gprmax.com/en/latest/gprmodelling.html
        min_cells_above = 15  # Conservative: 15 cells minimum
        free_space_required = min_cells_above * scene.config.dy
        actual_free_space = domain_top - tx_rx_y

        if actual_free_space < free_space_required:
            import warnings
            warning_msg = (
                f"Limited free space above antenna (gprMax recommends 15-20 cells).\n"
                f"  Antenna Y: {tx_rx_y:.4f} m\n"
                f"  Domain top: {domain_top:.4f} m\n"
                f"  Available: {actual_free_space:.4f} m ({actual_free_space / scene.config.dy:.1f} cells)\n"
                f"  Recommended: {free_space_required:.4f} m ({min_cells_above} cells)\n"
                f"  Deficit: {free_space_required - actual_free_space:.4f} m\n"
                f"Suggestion: Increase domain_y or reduce antenna_clearance_above_ballast"
            )
            warnings.warn(f"{self.name}: {warning_msg}", UserWarning)
            if scene.work_order:
                scene.work_order.log(f"[WARNING] {warning_msg}", self.name)

        # 3. Add Waveform
        # The source identifier stays "ricker_src" for backward compatibility
        # (the dipole references it by name), regardless of waveform type.
        waveform_name = "ricker_src"
        wf_type = getattr(scene.config, 'source_waveform', 'ricker').lower()
        if scene.config.add_waveform:
            freq_normalized = 1.0  # gprMax amplitude (normalized)
            if wf_type == 'gaussian':
                # GSSI-antenna-style excitation: Gaussian at the antenna resonant
                # frequency. Matches the real antenna's source spectrum without
                # adding any 3D antenna geometry (stays 2D / same sim cost).
                exc_freq = getattr(scene.config, 'gaussian_excitation_freq', None)
                if exc_freq is None:
                    # 1.71 GHz is gprMax's optimised excitation for the 1.5 GHz
                    # GSSI model; otherwise fall back to the configured centre freq.
                    exc_freq = 1.71e9 if abs(scene.config.center_freq - 1.5e9) < 1e8 \
                        else scene.config.center_freq
                waveform = WaveformCommand("gaussian", freq_normalized, exc_freq, waveform_name)
            else:
                waveform = WaveformCommand("ricker", freq_normalized,
                                           scene.config.center_freq, waveform_name)
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
            if not scene.coordinate_system.validate_point(rx_pos):
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

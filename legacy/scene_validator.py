from typing import List, Optional
from .scene_descriptor import SceneDefinition
from .gpr_commands import (
    BoxCommand, CylinderCommand, DomainCommand, DxDyDzCommand, 
    TimeWindowCommand, WaveformCommand, HertzianDipoleCommand, MaterialCommand
)
from .quality_log import QualityLog  # NEW: Optional quality logging

class SceneValidator:
    """
    Validates the generated scene against physical limits and gprMax requirements.
    Ensures that geometry is within bounds and properly defined before writing to file.
    
    Optionally logs issues to a QualityLog for ML analysis.
    """

    @staticmethod
    def validate(
        scene: SceneDefinition, 
        quality_log: Optional[QualityLog] = None  # NEW: Optional log
    ) -> List[str]:
        """
        Validate the scene definition.

        Args:
            scene: The SceneDefinition to validate.
            quality_log: Optional QualityLog to record issues for ML learning.

        Returns:
            List of error strings. Empty list implies validity.
        """
        errors = []
        config = scene.config
        
        # Helper: log to QualityLog if provided (doesn't change error list behavior)
        def log_issue(issue_type: str, severity: str, description: str, context: dict = None):
            if quality_log is not None:
                quality_log.log_issue(
                    worker="SceneValidator",
                    issue_type=issue_type,
                    severity=severity,
                    description=description,
                    context=context or {}
                )
        
        # 1. Essential Commands Check
        # We check if the command lists contain the required types
        has_domain = any(isinstance(c, DomainCommand) for c in scene.domain_commands)
        has_grid = any(isinstance(c, DxDyDzCommand) for c in scene.domain_commands)
        has_time = any(isinstance(c, TimeWindowCommand) for c in scene.domain_commands)
        
        if not has_domain: 
            errors.append("Missing essential command: #domain")
            log_issue("missing_command", "critical", "Missing #domain", {"command": "#domain"})
        if not has_grid: 
            errors.append("Missing essential command: #dx_dy_dz")
            log_issue("missing_command", "critical", "Missing #dx_dy_dz", {"command": "#dx_dy_dz"})
        if not has_time: 
            errors.append("Missing essential command: #time_window")
            log_issue("missing_command", "critical", "Missing #time_window", {"command": "#time_window"})
        
        # 2. Reference Integrity: Waveforms
        # Collect defined waveform IDs
        defined_waveforms = set()
        for cmd in scene.source_commands:
            if isinstance(cmd, WaveformCommand):
                defined_waveforms.add(cmd.identifier)

        # Check sources usage
        for cmd in scene.source_commands:
            if isinstance(cmd, HertzianDipoleCommand):
                # signature: #hertzian_dipole: pol x y z waveform
                if cmd.waveform not in defined_waveforms:
                    errors.append(f"Source references undefined waveform: '{cmd.waveform}'")
            # Add other source types if they use waveforms (magnetic_dipole, etc)

        # 3. Reference Integrity: Materials
        defined_materials = set()
        # Add standard built-in materials
        defined_materials.add("free_space")
        defined_materials.add("pec")
        
        for cmd in scene.material_commands:
            if isinstance(cmd, MaterialCommand):
                defined_materials.add(cmd.identifier)

        # Check geometry usage
        for cmd in scene.geometry_commands:
            if hasattr(cmd, 'material'):
                if cmd.material not in defined_materials:
                    # Soft warning or hard error? gprMax errors.
                    errors.append(f"Geometry references undefined material: '{cmd.material}'")

        # 4. Domain & Geometry Logic
        dx, dy, dz = config.domain_x, config.domain_y, config.domain_z
        
        for idx, cmd in enumerate(scene.geometry_commands):
            cmd_prefix = f"Cmd #{idx} ({type(cmd).__name__})"
            
            if isinstance(cmd, BoxCommand):
                # Coordinate Order (Lower < Upper)
                if cmd.x1 >= cmd.x2:
                    errors.append(f"{cmd_prefix}: Invalid X range {cmd.x1} >= {cmd.x2}")
                if cmd.y1 >= cmd.y2:
                    errors.append(f"{cmd_prefix}: Invalid Y range {cmd.y1} >= {cmd.y2}")
                if cmd.z1 >= cmd.z2:
                    errors.append(f"{cmd_prefix}: Invalid Z range {cmd.z1} >= {cmd.z2}")

                # Domain Bounds
                tol = 1e-4
                if cmd.x1 < -tol or cmd.x2 > dx + tol:
                     errors.append(f"{cmd_prefix}: X bounds out of domain (0-{dx}): [{cmd.x1}, {cmd.x2}]")
                if cmd.y1 < -tol or cmd.y2 > dy + tol:
                     errors.append(f"{cmd_prefix}: Y bounds out of domain (0-{dy}): [{cmd.y1}, {cmd.y2}]")
                if cmd.z1 < -tol or cmd.z2 > dz + tol:
                     errors.append(f"{cmd_prefix}: Z bounds out of domain (0-{dz}): [{cmd.z1}, {cmd.z2}]")

            elif isinstance(cmd, CylinderCommand):
                if cmd.radius <= 0:
                     errors.append(f"{cmd_prefix}: Invalid radius {cmd.radius}")
                
                # Check antenna clearance for rocks
                if 'bal_rock' in cmd.material:
                    rock_top_y = cmd.y1 + cmd.radius  # y1 is center for vertical cylinders
                    antenna_y = config.tx_rx_y
                    min_clearance = 0.50  # 50cm minimum clearance
                    
                    if rock_top_y > antenna_y - min_clearance:
                        errors.append(
                            f"{cmd_prefix}: Rock too close to antenna! "
                            f"Rock top at {rock_top_y:.3f}m, antenna at {antenna_y:.3f}m "
                            f"(needs {min_clearance}m clearance)"
                        )
                        # Log for ML learning - includes context for analysis
                        log_issue(
                            "antenna_clearance", 
                            "error",
                            "Rock breaches antenna clearance zone",
                            {
                                "rock_x": cmd.x1,
                                "rock_y": cmd.y1,
                                "rock_radius": cmd.radius,
                                "rock_top_y": rock_top_y,
                                "antenna_y": antenna_y,
                                "clearance_needed": min_clearance,
                                "clearance_actual": antenna_y - rock_top_y
                            }
                        )
                
        # Metadata consistency
        if 'fouling_thickness' in scene.metadata:
            ft = scene.metadata['fouling_thickness']
            if ft < 0:
                errors.append(f"Metadata: Negative fouling thickness {ft}")

        # 5. Antenna Spacing Check (TX and RX must be properly separated)
        # This is a config-level check since RX isn't tracked as a command object
        expected_spacing = abs(config.rx_x - config.tx_x)
        if expected_spacing < 0.01:  # 1cm minimum
            errors.append(
                f"Antenna spacing too small! TX at x={config.tx_x:.3f}, "
                f"RX at x={config.rx_x:.3f} (spacing: {expected_spacing*100:.1f}cm, min: 1cm)"
            )

        return errors

# GPRMax File Writer with validation and structured output.
# 
# Implements patterns from gprMax source:
# 1. Command Validation - ensures required commands present, no duplicates
# 2. Python Code Blocks - support for embedded Python in output
# 3. Structured Command Separation - organizes output by type

from datetime import date
from typing import List, Dict, Any, Optional, Tuple

from .physics import fmt


from .gpr_commands import (
    GPRCommand, DomainCommand, DxDyDzCommand, TimeWindowCommand, 
    WaveformCommand, 
    HertzianDipoleCommand, RxCommand, Header
)
from .scene_descriptor import SceneDefinition
from .version_utils import get_git_revision_hash

# ============================================================
# Command Validation (Pattern 1)
# ============================================================

class CommandValidator:
    # Validates gprMax command structure and requirements.
    
    REQUIRED_TYPES = {DomainCommand, DxDyDzCommand, TimeWindowCommand}
    SINGLE_ONLY_TYPES = {DomainCommand, DxDyDzCommand, TimeWindowCommand}
    
    @classmethod
    def validate(cls, commands: List[GPRCommand]) -> List[str]:
        # Validate command list and return any errors found.
        # 
        # Returns:
        #     List of error messages (empty if valid)
        errors = []
        seen_types = set()
        
        for cmd in commands:
            cmd_type = type(cmd)
            
            # Check for duplicate single-only commands
            if cmd_type in cls.SINGLE_ONLY_TYPES:
                if cmd_type in seen_types:
                    errors.append(f"Duplicate command not allowed: {cmd_type.__name__}")
                seen_types.add(cmd_type)
        
        # Check for missing required commands
        for req_type in cls.REQUIRED_TYPES:
            if req_type not in seen_types:
                errors.append(f"Missing required command: {req_type.__name__}")
        
        return errors
    
    @classmethod
    def is_valid(cls, commands: List[GPRCommand]) -> bool:
        # Quick check if command list is valid.
        return len(cls.validate(commands)) == 0


# ============================================================
# Structured Command Organization (Pattern 4)
# ============================================================




# ============================================================
# Main File Writer
# ============================================================

class GPRMaxFileWriter:
    # Assembles gprMax input file content with validation and structure using Command Pattern.
    
    @staticmethod
    def _format_defaults_section(config) -> str:
        """Generate a human-readable DEFAULTS section from config."""
        lines = []
        lines.append(Header("=" * 60).render())
        lines.append(Header("DEFAULTS (Fixed Configuration)").render())

        # Format frequency in MHz for readability
        freq_mhz = config.center_freq / 1e6
        lines.append(Header(f"Frequency: {freq_mhz:.0f} MHz").render())

        # Rock shape
        rock_shape = f"Angular ({config.rock_sides}-sided)" if config.angular_rocks else "Circular"
        lines.append(Header(f"Rock Shape: {rock_shape}").render())

        # Packing
        lines.append(Header(f"Packing: {config.rock_packing_algorithm} ({config.rock_psd_type} PSD)").render())

        # Antenna
        lines.append(Header(f"Antenna: {config.num_receivers} RX @ {config.receiver_spacing}m spacing").render())

        lines.append(Header("=" * 60).render())
        return "\n".join(lines)

    @staticmethod
    def write_scene(
        scene: SceneDefinition,
        scenario_type: str,
        extra_headers: Optional[Dict[str, Any]] = None
    ) -> str:
        # Render a SceneDefinition to a string.
        lines = []

        # 1. Header
        lines.append(Header("=" * 60).render())
        lines.append(Header("Generated gprMax Input File").render())
        lines.append(Header(f"Scenario: {scenario_type}").render())
        lines.append(Header(f"Date: {date.today().isoformat()}").render())

        # Git Version
        git_hash = get_git_revision_hash()
        if git_hash:
            lines.append(Header(f"Git Version: {git_hash}").render())

        if scene.config.base_seed is not None:
             lines.append(Header(f"Base Seed: {scene.config.base_seed}").render())

        # DEFAULTS section
        lines.append(GPRMaxFileWriter._format_defaults_section(scene.config))

        # Metadata
        for k, v in scene.metadata.items():
            val_str = fmt(v) if isinstance(v, float) else str(v)
            lines.append(Header(f"{k}: {val_str}").render())
            
        if extra_headers:
            for k, v in extra_headers.items():
                val_str = fmt(v) if isinstance(v, float) else str(v)
                lines.append(Header(f"{k}: {val_str}").render())
                
        lines.append(Header("=" * 60).render())
        
        # 2. Python Blocks
        for cmd in scene.python_blocks:
            lines.append(cmd.render())
            
        # 3. Domain (FIXED from config)
        if scene.domain_commands:
            lines.append(Header("Domain Configuration").render())
            for cmd in scene.domain_commands:
                lines.append(cmd.render())
            lines.append("#messages: n")

        # 4. Sources (Antenna + Waveform) - Explicit Sorting
        if scene.source_commands:
            lines.append(Header("Sources and Receivers").render())
            
            # Sort: Waveforms FIRST, then Dipoles/Rx (Antenna)
            # Use strict order: Waveforms definition must precede their usage in Dipoles.
            dipoles = [c for c in scene.source_commands if isinstance(c, (HertzianDipoleCommand, RxCommand))]
            waveforms = [c for c in scene.source_commands if isinstance(c, WaveformCommand)]
            others = [c for c in scene.source_commands if c not in dipoles and c not in waveforms]
            
            for cmd in waveforms: lines.append(cmd.render())
            for cmd in dipoles: lines.append(cmd.render())
            for cmd in others: lines.append(cmd.render())
            
        # 5. Materials
        if scene.material_commands:
            lines.append(Header("Materials").render())
            # Deduplication could happen here if needed, but Layer logic usually handles specific names
            # We can use a set to track rendered material identifiers if we wanted strict uniqueness.
            for cmd in scene.material_commands:
                lines.append(cmd.render())

        # 6. Geometry Layers
        if scene.geometry_commands:
            lines.append(Header("Geometry").render())

            # SORT BY PRIORITY
            sorted_geometry = sorted(scene.geometry_commands, key=lambda c: getattr(c, 'priority', 10))

            for cmd in sorted_geometry:
                if isinstance(cmd, str): 
                     # Should not happen with typed system, but safety net
                     lines.append(Header(f"RAW: {cmd}").render())
                elif hasattr(cmd, 'render'):
                     lines.append(cmd.render())
                else:
                     lines.append(Header(f"INVALID: {repr(cmd)}").render())

        return "\n".join(lines)
    
    
    
    @staticmethod
    def create_python_block(
        variable_definitions: Dict[str, Any],
        comment: str = "Dynamic parameters"
    ) -> Tuple[str, str]:
        # Helper to create a Python block from variable definitions.
        # 
        # Args:
        #     variable_definitions: Dict of variable names to values
        #     comment: Comment to add before block
        #     
        # Returns:
        #     Tuple of (code, comment) suitable for python_blocks parameter
        lines = []
        for name, value in variable_definitions.items():
            if isinstance(value, str):
                lines.append(f"{name} = '{value}'")
            else:
                lines.append(f"{name} = {value}")
        return ("\n".join(lines), comment)

    @staticmethod
    def write_to_file(
        scene: SceneDefinition,
        output_path: str,
        scenario_type: str = "Sim",
        extra_headers: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Write a SceneDefinition to a .in file.
        
        Encapsulates all file I/O operations for gprMax input files.
        
        Args:
            scene: SceneDefinition to write
            output_path: Full path to output file (including .in extension)
            scenario_type: Scenario identifier for header
            extra_headers: Optional additional metadata for headers
            
        Returns:
            Path to written file
            
        Raises:
            IOError: If file write fails
        """
        import os
        
        # Generate content
        content = GPRMaxFileWriter.write_scene(
            scene,
            scenario_type=scenario_type,
            extra_headers=extra_headers or {}
        )
        
        # Ensure output directory exists
        output_dir = os.path.dirname(output_path)
        if output_dir:  # Only create if there's a directory component
            os.makedirs(output_dir, exist_ok=True)
        
        # Write to file
        try:
            with open(output_path, 'w') as f:
                f.write(content)
            return output_path
        except Exception as e:
            raise IOError(f"Failed to write file {output_path}: {e}") from e

    @staticmethod
    def save_scene_checkpoint(
        checkpoint,  # SceneCheckpoint type (avoiding circular import)
        output_path: str,
        scenario_type: str = "Sim",
        config=None,  # GeneratorConfig for config embedding
        extra_headers: Optional[Dict[str, Any]] = None,
        sample_id: Optional[int] = None,  # Sample ID for computing actual seed in batch mode
        param_sources: Optional[Dict[str, str]] = None,  # Track parameter sources (CLI_OVERRIDE, SAMPLED, etc.)
    ) -> str:
        """
        Save a SceneCheckpoint to a .in file with optional config embedding.

        Handles all conversion from SceneCheckpoint → SceneDefinition → file.
        The production line doesn't need to know about file formats or paths.

        If config is provided, critical parameters are embedded in the .in file header
        as CONFIG_* comments for replication purposes. SOURCE_* comments track where
        each parameter came from (CLI_OVERRIDE, SAMPLED, BATCH_AUTO, DEFAULT).

        Args:
            checkpoint: SceneCheckpoint to save
            output_path: Full path to output file (including .in extension)
            scenario_type: Scenario identifier for header
            config: Optional GeneratorConfig to embed in .in file headers
            extra_headers: Optional additional metadata for headers
            sample_id: Optional sample ID for computing actual seed (batch mode)
            param_sources: Optional dict mapping param names to sources (CLI_OVERRIDE, SAMPLED, BATCH_AUTO, DEFAULT)

        Returns:
            Path to written file

        Raises:
            IOError: If file write fails
        """
        from .scene_descriptor import SceneDefinition

        # Prepare config embedding if provided
        if config:
            extra_headers = extra_headers or {}
            param_sources = param_sources or {}

            # Add critical config fields for replication
            config_pairs = {
                "CONFIG_center_freq_hz": config.center_freq,
                "CONFIG_rock_packing_algorithm": config.rock_packing_algorithm,
                "CONFIG_angular_rocks": str(config.angular_rocks),
                "CONFIG_rock_sides": config.rock_sides,
                "CONFIG_packing_psd_type": config.rock_psd_type,
                "CONFIG_num_receivers": config.num_receivers,
                "CONFIG_receiver_spacing": config.receiver_spacing,
            }
            extra_headers.update(config_pairs)

            # Add SOURCE_* markers for config parameters
            for key in config_pairs.keys():
                param_name = key.replace("CONFIG_", "")
                source = param_sources.get(param_name, "DEFAULT")
                extra_headers[f"SOURCE_{param_name}"] = source

            # Add base seed if set (essential for exact replication)
            if config.base_seed is not None:
                extra_headers["CONFIG_base_seed"] = config.base_seed
                extra_headers["SOURCE_base_seed"] = param_sources.get("base_seed", "DEFAULT")

            # Add PVC and moisture from metadata if available (for exact parameter replication)
            if hasattr(checkpoint, 'metadata') and checkpoint.metadata:
                if 'pvc' in checkpoint.metadata:
                    extra_headers["CONFIG_pvc_sampled"] = checkpoint.metadata['pvc']
                    extra_headers["SOURCE_pvc_sampled"] = param_sources.get("pvc", "SAMPLED")
                if 'moisture' in checkpoint.metadata:
                    extra_headers["CONFIG_moisture_sampled"] = checkpoint.metadata['moisture']
                    extra_headers["SOURCE_moisture_sampled"] = param_sources.get("moisture", "SAMPLED")

                # Compute and embed the actual seed used for this sample
                # For batch mode: actual_seed = base_seed + sample_id
                if sample_id is not None and config.base_seed is not None:
                    actual_seed = config.base_seed + sample_id
                    extra_headers["CONFIG_actual_seed"] = actual_seed
                    extra_headers["SOURCE_actual_seed"] = "BATCH_AUTO"

        # Convert SceneCheckpoint to SceneDefinition
        # Combine sources and receivers into one list for the source_commands field
        all_source_commands = list(checkpoint.sources) + list(checkpoint.receivers)

        domain_cmds = [
            checkpoint.domain_cmd,
            checkpoint.dx_dy_dz_cmd,
            checkpoint.time_window_cmd,
            checkpoint.absorbing_bc_cmd,  # PML boundary (may be None for old checkpoints)
        ]
        scene_def = SceneDefinition(
            config=checkpoint.config,
            domain_commands=[c for c in domain_cmds if c is not None],
            material_commands=checkpoint.materials,
            geometry_commands=checkpoint.geometry,
            source_commands=all_source_commands,
            metadata=checkpoint.metadata
        )

        # Delegate to write_to_file
        return GPRMaxFileWriter.write_to_file(
            scene_def,
            output_path=output_path,
            scenario_type=scenario_type,
            extra_headers=extra_headers or {}
        )

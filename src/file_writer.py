# GPRMax File Writer with validation and structured output.
# 
# Implements patterns from gprMax source:
# 1. Command Validation - ensures required commands present, no duplicates
# 2. Python Code Blocks - support for embedded Python in output
# 3. Structured Command Separation - organizes output by type

from datetime import date
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass

from .config import GeneratorConfig
from .physics import fmt


from .gpr_commands import (
    GPRCommand, DomainCommand, DxDyDzCommand, TimeWindowCommand, 
    MaterialCommand, BoxCommand, CylinderCommand, WaveformCommand, 
    HertzianDipoleCommand, RxCommand, GeometryViewCommand, CommentCommand, PythonBlockCommand, RawCommand
)
from .scene_descriptor import SceneDefinition

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
    def write_scene(
        scene: SceneDefinition,
        scenario_type: str,
        extra_headers: Optional[Dict[str, Any]] = None
    ) -> str:
        # Render a SceneDefinition to a string.
        lines = []
        
        # 1. Header
        lines.append(CommentCommand("=" * 60).render())
        lines.append(CommentCommand("Generated gprMax Input File").render())
        lines.append(CommentCommand(f"Scenario: {scenario_type}").render())
        lines.append(CommentCommand(f"Date: {date.today().isoformat()}").render())
        
        if scene.config.base_seed is not None:
             lines.append(CommentCommand(f"Base Seed: {scene.config.base_seed}").render())
             
        # Metadata
        for k, v in scene.metadata.items():
            val_str = fmt(v) if isinstance(v, float) else str(v)
            lines.append(CommentCommand(f"{k}: {val_str}").render())
            
        if extra_headers:
            for k, v in extra_headers.items():
                val_str = fmt(v) if isinstance(v, float) else str(v)
                lines.append(CommentCommand(f"{k}: {val_str}").render())
                
        lines.append(CommentCommand("=" * 60).render())
        
        # 2. Python Blocks
        for cmd in scene.python_blocks:
            lines.append(cmd.render())
            
        # 3. Domain (FIXED from config)
        if scene.domain_commands:
            lines.append(CommentCommand("Domain Configuration").render())
            for cmd in scene.domain_commands:
                lines.append(cmd.render())

        # 4. Sources (Antenna + Waveform) - Explicit Sorting
        if scene.source_commands:
            lines.append(CommentCommand("Sources and Receivers").render())
            
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
            lines.append(CommentCommand("Materials").render())
            # Deduplication could happen here if needed, but Layer logic usually handles specific names
            # We can use a set to track rendered material identifiers if we wanted strict uniqueness.
            for cmd in scene.material_commands:
                lines.append(cmd.render())

        # 6. Geometry Layers
        if scene.geometry_commands:
            lines.append(CommentCommand("Geometry").render())
            for cmd in scene.geometry_commands:
                if isinstance(cmd, str): 
                     # Should not happen with typed system, but safety net
                     lines.append(CommentCommand(f"RAW: {cmd}").render())
                elif hasattr(cmd, 'render'):
                     lines.append(cmd.render())
                else:
                     lines.append(CommentCommand(f"INVALID: {repr(cmd)}").render())

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

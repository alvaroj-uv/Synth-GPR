from dataclasses import dataclass, field
from typing import List, Dict, Any
from .gpr_commands import GPRCommand
from .config import GeneratorConfig

@dataclass
class LayerResult:
    """
    The output of a single layer's calculation.
    Separates commands into logical categories at generation time.
    """
    geometry: List[GPRCommand] = field(default_factory=list)
    materials: List[GPRCommand] = field(default_factory=list)
    sources: List[GPRCommand] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    top_y: float = 0.0

@dataclass
class SceneDefinition:
    """
    The complete, validated scene ready for writing.
    Represents the full simulation state decoupled from file format.
    """
    config: GeneratorConfig
    domain_commands: List[GPRCommand] = field(default_factory=list)
    material_commands: List[GPRCommand] = field(default_factory=list)
    source_commands: List[GPRCommand] = field(default_factory=list)
    geometry_commands: List[GPRCommand] = field(default_factory=list) # Ordered by layer
    python_blocks: List[GPRCommand] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

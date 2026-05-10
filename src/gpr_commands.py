from abc import ABC, abstractmethod
from dataclasses import dataclass

from .physics import fmt

class GPRCommand(ABC):
    """Abstract Base Class for all gprMax commands."""

    commented: bool = False  # Subclasses override via dataclass field

    @property
    def priority(self) -> int:
        """Rendering priority (lower = earlier). Default: 10"""
        return 10

    @abstractmethod
    def get_cmd_string(self) -> str:
        """Return the raw command string without comment prefix."""
        pass

    def render(self) -> str:
        """Render the command, prefixing with ## when commented."""
        cmd_str = self.get_cmd_string()
        if self.commented:
            return f"## {cmd_str}"
        return cmd_str

@dataclass
class Header(GPRCommand):
    """Represents a header or metadata line (starting with ##)."""
    text: str
    
    @property
    def priority(self) -> int:
        return 0 # Highest priority (top of file)
    
    def get_cmd_string(self) -> str:
        if self.text.startswith("##"):
            return self.text
        return f"## {self.text}"

@dataclass
class PythonBlockCommand(GPRCommand):
    """Represents a Python code block."""
    code: str
    comment: str = ""
    commented: bool = False
    
    def get_cmd_string(self) -> str:
        lines = []
        if self.comment:
            lines.append(f"## {self.comment}")
        lines.append("#python:")
        lines.append(self.code.strip())
        lines.append("#end_python:")
        return "\n".join(lines)

@dataclass
class DomainCommand(GPRCommand):
    x: float
    y: float
    z: float
    commented: bool = False
    
    def get_cmd_string(self) -> str:
        return f"#domain: {fmt(self.x)} {fmt(self.y)} {fmt(self.z)}"

@dataclass
class DxDyDzCommand(GPRCommand):
    dx: float
    dy: float
    dz: float
    commented: bool = False
    
    def get_cmd_string(self) -> str:
        return f"#dx_dy_dz: {fmt(self.dx)} {fmt(self.dy)} {fmt(self.dz)}"

@dataclass
class TimeWindowCommand(GPRCommand):
    time_window: float
    commented: bool = False
    
    def get_cmd_string(self) -> str:
        return f"#time_window: {fmt(self.time_window)}"

@dataclass
class MaterialCommand(GPRCommand):
    eps: float
    sigma: float
    mu: float
    mag_loss: float
    identifier: str
    commented: bool = False
    
    def get_cmd_string(self) -> str:
        return f"#material: {fmt(self.eps)} {fmt(self.sigma)} {fmt(self.mu)} {fmt(self.mag_loss)} {self.identifier}"

@dataclass
class BoxCommand(GPRCommand):
    x1: float
    y1: float
    z1: float
    x2: float
    y2: float
    z2: float
    material: str
    commented: bool = False
    
    def get_cmd_string(self) -> str:
        return f"#box: {fmt(self.x1)} {fmt(self.y1)} {fmt(self.z1)} {fmt(self.x2)} {fmt(self.y2)} {fmt(self.z2)} {self.material}"

@dataclass
class CylinderCommand(GPRCommand):
    x1: float
    y1: float
    z1: float
    x2: float
    y2: float
    z2: float
    radius: float
    material: str
    commented: bool = False
    
    @property
    def priority(self) -> int:
        return 20 # Objects (Rocks) - Render AFTER Box (10)
    
    def get_cmd_string(self) -> str:
        return f"#cylinder: {fmt(self.x1)} {fmt(self.y1)} {fmt(self.z1)} {fmt(self.x2)} {fmt(self.y2)} {fmt(self.z2)} {fmt(self.radius)} {self.material}"

@dataclass
class TriangleCommand(GPRCommand):
    x1: float; y1: float; z1: float
    x2: float; y2: float; z2: float
    x3: float; y3: float; z3: float
    material: str
    commented: bool = False
    
    @property
    def priority(self) -> int:
        return 21 # Objects (Angular Rocks) - Render AFTER Box
    
    def get_cmd_string(self) -> str:
        return f"#triangle: {fmt(self.x1)} {fmt(self.y1)} {fmt(self.z1)} {fmt(self.x2)} {fmt(self.y2)} {fmt(self.z2)} {fmt(self.x3)} {fmt(self.y3)} {fmt(self.z3)} {self.material}"


@dataclass
class WaveformCommand(GPRCommand):
    type_name: str
    amplitude: float
    frequency: float
    identifier: str
    commented: bool = False
    
    @property
    def priority(self) -> int:
        return 50 # Waveforms
    
    def get_cmd_string(self) -> str:
        return f"#waveform: {self.type_name} {fmt(self.amplitude)} {fmt(self.frequency)} {self.identifier}"

@dataclass
class HertzianDipoleCommand(GPRCommand):
    polarization: str
    x: float
    y: float
    z: float
    waveform: str
    commented: bool = False
    
    @property
    def priority(self) -> int:
        return 100 # Sources (Antenna) - Render last
    
    def get_cmd_string(self) -> str:
        return f"#hertzian_dipole: {self.polarization} {fmt(self.x)} {fmt(self.y)} {fmt(self.z)} {self.waveform}"

@dataclass
class RxCommand(GPRCommand):
    x: float
    y: float
    z: float
    commented: bool = False
    
    @property
    def priority(self) -> int:
        return 100 # Receivers
    
    def get_cmd_string(self) -> str:
        return f"#rx: {fmt(self.x)} {fmt(self.y)} {fmt(self.z)}"

@dataclass
class GeometryViewCommand(GPRCommand):
    x1: float
    y1: float
    z1: float
    x2: float
    y2: float
    z2: float
    dx: float
    dy: float
    dz: float
    filename: str
    type_char: str = 'n'
    commented: bool = True  # Default to commented out
    
    @property
    def priority(self) -> int:
        return 200 # Geometry View - Very last
    
    def get_cmd_string(self) -> str:
        return f"#geometry_view: {fmt(self.x1)} {fmt(self.y1)} {fmt(self.z1)} {fmt(self.x2)} {fmt(self.y2)} {fmt(self.z2)} {fmt(self.dx)} {fmt(self.dy)} {fmt(self.dz)} {self.filename} {self.type_char}"

@dataclass
class AbsorbingBCCommand(GPRCommand):
    """PML absorbing boundary: #pml_cells: n_cells (Benedetto et al. 2016)."""
    cells: int = 10
    commented: bool = False

    def get_cmd_string(self) -> str:
        return f"#pml_cells: {self.cells}"


class RawCommand(GPRCommand):
    """Fallback for raw command strings that don't fit other categories."""
    def __init__(self, text: str, commented: bool = False):
        self.text = text
        self.commented = commented
        
    def get_cmd_string(self) -> str:
        return self.text

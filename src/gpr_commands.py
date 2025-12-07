from abc import ABC, abstractmethod
from typing import Optional
from dataclasses import dataclass

from .config import fmt

class GPRCommand(ABC):
    """Abstract Base Class for all gprMax commands."""
    
    @abstractmethod
    def render(self) -> str:
        """Render the command as a string for the .in file."""
        pass

@dataclass
class CommentCommand(GPRCommand):
    """Represents a comment line."""
    text: str
    
    def render(self) -> str:
        if self.text.startswith("##"):
            return self.text
        return f"## {self.text}"

@dataclass
class PythonBlockCommand(GPRCommand):
    """Represents a Python code block."""
    code: str
    comment: str = ""
    
    def render(self) -> str:
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
    
    def render(self) -> str:
        return f"#domain: {fmt(self.x)} {fmt(self.y)} {fmt(self.z)}"

@dataclass
class DxDyDzCommand(GPRCommand):
    dx: float
    dy: float
    dz: float
    
    def render(self) -> str:
        return f"#dx_dy_dz: {fmt(self.dx)} {fmt(self.dy)} {fmt(self.dz)}"

@dataclass
class TimeWindowCommand(GPRCommand):
    time_window: float
    
    def render(self) -> str:
        return f"#time_window: {fmt(self.time_window)}"

@dataclass
class MaterialCommand(GPRCommand):
    eps: float
    sigma: float
    mu: float
    mag_loss: float
    identifier: str
    
    def render(self) -> str:
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
    
    def render(self) -> str:
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
    
    def render(self) -> str:
        return f"#cylinder: {fmt(self.x1)} {fmt(self.y1)} {fmt(self.z1)} {fmt(self.x2)} {fmt(self.y2)} {fmt(self.z2)} {fmt(self.radius)} {self.material}"

@dataclass
class WaveformCommand(GPRCommand):
    type_name: str
    amplitude: float
    frequency: float
    identifier: str
    
    def render(self) -> str:
        return f"#waveform: {self.type_name} {fmt(self.amplitude)} {fmt(self.frequency)} {self.identifier}"

@dataclass
class HertzianDipoleCommand(GPRCommand):
    polarization: str
    x: float
    y: float
    z: float
    waveform: str
    
    def render(self) -> str:
        return f"#hertzian_dipole: {self.polarization} {fmt(self.x)} {fmt(self.y)} {fmt(self.z)} {self.waveform}"

@dataclass
class RxCommand(GPRCommand):
    x: float
    y: float
    z: float
    
    def render(self) -> str:
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
    
    def render(self) -> str:
        return f"#geometry_view: {fmt(self.x1)} {fmt(self.y1)} {fmt(self.z1)} {fmt(self.x2)} {fmt(self.y2)} {fmt(self.z2)} {fmt(self.dx)} {fmt(self.dy)} {fmt(self.dz)} {self.filename} {self.type_char}"

class RawCommand(GPRCommand):
    """Fallback for raw command strings that don't fit other categories."""
    def __init__(self, text: str):
        self.text = text
        
    def render(self) -> str:
        return self.text

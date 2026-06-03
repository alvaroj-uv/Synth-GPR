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

    def __post_init__(self):
        # gprMax requires the static (DC) relative permittivity to be >= 1
        # (cannot be below vacuum). When a material is made dispersive with
        # #add_dispersion_debye, this eps is eps_inf and STILL must be >= 1.
        # Guard here so no generation path can ever emit an invalid material
        # (e.g. eps_inf = eps - d_eps going below 1 for low-eps fouling).
        if self.eps < 1.0:
            raise ValueError(
                f"#material '{self.identifier}': relative permittivity must be "
                f">= 1 (got {self.eps}). If using Debye dispersion, cap d_eps so "
                f"eps_inf = eps_static - d_eps stays >= 1."
            )

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
class SoilPeplinskiCommand(GPRCommand):
    """gprMax #soil_peplinski mixing model for a semi-empirical heterogeneous soil.

    #soil_peplinski: sand_frac clay_frac bulk_density sand_part_density water_lo water_hi name

    Used together with #fractal_box to give a fouling layer internal volumetric
    dielectric texture (scattering) instead of a single homogeneous value.
    """
    sand_frac: float
    clay_frac: float
    bulk_density: float
    sand_part_density: float
    water_lo: float
    water_hi: float
    identifier: str
    commented: bool = False

    @property
    def priority(self) -> int:
        return 5  # Material-like: must be defined before the fractal_box that uses it

    def get_cmd_string(self) -> str:
        return (f"#soil_peplinski: {fmt(self.sand_frac)} {fmt(self.clay_frac)} "
                f"{fmt(self.bulk_density)} {fmt(self.sand_part_density)} "
                f"{fmt(self.water_lo)} {fmt(self.water_hi)} {self.identifier}")


@dataclass
class FractalBoxCommand(GPRCommand):
    """gprMax #fractal_box: a box filled with a fractally-distributed mix of a
    soil's material variants, producing spatially heterogeneous permittivity.

    #fractal_box: x1 y1 z1 x2 y2 z2 frac_dim w_x w_y w_z n_materials soil box_id [seed]

    Rendered at box priority (10) so subsequent #cylinder/#triangle rocks stamp
    on top of it (painter's algorithm), matching the solid-box fouling path.
    """
    x1: float
    y1: float
    z1: float
    x2: float
    y2: float
    z2: float
    frac_dim: float
    n_materials: int
    soil: str
    box_id: str
    seed: int = None
    weight_x: float = 1.0
    weight_y: float = 1.0
    weight_z: float = 1.0
    commented: bool = False

    def get_cmd_string(self) -> str:
        s = (f"#fractal_box: {fmt(self.x1)} {fmt(self.y1)} {fmt(self.z1)} "
             f"{fmt(self.x2)} {fmt(self.y2)} {fmt(self.z2)} {fmt(self.frac_dim)} "
             f"{fmt(self.weight_x)} {fmt(self.weight_y)} {fmt(self.weight_z)} "
             f"{self.n_materials} {self.soil} {self.box_id}")
        if self.seed is not None:
            s += f" {self.seed}"
        return s


@dataclass
class AddSurfaceRoughnessCommand(GPRCommand):
    """gprMax #add_surface_roughness: applies fractal roughness to a face of an
    existing #fractal_box, replacing a flat specular interface with an undulating
    one (breaks the coherent layer reflections that dominate flat-box scenes).

    #add_surface_roughness: x1 y1 z1 x2 y2 z2 frac_dim w_x w_y limit_lower limit_upper box_id [seed]

    The (x1,y1,z1)-(x2,y2,z2) define the surface plane (for a horizontal top
    surface, y1==y2==top). limit_lower/limit_upper bound the y-range the surface
    undulates between. MUST be emitted AFTER the #fractal_box it references.
    """
    x1: float
    y1: float
    z1: float
    x2: float
    y2: float
    z2: float
    frac_dim: float
    limit_lower: float
    limit_upper: float
    box_id: str
    seed: int = None
    weight_x: float = 1.0
    weight_y: float = 1.0
    commented: bool = False

    @property
    def priority(self) -> int:
        return 11  # right after #fractal_box (10), before rocks (20)

    def get_cmd_string(self) -> str:
        s = (f"#add_surface_roughness: {fmt(self.x1)} {fmt(self.y1)} {fmt(self.z1)} "
             f"{fmt(self.x2)} {fmt(self.y2)} {fmt(self.z2)} {fmt(self.frac_dim)} "
             f"{fmt(self.weight_x)} {fmt(self.weight_y)} "
             f"{fmt(self.limit_lower)} {fmt(self.limit_upper)} {self.box_id}")
        if self.seed is not None:
            s += f" {self.seed}"
        return s


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
    thickness: float = 0.0
    material: str = ""
    commented: bool = False

    @property
    def priority(self) -> int:
        return 21 # Objects (Angular Rocks) - Render AFTER Box

    def get_cmd_string(self) -> str:
        return f"#triangle: {fmt(self.x1)} {fmt(self.y1)} {fmt(self.z1)} {fmt(self.x2)} {fmt(self.y2)} {fmt(self.z2)} {fmt(self.x3)} {fmt(self.y3)} {fmt(self.z3)} {fmt(self.thickness)} {self.material}"

@dataclass
class SphereCommand(GPRCommand):
    x: float
    y: float
    z: float
    radius: float
    material: str
    commented: bool = False

    @property
    def priority(self) -> int:
        return 20  # Objects (3D Rocks) - Render AFTER Box

    def get_cmd_string(self) -> str:
        return f"#sphere: {fmt(self.x)} {fmt(self.y)} {fmt(self.z)} {fmt(self.radius)} {self.material}"

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
    """PML absorbing boundary: #pml_cells: x0 y0 z0 xmax ymax zmax

    gprMax requires EXACTLY 1 parameter (all sides) or 6 parameters (per-side control).
    This class generates the 6-parameter format for fine-grained PML control.

    For 2D TMz simulations (domain Z = 1 cell), z_cells MUST be 0 —
    otherwise gprMax raises 'CmdInputError: #pml_cells has too many cells
    for the domain size'.  The default is z_cells=0 (safe for 2D).

    For true 3D simulations, set z_cells equal to cells (xy_cells).

    Parameters:
        cells: Number of PML cells on X and Y boundaries (left, right, top, bottom)
        z_cells: Number of PML cells on Z boundaries (back, front). 0 for 2D TMz mode.

    Reference: gprMax source (input_cmds_singleuse.py) and Benedetto et al. (2016).
    """
    cells: int = 10
    z_cells: int = 0          # 0 = 2D/TMz safe; set equal to cells for 3D
    commented: bool = False

    def get_cmd_string(self) -> str:
        # gprMax v3 validates: len(params) == 1 OR len(params) == 6
        # Format: x0(left) y0(bottom) z0(back) xmax(right) ymax(top) zmax(front)
        # For 2D TMz (nz=1): z0 and zmax MUST be 0, otherwise domain constraint fails
        return f"#pml_cells: {self.cells} {self.cells} {self.z_cells} {self.cells} {self.cells} {self.z_cells}"


class RawCommand(GPRCommand):
    """Fallback for raw command strings that don't fit other categories."""
    def __init__(self, text: str, commented: bool = False):
        self.text = text
        self.commented = commented
        
    def get_cmd_string(self) -> str:
        return self.text

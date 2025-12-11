from abc import ABC, abstractmethod
from typing import List, Optional, Tuple, Any, Dict
from dataclasses import dataclass, field
import numpy as np

@dataclass
class Style:
    """Base class for style properties."""
    pass

@dataclass
class LineStyle(Style):
    color: str = 'black'
    linewidth: float = 1.0
    linestyle: str = '-'
    alpha: float = 1.0

@dataclass
class Node(ABC):
    """Base class for all visualization nodes."""
    parent: Optional['Node'] = None
    children: List['Node'] = field(default_factory=list)
    visible: bool = True
    
    def add_child(self, node: 'Node'):
        node.parent = self
        self.children.append(node)
        return node

    def get_children_of_type(self, node_type: type) -> List['Node']:
        return [child for child in self.children if isinstance(child, node_type)]

@dataclass
class FigureNode(Node):
    """Root node representing the entire figure."""
    figsize: Tuple[float, float] = (10, 8)
    dpi: int = 100
    title: Optional[str] = None

@dataclass
class GraphNode(Node):
    """Represents a plot area (axes)."""
    title: Optional[str] = None
    xlabel: Optional[str] = None
    ylabel: Optional[str] = None
    position: int = 111 # Standard matplotlib subplot position
    projection: str = 'rectilinear' # 'rectilinear', 'polar', '3d'

@dataclass
class AxisNode(Node):
    """Represents a single axis (X or Y)."""
    axis_type: str = 'x' # 'x' or 'y'
    label: Optional[str] = None
    limits: Optional[Tuple[float, float]] = None
    scale: str = 'linear' # 'linear', 'log'
    invert: bool = False

@dataclass
class TraceNode(Node):
    """Represents a 1D signal trace."""
    x: np.ndarray = field(default_factory=lambda: np.array([]))
    y: np.ndarray = field(default_factory=lambda: np.array([]))
    style: LineStyle = field(default_factory=LineStyle)
    label: Optional[str] = None
    
    # "Wiggle" plot properties
    is_wiggle: bool = False
    wiggle_fill_color: Optional[str] = 'black'
    wiggle_gain: float = 1.0

@dataclass
class RasterNode(Node):
    """Represents a 2D matrix (image/B-scan)."""
    data: np.ndarray = field(default_factory=lambda: np.array([[]]))
    extent: Optional[Tuple[float, float, float, float]] = None # (left, right, bottom, top)
    cmap: str = 'seismic'
    vmin: Optional[float] = None
    vmax: Optional[float] = None
    interpolation: str = 'nearest'
    colorbar_label: Optional[str] = None

@dataclass
class TextNode(Node):
    """Represents arbitrary text."""
    x: float = 0.0
    y: float = 0.0
    text: str = ""
    fontsize: int = 10
    color: str = 'black'
    rotation: float = 0.0

@dataclass
class SpectrogramNode(Node):
    """Represents a Time-Frequency Spectrogram."""
    t: np.ndarray = field(default_factory=lambda: np.array([]))
    f: np.ndarray = field(default_factory=lambda: np.array([]))
    Sxx: np.ndarray = field(default_factory=lambda: np.array([[]]))
    cmap: str = 'inferno'
    colorbar_label: Optional[str] = 'Power (dB)'
    vmin: Optional[float] = None
    vmax: Optional[float] = None
    

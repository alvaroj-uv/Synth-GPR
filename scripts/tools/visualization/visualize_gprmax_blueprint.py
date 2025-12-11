#!/usr/bin/env python3
from __future__ import annotations
"""
Script to create a graphical blueprint representation of gprMax input files.

Reads .in files and visualizes the geometry showing materials, layers, and heights.
If a corresponding .out file matches the input filename, it will also visualize the simulated Hx signal.

Usage:
    python visualize_gprmax_blueprint.py <input_file.in>

Example:
    python visualize_gprmax_blueprint.py input/generated/synthetic_inputs/s0000_unif.in
"""

import sys
import argparse
import logging
from pathlib import Path

# Add parent directory to path for imports
# scripts/tools/visualization/ -> up 4 levels to project root
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

from typing import Dict, Any, Optional, Tuple, List
from dataclasses import dataclass, field
from abc import ABC, abstractmethod

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.gridspec as gridspec
import numpy as np
from scipy.signal import hilbert
from scipy.fft import fft, fftfreq
@dataclass
class Point:
    x: float
    y: float
    z: float

@dataclass
class Domain:
    size: Point

@dataclass
class Material:
    eps: float
    sigma: float

@dataclass
class VisualizationConfig:
    """Configuration for visualization styling."""
    dpi: int = 300
    edge_color: str = '#404040'
    line_width: float = 0.3
    default_cmap: Any = field(default_factory=lambda: plt.cm.YlOrBr)
    # Colors
    color_free_space: str = '#F5F5F5'
    color_bal_rock: str = '#F4A460'
    color_bal_foul: str = '#4B3621'
    color_subgrade: str = '#2F4F4F'

class GeometryVisitor(ABC):
    """
    Abstract Visitor for geometry objects.
    """
    @abstractmethod
    def visit_box(self, box: 'Box') -> Any:
        pass

    @abstractmethod
    def visit_cylinder(self, cylinder: 'Cylinder') -> Any:
        pass

@dataclass
class GeometryObject(ABC):
    type: str
    material: str
    order: int

    @abstractmethod
    def accept(self, visitor: GeometryVisitor) -> Any:
        pass

@dataclass
class Box(GeometryObject):
    p1: Point
    p2: Point

    def accept(self, visitor: GeometryVisitor) -> Any:
        return visitor.visit_box(self)

@dataclass
class Cylinder(GeometryObject):
    p1: Point
    p2: Point
    radius: float

    def accept(self, visitor: GeometryVisitor) -> Any:
        return visitor.visit_cylinder(self)



@dataclass
class Antenna:
    position: Point


def load_simulation_signals(out_file_path: str) -> Dict[str, np.ndarray]:
    """
    Attempt to load E and H fields from a gprMax HDF5 output file.
    Handles optional dependency on src.data_loader.
    """
    valid_signals = {}
    
    # Lazy import to avoid hard dependency at module level
    try:
        from src.data_loader import read_gprmax_hdf5
    except ImportError:
        print("[WARN] Could not import src.data_loader. Signal plotting disabled.")
        return valid_signals

    print(f"[BLUEPRINT] Attempting to load signals from: {out_file_path}")
    
    try:
        # Load both E and H fields
        signal_df = read_gprmax_hdf5(out_file_path, fields=['E', 'H'])
        
        if not signal_df.empty:
             # Check each numeric column (excluding Time)
             # Determine if it's "empty" (all zeros or negligible)
             threshold = 1e-9
             for col in signal_df.columns:
                 if col == 'Time':
                     continue
                 
                 signal_vals = signal_df[col].values
                 amplitude = np.max(np.abs(signal_vals))
                 if amplitude > threshold:
                     valid_signals[col] = signal_vals
        
        if valid_signals:
            print(f"Plotting {len(valid_signals)} non-empty signals: {list(valid_signals.keys())}")
            
    except Exception as e:
        print(f"Warning: Could not load signal from {out_file_path}: {e}")
        
    return valid_signals


@dataclass
class SimulationModel:
    """
    Represents the parsed simulation data using a structured model.
    Replaces the unstructured dictionary.
    """
    title: Optional[str] = None
    domain: Optional[Domain] = None
    materials: Dict[str, Material] = field(default_factory=dict)
    objects: List[GeometryObject] = field(default_factory=list)
    source: Optional[Antenna] = None
    receiver: Optional[Antenna] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class GeometryFactory:
    """
    Factory for creating geometry objects from gprMax commands.
    """
    @staticmethod
    def create_object(command: str, parts: List[str], order: int) -> Optional[GeometryObject]:
        if command == '#box':
            return Box(
                type='box',
                p1=Point(float(parts[0]), float(parts[1]), float(parts[2])),
                p2=Point(float(parts[3]), float(parts[4]), float(parts[5])),
                material=parts[6],
                order=order
            )
        elif command == '#cylinder':
            return Cylinder(
                type='cylinder',
                p1=Point(float(parts[0]), float(parts[1]), float(parts[2])),
                p2=Point(float(parts[3]), float(parts[4]), float(parts[5])),
                radius=float(parts[6]),
                material=parts[7],
                order=order
            )
        return None
class GprMaxInputParser:
    """
    Parses gprMax input files (.in) into a structured dictionary/model.
    """
    def __init__(self, filepath: str):
        self.filepath = filepath
        # Initialize the new SimulationModel
        self.model = SimulationModel()


    def parse(self) -> SimulationModel:
        """
        Parse a gprMax input file and extract geometry information using Factory pattern.
        """

        logging.info(f"[BLUEPRINT] Parsing geometry from: {self.filepath}")
        self.model.metadata['filename'] = Path(self.filepath).name
        
        order_counter = 0
        
        with open(self.filepath, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line: continue
                
                parts = line.split(':')
                command = parts[0].strip()
                
                if command == '#title':
                    self.model.title = parts[1].strip()
                
                elif command == '#domain':
                    vals = parts[1].strip().split()
                    self.model.domain = Domain(
                        size=Point(float(vals[0]), float(vals[1]), float(vals[2]))
                    )
                
                elif command == '#material':
                    vals = parts[1].strip().split()
                    material_name = vals[-1]
                    self.model.materials[material_name] = Material(
                        eps=float(vals[0]),
                        sigma=float(vals[1])
                    )
                
                elif command == '#hertzian_dipole':
                    vals = parts[1].strip().split()
                    self.model.source = Antenna(
                        position=Point(float(vals[1]), float(vals[2]), float(vals[3]))
                    )
                
                elif command == '#rx':
                    vals = parts[1].strip().split()
                    self.model.receiver = Antenna(
                        position=Point(float(vals[0]), float(vals[1]), float(vals[2]))
                    )

                elif command == '## FI (%)':
                    self.model.metadata['FI'] = parts[1].strip()
                elif command == '## FI_class':
                    self.model.metadata['FI_class'] = parts[1].strip()
                elif command == '## Scenario':
                    self.model.metadata['scenario'] = parts[1].strip()
                
                # Use Factory for geometry objects
                elif command in ['#box', '#cylinder']:
                    vals = parts[1].strip().split()
                    geom_obj = GeometryFactory.create_object(command, vals, order_counter)
                    if geom_obj:
                        self.model.objects.append(geom_obj)
                        order_counter += 1
        
        obj_count = len(self.model.objects)
        mat_count = len(self.model.materials)
        logging.info(f"[BLUEPRINT] Parsed {obj_count} objects and {mat_count} material definitions.")
        return self.model


class MatplotlibDrawer(GeometryVisitor):


    """
    Concrete Visitor that draws geometry objects using Matplotlib.
    """
    def __init__(self, ax: Any, config: VisualizationConfig, min_eps: float, max_eps: float, visualizer: 'GprMaxBlueprintVisualizer'):
        self.ax = ax
        self.config = config
        self.min_eps = min_eps
        self.max_eps = max_eps
        self.visualizer = visualizer

    def visit_box(self, box: Box) -> Any:
        color, alpha = self.visualizer._get_mat_color_alpha(
            box.material, self.min_eps, self.max_eps, self.config.default_cmap
        )
        z_order = 1 + box.order
        
        width = box.p2.x - box.p1.x
        height = box.p2.y - box.p1.y
        rect = mpatches.Rectangle(
            (box.p1.x, box.p1.y), width, height,
            linewidth=self.config.line_width, edgecolor=self.config.edge_color, 
            facecolor=color, alpha=alpha, zorder=z_order
        )
        self.ax.add_patch(rect)

    def visit_cylinder(self, cylinder: Cylinder) -> Any:
        color, alpha = self.visualizer._get_mat_color_alpha(
            cylinder.material, self.min_eps, self.max_eps, self.config.default_cmap
        )
        z_order = 1 + cylinder.order
        
        # Smart Projection: Check alignment
        dx = abs(cylinder.p1.x - cylinder.p2.x)
        dy = abs(cylinder.p1.y - cylinder.p2.y)
        is_vertical_z = (dx < 1e-6 and dy < 1e-6)

        if is_vertical_z:
            # Vertical (Z-aligned) -> Draw Circle
            circle = mpatches.Circle(
                (cylinder.p1.x, cylinder.p1.y), cylinder.radius,
                linewidth=self.config.line_width, edgecolor=self.config.edge_color, 
                facecolor=color, alpha=alpha, zorder=z_order
            )
            self.ax.add_patch(circle)
        else:
            # Horizontal/Diagonal -> Draw Projected Rectangle
            angle_rad = np.arctan2(cylinder.p2.y - cylinder.p1.y, cylinder.p2.x - cylinder.p1.x)
            length = np.sqrt(dx**2 + dy**2)
            angle_deg = np.degrees(angle_rad)
            
            # Calculate anchor point (bottom-left corner of rotated rect)
            # Shift from center line by radius perpendicular to axis
            anchor_x = cylinder.p1.x - cylinder.radius * np.sin(angle_rad)
            anchor_y = cylinder.p1.y + cylinder.radius * np.cos(angle_rad)

            rect = mpatches.Rectangle(
                (anchor_x, anchor_y), length, 2*cylinder.radius, angle=angle_deg,
                linewidth=self.config.line_width, edgecolor=self.config.edge_color, 
                facecolor=color, alpha=alpha, zorder=z_order
            )
            self.ax.add_patch(rect)


class GeometryScaler(GeometryVisitor):
    """
    Visitor that scales geometry objects in-place.
    """
    def __init__(self, scale_factor: float):
        self.scale = scale_factor

    def visit_box(self, box: Box) -> Any:
        # Scale p1
        box.p1.x *= self.scale
        box.p1.y *= self.scale
        box.p1.z *= self.scale
        # Scale p2
        box.p2.x *= self.scale
        box.p2.y *= self.scale
        box.p2.z *= self.scale

    def visit_cylinder(self, cylinder: Cylinder) -> Any:
        # Scale p1
        cylinder.p1.x *= self.scale
        cylinder.p1.y *= self.scale
        cylinder.p1.z *= self.scale
        # Scale p2
        cylinder.p2.x *= self.scale
        cylinder.p2.y *= self.scale
        cylinder.p2.z *= self.scale
        # Scale radius
        cylinder.radius *= self.scale


class GprMaxBlueprintVisualizer:
    """
    Visualizer for gprMax input files.
    Encapsulates parsing and plotting logic.
    """

    # Material color mapping for visualization
    DEFAULT_COLORS = {
        'free_space': '#F5F5F5',       # White Smoke
        'bal_rock': '#F4A460',         # Sandy Brown
        'bal_foul': '#4B3621',         # Cafe Noir
        'bal_foul_granular': '#4B3621',# Same as above
        'subgrade': '#2F4F4F',         # Dark Slate Gray
        'formation': '#BDB76B',        # Dark Khaki
        'concrete_sleeper': '#708090', # Slate Gray
    }

    def __init__(self, model: SimulationModel, config: VisualizationConfig = VisualizationConfig()):
        """
        Initialize the visualizer with parsed model.
        """
        self.model = model
        self.config = config
        # Use config defaults, but override with dynamic heatmap logic if needed
        # Actually material_colors logic below is specific to this project's heatmap needs
        # We'll keep it as is, but could potentially move to Config later.
        self.material_colors: Dict[str, Any] = self.DEFAULT_COLORS.copy()

        # Add dynamic/granular colors
        for i in range(1, 10):
            self.material_colors[f'bal_foul_g{i}'] = plt.cm.YlOrBr(0.3 + i * 0.07)

        self.material_colors.update({
            'bal_foul_granular': '#5D4037',
            'bal_rock_L1': '#A1887F',
            'bal_rock_L2': '#8D6E63',
            'bal_rock_L3': '#6D4C41',
        })



    def _get_mat_color_alpha(self, material: str, min_eps: float, max_eps: float, cmap: Any) -> Tuple[Any, float]:
        """Helper to get color based on material properties."""
        if material == 'free_space':
            return '#E8F4F8', 0.1

        mat_props = self.model.materials.get(material)
        eps = mat_props.eps if mat_props else 5.0

        if max_eps > min_eps:
            norm_eps = (eps - min_eps) / (max_eps - min_eps)
        else:
            norm_eps = 0.5

        return cmap(0.3 + norm_eps * 0.6), 1.0

    def visualize(self, output_file: Optional[str] = None, show_plot: bool = True, out_file_path: Optional[str] = None) -> None:
        """
        Create the blueprint visualization.
        """
        # 1. Load Signals if available
        valid_signals = {}
        show_signal = False

        if out_file_path and Path(out_file_path).exists():
            valid_signals = load_simulation_signals(out_file_path)
            show_signal = bool(valid_signals)

        # 2. Setup Plot
        if show_signal:
            fig = plt.figure(figsize=(18, 10))
            # 2 Columns: Main Blueprint (Left) vs Signals (Right)
            gs = gridspec.GridSpec(1, 2, width_ratios=[3, 1])
            
            ax = fig.add_subplot(gs[0, 0])
            
            # Right Column: 4 Vertical Rows
            gs_right = gridspec.GridSpecFromSubplotSpec(4, 1, subplot_spec=gs[0, 1], hspace=0.4)
            
            ax_signal = fig.add_subplot(gs_right[0, 0])
            ax_envelope = fig.add_subplot(gs_right[1, 0])
            ax_gain = fig.add_subplot(gs_right[2, 0])
            ax_legend = fig.add_subplot(gs_right[3, 0])
            
            # Hide axes for legend block
            ax_legend.axis('off')
        else:
            fig, ax = plt.subplots(figsize=(12, 8))

        domain = self.model.domain
        if not domain:
            logging.error("No domain defined in input file.")
            return

        # 3. Color Map Setup
        eps_values = [props.eps for props in self.model.materials.values()]
        min_eps = min(eps_values) if eps_values else 1
        max_eps = max(eps_values) if eps_values else 10
        cmap = plt.cm.YlOrBr

        # 4. Draw Objects
        objects = self.model.objects
        objects.sort(key=lambda x: x.order)

        # Visitor Pattern Usage
        drawer = MatplotlibDrawer(ax, config=self.config, min_eps=min_eps, max_eps=max_eps, visualizer=self)

        # Collect materials for Legend
        seen_materials = set()
        for i, obj in enumerate(objects):
            seen_materials.add(obj.material)
            # Dispatch drawing to visitor
            obj.accept(drawer)

        # 5. Rulers and Annotations
        self._add_annotations(ax, domain)

        # 6. Source/Receiver
        if self.model.source:
            src = self.model.source
            ax.plot(src.position.x, src.position.y, 'r^', markersize=12, label='TX (Source)', zorder=10)
            ax.text(src.position.x, src.position.y + 0.03, 'TX', ha='center', fontsize=10, fontweight='bold', color='red')

        if self.model.receiver:
            rx = self.model.receiver
            ax.plot(rx.position.x, rx.position.y, 'bv', markersize=12, label='RX (Receiver)', zorder=10)
            ax.text(rx.position.x, rx.position.y + 0.03, 'RX', ha='center', fontsize=10, fontweight='bold', color='blue')

        # 7. Formatting
        ax.set_xlim(-0.02, domain.size.x + 0.15)
        ax.set_ylim(-0.05, domain.size.y + 0.05)
        ax.set_xlabel('X (meters)', fontsize=12, fontweight='bold')
        ax.set_ylabel('Y (meters)', fontsize=12, fontweight='bold')
        self._set_title(ax)
        ax.grid(True, alpha=0.3, linestyle='--')
        ax.set_aspect('equal')

        # 8. Legend
        if show_signal:
            self._create_legend_block(ax_legend, cmap, min_eps, max_eps)
        else:
            self._create_legend(ax, min_eps, max_eps, cmap)

        # 9. Plot Signals if enabled
        if show_signal:
            self._plot_signals(ax_signal, ax_envelope, ax_gain, valid_signals)

        plt.tight_layout()

        if output_file:
            plt.savefig(output_file, dpi=300, bbox_inches='tight')
            print(f"[BLUEPRINT] Visualization saved to: {output_file}")

        if show_plot:
            plt.show()

    def _add_annotations(self, ax: Any, domain: Domain) -> None:
        """Add height rulers and rock annotations."""
        # Layer lines
        layer_boundaries = set()
        for obj in self.model.objects:
            if isinstance(obj, Box) and obj.material != 'free_space':
                layer_boundaries.add(obj.p1.y)
                layer_boundaries.add(obj.p2.y)
        
        cyl_tops = [max(o.p1.y, o.p2.y) + o.radius for o in self.model.objects if isinstance(o, Cylinder)]
        if cyl_tops:
            layer_boundaries.add(max(cyl_tops))
            
        for h in sorted([h for h in layer_boundaries if h >= 0]):
            if h > 0.001:
                ax.axhline(y=h, color='gray', linestyle=':', linewidth=1.0, alpha=0.6, zorder=5)

        # Right-side height labels
        unique_heights = set()
        for obj in self.model.objects:
            if isinstance(obj, Box) and obj.material != 'free_space':
                unique_heights.add(obj.p2.y)
        
        for height in sorted(unique_heights):
            if height > 0.01:
                ax.plot([domain.size.x, domain.size.x + 0.02], [height, height], 'k-', linewidth=1, alpha=0.5)
                ax.text(domain.size.x + 0.025, height, f'{height:.3f} m', va='center', fontsize=8, style='italic')
        
        # Max Rock Height
        if cyl_tops:
            max_y_cyl = max(cyl_tops)
            formation_top = 0.0
            for o in self.model.objects:
                if isinstance(o, Box) and o.material == 'formation':
                    formation_top = max(formation_top, o.p2.y)
            
            ax.axhline(y=max_y_cyl, color='#8B7355', linestyle=':', linewidth=1.5, alpha=0.8, zorder=20)
            
            label_text = f'Max Rock Height: {max_y_cyl:.3f} m'
            if formation_top > 0:
                relative_height = max_y_cyl - formation_top
                label_text += f'\n(From Formation: {relative_height*100:.1f} cm)'
            
            ax.text(domain.size.x + 0.08, max_y_cyl, label_text, color='#4A3310',
                   ha='left', va='center', fontsize=8, fontweight='bold', style='italic',
                   bbox=dict(boxstyle='round,pad=0.2', facecolor='#FFF8DC', alpha=0.8, edgecolor='#8B7355'))

    def _set_title(self, ax: Any) -> None:
        """Build and set the plot title."""
        title_parts = []
        if self.model.title:
            title_parts.append(f"Class: {self.model.title}")
        if 'FI_class' in self.model.metadata:
            title_parts.append(f"Class: {self.model.metadata['FI_class']}")
        if 'scenario' in self.model.metadata:
            title_parts.append(f"Scenario: {self.model.metadata['scenario']}")
        if 'FI' in self.model.metadata:
            title_parts.append(f"FI: {self.model.metadata['FI']}%")

        title = ' | '.join(title_parts) if title_parts else 'gprMax Geometry Blueprint'
        ax.set_title(title, fontsize=14, fontweight='bold', pad=25)

        ax.text(0.5, 1.02, f"File: {self.model.metadata.get('filename', 'Unknown')}",
               transform=ax.transAxes, ha='center', va='bottom', fontsize=10,
               color='#555555', family='monospace')

    def _create_legend(self, ax: Any, min_eps: float, max_eps: float, cmap: Any) -> None:
        """Create material legend."""
        material_patches = []
        # Sort for consistency? Reversed to match drawing layer roughly (top down)
        all_objects = self.model.objects
        displayed_mats = set()
        
        for obj in reversed(all_objects):
            material = obj.material
            if material not in displayed_mats:
                displayed_mats.add(material)
                color, _ = self._get_mat_color_alpha(material, min_eps, max_eps, cmap)
                mat_props = self.model.materials.get(material)
                eps = mat_props.eps if mat_props else 5.0
                label = f"{material} (ε={eps:.1f})"
        if material_patches:
            ax.legend(handles=material_patches, bbox_to_anchor=(-0.02, 1.0), loc='upper right', fontsize=8, framealpha=0.9)

    def _create_legend_block(self, ax: Any, cmap: Any, min_eps: float, max_eps: float) -> None:
        """Create a dedicated legend block in the dashboard."""
        
        # 1. Materials
        all_objects = self.model.objects
        displayed_mats = set()
        legend_elements = []
        
        # Title
        ax.text(0.5, 1.0, "Legend", ha='center', va='top', fontsize=12, fontweight='bold', transform=ax.transAxes)
        
        # Collect unique materials
        for obj in reversed(all_objects):
            material = obj.material
            if material not in displayed_mats and material != 'free_space':
                displayed_mats.add(material)
                color, _ = self._get_mat_color_alpha(material, min_eps, max_eps, cmap)
                mat_props = self.model.materials.get(material)
                eps = mat_props.eps if mat_props else 0.0
                sigma = mat_props.sigma if mat_props else 0.0
                
                label = f"{material}\n(ε={eps:.1f}, σ={sigma:.3f})"
                patch = mpatches.Patch(facecolor=color, edgecolor=self.config.edge_color, label=label)
                legend_elements.append(patch)

        # 2. Add Signal Lines to Legend
        legend_elements.append(mpatches.Patch(color='none', label="")) # Spacer
        legend_elements.append(plt.Line2D([0], [0], color='blue', lw=1.5, label='E-Field (V/m)'))
        legend_elements.append(plt.Line2D([0], [0], color='green', lw=1.5, linestyle='--', label='H-Field (A/m)'))
        legend_elements.append(plt.Line2D([0], [0], color='red', lw=1.5, label='Envelope'))
        legend_elements.append(plt.Line2D([0], [0], color='purple', lw=1.5, label='Gain Corrected'))
        legend_elements.append(plt.Line2D([0], [0], color='gray', lw=1.0, linestyle=':', label='Raw (Ref)'))

        # Place Legend in the Axis
        ax.legend(handles=legend_elements, loc='center', fontsize=9, frameon=False, borderaxespad=0)


    def _plot_signals(self, ax_signal: Any, ax_envelope: Any, ax_gain: Any, signals: Dict[str, np.ndarray]) -> None:
        """Plot A-Scans, Envelope, and Gain."""
        # 1. RAW SIGNAL (A-Scan)
        ax_h = ax_signal.twinx()
        has_e = False
        has_h = False

        strongest_name = ""
        max_amp = 0
        
        for name, data in signals.items():
            if np.max(np.abs(data)) > max_amp:
                max_amp = np.max(np.abs(data))
                strongest_name = name

            if 'E' in name:
                ax_signal.plot(data, label=name, linestyle='-', linewidth=1.0)
                has_e = True
            elif 'H' in name:
                ax_h.plot(data, label=name, linestyle='--', color='green', linewidth=1.0)
                has_h = True
        
        ax_signal.set_title('Time Domain (Raw)', fontsize=10, fontweight='bold')
        ax_signal.grid(True, alpha=0.3)
        if has_e: ax_signal.set_ylabel('E-Field')
        
        # 2. ENVELOPE (Hilbert)
        if strongest_name:
            data = signals[strongest_name]
            envelope = np.abs(hilbert(data))
            ax_envelope.plot(envelope, 'r-', linewidth=1.5)
            ax_envelope.fill_between(range(len(envelope)), 0, envelope, color='red', alpha=0.2)
            ax_envelope.set_title(f'Envelope ({strongest_name})', fontsize=10, fontweight='bold')
            ax_envelope.grid(True, alpha=0.3)

        # 3. TIME-VARYING GAIN (SEC)
        # Simple energy compensation: t^1.5 or exponential
        if strongest_name:
            t = np.arange(len(data))
            gain_curve = (t + 1) ** 1.5  # Simple power gain
            # Normalize gain to avoid explosion
            gain_curve = gain_curve / np.max(gain_curve) * 5 
            gained_signal = data * gain_curve
            
            # Primary Axis: Gained Signal
            ax_gain.plot(gained_signal, 'purple', linewidth=1.2, label='Gain Corrected')
            ax_gain.set_title(f'Time-Varying Gain (vs Raw)', fontsize=10, fontweight='bold')
            ax_gain.grid(True, alpha=0.3)
            
            # Secondary Axis: Raw Signal (Reference)
            ax_gain_raw = ax_gain.twinx()
            ax_gain_raw.plot(data, color='gray', linewidth=0.8, linestyle=':', alpha=0.6, label='Raw')
            ax_gain_raw.set_yticks([]) # Hide ticks to reduce clutter, just shape comparison


def main():
    """
    Main entry point for the blueprint visualization script.
    """
    parser = argparse.ArgumentParser(
        description='Create a blueprint visualization of gprMax input files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s input/templates/sample.in
  %(prog)s synthetic_inputs/s0000_unif.in -o blueprint.png
  %(prog)s synthetic_inputs/s0000_unif.in --no-show --dpi 600
        """
    )

    parser.add_argument('input_file', help='gprMax input file (.in) to visualize')
    parser.add_argument('-o', '--output', help='Output image file (png, pdf, svg, etc.)')
    parser.add_argument('--no-show', action='store_true', help='Do not display the plot')
    parser.add_argument('--dpi', type=int, default=300, help='DPI for output image (default: 300)')
    parser.add_argument('--scale', type=float, default=1.0, help='Scale factor for geometry (default: 1.0)')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')

    args = parser.parse_args()

    # 1. Setup Logging
    log_level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(level=log_level, format='%(name)s - %(levelname)s - %(message)s')

    if not Path(args.input_file).exists():
        logging.error(f"Input file not found: {args.input_file}")
        sys.exit(1)

    # 2. Parse Input
    input_parser = GprMaxInputParser(args.input_file)
    parsed_data = input_parser.parse()

    # Apply Scaling if requested
    if args.scale != 1.0:
        logging.info(f"Applying scale factor: {args.scale}")
        scaler = GeometryScaler(args.scale)
        
        # Scale Objects
        for obj in parsed_data.objects:
            obj.accept(scaler)
        
        # Scale Domain
        if parsed_data.domain:
            parsed_data.domain.size.x *= args.scale
            parsed_data.domain.size.y *= args.scale
            parsed_data.domain.size.z *= args.scale
            
        # Scale Source/Receiver
        if parsed_data.source:
            parsed_data.source.position.x *= args.scale
            parsed_data.source.position.y *= args.scale
            parsed_data.source.position.z *= args.scale
            
        if parsed_data.receiver:
            parsed_data.receiver.position.x *= args.scale
            parsed_data.receiver.position.y *= args.scale
            parsed_data.receiver.position.z *= args.scale

    # 3. Configure
    config = VisualizationConfig(dpi=args.dpi)

    # 4. Visualize
    visualizer = GprMaxBlueprintVisualizer(parsed_data, config)

    # Try to find corresponding .out file
    input_path = Path(args.input_file)
    out_file_path = input_path.with_suffix('.out')

    if not out_file_path.exists():
        out_file_path = None
        logging.warning(f"No .out file found (expected at {input_path.with_suffix('.out')})")
    else:
        logging.info(f"Found .out file: {out_file_path}")

    visualizer.visualize(
        output_file=args.output,
        show_plot=not args.no_show,
        out_file_path=str(out_file_path) if out_file_path else None
    )

    return 0


if __name__ == "__main__":
    sys.exit(main())

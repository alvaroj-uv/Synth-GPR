#!/usr/bin/env python3
"""
Script to create a graphical blueprint representation of gprMax input files.

Reads .in files and visualizes the geometry showing materials, layers, and heights.
If a corresponding .out file matches the input filename, it will also visualize the simulated Hx signal.

Usage:
    python visualize_gprmax_blueprint.py <input_file.in>
    
Example:
    python visualize_gprmax_blueprint.py input/generated/synthetic_inputs/s0000_unif.in
"""

import re
import sys
import argparse
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from pathlib import Path
import numpy as np
import h5py
from scipy.signal import hilbert
import matplotlib.gridspec as gridspec

# Add parent directory to path for imports
# Now in scripts/tools/, so we need to go up 3 levels to reach project root (if root is above scripts/)
# Actually root is d:/Codigo/Synth-GPR
# scripts/tools/visualize.py -> parent = tools -> parent = scripts -> parent = Synth-GPR
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    from src.data_loader import read_gprmax_hdf5
    HAS_DATA_LOADER = True
except ImportError:
    HAS_DATA_LOADER = False


# Material color mapping for visualization
# This dictionary maps specific material identifiers found in gprMax input files
# to hex color codes for Matplotlib visualization.
MATERIAL_COLORS = {
    'free_space': '#E8F4F8',       # Light blue: Represents air/background
    'bal_rock': '#8B7355',         # Brown: Clean ballast aggregates (rocks)
    'bal_foul': '#654321',         # Dark brown: Generic fouled ballast
    'bal_foul_wet': '#4A3310',     # Very dark brown: Wet fouled ballast
    'foul_pocket': '#3D2817',      # Almost black: Localized fouling pockets
    'subgrade': '#D2B48C',         # Tan: The layer beneath the formation (soil)
    'formation': '#C19A6B',        # Camel brown: The capping layer/formation
    'concrete_sleeper': '#2F4F4F', # Dark Slate Gray: Concrete railway ties/sleepers
}

# Add gradient materials dynamically
# Generates colors for 'bal_foul_g1' to 'bal_foul_g9' to visualize varying degrees of fouling
# using the YlOrBr (Yellow-Orange-Brown) colormap.
for i in range(1, 10):
    MATERIAL_COLORS[f'bal_foul_g{i}'] = plt.cm.YlOrBr(0.3 + i * 0.07)

# Add Granular mode materials (High-Fidelity)
# Specific colors for granular simulation components
MATERIAL_COLORS['bal_foul_granular'] = '#5D4037' # Darker brown for the fine matrix between rocks
MATERIAL_COLORS['bal_rock_L1'] = '#A1887F'       # Lighter brown for Small rocks
MATERIAL_COLORS['bal_rock_L2'] = '#8D6E63'       # Medium brown for Medium rocks
MATERIAL_COLORS['bal_rock_L3'] = '#6D4C41'       # Darker brown for Large rocks


def parse_gprmax_input(filepath):
    """
    Parse a gprMax input file and extract geometry information.
    
    Reads lines sequentially and extracts commands like #domain, #material, #box, #cylinder.
    Stores objects in a list to preserve the "painter's algorithm" drawing order.
    
    Args:
        filepath (str): Path to the .in file to parse.
        
    Returns:
        dict: A dictionary containing:
            - title (str): Simulation title from #title
            - domain (dict): {'x': float, 'y': float, 'z': float}
            - materials (dict): Map of material_name -> {'eps': float, 'sigma': float}
            - objects (list): List of dicts, each representing a drawn shape (box/cylinder)
                              with keys: type, material, order, coordinates...
            - source (dict): Position of the source antenna
            - receiver (dict): Position of the receiver antenna
            - metadata (dict): Custom metadata extracted from comments (e.g. FI, Scenario)
    """
    data = {
        'title': None,
        'domain': None,
        'materials': {},
        'objects': [], # Combined list with order
        'source': None,
        'receiver': None,
        'metadata': {}
    }
    
    order_counter = 0

    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            
            # Parse title
            if line.startswith('#title:'):
                data['title'] = line.split(':', 1)[1].strip()
            
            # Parse domain
            elif line.startswith('#domain:'):
                parts = line.split(':')[1].strip().split()
                data['domain'] = {
                    'x': float(parts[0]),
                    'y': float(parts[1]),
                    'z': float(parts[2])
                }
            
            # Parse materials
            elif line.startswith('#material:'):
                parts = line.split(':')[1].strip().split()
                material_name = parts[-1]  # Last part is the name
                data['materials'][material_name] = {
                    'eps': float(parts[0]),
                    'sigma': float(parts[1]),
                }
            
            # Parse boxes
            elif line.startswith('#box:'):
                parts = line.split(':')[1].strip().split()
                # Format: x0 y0 z0 x1 y1 z1 material
                data['objects'].append({
                    'type': 'box',
                    'x0': float(parts[0]),
                    'y0': float(parts[1]),
                    'z0': float(parts[2]),
                    'x1': float(parts[3]),
                    'y1': float(parts[4]),
                    'z1': float(parts[5]),
                    'material': parts[6],
                    'order': order_counter
                })
                order_counter += 1

            # Parse cylinders
            elif line.startswith('#cylinder:'):
                parts = line.split(':')[1].strip().split()
                # Format: x1 y1 z1 x2 y2 z2 radius material
                data['objects'].append({
                    'type': 'cylinder',
                    'x': float(parts[0]),
                    'y': float(parts[1]),
                    'z': float(parts[2]),
                    'radius': float(parts[6]),
                    'length': abs(float(parts[5]) - float(parts[2])),
                    'material': parts[7],
                    'order': order_counter
                })
                order_counter += 1
            
            # Parse source
            elif line.startswith('#hertzian_dipole:'):
                parts = line.split(':')[1].strip().split()
                data['source'] = {
                    'x': float(parts[1]),
                    'y': float(parts[2]),
                    'z': float(parts[3])
                }
            
            # Parse receiver
            elif line.startswith('#rx:'):
                parts = line.split(':')[1].strip().split()
                data['receiver'] = {
                    'x': float(parts[0]),
                    'y': float(parts[1]),
                    'z': float(parts[2])
                }
            
            # Parse metadata
            elif line.startswith('## FI (%):'):
                data['metadata']['FI'] = line.split(':')[1].strip()
            elif line.startswith('## FI class:'):
                data['metadata']['FI_class'] = line.split(':')[1].strip()
            elif line.startswith('## Scenario:'):
                data['metadata']['scenario'] = line.split(':')[1].strip()
    
    return data


def create_blueprint(data, output_file=None, show_plot=True, out_file_path=None):
    """
    Create a blueprint visualization of the gprMax geometry using Matplotlib.
    
    Generates a 2D cross-section view (X-Y plane) of the simulation domain.
    Draws objects in the order they appear in the file to correctly visualize layers.
    Also calculates and displays a vertical ruler for layer heights and a rock height annotation.
    
    Args:
        data (dict): Parsed geometry data returned by parse_gprmax_input.
        output_file (str, optional): Path to save the resulting image file (e.g. .png).
        show_plot (bool): If True, calls plt.show() to display the window.
        out_file_path (str, optional): Path to a corresponding .out HDF5 file. 
                                       If provided and valid, adds signal plots.
                                       
    Variables:
        fig (Figure): Matplotlib figure object.
        ax (Axes): Main axes for the geometry blueprint.
        objects (list): List of geometry objects (boxes, cylinders) to draw.
        z_order (int): Drawing order index. Higher values are drawn on top.
        material_patches (list): List of patches for the legend.
    """
    # Check if .out file exists and can be loaded
    show_signal = False
    signal_data = None
    
    if out_file_path and Path(out_file_path).exists() and HAS_DATA_LOADER:
        try:
            signal_df = read_gprmax_hdf5(out_file_path, fields=['Hx'])
            if not signal_df.empty and 'rx1_Hx' in signal_df.columns:
                signal_data = signal_df
                show_signal = True
        except Exception as e:
            print(f"Warning: Could not load signal from {out_file_path}: {e}")
    
    # Create figure with subplots if showing signal
    if show_signal:
        fig = plt.figure(figsize=(16, 8))
        gs = gridspec.GridSpec(2, 2, width_ratios=[1, 1])
        ax = fig.add_subplot(gs[:, 0])      # Left: Blueprint (full height)
        ax_signal = fig.add_subplot(gs[0, 1])  # Top Right: Signal
        ax_envelope = fig.add_subplot(gs[1, 1])  # Bottom Right: Envelope
    else:
        fig, ax = plt.subplots(figsize=(12, 8))
    
    domain = data['domain']
    
    
    # Create color mapping based on dielectric values
    # Get all dielectric constants for color scale
    eps_values = []
    
    # Collect materials from defined materials list
    for mat, props in data['materials'].items():
        if 'eps' in props:
            eps_values.append(props['eps'])
    
    if eps_values:
        min_eps = min(eps_values)
        max_eps = max(eps_values)
        # Use a colormap - YlOrBr (Yellow-Orange-Brown) for earth materials
        cmap = plt.cm.YlOrBr
    else:
        min_eps, max_eps = 1, 10
        cmap = plt.cm.YlOrBr
    
    # Helper to get color
    def get_mat_color_alpha(material):
        if material == 'free_space':
            return '#E8F4F8', 0.3
        
        mat_props = data['materials'].get(material, {})
        eps = mat_props.get('eps', 5.0)
        
        if max_eps > min_eps:
            norm_eps = (eps - min_eps) / (max_eps - min_eps)
        else:
            norm_eps = 0.5
        
        # Get color from colormap
        return cmap(0.3 + norm_eps * 0.6), 0.8

    # Draw all objects in order
    objects = data.get('objects', [])
    # Sort by order just in case, though they should be appended in order
    objects.sort(key=lambda x: x['order'])

    for i, obj in enumerate(objects):
        obj_type = obj['type']
        material = obj['material']
        color, alpha = get_mat_color_alpha(material)
        
        # Determine zorder based on file order (plus offset for base elements)
        # Background is 0. Objects start at 1.
        z_order = 1 + i
        
        if obj_type == 'box':
            x0, y0 = obj['x0'], obj['y0']
            x1, y1 = obj['x1'], obj['y1']
            width = x1 - x0
            height = y1 - y0
            
            rect = mpatches.Rectangle(
                (x0, y0), width, height,
                linewidth=0.5,
                edgecolor='black',
                facecolor=color,
                alpha=alpha,
                zorder=z_order
            )
            ax.add_patch(rect)
            
        elif obj_type == 'cylinder':
            x, y = obj['x'], obj['y']
            r = obj['radius']
            
            circle = mpatches.Circle(
                (x, y), r,
                linewidth=0.5,
                edgecolor='black',
                facecolor=color,
                alpha=alpha,
                zorder=z_order 
            )
            ax.add_patch(circle)
        
    # Labels removed - information shown in legend instead
    
    
    # Add vertical ruler on the left side showing layer heights
    # Identify distinct horizontal layers (excluding free_space)
    layer_boundaries = set()
    for obj in data.get('objects', []):
        if obj['type'] == 'box' and obj['material'] != 'free_space':
            layer_boundaries.add(obj['y0'])
            layer_boundaries.add(obj['y1'])
    
    layer_boundaries = sorted([h for h in layer_boundaries if h >= 0])
    
    if len(layer_boundaries) > 1:
        ruler_x = -0.16  # Position on left side (more space from y-axis)
        
        # Draw vertical ruler line
        ax.plot([ruler_x, ruler_x], [0, max(layer_boundaries)], 
               'k-', linewidth=2, zorder=15)
        
        # Add tick marks and dimension annotations for each layer
        for i in range(len(layer_boundaries) - 1):
            y_bottom = layer_boundaries[i]
            y_top = layer_boundaries[i + 1]
            layer_height = y_top - y_bottom
            
            # Draw horizontal tick marks
            ax.plot([ruler_x - 0.01, ruler_x + 0.01], [y_bottom, y_bottom],
                   'k-', linewidth=1.5, zorder=15)
            ax.plot([ruler_x - 0.01, ruler_x + 0.01], [y_top, y_top],
                   'k-', linewidth=1.5, zorder=15)
            
            # Add dimension line with arrows
            y_mid = (y_bottom + y_top) / 2
            
            # Double-headed arrow for dimension
            ax.annotate('', xy=(ruler_x - 0.035, y_top), 
                       xytext=(ruler_x - 0.035, y_bottom),
                       arrowprops=dict(arrowstyle='<->', lw=1.5, color='black'),
                       zorder=15)
            
            # Layer height text
            if layer_height > 0.01:  # Only show if significant
                ax.text(ruler_x - 0.055, y_mid, 
                       f'{layer_height*100:.1f} cm',
                       ha='right', va='center', fontsize=8,
                       fontweight='bold',
                       bbox=dict(boxstyle='round,pad=0.3', 
                               facecolor='yellow', alpha=0.8, 
                               edgecolor='black', linewidth=1),
                       zorder=16)
        
        # Add ruler label at top
        ax.text(ruler_x, max(layer_boundaries) + 0.03, 
               'Layer\nHeights',
               ha='center', va='bottom', fontsize=9,
               fontweight='bold', style='italic')
    
    # Add height annotations on the right side
    unique_heights = set()
    for obj in data.get('objects', []):
        if obj['type'] == 'box' and obj['material'] != 'free_space':
            unique_heights.add(obj['y1'])
    
    for height in sorted(unique_heights):
        if height > 0.01:  # Skip very small heights
            ax.plot([domain['x'], domain['x'] + 0.02], [height, height], 
                   'k-', linewidth=1, alpha=0.5)
            ax.text(domain['x'] + 0.025, height, f'{height:.3f} m',
                   va='center', fontsize=8, style='italic')
    
    # Add source and receiver if present
    if data['source']:
        src = data['source']
        ax.plot(src['x'], src['y'], 'r^', markersize=12, 
               label='TX (Source)', zorder=10)
        ax.text(src['x'], src['y'] + 0.03, 'TX',
               ha='center', fontsize=10, fontweight='bold', color='red')
    
    if data['receiver']:
        rx = data['receiver']
        ax.plot(rx['x'], rx['y'], 'bv', markersize=12,
               label='RX (Receiver)', zorder=10)
        ax.text(rx['x'], rx['y'] + 0.03, 'RX',
               ha='center', fontsize=10, fontweight='bold', color='blue')
    
    # Set limits and labels (adjust left margin for ruler)
    ax.set_xlim(-0.30, domain['x'] + 0.15)
    ax.set_ylim(-0.05, domain['y'] + 0.05)
    ax.set_xlabel('X (meters)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Y (meters)', fontsize=12, fontweight='bold')
    
    # Title with metadata
    title_parts = []
    if data['title']:
        title_parts.append(f"Class: {data['title']}")
    if 'scenario' in data['metadata']:
        title_parts.append(f"Scenario: {data['metadata']['scenario']}")
    if 'FI' in data['metadata']:
        title_parts.append(f"FI: {data['metadata']['FI']}%")
    
    title = ' | '.join(title_parts) if title_parts else 'gprMax Geometry Blueprint'
    ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
    
    # Grid
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.set_aspect('equal')
    
    # Legend for materials with dielectric values
    material_patches = []
    seen_materials = set()
    
    # Collect materials from both boxes and cylinders
    all_objects = data.get('objects', [])
    
    # Sort objects to try to keep some order (e.g. by y0 or y) although distinct types make it hard
    # We'll just process them in order of appearance in the file/list
    
    for obj in reversed(all_objects):
        material = obj['material']
        if material not in seen_materials and material != 'free_space':
            seen_materials.add(material)
            
            # Get color based on dielectric (same logic as drawing)
            color, alpha = get_mat_color_alpha(material)
             
            # Create legend label with dielectric value
            mat_props = data['materials'].get(material, {})
            eps = mat_props.get('eps', 5.0)
            
            label = f"{material} (ε={eps:.1f})"
            patch = mpatches.Patch(color=color, label=label, alpha=0.8)
            material_patches.append(patch)
    
    if material_patches:
        ax.legend(handles=material_patches, loc='upper left', 
                  fontsize=9, framealpha=0.9)

    # --------------------------------------------------------
    # Annotation: Highest Cylinder (Rock Top)
    # --------------------------------------------------------
    cylinders = [o for o in data.get('objects', []) if o['type'] == 'cylinder']
    if cylinders:
        # Find the cylinder with the maximum top point (y + r)
        max_y_cyl = -1.0
        top_cyl = None
        
        for cyl in cylinders:
            y_top = cyl['y'] + cyl['radius']
            if y_top > max_y_cyl:
                max_y_cyl = y_top
                top_cyl = cyl
        
        if top_cyl:
            # Add a dashed line across
            ax.axhline(y=max_y_cyl, color='#8B7355', linestyle=':', linewidth=1.5, alpha=0.8, zorder=20)
            
            # Add text annotation
            ax.text(domain['x'] + 0.08, max_y_cyl, 
                   f'Max Rock Height\n{max_y_cyl:.3f} m',
                   color='#4A3310',
                   ha='left', va='center', fontsize=8,
                   fontweight='bold', style='italic',
                   bbox=dict(boxstyle='round,pad=0.2', 
                            facecolor='#FFF8DC', alpha=0.8, 
                            edgecolor='#8B7355', linewidth=0.5))
                            
            # Highlight this specific point
            ax.plot(top_cyl['x'], max_y_cyl, 'kx', markersize=5, zorder=21)

    # Plot Hz signal if available
    if show_signal and signal_data is not None:
        time = signal_data['Time'].values if 'Time' in signal_data.columns else np.arange(len(signal_data))
        time_ns = time * 1e9 # Convert to ns
        hx_signal = signal_data['rx1_Hx'].values
        
        # Calculate Hilbert Envelope
        analytic_signal = hilbert(hx_signal)
        envelope = np.abs(analytic_signal)
        
        # --- Top Right: Signal Graph (Time starting from 0 on left) ---
        ax_signal.plot(time_ns, hx_signal, 'b-', linewidth=1, label='Hx Signal')
        ax_signal.set_ylabel('Amplitude (A/m)', fontsize=10, fontweight='bold')
        ax_signal.set_title('A-Scan Signal', fontsize=12, fontweight='bold')
        ax_signal.grid(True, alpha=0.3, linestyle='--')
        ax_signal.set_xlim(0, max(time_ns))
        # Add x-label to top plot as requested
        ax_signal.set_xlabel('Time (ns)', fontsize=10, fontweight='bold')
        
        # --- Bottom Right: Hilbert Envelope ---
        ax_envelope.plot(time_ns, envelope, 'r-', linewidth=1.5, label='Envelope')
        ax_envelope.fill_between(time_ns, 0, envelope, color='red', alpha=0.2)
        ax_envelope.set_xlabel('Time (ns)', fontsize=10, fontweight='bold')
        ax_envelope.set_ylabel('Magnitude', fontsize=10, fontweight='bold')
        ax_envelope.set_title('Hilbert Envelope', fontsize=12, fontweight='bold')
        ax_envelope.grid(True, alpha=0.3, linestyle='--')
        ax_envelope.set_xlim(0, max(time_ns))

        # Align y-axes ranges if helpful? No, scales might differ.
        # But ensure they look clean.
    
    plt.tight_layout()
    
    # Save if output file specified
    if output_file:
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"Blueprint saved to: {output_file}")
    
    # Show plot
    if show_plot:
        plt.show()
    
    return fig, ax


def main():
    """
    Main entry point for the blueprint visualization script.
    
    Parses command line arguments, reads the input file, checks for an optional .out file,
    and calls the visualization function.
    """
    parser = argparse.ArgumentParser(
        description='Create a blueprint visualization of gprMax input files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s input/templates/sample.in
  %(prog)s synthetic_inputs/s0000_unif.in -o blueprint.png
  %(prog)s synthetic_inputs/s0000_unif.in --no-show
        """
    )
    
    parser.add_argument(
        'input_file',
        help='gprMax input file (.in) to visualize'
    )
    
    parser.add_argument(
        '-o', '--output',
        help='Output image file (png, pdf, svg, etc.)'
    )
    
    parser.add_argument(
        '--no-show',
        action='store_true',
        help='Do not display the plot (only save to file)'
    )
    
    args = parser.parse_args()
    
    # Check if input file exists
    if not Path(args.input_file).exists():
        print(f"Error: Input file not found: {args.input_file}")
        return 1
    
    print(f"Reading: {args.input_file}")
    
    
    # Parse input file
    data = parse_gprmax_input(args.input_file)
    
    # Try to find corresponding .out file
    input_path = Path(args.input_file)
    out_file_path = input_path.with_suffix('.out')
    
    if not out_file_path.exists():
        out_file_path = None
        print(f"Note: No .out file found (looking for {out_file_path})")
    else:
        print(f"Found .out file: {out_file_path}")
    
    # Create blueprint
    create_blueprint(
        data,
        output_file=args.output,
        show_plot=not args.no_show,
        out_file_path=out_file_path
    )
    
    return 0


if __name__ == "__main__":
    exit(main())

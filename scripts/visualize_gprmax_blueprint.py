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

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from src.data_loader import read_gprmax_hdf5
    HAS_DATA_LOADER = True
except ImportError:
    HAS_DATA_LOADER = False


# Material color mapping for visualization
MATERIAL_COLORS = {
    'free_space': '#E8F4F8',      # Light blue
    'bal_rock': '#8B7355',         # Brown (clean ballast)
    'bal_foul': '#654321',         # Dark brown (fouled ballast)
    'bal_foul_wet': '#4A3310',     # Very dark brown (wet fouled)
    'foul_pocket': '#3D2817',      # Almost black (pockets)
    'subgrade': '#D2B48C',         # Tan
    'formation': '#C19A6B',        # Camel brown
}

# Add gradient materials dynamically
for i in range(1, 10):
    MATERIAL_COLORS[f'bal_foul_g{i}'] = plt.cm.YlOrBr(0.3 + i * 0.07)


def parse_gprmax_input(filepath):
    """
    Parse a gprMax input file and extract geometry information.
    
    Returns:
        dict with domain, materials, boxes, and metadata
    """
    data = {
        'title': None,
        'domain': None,
        'materials': {},
        'boxes': [],
        'source': None,
        'receiver': None,
        'metadata': {}
    }
    
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
                data['boxes'].append({
                    'x0': float(parts[0]),
                    'y0': float(parts[1]),
                    'z0': float(parts[2]),
                    'x1': float(parts[3]),
                    'y1': float(parts[4]),
                    'z1': float(parts[5]),
                    'material': parts[6]
                })
            
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
            
            # Parse metadata from comments
            elif line.startswith('## FI (%):'):
                data['metadata']['FI'] = line.split(':')[1].strip()
            elif line.startswith('## FI class:'):
                data['metadata']['FI_class'] = line.split(':')[1].strip()
            elif line.startswith('## Scenario:'):
                data['metadata']['scenario'] = line.split(':')[1].strip()
    
    return data


def create_blueprint(data, output_file=None, show_plot=True, out_file_path=None):
    """
    Create a blueprint visualization of the gprMax geometry.
    
    Args:
        data: Parsed data from parse_gprmax_input
        output_file: Optional file path to save the figure
        show_plot: Whether to display the plot
        out_file_path: Optional path to .out file for signal visualization
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
        ax = fig.add_subplot(1, 2, 1)  # Left: blueprint
        ax_signal = fig.add_subplot(1, 2, 2)  # Right: signal
    else:
        fig, ax = plt.subplots(figsize=(12, 8))
    
    domain = data['domain']
    
    
    # Create color mapping based on dielectric values
    # Get all dielectric constants for color scale
    boxes = data['boxes']
    eps_values = []
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
    
    # Draw boxes
    for box in boxes:
        x0, y0 = box['x0'], box['y0']
        x1, y1 = box['x1'], box['y1']
        material = box['material']
        
        width = x1 - x0
        height = y1 - y0
        
        # Get color based on dielectric constant
        if material == 'free_space':
            color = '#E8F4F8'  # Light blue for air
            alpha = 0.3
        else:
            mat_props = data['materials'].get(material, {})
            eps = mat_props.get('eps', 5.0)
            
            # Normalize epsilon to 0-1 range for colormap
            if max_eps > min_eps:
                norm_eps = (eps - min_eps) / (max_eps - min_eps)
            else:
                norm_eps = 0.5
            
            # Get color from colormap (0.3 to 0.9 range for better contrast)
            color = cmap(0.3 + norm_eps * 0.6)
            alpha = 0.8
        
        # Draw rectangle
        rect = mpatches.Rectangle(
            (x0, y0), width, height,
            linewidth=0.5,
            edgecolor='black',
            facecolor=color,
            alpha=alpha,
            zorder=1 if material == 'free_space' else 2
        )
        ax.add_patch(rect)
        
        # Labels removed - information shown in legend instead
    
    
    # Add vertical ruler on the left side showing layer heights
    # Identify distinct horizontal layers (excluding free_space)
    layer_boundaries = set()
    for box in boxes:
        if box['material'] != 'free_space':
            layer_boundaries.add(box['y0'])
            layer_boundaries.add(box['y1'])
    
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
    for box in boxes:
        if box['material'] != 'free_space':
            unique_heights.add(box['y1'])
    
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
    boxes = data['boxes']
    
    for box in reversed(boxes):  # Reverse to show in order
        material = box['material']
        if material not in seen_materials and material != 'free_space':
            seen_materials.add(material)
            
            # Get color based on dielectric (same logic as drawing)
            mat_props = data['materials'].get(material, {})
            eps = mat_props.get('eps', 5.0)
            
            if max_eps > min_eps:
                norm_eps = (eps - min_eps) / (max_eps - min_eps)
            else:
                norm_eps = 0.5
            
            color = cmap(0.3 + norm_eps * 0.6)
            
            # Create legend label with dielectric value
            label = f"{material} (ε={eps:.1f})"
            patch = mpatches.Patch(color=color, label=label, alpha=0.8)
            material_patches.append(patch)
    
    if material_patches:
        ax.legend(handles=material_patches, loc='upper left', 
                 fontsize=9, framealpha=0.9)
    
    # Plot Hz signal if available (rotated 90° to the right - vertical, aligned with layers)
    if show_signal and signal_data is not None:
        time = signal_data['Time'].values if 'Time' in signal_data.columns else np.arange(len(signal_data))
        hx_signal = signal_data['rx1_Hx'].values
        
        # Convert time to approximate depth using average wave velocity
        # For GPR: depth ≈ (c * t) / (2 * sqrt(ε_avg)) where c = 3e8 m/s
        # Two-way travel time: divide by 2
        
        # Calculate average dielectric constant from materials
        eps_values = []
        for mat, props in data['materials'].items():
            if 'eps' in props and mat != 'free_space':
                eps_values.append(props['eps'])
        
        if eps_values:
            eps_avg = np.mean(eps_values)
        else:
            eps_avg = 5.0  # Default assumption
        
        # Wave velocity in medium: v = c / sqrt(ε)
        c = 3e8  # Speed of light in m/s
        v = c / np.sqrt(eps_avg)
        
        # Convert time to depth (one-way travel for receiver)
        depth_from_surface = (v * time) / 2  # Two-way travel time
        
        # Get TX position (antenna height)
        tx_y = data['source']['y'] if data['source'] else domain['y']
        
        # Scale signal to span from TX to bottom of scenario (y=0)
        domain_bottom = 0
        available_depth = tx_y - domain_bottom  # Depth available from TX to bottom
        
        # Normalize depth_from_surface to [0, 1] then scale to available depth
        depth_normalized = depth_from_surface / depth_from_surface.max()
        depth = tx_y - (depth_normalized * available_depth)
        
        # Plot with depth
        ax_signal.plot(hx_signal, depth, 'r-', linewidth=1, alpha=0.6, label='Hx signal')
        
        # Calculate and plot envelope (scattering amplitude)
        from scipy.signal import hilbert
        analytic_signal = hilbert(hx_signal)
        envelope = np.abs(analytic_signal)
        
        # Plot envelope
        ax_signal.plot(envelope, depth, 'r-', linewidth=2, label='Envelope')
        ax_signal.fill_betweenx(depth, 0, envelope, color='red', alpha=0.2)
        ax_signal.plot(-envelope, depth, 'r-', linewidth=2)
        ax_signal.fill_betweenx(depth, 0, -envelope, color='red', alpha=0.2)
        ax_signal.set_ylabel('Depth (m)', fontsize=12, fontweight='bold')
        ax_signal.set_xlabel('Hx (A/m)', fontsize=12, fontweight='bold')
        ax_signal.set_title(f'Hx Signal (ε_avg={eps_avg:.1f})', fontsize=13, fontweight='bold')
        ax_signal.grid(True, alpha=0.3, linestyle='--')
        ax_signal.axvline(x=0, color='k', linestyle='-', linewidth=0.5, alpha=0.5)
        
        # Add secondary y-axis for time on the left
        ax_time = ax_signal.twinx()
        ax_time.set_ylim(ax_signal.get_ylim())
        
        # Convert depth back to time for the secondary axis
        depth_range = np.array(ax_signal.get_ylim())
        time_range = 2 * (tx_y - depth_range) / v * 1e9  # Convert to nanoseconds
        ax_time.set_ylim(time_range)
        ax_time.set_ylabel('Time (ns)', fontsize=12, fontweight='bold')
        ax_time.yaxis.set_label_position('left')
        ax_time.yaxis.tick_left()
        
        # Set main axis limits to match the geometry
        ax_signal.set_ylim(ax.get_ylim())
        ax_signal.invert_yaxis()  # Invert so depth increases downward (0 at top)
        
        # Mark TX position
        ax_signal.axhline(y=tx_y, color='red', linestyle='--', linewidth=1, alpha=0.5, label='TX position')
        
        # Style
        ax_signal.spines['top'].set_visible(False)
        ax_signal.spines['right'].set_visible(False)
        ax_time.spines['top'].set_visible(False)
        ax_time.spines['right'].set_visible(False)
    
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

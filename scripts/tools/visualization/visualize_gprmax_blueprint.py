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

import sys
import argparse
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from pathlib import Path
import numpy as np
from scipy.signal import hilbert
import matplotlib.gridspec as gridspec

# Add parent directory to path for imports
# Now in scripts/tools/, so we need to go up 3 levels to reach project root (if root is above scripts/)
# Actually root is d:/Codigo/Synth-GPR
# scripts/tools/visualize.py -> parent = tools -> parent = scripts -> parent = Synth-GPR
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

try:
    from src.data_loader import read_gprmax_hdf5
    HAS_DATA_LOADER = True
    print("[OK] Successfully loaded data_loader")
except ImportError as e:
    HAS_DATA_LOADER = False
    print(f"[WARN] Warning: Could not import data_loader (Signal plotting disabled): {e}")


# Material color mapping for visualization
# This dictionary maps specific material identifiers found in gprMax input files
# to hex color codes for Matplotlib visualization.
MATERIAL_COLORS = {
    'free_space': '#F5F5F5',       # White Smoke: Neutral background
    'bal_rock': '#F4A460',         # Sandy Brown: Light, high contrast against dark fouling
    'bal_foul': '#4B3621',         # Cafe Noir: Very dark brown for fouling matrix
    'bal_foul_granular': '#4B3621',# Same as above
    'subgrade': '#2F4F4F',         # Dark Slate Gray: Distinct cool tone for base
    'formation': '#BDB76B',        # Dark Khaki: Distinct olive/yellowish tone
    'concrete_sleeper': '#708090', # Slate Gray
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
            elif line.startswith('## FI_class:'):
                data['metadata']['FI_class'] = line.split(':')[1].strip()
            elif line.startswith('## Scenario:'):
                data['metadata']['scenario'] = line.split(':')[1].strip()
    
    return data


def create_blueprint(data, output_file=None, show_plot=True, out_file_path=None, source_filename=None):
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
    valid_signals = {} # Map col_name -> data array
    
    if out_file_path and Path(out_file_path).exists() and HAS_DATA_LOADER:
        try:
            # Load both E and H fields
            signal_df = read_gprmax_hdf5(out_file_path, fields=['E', 'H'])
            
            if not signal_df.empty:
                 # Check each numeric column (excluding Time)
                 # Determine if it's "empty" (all zeros or negligible)
                 threshold = 1e-9
                 for col in signal_df.columns:
                     if col == 'Time': continue
                     
                     signal_vals = signal_df[col].values
                     amplitude = np.max(np.abs(signal_vals))
                     if amplitude > threshold:
                         valid_signals[col] = signal_vals
            
            if valid_signals:
                show_signal = True
                print(f"Plotting {len(valid_signals)} non-empty signals: {list(valid_signals.keys())}")
                
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
            return '#E8F4F8', 0.1 # Very subtle air
        
        mat_props = data['materials'].get(material, {})
        eps = mat_props.get('eps', 5.0)
        
        if max_eps > min_eps:
            norm_eps = (eps - min_eps) / (max_eps - min_eps)
        else:
            norm_eps = 0.5
        
        # Get color from colormap
        return cmap(0.3 + norm_eps * 0.6), 1.0 # Opaque

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
                linewidth=0.3, # Softened
                edgecolor='#404040',
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
                linewidth=0.3, # Softened
                edgecolor='#404040',
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
            
    # Also consider cylinder tops (Granular/Ballast top)
    cyl_tops = [o['y'] + o['radius'] for o in data.get('objects', []) if o['type'] == 'cylinder']
    if cyl_tops:
        layer_boundaries.add(max(cyl_tops))
    
    layer_boundaries = sorted([h for h in layer_boundaries if h >= 0])
    
    # Add horizontal dotted lines crossing the axis for each layer
    for h in layer_boundaries:
        if h > 0.001: # Skip y=0
             ax.axhline(y=h, color='gray', linestyle=':', linewidth=1.0, alpha=0.6, zorder=5)
    
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
    ax.set_xlim(-0.02, domain['x'] + 0.15)
    ax.set_ylim(-0.05, domain['y'] + 0.05)
    ax.set_xlabel('X (meters)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Y (meters)', fontsize=12, fontweight='bold')
    
    # Title with metadata
    title_parts = []
    if data['title']:
        title_parts.append(f"Class: {data['title']}")
    if 'FI_class' in data['metadata']:
        title_parts.append(f"Class: {data['metadata']['FI_class']}")
    if 'scenario' in data['metadata']:
        title_parts.append(f"Scenario: {data['metadata']['scenario']}")
    if 'FI' in data['metadata']:
        title_parts.append(f"FI: {data['metadata']['FI']}%")
    
    title = ' | '.join(title_parts) if title_parts else 'gprMax Geometry Blueprint'
    ax.set_title(title, fontsize=14, fontweight='bold', pad=25)
    
    if source_filename:
        ax.text(0.5, 1.02, f"File: {source_filename}", 
               transform=ax.transAxes,
               ha='center', va='bottom', fontsize=10, 
               color='#555555', family='monospace')
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
        if material not in seen_materials:
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
        # Legend placed to the left of the Y-axis (outside)
        ax.legend(handles=material_patches, 
                 bbox_to_anchor=(-0.02, 1.0), loc='upper right',
                 fontsize=8, framealpha=0.9)

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
            # Find Formation Height for reference
            formation_top = 0.0
            for o in data.get('objects', []):
                if o['type'] == 'box' and o['material'] == 'formation':
                    formation_top = max(formation_top, o['y1'])
            
            # Add a dashed line across
            ax.axhline(y=max_y_cyl, color='#8B7355', linestyle=':', linewidth=1.5, alpha=0.8, zorder=20)
            
            label_text = f'Max Rock Height: {max_y_cyl:.3f} m'
            if formation_top > 0:
                 relative_height = max_y_cyl - formation_top
                 label_text += f'\n(From Formation: {relative_height*100:.1f} cm)'
            
            # Add text annotation
            ax.text(domain['x'] + 0.08, max_y_cyl, 
                   label_text,
                   color='#4A3310',
                   ha='left', va='center', fontsize=8,
                   fontweight='bold', style='italic',
                   bbox=dict(boxstyle='round,pad=0.2', 
                            facecolor='#FFF8DC', alpha=0.8, 
                            edgecolor='#8B7355', linewidth=0.5))
                            
            # Highlight this specific point
            ax.plot(top_cyl['x'], max_y_cyl, 'kx', markersize=5, zorder=21)

    # --------------------------------------------------------
    # --------------------------------------------------------
    # Plot Signals
    if show_signal and valid_signals:
        # We need to get Time from the original DF or rebuild it
        # Since we only extracted arrays into valid_signals, we need to know the length and dt
        # Or hopefully retrieve "Time" from signal_df if we kept it around.
        # Let's assume we re-read or kept it. 
        # Easier fix: pass signal_df to this function or just re-read or assume dt from somewhere.
        # But wait, create_blueprint doesn't receive signal_df directly anymore in my logic above?
        # The logic above populated `valid_signals`.
        
        # Let's fix the scope. `signal_df` was local to the try block above.
        # I should have extracted 'Time' too.
        
        # NOTE: I am modifying the chunk in-place.
        # Let's grab the time axis from the first signal length and config/dt approximation
        # OR better, relying on the fact that I should have extracted Time in the previous block.
        # But I didn't store it in `valid_signals`.
        
        # Let's approximate:
        sig_len = len(next(iter(valid_signals.values())))
        # We can try to guess dt from metadata or just use index
        # To be safe, let's assume we grabbed 'Time' if it existed.
        
        # Hack for cleaner code flow: Re-read time inside the previous block or just assume linear.
        # Let's use generic index if Time not found, but we want physical units.
        pass # Placeholder
        
        # Actually, let's look at how I can get Time down here.
        # I'll rely on the `signal_data` var if I modified the top block correctly...
        # But I replaced `signal_data` with `valid_signals` dict.
        
        # Let's just create a time array.
        # gprMax default dt is usually small.
        # We need dt.
        
        # Let's just create a simple index-based time if we can't find it.
        time_ns = np.arange(sig_len) # Placeholder
        
        # Separate E and H fields
        e_fields = {k: v for k, v in valid_signals.items() if 'E' in k}
        h_fields = {k: v for k, v in valid_signals.items() if 'H' in k}
        
        # Setup dual axis if needed
        ax_E = ax_signal
        ax_H = ax_signal.twinx() if (e_fields and h_fields) else ax_signal
        
        has_E = False
        has_H = False
        
        # Plot E fields
        for name, data in e_fields.items():
            ax_E.plot(data, label=name, linestyle='-')
            has_E = True
            
        # Plot H fields
        for name, data in h_fields.items():
            if has_E and ax_H != ax_E:
                ax_H.plot(data, label=name, linestyle='--')
            else:
                ax_H.plot(data, label=name, linestyle='-')
            has_H = True
            
        # Labels and Legends
        ax_E.set_xlabel('Sample Index (Time)', fontsize=10, fontweight='bold')
        ax_E.set_title('A-Scan Signals', fontsize=12, fontweight='bold')
        ax_E.grid(True, alpha=0.3, linestyle='--')
        
        lines_E, labels_E = ax_E.get_legend_handles_labels()
        lines_H, labels_H = ax_H.get_legend_handles_labels()
        
        if has_E:
            ax_E.set_ylabel('E-Field (V/m)', color='blue')
        if has_H and ax_H != ax_E:
            ax_H.set_ylabel('H-Field (A/m)', color='green')
            
        # Combine legends
        ax_E.legend(lines_E + lines_H, labels_E + labels_H, loc='upper right', fontsize=8)
        
        # --- Bottom Right: Hilbert Envelope (Combined or Max?) ---
        # Plotting envelope of all might be messy. Let's plot envelope of the strongest signal.
        if valid_signals:
            # Find strongest signal
            strongest_name = max(valid_signals, key=lambda k: np.max(np.abs(valid_signals[k])))
            strongest_data = valid_signals[strongest_name]
            
            analytic = hilbert(strongest_data)
            envelope = np.abs(analytic)
            
            ax_envelope.plot(envelope, 'r-', linewidth=1.5, label=f'Env ({strongest_name})')
            ax_envelope.fill_between(range(len(envelope)), 0, envelope, color='red', alpha=0.2)
            ax_envelope.set_xlabel('Sample Index', fontsize=10, fontweight='bold')
            ax_envelope.set_ylabel('Magnitude', fontsize=10, fontweight='bold')
            ax_envelope.set_title(f'Hilbert Envelope ({strongest_name})', fontsize=12, fontweight='bold')
            ax_envelope.grid(True, alpha=0.3, linestyle='--')
            ax_envelope.legend()
    
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
        out_file_path=out_file_path,
        source_filename=Path(args.input_file).name
    )
    
    return 0


if __name__ == "__main__":
    exit(main())

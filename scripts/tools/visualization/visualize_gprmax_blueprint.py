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
from scipy.signal import hilbert, stft, convolve
import matplotlib.gridspec as gridspec

# Add parent directory to path for imports
# Now in scripts/tools/, so we need to go up 3 levels to reach project root (if root is above scripts/)
# Actually root is d:/Codigo/Synth-GPR
# scripts/tools/visualize.py -> parent = tools -> parent = scripts -> parent = Synth-GPR
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

try:
    from src.data_loader import read_gprmax_hdf5
    HAS_DATA_LOADER = True
except ImportError as e:
    HAS_DATA_LOADER = False


# === CONSTANTS ===
# Signal processing
SIGNAL_AMPLITUDE_THRESHOLD = 1e-9  # Minimum amplitude to consider signal non-empty

# Figure sizes
BLUEPRINT_FIGURE_SIZE = (12, 8)  # Width, height in inches for blueprint-only view
SIGNAL_FIGURE_SIZE = (16, 8)     # Width, height in inches for blueprint + signal view

# Visual styling
DEFAULT_LINE_WIDTH = 0.3    # Line width for geometry edges
EDGE_COLOR = '#404040'      # Default edge color for geometry objects
FREE_SPACE_COLOR = '#E8F4F8'  # Color for free_space material
FREE_SPACE_ALPHA = 0.1      # Alpha transparency for free_space

# Annotation thresholds
MIN_LAYER_HEIGHT = 0.001    # Minimum height (m) to draw layer boundary line
MIN_ANNOTATION_HEIGHT = 0.01  # Minimum height (m) to add text annotation

# Plot DPI
OUTPUT_DPI = 300  # DPI for saved images


# === HELPER FUNCTIONS ===

def generate_material_colors():
    """
    Generate the complete material colors dictionary for visualization.
    
    This dictionary maps specific material identifiers found in gprMax input files
    to hex color codes or RGBA tuples for Matplotlib visualization.
    
    Returns:
        dict: Mapping of material_name -> color (hex string or RGBA tuple)
    """
    colors = {
        'free_space': '#F5F5F5',       # White Smoke: Neutral background
        'bal_rock': '#F4A460',         # Sandy Brown: Light, high contrast against dark fouling
        'bal_foul': '#4B3621',         # Cafe Noir: Very dark brown for fouling matrix
        'bal_foul_granular': '#4B3621',# Same as above (overwritten below)
        'subgrade': '#2F4F4F',         # Dark Slate Gray: Distinct cool tone for base
        'formation': '#BDB76B',        # Dark Khaki: Distinct olive/yellowish tone
        'concrete_sleeper': '#708090', # Slate Gray
    }
    
    # Add gradient materials dynamically
    # Generates colors for 'bal_foul_g1' to 'bal_foul_g9' to visualize varying degrees of fouling
    # using the YlOrBr (Yellow-Orange-Brown) colormap.
    for i in range(1, 10):
        colors[f'bal_foul_g{i}'] = plt.cm.YlOrBr(0.3 + i * 0.07)
    
    # Add Granular mode materials (High-Fidelity)
    # Specific colors for granular simulation components
    colors['bal_foul_granular'] = '#5D4037'  # Darker brown for the fine matrix between rocks
    colors['bal_rock_L1'] = '#A1887F'        # Lighter brown for Small rocks
    colors['bal_rock_L2'] = '#8D6E63'        # Medium brown for Medium rocks
    colors['bal_rock_L3'] = '#6D4C41'        # Darker brown for Large rocks
    
    return colors


# Initialize module-level material colors using the generator function
MATERIAL_COLORS = generate_material_colors()


def filter_cylinders(objects):
    """
    Filter and return only cylinder objects from an objects list.
    
    Args:
        objects (list): List of geometry objects with 'type' key
        
    Returns:
        list: Filtered list containing only cylinder objects
    """
    return [obj for obj in objects if obj.get('type') == 'cylinder']


def filter_boxes(objects, exclude_material=None):
    """
    Filter and return only box objects from an objects list.
    
    Args:
        objects (list): List of geometry objects with 'type' key
        exclude_material (str, optional): Material name to exclude from results
        
    Returns:
        list: Filtered list containing only box objects (excluding specified material if provided)
    """
    boxes = [obj for obj in objects if obj.get('type') == 'box']
    
    if exclude_material:
        boxes = [box for box in boxes if box.get('material') != exclude_material]
    
    return boxes


def get_material_color_alpha(material, materials_dict, min_eps, max_eps, cmap):
    """
    Get the color and alpha value for a given material based on its dielectric constant.
    
    Args:
        material (str): Material name
        materials_dict (dict): Dictionary mapping material names to properties (eps, sigma)
        min_eps (float): Minimum epsilon value in the domain
        max_eps (float): Maximum epsilon value in the domain
        cmap: Matplotlib colormap to use for color mapping
        
    Returns:
        tuple: (color, alpha) where color is hex string or RGBA and alpha is float 0-1
    """
    if material == 'free_space':
        return FREE_SPACE_COLOR, FREE_SPACE_ALPHA
    
    mat_props = materials_dict.get(material, {})
    eps = mat_props.get('eps', 5.0)
    
    if max_eps > min_eps:
        norm_eps = (eps - min_eps) / (max_eps - min_eps)
    else:
        norm_eps = 0.5
    
    # Get color from colormap
    return cmap(0.3 + norm_eps * 0.6), 1.0  # Opaque



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
    print(f"[LOG] Parsing input file: {filepath}")
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
                print(f"[LOG] Found domain: {data['domain']['x']}m × {data['domain']['y']}m × {data['domain']['z']}m")
            
            # Parse materials
            elif line.startswith('#material:'):
                parts = line.split(':')[1].strip().split()
                material_name = parts[-1]  # Last part is the name
                data['materials'][material_name] = {
                    'eps': float(parts[0]),
                    'sigma': float(parts[1]),
                }
                print(f"[LOG] Material '{material_name}': ε_r={parts[0]}, σ={parts[1]}")
            
            # Parse boxes
            elif line.startswith('#box:'):
                parts = line.split(':')[1].strip().split()
                material_name = parts[6]
                print(f"[LOG] Box: material='{material_name}', bounds=({parts[0]},{parts[1]},{parts[2]}) to ({parts[3]},{parts[4]},{parts[5]})")
                data['objects'].append({
                    'type': 'box',
                    'material': material_name,
                    'order': order_counter,
                    'x1': float(parts[0]),
                    'y1': float(parts[1]),
                    'z1': float(parts[2]),
                    'x2': float(parts[3]),
                    'y2': float(parts[4]),
                    'z2': float(parts[5])
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
            
            # Parse waveforms
            elif line.startswith('#waveform:'):
                parts = line.split(':')[1].strip().split()
                waveform_type = parts[0]
                waveform_freq = parts[1]
                waveform_id = parts[2]
                print(f"[LOG] Waveform '{waveform_id}': type={waveform_type}, freq={waveform_freq}Hz")
            
            # Parse source (hertzian dipole)
            elif line.startswith('#hertzian_dipole:'):
                parts = line.split(':')[1].strip().split()
                data['source'] = {
                    'x': float(parts[1]),
                    'y': float(parts[2]),
                    'z': float(parts[3])
                }
                print(f"[LOG] Source (TX) at ({parts[1]}, {parts[2]}, {parts[3]})")
            
            # Parse receiver
            elif line.startswith('#rx:'):
                parts = line.split(':')[1].strip().split()
                data['receiver'] = {
                    'x': float(parts[0]),
                    'y': float(parts[1]),
                    'z': float(parts[2])
                }
                print(f"[LOG] Receiver (RX) at ({parts[0]}, {parts[1]}, {parts[2]})")
            
            # Parse metadata
            elif line.startswith('## FI (%):'):
                data['metadata']['FI'] = line.split(':')[1].strip()
            elif line.startswith('## FI_class:'):
                data['metadata']['FI_class'] = line.split(':')[1].strip()
            elif line.startswith('## Scenario:'):
                data['metadata']['scenario'] = line.split(':')[1].strip()
    
    return data


def extract_particle_sizes(filepath):
    """
    Extract particle size distribution from gprMax input file.
    
    Parses all #cylinder commands and extracts radii of bal_rock cylinders.
    
    Args:
        filepath (str): Path to the .in file
        
    Returns:
        np.array: Array of rock radii in millimeters, empty if no rocks found
    """
    radii_m = []
    
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            
            # Parse cylinder commands
            if line.startswith('#cylinder:'):
                parts = line.split(':')[1].strip().split()
                # Format: x1 y1 z1 x2 y2 z2 radius material
                if len(parts) >= 8:
                    radius = float(parts[6])
                    material = parts[7]
                    
                    # Only include bal_rock cylinders
                    if material == 'bal_rock':
                        radii_m.append(radius)
    
    # Convert to mm for better readability
    radii_mm = np.array(radii_m) * 1000  # meters to millimeters
    
    if len(radii_mm) > 0:
        print(f"[LOG] Found {len(radii_mm)} rocks, sizes: {radii_mm.min():.1f}-{radii_mm.max():.1f}mm")
    
    return radii_mm


def _load_signal_data(out_file_path):
    """
    Load and validate signal data from a gprMax .out HDF5 file.
    
    Reads E and H field data, filters out empty signals (below threshold amplitude),
    and returns only non-empty signal arrays.
    
    Args:
        out_file_path (str or Path): Path to .out HDF5 file
        
    Returns:
        dict: Mapping of signal_name -> numpy array for non-empty signals.
              Empty dict if file doesn't exist, can't be loaded, or all signals empty.
    """
    if not out_file_path or not Path(out_file_path).exists():
        return {}
    
    if not HAS_DATA_LOADER:
        return {}
    
    try:
        # Load both E and H fields
        signal_df = read_gprmax_hdf5(out_file_path, fields=['E', 'H'])
        
        if signal_df.empty:
            return {}
        
        # Check each numeric column (excluding Time)
        # Determine if it's "empty" (all zeros or negligible)
        print(f"[LOG] Signal DataFrame has {len(signal_df)} samples, columns: {signal_df.columns.tolist()}")
        
        valid_signals = {}
        for col in signal_df.columns:
            if col == 'Time':
                continue
            
            signal_vals = signal_df[col].values
            amplitude = np.max(np.abs(signal_vals))
            
            if amplitude > SIGNAL_AMPLITUDE_THRESHOLD:
                valid_signals[col] = signal_vals
                print(f"[LOG]   {col}: max amplitude = {amplitude:.2e}")
            else:
                print(f"[LOG]   {col}: EMPTY (max amplitude = {amplitude:.2e})")
        
        if valid_signals:
            print(f"Plotting {len(valid_signals)} non-empty signals: {list(valid_signals.keys())}")
        
        return valid_signals
        
    except Exception as e:
        print(f"Warning: Could not load signal from {out_file_path}: {e}")
        return {}


def _plot_analytic_signal_overlay(ax, signal, signal_name):
    """
    Plot raw A-scan with instantaneous amplitude (envelope) overlay.
    
    Visualization #1: The "Analytic Signal" Overlay
    - Removes phase confusion
    - Clearly defines start/end of reflection events
    - Highlights scattering zones
    
    Args:
        ax: Matplotlib axes
        signal (np.array): Raw signal data
        signal_name (str): Signal name for title
    """
    # Compute analytic signal and envelope
    analytic = hilbert(signal)
    envelope = np.abs(analytic)
    
    # Plot raw signal (lighter, dashed)
    ax.plot(signal, 'b-', linewidth=0.8, alpha=0.5, label='Raw Signal')
    
    # Overlay envelope (bold, solid)
    ax.plot(envelope, 'r-', linewidth=2.0, label='Instantaneous Amplitude (Envelope)')
    ax.plot(-envelope, 'r-', linewidth=2.0, alpha=0.3)  # Mirror for symmetry
    
    ax.set_xlabel('Sample Index (Time)', fontweight='bold')
    ax.set_ylabel('Amplitude', fontweight='bold')
    ax.set_title(f'Analytic Signal: {signal_name}', fontweight='bold')
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.legend(loc='upper right', fontsize=8)
    ax.axhline(y=0, color='k', linestyle='-', linewidth=0.5, alpha=0.3)


def _ricker(points, a):
    """
    Custom Ricker wavelet implementation since scipy.signal.ricker is missing.
    Points is the number of points in the wavelet.
    a is the width parameter.
    """
    A = 2 / (np.sqrt(3 * a) * (np.pi ** 0.25))
    wsq = a ** 2
    vec = np.arange(0, points) - (points - 1.0) / 2
    xsq = vec ** 2
    mod = (1 - xsq / wsq)
    gauss = np.exp(-xsq / (2 * wsq))
    total = A * mod * gauss
    return total

def _cwt(data, wavelet, widths):
    """
    Custom Continuous Wavelet Transform implementation.
    """
    output = np.zeros([len(widths), len(data)])
    for ind, width in enumerate(widths):
        # Generate wavelet with appropriate length (approx 10 * width)
        points = int(min(10 * width, len(data)))
        points = max(points, 10) # Minimum points
        if points % 2 == 0: points += 1 # Odd length
        
        wavelet_data = wavelet(points, width)
        
        # Convolve
        # signal.convolve mode='same'
        output[ind, :] = convolve(data, wavelet_data, mode='same')
    return output

def _plot_cwt_scalogram(ax, signal, signal_name, fs=1e10, widths=None):
    """
    Plot Continuous Wavelet Transform (CWT) scalogram.
    
    Visualization #2: Time-Frequency Scalogram
    - Shows frequency content evolution over time
    - Reveals attenuation (high freq loss)
    - Identifies dispersion (frequency downshifting)
    
    Args:
        ax: Matplotlib axes
        signal (np.array): Signal data
        signal_name (str): Signal name
        fs (float): Sampling frequency (Hz)
        widths (array): Wavelet widths (scales)
    """
    if widths is None:
        # Create scales corresponding to frequencies from 100 MHz to 2000 MHz
        # Scale = fc / (frequency * dt), where fc is center frequency of wavelet
        dt = 1 / fs
        freqs = np.linspace(100e6, 2000e6, 100)  # 100 MHz to 2 GHz
        # A rough approximation for a ~ 1 width
        widths = fs / freqs 
    
    # Compute CWT using custom Ricker wavelet
    coefficients = _cwt(signal, _ricker, widths)
    
    # Convert to power (dB scale)
    power = np.abs(coefficients) ** 2
    power_db = 10 * np.log10(power + 1e-10)
    
    # Create time and frequency axes
    time_axis = np.arange(len(signal)) * (1/fs) * 1e9  # Convert to ns
    freq_axis = (1.0 / widths) * fs / 1e6  # Convert to MHz
    
    # Plot scalogram
    im = ax.pcolormesh(time_axis, freq_axis, power_db, shading='gouraud', cmap='jet')
    
    ax.set_xlabel('Time (ns)', fontweight='bold')
    ax.set_ylabel('Frequency (MHz)', fontweight='bold')
    ax.set_title(f'CWT Scalogram: {signal_name}', fontweight='bold')
    
    # Add colorbar
    cbar = plt.colorbar(im, ax=ax)
    cbar.set_label('Power (dB)', rotation=270, labelpad=15)


def _plot_ghost_reference(ax, signal, reference_signal, signal_name, ref_name='Reference'):
    """
    Plot target A-scan with ghost reference trace for comparison.
    
    Visualization #3: The "Ghost" Reference Trace
    - Provides context for interpretation
    - Instantly shows deviations/anomalies
    - Relative comparison is key
    
    Args:
        ax: Matplotlib axes
        signal (np.array): Target signal
        reference_signal (np.array): Reference/ghost signal
        signal_name (str): Target signal name
        ref_name (str): Reference description
    """
    # Plot ghost reference (faint gray, behind)
    ax.plot(reference_signal, 'gray', linewidth=1.5, alpha=0.3, 
            label=f'{ref_name} (Ghost)', zorder=1)
    
    # Plot target signal (bold color, front)
    ax.plot(signal, 'b-', linewidth=2.0, label=signal_name, zorder=2)
    
    # Highlight deviations
    deviation = signal - reference_signal
    ax.fill_between(range(len(signal)), 0, deviation, 
                     where=(deviation > 0), color='green', alpha=0.2, label='Above Reference')
    ax.fill_between(range(len(signal)), 0, deviation,
                     where=(deviation < 0), color='red', alpha=0.2, label='Below Reference')
    
    ax.set_xlabel('Sample Index (Time)', fontweight='bold')
    ax.set_ylabel('Amplitude', fontweight='bold')
    ax.set_title(f'Ghost Reference: {signal_name}', fontweight='bold')
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.legend(loc='upper right', fontsize=8)
    ax.axhline(y=0, color='k', linestyle='-', linewidth=0.5, alpha=0.3)


def _plot_hodogram(ax, signal, window_start=None, window_end=None, signal_name='Signal'):
    """
    Plot hodogram (phase plot) for analyzing reflection events.
    
    Visualization #4: Hodogram (Phase-Plot)
    - Visualizes phase characteristics
    - Distinguishes clean reflections from complex scattering
    - Analyzes specific time windows
    
    Args:
        ax: Matplotlib axes
        signal (np.array): Signal data
        window_start (int): Start index of analysis window
        window_end (int): End index of analysis window
        signal_name (str): Signal name
    """
    # Extract window
    if window_start is None or window_end is None:
        # Auto-detect strongest reflection
        envelope = np.abs(hilbert(signal))
        peak_idx = np.argmax(envelope)
        window_size = min(100, len(signal) // 4)
        window_start = max(0, peak_idx - window_size // 2)
        window_end = min(len(signal), peak_idx + window_size // 2)
    
    windowed_signal = signal[window_start:window_end]
    
    # Compute Hilbert transform
    analytic = hilbert(windowed_signal)
    real_part = windowed_signal  # Real component
    imag_part = np.imag(analytic)  # Imaginary component (quadrature)
    
    # Create hodogram (phase plot)
    # Color by time to show evolution
    colors = np.arange(len(real_part))
    scatter = ax.scatter(real_part, imag_part, c=colors, cmap='viridis', 
                        s=20, alpha=0.6, edgecolors='k', linewidth=0.5)
    
    # Add trajectory line
    ax.plot(real_part, imag_part, 'k-', linewidth=0.5, alpha=0.3)
    
    # Mark start and end
    ax.plot(real_part[0], imag_part[0], 'go', markersize=10, label='Start', zorder=10)
    ax.plot(real_part[-1], imag_part[-1], 'ro', markersize=10, label='End', zorder=10)
    
    ax.set_xlabel('Amplitude (Real)', fontweight='bold')
    ax.set_ylabel('Amplitude (Quadrature)', fontweight='bold')
    ax.set_title(f'Hodogram: {signal_name} [samples {window_start}-{window_end}]', fontweight='bold')
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.legend(loc='upper right', fontsize=8)
    ax.axhline(y=0, color='k', linestyle='-', linewidth=0.5, alpha=0.3)
    ax.axvline(x=0, color='k', linestyle='-', linewidth=0.5, alpha=0.3)
    ax.set_aspect('equal', adjustable='box')
    
    # Add colorbar for time evolution
    cbar = plt.colorbar(scatter, ax=ax)
    cbar.set_label('Time Evolution', rotation=270, labelpad=15)


def _plot_spectrogram(ax, signal, signal_name, fs=1e10, nperseg=256):
    """
    Plot spectrogram (STFT) showing frequency vs time analysis.
    
    Args:
        ax: Matplotlib axes to plot on
        signal (np.array): Signal data
        signal_name (str): Name of the signal for title
        fs (float): Sampling frequency in Hz (default: 10 GHz for gprMax)
        nperseg (int): Length of each segment for STFT
    """
    # Compute STFT
    f, t, Zxx = stft(signal, fs=fs, nperseg=nperseg)
    
    # Convert to dB scale for better visualization
    magnitude = np.abs(Zxx)
    magnitude_db = 20 * np.log10(magnitude + 1e-10)  # Add small value to avoid log(0)
    
    # Plot spectrogram
    im = ax.pcolormesh(t * 1e9, f / 1e6, magnitude_db, shading='gouraud', cmap='viridis')
    
    # Labels and formatting
    ax.set_ylabel('Frequency (MHz)', fontweight='bold')
    ax.set_xlabel('Time (ns)', fontweight='bold')
    ax.set_title(f'Spectrogram: {signal_name}', fontweight='bold')
    ax.set_ylim([0, fs / 2e6])  # Show up to Nyquist frequency
    
    # Add colorbar
    cbar = plt.colorbar(im, ax=ax)
    cbar.set_label('Magnitude (dB)', rotation=270, labelpad=15)
    
    ax.grid(True, alpha=0.3, linestyle='--')


def _plot_particle_size_distribution(ax, radii_mm):
    """
    Plot grain size distribution curve (semi-log) - industry standard.
    
    Shows cumulative percentage passing vs particle diameter on log scale,
    with shaded zones for gravel, sand, and fines classification.
    
    Args:
        ax: Matplotlib axes
        radii_mm (np.array): Array of rock radii in millimeters
    """
    if len(radii_mm) == 0:
        # No rocks found - show empty message
        ax.text(0.5, 0.5, 'No rocks found\n(Clean ballast)', 
                ha='center', va='center', fontsize=14, color='gray',
                transform=ax.transAxes)
        ax.set_xlim(0.01, 100)
        ax.set_ylim(0, 100)
        ax.set_xlabel('Particle Diameter (mm)', fontweight='bold')
        ax.set_ylabel('Percent Passing (%)', fontweight='bold')
        ax.set_title('Grain Size Distribution', fontweight='bold')
        ax.set_xscale('log')
        ax.grid(True, alpha=0.3, linestyle='--', which='both')
        return
    
    # Convert radii to diameters
    diameters_mm = radii_mm * 2
    
    # Sort diameters for cumulative calculation
    sorted_diameters = np.sort(diameters_mm)
    
    # Calculate cumulative percentage passing
    # "Passing" means smaller than the given size
    n_total = len(sorted_diameters)
    percent_passing = np.arange(1, n_total + 1) / n_total * 100
    
    # Add background shading for soil classification zones
    # Gravel: > 4.75 mm (Sieve No. 4)
    # Sand: 4.75 mm to 0.075 mm (Sieve No. 200)
    # Fines: < 0.075 mm
    
    ax.axvspan(4.75, 100, alpha=0.15, color='brown', label='Gravel (>4.75mm)')
    ax.axvspan(0.075, 4.75, alpha=0.15, color='yellow', label='Sand (0.075-4.75mm)')
    ax.axvspan(0.001, 0.075, alpha=0.15, color='gray', label='Fines (<0.075mm)')
    
    # Add vertical lines for standard sieves
    ax.axvline(4.75, color='red', linestyle='--', linewidth=1.5, 
               alpha=0.7, label='Sieve No. 4')
    ax.axvline(0.075, color='blue', linestyle='--', linewidth=1.5,
               alpha=0.7, label='Sieve No. 200')
    
    # Plot the grain size distribution curve
    ax.plot(sorted_diameters, percent_passing, 'k-', linewidth=2.5, 
            label='Distribution Curve', zorder=10)
    ax.plot(sorted_diameters, percent_passing, 'o', markersize=3, 
            color='darkblue', alpha=0.5, zorder=11)
    
    # Calculate key percentiles (D10, D30, D50, D60)
    if n_total >= 10:
        d10_idx = int(n_total * 0.10)
        d30_idx = int(n_total * 0.30)
        d50_idx = int(n_total * 0.50)
        d60_idx = int(n_total * 0.60)
        
        d10 = sorted_diameters[d10_idx]
        d30 = sorted_diameters[d30_idx]
        d50 = sorted_diameters[d50_idx]
        d60 = sorted_diameters[d60_idx]
        
        # Calculate uniformity coefficient (Cu) and coefficient of curvature (Cc)
        cu = d60 / d10 if d10 > 0 else 0
        cc = (d30 ** 2) / (d60 * d10) if (d60 * d10) > 0 else 0
        
        # Add statistics text box
        stats_text = (f'D₁₀: {d10:.1f}mm\n'
                     f'D₅₀: {d50:.1f}mm\n'
                     f'D₆₀: {d60:.1f}mm\n'
                     f'Cᵤ: {cu:.2f}\n'
                     f'Cᶜ: {cc:.2f}\n'
                     f'n={n_total}')
    else:
        stats_text = f'n={n_total}\n(too few for\ncoefficients)'
    
    ax.text(0.02, 0.98, stats_text,
            transform=ax.transAxes,
            fontsize=8,
            verticalalignment='top',
            horizontalalignment='left',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.7),
            family='monospace')
    
    # Labels and title
    ax.set_xlabel('Particle Diameter (mm)', fontweight='bold', fontsize=10)
    ax.set_ylabel('Percent Passing (%)', fontweight='bold', fontsize=10)
    ax.set_title('Grain Size Distribution Curve', fontweight='bold', fontsize=12)
    
    # Set log scale for x-axis (standard for grain size)
    ax.set_xscale('log')
    
    # Set axis limits adaptively based on data
    min_d = np.min(sorted_diameters)
    max_d = np.max(sorted_diameters)
    
    # For ballast (typically 20-60mm), use tighter range
    # Add 20% margin on each side in log space
    x_min = max(0.1, min_d * 0.5)   # Don't go below 0.1mm
    x_max = min(200, max_d * 2.0)   # Don't go above 200mm
    
    ax.set_xlim(x_min, x_max)
    ax.set_ylim(0, 100)
    
    # Grid
    ax.grid(True, alpha=0.3, linestyle='-', which='major', linewidth=0.8)
    ax.grid(True, alpha=0.15, linestyle=':', which='minor', linewidth=0.5)
    
    # Legend
    ax.legend(loc='lower right', fontsize=7, ncol=2)


def _create_figure_layout(show_signal):
    """
    Create the matplotlib figure layout based on whether signals will be plotted.
    
    When signals are available, creates a comprehensive layout with 5 signal analysis plots + PSD:
    - Row 1: A-scan signals, Analytic signal overlay
    - Row 2: Hilbert envelope, CWT scalogram
    - Row 3: Spectrogram (full width)
    - Row 4: Particle Size Distribution (full width)
    
    Args:
        show_signal (bool): If True, creates signal plots.
    
    Returns:
        tuple: (fig, axes_dict) where axes_dict contains keys:
               'main', 'ascan', 'analytic', 'envelope', 'cwt', 'spectrogram', 'psd'
    """
    axes = {
        'main': None,
        'ascan': None,
        'analytic': None, 
        'envelope': None,
        'cwt': None,
        'spectrogram': None,
        'psd': None
    }
    
    if show_signal:
        print("[LOG] Creating figure with MERGED signal plots (5 visualizations + PSD)")
        fig = plt.figure(figsize=(22, 14))  # Increased height for 4 rows
        
        # Create grid: Left column for blueprint, right side for signals + PSD
        gs = gridspec.GridSpec(4, 3, width_ratios=[1.2, 1, 1], height_ratios=[1, 1, 1, 0.8],
                              hspace=0.3, wspace=0.3)
        
        # Left: Blueprint (full height, spanning all 4 rows)
        axes['main'] = fig.add_subplot(gs[:, 0])
        
        # Right side: signal plots
        # Row 1
        axes['ascan'] = fig.add_subplot(gs[0, 1])        # Top left: A-scan signals
        axes['analytic'] = fig.add_subplot(gs[0, 2])     # Top right: Analytic signal
        
        # Row 2
        axes['envelope'] = fig.add_subplot(gs[1, 1])     # Middle left: Hilbert envelope
        axes['cwt'] = fig.add_subplot(gs[1, 2])          # Middle right: CWT scalogram
        
        # Row 3
        axes['spectrogram'] = fig.add_subplot(gs[2, 1:])  # Spectrogram (full width)
        
        # Row 4
        axes['psd'] = fig.add_subplot(gs[3, 1:])  # PSD histogram (full width)
        
    else:
        print("[LOG] Creating figure without signal plots (blueprint only)")
        fig, axes['main'] = plt.subplots(figsize=BLUEPRINT_FIGURE_SIZE)
    
    return fig, axes



def create_blueprint(data, output_file=None, show_plot=True, out_file_path=None, source_filename=None):
    """
    Create a blueprint visualization of the gprMax geometry using Matplotlib.
    
    Generates a 2D cross-section view (X-Y plane) of the simulation domain.
    Draws objects in the order they appear in the file to correctly visualize layers.
    When signal data is available (.out file), displays all 6 signal analysis plots.
    
    Args:
        data (dict): Parsed geometry data returned by parse_gprmax_input.
        output_file (str, optional): Path to save the resulting image file (e.g. .png).
        show_plot (bool): If True, calls plt.show() to display the window.
        out_file_path (str, optional): Path to a corresponding .out HDF5 file. 
                                       If provided and valid, adds all 6 signal plots.
        source_filename (str, optional): Source filename to display in the plot.
                                       
    Variables:
        fig (Figure): Matplotlib figure object.
        ax (Axes): Main axes for the geometry blueprint.
        objects (list): List of geometry objects (boxes, cylinders) to draw.
        z_order (int): Drawing order index. Higher values are drawn on top.
        material_patches (list): List of patches for the legend.
    """
    # Load signal data if .out file is provided
    valid_signals = _load_signal_data(out_file_path)
    show_signal = bool(valid_signals)
    
    # Create figure layout
    fig, axes = _create_figure_layout(show_signal)
    ax = axes['main']

    
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
    
    
    # Create wrapper for the extracted function with closures
    def get_mat_color_alpha(material):
        return get_material_color_alpha(material, data['materials'], min_eps, max_eps, cmap)


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
            x0, y0 = obj['x1'], obj['y1']
            x1, y1 = obj['x2'], obj['y2']
            width = x1 - x0
            height = y1 - y0
            
            rect = mpatches.Rectangle(
                (x0, y0), width, height,
                linewidth=DEFAULT_LINE_WIDTH,
                edgecolor=EDGE_COLOR,
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
                linewidth=DEFAULT_LINE_WIDTH,
                edgecolor=EDGE_COLOR,
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
            layer_boundaries.add(obj['y1'])
            layer_boundaries.add(obj['y2'])
            
    # Also consider cylinder tops (Granular/Ballast top)
    cylinders = filter_cylinders(data.get('objects', []))
    cyl_tops = [cyl['y'] + cyl['radius'] for cyl in cylinders]
    if cyl_tops:
        layer_boundaries.add(max(cyl_tops))
    
    layer_boundaries = sorted([h for h in layer_boundaries if h >= 0])
    
    # Add horizontal dotted lines crossing the axis for each layer
    for h in layer_boundaries:
        if h > MIN_LAYER_HEIGHT:
             ax.axhline(y=h, color='gray', linestyle=':', linewidth=1.0, alpha=0.6, zorder=5)
    
    # Add height annotations on the right side
    unique_heights = set()
    for obj in data.get('objects', []):
        if obj['type'] == 'box' and obj['material'] != 'free_space':
            unique_heights.add(obj['y2'])
    
    for height in sorted(unique_heights):
        if height > MIN_ANNOTATION_HEIGHT:
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
    cylinders = filter_cylinders(data.get('objects', []))
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
                    formation_top = max(formation_top, o['y2'])
            
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
    print(f"[LOG] Rendering {len(data['objects'])} geometry objects...")
    if show_signal and valid_signals:
        # Find strongest signal for single-channel analysis plots
        strongest_name = max(valid_signals, key=lambda k: np.max(np.abs(valid_signals[k])))
        strongest_data = valid_signals[strongest_name]

        # --- MERGED MODE: ALL 6 PLOTS ---
        
        # Separate E and H fields for A-scan plot
        e_fields = {k: v for k, v in valid_signals.items() if 'E' in k}
        h_fields = {k: v for k, v in valid_signals.items() if 'H' in k}
        
        # === ROW 1: A-Scan Signals & Analytic Signal ===
        
        # Plot 1: A-Scan Signals (E and H fields)
        ax_ascan = axes['ascan']
        ax_E = ax_ascan
        ax_H = ax_ascan.twinx() if (e_fields and h_fields) else ax_ascan
        
        has_E = False
        has_H = False
        
        # Plot E fields
        for name, data_arr in e_fields.items():
            ax_E.plot(data_arr, label=name, linestyle='-')
            has_E = True
            
        # Plot H fields
        for name, data_arr in h_fields.items():
            if has_E and ax_H != ax_E:
                ax_H.plot(data_arr, label=name, linestyle='--')
            else:
                ax_H.plot(data_arr, label=name, linestyle='-')
            has_H = True
            
        # Labels and Legends for A-scan
        ax_E.set_xlabel('Sample Index (Time)', fontsize=10, fontweight='bold')
        ax_E.set_title('A-Scan Signals', fontsize=12, fontweight='bold')
        ax_E.grid(True, alpha=0.3, linestyle='--')
        
        lines_E, labels_E = ax_E.get_legend_handles_labels()
        lines_H, labels_H = ax_H.get_legend_handles_labels()
        
        if has_E:
            ax_E.set_ylabel('E-Field (V/m)', color='blue', fontsize=9)
        if has_H and ax_H != ax_E:
            ax_H.set_ylabel('H-Field (A/m)', color='green', fontsize=9)
        
        # Combine legends
        ax_E.legend(lines_E + lines_H, labels_E + labels_H, loc='upper right', fontsize=7)
        
        # Plot 2: Analytic Signal Overlay
        ax_analytic = axes['analytic']
        _plot_analytic_signal_overlay(ax_analytic, strongest_data, strongest_name)
        
        # === ROW 2: Hilbert Envelope & CWT Scalogram ===
        
        # Plot 3: Hilbert Envelope
        ax_envelope = axes['envelope']
        analytic = hilbert(strongest_data)
        envelope = np.abs(analytic)
        
        ax_envelope.plot(envelope, 'r-', linewidth=1.5, label=f'Env ({strongest_name})')
        ax_envelope.fill_between(range(len(envelope)), 0, envelope, color='red', alpha=0.2)
        ax_envelope.set_xlabel('Sample Index', fontsize=10, fontweight='bold')
        ax_envelope.set_ylabel('Magnitude', fontsize=10, fontweight='bold')
        ax_envelope.set_title(f'Hilbert Envelope ({strongest_name})', fontsize=12, fontweight='bold')
        ax_envelope.grid(True, alpha=0.3, linestyle='--')
        ax_envelope.legend(fontsize=8)
        
        # Plot 4: CWT Scalogram
        ax_cwt = axes['cwt']
        _plot_cwt_scalogram(ax_cwt, strongest_data, strongest_name)
        
        # === ROW 3: Spectrogram ===
        
        # Plot 5: Spectrogram (STFT) - Full width
        ax_spectrogram = axes['spectrogram']
        _plot_spectrogram(ax_spectrogram, strongest_data, strongest_name)
        
        # === ROW 4: Particle Size Distribution ===
        
        # Plot 6: PSD Histogram
        ax_psd = axes['psd']
        particle_sizes = extract_particle_sizes(source_filename)
        _plot_particle_size_distribution(ax_psd, particle_sizes)


    
    plt.tight_layout()
    
    # Save if output file specified
    if output_file:
        plt.savefig(output_file, dpi=OUTPUT_DPI, bbox_inches='tight')
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
    
    # Create blueprint with all visualizations
    create_blueprint(
        data, 
        output_file=args.output, 
        show_plot=not args.no_show,
        out_file_path=out_file_path,
        source_filename=input_path.name
    )
    
    return 0


if __name__ == "__main__":
    exit(main())

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
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

from typing import Dict, Any, Optional, Tuple, List, Union
from dataclasses import dataclass, field
import matplotlib.axes

@dataclass
class ProcessingConfig:
    enable: bool = True
    dewow: bool = True
    gain_type: Optional[str] = None
    gain_alpha: float = 1.0

@dataclass
class FilterConfig:
    components: List[str] = field(default_factory=lambda: ['Ez'])
    receivers: Optional[List[str]] = None

@dataclass
class GeometryEntity:
    material: str
    order: int
    
    
    def draw(self, ax: matplotlib.axes.Axes, style: MaterialStyle) -> None:
        """
        Draws the entity on the given axes.
        
        Args:
            ax: The matplotlib axes to draw on.
            style: The MaterialStyle (color, hatch) to use.
        """
        raise NotImplementedError

@dataclass
class Box(GeometryEntity):
    coords: List[float] # x1, y1, z1, x2, y2, z2
    
    def draw(self, ax: matplotlib.axes.Axes, style: MaterialStyle) -> None:
        """Draws a Box on the axes."""
        c = self.coords
        x, y = c[0], c[1]
        w, h = c[3]-c[0], c[4]-c[1]
        rect = mpatches.Rectangle((x, y), w, h, facecolor=style.color, 
                                  edgecolor='black', linewidth=0.5, hatch=style.hatch)
        ax.add_patch(rect)

@dataclass
class Cylinder(GeometryEntity):
    center: List[float]
    radius: float
    
    
    def draw(self, ax: matplotlib.axes.Axes, style: MaterialStyle) -> None:
        """Draws a Cylinder on the axes."""
        circ = mpatches.Circle(self.center, self.radius, facecolor=style.color, 
                               edgecolor='black', linewidth=0.5, hatch=style.hatch)
        ax.add_patch(circ)

class SignalPlotStrategy:
    """Strategy for plotting signal traces."""
    def plot(self, ax: matplotlib.axes.Axes, time: np.ndarray, signal: np.ndarray, 
             label: str, color: str, linestyle: str = '-') -> None:
        raise NotImplementedError

class LinePlotStrategy(SignalPlotStrategy):
    """Standard line plot."""
    def plot(self, ax: matplotlib.axes.Axes, time: np.ndarray, signal: np.ndarray, 
             label: str, color: str, linestyle: str = '-') -> None:
        ax.plot(time, signal, label=label, color=color, linestyle=linestyle, linewidth=1.2)

class WigglePlotStrategy(SignalPlotStrategy):
    """Seismic-style wiggle trace (Variable Area)."""
    def plot(self, ax: matplotlib.axes.Axes, time: np.ndarray, signal: np.ndarray, 
             label: str, color: str, linestyle: str = '-') -> None:
        # Plot the line
        ax.plot(time, signal, label=label, color=color, linestyle=linestyle, linewidth=0.8, alpha=0.8)
        # Fill positive lobes
        if linestyle == '-': # Only fill primary signals
            ax.fill_between(time, signal, 0, where=(signal > 0), interpolate=True, color=color, alpha=0.3)
import matplotlib.colors 
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.gridspec as gridspec
import numpy as np

@dataclass
class MaterialStyle:
    color: str
    hatch: Optional[str] = None
    label: str = ""

# Material color/hatch mapping
STYLES = {
    'free_space':        MaterialStyle('#F5F5F5', None, 'Free Space'),
    'bal_rock':          MaterialStyle('#F4A460', '/', 'Ballast (Rock)'), # Hatch: diagonal
    'bal_foul':          MaterialStyle('#4B3621', '.', 'Ballast (Fouled)'), # Hatch: dots
    'bal_foul_granular': MaterialStyle('#5D4037', '.', 'Ballast (Granular)'),
    'subgrade':          MaterialStyle('#2F4F4F', '-', 'Subgrade'),       # Hatch: horizontal
    'formation':         MaterialStyle('#BDB76B', '+', 'Formation'),      # Hatch: cross
    'concrete_sleeper':  MaterialStyle('#708090', 'x', 'Sleeper'),        # Hatch: diagonal cross
    'bal_rock_L1':       MaterialStyle('#A1887F', '/', 'Rock L1'),
    'bal_rock_L2':       MaterialStyle('#8D6E63', '//', 'Rock L2'),
    'bal_rock_L3':       MaterialStyle('#6D4C41', '///', 'Rock L3'),
}

# Add gradient styles (dynamic)
for i in range(1, 10):
    STYLES[f'bal_foul_g{i}'] = MaterialStyle(
        matplotlib.colors.to_hex(plt.cm.YlOrBr(0.3 + i * 0.07)), 
        '.' * ((i % 3) + 1), 
        f'Foul L{i}'
    )

# Try importing project modules
try:
    import pandas as pd
    from src.data_loader import read_gprmax_hdf5
    from src.signal_processing import preprocess_signal, compute_spectrum, calculate_instantaneous_attributes, compute_spectrogram
    from src.feature_extraction import extract_features
    HAS_DATA_LOADER = True
except ImportError as e:
    HAS_DATA_LOADER = False
    logging.warning(f"Could not import project modules: {e}. Signal plotting disabled.")

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger("Visualizer")

class GPRResultVisualizer:
    """
    Class to visualize gprMax simulation inputs and results.
    
    Encapsulates the logic for parsing geometry, loading signal data,
    processing signals, and generating the dashboard plot.
    """
    
    # Material color mapping
    # Material color mapping (Moved to global STYLES)

    # Constants
    DEFAULT_DT = 1e-10
    SIGNAL_THRESHOLD = 1e-9
    MAX_FEATURES = 3
    PRE_TIME_ZERO_SAMPLES = 5
    SIGNAL_COLORS = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b']

    def __init__(self, input_file: str, output_file: Optional[str] = None, show_plot: bool = True, 
                 process_config: Optional[ProcessingConfig] = None, filter_config: Optional[FilterConfig] = None):
        """
        Initialize the visualizer.
        
        Args:
            input_file: Path to the .in file.
            output_file: Optional path to save the plot image.
            show_plot: Whether to display the plot window.
            process_config: Processing configuration object.
            filter_config: Filtering configuration object.
        """
        self.input_file = Path(input_file)
        self.output_file = output_file
        self.show_plot = show_plot
        self.process_config = process_config or ProcessingConfig()
        self.filter_config = filter_config or FilterConfig()
        
        # Select Strategy (could be Configured)
        self.plot_strategy = WigglePlotStrategy() # Default to Wiggle for "Best Practice" look
        
        self.data = self._parse_input(self.input_file)
        self.signals = {}
        self.dt = self.DEFAULT_DT
        
        # Check for output file
        self.out_file = self.input_file.with_suffix('.out')
        if not self.out_file.exists():
            # Try looking in 'outputs' dir relative to input
             possible = self.input_file.parent / 'outputs' / self.out_file.name
             if possible.exists():
                 self.out_file = possible



    def run(self) -> None:
        """Main execution method."""
        logger.info(f"Visualizing: {self.input_file.name}")
        
        # Load signals if available
        if self.out_file.exists() and HAS_DATA_LOADER:
            self._load_signals()
        else:
            logger.info("No .out file found or dependencies missing. Skipping signal plotting.")
            
        self._create_plot()

    def _parse_input(self, filepath: Path) -> Dict[str, Any]:
        """Parses the gprMax input file."""
        logger.info(f"Parsing {filepath}...")
        data = {
            'title': 'gprMax Simulation',
            'domain': {'x': 0.0, 'y': 0.0, 'z': 0.0},
            'materials': {},
            'objects': [],
            'source': None,
            'receiver': None,
            'metadata': {}
        }
        
        try:
            with open(filepath, 'r') as f:
                lines = f.readlines()
                
            for i, line in enumerate(lines):
                line = line.strip()
                if not line or line.startswith('#python'): continue
                
                parts = line.split()
                cmd = parts[0].lower() if parts else ''
                
                if cmd == '#domain:':
                    data['domain'] = {'x': float(parts[1]), 'y': float(parts[2]), 'z': float(parts[3])}
                elif cmd == '#material:':
                    # #material: f_r f_i sigma_r sigma_i ID
                    mat_id = parts[5] if len(parts) >= 6 else 'unknown'
                    data['materials'][mat_id] = {'eps': float(parts[1]), 'sigma': float(parts[3])}
                elif cmd == '#box:':
                    # #box: x1 y1 z1 x2 y2 z2 ID
                    coords = [float(p) for p in parts[1:7]]
                    mat = parts[7]
                    data['objects'].append(Box(material=mat, order=i, coords=coords))
                elif cmd == '#cylinder:':
                    # #cylinder: x y z radius length ID
                    data['objects'].append(Cylinder(
                        material=parts[8],
                        order=i,
                        center=[float(parts[1]), float(parts[2])],
                        radius=float(parts[7])
                    ))
                elif cmd == '#hertzian_dipole:':
                    data['source'] = {'x': float(parts[2]), 'y': float(parts[3]), 'z': float(parts[4])}
                elif cmd == '#rx:':
                    data['receiver'] = {'x': float(parts[1]), 'y': float(parts[2]), 'z': float(parts[3])}
                elif cmd == '#title:':
                    data['title'] = ' '.join(parts[1:])
                # Metadata
                elif line.startswith('## FI (%):'):
                    data['metadata']['FI'] = line.split(':')[1].strip()
                elif line.startswith('## FI_class:'):
                    data['metadata']['FI_class'] = line.split(':')[1].strip()
                elif line.startswith('## Scenario:'):
                    data['metadata']['scenario'] = line.split(':')[1].strip()
                    
            return data
        except Exception as e:
            logger.error(f"Error parsing input file: {e}", exc_info=True)
            return data

    def _load_signals(self) -> None:
        """Loads and filters signals from HDF5."""
        logger.info(f"Loading signals from {self.out_file}...")
        try:
            df = read_gprmax_hdf5(str(self.out_file), fields=['E', 'H'])
            if df.empty:
                logger.warning("Loaded DataFrame is empty.")
                return

            if 'Time' in df.columns:
                self.time_vector = df['Time'].values
                # Estimate dt
                if len(self.time_vector) > 1:
                    self.dt = (self.time_vector[1] - self.time_vector[0])
            
            # Filter Logic
            valid_signals = {}
            threshold = self.SIGNAL_THRESHOLD
            
            # Apply filters
            target_comps = self.filter_config.components
            if target_comps and 'all' in target_comps: target_comps = None
            
            target_rxs = self.filter_config.receivers
            
            for col in df.columns:
                if col == 'Time': continue
                
                # Check amplitude
                vals = df[col].values
                if np.max(np.abs(vals)) < threshold: continue
                
                # Parse Name
                parts = col.split('_')
                if len(parts) >= 2:
                    rx_name = parts[0]
                    comp_name = parts[1]
                    
                    if target_comps and comp_name not in target_comps: continue
                    if target_rxs and rx_name not in target_rxs: continue
                
                valid_signals[col] = vals
                
            self.signals = valid_signals
            logger.info(f"Signals loaded: {list(self.signals.keys())}")
            
        except Exception as e:
            logger.error(f"Failed to load signals: {e}", exc_info=True)

    def _get_feature_text(self, signal_map: Dict[str, np.ndarray]) -> str:
        """Calculates features for overlay."""
        if not signal_map: return ""
        
        txt_output = "Features:\n"
        count = 0
        max_show = self.MAX_FEATURES
        
        for name, sig in signal_map.items():
            if count >= max_show:
                txt_output += "..."
                break
            try:
                # Create minimal DF
                df_tmp = pd.DataFrame({'Time': np.arange(len(sig))*self.dt, 'Signal': sig})
                # Dummy metadata
                for c in ['gprMax', 'Title', 'Iterations', 'nx_ny_nz', 'dx_dy_dz', 'dt', 'srcsteps', 'rxsteps', 'nsrc', 'nrx']:
                    df_tmp[c] = 0
                    
                df_feats = extract_features(df_tmp, dt=self.dt)
                if not df_feats.empty:
                    # Extract
                    dom_freq = df_feats.iloc[0]['dominant_frequency'] / 1e6
                    entropy = df_feats.iloc[0]['spectral_entropy']
                    rms = df_feats.iloc[0]['root_mean_square']
                    
                    txt_output += (f"[{name}]\n"
                                   f" Freq: {dom_freq:.0f}M | Ent: {entropy:.2f} | RMS: {rms:.1e}\n")
                    count += 1
            except Exception as e:
                logger.warning(f"Feature extraction error for {name}: {e}")
                
        return txt_output.strip()

    def _plot_signal_column(self, ax_time: matplotlib.axes.Axes, ax_env: matplotlib.axes.Axes, 
                            ax_freq: matplotlib.axes.Axes, signals: Dict[str, np.ndarray], 
                            title_prefix: str, info_text: str = "", feature_text: str = "") -> None:
        """Plots a column of signal analysis (Time, Envelope, Freq)."""
        if not signals:
            return
            
        time_ns = self.time_vector * 1e9 if self.time_vector is not None else np.arange(len(next(iter(signals.values())))) * self.dt * 1e9
        
        
        # 1. Time Plot (A-Scan)
        colors = self.SIGNAL_COLORS
        ax_h_twin = ax_time.twinx() if any('H' in k for k in signals) and any('E' in k for k in signals) else ax_time
        
        strongest_sig = None
        max_amp = -1
        
        for i, (name, sig) in enumerate(signals.items()):
            c = colors[i % len(colors)]
            if 'E' in name:
                self.plot_strategy.plot(ax_time, time_ns, sig, label=name, color=c)
            elif 'H' in name:
                target_ax = ax_h_twin if ax_h_twin != ax_time else ax_time
                self.plot_strategy.plot(target_ax, time_ns, sig, label=name, color=c, linestyle='--')
                
            amp = np.max(np.abs(sig))
            if amp > max_amp:
                max_amp = amp
                strongest_sig = sig
                
        # Decoration
        ax_time.set_title(f"{title_prefix} Signal")
        ax_time.set_xlabel(f"Time [ns]\n[{info_text}]", fontsize=8)
        ax_time.grid(True, alpha=0.3)
        ax_time.legend(loc='upper right', fontsize='small')
        
        # Overlay Box
        if feature_text:
            props = dict(boxstyle='round', facecolor='wheat', alpha=0.8)
            ax_time.text(0.02, 0.98, feature_text, transform=ax_time.transAxes, fontsize=7,
                         verticalalignment='top', bbox=props, zorder=100)
                         
        # Time Zero Visuals
        ax_time.axvline(0, color='black', linestyle=':', linewidth=1, alpha=0.6)
        if len(time_ns) > 1:
            dt_ns = time_ns[1] - time_ns[0]
            ax_time.set_xlim(left=-self.PRE_TIME_ZERO_SAMPLES * dt_ns)

        # 2. Envelope & Inst Attributes
        if strongest_sig is not None:
            attrs = calculate_instantaneous_attributes(strongest_sig, self.dt)
            env = attrs['envelope']
            cos_phase = attrs['cosine_phase']
            
            # Twin axis for Phase
            ax_phase = ax_env.twinx()
            ax_phase.fill_between(time_ns, cos_phase, color='gray', alpha=0.15, label='CosPhase')
            ax_phase.set_ylim(-1.5, 1.5)
            ax_phase.set_yticks([])
            
            # Envelope
            ax_env.plot(time_ns, env, color='orange', label='Envelope', linewidth=1.5)
            
            ax_env.set_title(f"{title_prefix} Env/Phase")
            ax_env.set_xlabel("Time [ns]")
            ax_env.grid(True, alpha=0.3)
            
            # Legend
            l1, lab1 = ax_env.get_legend_handles_labels()
            l2, lab2 = ax_phase.get_legend_handles_labels()
            ax_env.legend(l1+l2, lab1+lab2, loc='upper right', fontsize='small')

        # 3. Spectrum
        # 3. Spectrogram (Time-Frequency)
        if strongest_sig is not None:
            # Spectrogram Parameters
            fs = 1.0 / self.dt
            nperseg = 128  # Window size (adjust for resolution balance)
            noverlap = 96  # High overlap for smooth image
            
            f, t_spec, Sxx = compute_spectrogram(strongest_sig, fs=fs, nperseg=nperseg, noverlap=noverlap)
            
            # Convert Time to ns and Freq to MHz
            t_spec_ns = t_spec * 1e9
            f_mhz = f / 1e6
            
            # Plot
            # Use Gouraud shading for smoothing
            # Use 'plasma' or 'inferno' for perceptual quality
            im = ax_freq.pcolormesh(t_spec_ns, f_mhz, 10 * np.log10(Sxx + 1e-12), cmap='inferno', shading='gouraud')
            
            # Colorbar (optional, might crowd the layout)
            # plt.colorbar(im, ax=ax_freq, label='dB') 
            
            ax_freq.set_title("Time-Frequency Spectrogram")
            ax_freq.set_xlabel("Time [ns]")
            ax_freq.set_ylabel("Frequency [MHz]")
            ax_freq.set_ylim(0, 1200) # GPR Bandwidth
            ax_freq.grid(True, alpha=0.3, linestyle=':')

    def _plot_blueprint(self, ax: matplotlib.axes.Axes) -> None:
        """Draws the geometry blueprint."""
        logger.info("Starting _plot_blueprint...")
        
        # Draw Objects
        data = self.data
        if not data['objects']:
             logger.warning("No objects found in data['objects']!")
             
        sorted_objs = sorted(data['objects'], key=lambda x: x.order)
        logger.info(f"Drawing {len(sorted_objs)} geometry objects.")
        
        # Draw Objects
        for obj in sorted_objs:
            mat = obj.material
            style = STYLES.get(mat, MaterialStyle('#CCCCCC', None, mat))
            obj.draw(ax, style)
                
        # Draw Source/Rx
        if data['source']:
            ax.plot(data['source']['x'], data['source']['y'], 'r^', markersize=12, label='Tx', markeredgecolor='white')
        if data['receiver']:
            rx_x, rx_y = data['receiver']['x'], data['receiver']['y']
            ax.plot(rx_x, rx_y, 'bv', markersize=10, label='Rx', markeredgecolor='white')
            
            # --- SPARKLINE ---
            # If signals exist, draw the strongest one near the Rx
            if self.signals:
                strongest_sig = None
                max_amp = -1
                for sig in self.signals.values():
                    if np.max(np.abs(sig)) > max_amp:
                        max_amp = np.max(np.abs(sig))
                        strongest_sig = sig
                
                if strongest_sig is not None:
                    if self.process_config.enable:
                         strongest_sig, _ = preprocess_signal(strongest_sig, self.dt, 
                                                            use_dewow=self.process_config.dewow)
                                                            
                    self._draw_sparkline(ax, rx_x + 0.15, rx_y, strongest_sig, self.dt, height=0.4)
        
        # --- AXIS BREAKS ---
        self._draw_axis_break(ax, 'top')
        self._draw_axis_break(ax, 'bottom')
        
        # Meta info title
        title_txt = f"{data['title']}"
        if 'scenario' in data['metadata']:
            title_txt += f"\nScenario: {data['metadata']['scenario']}"
        if 'FI_class' in data['metadata']:
             title_txt += f" | FI: {data['metadata'].get('FI_class', '?')}"
             
        ax.set_title(title_txt, fontweight='bold')
        ax.set_xlabel("X Position [m]")
        ax.set_ylabel("Y Position [m]")
        ax.axis('scaled')
        
        # Grid lines
        ax.grid(True, which='major', linestyle='--', linewidth=0.5, alpha=0.5, color='gray')
        ax.minorticks_on()
        ax.grid(True, which='minor', axis='y', linestyle=':', linewidth=0.3, alpha=0.3, color='gray')
        ax.grid(True, which='minor', axis='x', linestyle=':', linewidth=0.3, alpha=0.3, color='gray')
        
        # Draw Domain Limits
        dom = data.get('domain')
        if dom:
             rect = mpatches.Rectangle((0, 0), dom['x'], dom['y'], 
                                       fill=False, edgecolor='black', linewidth=1.5, linestyle='-')
             ax.add_patch(rect)
             
        # --- OVERLAY LEGEND ---
        # --- OVERLAY LEGEND ---
        handles = []
        labels = []
        
        # 1. Source/Rx
        if data['source']:
            # Use Line2D as specific proxy artists
            h = plt.Line2D([0], [0], marker='^', color='w', label='Tx', 
                          markerfacecolor='r', markersize=10, markeredgecolor='white')
            handles.append(h)
        if data['receiver']:
            h = plt.Line2D([0], [0], marker='v', color='w', label='Rx', 
                          markerfacecolor='b', markersize=10, markeredgecolor='white')
            handles.append(h)
            
        # 2. Materials
        seen_mats = set(o.material for o in data['objects'])
        for m in sorted(list(seen_mats)):
            style = STYLES.get(m, MaterialStyle('#999999', None, m))
            patch = mpatches.Patch(facecolor=style.color, edgecolor='black', 
                                   hatch=style.hatch, label=style.label or m)
            handles.append(patch)
            
        if handles:
            print(f"DEBUG: Creating legend with {len(handles)} info items: {[h.get_label() for h in handles]}")
            logger.info(f"Creating legend with {len(handles)} info items: {[h.get_label() for h in handles]}")
            leg = ax.legend(handles=handles, loc='upper right', frameon=True, fontsize='small', title="Legend")
            leg.set_zorder(1000) # Force on top
            leg.get_frame().set_facecolor('white')
            leg.get_frame().set_alpha(1.0)
        else:
            print("DEBUG: No handles found for legend!")
            logger.warning("No handles found for legend!")


    def _create_plot(self) -> None:
        """Generates the full dashboard."""
        logger.info("Generating plot dashboard...")
        
        # Figure Setup
        # Back to standard width since we removed the extra column
        fig = plt.figure(figsize=(18, 10)) 
        
        # 3 Columns:
        # 0: Raw Signals
        # 1: Blueprint (Main) - with Overlay Legend
        # 2: Processed Signals
        gs = gridspec.GridSpec(3, 3, width_ratios=[1, 2, 1])
        
        # --- Column 1: Blueprint ---
        ax_main = fig.add_subplot(gs[:, 1])
        self._plot_blueprint(ax_main)
        
        # --- Column 0: Raw Signals ---
        ax_raw_time = fig.add_subplot(gs[0, 0])
        ax_raw_env = fig.add_subplot(gs[1, 0])
        ax_raw_freq = fig.add_subplot(gs[2, 0])
        
        # --- Column 2: Processed Signals ---
        ax_proc_time = fig.add_subplot(gs[0, 2])
        ax_proc_env = fig.add_subplot(gs[1, 2])
        ax_proc_freq = fig.add_subplot(gs[2, 2])
        
        # Signals content
        if self.signals:
            # 1. Raw
            raw_feats = self._get_feature_text(self.signals)
            self._plot_signal_column(ax_raw_time, ax_raw_env, ax_raw_freq, self.signals, 
                                     "Raw", "Raw Data", raw_feats)
            
            # 2. Processed
            proc_signals = {}
            info_parts = ["TimeZero"] # Always default
            
            cfg = self.process_config
            if cfg.enable:
                if cfg.dewow: info_parts.append("Dewow")
                if cfg.gain_type:
                    info_parts.append(f"Gain:{cfg.gain_type}")
            else:
                info_parts = ["None"]

            if cfg.enable:
                for name, sig in self.signals.items():
                    psig, _ = preprocess_signal(
                        sig, self.dt,
                        use_dewow=cfg.dewow,
                        use_gain=bool(cfg.gain_type),
                        gain_params={'type': cfg.gain_type, 'alpha': cfg.gain_alpha},
                        use_time_zero=True
                    )
                    proc_signals[name] = psig
            else:
                proc_signals = self.signals # Fallback/None
                
            proc_feats = self._get_feature_text(proc_signals)
            self._plot_signal_column(ax_proc_time, ax_proc_env, ax_proc_freq, proc_signals,
                                     "Processed", ", ".join(info_parts), proc_feats)
            
        plt.tight_layout()
        if self.output_file:
            plt.savefig(self.output_file, dpi=150)
            logger.info(f"Saved to {self.output_file}")
            
        if self.show_plot:
            plt.show()

    def _draw_sparkline(self, ax: matplotlib.axes.Axes, x_start: float, y_start: float,
                        signal: np.ndarray, dt: float, height: float = 0.3, width: float = 0.1, 
                        color: str = 'red') -> None:
        """
        Draws a miniature signal trace (sparkline) at the specified location.
        
        Args:
            ax: Axes to draw on.
            x_start, y_start: Origin (top-left) of the sparkline box.
            signal: 1D signal array.
            dt: Time step.
            height: Physical height of the sparkline box in meters.
            width: Physical width of the sparkline box (amplitude excursion).
        """
        # Normalize signal to [-1, 1]
        max_val = np.max(np.abs(signal))
        if max_val == 0: return
        norm_sig = signal / max_val
        
        # Map Time to Y (Depth) -> Downwards
        # Map Amplitude to X -> Centered around x_start
        
        n_samples = len(signal)
        # y goes from y_start down to y_start - height
        y_coords = np.linspace(y_start, y_start - height, n_samples)
        
        # x goes from x_start - width/2 to x_start + width/2
        x_coords = x_start + (norm_sig * (width / 2))
        
        # Draw Line
        ax.plot(x_coords, y_coords, color=color, linewidth=0.8, alpha=0.9)
        
        # Draw Wiggle Fill (Positive Lobes)
        ax.fill_betweenx(y_coords, x_start, x_coords, where=(x_coords > x_start), 
                         color=color, alpha=0.4)
                         
        # Draw Box Frame
        rect = mpatches.Rectangle((x_start - width/2, y_start - height), width, height, 
                                  fill=False, edgecolor='gray', linestyle=':', linewidth=0.5, alpha=0.5)
        ax.add_patch(rect)
        
        # Axis Line
        ax.plot([x_start, x_start], [y_start, y_start - height], color='gray', linewidth=0.5, alpha=0.5)

    def _draw_axis_break(self, ax: matplotlib.axes.Axes, location: str = 'bottom', size: float = 0.015) -> None:
        """
        Draws a double-slash break symbol on the vertical axis spines.
        
        Args:
            ax: The axes to draw on.
            location: 'top' or 'bottom'.
            size: Relative size of the slashes.
        """
        d = size
        # Vertical offset between the two slashes
        gap = d 
        
        kwargs = dict(transform=ax.transAxes, color='black', clip_on=False, linewidth=1)
        
        # Y-position: 0 for bottom, 1 for top
        y_base = 0 if location == 'bottom' else 1
        
        # Direction of slant: / (plus x, plus y)
        # We draw cuts on the left spine (x=0) and right spine (x=1)
        
        # Left Spine (x=0)
        # Cut 1
        ax.plot((-d, d), (y_base - d - gap/2, y_base + d - gap/2), **kwargs)
        # Cut 2
        ax.plot((-d, d), (y_base - d + gap/2, y_base + d + gap/2), **kwargs)
        
        # Right Spine (x=1)
        # Cut 1
        ax.plot((1 - d, 1 + d), (y_base - d - gap/2, y_base + d - gap/2), **kwargs)
        # Cut 2
        ax.plot((1 - d, 1 + d), (y_base - d + gap/2, y_base + d + gap/2), **kwargs)



def main():
    parser = argparse.ArgumentParser(description="Visualize gprMax input geometry and results.")
    parser.add_argument("input_file", help="Path to the .in input file")
    parser.add_argument("-o", "--output", help="Path to save the output image")
    parser.add_argument("--no-show", action="store_true", help="Do not display the window")
    
    # Process Defaults: ON by default
    parser.add_argument("--no-process", action="store_true", help="Disable signal processing")
    parser.add_argument("--no-dewow", action="store_true", help="Disable dewow")
    parser.add_argument("--gain", type=str, choices=['power', 'exp', 'agc'], help="Apply gain")
    parser.add_argument("--alpha", type=float, default=1.0, help="Gain exponent/alpha")
    
    # Filters
    parser.add_argument("--components", nargs='+', default=['Ez'], help="Components to show (Ez, Hx..)")
    parser.add_argument("--rx", nargs='+', help="Receivers to show (rx1, rx2..)")

    args = parser.parse_args()
    
    # Setup Configs
    process_cfg = ProcessingConfig(
        enable=not args.no_process,
        dewow=not args.no_dewow,
        gain_type=args.gain,
        gain_alpha=args.alpha
    )
    
    filter_cfg = FilterConfig(
        components=args.components,
        receivers=args.rx
    )

    viz = GPRResultVisualizer(
        args.input_file, 
        output_file=args.output, 
        show_plot=not args.no_show,
        process_config=process_cfg,
        filter_config=filter_cfg
    )
    viz.run()

if __name__ == "__main__":
    main()

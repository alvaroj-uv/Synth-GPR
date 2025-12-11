import sys
import os
import numpy as np
import matplotlib.pyplot as plt

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

from src.visualization.nodes import (
    FigureNode, GraphNode, AxisNode, TraceNode, RasterNode, TextNode, LineStyle
)
from src.visualization.renderer import MatplotlibRenderer

def create_synthetic_data():
    # 2D B-scan data (random noise + a hyperbolic shape)
    x = np.linspace(0, 10, 100)
    y = np.linspace(0, 20, 200)
    X, Y = np.meshgrid(x, y)
    Z = np.sin(X) * np.exp(-Y/10) + np.random.normal(0, 0.1, size=X.shape)
    
    # 1D Trace data (slice)
    trace_x = np.linspace(0, 10, 100)
    trace_y = np.sin(trace_x)
    
    return Z, trace_x, trace_y

def main():
    print("Building Node Tree...")
    
    # Data
    bscan_data, trace_x, trace_y = create_synthetic_data()
    
    # Build Tree
    figure = FigureNode(title="GPR Analysis (Node Model)", figsize=(12, 6))
    
    # Left Plot: B-scan (Raster)
    ax1 = GraphNode(position=121, title="B-Scan", xlabel="Distance (m)", ylabel="Time (ns)")
    
    raster = RasterNode(
        data=bscan_data, 
        cmap='gray', 
        extent=[0, 10, 20, 0], # Inverted Y for GPR usually
        colorbar_label="Amplitude"
    )
    ax1.add_child(raster)
    
    # Right Plot: A-scan (Trace)
    ax2 = GraphNode(position=122, title="A-Scan (Wiggle)", xlabel="Time (ns)", ylabel="Amplitude")
    
    # Wiggle Trace
    # Note: Wiggles are usually vertical (Time on Y). 
    # Let's plot Time on X for this simple test unless we rotate.
    # Wiggle: Fill positive
    trace = TraceNode(
        x=trace_x, 
        y=trace_y, 
        label="Signal", 
        is_wiggle=True, 
        wiggle_fill_color='red'
    )
    trace.style = LineStyle(color='black', linewidth=0.5)
    ax2.add_child(trace)
    
    # Add GraphNodes to Figure
    figure.add_child(ax1)
    figure.add_child(ax2)
    
    print("Rendering...")
    renderer = MatplotlibRenderer()
    fig = renderer.render(figure)
    
    output_path = "node_model_test.webp"
    print(f"Saving to {output_path}...")
    fig.savefig(output_path)
    print("Done!")

if __name__ == "__main__":
    main()

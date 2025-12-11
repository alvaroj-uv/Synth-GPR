import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from typing import Dict, Any, Optional
import numpy as np

from src.visualization.nodes import (
    Node, FigureNode, GraphNode, AxisNode, TraceNode, RasterNode, TextNode, SpectrogramNode
)

class MatplotlibRenderer:
    """Renders a Node tree using Matplotlib."""
    
    def render(self, node: Node) -> Optional[Any]:
        """Recursive render method."""
        if not node.visible:
            return None

        # Dispatch based on type
        if isinstance(node, FigureNode):
            return self._render_figure(node)
        elif isinstance(node, GraphNode):
            return self._render_graph(node)
        elif isinstance(node, TraceNode):
            return self._render_trace(node)
        elif isinstance(node, RasterNode):
            return self._render_raster(node)
        elif isinstance(node, TextNode):
            return self._render_text(node)
        elif isinstance(node, SpectrogramNode):
            return self._render_spectrogram(node)
        else:
            # For unknown nodes, just visit children
            for child in node.children:
                self.render(child)
            return None

    def _render_figure(self, node: FigureNode):
        fig = plt.figure(figsize=node.figsize, dpi=node.dpi)
        if node.title:
            fig.suptitle(node.title)
        
        # Store figure reference in the node (optional, creates coupling but useful)
        # Instead, we pass the context down or let children use plt.gca() if carefully managed.
        # Better: keep track of axes.
        
        # Simply iterating children. GraphNodes will create subplots.
        for child in node.children:
            self.render(child)
            
        return fig

    def _render_graph(self, node: GraphNode):
        # Determine projection
        kwargs = {}
        if node.projection != 'rectilinear':
            kwargs['projection'] = node.projection
            
        # Add subplot
        # Note: 'position' can be 3-digit int or gridspec, simple int for now
        ax = plt.subplot(node.position, **kwargs)
        
        if node.title:
            ax.set_title(node.title)
        if node.xlabel:
            ax.set_xlabel(node.xlabel)
        if node.ylabel:
            ax.set_ylabel(node.ylabel)
            
        # Handle AxisNode children *before* plotting data to set limits/styles early? 
        # Or after? Matplotlib usually handles auto-scaling.
        # Let's handle them after to override auto-scaling.
        
        # Render data children (Trace, Raster)
        for child in node.children:
            if not isinstance(child, AxisNode):
                self.render(child)
                
        # Render axis configuration
        for child in node.get_children_of_type(AxisNode):
            self._apply_axis_settings(ax, child)
            
        return ax

    def _apply_axis_settings(self, ax, node: AxisNode):
        if node.axis_type == 'x':
            if node.label: ax.set_xlabel(node.label)
            if node.limits: ax.set_xlim(node.limits)
            if node.scale: ax.set_xscale(node.scale)
            if node.invert: ax.invert_xaxis()
        elif node.axis_type == 'y':
            if node.label: ax.set_ylabel(node.label)
            if node.limits: ax.set_ylim(node.limits)
            if node.scale: ax.set_yscale(node.scale)
            if node.invert: ax.invert_yaxis()

    def _render_trace(self, node: TraceNode):
        ax = plt.gca()
        
        if node.is_wiggle:
            self._render_wiggle_trace(ax, node)
        else:
            ax.plot(
                node.x, node.y, 
                label=node.label,
                color=node.style.color,
                linewidth=node.style.linewidth,
                linestyle=node.style.linestyle,
                alpha=node.style.alpha
            )
            
    def _render_wiggle_trace(self, ax, node: TraceNode):
        """Renders variable area wiggle trace."""
        # Typically x is depth/time, y is amplitude? 
        # Or x is offset, y is time?
        # Assuming standard plot x, y.
        # Wiggle usually means filling the positive lobes.
        
        # Apply gain
        y_scaled = node.y * node.wiggle_gain
        
        # Base line
        # If this is part of a multi-trace plot, 'x' might need to be shifted.
        # But TraceNode assumes absolute coordinates.
        
        # Fill positive
        ax.fill_between(
            node.x, 
            node.x, # Base (vertical trace? wiggle usually vertical). 
            # WAIT: Standard wiggle is vertical.
            # If x is time/depth and we plot L-R, wiggle is usually filling "peaks".
            # Let's assume standard Y vs X plot. Fill between y=0 and y=y_scaled.
            # But usually wiggle is offset.
            # The TraceNode has absolute X,Y. So fill between Y_axis_baseline and Y.
            # Actually, usually wiggle plots are: X = Offset + Amplitude, Y = Time.
            # Let's assume the user has set X/Y correctly for the display.
            # Then we fill between the "zero" line of the trace.
            
            # Since we don't know the "zero" line from just X,Y arrays unless we know the offset...
            # We will assume the user provides specific X for the signal.
            # If it's a "wiggle" on a vertical trace (X=amp, Y=depth), we fill against base X.
            # If generic, let's just support filling under the curve.
            
            # Simple implementation: Fill positive lobes
            # We need a baseline. For now, assume baseline is 0 if not specified?
            # Or assume the X array *is* the shape including offset.
            # This is tricky without a "baseline" property.
            # Let's assume for standard Time(y) vs Offset(x) plot:
            # The "Trace" object usually has: center_x, time_y, amplitude.
            # But our TraceNode is generic x,y. 
            # I will just implement standard fill_between for now.
            y_base = np.zeros_like(node.y) # Assuming oscillation around 0? 
            # No, if X is oscillating, we fill X against X_base.
            # If Y is oscillating, we fill Y against Y_base.
             pass 
        )
        
        # Re-thinking Wiggle:
        # If is_wiggle is True, we fill the area between the curve and a baseline.
        # We need to know orientation. 
        # Assuming Y is signal amplitude and X is index/time?
        # Let's assume standard "fill positive Y".
        ax.fill_between(
            node.x, 
            0, # Baseline 0? This might be wrong if trace is offset.
            node.y, 
            where=(node.y > 0), 
            facecolor=node.wiggle_fill_color, 
            interpolate=True
        )
        # Line
        ax.plot(node.x, node.y, color=node.style.color, linewidth=node.style.linewidth)

    def _render_raster(self, node: RasterNode):
        ax = plt.gca()
        
        kwargs = {
            'cmap': node.cmap,
            'interpolation': node.interpolation,
        }
        if node.vmin is not None: kwargs['vmin'] = node.vmin
        if node.vmax is not None: kwargs['vmax'] = node.vmax
        if node.extent: kwargs['extent'] = node.extent
        
        im = ax.imshow(node.data, **kwargs)
        
        if node.colorbar_label:
            plt.colorbar(im, ax=ax, label=node.colorbar_label)
            
    def _render_text(self, node: TextNode):
        ax = plt.gca()
        ax.text(
            node.x, node.y, node.text,
            fontsize=node.fontsize,
            color=node.color,
            rotation=node.rotation
        )
            rotation=node.rotation
        )

    def _render_spectrogram(self, node: SpectrogramNode):
        ax = plt.gca()
        
        # Spectrogram is typically plotted with pcolormesh
        # Sxx is power, usually better in dB
        # 10 * log10(Sxx)
        # But maybe the Node data is already linear power?
        # Let's assume input is linear and we use Db scale in colorbar or logic if requested?
        # For flexibility, render raw data. User should convert to dB if desired or set vmin/vmax.
        
        kwargs = {
            'cmap': node.cmap,
            'shading': 'gouraud'
        }
        if node.vmin is not None: kwargs['vmin'] = node.vmin
        if node.vmax is not None: kwargs['vmax'] = node.vmax
        
        im = ax.pcolormesh(node.t, node.f, node.Sxx, **kwargs)
        
        if node.colorbar_label:
            plt.colorbar(im, ax=ax, label=node.colorbar_label)

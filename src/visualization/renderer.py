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
        """Renders variable area wiggle trace (positive lobes filled)."""
        y_scaled = node.y * node.wiggle_gain
        ax.fill_between(
            node.x, 0, y_scaled,
            where=(y_scaled > 0),
            facecolor=node.wiggle_fill_color,
            interpolate=True,
        )
        ax.plot(node.x, y_scaled, color=node.style.color, linewidth=node.style.linewidth)

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
            rotation=node.rotation,
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

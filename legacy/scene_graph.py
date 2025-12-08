from abc import ABC, abstractmethod
from typing import List, Dict, Any
from dataclasses import dataclass, field

from .config import GeneratorConfig, fmt
from .scene_descriptor import LayerResult
from .gpr_commands import Header

@dataclass
class BuildContext:
    """
    Context passed down through the scene graph during the build process.
    Carries configuration and state (like current Y position).
    """
    config: GeneratorConfig
    current_y: float = 0.0
    # Shared metadata accumulator
    metadata: Dict[str, Any] = field(default_factory=dict)
    # Extra context parameters (pvc, moisture, etc)
    params: Dict[str, Any] = field(default_factory=dict)

    def clone(self) -> 'BuildContext':
        """Create a shallow copy for branching if needed."""
        return BuildContext(
            config=self.config,
            current_y=self.current_y,
            metadata=self.metadata, # Shared reference intentionally? Or copy?
            # Typically metadata is additive, so shared reference is good for accumulation.
            params=self.params.copy()
        )

class SceneNode(ABC):
    """
    Abstract Component in the Composite Pattern.
    Represents any element in the scene (Layer, Group, Object).
    """
    
    def __init__(self, name: str = "Node"):
        self.name = name

    @abstractmethod
    def build(self, ctx: BuildContext) -> LayerResult:
        """
        Build the geometry/commands for this node.
        
        Args:
            ctx: The current build context.
            
        Returns:
            LayerResult containing commands and ANY local Y updates.
        """
        pass

class CompositeNode(SceneNode):
    """
    Composite Component. Holds a list of children and builds them sequentially.
    """
    def __init__(self, name: str = "Composite"):
        super().__init__(name)
        self.children: List[SceneNode] = []

    def add(self, node: SceneNode) -> 'CompositeNode':
        self.children.append(node)
        return self

    def build(self, ctx: BuildContext) -> LayerResult:
        combined_result = LayerResult()
        
        # Optional: Start Marker
        combined_result.geometry.append(Header(f"--- Group: {self.name} Start (Y={fmt(ctx.current_y)}) ---"))

        for child in self.children:
            # Build child
            child_result = child.build(ctx)
            
            # Merge results
            combined_result.geometry.extend(child_result.geometry)
            combined_result.materials.extend(child_result.materials)
            combined_result.sources.extend(child_result.sources)
            combined_result.metadata.update(child_result.metadata)
            
            # Update Context for next child (Sequential Stacking)
            # If child returned a new top_y, use it.
            # If child didn't change Y (e.g. an overlay), top_y might be same as start.
            # We assume layers generally grow upwards.
            if child_result.top_y > ctx.current_y:
                ctx.current_y = child_result.top_y
        
        combined_result.top_y = ctx.current_y
        
        # Optional: End Marker
        combined_result.geometry.append(Header(f"--- Group: {self.name} End (Top={fmt(ctx.current_y)}) ---"))
        
        return combined_result

class LeafLayer(SceneNode):
    """
    Base class for leaf nodes (actual geometry generators).
    Adapts the old Layer pattern to SceneNode.
    """
    def build(self, ctx: BuildContext) -> LayerResult:
        result = LayerResult()
        
        result.geometry.append(Header(f"--- Layer: {self.name} ---"))
        
        # Hook for specific logic
        sub_res = self._generate(ctx)
        
        result.geometry.extend(sub_res.geometry)
        result.materials.extend(sub_res.materials)
        result.sources.extend(sub_res.sources)
        result.metadata.update(sub_res.metadata)
        
        # Update Y
        # If sub_res defined a specific top_y, use it.
        # Otherwise, if it just added geometry without moving the 'cursor', keep ctx.current_y?
        # Most layers calculate a thickness.
        if sub_res.top_y == 0.0 and len(sub_res.geometry) > 0:
             # Safety fallback or overlay?
             pass 
        else:
             result.top_y = sub_res.top_y
             
        result.geometry.append(Header(f"--- End {self.name} (Top: {fmt(result.top_y)}) ---"))
        return result

    @abstractmethod
    def _generate(self, ctx: BuildContext) -> LayerResult:
        pass

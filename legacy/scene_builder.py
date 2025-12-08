from pathlib import Path
from typing import Optional

from .config import GeneratorConfig
from .geometry_composer import (
    ScenePainter,
    BackgroundLayer,
    SubgradeLayer,
    FormationLayer,
    GranularBallastLayer,
    SleeperLayer,
    AntennaLayer
)
from .rock_packing import RockPackingStrategy, PoissonDiskPacking

class SceneBuilder:
    # Builder Pattern implementation for constructing a ScenePainter.
    # 
    # Encapsulates the construction steps of the complex ScenePainter object,
    # separating the construction logic from the representation.
    
    def __init__(self, config: GeneratorConfig, packing_strategy: RockPackingStrategy = None):
        self.config = config
        self.painter = ScenePainter(config)
        # Use Poisson disk by default for realistic, non-overlapping rocks
        self.packing_strategy = packing_strategy or PoissonDiskPacking()
        
    def reset(self) -> None:
        # Resets the builder to start a new scene.
        self.painter = ScenePainter(self.config)
        
    def build_base_layers(self) -> 'SceneBuilder':
        # Adds standard base layers (Background, Subgrade, Formation).
        self.painter.add_layer(BackgroundLayer())
        self.painter.add_layer(SubgradeLayer())
        self.painter.add_layer(FormationLayer())
        return self

    def build_ballast_layer(self, context: dict, granular_fallback: bool = True) -> 'SceneBuilder':
        # Builds the ballast layer based on configuration and context.
        # 
        # Args:
        #     context: Dictionary containing 'pvc', 'moisture', etc.
        #     granular_fallback: Whether to fallback to GranularBallastLayer if MasterPattern is missing.
        pvc = context.get('pvc', 0.0)
        moisture = context.get('moisture', 0.0)
        
        # Consistent logic: use GranularBallastLayer with injected strategy
        if granular_fallback or self.config.granular_mode:
            self.painter.add_layer(
                GranularBallastLayer(None, pvc, moisture, self.packing_strategy)
            )
                
        return self

    def add_sleepers(self) -> 'SceneBuilder':
        """Adds sleepers if configured."""
        if self.config.add_sleepers:
            self.painter.add_layer(SleeperLayer())
        return self
        
    def add_antenna(self) -> 'SceneBuilder':
        """Adds antenna if configured."""
        if self.config.add_source:
             self.painter.add_layer(AntennaLayer())
        return self

    def get_result(self) -> ScenePainter:
        """Returns the fully constructed ScenePainter."""
        return self.painter

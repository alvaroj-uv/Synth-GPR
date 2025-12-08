from .config import GeneratorConfig
from .geometry_composer import ScenePainter
from .scene_builder import SceneBuilder
from .rock_packing import RandomPacking, PoissonDiskPacking, WangTileRockPacking

class ScenarioFactory:
    """
    Factory acting as the Director for the SceneBuilder.
    
    Orchestrates the construction process using the SceneBuilder.
    """
    
    @staticmethod
    def create_painter(config: GeneratorConfig, scenario_type: str, context: dict) -> ScenePainter:
        """
        Creates a ScenePainter using the SceneBuilder.
        
        Args:
            config: The generator configuration.
            scenario_type: The type of scenario (e.g., 'granular').
            context: Dynamic context (pvc, moisture, etc.).
                     
        Returns:
            A fully configured ScenePainter.
        """
        # Select rock packing strategy
        strategy_map = {
            "random": RandomPacking(),
            "poisson": PoissonDiskPacking(k_attempts=30),
            "wang": WangTileRockPacking(tile_size=config.wang_tile_size)
        }
        
        packing_strategy = strategy_map.get(
            config.rock_packing_algorithm,
            WangTileRockPacking(tile_size=config.wang_tile_size)  # Default
        )
        
        builder = SceneBuilder(config, packing_strategy=packing_strategy)
        
        # Director orchestration sequence
        builder.build_base_layers()
        
        # Determine specific strategy adjustments based on scenario_type if needed
        # (Currently aligned with config.granular_mode inside builder, but could be explicit here)
        granular_fallback = (scenario_type == 'granular' or config.granular_mode)
        
        builder.build_ballast_layer(context, granular_fallback=granular_fallback)
        
        builder.add_sleepers()
        builder.add_antenna()
        
        return builder.get_result()

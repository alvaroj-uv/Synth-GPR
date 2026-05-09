"""
RecipeBook: Registry of standard production sequences.

Defines the order of operations (workers) for different product types.
"""
from typing import List
from .worker import Worker
from .workers import (
    AirWorker, SubgradeWorker, FormationWorker, BallastWorker, 
    RockWorker, FoulingWorker
)
from .degradation_worker import DegradationWorker
from .lab_worker import LabWorker

class RecipeBook:
    """
    Catalog of standard production recipes.
    """
    
    @staticmethod
    def get_base_recipe(product_type: str = "standard") -> List[Worker]:
        """
        Get the sequence of workers for the base construction phase.
        
        Args:
            product_type: Identifier for the recipe (e.g., 'standard')
            
        Returns:
            List of Worker instances in execution order.
        """
        # TODO: Dynamic lookup or registry pattern
        if product_type == "standard":
            return [
                AirWorker(),
                SubgradeWorker(),
                FormationWorker(),
                BallastWorker(),
                RockWorker(),
                DegradationWorker(),  # Simulates aging/breakage (optional, controlled by config)
                FoulingWorker()
            ]
        else:
            raise ValueError(f"Unknown recipe: {product_type}")

    @staticmethod
    def get_finalization_recipe() -> List[Worker]:
        """
        Get the sequence of workers for the finalization phase.
        
        These workers run after the base construction is complete and checkpointed.
        They perform final assembly, validation, and analysis.
        
        Returns:
            List of Worker instances in execution order.
        """
        from .workers import AntennaWorker, AssemblerWorker
        return [
            AntennaWorker(),    # Position antennas based on final ballast height
            AssemblerWorker(),  # Final validation and geometry view
            LabWorker()         # Virtual sieve analysis on final clipped geometry
        ]
    
    @staticmethod
    def get_variant_recipe(variant_type: str) -> List[Worker]:
        """
        Get workers for the variant/customization phase.

        Reserved for future multi-variant generation
        (e.g., different antenna offsets, moisture variations, etc.)
        """
        raise NotImplementedError(f"No variant recipe defined for '{variant_type}'")

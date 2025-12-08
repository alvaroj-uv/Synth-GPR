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
                FoulingWorker()
            ]
        else:
            raise ValueError(f"Unknown recipe: {product_type}")

    @staticmethod
    def get_variant_recipe(variant_type: str) -> List[Worker]:
        """Get workers for the variant/customization phase."""
        pass

"""
RecipeBook: Registry of standard production sequences.

Defines the order of operations (workers) for different product types.
"""
from typing import List
from .worker import Worker
from .workers import AirWorker, SubgradeWorker, FormationWorker, BallastWorker
from .lab_worker import LabWorker


class RecipeBook:
    """Catalog of standard production recipes."""

    @staticmethod
    def get_base_recipe(config, product_type: str = "standard") -> List[Worker]:
        """
        Get the worker sequence for the base construction phase.

        All scenes use the standard layer stack; config.rock_packing_algorithm
        only controls how the ballast region is packed (see warehouses.py).
        """
        from .granular_worker import GranularMatrixWorker

        if product_type == "standard":
            return [
                AirWorker(),
                SubgradeWorker(),
                FormationWorker(),
                BallastWorker(),
                GranularMatrixWorker(),
            ]

        raise ValueError(f"Unknown recipe: {product_type}")

    @staticmethod
    def get_finalization_recipe() -> List[Worker]:
        """Worker sequence for finalization: antenna placement, assembly, lab analysis."""
        from .workers import AntennaWorker, AssemblerWorker
        return [
            AntennaWorker(),
            AssemblerWorker(),
            LabWorker(),
        ]

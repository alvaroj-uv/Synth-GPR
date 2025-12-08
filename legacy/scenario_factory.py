"""
ScenarioFactory: Manages the definition of production scenarios and variants.

Decouples the logic of "what variants to produce" from the ProductionLine.
"""
from typing import List, Dict, Any
from .config import GeneratorConfig

class ScenarioFactory:
    """
    Determines the variations and parameters for a production run.
    """
    
    def __init__(self, config: GeneratorConfig):
        self.config = config
        
    def get_variants(self) -> List[Dict[str, Any]]:
        """
        Generate a list of parameter overrides for each variant.
        
        Returns:
            List of dicts, where each dict contains parameters to override
            in the WorkOrder for that variant (e.g., antenna_offset).
        """
        variants = []
        
        # Always include the base case (offset 0)
        variants.append({'antenna_offset': 0.0, 'variant_id': 'base'})
        
        # Check config for additional variants
        # Example: if config.generate_offsets:
        #    variants.append({'antenna_offset': -0.05, 'variant_id': 'left'})
        #    variants.append({'antenna_offset': +0.05, 'variant_id': 'right'})
        
        return variants

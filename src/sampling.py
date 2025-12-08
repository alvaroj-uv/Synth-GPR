"""
ParameterSampler: Handles the stochastic generation of simulation parameters.

Decouples random sampling logic from the main dataset generation pipeline.
"""
import random
from dataclasses import dataclass
from typing import Dict, Any, Tuple

from .config import GeneratorConfig
from .physics import compute_fouling_index, classify_fouling_index, convert_pvc_to_fi, classify_pvc

class ParameterSampler:
    """
    Encapsulates logic for sampling random simulation parameters.
    """
    def __init__(self, config: GeneratorConfig):
        self.config = config
        
    def sample(self) -> Dict[str, Any]:
        """
        Generate a set of random parameters based on configuration.
        """
        cfg = self.config
        
        # Sample ballast thickness
        ballast_thickness = random.uniform(
            cfg.min_ballast_thickness,
            cfg.max_ballast_thickness
        )
        
        # Sample PVC and moisture
        pvc = random.uniform(cfg.pvc_min, cfg.pvc_max) if cfg.granular_mode else 0.0
        moisture = random.uniform(cfg.moisture_min, cfg.moisture_max)
        
        # Calculate Fouling Index (FI)
        if cfg.granular_mode:
            FI = convert_pvc_to_fi(pvc)
            FI_class = classify_fouling_index(FI)
        else:
            rock_h, foul_h = self._sample_heights()
            # If not granular, does ballast_thickness apply?
            # Yes, total thickness.
            FI = compute_fouling_index(rock_h + foul_h, foul_h) # Wait, compute_FI takes (ballast, foul) or (rock, foul)?
            # physics.compute_fouling_index(ballast_thickness, fouling_thickness)
            # Legacy logic sampled total and foul separately.
            FI_class = classify_fouling_index(FI)
            
        return {
            'ballast_thickness': ballast_thickness,
            'pvc': pvc,
            'moisture': moisture,
            'antenna_offset': 0.0,
            'FI': FI,
            'FI_class': FI_class
        }

    def _sample_heights(self) -> Tuple[float, float]:
        """Sample rock and fouling thicknesses for non-granular mode."""
        cfg = self.config
        total = random.uniform(cfg.min_ballast_thickness, cfg.max_ballast_thickness)
        foul = random.uniform(cfg.min_foul_thickness, cfg.max_foul_thickness)
        foul = min(foul, total)
        rock = total - foul
        return rock, foul

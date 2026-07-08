"""
ParameterSampler: Handles the stochastic generation of simulation parameters.

Decouples random sampling logic from the main dataset generation pipeline.
"""
import random
from dataclasses import dataclass
from typing import Dict, Any

from .config import GeneratorConfig
from .physics import classify_fouling_index, convert_pvc_to_fi

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
        moisture = random.uniform(cfg.moisture_min, cfg.moisture_max)
        
        # Sample antenna height (Namdari et al. 2025)
        antenna_clearance = random.uniform(cfg.min_antenna_clearance, cfg.max_antenna_clearance)


        if cfg.stratified_fouling:
            return self._sample_stratified(ballast_thickness, moisture, antenna_clearance)

        pvc = random.uniform(cfg.pvc_min, cfg.pvc_max)
        FI = convert_pvc_to_fi(pvc)
        FI_class = classify_fouling_index(FI)

        return {
            'ballast_thickness': ballast_thickness,
            'pvc': pvc,
            'moisture': moisture,
            'antenna_clearance': antenna_clearance,
            'FI': FI,
            'FI_class': FI_class
        }


    def _sample_stratified(self, ballast_thickness: float, moisture: float, antenna_clearance: float) -> Dict[str, Any]:

        """
        Sample independent PVC values for top and bottom ballast halves.

        Both layers are sampled from the full [pvc_min, pvc_max] range independently.
        The column-level label is derived from the mean FI of the two layers.
        Per-layer FI values are preserved in the returned dict for metadata logging.
        """
        cfg = self.config
        pvc_bottom = random.uniform(cfg.pvc_min, cfg.pvc_max)
        pvc_top    = random.uniform(cfg.pvc_min, cfg.pvc_max)

        FI_bottom = convert_pvc_to_fi(pvc_bottom)
        FI_top    = convert_pvc_to_fi(pvc_top)
        FI        = (FI_bottom + FI_top) / 2.0
        FI_class  = classify_fouling_index(FI)
        pvc_mean  = (pvc_bottom + pvc_top) / 2.0

        return {
            'ballast_thickness': ballast_thickness,
            'pvc':        pvc_mean,
            'pvc_bottom': pvc_bottom,
            'pvc_top':    pvc_top,
            'moisture':   moisture,
            'antenna_clearance': antenna_clearance,
            'FI':         FI,
            'FI_bottom':  FI_bottom,
            'FI_top':     FI_top,
            'FI_class':   FI_class,
        }



"""
Warehouses for managing tools and materials in the Synth-GPR factory.

These components act as central repositories or factories for resources
needed by workers, ensuring consistency and centralizing configuration.
"""
from typing import Dict, Any, Optional
from .gpr_commands import MaterialCommand
from .constants import MC, PC

class MaterialWarehouse:
    """
    Manages GPR materials definition and retrieval.
    
    Responsibilities:
    1. Store standard material definitions (dielectric, conductivity).
    2. Provide mixed materials (e.g., fouled ballast).
    3. Ensure single source of truth for physical properties.
    """
    
    def __init__(self, config: Any):
        self.config = config
        self._materials: Dict[str, MaterialCommand] = {}
        self._initialize_base_materials()
        
    def _initialize_base_materials(self):
        """Register default materials from config."""
        # Universal Constants
        self._materials[MC.AIR] = MaterialCommand(*MC.AIR_PROPS, 1.0, 0.0, MC.AIR)
        
        # Subgrade: dry εr=10, saturated εr=21 (Xie et al. 2010)
        sub_eps = (MC.SUBGRADE_EPS_SAT if getattr(self.config, 'subgrade_wet', False)
                   else MC.SUBGRADE_PROPS[0])
        self._materials[MC.SUBGRADE] = MaterialCommand(
            sub_eps,
            MC.SUBGRADE_PROPS[1],
            1.0, 0.0,
            MC.SUBGRADE
        )
        
        # Formation
        self._materials[MC.FORMATION] = MaterialCommand(
            *MC.FORMATION_PROPS, 1.0, 0.0,
            MC.FORMATION
        )
        
        # Clean Ballast Rock
        self._materials[MC.BALLAST_ROCK] = MaterialCommand(
            self.config.bal_rock_eps,
            self.config.bal_rock_sigma,
            1.0, 0.0,
            MC.BALLAST_ROCK
        )
        
        # Fouling (Clay/Soil) - Base
        self._materials['fouling_base'] = MaterialCommand(
            self.config.bal_foul_eps_min,
            self.config.bal_foul_sigma_min,
            1.0, 0.0,
            "fouling_base"
        )

        # Dense fouling placeholder (actual value computed moisture-dependently at runtime)
        self._materials[MC.FOULING_DENSE] = MaterialCommand(
            self.config.bal_foul_eps_max,
            self.config.bal_foul_sigma_max if hasattr(self.config, 'bal_foul_sigma_max') else 0.05,
            1.0, 0.0,
            MC.FOULING_DENSE
        )

    def get_material(self, name: str, **kwargs) -> Optional[MaterialCommand]:
        """Retrieve a material definition by name."""
        if name == MC.FOULING and "moisture" in kwargs:
            return self.get_fouled_material(kwargs["moisture"])
        if name == MC.FOULING_DENSE and "moisture" in kwargs:
            return self.get_fouled_dense_material(kwargs["moisture"])
        return self._materials.get(name)
    
    def get_fouled_material(self, moisture: float, pvc: float = 0.0) -> MaterialCommand:
        """Granular dispersed fouling (zones 2-3): CRIM three-phase mix.

        εr derived from mineral grains + pore water + pore air using the
        Complex Refractive Index Method (Bruggeman 1935; Barrett et al. 2019).
        PVC boosts pore-space saturation via capillary retention.
        """
        from .physics import crim_fouling_eps
        eps, sigma = crim_fouling_eps(
            moisture, pvc, zone='granular',
            eps_mineral=getattr(self.config, 'fouling_mineral_eps', 5.5),
        )
        return MaterialCommand(eps, sigma, 1.0, 0.0, MC.FOULING)

    def get_fouled_dense_material(self, moisture: float, pvc: float = 0.0) -> MaterialCommand:
        """Dense settled fouling (zone 1): CRIM with compacted-fines porosity (φ=0.32)."""
        from .physics import crim_fouling_eps
        eps, sigma = crim_fouling_eps(
            moisture, pvc, zone='dense',
            eps_mineral=getattr(self.config, 'fouling_mineral_eps', 5.5),
        )
        return MaterialCommand(eps, sigma, 1.0, 0.0, MC.FOULING_DENSE)

    def mix_material(self, base_name: str, additive_name: str, fraction: float) -> MaterialCommand:
        """
        Create a new material by mixing two others (typically CRIM/Topp).
        
        Simplified Mixing (Linear Volumetric):
        e_mix = e_base * (1-f) + e_add * f
        s_mix = s_base * (1-f) + s_add * f
        """
        base = self.get_material(base_name)
        add = self.get_material(additive_name)
        
        if not base or not add:
            raise ValueError(f"Cannot mix unknown materials: {base_name}, {additive_name}")
            
        new_name = f"{base_name}_{int(fraction*100)}_{additive_name}"
        
        new_eps = base.eps * (1 - fraction) + add.eps * fraction
        new_sigma = base.sigma * (1 - fraction) + add.sigma * fraction
        
        return MaterialCommand(new_eps, new_sigma, 1.0, 0.0, new_name)

class ToolWarehouse:
    """
    Manages tools and algorithms used by workers.
    
    Responsibilities:
    1. Provide instances of algorithms (e.g., RockPackingStrategy).
    2. Manage tool configuration.
    """
    
    def __init__(self, config: Any):
        self.config = config
        self._tools: Dict[str, Any] = {}
        
    def get_tool(self, tool_name: str) -> Any:
        """Retrieve a specialized tool."""
        if tool_name not in self._tools:
            self._tools[tool_name] = self._create_tool(tool_name)
        return self._tools[tool_name]
        
    def _create_tool(self, name: str) -> Any:
        """Factory method for tools."""
        if name == "rock_packer":
            # Select strategy based on config
            algo = self.config.rock_packing_algorithm
            
            if algo == "wang":
                from .rock_packing import WangTileRockPacking
                return WangTileRockPacking(tile_size=self.config.wang_tile_size)
            elif algo == "poisson":
                from .rock_packing import PoissonDiskPacking
                return PoissonDiskPacking()
            elif algo == "front_chain":
                from .rock_packing import FrontChainPacking
                return FrontChainPacking()
            elif algo == "physics":
                from .rock_packing import PhysicsPacking
                return PhysicsPacking()
            elif algo == "triangle":
                from .rock_packing import TrianglePacking
                return TrianglePacking()
            elif algo == "circlify":
                from .rock_packing import CirclifyPacking
                return CirclifyPacking()
            elif algo == "growth":
                from .rock_packing import GrowthPacking
                return GrowthPacking(place_attempts=500, grow_step=0.001)
            elif algo == "shang_chu":
                from .rock_packing import ShangChuPacking
                return ShangChuPacking()
            elif algo == "hybris_shang":
                from .rock_packing import HybridShangPacking
                return HybridShangPacking()
            elif algo == "strip":
                from .rock_packing import StripPackingStrategy
                # Use 5m × 3.2m strip: yields 2 domains in ~20s (vs 32s individual)
                return StripPackingStrategy(strip_width=5.0, strip_height=3.2,
                                          base_strategy="hybris_shang")
            elif algo == "rsa":
                from .rock_packing import RSAPacking
                return RSAPacking()
            elif algo == "pymunk":
                try:
                    from .rock_packing import PymunkBallastPacking
                    return PymunkBallastPacking()
                except ImportError:
                    raise ImportError(
                        "pymunk packing requires 'pymunk' package. "
                        "Install with: pip install pymunk"
                    )
            elif algo == "mbubia_ballast":
                # Dense mbubia physics packing confined to the ballast region,
                # for use inside the STANDARD layer stack (Air/Subgrade/Formation/
                # Fouling). Returns full-grading polygon rocks; GranularMatrixWorker
                # keeps ALL of them (no size filter, no fill cap) for a dense,
                # settled ballast skeleton. clean_ballast grading gives the rock
                # skeleton (fouling is added separately as a layer).
                try:
                    from .pymunk_packing import MbubiaPymunkSceneGenerator
                    return MbubiaPymunkSceneGenerator(
                        scene_name="ballast_pack",
                        upper_material="clean_ballast",
                        verbose=False,
                    )
                except ImportError:
                    raise ImportError(
                        "mbubia_ballast packing requires 'pymunk' package. "
                        "Install with: pip install pymunk"
                    )
            else:
                from .rock_packing import RSAPacking
                return RSAPacking()

        raise ValueError(f"Unknown tool requested: {name}")

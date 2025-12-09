"""
Warehouses for managing tools and materials in the Synth-GPR factory.

These components act as central repositories or factories for resources
needed by workers, ensuring consistency and centralizing configuration.
"""
from typing import Dict, Any, Optional
from .gpr_commands import MaterialCommand

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
        self._materials['free_space'] = MaterialCommand(1.0, 0.0, 1.0, 0.0, "free_space")
        
        # Subgrade
        # TODO: Get from Config if available, else standard
        self._materials['subgrade'] = MaterialCommand(
            self.config.bal_foul_eps_max, # Approximation
            0.02, # Approximation
            1.0, 0.0,
            "subgrade" 
        )
        
        # Formation
        self._materials['formation'] = MaterialCommand(
            10.0, 0.03, 1.0, 0.0,
            "formation"
        )
        
        # Clean Ballast Rock
        self._materials['bal_rock'] = MaterialCommand(
            self.config.bal_rock_eps,
            self.config.bal_rock_sigma,
            1.0, 0.0,
            "bal_rock"
        )
        
        # Fouling (Clay/Soil) - Base
        # We use minimum fouling props as base
        self._materials['fouling_base'] = MaterialCommand(
            self.config.bal_foul_eps_min,
            self.config.bal_foul_sigma_min,
            1.0, 0.0,
            "fouling_base"
        )

    def get_material(self, name: str, **kwargs) -> Optional[MaterialCommand]:
        """Retrieve a material definition by name."""
        # Dynamic handling for moisture-dependent fouling
        if name == "bal_foul_granular" and "moisture" in kwargs:
            return self.get_fouled_material(kwargs["moisture"])
            
        return self._materials.get(name)
    
    def get_fouled_material(self, moisture: float) -> MaterialCommand:
        """
        Generate fouled ballast material with moisture-dependent properties.
        
        Args:
            moisture: Volumetric water content (0.0 - 1.0)
            
        Returns:
            MaterialCommand for fouled ballast with computed dielectric properties
        """
        from .physics import topp_mixing_model
        
        # Compute dielectric properties based on moisture
        foul_eps = topp_mixing_model(moisture)
        foul_sigma = 0.001 + 0.2 * moisture
        
        return MaterialCommand(foul_eps, foul_sigma, 1.0, 0.0, "bal_foul_granular")

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
            else:
                from .rock_packing import RandomPacking
                return RandomPacking()
        

             
        raise ValueError(f"Unknown tool requested: {name}")

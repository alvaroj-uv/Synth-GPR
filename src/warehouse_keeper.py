"""
Warehouse Keeper - Intermediary between Workers and Warehouses.

Implements the Facade pattern to provide a clean interface for workers
to request materials and tools without directly accessing warehouses.
"""
from .gpr_commands import MaterialCommand
from .warehouses import MaterialWarehouse, ToolWarehouse


class WarehouseKeeper:
    """
    Intermediary that handles material and tool requests from workers.
    
    Workers call the keeper, keeper goes to warehouse, returns resource.
    This decouples workers from warehouse implementation details.
    """
    
    def __init__(self, material_warehouse: MaterialWarehouse, tool_warehouse: ToolWarehouse):
        """
        Initialize keeper with warehouse references.
        
        Args:
            material_warehouse: MaterialWarehouse instance
            tool_warehouse: ToolWarehouse instance
        """
        self.materials = material_warehouse
        self.tools = tool_warehouse
    
    def get_material(self, material_name: str, **kwargs) -> MaterialCommand:
        """
        Request a material from the warehouse.
        """
        if material_name == "bal_foul_granular" and "moisture" in kwargs:
            # Dynamic material - keeper handles complexity
            return self.materials.get_fouled_material(kwargs["moisture"])
        else:
            # Standard material
            return self.materials.get_material(material_name)
    
    def get_tool(self, tool_name: str):
        """
        Request a tool from the warehouse.
        """
        return self.tools.get_tool(tool_name)


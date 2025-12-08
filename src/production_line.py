import os
import dataclasses
from typing import List, Dict, Any, Optional
from .config import GeneratorConfig
from .work_order import WorkOrderSystem
from .worker import SceneCheckpoint
from .workers import (
    AntennaWorker, AssemblerWorker
)
from .recipes import RecipeBook
from .file_writer import GPRMaxFileWriter
from .warehouses import MaterialWarehouse, ToolWarehouse

class ProductionLine:
    """
    Orchestrates the factory floor to build railway ballast geometry.
    
    Layer Structure (bottom → top):
    - Subgrade: base soil layer (0-0.5m)
    - Formation (Subballast): transition layer (0.5-0.6m, ~100mm)
    - Ballast: crushed rock layer (0.6-1.0m, 250-500mm)
      └─ Rocks: individual particles (cylinders)
      └─ Fouling: fine material filling voids (PVC-controlled)
    - Air: free space above
    
    Responsibilities:
    1. Instantiates the SceneCheckpoint.
    2. Runs Base Workers (Construction Phase) - builds layers bottom-up.
    3. Manages Checkpointing.
    4. Runs Variant Workers (Customization Phase).
    5. Runs Assembler (Finalization Phase).
    6. Writes Output Files - includes FI_class in headers.
    """
    
    def __init__(self, config: GeneratorConfig):
        """
        Initialize ProductionLine with configuration.
        
        Args:
            config: Generator configuration containing all simulation parameters
        """
        self.config = config
        self.material_warehouse = MaterialWarehouse(config)
        self.tool_warehouse = ToolWarehouse(config)
        
        # Create Warehouse Keeper (facade for workers)
        from .warehouse_keeper import WarehouseKeeper
        self.keeper = WarehouseKeeper(self.material_warehouse, self.tool_warehouse)
        
    def run(self, work_order: WorkOrderSystem, output_dir: str) -> List[str]:
        """
        Execute the full production line for a given WorkOrder.
        """
        generated_files = []
        work_order.log("Production Line Started", "System")
        
        # 1. Base Sequence
        # ----------------
        scene = SceneCheckpoint(config=self.config, work_order=work_order)
        
        # Define Base Recipe (could be injected)
        base_workers = RecipeBook.get_base_recipe("standard")
        
        # Execute Base Workers
        for worker in base_workers:
            self._execute_worker(worker, scene, self.keeper)
            if self._has_critical_errors(work_order):
                work_order.log("Aborting due to critical errors in Base Phase", "System")
                return []
            
        # 2. Checkpoint
        # -------------
        checkpoint = scene.clone()
        work_order.log("Base Checkpoint Created", "System")
        
        # 3. Variant Generation
        # ---------------------
        # Single variant for now (can extend later)
        variants = [{'antenna_offset': 0.0}]
        
        for var_idx, var_params in enumerate(variants):
             # Clone from checkpoint
             var_scene = checkpoint.clone()
             
             # Apply Variant Params to WorkOrder
             # Note: This updates the shared blackboard state sequentially.
             offset = var_params.get('antenna_offset', 0.0)
             work_order.set('antenna_offset', offset, "System")
             work_order.log(f"Starting Variant {var_idx} (Offset={offset})", "System")
             
             # Run Antenna Worker (Variant Specific)
             self._execute_worker(AntennaWorker(), var_scene, self.keeper)
             
             # Run Assembler (Finalizer)
             assembler = AssemblerWorker()
             self._execute_worker(assembler, var_scene, self.keeper)
             
             # 4. Write Output
             # ---------------
             if var_scene.assembled and not self._has_critical_errors(work_order):
                 # Generate filename
                 suffix = f"_var{var_idx}" if len(variants) > 1 else ""
                 filename = f"{work_order.work_order.id}{suffix}.in"
                 path = os.path.join(output_dir, filename)
                 
                 try:
                     # Build extra headers
                     extra_headers = {
                         "Variant": var_idx,
                         "Offset": offset
                     }
                     
                     # Create SceneDefinition from SceneCheckpoint
                     from .scene_descriptor import SceneDefinition
                     scene_def = SceneDefinition(
                         config=var_scene.config,
                         domain_commands=[var_scene.domain_cmd, var_scene.dx_dy_dz_cmd, var_scene.time_window_cmd],
                         material_commands=var_scene.materials,
                         geometry_commands=var_scene.geometry,
                         source_commands=var_scene.sources,
                         metadata=var_scene.metadata
                     )
                     
                     content = GPRMaxFileWriter.write_scene(
                         scene_def, 
                         scenario_type="Sim",
                         extra_headers=extra_headers
                     )
                     
                     # Ensure output directory exists
                     os.makedirs(output_dir, exist_ok=True)
                     
                     with open(path, 'w') as f:
                         f.write(content)
                         
                     generated_files.append(path)
                     work_order.log(f"Generated {filename}", "System")
                     
                 except Exception as e:
                     work_order.log_issue("System", "critical", "high", f"Write Failed: {e}")
             else:
                 work_order.log_issue("System", "error", "high", f"Variant {var_idx} failed assembly or qc")
                 
        return generated_files

    def _execute_worker(self, worker, scene, params):
        """Helper to run a worker and handle logs."""
        try:
            worker.execute(scene, {}, params, params)  # params is actually keeper
            errors = worker.quality_check(scene)
            for err in errors:
                # QC failures are errors but maybe not critical unless they break assumptions?
                # We log them.
                scene.log_issue(worker.name, "error", "high", err)
        except Exception as e:
            import traceback
            trace = traceback.format_exc()
            scene.log_issue(worker.name, "critical", "high", f"Crash: {str(e)}\n{trace}")
            
    def _has_critical_errors(self, work_order: WorkOrderSystem) -> bool:
        """Check if any critical issues were logged recently."""
        # This is a bit simplistic. In a real system we'd check the issue list.
        # But WorkOrderSystem.export_issues() returns a list.
        issues = work_order.export_issues()
        return any(i['severity'] == 'critical' for i in issues)

import os
from typing import List
from .config import GeneratorConfig
from .work_order import WorkOrderSystem
from .worker import SceneCheckpoint
from .recipes import RecipeBook
from .warehouses import MaterialWarehouse, ToolWarehouse
from .domain.coordinates import CoordinateSystem, LayerStack

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
        
    def run(self, work_order_system: WorkOrderSystem) -> SceneCheckpoint:
        """
        Execute the full production line for a given WorkOrder.
        
        Returns the finalized SceneCheckpoint. The caller is responsible
        for persistence (file, database, memory, etc.).
        
        Architecture:
        1. Base Phase: Build layers (Air → Subgrade → Formation → Ballast → Rocks → Degradation → Fouling)
        2. Checkpoint: Save state for potential variants
        3. Finalization Phase: Antenna → Assembler → LabWorker
        4. Return: Finalized scene (caller handles persistence)
        
        Returns:
            Finalized SceneCheckpoint ready for persistence
            
        Raises:
            RuntimeError: If critical errors occur during production
        """
        if work_order_system:
            work_order_system.log("Production Line Started", "System")
        
        # ========================================================================
        # PHASE 1: Base Construction
        # ========================================================================
        # Initialize Coordinate System
        ballast_thickness_val = self.config.max_ballast_thickness
        if work_order_system:
            ballast_thickness_val = work_order_system.work_order.get('ballast_thickness', ballast_thickness_val)

        layer_stack = LayerStack(
            subgrade_thickness=self.config.subgrade_thickness,
            formation_thickness=self.config.formation_thickness,
            ballast_thickness=ballast_thickness_val,
            antenna_clearance=self.config.antenna_clearance_above_ballast
        )
        coords = CoordinateSystem(
            layer_stack=layer_stack,
            domain_x=self.config.domain_x,
            domain_z=self.config.domain_z
        )
            
        # Create initial scene state
        scene = SceneCheckpoint(
            config=self.config,
            work_order=work_order_system,
            coordinate_system=coords
        )
        
        base_workers = RecipeBook.get_base_recipe("standard")
        
        for worker in base_workers:
            self._execute_worker(worker, scene, self.keeper)
            if self._has_critical_errors(work_order_system):
                if work_order_system:
                    work_order_system.log("Aborting due to critical errors in Base Phase", "System")
                raise RuntimeError("Production line failed in Base Phase")
        
        # ========================================================================
        # PHASE 2: Checkpoint (for future variant support)
        # ========================================================================
        checkpoint = scene.clone()
        if work_order_system:
            work_order_system.log("Base Checkpoint Created", "System")
        
        # ========================================================================
        # PHASE 3: Finalization
        # ========================================================================
        finalization_workers = RecipeBook.get_finalization_recipe()
        
        for worker in finalization_workers:
            self._execute_worker(worker, checkpoint, self.keeper)
            if self._has_critical_errors(work_order_system):
                if work_order_system:
                    work_order_system.log("Aborting due to critical errors in Finalization Phase", "System")
                raise RuntimeError("Production line failed in Finalization Phase")
        
        # ========================================================================
        # PHASE 4: Validation & Statistics
        # ========================================================================
        if not checkpoint.assembled:
            if work_order_system:
                work_order_system.log_issue("System", "error", "high", "Scene failed assembly")
            raise RuntimeError("Scene failed assembly validation")
        
        if self._has_critical_errors(work_order_system):
            if work_order_system:
                work_order_system.log_issue("System", "error", "high", "Scene has critical errors")
            raise RuntimeError("Scene has critical quality check errors")
        
        # Run comprehensive validation
        validation_errors = checkpoint.validate_all()
        if validation_errors and work_order_system:
            work_order_system.log("=== Scene Validation ===", "System")
            for err in validation_errors:
                # Log as warnings (non-critical) since scene assembled successfully
                work_order_system.log(f"  [VALIDATION] {err}", "System")
        
        # Log component statistics for analysis
        if work_order_system:
            work_order_system.log("=== Scene Statistics ===", "System")
            work_order_system.log(f"  Materials: {len(checkpoint.materials)}", "System")
            work_order_system.log(f"  Geometry Commands: {len(checkpoint.geometry)}", "System")
            work_order_system.log(f"  Rocks: {checkpoint._rock_collection.count}", "System")
            physical_sources = [s for s in checkpoint.sources if not s.__class__.__name__.startswith('Waveform')]
            work_order_system.log(f"  Sources: {len(physical_sources)}", "System")
            work_order_system.log(f"  Receivers: {len(checkpoint.receivers)}", "System")
            work_order_system.log(f"  Antennas Configured: {checkpoint._antenna_config.is_configured}", "System")
            
            # Domain info
            if checkpoint.domain_settings:
                x, y, z = checkpoint.domain_settings.get_domain_dimensions()
                dx, dy, dz = checkpoint.domain_settings.get_discretization()
                work_order_system.log(f"  Domain: {x:.2f}×{y:.2f}×{z:.2f}m", "System")
                work_order_system.log(f"  Resolution: {dx:.4f}×{dy:.4f}×{dz:.4f}m", "System")
        
        if work_order_system:
            work_order_system.log("Production Line Completed", "System")
        return checkpoint

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
            # Capture full context
            sample_id = "UNKNOWN"
            if scene.work_order:
                sample_id = scene.work_order.work_order.id
                
            trace = traceback.format_exc()
            
            # 1. Log to internal system (if available)
            scene.log_issue(worker.name, "critical", "high", f"Crash: {str(e)}\n{trace}")
            
            # 2. Force dump to console/stderr for immediate visibility
            # Use a distinctive banner
            msg = (
                f"\n{'!'*60}\n"
                f"[CRITICAL WORKER FAILURE]\n"
                f"Worker: {worker.name}\n"
                f"Sample ID: {sample_id}\n"
                f"Error: {str(e)}\n"
                f"{'-'*60}\n"
                f"{trace}\n"
                f"{'!'*60}\n"
            )
            sys.stderr.write(msg)
            sys.stderr.flush()
            
    def _has_critical_errors(self, work_order: WorkOrderSystem) -> bool:
        """Check if any critical issues were logged recently."""
        # This is a bit simplistic. In a real system we'd check the issue list.
        # But WorkOrderSystem.export_issues() returns a list.
        issues = work_order.export_issues()
        return any(i['severity'] == 'critical' for i in issues)

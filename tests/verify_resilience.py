
import sys
import unittest
from pathlib import Path

sys.path.append(str(Path("d:/Codigo/Synth-GPR")))

from src.worker import SceneCheckpoint
from src.workers import RockWorker
from src.config import GeneratorConfig
from src.work_order import WorkOrderSystem, WorkOrder
from src.warehouses import MaterialWarehouse
from src.rock_packing import RockPackingStrategy, PackingBounds, Rock
from src.physics import classify_pvc

class BrokenStrategy(RockPackingStrategy):
    """Mocks a strategy that always fails (returns empty list)."""
    def generate_rocks(self, *args, **kwargs):
        # Simulate catastrophic failure or timeout
        return []

class TestResilience(unittest.TestCase):
    def setUp(self):
        self.config = GeneratorConfig()
        self.materials = MaterialWarehouse(self.config)

    def test_grid_fallback(self):
        print("\n--- Testing RockWorker Resilience ---")
        
        # 1. Setup Scene
        system = WorkOrderSystem(WorkOrder(id="resilience_test"))
        # Must provide bounds so RockWorker runs
        system.set('ballast_bottom_y', 0.5, 'TestSetup')
        system.set('ballast_top_y', 0.9, 'TestSetup')
        
        scene = SceneCheckpoint(config=self.config, work_order=system, materials=[])

        # 2. Inject Broken Strategy
        broken_strat = BrokenStrategy()
        params = {'packing_strategy': broken_strat}
        
        # 3. Execute RockWorker
        print("Executing RockWorker with BrokenStrategy (expecting fallback)...")
        worker = RockWorker()
        worker.execute(scene, params, self.materials, None)
        
        # 4. Verify Geometry Created (proving fallback worked)
        rock_geometry = [c for c in scene.geometry if getattr(c, 'material', '') == 'bal_rock']
        rock_count = len(rock_geometry)
        
        print(f"Rocks generated via fallback: {rock_count}")
        self.assertTrue(rock_count > 0, "Fallback failed to produce any rocks!")
        
        # 5. Verify Metadata (proving we switched)
        print("Strategy used:", scene.metadata.get('packing_strategy'))
        self.assertEqual(scene.metadata.get('packing_strategy'), "GridPacking")
        
        # 6. Verify FI Class logic (Regression check for FoulingWorker)
        # Manually invoke FoulingWorker to check metadata registration
        from src.workers import FoulingWorker
        
        # Create NEW system with PVC input (since get_input reads immutable params)
        new_wo = WorkOrder(id="resilience_test_fouling", params={'pvc': 35.0})
        system = WorkOrderSystem(new_wo)
        # Re-inject blackboard values needed
        system.set('ballast_bottom_y', 0.5, 'TestSetup')
        system.set('ballast_top_y', 0.9, 'TestSetup')
        system.set('ballast_thickness', 0.4, 'TestSetup')
        
        # Update scene to use new work order
        scene = SceneCheckpoint(config=self.config, work_order=system, materials=[]) # Fresh scene
        scene.rock_positions = [] # No rocks needed for metadata check, or mock them if needed
        # actually FoulingWorker needs rock_positions for dispersed phase, but settled phase runs anyway?
        
        f_worker = FoulingWorker()
        f_worker.execute(scene, {}, self.materials, None)
        
        fi_class = scene.metadata.get('fi_class')
        print(f"FI Class Registered: {fi_class}")
        self.assertEqual(fi_class, "F", "FoulingWorker failed to register correct FI class (expected 'F' for 35% PVC)")

if __name__ == '__main__':
    unittest.main()

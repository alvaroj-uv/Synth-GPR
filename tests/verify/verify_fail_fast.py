
import sys
import unittest
from pathlib import Path

sys.path.append(str(Path("d:/Codigo/Synth-GPR")))

from src.work_order import WorkOrder
from src.workers import RockWorker
from src.worker import SceneCheckpoint
from src.config import GeneratorConfig
from src.work_order import WorkOrderSystem
from src.warehouses import MaterialWarehouse

class TestFailFast(unittest.TestCase):
    def setUp(self):
        self.config = GeneratorConfig()
        self.materials = MaterialWarehouse(self.config)

    def test_workorder_validation(self):
        print("\n--- Testing WorkOrder Validation ---")
        
        # 1. Negative Dimension
        with self.assertRaises(ValueError) as cm:
            wo = WorkOrder(id="bad_dim", params={'domain_x': -1.0})
            wo.validate()
        print(f"Caught expected error: {cm.exception}")
        self.assertIn("domain_x", str(cm.exception))
        self.assertIn("positive", str(cm.exception))
        
        # 2. Invalid PVC
        with self.assertRaises(ValueError) as cm:
            wo = WorkOrder(id="bad_pvc", params={'pvc': 150})
            wo.validate()
        print(f"Caught expected error: {cm.exception}")
        self.assertIn("PVC", str(cm.exception))
        self.assertIn("0-100", str(cm.exception))
        
    def test_rockworker_preflight(self):
        print("\n--- Testing RockWorker Pre-flight ---")
        
        # Scenario: Ballast Layer is 0.01m (1cm)
        # Rock Radius Min is 0.02m (2cm)
        # Should fail fast
        
        system = WorkOrderSystem(WorkOrder(id="thin_ballast"))
        scene = SceneCheckpoint(config=self.config, work_order=system, materials=[])
        
        # Mock inputs
        system.set('ballast_bottom_y', 0.5, 'BallastWorker')
        system.set('ballast_top_y', 0.51, 'BallastWorker') # Thickness = 0.01m
        
        print(f"Ballast Thickness: 0.01m, Min Rock Diameter: {self.config.rock_radius_min * 2}m")
        
        with self.assertRaises(ValueError) as cm:
            RockWorker().execute(scene, {}, self.materials, None)
            
        print(f"Caught expected error: {cm.exception}")
        self.assertIn("Ballast thickness", str(cm.exception))
        self.assertIn("less than minimum rock diameter", str(cm.exception))

if __name__ == '__main__':
    unittest.main()

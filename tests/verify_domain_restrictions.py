
import sys
import unittest
from pathlib import Path

sys.path.append(str(Path("d:/Codigo/Synth-GPR")))

from src.workers import BallastWorker, AntennaWorker, FormationWorker
from src.worker import SceneCheckpoint
from src.config import GeneratorConfig
from src.work_order import WorkOrderSystem, WorkOrder
from src.warehouses import MaterialWarehouse

class TestDomainRestrictions(unittest.TestCase):
    def setUp(self):
        self.config = GeneratorConfig()
        self.materials = MaterialWarehouse(self.config)
        
    def test_ballast_clamping(self):
        print("\n--- Testing Ballast Clamping ---")
        # Define small domain height (1.0m)
        domain_y = 1.0
        # Define Stack that WOULD equal 1.2m
        # Subgrade(0.5) + Formation(0.1) + Ballast(0.6) = 1.2m
        # Ballast should be clamped to fill only up to 1.0m (thickness -> 0.4)
        
        params = {
            'domain_y': domain_y,
            'subgrade_height': 0.5,
            'formation_thickness': 0.1,
            'ballast_thickness': 0.6  # EXCESSIVE
        }
        order = WorkOrder(id="clamp_test", params=params)
        system = WorkOrderSystem(order)
        
        scene = SceneCheckpoint(config=self.config, work_order=system, materials=[])
        
        # Mock Previous Layers outputs
        system.set('subgrade_top_y', 0.5, 'SubgradeWorker')
        system.set('formation_top_y', 0.6, 'FormationWorker')
        
        # Execute BallastWorker
        BallastWorker().execute(scene, {}, self.materials, None)
        
        # Verify Clamping
        actual_top = system.get('ballast_top_y')
        actual_thickness = system.get('ballast_thickness')
        
        print(f"Goal Domain Y: {domain_y}")
        print(f"Actual Ballast Top: {actual_top}")
        print(f"Actual Ballast Thickness: {actual_thickness}")
        
        self.assertAlmostEqual(actual_top, domain_y, msg="Ballast top was not clamped to domain_y")
        self.assertAlmostEqual(actual_thickness, 0.4, msg="Ballast thickness was not adjusted")
        
    def test_antenna_restriction(self):
        print("\n--- Testing Antenna Restriction ---")
        # Domain X = 0.5
        params = {
            'domain_x': 0.5,
            'antenna_offset': 0.3 # Default Tx is 0.3. +0.3 = 0.6. Outside!
        }
        order = WorkOrder(id="restrict_test", params=params)
        system = WorkOrderSystem(order)
        
        scene = SceneCheckpoint(config=self.config, work_order=system, materials=[])
        
        # Mock highest rock
        system.set('highest_rock_y', 0.5, 'RockWorker')
        
        # Execute AntennaWorker - Should Raise ValueError
        print("Checking for ValueError on excessive offset...")
        with self.assertRaises(ValueError) as cm:
            AntennaWorker().execute(scene, {}, self.materials, None)
            
        print(f"Caught expected error: {cm.exception}")
        self.assertIn("TX X", str(cm.exception))
        self.assertIn("outside domain", str(cm.exception))

if __name__ == '__main__':
    unittest.main()

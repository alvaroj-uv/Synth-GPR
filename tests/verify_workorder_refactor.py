
import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock

# Add src to path
sys.path.append(str(Path("d:/Codigo/Synth-GPR")))

from src.workers import AirWorker, SubgradeWorker, FormationWorker, BallastWorker, RockWorker, AntennaWorker, AssemblerWorker
from src.worker import SceneCheckpoint
from src.config import GeneratorConfig
from src.work_order import WorkOrderSystem, WorkOrder
from src.warehouses import MaterialWarehouse

class TestWorkerRefactor(unittest.TestCase):
    def setUp(self):
        self.config = GeneratorConfig() # Default config
        self.materials = MaterialWarehouse(self.config)
        # Note: MaterialWarehouse needs config
        
    def test_subgrade_workorder_authority(self):
        print("\n--- Testing SubgradeWorker Authority ---")
        # Initialize with overridden subgrade height
        order = WorkOrder(id="test_001", params={'subgrade_height': 0.8})
        system = WorkOrderSystem(order)
        
        scene = SceneCheckpoint(
            config=self.config,
            work_order=system,
            materials=[]
        )
        
        worker = SubgradeWorker()
        worker.execute(scene, {}, self.materials, None)
        
        # Check geometry
        subgrade_box = scene.geometry[-1] # Assuming last added
        print(f"Subgrade Top Y: {subgrade_box.y2}")
        
        self.assertAlmostEqual(subgrade_box.y2, 0.8, msg="SubgradeWorker did not use WorkOrder height!")
        self.assertAlmostEqual(system.get('subgrade_top_y'), 0.8, msg="SubgradeWorker output not logged!")

    def test_antenna_dynamic_height(self):
        print("\n--- Testing AntennaWorker Dynamic Height ---")
        # Initialize with clearance
        clearance = 0.1
        order = WorkOrder(id="test_002", params={'antenna_clearance_above_ballast': clearance})
        system = WorkOrderSystem(order)
        
        scene = SceneCheckpoint(
            config=self.config,
            work_order=system,
            materials=[]
        )
        
        # Simulate RockWorker outputting a high rock
        high_rock_y = 1.5
        system.set('highest_rock_y', high_rock_y, 'RockWorker')
        
        worker = AntennaWorker()
        worker.execute(scene, {}, self.materials, None)
        
        # Find antenna source
        tx_y = None
        for cmd in scene.sources:
            if hasattr(cmd, 'y'): # Dipole or Rx
                tx_y = cmd.y
                break
                
        expected_y = high_rock_y + clearance
        print(f"Highest Rock: {high_rock_y}, Clearance: {clearance}")
        print(f"Antenna Y: {tx_y}")
        
        self.assertAlmostEqual(tx_y, expected_y, msg=f"Antenna height {tx_y} != expected {expected_y}")

if __name__ == '__main__':
    unittest.main()

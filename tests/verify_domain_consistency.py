
import sys
import unittest
from pathlib import Path
sys.path.append(str(Path("d:/Codigo/Synth-GPR")))

from src.workers import AirWorker, SubgradeWorker, AssemblerWorker
from src.worker import SceneCheckpoint
from src.config import GeneratorConfig
from src.work_order import WorkOrderSystem, WorkOrder
from src.warehouses import MaterialWarehouse

class TestDomainConsistency(unittest.TestCase):
    def setUp(self):
        self.config = GeneratorConfig()
        self.materials = MaterialWarehouse(self.config)
        
    def test_domain_override(self):
        print("\n--- Testing Domain Override Consistency ---")
        
        # Override default domain (0.5) with strict 1.0m
        target_domain_x = 1.0
        order = WorkOrder(id="test_domain", params={'domain_x': target_domain_x})
        system = WorkOrderSystem(order)
        
        scene = SceneCheckpoint(
            config=self.config,
            work_order=system,
            materials=[]
        )
        
        # 1. Run AirWorker (Sets background)
        print("Running AirWorker...")
        AirWorker().execute(scene, {}, self.materials, None)
        air_box = scene.geometry[0]
        self.assertAlmostEqual(air_box.x2, target_domain_x, msg="AirWorker failed to use overridden domain_x")
        
        # 2. Run SubgradeWorker (Sets foundational layer)
        print("Running SubgradeWorker...")
        SubgradeWorker().execute(scene, {}, self.materials, None)
        sub_box = scene.geometry[-1]
        self.assertAlmostEqual(sub_box.x2, target_domain_x, msg="SubgradeWorker failed to use overridden domain_x")
        
        # 3. Run AssemblerWorker (Validates domain)
        print("Running AssemblerWorker...")
        # Mock source to pass check
        # Place antenna at X=0.9 (Valid for 1.0m, invalid for default 0.5m)
        from src.gpr_commands import HertzianDipoleCommand, RxCommand
        scene.sources.append(HertzianDipoleCommand("z", 0.9, 1.0, 0.0, "src"))
        scene.sources.append(RxCommand(0.95, 1.0, 0.0))
        scene.rock_positions = [] # No rocks to crash into
        
        qc_errors = AssemblerWorker().quality_check(scene)
        
        if qc_errors:
            print("QC Errors found:")
            for e in qc_errors:
                print(f"  - {e}")
                
        self.assertEqual(len(qc_errors), 0, msg=f"AssemblerWorker flagged valid positions for overridden domain: {qc_errors}")

if __name__ == '__main__':
    unittest.main()

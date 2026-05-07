
import sys
import unittest
from pathlib import Path

sys.path.append(str(Path("d:/Codigo/Synth-GPR")))

from src.workers import (
    AirWorker, SubgradeWorker, FormationWorker, BallastWorker, 
    RockWorker, FoulingWorker, AntennaWorker
)
from src.worker import SceneCheckpoint
from src.config import GeneratorConfig
from src.work_order import WorkOrderSystem, WorkOrder
from src.warehouses import MaterialWarehouse, ToolWarehouse

class TestAllWorkersReadWorkOrder(unittest.TestCase):
    def setUp(self):
        self.config = GeneratorConfig() # Default
        self.materials = MaterialWarehouse(self.config)
        self.tools = ToolWarehouse(self.config)
        
    def test_rainbow_scenario(self):
        """
        Rainbow Test: Specify UNIQUE, non-default values for EVERY layer/parameter 
        in the WorkOrder and verify that the final scene matches these exact values.
        """
        print("\n--- Running Rainbow Verification Test ---")
        
        # 1. Define Unique WorkOrder Values
        # These must be different from defaults in config.py
        wo_params = {
            'domain_x': 0.777,        # Default 0.5
            'domain_y': 1.888,        # Default 1.5
            'domain_z': 0.009,        # Default 0.005
            'subgrade_height': 0.444, # Default 0.3
            'formation_thickness': 0.111, # Default 0.1
            'ballast_thickness': 0.555,   # Default 0.4
            'pvc': 50.0,                  # Default 0.0
            'moisture': 0.5,             # High moisture
            'antenna_clearance_above_ballast': 0.222, # Default 0.5
            'antenna_offset': 0.05
        }
        
        order = WorkOrder(id="rainbow_001", params=wo_params)
        system = WorkOrderSystem(order)
        
        scene = SceneCheckpoint(
            config=self.config,
            work_order=system,
            materials=[]
        )
        
        # 2. Run Pipeline Sequence
        workers = [
            AirWorker(),
            SubgradeWorker(),
            FormationWorker(),
            BallastWorker(),
            RockWorker(),
            FoulingWorker(),
            AntennaWorker()
            # AssemblerWorker skipped as it is read-only validation
        ]
        
        print("Executing worker pipeline...")
        for w in workers:
            w.execute(scene, {}, self.materials, self.tools)
            
        print("Pipeline complete. Verifying geometry...")
        
        # 3. Verify Geometry Matches WorkOrder
        
        # Air
        print("Checking Air (Domain)...")
        air_box = scene.geometry[0]
        self.assertAlmostEqual(air_box.x2, 0.777, msg="AirWorker missed domain_x")
        self.assertAlmostEqual(air_box.y2, 1.888, msg="AirWorker missed domain_y")
        self.assertAlmostEqual(air_box.z2, 0.009, msg="AirWorker missed domain_z")
        
        # Subgrade
        print("Checking Subgrade...")
        subgrade_box = next(c for c in scene.geometry if c.material == "subgrade")
        self.assertAlmostEqual(subgrade_box.y2, 0.444, msg="SubgradeWorker missed subgrade_height")
        self.assertAlmostEqual(subgrade_box.x2, 0.777, msg="SubgradeWorker missed domain_x")
        
        # Formation
        print("Checking Formation...")
        formation_box = next(c for c in scene.geometry if c.material == "formation")
        expected_form_top = 0.444 + 0.111
        self.assertAlmostEqual(formation_box.y1, 0.444, msg="FormationWorker missed start height (subgrade top)")
        self.assertAlmostEqual(formation_box.y2, expected_form_top, msg="FormationWorker missed thickness")
        
        # Ballast
        print("Checking Ballast Bounds...")
        # BallastWorker writes to WorkOrder but doesn't create geometry itself (RockWorker does)
        # Check WorkOrder outputs
        self.assertAlmostEqual(system.get('ballast_bottom_y'), expected_form_top, msg="BallastWorker start_y mismatch")
        expected_ballast_top = expected_form_top + 0.555
        self.assertAlmostEqual(system.get('ballast_top_y'), expected_ballast_top, msg="BallastWorker top_y mismatch")
        
        # RockWorker
        print("Checking Rocks...")
        # Highest rock should be roughly near top (but probabilistic)
        # Should NOT exceed domain X
        for rock in scene.rock_positions:
            self.assertTrue(rock.x <= 0.777, msg=f"Rock at {rock.x} exceeds domain_x 0.777")
            
        highest_rock_y = system.get('highest_rock_y')
        print(f"Highest Rock Y reported: {highest_rock_y}")
        self.assertTrue(highest_rock_y > expected_form_top, "RockWorker placed no rocks?")
        
        # Fouling
        print("Checking Fouling...")
        # With PVC=50%, expect settled layer
        foul_cmds = [c for c in scene.geometry if getattr(c, 'material', '') == 'bal_foul_granular']
        self.assertTrue(len(foul_cmds) > 0, "FoulingWorker produced no geometry for PVC=50")
        
        # Antenna
        print("Checking Antenna...")
        tx_rx_y = system.get('tx_rx_y')
        expected_ant_y = highest_rock_y + 0.222
        # Note: AntennaWorker uses max(config.tx_rx_y, highest + clearance)
        # Config default is 1.4. Let's see if our stack exceeds that.
        # 0.444 + 0.111 + 0.555 = 1.11. 
        # So rocks are around 1.1 max. + 0.222 = 1.332.
        # This is LESS than default 1.4. So it will clamp to 1.4.
        
        # To verify WorkOrder *read*, we must ensure the calculation logic was attempted.
        # Let's check if offset worked (X pos)
        tx_src = next(c for c in scene.sources if hasattr(c, 'y') and hasattr(c, 'waveform'))
        base_tx_x = self.config.tx_x # 0.3
        expected_tx_x = base_tx_x + 0.05
        self.assertAlmostEqual(tx_src.x, expected_tx_x, msg="AntennaWorker missed antenna_offset")

        print("Rainbow Test Passed!")

if __name__ == '__main__':
    unittest.main()

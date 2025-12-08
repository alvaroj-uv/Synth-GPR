
import sys
import unittest
import pandas as pd
from pathlib import Path

sys.path.append(str(Path("d:/Codigo/Synth-GPR")))

from src.worker import SceneCheckpoint
from src.workers import RockWorker
from src.config import GeneratorConfig
from src.work_order import WorkOrderSystem, WorkOrder
from src.warehouses import MaterialWarehouse

class TestRockDataFrame(unittest.TestCase):
    def setUp(self):
        self.config = GeneratorConfig()
        self.materials = MaterialWarehouse(self.config)

    def test_rock_dataframe_generation(self):
        print("\n--- Testing Rock DataFrame Generation ---")
        
        # 1. Setup Scene
        system = WorkOrderSystem(WorkOrder(id="df_test"))
        system.set('ballast_bottom_y', 0.5, 'TestSetup')
        system.set('ballast_top_y', 0.9, 'TestSetup')
        
        scene = SceneCheckpoint(config=self.config, work_order=system, materials=[])

        # 2. Execute RockWorker
        worker = RockWorker()
        worker.execute(scene, {}, self.materials, None)
        
        # 3. Verify DataFrame in WorkOrder
        df = system.get('rock_model')
        
        print(f"DataFrame Retrieved: {type(df)}")
        self.assertIsNotNone(df, "Rock DataFrame not found in WorkOrder!")
        self.assertIsInstance(df, pd.DataFrame, "Stored object is not a DataFrame")
        
        # 4. Verify Columns and Content
        expected_cols = ['x', 'y', 'z_start', 'z_end', 'radius', 'material']
        self.assertTrue(all(col in df.columns for col in expected_cols), f"Missing columns. Found: {df.columns}")
        
        print(f"Rows generated: {len(df)}")
        self.assertTrue(len(df) > 0, "DataFrame is empty")
        
        # Verify Z coverage (should be 0-0 for default config request)
        print(f"Z range: {df['z_start'].min()} - {df['z_end'].max()}")
        self.assertEqual(df['z_start'].min(), 0.0)
        # Default rock_z_end is now 0.005, so max should be 0.005
        self.assertEqual(df['z_end'].max(), 0.005)
        
        # 5. Verify COORDINATES (Absolute Y > 0.5)
        min_y = df['y'].min()
        print(f"Minimum Y found: {min_y}")
        self.assertGreaterEqual(min_y, 0.5, "Y coordinates should be absolute (>= ballast_bottom_y)")
        
        # 6. Verify Consumers (Regression)
        # Check if FoulingWorker can run without crashing (reading from DF)
        from src.workers import FoulingWorker
        system.set('pvc', 20.0, 'TestSetup')
        fworker = FoulingWorker()
        try:
            fworker.execute(scene, {}, self.materials, None)
            print("FoulingWorker executed successfully with DataFrame input.")
        except Exception as e:
            self.fail(f"FoulingWorker crashed consuming DataFrame: {e}")

if __name__ == '__main__':
    unittest.main()

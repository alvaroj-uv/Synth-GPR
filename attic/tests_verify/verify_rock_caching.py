
import unittest
import sys
import os
import shutil
import time
from unittest.mock import MagicMock

# Add project root to path (one level up from tests)
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.workers import RockWorker
from src.warehouse_keeper import WarehouseKeeper
from src.warehouses import MaterialWarehouse, ToolWarehouse
from src.config import GeneratorConfig
from src.worker import SceneCheckpoint
from src.rock_packing import PoissonDiskPacking

class TestRockCaching(unittest.TestCase):
    def setUp(self):
        # Setup temp cache dir
        self.cache_dir = os.path.join(os.path.dirname(__file__), "temp_cache")
        if os.path.exists(self.cache_dir):
            shutil.rmtree(self.cache_dir)
        os.makedirs(self.cache_dir)
        
        
        # Setup Components
        # Verify caching requires it to be enabled.
        self.config = GeneratorConfig(enable_rock_caching=True)
        self.materials = MaterialWarehouse(self.config)
        self.tools = ToolWarehouse(self.config)
        self.keeper = WarehouseKeeper(self.materials, self.tools, cache_dir=self.cache_dir)
        
        self.worker = RockWorker()
        
    def tearDown(self):
        if os.path.exists(self.cache_dir):
            shutil.rmtree(self.cache_dir)
            
    def test_caching_mechanism(self):
        scene = SceneCheckpoint(self.config)
        # Mock work order for bounds
        scene.work_order = MagicMock()
        scene.work_order.get.side_effect = lambda k, default: default
        scene.work_order.get_input.side_effect = lambda k, default: default
        
        params = {
            'seed': 'test_seed'
            # 'packing_strategy': PoissonDiskPacking(k_attempts=5), # Removed to test default
        }
        
        print("\n--- Run 1: Generation ---")
        start = time.time()
        self.worker.execute(scene, self.keeper, params)
        duration_1 = time.time() - start
        
        # Check trace or log to confirm Strategy used?
        # RockWorker prints "[RockWorker] Cache MISS..."
        # But doesn't print strategy name.
        # However, we can assert metadata or derived properties.
        # FrontChain is generally slower than Poisson.
        
        self.assertEqual(scene.metadata.get('packing_source'), 'generated')
        print(f"Time 1: {duration_1:.4f}s")
        
        # Verify cache file created
        files = os.listdir(self.cache_dir)
        pkl_files = [f for f in files if f.endswith('.pkl')]
        self.assertEqual(len(pkl_files), 1, "Should have created 1 cache file")
        
        print("\n--- Run 2: Cache Hit ---")
        # Reset scene rocks
        scene.rock_positions = []
        scene.geometry = []
        
        start = time.time()
        self.worker.execute(scene, self.keeper, params)
        duration_2 = time.time() - start
        
        self.assertEqual(scene.metadata.get('packing_source'), 'cache')
        print(f"Time 2: {duration_2:.4f}s")
        
        # Assert Speedup (though for small N it might be negligible, checking logic mostly)
        self.assertTrue(os.path.exists(os.path.join(self.cache_dir, pkl_files[0])))
        
        print("\n--- Run 3: Cache Disabled ---")
        # Disable caching in config
        # Config is frozen, so we hack it for the test or verify logic by params
        # RockWorker checks `scene.config.enable_rock_caching`.
        # We can mock the attribute access on the config object if we can't replace it
        # Actually SceneCheckpoint holds the config.
        new_config = dataclasses.replace(self.config, enable_rock_caching=False)
        scene.config = new_config
        
        # Reset scene rocks
        scene.rock_positions = []
        scene.metadata['packing_source'] = 'unknown'
        
        start = time.time()
        self.worker.execute(scene, self.keeper, params)
        duration_3 = time.time() - start
        
        self.assertEqual(scene.metadata.get('packing_source'), 'generated', 
                         "Should be 'generated' when cache is disabled")
        print(f"Time 3: {duration_3:.4f}s")

if __name__ == '__main__':
    import dataclasses
    unittest.main()

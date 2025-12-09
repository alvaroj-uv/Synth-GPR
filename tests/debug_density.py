
import unittest
import sys
import os
import numpy as np
from unittest.mock import MagicMock

# Add project root
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.workers import RockWorker
from src.worker import SceneCheckpoint
from src.config import GeneratorConfig
from src.rock_packing import FrontChainPacking, TrianglePacking, PoissonDiskPacking

# Check scipy
try:
    import scipy.spatial
    print("Scipy available.")
except ImportError:
    print("CRITICAL: Scipy missing!")

class DummyWorkOrder:
    def __init__(self):
        self.logs = []
    
    def get_input(self, key, default):
        return default
        
    def get(self, key, default):
        return default
        
    def set(self, key, val, source=None):
        pass
        
    def log_issue(self, worker, issue_type, severity, description, context=None):
        entry = f"[{worker}] {severity.upper()}: {description}"
        self.logs.append(entry)
        print(entry)

class TestDensityDebug(unittest.TestCase):
    def test_density_calculation(self):
        config = GeneratorConfig()
        # Ensure consistent bounds
        config = dataclasses.replace(config, 
            domain_x=0.5, 
            rock_z_start=0.0, rock_z_end=0.005,
            rock_radius_min=0.02, rock_radius_max=0.03,
            rock_packing_max_attempts=100
        )
        
        scene = SceneCheckpoint(config)
        scene.work_order = DummyWorkOrder()
        
        # Mock bounds in metadata
        scene.metadata['ballast_bottom_y'] = 0.0
        scene.metadata['ballast_thickness'] = 0.4
        
        # Use TrianglePacking
        strategy = TrianglePacking() 
        
        print("\n--- Testing TrianglePacking Density ---")
        worker = RockWorker()
        
        params = {'packing_strategy': strategy, 'seed': 42}
        tools = MagicMock() # Tools can be mock if not used for JSON
        
        # Tools warning: passing MagicMock as tools might cause issues if tools properties are accessed and hashed?
        # get_cached_rocks logic checks hasattr(tools, 'get_cached_rocks').
        # MagicMock has everything.
        # It calls tools.get_cached_rocks(key). returns Mock.
        # if cached_rocks: (Mock is truthy).
        # It tries to iterate Mock.
        # So we MUST set tools.get_cached_rocks.return_value = None to force miss.
        tools.get_cached_rocks.return_value = None
        
        worker.execute(scene, params, tools, tools)
        
        # Verify Results
        n_rocks = len(scene.rock_positions)
        print(f"Rocks Generated: {n_rocks}")
        
        if n_rocks == 0:
             print("ERRORS in WorkOrder:", scene.work_order.logs)


        
        if n_rocks == 0:
             print("ERRORS in WorkOrder:", scene.work_order.logs)
        
        # Monte Carlo Density Check
        achieved_density = scene.metadata.get('achieved_density', -1)
        porosity = scene.metadata.get('porosity', -1)
        
        print(f"Worker Reported Density (MC): {achieved_density:.4f}")
        print(f"Worker Reported Porosity (MC): {porosity:.4f}")
        
        self.assertLess(achieved_density, 0.95, "Density should be realistic (<95%) even with dense packing")
        self.assertGreater(achieved_density, 0.1, "Density should be >10%")
        self.assertAlmostEqual(achieved_density + porosity, 1.0, places=5)

import dataclasses
if __name__ == '__main__':
    unittest.main()

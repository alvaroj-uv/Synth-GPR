
import unittest
import sys
import os
import time

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from rock_packing import FrontChainPacking, PoissonDiskPacking, PhysicsPacking, PackingBounds, Rock

class TestPackingStrategies(unittest.TestCase):
    def test_density_comparison(self):
        bounds = PackingBounds(0.0, 0.5, 0.0, 0.2)
        r_min = 0.015
        r_max = 0.025
        
        print("\n--- Comparing All Packing Strategies ---")
        
        # 1. Poisson Disk
        start = time.time()
        poisson = PoissonDiskPacking(k_attempts=30)
        rocks_p = poisson.generate_rocks(bounds, r_min, r_max, target_fill_ratio=0.8)
        time_p = time.time() - start
        
        area_p = sum([3.14159 * r.radius**2 for r in rocks_p])
        density_p = area_p / bounds.area
        print(f"Poisson:     {len(rocks_p)} rocks, Density={density_p:.3f}, Time={time_p:.3f}s")
        
        # 2. Front Chain
        start = time.time()
        front = FrontChainPacking()
        rocks_f = front.generate_rocks(bounds, r_min, r_max, target_fill_ratio=0.8)
        time_f = time.time() - start
        
        area_f = sum([3.14159 * r.radius**2 for r in rocks_f])
        density_f = area_f / bounds.area
        print(f"FrontChain:  {len(rocks_f)} rocks, Density={density_f:.3f}, Time={time_f:.3f}s")
        
        # 3. Physics (Relaxation)
        start = time.time()
        physics = PhysicsPacking()
        # Physics starts overpacked (target 1.0) and settles
        # Mass-weighted packing should run smoother.
        rocks_h = physics.generate_rocks(bounds, r_min, r_max, target_fill_ratio=0.85, max_attempts=150)
        time_h = time.time() - start
        
        area_h = sum([3.14159 * r.radius**2 for r in rocks_h])
        density_h = area_h / bounds.area
        print(f"Physics:     {len(rocks_h)} rocks, Density={density_h:.3f}, Time={time_h:.3f}s")
        
        # Assertions
        # Physics should generally achieve high density if configured right
        self.assertTrue(len(rocks_h) > 0, "PhysicsPacking should generate rocks")
        
        # Check that we didn't break older ones
        self.assertTrue(len(rocks_p) > 0)
        self.assertTrue(len(rocks_f) > 0)


if __name__ == '__main__':
    unittest.main()

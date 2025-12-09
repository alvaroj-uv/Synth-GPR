
import unittest
import sys
import os
import time

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from rock_packing import PoissonDiskPacking, PackingBounds, Rock

class TestVoidFilling(unittest.TestCase):
    def test_void_filling(self):
        bounds = PackingBounds(0.0, 0.5, 0.0, 0.5)
        r_min = 0.04 # Large rocks initially
        r_max = 0.06
        
        # 1. Initial sparse packing
        strategy = PoissonDiskPacking(k_attempts=30)
        rocks = strategy.generate_rocks(bounds, r_min, r_max, target_fill_ratio=0.6)
        
        initial_count = len(rocks)
        initial_area = sum([3.14159 * r.radius**2 for r in rocks])
        initial_density = initial_area / bounds.area
        
        print(f"\nInitial: {initial_count} rocks, Density={initial_density:.3f}")
        
        # 2. Fill Voids
        start = time.time()
        # Try to insert small 1cm rocks
        rocks_filled = strategy.fill_voids(rocks, bounds, min_void_radius=0.01, attempts=1000)
        duration = time.time() - start
        
        final_count = len(rocks_filled)
        final_area = sum([3.14159 * r.radius**2 for r in rocks_filled])
        final_density = final_area / bounds.area
        
        print(f"Final:   {final_count} rocks, Density={final_density:.3f}, Time={duration:.3f}s")
        print(f"Added:   {final_count - initial_count} fillers")
        
        # Assertions
        self.assertGreater(final_count, initial_count, "Should have added filler rocks")
        self.assertGreater(final_density, initial_density, "Density should increase")
        
        # Check validity (ensure no overlap)
        # We only check the *new* rocks against all rocks
        # Naive O(N^2) check
        for i in range(initial_count, final_count):
            r_new = rocks_filled[i]
            for j in range(final_count):
                if i == j: continue
                r_other = rocks_filled[j]
                dist = ((r_new.x - r_other.x)**2 + (r_new.y - r_other.y)**2)**0.5
                min_dist = r_new.radius + r_other.radius
                self.assertGreaterEqual(dist, min_dist - 0.001, f"Overlap detected between {i} and {j}")

if __name__ == '__main__':
    unittest.main()


import unittest
import sys
import os
import time
import numpy as np

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from rock_packing import TrianglePacking, PackingBounds, Rock

class TestTrianglePacking(unittest.TestCase):
    def test_triangle_packing_validity(self):
        bounds = PackingBounds(0.0, 1.0, 0.0, 1.0) # 1x1m box
        r_min = 0.02
        r_max = 0.10
        
        strategy = TrianglePacking()
        start = time.time()
        
        # Triangle packing ignores target_fill_ratio (determined by mesh geometry)
        rocks = strategy.generate_rocks(bounds, r_min, r_max)
        duration = time.time() - start
        
        count = len(rocks)
        area = sum([np.pi * r.radius**2 for r in rocks])
        density = area / bounds.area
        
        print(f"\nTriangle Packing: {count} rocks, Density={density:.3f}, Time={duration:.3f}s")
        
        self.assertGreater(count, 0, "Should generate rocks")
        self.assertLess(density, 1.0, "Density < 100%")
        
        # Verify no intersections (property of mesh packing)
        # Random sample check
        for i in range(min(count, 50)): 
            r1 = rocks[i]
            for j in range(i+1, min(count, 50)):
                r2 = rocks[j]
                dist = np.hypot(r1.x - r2.x, r1.y - r2.y)
                # Allow tiny float error
                self.assertGreaterEqual(dist, r1.radius + r2.radius - 0.0001, "Rocks should not overlap")

if __name__ == '__main__':
    unittest.main()

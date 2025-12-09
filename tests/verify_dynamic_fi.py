
import unittest
import sys
import os
from unittest.mock import MagicMock

# Add project root to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.workers import RockWorker, FoulingWorker
from src.physics import classify_pvc, convert_pvc_to_fi
from src.worker import SceneCheckpoint
from src.config import GeneratorConfig

class TestDynamicFI(unittest.TestCase):
    def test_fi_calculation_sensitivity(self):
        """Verify FI changes with porosity for same PVC."""
        pvc = 50.0
        
        # Case A: Loose Packing (n=0.4)
        # Voids = 40% of Volume. Foul = 50% of Voids = 20% of Tot Vol.
        # Rock = 60% of Tot Vol.
        # Mass Ratio approx 20/60 = 1/3 -> FI ~ 25%
        fi_loose = convert_pvc_to_fi(pvc, porosity=0.4)
        print(f"Loose (n=0.4, PVC=50) -> FI={fi_loose:.2f}")
        
        # Case B: Dense Packing (n=0.2)
        # Voids = 20% of Volume. Foul = 50% of Voids = 10% of Tot Vol.
        # Rock = 80% of Tot Vol.
        # Mass Ratio approx 10/80 = 1/8 -> FI ~ 11%
        fi_dense = convert_pvc_to_fi(pvc, porosity=0.2)
        print(f"Dense (n=0.2, PVC=50) -> FI={fi_dense:.2f}")
        
        self.assertLess(fi_dense, fi_loose, "Dense packing should result in lower FI for same PVC (less void volume)")
        
        # Verify Classification
        cls_loose = classify_pvc(pvc, porosity=0.4)
        cls_dense = classify_pvc(pvc, porosity=0.2)
        print(f"Class Loose: {cls_loose}")
        print(f"Class Dense: {cls_dense}")
        
        # Might be different classes depending on thresholds
        # Loose (25%) -> F (20-40)
        # Dense (11%) -> MF (10-20)
        self.assertNotEqual(cls_loose, cls_dense)

    def test_worker_integration(self):
        """Verify workers pass porosity correctly."""
        config = GeneratorConfig()
        scene = SceneCheckpoint(config)
        scene.work_order = MagicMock()
        scene.work_order.get_input.return_value = 50.0 # PVC
        
        # Mock geometry and rock model
        import pandas as pd
        empty_df = pd.DataFrame(columns=['x', 'y', 'radius'])
        
        def mock_get(key, default=None):
            if key == 'rock_model': return empty_df
            if key == 'ballast_bottom_y': return 0.0
            if key == 'ballast_thickness': return 0.4
            return default if default is not None else 0.5
            
        scene.work_order.get.side_effect = mock_get
        scene.work_order.get_input.return_value = 50.0 # PVC
        
        # Mock RockWorker setting porosity
        scene.metadata['porosity'] = 0.2
        scene.metadata['ballast_bottom_y'] = 0.0
        scene.metadata['ballast_thickness'] = 0.4
        
        # Run FoulingWorker
        worker = FoulingWorker()
        # Mock dependencies
        materials = MagicMock()
        
        # Avoid _calculate_ballast_bounds failing if called
        # config defaults are sufficient (domain_x=0.5, etc)
        
        worker.execute(scene, {}, materials, None)
        
        # Check if FI_class matches dense calculation
        expected_class = classify_pvc(50.0, porosity=0.2)
        self.assertEqual(scene.metadata['FI_class'], expected_class)
        self.assertEqual(scene.metadata['used_porosity'], 0.2)

if __name__ == '__main__':
    unittest.main()

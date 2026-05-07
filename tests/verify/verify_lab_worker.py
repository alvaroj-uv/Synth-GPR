
import unittest
import sys
import os
import numpy as np
from unittest.mock import MagicMock
from dataclasses import dataclass

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.lab_worker import LabWorker
from src.worker import SceneCheckpoint
from src.config import GeneratorConfig
from src.physics import convert_pvc_to_fi

@dataclass
class MockRock:
    x: float
    y: float
    radius: float

class TestLabWorker(unittest.TestCase):
    def test_sieve_analysis_clean(self):
        """Test clean ballast -> FI=0"""
        config = GeneratorConfig()
        scene = SceneCheckpoint(config)
        scene.rock_positions = [MockRock(0,0,0.02)]
        scene.metadata['pvc'] = 0.0
        
        worker = LabWorker()
        worker.execute(scene, {}, None, None)
        
        self.assertEqual(scene.metadata.get('Lab_FI'), 0.0)
        self.assertEqual(scene.metadata.get('Lab_Class'), "C")

    def test_sieve_analysis_fouled(self):
        """Test fouled ballast logic"""
        config = GeneratorConfig()
        scene = SceneCheckpoint(config)
        
        
        # 1. Setup Scene
        # 10 rocks, r=20mm (0.02m)
        # Place them at y=0.05 to be inside the default 0.15m sampling layer.
        # With r=0.02, y range is [0.03, 0.07]. Fully inside.
        rocks = [MockRock(0.1*i, 0.05, 0.02) for i in range(10)]
        scene.rock_positions = rocks
        
        # Metadata
        scene.metadata['ballast_bottom_y'] = 0.0 # Anchor
        scene.metadata['domain_x'] = 1.0
        pvc = 40.0
        porosity = 0.35 # Realistic
        scene.metadata['pvc'] = pvc
        scene.metadata['porosity'] = porosity
        
        # 2. Execute
        worker = LabWorker()
        worker.execute(scene, {}, None, None)
        
        # 3. Verify
        lab_fi = scene.metadata.get('Lab_FI')
        lab_porosity = scene.metadata.get('Lab_Porosity', porosity) # Use actual extracted porosity
        self.assertIsNotNone(lab_fi)
        
        # 4. Compare with Analytical Physics Calculation
        # Recalculate expected FI using the Lab's measured porosity
        expected_fi = convert_pvc_to_fi(pvc, porosity=lab_porosity)
        
        print(f"Lab FI: {lab_fi:.2f}")
        # Tolerance: Floating point noise
        # Lab FI should be HIGHER than Mass Fraction (Physics FI) because FI = P4 + P200.
        # Physics FI is essentially P4 (Mass Fraction of Material < 4.75mm).
        # Lab FI adds the P200 component (Fines).
        
        self.assertGreater(lab_fi, expected_fi)
        
        # Verify Ratio
        # P200 = 0.3 * P4 (Hardcoded in LabWorker for now)
        # FI = P4 + 0.3*P4 = 1.3 * P4
        # expected_fi is roughly P4.
        ratio = lab_fi / expected_fi
        print(f"Ratio Lab/Physics: {ratio:.2f}")
        # Ratio Lab/Physics:
        # Lab FI accounts for fines (P200) and Local Density (Slice).
        # Physics FI is Global Mass Estimator.
        # Expect Lab > Physics generally.
        self.assertGreater(ratio, 1.1)
        self.assertLess(ratio, 1.6)

    def test_layer_sampling(self):
        """Test vertical slicing (Horizontal Layer) logic"""
        config = GeneratorConfig()
        scene = SceneCheckpoint(config)
        
        # 3 Rocks stacked vertically
        # r=0.05 (10cm dia). Center Y at 0.05, 0.15, 0.25 (Assuming ballast start 0.0)
        scene.rock_positions = [
            MockRock(0.5, 0.05, 0.05), # Bottom (Should be fully in 0-0.15 strip)
            MockRock(0.5, 0.15, 0.05), # Middle (Half in, half out?)
            # Wait, r=0.05.
            # Rock 1: Y=[0.0, 0.10]. Fully inside [0.0, 0.15].
            # Rock 2: Center 0.15. Y=[0.10, 0.20]. Half inside [0.0, 0.15].
            # Rock 3: Center 0.25. Y=[0.20, 0.30]. Outside.
            MockRock(0.5, 0.25, 0.05) 
        ]
        
        scene.metadata['ballast_bottom_y'] = 0.0
        scene.metadata['domain_x'] = 1.0
        pvc = 40.0 
        scene.metadata['pvc'] = pvc # Global PVC
        
        # Calculate Fouling Height
        # ballast thick = 0.4 (default).
        # fouling_height = 0.4 * 0.4 = 0.16m.
        # settled (100% fill) = 0.16 * 0.7 = 0.112m.
        
        # If we sample 0.05m (bottom 5cm), it is FULLY SATURATED.
        # So effective local PVC = 100%.
        
        params = {'sample_height': 0.05}
        
        worker = LabWorker()
        
        print("\n--- Test Layer Sampling ---")
        worker.execute(scene, params, None, None)
        
        # Verification
        # 1. Porosity ~0.9 (Low rock count in this bottom slice?)
        # 2. Local PVC = 100% (Saturated).
        # 3. Expected FI = convert_pvc_to_fi(100, porosity=Lab_Porosity)
        # 4. Lab FI = Expected FI * 1.3 (Silt factor)
        
        lab_fi = scene.metadata.get('Lab_FI')
        lab_porosity = scene.metadata.get('Lab_Porosity')
        
        expected_physics_fi_saturated = convert_pvc_to_fi(100.0, porosity=lab_porosity)
        
        print(f"Lab FI: {lab_fi:.2f}")
        print(f"Physics Saturated FI: {expected_physics_fi_saturated:.2f}")
        
        
        ratio = lab_fi / expected_physics_fi_saturated
        print(f"Ratio: {ratio:.2f}")
        
        # Ratio around 1.3 - 1.45 is expected due to fines/density nuances.
        # Validating simply that Lab FI accounts for fines (Ratio > 1.1) is sufficient.
        self.assertGreater(ratio, 1.1)
        self.assertLess(ratio, 1.6)

if __name__ == '__main__':
    unittest.main()

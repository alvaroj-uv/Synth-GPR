import sys
import os
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent))

from src.physics import convert_pvc_to_fi, inverse_convert_fi_to_pvc

def test_round_trip():
    print("Testing Physics Math Round-Trip (FI -> PVC -> FI)...")
    
    test_fis = [1.0, 5.0, 10.0, 25.0, 40.0, 45.0, 99.0]
    
    for target_fi in test_fis:
        # 1. Inverse: Get required PVC
        pvc = inverse_convert_fi_to_pvc(target_fi)
        
        # 2. Forward: Calculate resulting FI
        calculated_fi = convert_pvc_to_fi(pvc)
        
        # 3. Check
        error = abs(target_fi - calculated_fi)
        print(f"Target FI: {target_fi:5.2f}% -> Required PVC: {pvc:6.2f}% -> Result FI: {calculated_fi:5.2f}% | Error: {error:.2e}")
        
        if error > 1e-4:
            print("  [FAIL] Round trip failed!")
            sys.exit(1)
            
    print("\n[SUCCESS] All math checks passed.")

if __name__ == "__main__":
    test_round_trip()

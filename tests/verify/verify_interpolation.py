
import unittest
import math
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.physics import log_linear_interpolation, get_percent_passing

class TestInterpolation(unittest.TestCase):
    def test_log_linear_simple(self):
        """Test simple log-linear case D=10, P=10; D=1000, P=30."""
        # Log10(10)=1, Log10(1000)=3.
        # Log10(100)=2 (Midpoint in Log Space).
        # P should be midpoint of 10 and 30 -> 20.
        
        px = log_linear_interpolation(100.0, 10.0, 10.0, 1000.0, 30.0)
        self.assertAlmostEqual(px, 20.0)

    def test_linear_fail(self):
        """Demonstrate that Linear Interpolation would give different result."""
        # Linear Midpoint of 10 and 1000 is 505.
        # P at 505 should be 20 linear.
        # But in Log-Linear:
        # Log(505) ~ 2.703.
        # Range Log [1, 3] -> span 2.
        # (2.703 - 1) / 2 = 0.8515 (85% of range).
        # P = 10 + 0.8515 * 20 = 27.03.
        
        px_log = log_linear_interpolation(505.0, 10.0, 10.0, 1000.0, 30.0)
        self.assertAlmostEqual(px_log, 27.03, places=2)
        
        # P at 100 (Log midpoint) is 20.
        # Linear P at 100: (100-10)/(1000-10) * 20 + 10 = 0.09 * 20 + 10 = 11.8.
        # Big difference! 20 vs 11.8.

    def test_get_percent_passing(self):
        """Test PSD curve lookup."""
        psd = [
            (4.75, 100.0),
            (2.0, 80.0), # Log(2) ~ 0.301
            (0.075, 30.0) # Log(0.075) ~ -1.125
        ]
        
        # Check Exact Matches
        self.assertEqual(get_percent_passing(4.75, psd), 100.0)
        self.assertEqual(get_percent_passing(0.075, psd), 30.0)
        
        # Check Interpolated Point
        # Between 2.0 and 0.075.
        # D=0.425.
        # Log(0.425) = -0.371.
        # Log(2.0) = 0.301.
        # Log(0.075) = -1.125.
        # Fraction = (-0.371 - (-1.125)) / (0.301 - (-1.125)) = 0.754 / 1.426 = 0.528.
        # P1=30, P2=80. Delta=50.
        # Px = 30 + 0.528 * 50 = 30 + 26.4 = 56.4.
        
        result = get_percent_passing(0.425, psd)
        print(f"P_0.425 = {result:.2f}")
        self.assertAlmostEqual(result, 56.4, delta=0.5)

if __name__ == '__main__':
    unittest.main()


import unittest
import sys
import shutil
from pathlib import Path

# Add project root to sys.path
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from src.synthetic_data_generator import BallastScenarioGenerator
from src.config import GeneratorConfig
import re

class TestDataGeneration(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        # Setup test paths
        cls.test_config_path = Path(__file__).parent / "test_config.ini"
        cls.output_dir = Path("d:/Codigo/Synth-Data/Test_Output")
        
        # Ensure clean state
        if cls.output_dir.exists():
            shutil.rmtree(cls.output_dir)
            
    def test_load_config(self):
        """Test if config can be loaded from INI."""
        cfg = GeneratorConfig.from_ini(str(self.test_config_path))
        self.assertTrue(cfg.granular_mode)
        # n_samples is not in GeneratorConfig, it's a dataset generation param
        self.assertEqual(cfg.domain_x, 0.5)

    def test_generation_end_to_end(self):
        """Test full generation pipeline using BallastScenarioGenerator."""
        cfg = GeneratorConfig.from_ini(str(self.test_config_path))
        generator = BallastScenarioGenerator(cfg)
        
        # We need to manually parse the DatasetGeneration params since they aren't in cfg
        import configparser
        cp = configparser.ConfigParser()
        cp.read(self.test_config_path)
        
        n_samples = cp.getint("DatasetGeneration", "n_samples")
        start_id = cp.getint("DatasetGeneration", "start_id")
        out_dir = Path(cp.get("DatasetGeneration", "output_dir"))
        
        # Generate
        df = generator.generate_dataset(
            out_dir=out_dir,
            n_samples=n_samples,
            start_id=start_id
        )
        
        # Verification
        self.assertTrue(out_dir.exists())
        file_path = out_dir / f"s_{start_id:04d}.in"
        self.assertTrue(file_path.exists())
        
        # Check CSV
        csv_path = out_dir / "metadata.csv"
        self.assertTrue(csv_path.exists())
        self.assertFalse(df.empty)
        
        # Check content
        content = file_path.read_text()
        self.assertIn("#domain", content)
        self.assertIn("Granular Aggregates", content)
        
        # Validate Geometry Validity
        self.check_geometry_validity(content, cfg)

    def check_geometry_validity(self, content: str, cfg: GeneratorConfig):
        """Parse commands and verify geometric constraints."""
        lines = content.splitlines()
        
        # Parse domain
        domain = [0.0, 0.0, 0.0]
        for line in lines:
            if line.startswith("#domain:"):
                parts = line.split(":")[1].strip().split()
                domain = [float(p) for p in parts]
                break
        
        # Verify Domain matches config
        self.assertAlmostEqual(domain[0], cfg.domain_x)
        self.assertAlmostEqual(domain[1], cfg.domain_y)
        self.assertAlmostEqual(domain[2], cfg.domain_z)
        
        # Check commands
        for line in lines:
            if line.startswith("#box:"):
                # Format: #box: x1 y1 z1 x2 y2 z2 material
                parts = line.split(":")[1].strip().split()
                coords = [float(x) for x in parts[:6]]
                x1, y1, z1, x2, y2, z2 = coords
                
                # Tuple Consistency (Min <= Max)
                self.assertLessEqual(x1, x2, f"Box x1>x2: {line}")
                self.assertLessEqual(y1, y2, f"Box y1>y2: {line}")
                self.assertLessEqual(z1, z2, f"Box z1>z2: {line}")
                
                # Domain Limits
                # Allow small float tolerance if needed, but strict is better for 'validity'
                self.assertGreaterEqual(x1, 0.0)
                self.assertGreaterEqual(y1, 0.0)
                self.assertGreaterEqual(z1, 0.0)
                self.assertLessEqual(x2, domain[0])
                self.assertLessEqual(y2, domain[1])
                self.assertLessEqual(z2, domain[2])
                
            elif line.startswith("#cylinder:"):
                # Format: #cylinder: x1 y1 z1 x2 y2 z2 radius material
                parts = line.split(":")[1].strip().split()
                coords = [float(x) for x in parts[:6]]
                radius = float(parts[6])
                
                x1, y1, z1, x2, y2, z2 = coords
                
                # Check Radius
                self.assertGreater(radius, 0.0, f"Cylinder radius <= 0: {line}")
                
                # Check Axis Consistency (Here we check if points are within expanded domain?)
                # GprMax requires objects to be specified, clipping happens automatically? 
                # Or does it error if strictly outside? Manual says "Objects can be defined outside... they are clipped".
                # But 'validity' usually means 'intended placement'. 
                # We check center is inside domain.
                
                # Center estimate
                cx = (x1 + x2) / 2
                cy = (y1 + y2) / 2
                cz = (z1 + z2) / 2
                
                # Check center is roughly in domain (allow margin for edge clipping)
                # Being strict: Center MUST be valid?
                # Actually, aggregates at edges are fine.
                # Let's check min/max tuple consistency for axis? 
                # Cylinder axis definition doesn't enforce x1<x2, it's a vector. 
                # But for our 2D Z-invariant cylinders, we usually expect z1=0, z2=domain_z.
                self.assertAlmostEqual(z1, 0.0)
                self.assertAlmostEqual(z2, domain[2])
                self.assertAlmostEqual(x1, x2) # Vertical cylinder in Z? No, 'axis' is the length.
                # Wait, #cylinder: x1 y1 z1 x2 y2 z2 r
                # If it represents a circle in XY plane, the axis is parallel to Z.
                # So x1=x2, y1=y2, z1=0, z2=domain_z.
                
                self.assertAlmostEqual(x1, x2, places=4, msg=f"Cylinder not Z-aligned: {line}")
                self.assertAlmostEqual(y1, y2, places=4, msg=f"Cylinder not Z-aligned: {line}")
                
                # Check bounds (allowing radius to poke out)
                # But centers should be reasonable (e.g. not -100)
                self.assertGreaterEqual(x1, -radius)
                self.assertLessEqual(x1, domain[0] + radius)
                self.assertGreaterEqual(y1, -radius)
                self.assertLessEqual(y1, domain[1] + radius)

if __name__ == '__main__':
    unittest.main()

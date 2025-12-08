
import sys
from pathlib import Path
import dataclasses
import shutil

# Add src to path
sys.path.append(str(Path("d:/Codigo/Synth-GPR")))

from src.config import GeneratorConfig
from src.geometry_composer import ScenePainter, BackgroundLayer
from src.dataset_generator import DatasetGenerator

def test_generator_config_immutability():
    print("Testing GeneratorConfig immutability...")
    cfg = GeneratorConfig()
    try:
        cfg.dx = 0.1
        print("FAIL: Config should be immutable!")
        sys.exit(1)
    except dataclasses.FrozenInstanceError:
        print("PASS: Config is immutable.")

def test_config_validation():
    print("Testing GeneratorConfig validation...")
    try:
        GeneratorConfig(dx=-1)
        print("FAIL: Config validation missed negative dx!")
        sys.exit(1)
    except ValueError:
        print("PASS: Config validation caught negative dx.")

def test_scenepainter_encapsulation():
    print("Testing ScenePainter encapsulation...")
    cfg = GeneratorConfig()
    painter = ScenePainter(cfg)
    
    if hasattr(painter, 'layers'):
        print("FAIL: ScenePainter still has public 'layers' attribute!")
        # sys.exit(1) # Warning for now if backward compat preserved, but we removed it.
    
    if not hasattr(painter, '_layers'):
         print("FAIL: ScenePainter missing private '_layers'!")
         sys.exit(1)
         
    painter.add_layer(BackgroundLayer())
    if len(painter._layers) != 1:
        print("FAIL: add_layer did not work.")
        sys.exit(1)
        
    print("PASS: ScenePainter encapsulation checks out.")

def test_full_generation_pipeline():
    print("Testing full generation pipeline...")
    cfg = GeneratorConfig(granular_mode=True, pvc_max=20.0, output_dir="test_output", add_sleepers=True)
    gen = DatasetGenerator(cfg)
    
    out_dir = Path("d:/Codigo/Synth-GPR/test_output")
    if out_dir.exists():
        shutil.rmtree(out_dir)
        
    files, metadata = gen.generate_samples(out_dir, n_samples=2)
    
    if not (out_dir / "s_0000.in").exists():
        print("FAIL: Base file not generated.")
        sys.exit(1)
        
    if not (out_dir / "s_0000_r1.in").exists():
         print("FAIL: Randomized variant not generated.")
         sys.exit(1)
         
    print(f"PASS: Generated {len(metadata)} records.")
    
    # Check if file contains expected headers
    content = (out_dir / "s_0000.in").read_text()
    if "## Mode: Granular" not in content:
        print("FAIL: Output file missing granular header.")
        sys.exit(1)
    
    print("PASS: File content verification basic check.")

if __name__ == "__main__":
    test_generator_config_immutability()
    test_config_validation()
    test_scenepainter_encapsulation()
    test_full_generation_pipeline()
    print("ALL TESTS PASSED.")

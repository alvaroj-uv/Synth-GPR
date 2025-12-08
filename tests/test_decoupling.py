import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from src.geometry_composer import AntennaLayer, ScenePainter
from src.config import GeneratorConfig
from src.gpr_commands import HertzianDipoleCommand, Header, RxCommand

def test_antenna_layer_output():
    config = GeneratorConfig()
    layer = AntennaLayer()
    
    # Run apply
    result = layer.apply(config, start_y=1.0)
    
    print("Testing Antenna Layer Output...")
    
    # Check Sources
    sources = result.sources
    print(f"Sources count: {len(sources)}")
    assert len(sources) >= 2, "Should have dipole and rx"
    assert any(isinstance(c, HertzianDipoleCommand) for c in sources), "Missing HertzianDipole"
    assert any(isinstance(c, RxCommand) for c in sources), "Missing Rx"
    
    # Check Geometry
    geom = result.geometry
    print(f"Geometry count: {len(geom)}")
    # Should have Start Layer, End Layer, and maybe "TX/RX in aire" comment
    assert any("Start Layer" in c.render() for c in geom if isinstance(c, Header)), "Missing Start Layer comment"
    assert any("End Layer" in c.render() for c in geom if isinstance(c, Header)), "Missing End Layer comment"
    
    print("PASS: Antenna Layer output is correctly decoupled.")

def test_scene_painter_aggregation():
    config = GeneratorConfig()
    painter = ScenePainter(config)
    painter.add_layer(AntennaLayer())
    
    print("\nTesting Scene Painter Aggregation...")
    scene = painter.paint()
    
    # Check Source Commands
    print(f"Scene Sources: {len(scene.source_commands)}")
    assert len(scene.source_commands) >= 2
    
    # Check Geometry Commands
    print(f"Scene Geometry: {len(scene.geometry_commands)}")
    assert len(scene.geometry_commands) >= 2
    
    print("PASS: Scene Painter aggregation works.")

if __name__ == "__main__":
    try:
        test_antenna_layer_output()
        test_scene_painter_aggregation()
        print("\nALL TESTS PASSED")
    except AssertionError as e:
        print(f"\nFAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\nERROR: {e}")
        sys.exit(1)

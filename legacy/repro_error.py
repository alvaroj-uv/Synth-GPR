
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path("d:/Codigo/Synth-GPR")))

from src.file_writer import GPRMaxFileWriter, StructuredCommands
from src.gpr_commands import Header, GPRCommand
from src.geometry_composer import ScenePainter, BackgroundLayer, GeneratorConfig

def test_manual_structure():
    print("Testing StructuredCommands manually...")
    sc = StructuredCommands()
    sc.header.append(CommentCommand("Header"))
    try:
        # Simulate the error condition
        sc.header.append("I am a string imposter") 
        print("Added imposter.")
        sc.render()
    except AttributeError as e:
        print(f"Caught expected error: {e}")

def test_pipeline_components():
    print("\nTesting Pipeline Components...")
    cfg = GeneratorConfig()
    painter = ScenePainter(cfg)
    painter.add_layer(BackgroundLayer())
    
    print("Painting scene...")
    setup, content, meta = painter.paint()
    
    print(f"Setup items: {len(setup)}")
    for i, item in enumerate(setup):
        if not isinstance(item, GPRCommand):
             print(f"FAIL: Setup item {i} is not GPRCommand: {type(item)} = {item}")
        else:
             print(f"  Setup item {i}: {type(item).__name__}")
             
    print(f"Content items: {len(content)}")
    for i, item in enumerate(content):
        if not isinstance(item, GPRCommand):
             print(f"FAIL: Content item {i} is not GPRCommand: {type(item)} = {item}")
        else:
             print(f"  Content item {i}: {type(item).__name__}")

    # Test Writer
    print("\nTesting Writer...")
    try:
        GPRMaxFileWriter.compose_content(cfg, "test", setup, content, meta)
        print("Writer compose_content successful.")
    except Exception as e:
        print(f"Writer failed: {e}")

if __name__ == "__main__":
    test_manual_structure()
    test_pipeline_components()

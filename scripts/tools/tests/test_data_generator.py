import sys
from pathlib import Path
# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.synthetic_data_generator import GeneratorConfig, BallastScenarioGenerator
import pandas as pd
from pathlib import Path

def test_generation():
    cfg = GeneratorConfig(
        base_seed=123,
        add_waveform=True,
        add_source=True,
        add_geometry_view=False
    )
    gen = BallastScenarioGenerator(cfg)
    
    out_dir = Path("test_output")
    if out_dir.exists():
        import shutil
        shutil.rmtree(out_dir)
    
    df = gen.generate_dataset(out_dir=out_dir, n_samples=5, csv_name="test_metadata.csv")
    print(f"Generated {len(df)} samples.")
    
    # Read one file and print content
    sample_file = out_dir / df.iloc[0]['filename']
    print(f"\n--- Content of {sample_file.name} ---")
    print(sample_file.read_text(encoding='utf-8'))

if __name__ == "__main__":
    test_generation()

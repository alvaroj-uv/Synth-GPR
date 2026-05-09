"""
Generate sample WITH domain randomization enabled.
Uses same seed as baseline for comparison.
"""
import random
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from src.config import GeneratorConfig
from src.dataset_generator import DatasetGenerator

# Set seed for reproducibility
random.seed(30000)

# Create config with domain randomization ENABLED
config = GeneratorConfig()
config.enable_domain_randomization = True
config.base_seed = 30000

# Use default randomization parameters
print("Domain Randomization Parameters:")
print(f"  Soil ε variation: ±{config.soil_eps_variation*100}%")
print(f"  Rock ε variation: ±{config.rock_eps_variation*100}%")
print(f"  Moisture range: 0-{config.moisture_randomization_range*100}%")
print(f"  Spatial jitter σ: {config.spatial_jitter_sigma*100}cm")
print()

# Generate dataset
generator = DatasetGenerator(
    output_dir="d:/Codigo/Synth-Data/ComparisonTest/Randomized",
    config=config
)

print("Generating sample with domain randomization...")
generator.generate_dataset(
    labels=["C"],
    samples_per_label=1,
    start_id=30000
)

print("\nDone! File created:")
print("  d:/Codigo/Synth-Data/ComparisonTest/Randomized/s_30000.in")

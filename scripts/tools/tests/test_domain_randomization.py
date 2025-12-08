"""
Test script to compare domain randomization ON vs OFF.
Generates samples with same seed to show differences.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.config import GeneratorConfig
from src.dataset_generator import DatasetGenerator

# Test 1: Without randomization (baseline)
print("=" * 60)
print("Test 1: WITHOUT Domain Randomization")
print("=" * 60)

config_baseline = GeneratorConfig()
config_baseline.enable_domain_randomization = False
config_baseline.base_seed = 30000

generator_baseline = DatasetGenerator(
    output_dir="d:/Codigo/Synth-Data/DomainRandComparison/Baseline",
    config=config_baseline
)

# Generate 1 clean sample
generator_baseline.generate_dataset(
    labels=["CL"],
    samples_per_label=1,
    start_id=30000
)

print("\n" + "=" * 60)
print("Test 2: WITH Domain Randomization")
print("=" * 60)

# Test 2: With randomization (same seed!)
config_randomized = GeneratorConfig()
config_randomized.enable_domain_randomization = True
config_randomized.base_seed = 30000  # SAME SEED

# Randomization parameters (using defaults)
config_randomized.soil_eps_variation = 0.2
config_randomized.rock_eps_variation = 0.1
config_randomized.moisture_randomization_range = 0.15
config_randomized.spatial_jitter_sigma = 0.02

generator_randomized = DatasetGenerator(
    output_dir="d:/Codigo/Synth-Data/DomainRandComparison/Randomized",
    config=config_randomized
)

# Generate 1 clean sample (same parameters)
generator_randomized.generate_dataset(
    labels=["CL"],
    samples_per_label=1,
    start_id=30000
)

print("\n" + "=" * 60)
print("Comparison Test Complete!")
print("=" * 60)
print("\nGenerated files:")
print("  Baseline:    d:/Codigo/Synth-Data/DomainRandComparison/Baseline/s_30000.in")
print("  Randomized:  d:/Codigo/Synth-Data/DomainRandComparison/Randomized/s_30000.in")
print("\nNext steps:")
print("  1. Run gprMax simulations on both")
print("  2. Generate blueprints")
print("  3. Compare visually")

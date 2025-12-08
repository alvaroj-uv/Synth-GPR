"""Quick test of DatasetGenerator"""
from src.dataset_generator import DatasetGenerator
from src.config import GeneratorConfig

# Create minimal config
cfg = GeneratorConfig(
    base_seed=42,
    granular_mode=True,
    pvc_min=10.0,
    pvc_max=30.0
)

# Create generator
gen = DatasetGenerator(cfg)

# Test parameter sampling
params = gen._sample_parameters()
print(f"Sampled parameters: {params}")

# Test single sample generation
print("\nGenerating 1 sample...")
files = gen.generate_samples("output/test_dataset", n_samples=1, start_id=0)

print(f"\n✓ Generated {len(files)} file(s)")
for f in files:
    print(f"  - {f}")

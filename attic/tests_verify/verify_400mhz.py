from src.dataset_generator import DatasetGenerator
from src.config import GeneratorConfig
import os

# Create 400MHz config mimicking 400MHz_production.ini
cfg = GeneratorConfig(
    center_freq=4e8,        # 400 MHz
    time_window=3.0e-8,     # Larger window for lower freq
    dx=0.005,
    dy=0.005,
    dz=0.005,
    domain_x=0.5,
    domain_y=1.5,
    domain_z=0.005,
    granular_mode=True,
    base_seed=123
)

print(f"Testing Config: Freq={cfg.center_freq/1e6} MHz, Window={cfg.time_window}")

# Create generator
gen = DatasetGenerator(cfg)

# Output directory
out_dir = "output/verify_400"
if os.path.exists(out_dir):
    try:
        import shutil
        shutil.rmtree(out_dir)
    except:
        pass

# Run 1 sample
print("\nRunning pipeline...")
files = gen.generate_samples(out_dir, n_samples=1, start_id=400)

print(f"\nGenerated Files: {files}")

# Verify content
in_file = files[0]
with open(in_file, 'r') as f:
    content = f.read()
    
# Check crucial 400MHz indicators
checks = {
    "center_freq parameter": "#center_freq" not in content, # Should NOT be there, handled by waveform
    "waveform freq": "ricker 1 4e+08" in content,
    "time_window": "time_window: 3e-08" in content,
    "FI_class header": "FI_class:" in content
}

print("\nVerification Results:")
all_pass = True
for name, passed in checks.items():
    status = "OK" if passed else "FAIL"
    print(f"[{status}] {name}")
    if not passed: all_pass = False

if all_pass:
    print("\nSUCCESS: 400MHz Pipeline Verified")
else:
    print("\nFAILURE: Issues Validating 400MHz Output")

import os
import shutil
import subprocess
import sys
from src.dataset_generator import DatasetGenerator
from src.config import GeneratorConfig

OUT_DIR = "output/contrast_set"
BLUEPRINT_TOOL = "scripts/tools/visualization/visualize_gprmax_blueprint.py"

# Clean up passed output
if os.path.exists(OUT_DIR):
    try:
        shutil.rmtree(OUT_DIR)
    except:
        pass
os.makedirs(OUT_DIR, exist_ok=True)

# --------------------------------------------------------------------------
# 1. Generate CLEAN Sample (Class C: PVC < 1%)
# --------------------------------------------------------------------------
print("\n[1/4] Generating CLEAN Sample (Class C)...")
cfg_c = GeneratorConfig(
    center_freq=4e8,
    time_window=2e-8,
    domain_x=0.5,
    domain_y=1.5,
    domain_z=0.005,
    granular_mode=True,
    pvc_min=0.0,
    pvc_max=0.5,    # < 1%
    moisture_min=0.0,
    moisture_max=0.05,
    base_seed=1001,
    output_dir=OUT_DIR
)
gen_c = DatasetGenerator(cfg_c)
files_c = gen_c.generate_samples(OUT_DIR, n_samples=1, start_id=100)
file_c = files_c[0] if files_c else None

# Rename for clarity
clean_in = os.path.join(OUT_DIR, "clean_sample.in")
if file_c:
    os.rename(file_c, clean_in)
    file_c = clean_in

# --------------------------------------------------------------------------
# 2. Generate HIGHLY FOULED Sample (Class HF: FI >= 40%) -- PVC ~ 45-50
# --------------------------------------------------------------------------
print("\n[2/4] Generating HIGHLY FOULED Sample (Class HF)...")
cfg_hf = GeneratorConfig(
    center_freq=4e8,
    time_window=2e-8,
    domain_x=0.5,
    domain_y=1.5,
    domain_z=0.005,
    granular_mode=True,
    pvc_min=85.0,
    pvc_max=95.0,   # > 85% PVC needed for > 40% FI (HF)
    moisture_min=0.20,
    moisture_max=0.25, # High moisture often accompanies fouling
    base_seed=1002,
    output_dir=OUT_DIR
)
gen_hf = DatasetGenerator(cfg_hf)
files_hf = gen_hf.generate_samples(OUT_DIR, n_samples=1, start_id=200)
file_hf = files_hf[0] if files_hf else None

# Rename
hf_in = os.path.join(OUT_DIR, "hf_sample.in")
if file_hf:
    os.rename(file_hf, hf_in)
    file_hf = hf_in

# --------------------------------------------------------------------------
# 3. Simulate Both (Optional but good for verification)
#    We will skip full simulation to save time unless requested, 
#    but running it ensures .out files exist for blueprint signal plotting.
#    Let's run them.
# --------------------------------------------------------------------------
print("\n[3/4] Running Simulations...")
for fname, label in [(clean_in, "CLEAN"), (hf_in, "HF")]:
    if fname and os.path.exists(fname):
        print(f"   Simulating {label}...")
        cmd = f'"{sys.executable}" -m gprMax "{fname}" -n 1'
        subprocess.run(cmd, shell=True, capture_output=True)
    else:
        print(f"   Skipping {label} (File not found)")

# --------------------------------------------------------------------------
# 4. Generate Blueprints
# --------------------------------------------------------------------------
print("\n[4/4] Generating Blueprints...")
for fname, label in [(clean_in, "clean"), (hf_in, "hf")]:
    if fname and os.path.exists(fname):
        out_img = os.path.join(OUT_DIR, f"blueprint_{label}.png")
        print(f"   Visualizing {label.upper()} -> {out_img}")
        cmd = f'"{sys.executable}" {BLUEPRINT_TOOL} "{fname}" -o "{out_img}" --no-show'
        subprocess.run(cmd, shell=True, capture_output=True)

print("\nProcessing Complete.")
print(f"Outputs in: {OUT_DIR}")

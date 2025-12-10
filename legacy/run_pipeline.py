import os
import sys
import subprocess
import shutil
from src.dataset_generator import DatasetGenerator
from src.config import GeneratorConfig

# 1. SETUP
OUT_DIR = "output/pipeline_e2e"
IN_FILE = os.path.join(OUT_DIR, "pipeline_test.in")
BLUEPRINT_TOOL = "scripts/tools/visualization/visualize_gprmax_blueprint.py"

if os.path.exists(OUT_DIR):
    try:
        shutil.rmtree(OUT_DIR)
    except:
        pass
os.makedirs(OUT_DIR, exist_ok=True)

# 2. GENERATE
print("[1/3] Generating Input File...")
cfg = GeneratorConfig(
    center_freq=4e8,
    time_window=2e-8,
    domain_x=0.5,
    domain_y=1.5,
    domain_z=0.005,
    pvc_min=45.0,
    pvc_max=55.0,
    moisture_min=0.15,
    moisture_max=0.20,
    granular_mode=True,
    base_seed=999 # Use a different seed for variety
)
gen = DatasetGenerator(cfg)
files, metadata = gen.generate_samples(OUT_DIR, n_samples=1, start_id=0)

# Rename to known filename
if files and os.path.exists(files[0]):
    try:
        if os.path.abspath(files[0]) != os.path.abspath(IN_FILE):
             os.rename(files[0], IN_FILE)
    except Exception as e:
        print(f"Rename error: {e}")


# 3. RUN SIMULATION
print("[2/3] Running gprMax Simulation...")
cmd_sim = f'"{sys.executable}" -m gprMax "{IN_FILE}" -n 1'
res = subprocess.run(cmd_sim, shell=True, capture_output=True, text=True)
if res.returncode != 0:
    print("Simulation Failed:", res.stderr)
    exit(1)
else:
    print("Simulation Complete.")

# 4. VISUALIZE (Using BluePrint Tool)
print("[3/3] Generating Blueprint Image...")
cmd_viz = f'"{sys.executable}" {BLUEPRINT_TOOL} "{IN_FILE}" -o "{OUT_DIR}/blueprint_final.png" --no-show'
res_viz = subprocess.run(cmd_viz, shell=True, capture_output=True, text=True)

if res_viz.returncode != 0:
    print("Visualization Failed:", res_viz.stderr)
    print(res_viz.stdout)
else:
    print("Visualization Complete.")
    print(f"Output: {OUT_DIR}/blueprint_final.png")

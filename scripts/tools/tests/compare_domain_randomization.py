# -*- coding: utf-8 -*-
"""
Comparison test for domain randomization using INI files.
Generates baseline and randomized samples, runs simulations, and creates blueprints.
"""
import subprocess
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from src.config import GeneratorConfig
from src.synthetic_data_generator import BallastScenarioGenerator

print("=" * 70)
print("DOMAIN RANDOMIZATION COMPARISON TEST")
print("=" * 70)

# Test 1: Baseline (randomization OFF)
print("\n[1/6] Generating BASELINE sample (randomization OFF)...")
config_baseline = GeneratorConfig.from_ini("config_baseline.ini")
gen_baseline = BallastScenarioGenerator(config=config_baseline)
gen_baseline.generate_dataset(
    out_dir="d:/Codigo/Synth-Data/Tests/RandomizationTest/Baseline",
    n_samples=1,
    start_id=30000
)
print("[OK] Generated: d:/Codigo/Synth-Data/Tests/RandomizationTest/Baseline/s_30000.in")

# Test 2: Randomized (randomization ON)
print("\n[2/6] Generating RANDOMIZED sample (randomization ON)...")
config_randomized = GeneratorConfig.from_ini("config_randomized.ini")
gen_randomized = BallastScenarioGenerator(config=config_randomized)
gen_randomized.generate_dataset(
    out_dir="d:/Codigo/Synth-Data/Tests/RandomizationTest/Randomized",
    n_samples=1,
    start_id=30000
)
print("[OK] Generated: d:/Codigo/Synth-Data/Tests/RandomizationTest/Randomized/s_30000.in")

# Run gprMax simulations
print("\n[3/6] Running gprMax simulation (Baseline)...")
subprocess.run([
    "python", "-m", "gprMax",
    "d:/Codigo/Synth-Data/Tests/RandomizationTest/Baseline/s_30000.in",
    "-n", "1"
], check=True)
print("[OK] Simulation complete")

print("\n[4/6] Running gprMax simulation (Randomized)...")
subprocess.run([
    "python", "-m", "gprMax",
    "d:/Codigo/Synth-Data/Tests/RandomizationTest/Randomized/s_30000.in",
    "-n", "1"
], check=True)
print("[OK] Simulation complete")

# Generate blueprints
print("\n[5/6] Generating blueprint (Baseline)...")
subprocess.run([
    "python", "scripts/tools/visualization/visualize_gprmax_blueprint.py",
    "d:/Codigo/Synth-Data/Tests/RandomizationTest/Baseline/s_30000.in",
    "-o", "d:/Codigo/Synth-Data/Tests/RandomizationTest/baseline_blueprint.png",
    "--no-show"
], check=True)
print("[OK] Blueprint saved")

print("\n[6/6] Generating blueprint (Randomized)...")
subprocess.run([
    "python", "scripts/tools/visualization/visualize_gprmax_blueprint.py",
    "d:/Codigo/Synth-Data/Tests/RandomizationTest/Randomized/s_30000.in",
    "-o", "d:/Codigo/Synth-Data/Tests/RandomizationTest/randomized_blueprint.png",
    "--no-show"
], check=True)
print("[OK] Blueprint saved")

print("\n" + "="*70)
print("COMPARISON TEST COMPLETE!")
print("="*70)
print("\nResults:")
print("  Baseline blueprint:    d:/Codigo/Synth-Data/Tests/RandomizationTest/baseline_blueprint.png")
print("  Randomized blueprint:  d:/Codigo/Synth-Data/Tests/RandomizationTest/randomized_blueprint.png")
print("\nCompare the blueprints to see the effect of domain randomization!")

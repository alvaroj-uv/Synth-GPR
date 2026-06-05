#!/usr/bin/env python3
"""
Experiment: Compare monostatic vs bistatic antenna modes
Same scene, different antenna configurations, analyze .out files
"""

from pathlib import Path
import sys
import subprocess
import json

sys.path.insert(0, str(Path(__file__).parent))

from src.config import GeneratorConfig
from src.production_line import ProductionLine
from src.file_writer import GPRMaxFileWriter
from src.work_order import WorkOrder, WorkOrderSystem
from src.domain import SceneParameters

output_dir = Path("antenna_experiment")
output_dir.mkdir(exist_ok=True)

print("=" * 80)
print("EXPERIMENT: ANTENNA MODE COMPARISON")
print("Same scene, different antenna configurations")
print("=" * 80)

# Use fixed seed for reproducibility
scene_params = SceneParameters(
    pvc=25.0,
    moisture=0.05,
    ballast_thickness=0.35,
)

# 1. Generate Monostatic Scene
print("\n1. GENERATING MONOSTATIC SCENE (.in file)...")
mono_config = GeneratorConfig(antenna_mode="monostatic", domain_y=1.7)
work_order_mono = WorkOrderSystem(WorkOrder(id="exp-mono", typed_params=scene_params))
pipeline_mono = ProductionLine(mono_config)
mono_scene = pipeline_mono.run(work_order_mono)

mono_in = output_dir / "monostatic.in"
mono_out = output_dir / "monostatic"

print(f"✓ Scene generated (PVC={scene_params.pvc}%)")
print(f"  Domain: {mono_config.domain_x:.2f}m × {mono_config.domain_y:.2f}m")
print(f"  Antenna mode: {mono_config.antenna_mode}")
print(f"  TX position: X = {mono_config.tx_x:.3f}m")
print(f"  RX position: X = {mono_config.tx_x:.3f}m (co-located)")

# Write monostatic .in file
print(f"\n  Writing .in file...")
writer = GPRMaxFileWriter()
try:
    writer.write_to_file(mono_scene, str(mono_in))
    print(f"✓ Written: {mono_in}")
    file_size = mono_in.stat().st_size
    print(f"  Size: {file_size / 1024:.1f} KB")
except Exception as e:
    print(f"⚠️  Error: {e}")
    print(f"  Skipping simulation for this mode")

# 2. Generate Bistatic Scene (SAME parameters, different antenna)
print("\n2. GENERATING BISTATIC SCENE (.in file)...")
bi_config = GeneratorConfig(antenna_mode="bistatic", domain_y=1.7)
work_order_bi = WorkOrderSystem(WorkOrder(id="exp-bi", typed_params=scene_params))
pipeline_bi = ProductionLine(bi_config)
bi_scene = pipeline_bi.run(work_order_bi)

bi_in = output_dir / "bistatic.in"
bi_out = output_dir / "bistatic"

print(f"✓ Scene generated (PVC={scene_params.pvc}%)")
print(f"  Domain: {bi_config.domain_x:.2f}m × {bi_config.domain_y:.2f}m")
print(f"  Antenna mode: {bi_config.antenna_mode}")
print(f"  TX position: X = {bi_config.tx_x:.3f}m")
print(f"  RX position: X = {bi_config.rx_x:.3f}m (offset: {bi_config.rx_x - bi_config.tx_x:.3f}m)")

# Write bistatic .in file
print(f"\n  Writing .in file...")
try:
    writer.write_to_file(bi_scene, str(bi_in))
    print(f"✓ Written: {bi_in}")
    file_size = bi_in.stat().st_size
    print(f"  Size: {file_size / 1024:.1f} KB")
except Exception as e:
    print(f"⚠️  Error: {e}")
    print(f"  Skipping simulation for this mode")

# 3. Compare .in files
print("\n3. COMPARING .in FILES...")
print(f"\n  Monostatic .in structure:")
with open(mono_in) as f:
    mono_lines = f.readlines()
    print(f"    Total lines: {len(mono_lines)}")
    tx_count = sum(1 for line in mono_lines if 'hertzian_dipole' in line)
    rx_count = sum(1 for line in mono_lines if '#rx:' in line or 'rx:' in line)
    print(f"    TX commands: {tx_count}")
    print(f"    RX commands: {rx_count}")

    # Extract antenna positions
    print(f"    Antenna positions:")
    for line in mono_lines:
        if 'hertzian_dipole' in line:
            print(f"      TX: {line.strip()}")
        if '#rx:' in line:
            print(f"      RX: {line.strip()}")

print(f"\n  Bistatic .in structure:")
with open(bi_in) as f:
    bi_lines = f.readlines()
    print(f"    Total lines: {len(bi_lines)}")
    tx_count = sum(1 for line in bi_lines if 'hertzian_dipole' in line)
    rx_count = sum(1 for line in bi_lines if '#rx:' in line or 'rx:' in line)
    print(f"    TX commands: {tx_count}")
    print(f"    RX commands: {rx_count}")

    # Extract antenna positions
    print(f"    Antenna positions:")
    for line in bi_lines:
        if 'hertzian_dipole' in line:
            print(f"      TX: {line.strip()}")
        if '#rx:' in line:
            print(f"      RX: {line.strip()}")

# 4. Try to run gprMax simulations
print("\n4. RUNNING GPRMAX SIMULATIONS...")
print(f"\n  Note: gprMax simulation requires CUDA/HPC. Attempting...")

# Check if gprMax is available
gprmax_available = False
try:
    result = subprocess.run(["which", "gprMax"], capture_output=True, text=True)
    if result.returncode == 0:
        gprmax_available = True
        gprmax_path = result.stdout.strip()
        print(f"  ✓ gprMax found at: {gprmax_path}")
except:
    pass

if gprmax_available:
    print(f"\n  Running monostatic simulation...")
    try:
        result = subprocess.run(
            ["gprMax", str(mono_in), "-output", str(mono_out)],
            capture_output=True,
            text=True,
            timeout=300
        )
        if result.returncode == 0:
            print(f"  ✓ Monostatic .out generated: {mono_out}.out")
            out_file = Path(f"{mono_out}.out")
            if out_file.exists():
                print(f"    Size: {out_file.stat().st_size / (1024*1024):.2f} MB")
        else:
            print(f"  ⚠️  gprMax returned: {result.returncode}")
            if result.stderr:
                print(f"     Error: {result.stderr[:200]}")
    except subprocess.TimeoutExpired:
        print(f"  ⚠️  Simulation timed out (>300s)")
    except Exception as e:
        print(f"  ⚠️  Error: {e}")

    print(f"\n  Running bistatic simulation...")
    try:
        result = subprocess.run(
            ["gprMax", str(bi_in), "-output", str(bi_out)],
            capture_output=True,
            text=True,
            timeout=300
        )
        if result.returncode == 0:
            print(f"  ✓ Bistatic .out generated: {bi_out}.out")
            out_file = Path(f"{bi_out}.out")
            if out_file.exists():
                print(f"    Size: {out_file.stat().st_size / (1024*1024):.2f} MB")
        else:
            print(f"  ⚠️  gprMax returned: {result.returncode}")
            if result.stderr:
                print(f"     Error: {result.stderr[:200]}")
    except subprocess.TimeoutExpired:
        print(f"  ⚠️  Simulation timed out (>300s)")
    except Exception as e:
        print(f"  ⚠️  Error: {e}")
else:
    print(f"  ⚠️  gprMax not available in PATH")
    print(f"     To run simulations, install gprMax: https://www.gprmax.com")
    print(f"     Continuing with .in file comparison...")

# 5. Analysis Summary
print("\n" + "=" * 80)
print("EXPERIMENT SUMMARY")
print("=" * 80)

mono_size = mono_in.stat().st_size
bi_size = bi_in.stat().st_size
size_diff = abs(mono_size - bi_size)
size_diff_pct = (size_diff / min(mono_size, bi_size)) * 100

print(f"\nScene Configuration:")
print(f"  PVC: {scene_params.pvc}%")
print(f"  Moisture: {scene_params.moisture * 100:.0f}%")
print(f"  Ballast thickness: {scene_params.ballast_thickness:.2f}m")
print(f"  Domain: {mono_config.domain_x:.2f}m × {mono_config.domain_y:.2f}m")

print(f"\n.in File Comparison:")
print(f"  Monostatic size: {mono_size / 1024:.1f} KB")
print(f"  Bistatic size:   {bi_size / 1024:.1f} KB")
print(f"  Difference:      {size_diff / 1024:.1f} KB ({size_diff_pct:.1f}%)")

print(f"\nAntenna Configuration Impact:")
print(f"  MONOSTATIC:")
print(f"    • TX @ X = {mono_config.tx_x:.3f}m")
print(f"    • RX @ X = {mono_config.tx_x:.3f}m")
print(f"    • Offset = 0.000m (co-located)")
print(f"    • Signal: Direct TX-RX coupling, realistic railway GPR")
print(f"\n  BISTATIC:")
print(f"    • TX @ X = {bi_config.tx_x:.3f}m")
print(f"    • RX @ X = {bi_config.rx_x:.3f}m")
print(f"    • Offset = {bi_config.rx_x - bi_config.tx_x:.3f}m (separated)")
print(f"    • Signal: Reduced coupling, cleaner ML training data")

print(f"\nGenerated Files:")
print(f"  📄 {mono_in.absolute()}")
print(f"  📄 {bi_in.absolute()}")

if Path(f"{mono_out}.out").exists():
    print(f"  📊 {mono_out}.out ({Path(f'{mono_out}.out').stat().st_size / (1024*1024):.2f} MB)")
if Path(f"{bi_out}.out").exists():
    print(f"  📊 {bi_out}.out ({Path(f'{bi_out}.out').stat().st_size / (1024*1024):.2f} MB)")

print(f"\nTo run gprMax simulations:")
print(f"  1. Install gprMax from https://www.gprmax.com")
print(f"  2. Run: gprMax {mono_in}")
print(f"  3. Run: gprMax {bi_in}")
print(f"  4. Compare .out files to see signal differences")

print(f"\nExpected differences in .out:")
print(f"  • Monostatic: Direct pulse at T=0, strong coupling reflection")
print(f"  • Bistatic: Delayed signal due to TX-RX separation")
print(f"  • Amplitude difference due to antenna spacing")
print(f"  • Both see same subsurface (rocks/fouling)")

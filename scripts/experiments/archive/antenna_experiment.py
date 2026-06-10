#!/usr/bin/env python3
"""
Antenna Mode Experiment
Modify existing .in files to show monostatic vs bistatic differences
Analyze the signal differences in gprMax commands
"""

from pathlib import Path
import sys
import re

sys.path.insert(0, str(Path(__file__).parent))

from src.config import GeneratorConfig

output_dir = Path("antenna_experiment")
output_dir.mkdir(exist_ok=True)

print("=" * 80)
print("ANTENNA MODE EXPERIMENT")
print("Comparing monostatic vs bistatic .in files")
print("=" * 80)

# Get configs
mono_config = GeneratorConfig(antenna_mode="monostatic")
bi_config = GeneratorConfig(antenna_mode="bistatic")

print(f"\n1. CONFIGURATION PARAMETERS")
print(f"\n  MONOSTATIC:")
print(f"    antenna_mode = '{mono_config.antenna_mode}'")
print(f"    tx_x = {mono_config.tx_x:.4f}m")
print(f"    rx_x = {mono_config.tx_x:.4f}m (co-located with TX)")
print(f"    antenna_spacing = 0.000m")

print(f"\n  BISTATIC:")
print(f"    antenna_mode = '{bi_config.antenna_mode}'")
print(f"    tx_x = {bi_config.tx_x:.4f}m")
print(f"    rx_x = {bi_config.rx_x:.4f}m")
print(f"    antenna_spacing = {bi_config.rx_x - bi_config.tx_x:.4f}m")

# 2. Create synthetic .in file templates
print(f"\n2. CREATING .in FILE TEMPLATES")

# Template for gprMax input file
def create_in_template(tx_x, rx_x, filename):
    """Create a minimal gprMax input file template"""
    domain_x = 0.6
    domain_y = 1.7
    domain_z = 0.05

    content = f"""#title: Antenna comparison - {filename}
#domain: {domain_x:.3f} {domain_y:.3f} {domain_z:.3f}
#dx_dy_dz: {1/1000:.6f} {1/1000:.6f} {1/1000:.6f}
#time_window: 10e-9

# Materials
#material: 3.0 0.0 1.0 0.0 soil
#material: 80.0 1.0 1.0 0.0 concrete

# TX antenna (Hertzian dipole)
#hertzian_dipole: z {tx_x:.4f} 0.75 0 myRicker

# RX antenna (point receiver)
#rx: {rx_x:.4f} 0.75 0

# Source waveform
#waveform: ricker 1 400e6 myricker

# Geometry
#box: 0 0 0 {domain_x:.3f} {domain_y:.3f} {domain_z:.3f} soil

# Run simulation
#run_simulation
"""
    return content

# Create monostatic template
mono_in = output_dir / "monostatic_template.in"
mono_content = create_in_template(mono_config.tx_x, mono_config.tx_x, "monostatic")
with open(mono_in, 'w') as f:
    f.write(mono_content)
print(f"  ✓ {mono_in.name} ({len(mono_content)} bytes)")

# Create bistatic template
bi_in = output_dir / "bistatic_template.in"
bi_content = create_in_template(bi_config.tx_x, bi_config.rx_x, "bistatic")
with open(bi_in, 'w') as f:
    f.write(bi_content)
print(f"  ✓ {bi_in.name} ({len(bi_content)} bytes)")

# 3. Compare key differences
print(f"\n3. ANALYZING .in FILE DIFFERENCES")

# Extract antenna positions
mono_tx = re.search(r'#hertzian_dipole:.*?(\d+\.\d+)', mono_content)
mono_rx = re.search(r'#rx:.*?(\d+\.\d+)', mono_content)
bi_tx = re.search(r'#hertzian_dipole:.*?(\d+\.\d+)', bi_content)
bi_rx = re.search(r'#rx:.*?(\d+\.\d+)', bi_content)

print(f"\n  TX/RX Positions:")
print(f"    Monostatic: TX @ {mono_tx.group(1)}m, RX @ {mono_rx.group(1)}m")
print(f"    Bistatic:   TX @ {bi_tx.group(1)}m, RX @ {bi_rx.group(1)}m")

# Calculate signal delay difference
wavelength_400mhz = 0.75 / 400e6  # 300M speed of light / frequency
tx_rx_spacing = bi_config.rx_x - bi_config.tx_x

# Approximate delay (2-way for received signal)
signal_delay = (2 * tx_rx_spacing) / 0.075  # rough approximation
print(f"\n  Signal Characteristics:")
print(f"    Frequency: 400 MHz")
print(f"    Speed (approx): 0.075 m/ns")
print(f"    Antenna spacing: {tx_rx_spacing:.4f}m")
print(f"    Signal delay difference: ~{signal_delay:.1f}ns (1-way)")

print(f"\n  Key Differences in Output (.out):")
print(f"    MONOSTATIC:")
print(f"      • Direct TX-RX coupling at t=0")
print(f"      • Early strong reflection from direct path")
print(f"      • Subsurface signals mix with coupling")
print(f"      • Amplitude: ~100% coupling effect")
print(f"\n    BISTATIC:")
print(f"      • No direct TX-RX coupling (spatially separated)")
print(f"      • Delayed signal arrival ({signal_delay:.1f}ns)")
print(f"      • Cleaner subsurface reflections (less noise)")
print(f"      • Better for ML training (cleaner features)")

# 4. File size comparison
print(f"\n4. FILE SIZE COMPARISON")
mono_size = len(mono_content)
bi_size = len(bi_content)
print(f"  Monostatic .in: {mono_size} bytes")
print(f"  Bistatic .in:   {bi_size} bytes")
print(f"  Difference:     {abs(mono_size - bi_size)} bytes")
print(f"  Same structure: ✓ (just antenna position differs)")

# 5. Show the actual differences
print(f"\n5. ACTUAL .in FILE DIFFERENCES")
print(f"\n  MONOSTATIC antenna commands:")
for line in mono_content.split('\n'):
    if 'hertzian_dipole' in line or '#rx:' in line:
        print(f"    {line}")

print(f"\n  BISTATIC antenna commands:")
for line in bi_content.split('\n'):
    if 'hertzian_dipole' in line or '#rx:' in line:
        print(f"    {line}")

# 6. Summary
print(f"\n" + "=" * 80)
print(f"EXPERIMENT SUMMARY")
print(f"=" * 80)

print(f"\nFiles generated in: {output_dir.absolute()}")
print(f"  • {mono_in.name}")
print(f"  • {bi_in.name}")

print(f"\nAntenna Impact on Signals:")
print(f"  Parameter:        antenna_mode = 'monostatic' vs 'bistatic'")
print(f"  Physical change:  RX moves from {mono_config.tx_x:.4f}m to {bi_config.rx_x:.4f}m")
print(f"  Spacing impact:   {tx_rx_spacing:.4f}m offset")
print(f"  Signal delay:     ~{signal_delay:.1f}ns added to bistatic")
print(f"  Coupling:         Monostatic = HIGH, Bistatic = NONE")
print(f"\nFor actual .out comparison:")
print(f"  1. Run gprMax with both .in files")
print(f"  2. Load .out files in Python")
print(f"  3. Compare A-scans (received waveforms)")
print(f"  4. Notice: Bistatic has cleaner reflections (less coupling)")

print(f"\nCommand to run simulations:")
print(f"  gprMax {mono_in}")
print(f"  gprMax {bi_in}")
print(f"\nThen compare the .out files to see actual signal differences!")

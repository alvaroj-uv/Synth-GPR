#!/usr/bin/env python3
"""Create free space 400 MHz .in file using the project pipeline."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import GeneratorConfig
from src.work_order import WorkOrder, WorkOrderSystem
from src.file_writer import GPRMaxFileWriter
from src.scene_model import SceneBuilder

# Create configuration for free space 400 MHz
config = GeneratorConfig(
    center_freq=400e6,  # 400 MHz
    domain_x=0.5,       # 0.5m domain (large enough for free space)
    domain_y=0.5,       # 0.5m height
    domain_z=0.003,     # 3mm depth (minimal)
    dx=0.005,           # 5mm grid (coarse for free space)
    dy=0.005,
    dz=0.005,
    time_window=2.0e-8, # 20 ns (captures direct wave)
    tx_x=0.25,          # Center
    rx_x=0.30,          # 5cm offset
    tx_rx_z=0.0015,     # Center of domain_z
    pml_layers=10,
    add_waveform=True,
    add_source=True,
    source_waveform="ricker",
)

# Create work order (free space only, no ballast/fouling)
work_order = WorkOrder(
    id="freespace_400mhz",
    params={
        'fouling_class': 'FREEAIR',  # No fouling - free space
        'pvc': 0.0,                   # No fouling content
    }
)
work_order_system = WorkOrderSystem(work_order)

# Build scene (air only)
try:
    # Create minimal scene with just air domain
    scene_builder = SceneBuilder(config, work_order_system)
    scene = scene_builder.build()

    # Write .in file
    output_dir = Path('d:/Codigo/Synth-GPR/output_test')
    output_dir.mkdir(parents=True, exist_ok=True)

    writer = GPRMaxFileWriter()
    in_file = output_dir / 'freespace_400mhz.in'

    # Write the scene to .in file
    writer.write(scene, output_path=in_file)

    print(f"✓ Created free space 400 MHz .in file: {in_file}")
    print(f"  Domain: {config.domain_x}m × {config.domain_y}m × {config.domain_z}m")
    print(f"  Grid: {config.dx*1000:.1f}mm × {config.dy*1000:.1f}mm × {config.dz*1000:.1f}mm")
    print(f"  Frequency: 400 MHz")
    print(f"  Time window: 20 ns")
    print(f"\n  To run simulation:")
    print(f"  gprMax {in_file}")

except Exception as e:
    print(f"Error creating free space configuration: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

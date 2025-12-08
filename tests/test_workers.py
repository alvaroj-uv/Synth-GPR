
from dataclasses import dataclass
from typing import Optional
from src.workers import AirWorker, SubgradeWorker, FormationWorker, BallastWorker, RockWorker, FoulingWorker, AntennaWorker, AssemblerWorker
from src.worker import SceneCheckpoint
from src.work_order import WorkOrder, WorkOrderSystem

# Mock Config
@dataclass
class MockConfig:
    domain_x: float = 0.5   # Small domain for speed
    domain_y: float = 1.5
    domain_z: float = 0.005
    
    dx: float = 0.005
    dy: float = 0.005
    dz: float = 0.005
    time_window: float = 1.5e-8
    
    # Missing optional
    base_seed: Optional[int] = None
    
    tx_x: float = 0.10
    rx_x: float = 0.15
    tx_rx_y: float = 1.1
    tx_rx_z: float = 0.0025
    center_freq: float = 400e6
    
    max_ballast_thickness: float = 0.40
    rock_radius_min: float = 0.02
    rock_radius_max: float = 0.04
    formation_thickness: float = 0.10
    
    # Material Props needed by Warehouse
    bal_rock_eps: float = 5.0
    bal_rock_sigma: float = 0.001
    bal_foul_eps_min: float = 6.0
    bal_foul_eps_max: float = 8.0
    bal_foul_sigma_min: float = 0.002

print("Initializing Scene...")
scene = SceneCheckpoint(MockConfig())
# Initialize WorkOrder
wo_params = {
    'ballast_thickness': 0.40,
    'antenna_offset': 0.0,
    'pvc': 10.0,  # Test Fouling
    'moisture': 0.1
}
scene.work_order = WorkOrderSystem(WorkOrder("test-001", wo_params))

# Run Pipeline
workers = [
    AirWorker(),
    SubgradeWorker(),  # 0.5m
    FormationWorker(), # +0.10m = 0.60m
    BallastWorker(),   # +0.40m = 1.00m
    RockWorker(),      # Fills 0.60 - 1.00
    FoulingWorker(),   # Adds fines
    AntennaWorker(),   # Adds sources/receivers
    AssemblerWorker()  # Finalizes
]

for w in workers:
    print(f"Running {w.name}...")
    w.execute(scene, {}, {}, {})
    errors = w.quality_check(scene)
    if errors:
        print(f"❌ {w.name} Errors: {errors}")
    else:
        print(f"✅ {w.name} Passed")

# Verify Rocks
rock_count = scene.metadata.get('rock_count', 0)
if rock_count > 0:
    print(f"✅ RockGen Success: Placed {rock_count} rocks")
    # Verify bounds
    min_y = min(r.y for r in scene.rock_positions)
    max_y = max(r.y for r in scene.rock_positions)
    print(f"   - Rock Y Range: {min_y:.3f} - {max_y:.3f}")
    
    # Expected range: 0.60 to 1.00
    if min_y >= 0.60 and max_y <= 1.00:
        print("   - Bounds Valid")
    else:
        print("   ⚠️ Bounds Warning: Rocks might slightly exceed due to radius")
else:
    print("❌ RockGen Failed: No rocks")

# Verify Assembly
if scene.assembled:
    print("✅ Assembly Success")
    print(f"   - Total Geometry Commands: {len(scene.assembled.geometry_commands)}")
    print(f"   - Total Sources: {len(scene.assembled.source_commands)}")
    
    # Write to file
    from src.file_writer import GPRMaxFileWriter
    content = GPRMaxFileWriter.write_scene(scene.assembled, "Test Sanity")
    
    output_path = "test_output.in"
    with open(output_path, "w") as f:
        f.write(content)
        
    print(f"✅ Output written to {output_path}")
    print("   You can now run: python -m gprMax test_output.in")
    
else:
    print("❌ Assembly Failed")

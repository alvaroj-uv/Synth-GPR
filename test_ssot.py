from dataclasses import dataclass
from src.worker import SceneCheckpoint
from src.work_order import WorkOrder, WorkOrderSystem
from src.workers import BallastWorker, RockWorker
from src.gpr_commands import BoxCommand

# Mock Config
@dataclass
class MockConfig:
    max_ballast_thickness: float = 0.4
    rock_radius_min: float = 0.02
    rock_radius_max: float = 0.05
    domain_x: float = 1.0
    domain_z: float = 0.5
    
print("Initializing Single Source of Truth Test...")

# Setup WorkOrder
params = {"project_id": "TEST-SSOT", "ballast_thickness": 0.45}
wo = WorkOrder("WO-SSOT", params)
wo_sys = WorkOrderSystem(wo)
scene = SceneCheckpoint(config=MockConfig(), work_order=wo_sys)

# 1. Run BallastWorker
print("\n[Step 1] Running BallastWorker...")
ballast_worker = BallastWorker()
ballast_worker.execute(scene, params, None, None)

# Check WorkOrder outputs
if wo_sys.get('ballast_thickness') == 0.45:
    print("[PASS] BallastWorker wrote thickness to WorkOrder")
else:
    print(f"[FAIL] BallastWorker failed to write. Got: {wo_sys.get('ballast_thickness')}")

if wo_sys.get('ballast_top_y') is not None:
    print(f"[PASS] BallastWorker wrote top_y ({wo_sys.get('ballast_top_y')})")
else:
    print("[FAIL] BallastWorker did not write top_y")

# 2. Run RockWorker
print("\n[Step 2] Running RockWorker...")
# RockWorker needs to read ballast_top_y from WorkOrder
rock_worker = RockWorker()
# We expect RockWorker to succeed (no crash) and place rocks or at least try
# Since we don't have tools/strategy, it might fail inside, but we check if it READS the bounds.
# We can mock the tools if needed, but let's see if it crashes on 'No WorkOrder' or 'missing key'.
try:
    rock_worker.execute(scene, params, None, None)
    print("[PASS] RockWorker executed without WorkOrder error")
except Exception as e:
    print(f"[FAIL] RockWorker crashed: {e}")
    # If it crashes on tools/materials that's fine, as long as it's not "No WorkOrder"

# Check log for errors relating to WorkOrder
issues = wo_sys.export_issues()
print(f"\n[Audit] QC Issues Found: {len(issues)}")
for i in issues:
    print(f" - {i['worker']}: {i['description']}")

if not issues:
    print("[PASS] No QC issues logged")
else:
    print("[INFO] Issues present (check if expected)")

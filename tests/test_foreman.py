from dataclasses import dataclass
from src.worker import SceneCheckpoint
from src.work_order import WorkOrder, WorkOrderSystem
from src.workers import AssemblerWorker
from src.gpr_commands import BoxCommand

# Mock Config
@dataclass
class MockConfig:
    domain_x: float = 1.0
    domain_y: float = 1.0
    domain_z: float = 0.5
    tx_x: float = 0.5
    rx_x: float = 0.6
    tx_rx_z: float = 0.25

print("Initializing Foreman Test...")

# Case 1: Compliance
print("\n[Case 1] Testing Compliance (PVC=15 requested & delivered)...")
params_ok = {"project_id": "TEST-OK", "pvc": 15.0}
wo_sys_ok = WorkOrderSystem(WorkOrder("WO-OK", params_ok))
scene_ok = SceneCheckpoint(config=MockConfig(), work_order=wo_sys_ok)

# Manually add fouling geometry to simulate FoulingWorker success
scene_ok.add_geometry(BoxCommand(0,0,0,1,0.1,0.5, "bal_foul_granular"))

foreman = AssemblerWorker() # No args for Finalizer
# Run Assembly (New Requirement)
foreman.execute(scene_ok, {}, None, None)
errors = foreman.quality_check(scene_ok)
if not errors:
    print("[PASS] Compliant scene accepted")
else:
    print(f"[FAIL] Compliant scene rejected: {errors}")


# Case 2: Non-Compliance (PVC=20 requested, NO fouling in scene)
print("\n[Case 2] Testing Non-Compliance (PVC=20 requested but missing)...")
params_bad = {"project_id": "TEST-BAD", "pvc": 20.0}
wo_sys_bad = WorkOrderSystem(WorkOrder("WO-BAD", params_bad))
scene_bad = SceneCheckpoint(config=MockConfig(), work_order=wo_sys_bad)

# Add generic geometry but NO fouling
scene_bad.add_geometry(BoxCommand(0,0,0,1,1,0.5, "free_space"))

foreman.execute(scene_bad, {}, None, None)
errors_bad = foreman.quality_check(scene_bad)
expected_msg = "Foreman: WorkOrder requested PVC=20.0%, but no fouling material found."

found_expected = any(expected_msg in e for e in errors_bad)
if found_expected:
    print("[PASS] Non-compliant scene correctly flagged:")
    for e in errors_bad: print(f" - {e}")
else:
    print(f"[FAIL] Foreman failed to catch missing fouling. Errors: {errors_bad}")

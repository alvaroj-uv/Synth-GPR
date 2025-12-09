import sys
import os
import shutil
from pathlib import Path

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.work_order import WorkOrder, WorkOrderSystem

def test_serialization():
    print("[TEST] WorkOrder Serialization")
    
    # 1. Create Initial State
    wo = WorkOrder(id="test_001", params={"domain_x": 0.5, "pvc": 30.0})
    sys = WorkOrderSystem(wo)
    
    # Simulate Worker Activity
    sys.set("rock_count", 42, "RockWorker")
    sys.log_issue("FoulingWorker", "bad_geometry", "warning", "Fouling overlapping")
    sys.set("highest_rock_y", 0.35, "RockWorker")
    
    print(f"[INIT] Created system with {len(sys.export_history())} audit entries")
    
    # 2. Save
    output_dir = Path("test_output")
    output_dir.mkdir(exist_ok=True)
    json_path = output_dir / "work_order_dump.json"
    
    sys.save_to_file(str(json_path))
    print(f"[SAVE] Saved to {json_path}")
    
    # 3. Load
    loaded_sys = WorkOrderSystem.load_from_file(str(json_path))
    print(f"[LOAD] Loaded from file")
    
    # 4. Verify
    # Check Invariants
    assert loaded_sys.work_order.id == "test_001", "ID Mismatch"
    assert loaded_sys.work_order.get("pvc") == 30.0, "Param Mismatch"
    
    # Check Blackboard
    assert loaded_sys.get("rock_count") == 42, "Blackboard Mismatch"
    
    # Check Issues
    issues = loaded_sys.export_issues()
    assert len(issues) == 1, "Issue count mismatch"
    assert issues[0]["type"] == "bad_geometry", "Issue content mismatch"
    
    # Check Audit Log (complex)
    history = loaded_sys.export_history()
    # Initial INIT + 2 SETs + 1 QC + 1 QC Audit = 5 entries?
    # Let's count:
    # 1. INIT (System)
    # 2. SET rock_count (RockWorker)
    # 3. QC_WARNING bad_geometry (FoulingWorker) - log_issue does double log?
    #    Yes, log_issue appends to _issues AND calls _log_audit.
    # 4. SET highest_rock_y (RockWorker)
    
    assert len(history) >= 4, f"History length {len(history)} too short"
    print(f"[VERIFY] Audit history length: {len(history)}")
    
    # Clean up
    if output_dir.exists():
        shutil.rmtree(output_dir)
        
    print("[SUCCESS] Serialization verified!")

if __name__ == "__main__":
    try:
        test_serialization()
    except AssertionError as e:
        print(f"[FAIL] Assertion Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"[FAIL] Exception: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

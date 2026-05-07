
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.work_order import WorkOrder, WorkOrderSystem
from datetime import datetime
import contextlib
import io

def test_logging_timestamps():
    print("Testing Timestamps...")
    wo = WorkOrder(id="TEST_001")
    sys_wo = WorkOrderSystem(wo)
    
    # Capture stdout
    f = io.StringIO()
    with contextlib.redirect_stdout(f):
        sys_wo.log("Test standard log", "Tester")
        sys_wo.log_issue("Tester", "warning", "medium", "Test warning")
        
    output = f.getvalue()
    print("Captured Output:\n" + output)
    
    # Check for [HH:MM:SS] pattern
    # Regex validation or simple check
    passed = True
    for line in output.strip().split('\n'):
        if not line.startswith("["):
            print(f"FAIL: Line '{line}' does not start with timestamp bracket")
            passed = False
            continue
            
        parts = line.split(']')
        if len(parts) < 2:
             print(f"FAIL: Line '{line}' malformed")
             passed = False
             continue
             
        time_part = parts[0][1:]
        # Check simplified format H:M:S
        if len(time_part.split(':')) != 3:
             print(f"FAIL: Time part '{time_part}' not HH:MM:SS")
             passed = False
             
    if passed:
        print("SUCCESS: Timestamps verified.")
    else:
        sys.exit(1)

if __name__ == "__main__":
    test_logging_timestamps()

import os
import shutil
from src.production_line import ProductionLine
from src.work_order import WorkOrder, WorkOrderSystem
from src.config import GeneratorConfig

print("Initializing Production Line Integration Test...")

# 1. Setup Environment
output_dir = r"d:\Codigo\Synth-Data\Tests\FactoryTest"
if os.path.exists(output_dir):
    shutil.rmtree(output_dir)
os.makedirs(output_dir)

# 2. Setup Configuration
config = GeneratorConfig(
    domain_x=0.5,
    domain_y=1.5,
    domain_z=0.5,
    tx_x=0.25,
    rx_x=0.35,
    tx_rx_z=0.25
)
# config.generate_antenna_variants is likely not a field but handled by ProductionLine logic derived from logic? 
# Or if it is a field, add it to kwargs if it exists in GeneratorConfig definition.
# Checking GeneratorConfig definition... standard fields. 
# ProductionLine code uses `_get_variants(config)`.
# For now, I'll stick to geometry params. ProductionLine forces variants in `run` if logic dictates, 
# but currently `_get_variants` is hardcoded to return 1 variant (offset 0).
# If I want to test variants, I might need to hack `_get_variants` or just rely on default.

# 3. Setup WorkOrder
params = {
    "project_id": "PROD-TEST",
    "pvc": 15.0, # Request fouling
    "moisture": 10.0,
    "ballast_thickness": 0.4
}
wo = WorkOrder("PROD-TEST-001", params)
wo_sys = WorkOrderSystem(wo)

# 4. Initialize Production Line
pipeline = ProductionLine(config)

# 5. Run
print("\n[Step] Running Production Line...")
files = pipeline.run(wo_sys, output_dir)


print(f"\n[Result] Generated {len(files)} files.")
for f in files:
    print(f" - {f}")
    
    # DEBUG: Print content
    print(f"\n--- CONTENT OF {os.path.basename(f)} ---")
    with open(f, 'r') as file_handle:
        print(file_handle.read())
    print("-------------------------------------------\n")
    
# 6. Verification
if len(files) == 0:
    print("[FAIL] No files generated!")
    exit(1)

# Check Audit Log for success
history = wo_sys.export_history()
success_logs = [e for e in history if "Generated" in e['value']]
if success_logs:
    print(f"[PASS] Audit log confirms generation: {len(success_logs)}")
else:
    print("[FAIL] Audit log missing generation events")
    
# Check for issues
issues = wo_sys.export_issues()
errors = [i for i in issues if i['severity'] in ('error', 'critical')]
if errors:
    print(f"[FAIL] Critical/Error issues found: {len(errors)}")
    for e in errors:
        print(f" - {e['worker']}: {e['description']}")
else:
    print("[PASS] Clean run (no critical errors)")

# Check content of one file
with open(files[0], 'r') as f:
    content = f.read()
    if "#domain" in content and "#material" in content:
        print("[PASS] File content looks valid (headers found)")
    else:
        print("[FAIL] File content missing expected headers")

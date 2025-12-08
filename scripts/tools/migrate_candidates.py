import shutil
import sys
import subprocess
from pathlib import Path

ROOT_DIR = Path(r"d:\Codigo\Synth-GPR")
LEGACY_DIR = ROOT_DIR / "legacy"
REGRESSION_SCRIPT = ROOT_DIR / "scripts/tools/regression_check.py"

CANDIDATES = [
    "debug_pipeline.py",
    "run_pipeline.py",
    "generate_contrast_set.py"
    # Excluding __init__.py files as per safety decision
]

def run_regression():
    print("  -> Running Regression Check...")
    try:
        # Run regression_check.py using sys.executable
        subprocess.run(
            [sys.executable, str(REGRESSION_SCRIPT)], 
            cwd=ROOT_DIR, 
            check=True,
            stdout=subprocess.DEVNULL, # Keep output clean
            stderr=subprocess.PIPE
        )
        print("  -> PASSED")
        return True
    except subprocess.CalledProcessError:
        print("  -> FAILED")
        # print error if needed
        # print(e.stderr.decode())
        return False

def migrate():
    print("=== STARTING MIGRATION LOOP ===")
    LEGACY_DIR.mkdir(exist_ok=True)
    
    report = []
    
    for filename in CANDIDATES:
        src = ROOT_DIR / filename
        dst = LEGACY_DIR / filename
        
        if not src.exists():
            print(f"[SKIP] {filename} not found in root.")
            continue
            
        print(f"[MOVE] {filename} -> legacy/")
        try:
            shutil.move(src, dst)
        except Exception as e:
            print(f"  -> Error moving: {e}")
            continue
            
        if run_regression():
            print(f"[SUCCESS] {filename} migrated.")
            report.append(f"- [MIGRATED] {filename}")
        else:
            print(f"[ROLLBACK] {filename} caused regression. Moving back.")
            try:
                shutil.move(dst, src)
                report.append(f"- [ROLLED BACK] {filename}")
            except Exception as e:
                print(f"  -> CRITICAL: Failed to rollback {filename}: {e}")
                
    print("\n=== MIGRATION COMPLETE ===")
    print("\n".join(report))

if __name__ == "__main__":
    migrate()

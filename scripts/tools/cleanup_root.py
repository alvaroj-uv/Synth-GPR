import os
import shutil
from pathlib import Path

ROOT_DIR = Path(r"d:\Codigo\Synth-GPR")

# Targets
DOCS_REPORTS = ROOT_DIR / "docs" / "reports"
SCRIPTS_BATCH = ROOT_DIR / "scripts" / "batch"
LEGACY_CONFIGS = ROOT_DIR / "legacy" / "configs"
LEGACY_DIR = ROOT_DIR / "legacy"
TESTS_DIR = ROOT_DIR / "tests"

# Map file -> Destination Folder
MOVES = {
    # Documentation
    "API_MIGRATION.md": DOCS_REPORTS,
    "CLI_REFERENCE.md": DOCS_REPORTS,
    "CODEBASE_STRUCTURE.md": DOCS_REPORTS,
    "CODE_AUDIT_REPORT.md": DOCS_REPORTS,
    "FINAL_SYSTEM_SUMMARY.md": DOCS_REPORTS,
    "ML_PIPELINE_WORKFLOW.md": DOCS_REPORTS,
    "SMART_CONFIG_GUIDE.md": DOCS_REPORTS,
    "TEST_FILES_STATUS.md": DOCS_REPORTS,
    "vulture_report.txt": DOCS_REPORTS,
    
    # Legacy / Retired
    "repro_error.py": LEGACY_DIR,
    
    # Tests (Moved to tests/)
    "verify_400mhz.py": TESTS_DIR,
    "verify_refactor.py": TESTS_DIR,
    
    # Validation scripts -> Batch
    "clean_tests.bat": SCRIPTS_BATCH,
    "quick_test.bat": SCRIPTS_BATCH,
    "setup_tests.bat": SCRIPTS_BATCH,
    "test_pipeline.bat": SCRIPTS_BATCH,
    "test_randomization.bat": SCRIPTS_BATCH,
    "validate_tests.bat": SCRIPTS_BATCH,
    "visualize_all_test.bat": SCRIPTS_BATCH,

    # Configs
    "400MHz_full.ini": LEGACY_CONFIGS,
    "400MHz_production.ini": LEGACY_CONFIGS,
}

def cleanup():
    print("=== STARTING ROOT CLEANUP ===")
    
    # Ensure dirs exist
    for d in [DOCS_REPORTS, SCRIPTS_BATCH, LEGACY_CONFIGS, LEGACY_DIR, TESTS_DIR]:
        if d.exists() and not d.is_dir():
            print(f"[WARN] {d.name} exists as a FILE. Deleting to create directory.")
            os.remove(d)
        d.mkdir(parents=True, exist_ok=True)
        print(f"[DIR] Ensured: {d}")

    for filename, dest_dir in MOVES.items():
        src = ROOT_DIR / filename
        dst_path = dest_dir / filename
        
        if not src.exists():
            if dst_path.exists():
                print(f"[SKIP] Already moved: {filename}")
            else:
                print(f"[WARN] Source not found: {filename}")
            continue
            
        print(f"[MOVE] {filename} -> {dest_dir.name}/")
        try:
            # Overwrite if exists
            if dst_path.exists():
                os.remove(dst_path)
            shutil.move(str(src), str(dest_dir))
        except Exception as e:
            print(f"  -> FAILED: {e}")

    print("=== CLEANUP COMPLETE ===")

if __name__ == "__main__":
    cleanup()

import shutil
import subprocess
import sys
from pathlib import Path

# Paths
ROOT_DIR = Path(r"d:\Codigo\Synth-GPR")
TEST_OUTPUT = ROOT_DIR / "test_output_regression"

def run_command(cmd, cwd=ROOT_DIR):
    """Run a shell command and return success status."""
    # Use current python executable
    python_exe = sys.executable
    if cmd.startswith("python"):
        cmd = cmd.replace("python", f'"{python_exe}"', 1)
        
    print(f"[RUNNING] {cmd}")
    try:
        # Check output to ensure it doesn't hang
        result = subprocess.run(
            cmd, 
            cwd=cwd, 
            shell=True, 
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        return True
    except subprocess.CalledProcessError as e:
        print(f"[FAILED] Command: {cmd}")
        print(f"Error: {e.stderr}")
        return False

def check_file(path_str):
    p = Path(path_str)
    if p.exists():
        print(f"[OK] Found {p.name}")
        return True
    else:
        print(f"[FAIL] Missing {p.name}")
        return False

def main():
    print("=== STARTING REGRESSION CHECK ===")
    
    # 1. Clean previous data
    if TEST_OUTPUT.exists():
        shutil.rmtree(TEST_OUTPUT)
    
    # 2. Generation (Active Core Script)
    # Generate 2 samples
    cmd_gen = f"python generate_balanced_dataset.py -n 2 -o {TEST_OUTPUT}"
    if not run_command(cmd_gen):
        return False
        
    # Find timestamped folder
    subdirs = [d for d in TEST_OUTPUT.iterdir() if d.is_dir()]
    if not subdirs:
        print("[FAIL] No output directory created.")
        return False
    dataset_dir = subdirs[0]
    print(f"Dataset Dir: {dataset_dir}")
    
    # 3. Simulate (using the generated batch file or direct logic)
    # We prefer using the batch file to test that too, but Python calling batch 
    # can be flaky with envs. Let's run the idempotent batch file logic directly or call it.
    # The batch file assumes python in path.
    batch_file = dataset_dir / "run_simulations.bat"
    if not batch_file.exists():
        print("[FAIL] run_simulations.bat not created.")
        return False
        
    # Call batch
    if not run_command(str(batch_file), cwd=dataset_dir):
        return False
        
    # 4. Extract Features
    # Checks inputs and produces output
    extract_batch = dataset_dir / "extract_features.bat"
    if not extract_batch.exists():
        # It's not created by generator? Ah, I created it manually in previous steps?
        # create_feature_dataset.py expects to define it?
        # Note: The *user* instruction created `extract_features.bat` in the output dir.
        # But `generate_balanced_dataset.py` does NOT create it automatically yet.
        # So we must call `create_feature_dataset.py` directly here.
        pass
        
    cmd_extract = f"python create_feature_dataset.py {dataset_dir}"
    if not run_command(cmd_extract):
        return False
        
    # 5. Validation
    # Check for .in, .out, metadata.csv, features.csv
    # Sample names are global IDs. 
    # With 2 samples (Class C and MC), IDs might be 0 and 2 (if n=2).
    # Logic in `generate_balanced_dataset.py`: global_id = (cls_idx * n_samples) + i
    # C=0, MC=1.
    
    # Check any .out file
    out_files = list(dataset_dir.glob("*.out"))
    if not out_files:
        print("[FAIL] No .out files generated.")
        return False
        
    if not check_file(dataset_dir / "metadata.csv"):
        return False
        
    if not check_file(dataset_dir / "features.csv"):
        return False
        
    print("=== REGRESSION CHECK PASSED ===")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

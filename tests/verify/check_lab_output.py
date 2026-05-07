
import os
import glob
import sys

def check_lab_fi(output_dir):
    files = glob.glob(os.path.join(output_dir, "*.in"))
    if not files:
        print(f"No .in files found in {output_dir}")
        return False
        
    print(f"Found {len(files)} generated files.")
    
    success_count = 0
    for fpath in files:
        with open(fpath, 'r') as f:
            content = f.read()
            
        if "Lab_FI" in content:
            # Extract value line
            for line in content.splitlines():
                if "Lab_FI" in line:
                    print(f"[OK] {os.path.basename(fpath)} -> {line.strip()}")
            success_count += 1
        else:
            print(f"[FAIL] {os.path.basename(fpath)} missing Lab_FI")
            
    return success_count == len(files)

if __name__ == "__main__":
    # Default to test pipeline output
    output_dir = r"D:\Codigo\Synth-GPR\test_pipeline_output"
    if len(sys.argv) > 1:
        output_dir = sys.argv[1]
        
    if check_lab_fi(output_dir):
        print("All files contain Lab_FI metadata.")
        sys.exit(0)
    else:
        print("Some files missing Lab_FI metadata.")
        sys.exit(1)

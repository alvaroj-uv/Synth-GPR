import os
import glob
import subprocess
import argparse
import time
from pathlib import Path

import concurrent.futures

def run_single_simulation(args):
    """Worker for parallel execution"""
    f, n_gpu = args
    cmd = [sys.executable, "-m", "gprMax", str(f), "-n", "1"]
    if n_gpu is not None and n_gpu >= 0:
        cmd.extend(["-gpu", str(n_gpu)])
        
    try:
        # Run simulation
        # Use capture_output=True to suppress stdout unless error
        subprocess.run(cmd, check=True, capture_output=True)
        print(f"  [Done] {f.name}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"  [Error] {f.name}: {e}")
        return False

def run_batch_simulations(input_folder, n_gpu=0, jobs=4):
    """
    Run gprMax on all .in files in a folder.
    """
    input_folder = Path(input_folder)
    in_files = sorted(list(input_folder.glob("*.in")))
    
    if not in_files:
        print(f"No .in files found in {input_folder}")
        return

    print(f"Found {len(in_files)} input files. Running with {jobs} threads.")
    
    start_total = time.time()
    
    # Filter files that need running
    files_to_run = []
    for f in in_files:
        out_file = f.with_suffix('.out')
        if out_file.exists():
             # print(f"  Output exists, skipping: {out_file.name}")
             pass
        else:
             files_to_run.append((f, n_gpu))
             
    print(f"Simulations to run: {len(files_to_run)}")
    
    if not files_to_run:
        print("Nothing to do.")
        return

    # Run in parallel
    with concurrent.futures.ThreadPoolExecutor(max_workers=jobs) as executor:
        results = list(executor.map(run_single_simulation, files_to_run))
    
    duration = time.time() - start_total
    print(f"\nBatch completed in {duration:.2f} seconds.")

if __name__ == "__main__":
    import sys
    # Use the current python executable to ensure we use the same environment
    
    parser = argparse.ArgumentParser(description="Run gprMax simulations in batch.")
    parser.add_argument("input_folder", help="Folder containing .in files")
    parser.add_argument("-j", "--jobs", type=int, default=4, help="Number of parallel jobs")
    parser.add_argument("--gpu", nargs='+', type=int, help="GPU Device IDs to use (e.g. 0)")
    
    args = parser.parse_args()
    
    # If gpu provided, use those IDs. If not, n_gpu=0 (default cpu)
    # run_batch_simulations expects n_gpu to be passed. 
    # Logic in run_single_simulation handles 'n_gpu' as an argument to -gpu flag
    # If we want to use specific IDs, we need to adapt run_single_simulation too.
    # For now, let's assume if --gpu is passed, we pass the first ID or list.
    
    gpu_arg = -1
    if args.gpu:
        # If user passed --gpu 0, args.gpu is [0]
        # function run_single_simulation uses: cmd.extend(["-gpu", str(n_gpu)])
        # so we should pass the ID directly.
        # Limitation: run_single_simulation only takes one ID currently or integer count?
        # Let's trust gprMax syntax: -gpu <id>
        gpu_arg = args.gpu[0] 
    
    run_batch_simulations(args.input_folder, n_gpu=gpu_arg, jobs=args.jobs)

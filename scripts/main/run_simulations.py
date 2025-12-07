#!/usr/bin/env python3
"""
Batch runner for gprMax simulations.

Finds all .in files in the specified directory and runs them using the gprMax module.
Supports CUDA GPU acceleration.
"""
import sys
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
        subprocess.run(cmd, check=True, capture_output=True)
        print(f"  [Done] {f.name}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"  [Error] {f.name}: {e}")
        return False

def run_batch_simulations(input_folder, n_gpu=-1, n_jobs=4):
    """
    Run gprMax on all .in files in a folder.
    """
    input_folder = Path(input_folder)
    in_files = sorted(list(input_folder.glob("*.in")))
    
    if not in_files:
        print(f"No .in files found in {input_folder}")
        return

    print(f"Found {len(in_files)} input files. Running with {n_jobs} threads.")
    
    start_total = time.time()
    
    # Filter files that need running
    files_to_run = []
    for f in in_files:
        out_file = f.with_suffix('.out')
        if not out_file.exists():
            files_to_run.append((f, n_gpu))
             
    print(f"Simulations to run: {len(files_to_run)}")
    
    if not files_to_run:
        print("Nothing to do.")
        return

    # Run in parallel
    with concurrent.futures.ThreadPoolExecutor(max_workers=n_jobs) as executor:
        results = list(executor.map(run_single_simulation, files_to_run))
    
    duration = time.time() - start_total
    print(f"\nBatch completed in {duration:.2f} seconds.")

if __name__ == "__main__":
    # Add src to path
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))
    from src.config import GeneratorConfig
    
    # Determine script name for default INI file
    script_name = Path(__file__).stem
    default_ini = f"{script_name}.ini"
    
    # Check if default INI file exists or explicit INI provided
    use_ini = False
    config_file = None
    
    # Priority 1: Explicit INI file argument
    if len(sys.argv) >= 2 and sys.argv[1].endswith('.ini'):
        config_file = sys.argv[1]
        use_ini = True
    # Priority 2: Default INI file in current directory
    elif Path(default_ini).exists():
        config_file = default_ini
        use_ini = True
        print(f"Found default config: {default_ini}")
    
    # Use INI configuration if available
    if use_ini:
        try:
            config = GeneratorConfig.from_ini(config_file)
            
            print(f"Loaded configuration from: {config_file}")
            print(f"Input folder: {config.output_dir}")
            print(f"Number of jobs: {config.num_jobs}")
            print()
            
            # Run simulations using config parameters
            run_batch_simulations(
                input_folder=config.output_dir,
                n_jobs=config.num_jobs,
                n_gpu=-1 if not config.gpu_devices else config.gpu_devices[0]
            )
        except FileNotFoundError:
            print(f"Error: Config file not found: {config_file}")
            sys.exit(1)
        except Exception as e:
            print(f"Error loading config: {e}")
            sys.exit(1)
    
    # Fall back to command-line arguments
    else:
        print(f"No INI file found. Using command-line arguments.")
        print(f"(Tip: Create '{default_ini}' for easier configuration)")
        print()
        
        parser = argparse.ArgumentParser(
            description="Run gprMax simulations in batch.",
            epilog=f"Alternatively, create a '{default_ini}' file with [workflow] section."
        )
        parser.add_argument("input_folder", help="Folder containing .in files")
        parser.add_argument("-j", "--jobs", type=int, default=4, help="Number of parallel jobs")
        parser.add_argument("--gpu", nargs='+', type=int, help="GPU Device IDs to use (e.g. 0)")
        
        args = parser.parse_args()
        
        gpu_arg = -1
        if args.gpu:
            gpu_arg = args.gpu[0]
        
        run_batch_simulations(args.input_folder, n_jobs=args.jobs, n_gpu=gpu_arg)

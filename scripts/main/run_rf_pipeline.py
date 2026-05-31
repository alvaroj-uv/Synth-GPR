#!/usr/bin/env python3
"""
Run the full RF training pipeline: build parquet + train model.

Usage:
    python scripts/main/run_rf_pipeline.py [options]

Options:
    --skip-build       Skip parquet build if output already exists
    --dirs DIR1 DIR2   Specify dataset directories (default: gpr_dataset_10k dataset_variants)
    --parquet PATH     Path to parquet file (default: output/dataset_80k_features.parquet)
    --model-out PATH   Path for trained model (default: output/rf_model_80k.joblib)
    --report PATH      Path for report (default: output/rf_results_80k.txt)
"""

import sys
import subprocess
from pathlib import Path
import argparse


def run_command(cmd, description):
    """Run a subprocess command with nice error handling."""
    print(f"\n{'='*80}")
    print(f"Step: {description}")
    print(f"{'='*80}\n")
    print(f"Command: {' '.join(cmd)}\n")

    result = subprocess.run(cmd, check=False)
    if result.returncode != 0:
        print(f"\nERROR: {description} failed with exit code {result.returncode}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="RF training pipeline: build parquet + train model"
    )
    parser.add_argument("--skip-build", action="store_true",
                       help="Skip parquet build if it already exists")
    parser.add_argument("--dirs", nargs="+", default=None,
                       help="Dataset directories")
    parser.add_argument("--parquet", default="output/dataset_80k_features.parquet",
                       help="Output parquet path")
    parser.add_argument("--model-out", default="output/rf_model_80k.joblib",
                       help="Output model path")
    parser.add_argument("--report", default="output/rf_results_80k.txt",
                       help="Output report path")
    args = parser.parse_args()

    parquet_path = Path(args.parquet)
    skip_build = args.skip_build and parquet_path.exists()

    print(f"\n{'='*80}")
    print("RF TRAINING PIPELINE")
    print(f"{'='*80}")
    print(f"Parquet    : {args.parquet}")
    print(f"Model out  : {args.model_out}")
    print(f"Report out : {args.report}")
    print(f"Skip build : {skip_build}")

    # Stage 1: Build parquet
    if not skip_build:
        cmd = ["python", "scripts/main/build_parquet_merged.py",
               "--output", args.parquet]
        if args.dirs:
            cmd.extend(["--dirs"] + args.dirs)
        run_command(cmd, "Build parquet dataset")
    else:
        print(f"\nSkipping parquet build (file exists: {args.parquet})")

    # Stage 2: Train RF
    cmd = ["python", "scripts/main/train_rf.py",
           "--parquet", args.parquet,
           "--model-out", args.model_out,
           "--report", args.report]
    run_command(cmd, "Train Random Forest model")

    print(f"\n{'='*80}")
    print("PIPELINE COMPLETE")
    print(f"{'='*80}")
    print(f"Model saved  : {args.model_out}")
    print(f"Report saved : {args.report}")
    print(f"\nTo view results:")
    print(f"  cat {args.report}")


if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
    main()

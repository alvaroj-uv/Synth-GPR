#!/usr/bin/env python3
"""
Generate .in from TOML and organize files together.
Ensures TOML, IN, PNG, and OUT files stay in the same folder.
"""

import sys
from pathlib import Path
import argparse
import subprocess
import shutil

sys.path.insert(0, str(Path(__file__).parent.parent))


def generate_in_from_toml(toml_path: Path, output_dir: Path = None) -> Path:
    """
    Generate .in file from TOML using generate_in_files.py.
    Returns path to generated .in file.
    """
    toml_path = Path(toml_path)

    if not toml_path.exists():
        raise FileNotFoundError(f"TOML not found: {toml_path}")

    # Determine output directory
    if output_dir is None:
        output_dir = toml_path.parent
    else:
        output_dir = Path(output_dir)

    output_dir.mkdir(parents=True, exist_ok=True)
    in_path = output_dir / toml_path.with_suffix('.in').name

    print(f"[GEN]  {toml_path.name:<45}", end=" ", flush=True)

    try:
        result = subprocess.run(
            [
                sys.executable,
                "scripts/pipeline/generate_in_files.py",
                str(toml_path),
                "-o", str(in_path)
            ],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=str(toml_path.parent.parent.parent) if toml_path.parent.parent.parent.exists() else None
        )

        if result.returncode == 0 and in_path.exists():
            print(f"→ {in_path.name:<30} [OK]")
            return in_path
        else:
            print(f"[FAIL]")
            if result.stderr:
                print(f"      Error: {result.stderr[:150]}")
            return None

    except Exception as e:
        print(f"[ERROR] {str(e)[:80]}")
        return None


def organize_files(toml_path: Path, in_path: Path) -> None:
    """
    Organize files: copy TOML next to IN file.
    Both will be in the same directory.
    """
    toml_path = Path(toml_path)
    in_path = Path(in_path)

    if not in_path.exists():
        return

    # Copy TOML to same directory as IN
    target_toml = in_path.parent / toml_path.name

    if target_toml != toml_path:
        try:
            shutil.copy2(toml_path, target_toml)
            print(f"[ORG]  Copied TOML: {in_path.parent.name}/{target_toml.name}")
        except Exception as e:
            print(f"[WARN] Could not copy TOML: {str(e)[:80]}")


def main():
    ap = argparse.ArgumentParser(
        description="Generate .in from TOML and organize files in same folder",
        epilog="""
Examples:
  # Single file (output in same dir as TOML)
  python scripts/generate_and_organize.py output_test/ballast_eps51_antenna_30cm.toml

  # Batch files (output in specified dir)
  python scripts/generate_and_organize.py "output_test/ballast_epsilon_sweep_50ns/*.toml" -o output_test/organized/

  # Output to source directory (keep TOML and IN together)
  python scripts/generate_and_organize.py example.toml
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    ap.add_argument("input", type=str, help="Input TOML file(s) (glob pattern supported)")
    ap.add_argument("-o", "--output", type=Path, default=None, help="Output directory for .in files")

    args = ap.parse_args()

    # Find TOML files
    input_pattern = Path(args.input)
    if "*" in str(input_pattern) or "?" in str(input_pattern):
        parent = Path(input_pattern.parts[0])
        pattern = str(input_pattern.relative_to(parent)) if len(input_pattern.parts) > 1 else str(input_pattern)
        toml_files = list(parent.glob(pattern))
        if not toml_files:
            print(f"[ERR] No files match: {args.input}")
            return 1
    else:
        toml_path = Path(args.input)
        toml_files = [toml_path] if toml_path.exists() else []
        if not toml_files:
            print(f"[ERR] File not found: {args.input}")
            return 1

    toml_files = sorted(toml_files)
    out_dir = Path(args.output) if args.output else None

    print(f"\n{'='*90}")
    print(f"GENERATE .IN FROM TOML & ORGANIZE FILES")
    print(f"{'='*90}\n")

    print(f"Input files: {len(toml_files)}")
    if args.output:
        print(f"Output directory: {args.output}\n")
    else:
        print(f"Output directory: (same as TOML source)\n")

    generated = []
    failed = []

    for toml_path in toml_files:
        in_path = generate_in_from_toml(toml_path, output_dir=out_dir)

        if in_path:
            organize_files(toml_path, in_path)
            generated.append((toml_path, in_path))
        else:
            failed.append(toml_path)

    # Summary
    print(f"\n{'='*90}")
    print(f"SUMMARY")
    print(f"{'='*90}")
    print(f"Generated: {len(generated)} .in file(s)")
    print(f"Failed: {len(failed)}")

    if generated:
        print(f"\nGenerated files (TOML + IN together):")
        for toml, in_f in generated:
            print(f"  {in_f.parent.name}/")
            print(f"    - {toml.name}")
            print(f"    - {in_f.name}")

    if failed:
        print(f"\nFailed:")
        for f in failed:
            print(f"  {f}")

    print(f"{'='*90}\n")

    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main())

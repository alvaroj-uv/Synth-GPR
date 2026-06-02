#!/usr/bin/env python3
"""
Add Lab_LDCP_FI_est to dataset_variants .in files where missing.

Formula: Lab_LDCP_FI_est = Lab_LDCP_FH / 1.5 (Rojas-Vivanco 2025 eq. 9, clay fouling)

Usage:
    python scripts/main/add_ldcp_fi_est.py [--dir PATH]
"""

import sys
import re
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from src.physics import fi_from_fouling_height


def add_ldcp_fi_est(in_path: Path) -> bool:
    """Add Lab_LDCP_FI_est to .in file if missing. Returns True if modified."""
    try:
        with open(in_path, encoding="utf-8", errors="ignore") as f:
            content = f.read()

        # Check if Lab_LDCP_FI_est already exists
        if "Lab_LDCP_FI_est:" in content:
            return False

        # Extract Lab_LDCP_FH value
        match = re.search(r"## Lab_LDCP_FH:\s*([\d.]+)", content)
        if not match:
            return False

        fh_value = float(match.group(1))
        # Rojas-Vivanco 2025 quadratic (matches the real-data labeling), compaction
        # curve picked by ballast porosity from the header. Replaces linear FH/1.5.
        por_match = re.search(r"## porosity:\s*([\d.]+)", content)
        porosity = float(por_match.group(1)) if por_match else None
        fi_est_value = round(fi_from_fouling_height(fh_value, porosity), 2)

        # Insert Lab_LDCP_FI_est after Lab_LDCP_FH
        new_line = f"## Lab_LDCP_FI_est: {fi_est_value}\n"
        new_content = re.sub(
            r"(## Lab_LDCP_FH:\s*[\d.]+\n)",
            r"\1" + new_line,
            content
        )

        with open(in_path, "w", encoding="utf-8") as f:
            f.write(new_content)

        return True
    except Exception as e:
        print(f"[ERROR] {in_path.name}: {e}")
        return False


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Add Lab_LDCP_FI_est to .in files")
    parser.add_argument("--dir", default="output/dataset_variants",
                       help="Directory containing .in files")
    args = parser.parse_args()

    data_dir = Path(args.dir)
    if not data_dir.exists():
        print(f"ERROR: {data_dir} not found")
        sys.exit(1)

    in_files = sorted(data_dir.glob("s_*.in"))
    print(f"Processing {len(in_files)} .in files in {data_dir}")

    modified = 0
    skipped = 0
    errors = 0

    for in_path in in_files:
        if add_ldcp_fi_est(in_path):
            modified += 1
            if modified % 1000 == 0:
                print(f"  Modified {modified}...")
        elif "Lab_LDCP_FI_est:" in open(in_path).read():
            skipped += 1
        else:
            errors += 1

    print(f"\nDone:")
    print(f"  Modified: {modified}")
    print(f"  Skipped:  {skipped} (already had Lab_LDCP_FI_est)")
    print(f"  Errors:   {errors}")


if __name__ == "__main__":
    main()

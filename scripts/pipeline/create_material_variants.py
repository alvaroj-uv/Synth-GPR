#!/usr/bin/env python3
"""
Create N variants of a base .in file by replacing only material permittivities.

Rocks and geometry are preserved exactly. Only #material lines are rewritten.
This allows sweeping material parameters while keeping the same physics scene.

Usage:
    python create_material_variants.py base.in output_dir/ [--sets 10]
"""

import argparse
import json
import re
import sys
from pathlib import Path

# 10 physically meaningful parameter sets spanning clean -> highly fouled -> wet
# Based on:
#   Tosti & Benedetto (2018) NDT&E Int. — clean ballast
#   Benedetto et al. (2017) Constr.Build.Mater. — fouled ballast
#   Shang et al. (2021) Sensors PMC8539047 — fully fouled
#   PMC9003199 (2022) review — subgrade
PARAMETER_SETS = [
    # (label,       clean_ballast,  fouled_ballast,  hf_ballast,  subgrade_soil)
    # (name,        (eps, sigma),   (eps, sigma),    (eps, sigma), (eps, sigma))
    ("dry_clean",       (3.5, 0.001), (4.5, 0.004), (6.0, 0.010), (7.0, 0.015)),
    ("nominal_clean",   (4.0, 0.001), (5.0, 0.005), (6.5, 0.012), (8.0, 0.020)),
    ("moist_clean",     (4.5, 0.002), (5.5, 0.006), (7.0, 0.014), (9.0, 0.025)),
    ("light_fouling",   (4.2, 0.002), (5.2, 0.007), (6.8, 0.013), (8.5, 0.022)),
    ("mod_fouling",     (4.5, 0.003), (5.5, 0.008), (7.5, 0.016), (9.5, 0.028)),
    ("heavy_fouling",   (4.8, 0.004), (6.0, 0.010), (8.0, 0.018), (10.0, 0.030)),
    ("wet_fouling",     (5.0, 0.005), (6.5, 0.012), (9.0, 0.022), (11.0, 0.035)),
    ("saturated",       (5.5, 0.006), (7.0, 0.015), (10.0, 0.025), (12.0, 0.040)),
    ("clay_dominated",  (4.3, 0.003), (5.8, 0.010), (8.5, 0.020), (13.0, 0.045)),
    ("extreme_wet",     (6.0, 0.008), (8.0, 0.018), (11.0, 0.030), (15.0, 0.055)),
]

MATERIAL_NAMES = ["clean_ballast", "fouled_ballast", "highly_fouled_ballast", "subgrade_soil"]


def rewrite_materials(in_content: str, eps_sigma_map: dict) -> str:
    """
    Replace #material lines in .in content for named materials.
    Format: #material: eps sigma mu mag_loss name
    All other lines (geometry, antenna, time, etc.) are preserved verbatim.
    """
    lines = in_content.splitlines(keepends=True)
    result = []
    for line in lines:
        if line.startswith("#material:"):
            parts = line.split()
            if len(parts) >= 6:
                name = parts[5]
                if name in eps_sigma_map:
                    eps, sigma = eps_sigma_map[name]
                    result.append(f"#material: {eps:.4f} {sigma:.5f} 1.0 0.0 {name}\n")
                    continue
        result.append(line)
    return "".join(result)


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("base_in",    type=Path, help="Base .in file with rocks")
    parser.add_argument("output_dir", type=Path, help="Output directory for variants")
    parser.add_argument("--sets", type=int, default=10,
                        help="Number of parameter sets to generate (max 10, default: 10)")
    args = parser.parse_args()

    if not args.base_in.exists():
        print(f"ERROR: {args.base_in} not found")
        sys.exit(1)

    args.output_dir.mkdir(parents=True, exist_ok=True)
    base_content = args.base_in.read_text(encoding="utf-8")
    n_sets = min(args.sets, len(PARAMETER_SETS))

    manifest = []
    print(f"Creating {n_sets} material variants from: {args.base_in.name}")
    print()

    for i, (label, *props) in enumerate(PARAMETER_SETS[:n_sets], 1):
        eps_sigma_map = {name: val for name, val in zip(MATERIAL_NAMES, props)}

        variant_content = rewrite_materials(base_content, eps_sigma_map)
        out_path = args.output_dir / f"variant_{i:02d}_{label}.in"
        out_path.write_text(variant_content, encoding="utf-8")

        manifest.append({
            "index":  i,
            "label":  label,
            "in_file": str(out_path),
            "materials": {
                name: {"epsilon_r": eps, "sigma": sig}
                for name, (eps, sig) in zip(MATERIAL_NAMES, props)
            }
        })

        print(f"  [{i:02d}] {label}")
        for name, (eps, sig) in zip(MATERIAL_NAMES, props):
            print(f"         {name:25s}: eps={eps:.1f}  sigma={sig:.4f}")
        print()

    manifest_path = args.output_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"Manifest written: {manifest_path}")
    print(f"Total variants: {n_sets}")


if __name__ == "__main__":
    main()

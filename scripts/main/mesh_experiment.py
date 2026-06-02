#!/usr/bin/env python3
"""
Mesh-resolution experiment: regenerate a few scenes at different dx to test
whether a finer mesh recovers the fouling frequency-signature.

Takes existing .in files and rewrites ONLY the mesh lines (#domain, #dx_dy_dz,
and the z-extent which equals dx for 2D), leaving all geometry (physical-metre
coordinates) untouched — gprMax re-discretizes the same scene on the new grid.

Outputs <stem>_dx<NN>.in for each requested dx. Run these through gprMax and
return the .out files; then compare frequency features per mesh.

Usage:
    python scripts/main/mesh_experiment.py
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
SRC_DIR = ROOT / "output" / "gpr_synth_dataset_80k"
OUT_DIR = Path(r"D:\gprMax\user_models\mesh_experiment")

# Base scenes spanning the FI range (clean / moderate / highly fouled)
SCENES = {35000: "C", 56877: "MF", 4867: "HF"}
# Mesh sizes to test (metres): current, GPR-standard, fine
DX_VALUES = [0.0132, 0.0079, 0.0050]


def rewrite_mesh(content: str, dx: float) -> str:
    """Rewrite #domain z, #dx_dy_dz, and every box/cylinder z2 (=old dx) to new dx.

    Geometry x,y stay in metres; only the 2D z-thickness (one cell) tracks dx.
    """
    # old dx from the file
    m = re.search(r"#dx_dy_dz:\s*([\d.eE+-]+)", content)
    old_dx = float(m.group(1))

    def fmt(v):
        return f"{v:.6g}"

    # #dx_dy_dz
    content = re.sub(r"#dx_dy_dz:\s*[\d.eE+-]+ [\d.eE+-]+ [\d.eE+-]+",
                     f"#dx_dy_dz: {fmt(dx)} {fmt(dx)} {fmt(dx)}", content)
    # #domain: x y z  -> z becomes dx
    content = re.sub(r"(#domain:\s*[\d.eE+-]+ [\d.eE+-]+ )[\d.eE+-]+",
                     rf"\g<1>{fmt(dx)}", content)
    # z-extent in geometry: any coordinate equal to old_dx (the 2D thickness)
    # appears as the z2 of boxes/cylinders/sources. Replace the literal token.
    old_tok = fmt(old_dx)
    content = content.replace(f" {old_tok}\n", f" {fmt(dx)}\n")
    content = content.replace(f" {old_tok} ", f" {fmt(dx)} ")

    # CRITICAL: source/rx z must sit inside the single z-cell [0, dx]. The
    # original used z=old_dx/2 (cell centre). Move them to the NEW cell centre,
    # else with a smaller dx the old z falls OUTSIDE the domain -> empty trace.
    new_z = fmt(dx / 2.0)
    content = re.sub(r"(#hertzian_dipole:\s*\w+ [\d.eE+-]+ [\d.eE+-]+ )[\d.eE+-]+",
                     rf"\g<1>{new_z}", content)
    content = re.sub(r"(#rx:\s*[\d.eE+-]+ [\d.eE+-]+ )[\d.eE+-]+",
                     rf"\g<1>{new_z}", content)
    return content


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    made = []
    for sid, cls in SCENES.items():
        src = SRC_DIR / f"s_{sid:05d}.in"
        if not src.exists():
            print(f"  missing {src}")
            continue
        base = src.read_text(encoding="utf-8", errors="ignore")
        for dx in DX_VALUES:
            new = rewrite_mesh(base, dx)
            tag = f"dx{int(round(dx*10000)):03d}"  # e.g. 0.0132 -> 132
            out = OUT_DIR / f"s_{sid:05d}_{cls}_{tag}.in"
            out.write_text(new, encoding="utf-8")
            made.append(out.name)

    print(f"Wrote {len(made)} .in files to {OUT_DIR}")
    for n in made:
        print("  ", n)
    print("\nRun each through gprMax (2D), e.g.:")
    print("  python -m gprMax <file>.in")
    print("Then return the .out files in the same folder for comparison.")


if __name__ == "__main__":
    main()

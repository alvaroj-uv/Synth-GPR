#!/usr/bin/env python3
"""
Homogeneous-medium experiment: does the fouling frequency-signature flip SIGN
when the ballast is an EFFECTIVE MEDIUM (no explicit rocks) instead of explicit
scatterers?

Hypothesis (from physics analysis): with explicit rocks, increasing fouling
raises bulk eps -> shorter wavelength -> rocks scatter HIGH freqs more -> peak
freq DROPS (synthetic gives HF−C = −63 MHz). Real fouling (effective medium)
is dominated by dielectric loss -> peak freq RISES. If we replace rocks+fouling
with one homogeneous CRIM box, the sign should flip to match real.

For each base scene we keep domain / source / rx / subgrade / formation, but
replace the whole ballast layer with a single #box of the CRIM-effective eps,
sigma computed from the scene's rock/fouling/void fractions.

Outputs to D:\\gprMax\\user_models\\homogeneous_experiment.

Usage:
    python scripts/main/homogeneous_experiment.py
"""

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from src.physics import crim_bulk_eps

SRC_DIR = Path(r"D:\gprMax\user_models\mesh_experiment")
OUT_DIR = Path(r"D:\gprMax\user_models\homogeneous_experiment")

SCENES = {35000: "C", 56877: "MF", 4867: "HF"}

EPS_ROCK = 5.0      # bal_rock
SIG_ROCK = 0.001


def parse(content, key):
    m = re.search(rf"^## {key}:\s*([-\d.eE+]+)", content, re.MULTILINE)
    return float(m.group(1)) if m else None


def fouling_props(content):
    """eps, sigma of the bal_foul material in this scene."""
    m = re.search(r"^#material:\s*([\d.eE+-]+)\s+([\d.eE+-]+).*bal_foul", content, re.MULTILINE)
    return (float(m.group(1)), float(m.group(2))) if m else (5.0, 0.01)


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    made = []
    for sid, cls in SCENES.items():
        src = SRC_DIR / f"s_{sid:05d}_{cls}_dx132.in"
        if not src.exists():
            print(f"  missing {src}"); continue
        content = src.read_text(encoding="utf-8", errors="ignore")

        # ballast-layer phase fractions (renormalize rock+fouling+void to 1)
        fr = parse(content, "mc_rock_fraction") or 0.0
        ff = parse(content, "mc_fouling_fraction") or 0.0
        fv = parse(content, "mc_void_fraction") or 0.0
        tot = fr + ff + fv
        if tot <= 0:
            print(f"  [warn] zero fractions in {src.name}"); continue
        vr, vf, va = fr / tot, ff / tot, fv / tot

        eps_f, sig_f = fouling_props(content)

        # CRIM effective permittivity of the ballast (rock + fouling + air voids)
        eps_eff = crim_bulk_eps(
            v_rock=vr, eps_rock=EPS_ROCK,
            v_fines=vf, eps_fines=eps_f,
            v_water=0.0, eps_water=1.0,
            v_air=va,
        )
        # volume-weighted conductivity (rock + fouling; air/void ~0)
        sig_eff = round(vr * SIG_ROCK + vf * sig_f, 6)
        eps_eff = round(eps_eff, 4)

        bb = parse(content, "ballast_bottom_y")
        bt = parse(content, "ballast_top_y")
        dom = re.search(r"#domain:\s*([\d.eE+-]+) ([\d.eE+-]+) ([\d.eE+-]+)", content)
        dx_x, dz = dom.group(1), dom.group(3)

        # Build the homogeneous .in: strip all box/cylinder/triangle geometry,
        # keep headers/domain/dx/time/waveform/src/rx/materials, then re-add
        # subgrade+formation+a single homogeneous ballast box.
        lines = content.splitlines()
        kept = [ln for ln in lines
                if not ln.startswith(("#box:", "#cylinder:", "#triangle:", "#edge:", "#plate:"))]
        body = "\n".join(kept)

        homog_mat = f"#material: {eps_eff} {sig_eff} 1 0.0 ballast_eff"
        geom = (
            f"#box: 0.0 0.0 0.0 {dx_x} 0.2 {dz} subgrade\n"
            f"#box: 0.0 0.2 0.0 {dx_x} {bb} {dz} formation\n"
            f"#box: 0.0 {bb} 0.0 {dx_x} {bt} {dz} ballast_eff\n"
        )
        # insert material before first #box-less geometry section (append at end)
        out_content = body.rstrip() + "\n" + homog_mat + "\n" + geom

        out = OUT_DIR / f"s_{sid:05d}_{cls}_homog.in"
        out.write_text(out_content, encoding="utf-8")
        made.append((out.name, eps_eff, sig_eff))

    print(f"Wrote {len(made)} homogeneous .in to {OUT_DIR}\n")
    print(f"  {'file':32s} {'eps_eff':>8s} {'sig_eff':>9s}")
    for n, e, s in made:
        print(f"  {n:32s} {e:8.3f} {s:9.5f}")
    print("\nNote: eps_eff should RISE from C->MF->HF (more fouling). Run through")
    print("gprMax, return .out; then check if HF peak-freq > C (sign flipped).")


if __name__ == "__main__":
    main()

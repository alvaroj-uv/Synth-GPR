#!/usr/bin/env python3
"""
Debye-dispersion experiment: add frequency-dependent permittivity to the
fouling material and test whether it creates the real fouling FREQUENCY
signature (median/mean freq rising with fouling) that constant-eps does NOT.

For each base scene (C / MF / HF, dx=13.2 mm — mesh shown irrelevant), the
fouling #material line is replaced by a Debye version:

    OLD:  #material: eps  sigma 1 0 bal_foul_granular
    NEW:  #material: eps_inf sigma 1 0 bal_foul_granular
          #add_dispersion_debye: 1 d_eps tau bal_foul_granular

keeping eps_inf + d_eps == eps (the original CRIM static permittivity), so the
low-frequency eps is unchanged; we only ADD frequency dependence.

Sweep (wide): d_eps ∈ {20%, 50%, 80% of eps} × tau ∈ {0.5 ns, 2 ns} = 6 variants.
tau >> dt (~31 ps) as gprMax requires.

Outputs <scene>_de<pct>_tau<ns>.in to D:\\gprMax\\user_models\\debye_experiment.
Run through gprMax, return .out, then compare HF−C frequency contrast vs the
constant-eps baseline (which was ≈0).

Usage:
    python scripts/main/debye_experiment.py
"""

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from src.physics import debye_decompose

SRC_DIR = Path(r"D:\gprMax\user_models\mesh_experiment")
OUT_DIR = Path(r"D:\gprMax\user_models\debye_experiment")

SCENES = {35000: "C", 56877: "MF", 4867: "HF"}
D_EPS_FRACS = [0.2, 0.5, 0.8]      # fraction of eps made dispersive
TAUS = [0.5e-9, 2.0e-9]            # relaxation times (s), both >> dt

FOUL_RE = re.compile(
    r"^#material:\s*([\d.eE+-]+)\s+([\d.eE+-]+)\s+([\d.eE+-]+)\s+([\d.eE+-]+)\s+(bal_foul\w*)\s*$",
    re.MULTILINE,
)


def make_debye(content: str, d_eps_frac: float, tau: float) -> str:
    """Replace each fouling #material with eps_inf + a 1-pole Debye line."""
    def repl(m):
        eps, sigma, mu, mloss, name = m.groups()
        # Central, capped decomposition (eps_inf >= 1 guaranteed). See physics.
        eps_inf, d_eps = debye_decompose(float(eps), d_eps_frac)
        return (f"#material: {eps_inf} {sigma} {mu} {mloss} {name}\n"
                f"#add_dispersion_debye: 1 {d_eps} {tau:.4e} {name}")
    return FOUL_RE.sub(repl, content)


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    made = []
    for sid, cls in SCENES.items():
        src = SRC_DIR / f"s_{sid:05d}_{cls}_dx132.in"
        if not src.exists():
            print(f"  missing {src}")
            continue
        base = src.read_text(encoding="utf-8", errors="ignore")
        if not FOUL_RE.search(base):
            print(f"  [warn] no fouling material in {src.name} (clean scene?)")
        for frac in D_EPS_FRACS:
            for tau in TAUS:
                new = make_debye(base, frac, tau)
                tag = f"de{int(frac*100):02d}_tau{tau*1e9:.1f}ns".replace(".", "p")
                out = OUT_DIR / f"s_{sid:05d}_{cls}_{tag}.in"
                out.write_text(new, encoding="utf-8")
                made.append(out.name)

    print(f"Wrote {len(made)} .in files to {OUT_DIR}")
    for n in made:
        print("  ", n)
    print("\nNote: Clean (C) has no fouling material, so its variants are")
    print("identical baselines — useful as the constant reference for contrast.")
    print("\nRun through gprMax, then return the .out files for spectral comparison.")


if __name__ == "__main__":
    main()

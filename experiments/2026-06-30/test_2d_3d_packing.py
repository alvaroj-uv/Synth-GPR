"""Create + test 2-D and 3-D ballast packings with the dimension-agnostic
RCPGenerator packer (algo 'rcpgen'). Writes gprMax decks, renders them, and
runs gprMax --geometry-only to confirm both build.

Run: C:/Users/barba/miniconda3/python.exe experiments/2026-06-30/test_2d_3d_packing.py
"""
import sys, subprocess
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))
from src.rock_model import PackingBounds, Rock
from src.rcpgenerator_packing import RCPGeneratorPacking
from src.visualization.scene_3d import render_rocks_3d

HERE = Path(__file__).parent
GPRMAX = r"C:\Users\barba\.conda\envs\gprMax\python.exe"
ROCK = "#material: 6.1 0.001 1 0.0 granite"
SUB  = "#material: 8 0.02 1 0.0 subgrade"


def geom_only(deck: Path) -> bool:
    vti = deck.with_suffix(".vti")
    if vti.exists():
        vti.unlink()
    r = subprocess.run([GPRMAX, "-m", "gprMax", deck.name, "--geometry-only"],
                       capture_output=True, text=True, cwd=str(deck.parent))
    if vti.exists():
        return True
    tail = (r.stdout + r.stderr).strip().splitlines()[-3:]
    print("   gprMax error:", " | ".join(t.strip() for t in tail))
    return False


# ───────────────────────── 2-D ─────────────────────────
def build_2d():
    DOMX, DOMY = 0.5, 0.6
    bal_lo, bal_hi = 0.25, 0.55                      # ballast layer in y
    b = PackingBounds(0.0, DOMX, bal_lo, bal_hi)     # 2-D bounds
    rocks = RCPGeneratorPacking().pack(b, 0.018, 0.030, 0.72, seed=1)
    print(f"[2D] {len(rocks)} rocks  (ndim={rocks[0].ndim})")

    lines = [f"#domain: {DOMX} {DOMY} 0.003", "#dx_dy_dz: 0.003 0.003 0.003",
             "#time_window: 1.2e-8", ROCK, SUB,
             f"#box: 0 0 0 {DOMX} {bal_lo} 0.003 subgrade"]
    for r in rocks:                                  # disks → #cylinder (thin z)
        lines.append(f"#cylinder: {r.x:.4f} {r.y:.4f} 0 {r.x:.4f} {r.y:.4f} 0.003 {r.radius:.4f} granite")
    lines += ["#waveform: ricker 1 4.2e8 w",
              f"#hertzian_dipole: z {DOMX/2:.3f} 0.58 0.0015 w",
              f"#rx: {DOMX/2+0.03:.3f} 0.58 0.0015",
              f"#geometry_view: 0 0 0 {DOMX} {DOMY} 0.003 0.003 0.003 0.003 packing2d n",
              "#messages: n"]
    deck = HERE / "packing2d.in"; deck.write_text("\n".join(lines) + "\n")

    fig, ax = plt.subplots(figsize=(6, 7))
    ax.add_patch(Rectangle((0, 0), DOMX, bal_lo, fc="#cdc673", label="subgrade"))
    ax.add_patch(Rectangle((0, bal_lo), DOMX, DOMY - bal_lo, fc="#eef", ec="none"))
    for r in rocks:
        ax.add_patch(Circle((r.x, r.y), r.radius, fc="#8b7355", ec="k", lw=0.3))
    ax.plot(DOMX/2, 0.58, "vr", ms=8)
    ax.set_xlim(0, DOMX); ax.set_ylim(0, DOMY); ax.set_aspect("equal")
    ax.set_title(f"2-D packing ({len(rocks)} disks, rcpgen)"); ax.set_xlabel("x (m)"); ax.set_ylabel("y (m)")
    fig.savefig(HERE / "packing2d.png", dpi=130, bbox_inches="tight"); plt.close(fig)
    ok = geom_only(deck)
    print(f"[2D] geometry-only build: {'OK' if ok else 'FAILED'}  -> packing2d.png / .in / .vti")
    return ok


# ───────────────────────── 3-D ─────────────────────────
def build_3d():
    DOMX, DOMY, DOMZ = 0.3, 0.3, 0.5
    bal_lo, bal_hi = 0.15, 0.45                       # ballast layer in z (vertical)
    b = PackingBounds(0.0, DOMX, 0.0, DOMY, 0.0, bal_hi - bal_lo)   # 3-D bounds (z set)
    print(f"[3D] bounds ndim={b.ndim} volume={b.volume:.4f}")
    rocks = RCPGeneratorPacking().pack(b, 0.020, 0.040, 0.55, seed=1)
    print(f"[3D] {len(rocks)} spheres  (ndim={rocks[0].ndim}, z set={rocks[0].z is not None})")

    lines = [f"#domain: {DOMX} {DOMY} {DOMZ}", "#dx_dy_dz: 0.004 0.004 0.004",
             "#time_window: 1.2e-8", ROCK, SUB,
             f"#box: 0 0 0 {DOMX} {DOMY} {bal_lo} subgrade"]
    for r in rocks:                                   # spheres → #sphere, offset z into layer
        zc = bal_lo + r.z
        lines.append(f"#sphere: {r.x:.4f} {r.y:.4f} {zc:.4f} {r.radius:.4f} granite")
    lines += ["#waveform: ricker 1 4.2e8 w",
              f"#hertzian_dipole: z {DOMX/2:.3f} {DOMY/2:.3f} 0.48 w",
              f"#rx: {DOMX/2+0.03:.3f} {DOMY/2:.3f} 0.48",
              f"#geometry_view: 0 0 0 {DOMX} {DOMY} {DOMZ} 0.004 0.004 0.004 packing3d n",
              "#messages: n"]
    deck = HERE / "packing3d.in"; deck.write_text("\n".join(lines) + "\n")

    # Place rocks at their final scene z, then use the shared 3-D renderer.
    placed = [Rock(x=r.x, y=r.y, z=bal_lo + r.z, radius=r.radius) for r in rocks]
    fig = render_rocks_3d(placed, domain=(DOMX, DOMY, DOMZ),
                          boxes=[(0, 0, 0, DOMX, DOMY, bal_lo, "#cdc673")],
                          title="3-D packing (rcpgen)")
    fig.savefig(HERE / "packing3d.png", dpi=130, bbox_inches="tight"); plt.close(fig)
    ok = geom_only(deck)
    print(f"[3D] geometry-only build: {'OK' if ok else 'FAILED'}  -> packing3d.png / .in / .vti")
    return ok


if __name__ == "__main__":
    ok2 = build_2d()
    ok3 = build_3d()
    print(f"\nRESULT: 2D={'OK' if ok2 else 'FAIL'}  3D={'OK' if ok3 else 'FAIL'}")

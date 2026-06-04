#!/usr/bin/env python3
r"""
Full GSSI-400 antenna-twin A/B (3D, 2mm).

Question (the one the waveform-only test could NOT answer): does the REAL antenna
geometry — HDPE case, PEC shield, absorber, bowties, voltage source — reshape the
trace spectrum toward the real 400 MHz Site-1 data, vs an idealized hertzian
dipole? The antenna's effect is the GEOMETRY reshaping the pulse, not the pulse
alone, so this requires the full 3D twin at 1-2mm (here: 2mm).

Design: minimal A/B in a small 0.38 x 0.608 x 0.38 m, 2mm domain (~11M cells,
~5200 steps -> tens of min/scan on GPU). Same compact ballast scene under either:
  - "dipole": z hertzian dipole + ricker 400 MHz (matches the 2D pipeline source)
  - "antenna": antenna_like_GSSI_400 (Warren/Giannakis, ported from GPR-repo GSSI.py)
2-3 fouling levels x {dipole, antenna}. Geometry identical across the pair.

This is a PHYSICS VALIDATION tool, not dataset generation. NOT the 2D 80k pipeline.

Workflow:
    python scripts/experiments/antenna_twin_ab.py --generate
    <run run_all.bat through the gprMax env>          # tens of min per .out
    python scripts/experiments/antenna_twin_ab.py --analyze

The antenna emitter writes raw gprMax #-commands directly (no gprMax import needed
at generation time); it is a faithful 2mm port of antenna_like_GSSI_400.
"""
import sys, argparse
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

OUT_DIR = Path(r"D:\gprMax\user_models\antenna_twin_ab")

# --- Domain (small, 2mm) ----------------------------------------------------
# AXIS CONVENTION (gprMax-native, matching GSSI.py):
#   x, y = horizontal plane the antenna lies in (case footprint 0.3 x 0.3)
#   z    = DEPTH. The antenna body occupies HIGH z (skid bottom -> +z up into
#          the case), and radiates toward the ground built at LOW z.
# So the ground stack (subgrade/formation/ballast/fouling/rocks) is layered
# along z, NOT y. This keeps the antenna pointing at the ground.
DX = 0.002
CASE = (0.300, 0.300, 0.178)            # GSSI-400 external dims (x, y, body-depth)
MARGIN = 0.040                           # PML + buffer each lateral (x,y) side
DOMAIN_X = round(CASE[0] + 2 * MARGIN, 3)   # 0.380
DOMAIN_Y = round(CASE[1] + 2 * MARGIN, 3)   # 0.380
# Depth (z) stack, from z=0 (bottom) upward:
SUBGRADE_TOP = 0.10
FORMATION_TOP = 0.15
BALLAST_TOP = 0.35                        # 0.20 m ballast
AIR_GAP = 0.02                            # skid clearance above ballast
ANTENNA_SKID_Z = BALLAST_TOP + AIR_GAP    # z of antenna skid bottom (0.37)
DOMAIN_Z = round(ANTENNA_SKID_Z + CASE[2] + 0.06, 3)   # + body + 6cm air above

CENTER_FREQ = 400e6
FI_LEVELS = [0.0, 25.0, 45.0]            # clean / moderate / fouled
ROCK_R = 0.020                           # 2 cm rocks (sized for the small 2mm box)
TARGET_ROCK_FILL = 0.45
MOISTURE = 0.10
BASE_SEED = 707
TIME_WINDOW = 20e-9

# Material props (eps, sigma, mu, mag_loss) — mirror the 2D pipeline
MATERIALS = {
    "subgrade":  (10.0, 0.005, 1, 0),
    "formation": (6.0,  0.003, 1, 0),
    "bal_rock":  (5.5,  0.001, 1, 0),
}


def _foul_props(pvc):
    """CRIM-ish fouling permittivity rising with moisture-bearing fines."""
    eps = 5.0 + 0.06 * pvc + 8.0 * MOISTURE
    sig = 0.01 + 0.004 * pvc / 50.0
    return (round(eps, 3), round(sig, 4), 1, 0)


# ---------------------------------------------------------------------------
# GSSI-400 antenna: insert via the OFFICIAL gprMax antenna library using a
# #python block (https://docs.gprmax.com/en/latest/user_libs_antennas.html).
# This runs the exact validated Warren/Giannakis geometry at sim time — far more
# reliable than a hand-port. Convention: (x,y) = antenna centre in the horizontal
# plane; z = bottom of the antenna skid; the antenna radiates in +z (depth).
# ---------------------------------------------------------------------------
def emit_gssi_400(cx, cy, z_skid, resolution=0.002):
    """Return gprMax lines that insert antenna_like_GSSI_400 via #python."""
    res_mm = resolution
    return [
        "#python:",
        "from user_libs.antennas.GSSI import antenna_like_GSSI_400",
        f"antenna_like_GSSI_400({cx:.4f}, {cy:.4f}, {z_skid:.4f}, resolution={res_mm:g})",
        "#end_python:",
    ]


# ---------------------------------------------------------------------------
def _pack_spheres(seed):
    """Grid-jittered sphere pack in the ballast zone. Ballast is layered along
    z (depth) in [FORMATION_TOP, BALLAST_TOP); x,y span the lateral footprint."""
    rng = np.random.default_rng(seed)
    spheres = []
    r = ROCK_R
    step = 2 * r * 1.05
    xs = np.arange(MARGIN + r, DOMAIN_X - MARGIN - r, step)
    ys = np.arange(MARGIN + r, DOMAIN_Y - MARGIN - r, step)
    zs = np.arange(FORMATION_TOP + r, BALLAST_TOP - r, step)
    for xi in xs:
        for yi in ys:
            for zi in zs:
                jx, jy, jz = rng.uniform(-0.3, 0.3, 3) * r
                spheres.append((xi + jx, yi + jy, zi + jz, r))
    return spheres


def _general_block():
    pml = 10
    dt_steps = TIME_WINDOW
    return [
        "#title: antenna_twin_ab",
        f"#domain: {DOMAIN_X:.3f} {DOMAIN_Y:.3f} {DOMAIN_Z:.3f}",
        f"#dx_dy_dz: {DX} {DX} {DX}",
        f"#time_window: {dt_steps:g}",
        f"#pml_cells: {pml} {pml} {pml} {pml} {pml} {pml}",
        "#messages: n",
    ]


def _scene_geometry(pvc, spheres):
    """Ground stack + fouling box + rocks (shared by both arms)."""
    fe, fs, fm, fml = _foul_props(pvc)
    L = []
    for name, (e, s, m, ml) in MATERIALS.items():
        L.append(f"#material: {e:g} {s:g} {m:g} {ml:g} {name}")
    L.append(f"#material: {fe:g} {fs:g} {fm:g} {fml:g} fouling")
    # ground stack layered along z (depth); full x,y lateral extent
    L.append(f"#box: 0 0 0 {DOMAIN_X:.3f} {DOMAIN_Y:.3f} {SUBGRADE_TOP:.3f} subgrade")
    L.append(f"#box: 0 0 {SUBGRADE_TOP:.3f} {DOMAIN_X:.3f} {DOMAIN_Y:.3f} {FORMATION_TOP:.3f} formation")
    # fouling fills ballast zone (along z) up to a PVC-scaled depth; rocks overwrite it
    foul_top = FORMATION_TOP + (BALLAST_TOP - FORMATION_TOP) * (pvc / 100.0)
    if pvc > 0:
        L.append(f"#box: 0 0 {FORMATION_TOP:.3f} {DOMAIN_X:.3f} {DOMAIN_Y:.3f} {foul_top:.3f} fouling")
    for (sx, sy, sz, sr) in spheres:
        L.append(f"#sphere: {sx:.4f} {sy:.4f} {sz:.4f} {sr:.4f} bal_rock")
    return L


def _dipole_source():
    """Idealized arm: z-polarized hertzian dipole above the ground (high z),
    radiating down into the ballast. Mirrors the antenna's tx position."""
    ax = DOMAIN_X / 2
    ay = DOMAIN_Y / 2
    az = ANTENNA_SKID_Z + 0.05
    rx = ax + 0.10
    return [
        f"#waveform: ricker 1 {CENTER_FREQ:g} ricker_src",
        f"#hertzian_dipole: z {ax:.4f} {ay:.4f} {az:.4f} ricker_src",
        f"#rx: {rx:.4f} {ay:.4f} {az:.4f}",
    ]


def generate():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for old in OUT_DIR.glob("at_*.in"):
        old.unlink()
    rng = np.random.default_rng(BASE_SEED)
    manifest = []

    print(f"Domain {DOMAIN_X}x{DOMAIN_Y}x{DOMAIN_Z} m @ {DX*1000:.0f}mm")
    for i, pvc in enumerate(FI_LEVELS):
        seed = int(rng.integers(0, 2**31))
        spheres = _pack_spheres(seed)
        geom = _scene_geometry(pvc, spheres)

        for arm in ("dipole", "antenna"):
            lines = list(_general_block()) + geom
            if arm == "dipole":
                lines += _dipole_source()
            else:
                ax, ay = DOMAIN_X / 2, DOMAIN_Y / 2
                lines += emit_gssi_400(ax, ay, ANTENNA_SKID_Z, resolution=DX)
            stem = f"at_{i:02d}_{arm}"
            (OUT_DIR / f"{stem}.in").write_text("\n".join(lines) + "\n", encoding="utf-8")
            manifest.append({"FI": pvc, "arm": arm, "seed": seed, "stem": stem,
                             "n_rocks": len(spheres)})
        print(f"  FI={pvc:>4.0f} seed={seed} rocks={len(spheres)} -> dipole + antenna")

    pd.DataFrame(manifest).to_csv(OUT_DIR / "manifest.csv", index=False)
    _write_run_all(OUT_DIR)
    nx, ny, nz = DOMAIN_X / DX, DOMAIN_Y / DX, DOMAIN_Z / DX
    print(f"\nGenerated {len(manifest)} .in ({len(FI_LEVELS)} FI x 2 arms) in {OUT_DIR}")
    print(f"~{nx*ny*nz/1e6:.0f}M cells each. Run run_all.bat (GPU), then --analyze")


def _write_run_all(out_dir: Path):
    bat = r"""@echo off
REM GSSI-400 antenna-twin A/B (3D, 2mm). One .out per .in.
setlocal enabledelayedexpansion
set GPRMAX_ENV=gprMax
cd /d "%~dp0"
call "%USERPROFILE%\miniconda3\Scripts\activate.bat" %GPRMAX_ENV%
if errorlevel 1 ( echo [ERROR] activate env %GPRMAX_ENV% & pause )
cd /d D:\gprMax
set COUNT=0
for %%F in ("%~dp0*.in") do (
    set /a COUNT+=1
    echo. & echo ===== Running %%~nxF =====
    python -m gprMax "%%F" -gpu
    if errorlevel 1 echo [ERROR] gprMax failed on %%~nxF
)
echo. & echo Done. Ran !COUNT! files. .out in %~dp0
pause
"""
    (out_dir / "run_all.bat").write_text(bat, encoding="utf-8")


def _freq_feats(ez, dt):
    from src.feature_extraction import _extract_frequency_features
    f = _extract_frequency_features(np.asarray(ez, float), dt)
    return {"mean_freq": f["mean_frequency"] / 1e6,
            "median_freq": f["median_frequency"] / 1e6,
            "dom_freq": f["dominant_frequency"] / 1e6}


def analyze():
    from src.data_loader import read_rx_traces
    man = pd.read_csv(OUT_DIR / "manifest.csv")

    def load(p):
        # The two arms radiate on different components: the z-dipole -> Ez, the
        # GSSI bowties (y-aligned) -> Ey. Pick the DOMINANT component by energy
        # so each arm's principal trace is analysed (not a fixed preference).
        traces, dt = read_rx_traces(p)
        best, best_amp = None, -1.0
        for c in ("Ex", "Ey", "Ez"):
            if c in traces:
                arr = traces[c].astype(float)
                amp = np.abs(arr).max()
                if amp > best_amp:
                    best, best_amp = arr, amp
        return best, dt

    rows = []
    for _, r in man.iterrows():
        op = OUT_DIR / f"{r['stem']}.out"
        if op.exists():
            rows.append({"arm": r["arm"], "FI": float(r["FI"]), **_freq_feats(*load(op))})
        else:
            print(f"  [missing] {r['stem']}.out")
    d = pd.DataFrame(rows).dropna()
    if d.empty:
        print("No .out files. Run run_all.bat first."); return

    print(f"\nAnalyzed {len(d)} traces\n")
    cols = ["mean_freq", "median_freq", "dom_freq"]
    for arm in ("dipole", "antenna"):
        da = d[d.arm == arm]
        if len(da):
            print(f"  {arm:<8} " + "  ".join(f"{c}={da[c].mean():6.1f}" for c in cols))

    real_csv = ROOT / "docs" / "input" / "feature_dataset_real.csv"
    if real_csv.exists():
        rr = pd.read_csv(real_csv)
        real = {"mean_freq": rr.mean_frequency.median() / 1e6,
                "median_freq": rr.median_frequency.median() / 1e6,
                "dom_freq": rr.dominant_frequency.median() / 1e6}
        print(f"\n  REAL (Site-1 median): " + "  ".join(f"{c}={real[c]:.0f}" for c in cols))
        print("\n  |sim - real| (smaller=closer):")
        better = 0
        for c in cols:
            dd = abs(d[d.arm == "dipole"][c].mean() - real[c])
            aa = abs(d[d.arm == "antenna"][c].mean() - real[c])
            mark = "ANTENNA closer" if aa < dd else "dipole closer"
            better += aa < dd
            print(f"    {c:<12} dipole {dd:6.1f}  vs  antenna {aa:6.1f}  -> {mark}")
        print(f"\n  Antenna closer on {better}/{len(cols)} descriptors.")
        print("  -> Full twin justified ONLY if antenna closes the gap dipole couldn't.")
    d.to_csv(OUT_DIR / "results.csv", index=False)
    print(f"\n  Saved {OUT_DIR/'results.csv'}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--generate", action="store_true")
    ap.add_argument("--analyze", action="store_true")
    a = ap.parse_args()
    if a.generate: generate()
    elif a.analyze: analyze()
    else: print("Use --generate or --analyze")


if __name__ == "__main__":
    main()

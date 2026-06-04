#!/usr/bin/env python3
"""
Heterogeneous-fouling A/B using the ROCK LIBRARY (no text surgery).

The original hetero_fouling_ab.py had to derive the hetero arm by text-editing
the homog .in, because re-running the packer per arm caused RNG drift. With
src/rock_library.py we instead FIX the rock skeleton (load the same library
packing in both arms via config.rock_source_file) and vary ONLY
config.fouling_heterogeneous. Rocks are identical by construction -> the cleanest
possible isolation of the fouling-fill effect.

Workflow:
    python scripts/experiments/hetero_fouling_lib_ab.py --generate
    <run run_all.bat through the gprMax env>
    python scripts/experiments/hetero_fouling_lib_ab.py --analyze
"""
import sys, argparse
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

OUT_DIR = Path(r"D:\gprMax\user_models\hetero_fouling_lib_ab")
FREQ_HZ = 400e6
PVC_SWEEP = [10.0, 20.0, 30.0, 40.0, 50.0]
N_GEOM = 3              # distinct library packings (geometry seeds)
MOISTURE = 0.10
DOMAIN_W = 2.248       # matches FDTD domain_x at 400 MHz
BALLAST_H = 0.45


def _ensure_library():
    """Build (or reuse) a library of en13450 packings sized to the FDTD domain."""
    from src.rock_library import RockLibrary
    lib = RockLibrary()
    if len(lib.query(grading="en13450", width=DOMAIN_W)) < N_GEOM:
        lib.build(n_per_grading=N_GEOM, gradings=["en13450"],
                  width=DOMAIN_W, height=BALLAST_H, base_seed=3000)
    return lib


def _build(pvc, hetero, source_file, seed):
    from src.config import GeneratorConfig
    from src.dataset_generator import DatasetGenerator
    from src.work_order import WorkOrder, WorkOrderSystem

    cfg = GeneratorConfig.create_physically_perfect(
        center_freq_hz=FREQ_HZ,
        pvc_min=pvc, pvc_max=pvc,
        moisture_min=MOISTURE, moisture_max=MOISTURE,
        base_seed=seed,
        fouling_heterogeneous=hetero,
        rock_source_file=source_file,   # <-- identical rocks across arms
    )
    gen = DatasetGenerator(cfg)
    params = {'pvc': pvc, 'moisture': MOISTURE, 'pvc_bottom': pvc, 'pvc_top': pvc,
              'FI_bottom': pvc, 'FI_top': pvc, 'seed': seed}
    cp = gen.pipeline.run(WorkOrderSystem(WorkOrder.from_sampled_params(1, params)))
    return cp, cfg


def generate():
    from src.file_writer import GPRMaxFileWriter

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for old in OUT_DIR.glob("hl_*.in"):
        old.unlink()

    lib = _ensure_library()
    packings = lib.query(grading="en13450", width=DOMAIN_W)[:N_GEOM]
    print(f"Using {len(packings)} library packings:")
    for p in packings:
        print(f"  {p.name}: {p.n_rocks} rocks")

    manifest = []
    for i, pvc in enumerate(PVC_SWEEP):
        for g, pk in enumerate(packings):
            seed = 9000 + i * 10 + g
            for arm, hetero in (("homog", False), ("hetero", True)):
                cp, cfg = _build(pvc, hetero, pk.path, seed)
                stem = f"hl_{i:02d}_{g}_{arm}"
                GPRMaxFileWriter.save_scene_checkpoint(
                    cp, output_path=str(OUT_DIR / f"{stem}.in"),
                    scenario_type="Sim", config=cfg)
                manifest.append({"FI": pvc, "geom": g, "packing": pk.name,
                                 "arm": arm, "stem": stem})
            print(f"  FI={pvc:>4.0f} geom={g} ({pk.name}) -> homog + hetero")

    pd.DataFrame(manifest).to_csv(OUT_DIR / "manifest.csv", index=False)
    _write_run_all(OUT_DIR)
    print(f"\nGenerated {len(manifest)} .in "
          f"({len(PVC_SWEEP)}FI x {N_GEOM}geom x 2arms) in {OUT_DIR}")
    print("Next: run run_all.bat, then --analyze")


def _write_run_all(out_dir: Path):
    bat = r"""@echo off
REM Hetero-fouling (rock-library) A/B through gprMax (2D).
setlocal enabledelayedexpansion
set GPRMAX_ENV=gprMax
cd /d "%~dp0"
call "%USERPROFILE%\miniconda3\Scripts\activate.bat" %GPRMAX_ENV%
if errorlevel 1 ( echo [ERROR] activate %GPRMAX_ENV% & pause )
cd /d D:\gprMax
set COUNT=0
for %%F in ("%~dp0*.in") do (
    set /a COUNT+=1
    echo. & echo ===== %%~nxF =====
    python -m gprMax "%%F" -gpu
    if errorlevel 1 echo [ERROR] failed on %%~nxF
)
echo. & echo Done. Ran !COUNT! files.
pause
"""
    (out_dir / "run_all.bat").write_text(bat, encoding="utf-8")


def _metric(ez, dt):
    from scipy.signal import welch, butter, filtfilt
    pk = int(np.argmax(np.abs(ez))); coda = ez[pk + 20:]
    if len(coda) < 64: return np.nan
    sig = coda - coda.mean(); fs = 1 / dt
    b, a = butter(4, [150e6/(fs/2), 800e6/(fs/2)], btype="band"); sig = filtfilt(b, a, sig)
    f, p = welch(sig, fs=fs, nperseg=min(len(sig), 256), nfft=4096)
    band = (f >= 150e6) & (f <= 800e6); f, p = f[band], p[band]
    return np.sum(f*p)/np.sum(p)/1e6 if p.sum() > 0 else np.nan


def analyze():
    from scipy.stats import linregress
    man = pd.read_csv(OUT_DIR / "manifest.csv")

    from src.data_loader import read_ascan

    def load(p):
        d = read_ascan(p)
        return d["signal"].astype(float), d["dt"]

    rows = []
    for _, r in man.iterrows():
        op = OUT_DIR / f"{r['stem']}.out"
        if op.exists():
            rows.append({"arm": r["arm"], "FI": float(r["FI"]), "c": _metric(*load(op))})
        else:
            print(f"  [missing] {r['stem']}.out")
    d = pd.DataFrame(rows).dropna()
    if d.empty:
        print("No .out files. Run run_all.bat first."); return

    print(f"\nAnalyzed {len(d)} traces, FI {d.FI.min():.0f}-{d.FI.max():.0f}")
    print("  Reference: homog~0.17   real~3.6 MHz/FI\n")
    res = {}
    for arm in ("homog", "hetero"):
        da = d[d.arm == arm]
        if len(da) > 2:
            s = linregress(da["FI"], da["c"]); res[arm] = s.slope
            print(f"  {arm:<8} slope = {s.slope:+.3f} MHz/FI "
                  f"(r={s.rvalue:+.2f}, p={s.pvalue:.2g}, n={len(da)})")
    if "homog" in res and "hetero" in res:
        print(f"\n  DELTA (hetero - homog) = {res['hetero']-res['homog']:+.3f} MHz/FI")
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

#!/usr/bin/env python3
"""
Ballast permittivity A/B: follow the leaders (eps 5.0 -> 6.5).

Your config.bal_rock_eps defaults to 5.0 (emitted as #material: 5 ... bal_rock).
BOTH independent ETH theses (GPR-repo / Heller and PINN4GPR) use eps=6.5 for
railway ballast. eps sets bulk velocity and the rock/fouling scattering contrast
central to the (confirmed) heterogeneous-fouling result. Question: does following
the leaders to 6.5 move the SYNTHETIC trace spectrum toward the real 400 MHz
Site-1 data?

Rigorous matched pairs via the ROCK LIBRARY: identical geometry across arms, vary
ONLY bal_rock_eps. Metric = the project's own _extract_frequency_features so sim
== the real CSV definition (no artifact). Real ref: docs/input/feature_dataset_real.csv.

    python scripts/main/ballast_eps_ab.py --generate
    <run run_all.bat>
    python scripts/main/ballast_eps_ab.py --analyze
"""
import sys, argparse
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

OUT_DIR = Path(r"D:\gprMax\user_models\ballast_eps_ab")
FREQ_HZ = 400e6
PVC_SWEEP = [10.0, 30.0, 50.0]
N_GEOM = 3
MOISTURE = 0.10
DOMAIN_W = 2.248
BALLAST_H = 0.45
EPS_ARMS = {"eps50": 5.0, "eps65": 6.5}   # current vs "the leaders"


def _ensure_library():
    from src.rock_library import RockLibrary
    lib = RockLibrary()
    if len(lib.query(grading="en13450", width=DOMAIN_W)) < N_GEOM:
        lib.build(n_per_grading=N_GEOM, gradings=["en13450"],
                  width=DOMAIN_W, height=BALLAST_H, base_seed=3000)
    return lib


def _build(pvc, eps, source_file, seed):
    from src.config import GeneratorConfig
    from src.dataset_generator import DatasetGenerator
    from src.work_order import WorkOrder, WorkOrderSystem
    cfg = GeneratorConfig.create_physically_perfect(
        center_freq_hz=FREQ_HZ, pvc_min=pvc, pvc_max=pvc,
        moisture_min=MOISTURE, moisture_max=MOISTURE, base_seed=seed,
        rock_source_file=source_file, bal_rock_eps=eps)
    gen = DatasetGenerator(cfg)
    params = {'pvc': pvc, 'moisture': MOISTURE, 'pvc_bottom': pvc, 'pvc_top': pvc,
              'FI_bottom': pvc, 'FI_top': pvc, 'seed': seed}
    return gen.pipeline.run(WorkOrderSystem(WorkOrder.from_sampled_params(1, params))), cfg


def generate():
    from src.file_writer import GPRMaxFileWriter
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for old in OUT_DIR.glob("be_*.in"):
        old.unlink()
    lib = _ensure_library()
    packings = lib.query(grading="en13450", width=DOMAIN_W)[:N_GEOM]
    print(f"Using {len(packings)} library packings (geometry fixed across arms)")

    manifest = []
    for i, pvc in enumerate(PVC_SWEEP):
        for g, pk in enumerate(packings):
            seed = 8000 + i * 10 + g
            for arm, eps in EPS_ARMS.items():
                cp, cfg = _build(pvc, eps, pk.path, seed)
                stem = f"be_{i:02d}_{g}_{arm}"
                GPRMaxFileWriter.save_scene_checkpoint(
                    cp, output_path=str(OUT_DIR / f"{stem}.in"),
                    scenario_type="Sim", config=cfg)
                manifest.append({"FI": pvc, "geom": g, "arm": arm, "eps": eps, "stem": stem})
            print(f"  FI={pvc:>4.0f} geom={g} -> eps5.0 + eps6.5")
    pd.DataFrame(manifest).to_csv(OUT_DIR / "manifest.csv", index=False)
    _write_run_all(OUT_DIR)
    print(f"\nGenerated {len(manifest)} .in in {OUT_DIR}")
    print("Run run_all.bat, then --analyze")


def _write_run_all(out_dir: Path):
    bat = r"""@echo off
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


def _freq_feats(ez, dt):
    from src.feature_extraction import _extract_frequency_features
    f = _extract_frequency_features(np.asarray(ez, float), dt)
    return {"mean_freq": f["mean_frequency"]/1e6,
            "median_freq": f["median_frequency"]/1e6,
            "dom_freq": f["dominant_frequency"]/1e6}


def analyze():
    import h5py
    man = pd.read_csv(OUT_DIR / "manifest.csv")

    def load(p):
        f = h5py.File(p, "r"); dt = f.attrs["dt"]
        ez = np.array(f["rxs/rx1/Ez"]).astype(float); f.close(); return ez, dt

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

    cols = ["mean_freq", "median_freq", "dom_freq"]
    print(f"\nAnalyzed {len(d)} traces\n")
    for arm in ("eps50", "eps65"):
        da = d[d.arm == arm]
        if len(da):
            print(f"  {arm:<6} " + "  ".join(f"{c}={da[c].mean():6.1f}" for c in cols))

    real_csv = ROOT / "docs" / "input" / "feature_dataset_real.csv"
    if real_csv.exists():
        rr = pd.read_csv(real_csv)
        real = {"mean_freq": rr.mean_frequency.median()/1e6,
                "median_freq": rr.median_frequency.median()/1e6,
                "dom_freq": rr.dominant_frequency.median()/1e6}
        print(f"\n  REAL (Site-1 median): " + "  ".join(f"{c}={real[c]:.0f}" for c in cols))
        print("\n  |sim - real| (smaller=closer):")
        better = 0
        for c in cols:
            a = abs(d[d.arm=="eps50"][c].mean()-real[c])
            b = abs(d[d.arm=="eps65"][c].mean()-real[c])
            mark = "eps6.5 closer" if b < a else "eps5.0 closer"
            better += b < a
            print(f"    {c:<12} eps5.0 {a:6.1f}  vs  eps6.5 {b:6.1f}  -> {mark}")
        print(f"\n  Following the leaders (6.5) closer on {better}/{len(cols)} descriptors.")
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

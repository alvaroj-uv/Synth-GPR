#!/usr/bin/env python3
"""
Regenerate the dataset with the corrected + enriched physics recipe.

Recipe (all validated by the smoke test in this session):
  - ROCK Z-FIX (mandatory): rocks span the full z-cell so they are actually
    rasterized (the old dataset had PHANTOM rocks; a phantom-trained model
    collapses to chance on rock-present traces).
  - Heterogeneous sublayers: subgrade/formation as #soil_peplinski + #fractal_box
    (lower-eps, lossy, dispersive, heterogeneous) instead of flat eps=10 boxes.
  - Heterogeneous fouling: #fractal_box clay fouling.
  - Surface roughness on the fouling top (the strong sub-ballast reflector).
  - #messages:n, clay fouling, material-SSOT: already in.

Writes to a NEW directory (the old 80k is preserved as a safety/comparison copy).

    python scripts/main/regen_dataset_v2.py --n-per-class 5000 [--out DIR] [--start-id 0]

Generates .in files only. Run them through gprMax separately (run_all.bat /
run_simulations.py), then build_parquet.py + train_rf_waveform_only.py.
"""
import sys, argparse, time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

from src.config import GeneratorConfig, create_per_label_config
from src.dataset_generator import DatasetGenerator
from src.fouling import get_pvc_range

LABELS = ["CL", "MC", "MF", "F", "HF"]   # CL = clean (stored as 'C' in features)
FREQ_HZ = 400e6


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n-per-class", type=int, default=5000)
    ap.add_argument("--out", type=Path,
                    default=ROOT / "output" / "gpr_synth_dataset_v2")
    ap.add_argument("--start-id", type=int, default=0)
    ap.add_argument("--base-seed", type=int, default=20260603)
    a = ap.parse_args()

    a.out.mkdir(parents=True, exist_ok=True)
    print("=" * 70)
    print("DATASET REGEN v2 — corrected + enriched physics")
    print("=" * 70)
    print(f"Output       : {a.out}")
    print(f"Per class    : {a.n_per_class}   (x{len(LABELS)} = {a.n_per_class*len(LABELS)} total)")
    print(f"Recipe       : rock z-fix + hetero sublayers + hetero fouling + fouling-top roughness")
    print("=" * 70)

    base = GeneratorConfig.create_physically_perfect(
        center_freq_hz=FREQ_HZ,
        angular_rocks=True,          # matches the original 80k (#triangle rocks)
        base_seed=a.base_seed,
        # --- the recipe ---
        fouling_heterogeneous=True,
        heterogeneous_sublayers=True,
        layer_surface_roughness=True,
    )

    cur = a.start_id
    total = 0
    t0 = time.time()
    for label in LABELS:
        pmin, pmax = get_pvc_range(label)
        cfg = create_per_label_config(base, label)
        gen = DatasetGenerator(cfg)
        print(f"\n>> {label} (PVC {pmin:.0f}-{pmax:.0f}%): generating {a.n_per_class} ...")
        files = gen.generate_samples(output_dir=a.out, n_samples=a.n_per_class,
                                     start_id=cur)
        n = len(files)
        print(f"   [OK] {n} samples, IDs {cur}..{cur+n-1}  "
              f"(elapsed {time.time()-t0:.0f}s)")
        cur += n
        total += n

    _write_run_all(a.out)
    print(f"\n{'='*70}")
    print(f"DONE generating {total} .in in {time.time()-t0:.0f}s -> {a.out}")
    print("Next: run run_all.bat (gprMax), then build_parquet.py + train_rf_waveform_only.py")
    print("=" * 70)


def _write_run_all(out_dir: Path):
    bat = r"""@echo off
REM Run the regen v2 dataset through gprMax (single A-scan each).
setlocal enabledelayedexpansion
set GPRMAX_ENV=gprMax
cd /d "%~dp0"
call "%USERPROFILE%\miniconda3\Scripts\activate.bat" %GPRMAX_ENV%
if errorlevel 1 ( echo [ERROR] activate %GPRMAX_ENV% & pause )
cd /d D:\gprMax
set COUNT=0
for %%F in ("%~dp0*.in") do (
    set /a COUNT+=1
    python -m gprMax "%%F" -n 1 -gpu
    if errorlevel 1 echo [ERROR] failed on %%~nxF
)
echo. & echo Done. Ran !COUNT! files.
pause
"""
    (out_dir / "run_all.bat").write_text(bat, encoding="utf-8")


if __name__ == "__main__":
    main()

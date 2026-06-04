#!/usr/bin/env python3
"""
A/B test for heterogeneous fouling (Gap A).

Question: does emitting the fouling void-fill as #soil_peplinski + #fractal_box
(config.fouling_heterogeneous=True), while KEEPING the packed-rock skeleton,
move the coda-centroid-vs-FI slope toward the real ~3.6 MHz/FI — relative to the
homogeneous-box baseline (~0.17)?

This differs from scripts/experiments/peplinski_slope.py, which removed all rocks. Here
each FI/seed produces a MATCHED PAIR: one HOMOG arm and one HETERO arm with the
SAME geometry seed, so the only difference is the fouling fill primitive.

Workflow:
    python scripts/experiments/hetero_fouling_ab.py --generate   # writes .in + run_all.bat
    <run run_all.bat through the gprMax conda env>         # produces .out next to each .in
    python scripts/experiments/hetero_fouling_ab.py --analyze     # slope per arm + delta

Metric is identical to peplinski_slope.py: band-limited (150-800 MHz) spectral
centroid of the coda (post-direct-arrival), regressed against FI.
"""
import sys, argparse
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

OUT_DIR = Path(r"D:\gprMax\user_models\hetero_fouling_ab")
FREQ_HZ = 400e6
# FI sweep: PVC value used as the FI proxy (single-layer uniform fouling).
# FI=0 omitted: at PVC=0 there is no fouling fill, so both arms are identical
# (no A/B contrast). Sweep nonzero FI levels only.
PVC_SWEEP = [5.0, 10.0, 15.0, 20.0, 25.0, 30.0, 35.0, 40.0, 45.0, 50.0]
GEOM_SEEDS_PER_FI = 3      # distinct rock skeletons per FI level
FRACTAL_SEEDS_PER_GEOM = 2  # distinct fractal textures per hetero geometry
MOISTURE = 0.10
BASE_SEED = 4242


def _build_one(pvc: float, seed: int, hetero: bool):
    """Build one scene checkpoint and return (checkpoint, config)."""
    from src.config import GeneratorConfig
    from src.dataset_generator import DatasetGenerator
    from src.work_order import WorkOrder, WorkOrderSystem

    cfg = GeneratorConfig.create_physically_perfect(
        center_freq_hz=FREQ_HZ,
        pvc_min=pvc, pvc_max=pvc,
        moisture_min=MOISTURE, moisture_max=MOISTURE,
        base_seed=seed,
        fouling_heterogeneous=hetero,
    )
    gen = DatasetGenerator(cfg)
    params = {
        'pvc': pvc, 'moisture': MOISTURE,
        'pvc_bottom': pvc, 'pvc_top': pvc,
        'FI_bottom': pvc, 'FI_top': pvc,
        'seed': seed,
    }
    wos = WorkOrderSystem(WorkOrder.from_sampled_params(1, params))
    cp = gen.pipeline.run(wos)
    return cp, cfg


def _hetero_from_homog(homog_text: str, pvc: float, cfg, fractal_seed: int = None) -> str:
    """Derive the HETERO .in from the HOMOG .in by text surgery.

    Replaces ONLY the homogeneous fouling #box line with #soil_peplinski +
    #fractal_box spanning the SAME extents. Every rock (#cylinder/#triangle) and
    all other geometry stay byte-identical, so the matched pair differs ONLY in
    the fouling fill primitive. (Same approach as peplinski_slope.py.)
    """
    import re
    from src.constants import MC

    wf = cfg.fouling_water_frac_base + cfg.fouling_water_frac_slope * (
        min(max(pvc, 0.0), 100.0) / 100.0)
    spread = cfg.fouling_water_frac_spread
    wlo = max(0.001, wf - spread)
    whi = max(wlo + 1e-3, wf + spread)

    box_re = re.compile(
        rf"^#box:\s*([\d.eE+-]+)\s+([\d.eE+-]+)\s+([\d.eE+-]+)\s+"
        rf"([\d.eE+-]+)\s+([\d.eE+-]+)\s+([\d.eE+-]+)\s+{re.escape(MC.FOULING)}\s*$",
        re.MULTILINE)
    m = box_re.search(homog_text)
    if not m:
        raise RuntimeError("Could not find the homogeneous fouling #box to replace.")
    x1, y1, z1, x2, y2, z2 = m.groups()
    repl = (
        f"#soil_peplinski: {cfg.fouling_peplinski_sand_frac} "
        f"{cfg.fouling_peplinski_clay_frac} {cfg.fouling_peplinski_bulk_density} "
        f"{cfg.fouling_peplinski_sand_part_density} {wlo:.4f} {whi:.4f} foul_soil\n"
        f"#fractal_box: {x1} {y1} {z1} {x2} {y2} {z2} "
        f"{cfg.fouling_fractal_dimension} 1 1 1 {cfg.fouling_n_materials} "
        f"foul_soil foul_fb"
        + (f" {fractal_seed}" if fractal_seed is not None else "")
    )
    return box_re.sub(repl, homog_text, count=1)


def generate():
    from src.file_writer import GPRMaxFileWriter

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    # Clear stale files so a smaller re-run doesn't mix with old outputs.
    for old in OUT_DIR.glob("ab_*.in"):
        old.unlink()
    rng = np.random.default_rng(BASE_SEED)
    manifest = []

    for i, pvc in enumerate(PVC_SWEEP):
        for g in range(GEOM_SEEDS_PER_FI):
            seed = int(rng.integers(0, 2**31))

            # 1. HOMOG arm: rocks + solid fouling box.
            cp, cfg = _build_one(pvc, seed, hetero=False)
            stem_h = f"ab_{i:02d}_{g}_homog"
            homog_path = OUT_DIR / f"{stem_h}.in"
            GPRMaxFileWriter.save_scene_checkpoint(
                cp, output_path=str(homog_path), scenario_type="Sim", config=cfg)
            homog_text = homog_path.read_text(encoding="utf-8")
            manifest.append({"FI": pvc, "geom": g, "frac": -1, "seed": seed,
                             "arm": "homog", "stem": stem_h})

            # 2. HETERO arm(s): same rocks, fouling box -> fractal_box. One file
            #    per fractal seed to measure texture-induced variance.
            for fseed_i in range(FRACTAL_SEEDS_PER_GEOM):
                fseed = int(rng.integers(0, 2**31))
                stem_t = f"ab_{i:02d}_{g}_hetero{fseed_i}"
                txt = _hetero_from_homog(homog_text, pvc, cfg, fractal_seed=fseed)
                (OUT_DIR / f"{stem_t}.in").write_text(txt, encoding="utf-8")
                manifest.append({"FI": pvc, "geom": g, "frac": fseed_i, "seed": seed,
                                 "arm": "hetero", "stem": stem_t})

            print(f"  FI={pvc:>4.0f} geom={g} seed={seed} "
                  f"-> 1 homog + {FRACTAL_SEEDS_PER_GEOM} hetero (rocks identical)")

    pd.DataFrame(manifest).to_csv(OUT_DIR / "manifest.csv", index=False)
    _write_run_all(OUT_DIR)
    n_homog = sum(1 for m in manifest if m["arm"] == "homog")
    n_hetero = sum(1 for m in manifest if m["arm"] == "hetero")
    print(f"\nGenerated {len(manifest)} .in files "
          f"({n_homog} homog + {n_hetero} hetero) in {OUT_DIR}")
    print("Next: run run_all.bat through the gprMax env, then --analyze")


def _write_run_all(out_dir: Path):
    bat = r"""@echo off
REM Run all hetero-fouling A/B .in files through gprMax (2D).
setlocal enabledelayedexpansion
set GPRMAX_ENV=gprMax
cd /d "%~dp0"
call "%USERPROFILE%\miniconda3\Scripts\activate.bat" %GPRMAX_ENV%
if errorlevel 1 (
    echo [ERROR] Could not activate conda env "%GPRMAX_ENV%". Edit GPRMAX_ENV.
    pause
)
cd /d D:\gprMax
set COUNT=0
for %%F in ("%~dp0*.in") do (
    set /a COUNT+=1
    echo.
    echo ============================================================
    echo  Running: %%~nxF
    echo ============================================================
    python -m gprMax "%%F" -gpu
    if errorlevel 1 echo [ERROR] gprMax failed on %%~nxF
)
echo.
echo  Done. Ran !COUNT! input files. .out files in: %~dp0
pause
"""
    (out_dir / "run_all.bat").write_text(bat, encoding="utf-8")


def _metric(ez, dt):
    """Band-limited coda spectral centroid (MHz). Identical to peplinski_slope.py."""
    from scipy.signal import welch, butter, filtfilt
    pk = int(np.argmax(np.abs(ez)))
    coda = ez[pk + 20:]
    if len(coda) < 64:
        return np.nan
    sig = coda - coda.mean()
    fs = 1 / dt
    b, a = butter(4, [150e6 / (fs / 2), 800e6 / (fs / 2)], btype="band")
    sig = filtfilt(b, a, sig)
    f, p = welch(sig, fs=fs, nperseg=min(len(sig), 256), nfft=4096)
    band = (f >= 150e6) & (f <= 800e6)
    f, p = f[band], p[band]
    return np.sum(f * p) / np.sum(p) / 1e6 if p.sum() > 0 else np.nan


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
            rows.append({"arm": r["arm"], "FI": float(r["FI"]),
                         "geom": int(r["geom"]), "frac": int(r["frac"]),
                         "c": _metric(*load(op))})
        else:
            print(f"  [missing] {r['stem']}.out")

    d = pd.DataFrame(rows).dropna()
    if d.empty:
        print("No .out files found. Run run_all.bat first.")
        return

    print(f"\nAnalyzed {len(d)} traces, FI {d.FI.min():.0f}-{d.FI.max():.0f}\n")
    print(f"  Reference: homog~0.17   real~3.6 MHz/FI\n")

    def slope_ci(da, n_boot=2000):
        """Slope + bootstrap 95% CI (resample rows with replacement)."""
        s = linregress(da["FI"], da["c"])
        idx = np.arange(len(da))
        boots = []
        rng = np.random.default_rng(0)
        fi = da["FI"].to_numpy(); cc = da["c"].to_numpy()
        for _ in range(n_boot):
            b = rng.choice(idx, size=len(idx), replace=True)
            if len(np.unique(fi[b])) < 2:
                continue
            boots.append(linregress(fi[b], cc[b]).slope)
        lo, hi = np.percentile(boots, [2.5, 97.5]) if boots else (np.nan, np.nan)
        return s, lo, hi

    results = {}
    for arm in ("homog", "hetero"):
        da = d[d.arm == arm]
        if len(da) > 2:
            s, lo, hi = slope_ci(da)
            results[arm] = (s.slope, lo, hi)
            print(f"  {arm:<8} slope = {s.slope:+.3f} MHz/FI  "
                  f"95%CI[{lo:+.3f}, {hi:+.3f}]  "
                  f"(r={s.rvalue:+.2f}, p={s.pvalue:.2g}, n={len(da)})")
        else:
            print(f"  {arm:<8} insufficient points (n={len(da)})")

    # Fractal-seed variance: spread of hetero centroid across fractal seeds for
    # the SAME (FI, geom). If large, the slope is texture-seed-sensitive.
    het = d[d.arm == "hetero"]
    if not het.empty and "geom" in het:
        grp = het.groupby(["FI", "geom"])["c"]
        within_std = grp.std().mean()
        print(f"\n  Fractal-seed within-(FI,geom) centroid std = {within_std:.2f} MHz "
              f"(texture sensitivity)")

    if "homog" in results and "hetero" in results:
        h_slope, h_lo, h_hi = results["hetero"]
        m_slope, _, _ = results["homog"]
        delta = h_slope - m_slope
        print(f"\n  DELTA (hetero - homog) = {delta:+.3f} MHz/FI")
        ci_excludes_zero = (h_lo > 0)
        if delta > 0.2 and h_slope > 0.4 and ci_excludes_zero:
            print("  -> Heterogeneous fouling MOVES the slope (CI excludes 0). "
                  "Worth pursuing; still far from real 3.6.")
        elif delta > 0.2 and h_slope > 0.4:
            print("  -> Slope moved but hetero CI includes 0 — underpowered/noisy. "
                  "Inconclusive.")
        else:
            print("  -> No meaningful improvement. Likely confirms material models "
                  "don't close the gap (cf. project_freq_signature_causes).")

    d.to_csv(OUT_DIR / "results.csv", index=False)
    print(f"\n  Saved {OUT_DIR / 'results.csv'}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--generate", action="store_true")
    ap.add_argument("--analyze", action="store_true")
    a = ap.parse_args()
    if a.generate:
        generate()
    elif a.analyze:
        analyze()
    else:
        print("Use --generate or --analyze")


if __name__ == "__main__":
    main()

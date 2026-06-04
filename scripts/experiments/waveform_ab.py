#!/usr/bin/env python3
"""
A/B test: Ricker vs Gaussian (GSSI-style) source excitation at 400 MHz.

config.source_waveform = "ricker" (default) vs "gaussian" changes ONLY the
#waveform line. A Ricker is zero-mean (symmetric spectrum, no DC); a Gaussian
decays monotonically from DC. So the source spectrum differs and every frequency
feature shifts. Question: does the Gaussian move the SYNTHETIC trace spectrum
toward REAL 400 MHz GPR, or just shift features uniformly with no real-match gain?

Matched pairs via TEXT SURGERY: build the RICKER arm normally, then derive the
GAUSS arm by swapping ONLY the "#waveform: ricker ..." line for
"#waveform: gaussian ...". Identical geometry/rocks/fouling -> the trace
difference is attributable to the excitation alone.

Workflow:
    python scripts/experiments/waveform_ab.py --generate   # writes .in + run_all.bat
    <run run_all.bat through the gprMax conda env>   # .out next to each .in
    python scripts/experiments/waveform_ab.py --analyze     # spectra per arm + vs real

Spectral metric: full-trace power spectrum centroid + dominant freq, plus the
band-limited coda centroid (same band as the fouling test). If a real 400 MHz
reference trace is available, also report the spectral distance per arm.
"""
import sys, argparse
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

OUT_DIR = Path(r"D:\gprMax\user_models\waveform_ab")
FREQ_HZ = 400e6
GAUSS_EXC_FREQ = 400e6   # match centre freq (no 1.71 GHz default at 400 MHz)
# A spread of fouling levels so the comparison isn't tied to one scene type.
PVC_SWEEP = [0.0, 15.0, 30.0, 45.0]
GEOM_SEEDS_PER_FI = 3
MOISTURE = 0.10
BASE_SEED = 909


def _build_ricker(pvc: float, seed: int):
    """Build one RICKER scene checkpoint + config (default waveform)."""
    from src.config import GeneratorConfig
    from src.dataset_generator import DatasetGenerator
    from src.work_order import WorkOrder, WorkOrderSystem

    cfg = GeneratorConfig.create_physically_perfect(
        center_freq_hz=FREQ_HZ,
        pvc_min=pvc, pvc_max=pvc,
        moisture_min=MOISTURE, moisture_max=MOISTURE,
        base_seed=seed,
        source_waveform="ricker",
    )
    gen = DatasetGenerator(cfg)
    params = {
        'pvc': pvc, 'moisture': MOISTURE,
        'pvc_bottom': pvc, 'pvc_top': pvc,
        'FI_bottom': pvc, 'FI_top': pvc,
        'seed': seed,
    }
    wos = WorkOrderSystem(WorkOrder.from_sampled_params(1, params))
    return gen.pipeline.run(wos), cfg


def _gauss_from_ricker(ricker_text: str) -> str:
    """Swap ONLY the #waveform line: ricker -> gaussian @ GAUSS_EXC_FREQ.

    Everything else (geometry, rocks, fouling, source/rx) stays byte-identical.
    """
    import re
    wf_re = re.compile(r"^#waveform:\s+ricker\s+(\S+)\s+(\S+)\s+(\S+)\s*$",
                       re.MULTILINE)
    m = wf_re.search(ricker_text)
    if not m:
        raise RuntimeError("Could not find the '#waveform: ricker ...' line.")
    amp, _freq, name = m.groups()
    repl = f"#waveform: gaussian {amp} {GAUSS_EXC_FREQ:g} {name}"
    return wf_re.sub(repl, ricker_text, count=1)


def generate():
    from src.file_writer import GPRMaxFileWriter

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for old in OUT_DIR.glob("wf_*.in"):
        old.unlink()
    rng = np.random.default_rng(BASE_SEED)
    manifest = []

    for i, pvc in enumerate(PVC_SWEEP):
        for g in range(GEOM_SEEDS_PER_FI):
            seed = int(rng.integers(0, 2**31))

            cp, cfg = _build_ricker(pvc, seed)
            stem_r = f"wf_{i:02d}_{g}_ricker"
            rk_path = OUT_DIR / f"{stem_r}.in"
            GPRMaxFileWriter.save_scene_checkpoint(
                cp, output_path=str(rk_path), scenario_type="Sim", config=cfg)
            ricker_text = rk_path.read_text(encoding="utf-8")
            manifest.append({"FI": pvc, "geom": g, "seed": seed,
                             "arm": "ricker", "stem": stem_r})

            stem_g = f"wf_{i:02d}_{g}_gauss"
            (OUT_DIR / f"{stem_g}.in").write_text(
                _gauss_from_ricker(ricker_text), encoding="utf-8")
            manifest.append({"FI": pvc, "geom": g, "seed": seed,
                             "arm": "gauss", "stem": stem_g})

            print(f"  FI={pvc:>4.0f} geom={g} seed={seed} "
                  f"-> ricker + gauss (geometry identical)")

    pd.DataFrame(manifest).to_csv(OUT_DIR / "manifest.csv", index=False)
    _write_run_all(OUT_DIR)
    print(f"\nGenerated {len(manifest)} .in files "
          f"({len(PVC_SWEEP)*GEOM_SEEDS_PER_FI} matched pairs) in {OUT_DIR}")
    print("Next: run run_all.bat through the gprMax env, then --analyze")


def _write_run_all(out_dir: Path):
    bat = r"""@echo off
REM Run all waveform A/B .in files through gprMax (2D).
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


def _spectrum_feats(ez, dt):
    """Spectral descriptors using the PROJECT's OWN feature definition so sim
    and the real CSV are measured identically (no metric artifact).

    Returns mean_frequency / median_frequency / dominant_frequency in MHz,
    matching src.feature_extraction._extract_frequency_features (|FFT| centroid).
    """
    from src.feature_extraction import _extract_frequency_features
    f = _extract_frequency_features(np.asarray(ez, dtype=float), dt)
    return {
        "mean_freq": f.get("mean_frequency", np.nan) / 1e6,
        "median_freq": f.get("median_frequency", np.nan) / 1e6,
        "dom_freq": f.get("dominant_frequency", np.nan) / 1e6,
    }


def analyze():
    man = pd.read_csv(OUT_DIR / "manifest.csv")

    from src.data_loader import read_ascan

    def load(p):
        d = read_ascan(p)
        return d["signal"].astype(float), d["dt"]

    rows = []
    for _, r in man.iterrows():
        op = OUT_DIR / f"{r['stem']}.out"
        if op.exists():
            feats = _spectrum_feats(*load(op))
            rows.append({"arm": r["arm"], "FI": float(r["FI"]),
                         "geom": int(r["geom"]), **feats})
        else:
            print(f"  [missing] {r['stem']}.out")

    d = pd.DataFrame(rows).dropna()
    if d.empty:
        print("No .out files found. Run run_all.bat first.")
        return

    print(f"\nAnalyzed {len(d)} traces ({d.FI.min():.0f}-{d.FI.max():.0f} FI)\n")
    cols = ["mean_freq", "median_freq", "dom_freq"]
    summary = d.groupby("arm")[cols].agg(["mean", "std"])
    print("  Spectral descriptors (MHz), mean +/- std per arm:")
    for arm in ("ricker", "gauss"):
        if arm in summary.index:
            row = summary.loc[arm]
            print(f"    {arm:<7} "
                  f"mean={row[('mean_freq','mean')]:6.1f}+/-{row[('mean_freq','std')]:4.1f}  "
                  f"median={row[('median_freq','mean')]:6.1f}+/-{row[('median_freq','std')]:4.1f}  "
                  f"dom={row[('dom_freq','mean')]:6.1f}+/-{row[('dom_freq','std')]:4.1f}")

    # Paired delta (same FI,geom): gauss - ricker
    piv = d.pivot_table(index=["FI", "geom"], columns="arm", values=cols)
    print("\n  Paired delta (gauss - ricker), mean over pairs:")
    for c in cols:
        if ("gauss" in piv[c].columns) and ("ricker" in piv[c].columns):
            delta = (piv[c]["gauss"] - piv[c]["ricker"]).dropna()
            print(f"    {c:<12} {delta.mean():+7.1f} MHz  (n={len(delta)})")

    # Real 400 MHz reference: the n=101 Site-1 feature CSV. Metric is identical
    # (sim uses the same _extract_frequency_features), so this is apples-to-apples.
    real_csv = ROOT / "docs" / "input" / "feature_dataset_real.csv"
    if real_csv.exists():
        rr = pd.read_csv(real_csv)
        real = {"mean_freq": rr["mean_frequency"].median() / 1e6,
                "median_freq": rr["median_frequency"].median() / 1e6,
                "dom_freq": rr["dominant_frequency"].median() / 1e6}
        print(f"\n  REAL 400MHz (n={len(rr)} Site-1, median): "
              f"mean={real['mean_freq']:.0f}  median={real['median_freq']:.0f}  "
              f"dom={real['dom_freq']:.0f} MHz")
        print("\n  |sim - real| per arm (smaller = closer to reality):")
        better = 0
        for c in cols:
            rk = abs(d[d.arm == "ricker"][c].mean() - real[c])
            gs = abs(d[d.arm == "gauss"][c].mean() - real[c])
            mark = "GAUSS closer" if gs < rk else "ricker closer"
            if gs < rk:
                better += 1
            print(f"    {c:<12} ricker {rk:6.1f}  vs  gauss {gs:6.1f}  -> {mark}")
        print(f"\n  Gaussian closer to real on {better}/{len(cols)} descriptors.")
        if better >= 2:
            print("  -> Gaussian excitation moves synthetic spectrum TOWARD real. "
                  "Worth adopting (pending wider n).")
        else:
            print("  -> Gaussian does NOT improve real-match. A shift, not a fix.")
    else:
        print(f"\n  (Real CSV not found at {real_csv}; sim-vs-sim shift only.)")
        print("  NOTE: a shift alone is NOT a win — it must move TOWARD real.")

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

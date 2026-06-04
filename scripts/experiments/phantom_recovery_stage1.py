#!/usr/bin/env python3
"""
Stage 1 of the 80k phantom-rock recovery (docs/studies/phantom_rock_80k_recovery_plan.md).

Validation-subset A/B on the SAME samples:
  PHANTOM arm = the existing 80k .in as-is (triangle thickness 0.004 < dz=0.0132
                -> rocks dropped from the grid).
  ROCK arm    = identical .in with ONLY the rock z-extent fixed (thickness ->
                domain_z) so rocks are actually rasterized.
Everything else byte-identical -> a clean measure of how much the phantom-rock
bug actually changed the traces/features the 0.7083 baseline learned from.

    python scripts/experiments/phantom_recovery_stage1.py --generate   # subset + run_all.bat
    <run run_all.bat>
    python scripts/experiments/phantom_recovery_stage1.py --analyze     # phantom vs rock
"""
import sys, argparse, re, shutil
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))
from src.dataset_io import load_features

SRC_DIR = ROOT / "output" / "gpr_synth_dataset_80k"
LABELS = ROOT / "output" / "dataset_80k_features.parquet"
OUT_DIR = Path(r"D:\gprMax\user_models\phantom_recovery_s1")
N_PER_CLASS = 10
SEED = 1234


def _dz_of(in_text: str) -> float:
    m = re.search(r"#dx_dy_dz:\s*\S+\s+\S+\s+([\d.eE+-]+)", in_text)
    return float(m.group(1)) if m else None


def _fix_rock_z(in_text: str, dz: float) -> str:
    """Bump every sub-dz rock z-extent up to the full z-cell (dz).

    #triangle: ... thickness mat   -> thickness >= dz
    #cylinder: x1 y1 z1 x2 y2 z2 r mat -> z2-z1 >= dz (set z1=0, z2=dz)
    """
    out = []
    for ln in in_text.splitlines():
        if ln.startswith("#triangle:"):
            t = ln.split()
            # token 10 (0-idx) is thickness for #triangle: x1 y1 z1 x2 y2 z2 x3 y3 z3 th mat
            if len(t) >= 12 and float(t[10]) < dz:
                t[10] = f"{dz:g}"
                ln = " ".join(t)
        elif ln.startswith("#cylinder:"):
            t = ln.split()
            # #cylinder: x1 y1 z1 x2 y2 z2 r mat -> tokens 3 and 6 are z1,z2
            if len(t) >= 9 and (float(t[6]) - float(t[3])) < dz:
                t[3] = "0"
                t[6] = f"{dz:g}"
                ln = " ".join(t)
        out.append(ln)
    return "\n".join(out) + "\n"


def generate():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for old in OUT_DIR.glob("pr_*.in"):
        old.unlink()

    df = load_features(LABELS, columns=["sample_id", "label", "pvc", "Lab_FI"])
    rng = np.random.default_rng(SEED)
    picks = []
    for cls in sorted(df.label.unique()):
        pool = df[df.label == cls]
        take = pool.sample(min(N_PER_CLASS, len(pool)), random_state=SEED)
        picks.append(take)
    subset = pd.concat(picks).reset_index(drop=True)

    manifest = []
    for _, r in subset.iterrows():
        sid = int(r.sample_id)
        src = SRC_DIR / f"s_{sid:05d}.in"
        if not src.exists():
            print(f"  [missing src] {src.name}")
            continue
        txt = src.read_text(encoding="utf-8", errors="ignore")
        dz = _dz_of(txt)
        if dz is None:
            print(f"  [no dz] {src.name}")
            continue
        # PHANTOM arm: as-is
        (OUT_DIR / f"pr_{sid:05d}_phantom.in").write_text(txt, encoding="utf-8")
        # ROCK arm: z-extent fixed
        (OUT_DIR / f"pr_{sid:05d}_rock.in").write_text(_fix_rock_z(txt, dz), encoding="utf-8")
        for arm in ("phantom", "rock"):
            manifest.append({"sample_id": sid, "label": r.label, "pvc": float(r.pvc),
                             "Lab_FI": float(r.Lab_FI), "arm": arm,
                             "stem": f"pr_{sid:05d}_{arm}"})
        print(f"  s_{sid:05d} [{r.label}] pvc={r.pvc:.0f} -> phantom + rock")

    pd.DataFrame(manifest).to_csv(OUT_DIR / "manifest.csv", index=False)
    _write_run_all(OUT_DIR)
    n = len(manifest) // 2
    print(f"\nGenerated {len(manifest)} .in ({n} samples x 2 arms) in {OUT_DIR}")
    print("Run run_all.bat, then --analyze")


def _write_run_all(out_dir: Path):
    bat = r"""@echo off
REM Phantom-recovery Stage 1: run each .in (single A-scan) through gprMax.
setlocal enabledelayedexpansion
set GPRMAX_ENV=gprMax
cd /d "%~dp0"
call "%USERPROFILE%\miniconda3\Scripts\activate.bat" %GPRMAX_ENV%
if errorlevel 1 ( echo [ERROR] activate %GPRMAX_ENV% & pause )
cd /d D:\gprMax
set COUNT=0
for %%F in ("%~dp0*.in") do (
    set /a COUNT+=1
    python -m gprMax "%%F" -gpu
    if errorlevel 1 echo [ERROR] failed on %%~nxF
)
echo. & echo Done. Ran !COUNT! files.
pause
"""
    (out_dir / "run_all.bat").write_text(bat, encoding="utf-8")


def _feats(ez, dt):
    from src.feature_extraction import _extract_frequency_features
    from scipy.signal import welch, butter, filtfilt
    f = _extract_frequency_features(np.asarray(ez, float), dt)
    out = {"mean_freq": f["mean_frequency"]/1e6, "dom_freq": f["dominant_frequency"]/1e6}
    # coda energy fraction (rocks add late scattering energy)
    pk = int(np.argmax(np.abs(ez)))
    total = np.sum(ez.astype(float)**2)
    coda = np.sum(ez[pk+20:].astype(float)**2)
    out["coda_energy_frac"] = coda/total if total > 0 else np.nan
    return out


def analyze():
    from src.data_loader import read_ascan
    man = pd.read_csv(OUT_DIR / "manifest.csv")

    def load(p):
        d = read_ascan(p)
        return d["signal"].astype(float), d["dt"]

    rows = []
    for _, r in man.iterrows():
        op = OUT_DIR / f"{r['stem']}.out"
        if op.exists():
            rows.append({**r.to_dict(), **_feats(*load(op))})
        else:
            print(f"  [missing] {r['stem']}.out")
    d = pd.DataFrame(rows).dropna()
    if d.empty:
        print("No .out files. Run run_all.bat first."); return

    print(f"\nAnalyzed {len(d)} traces ({d.sample_id.nunique()} samples)\n")

    # Per-sample: how different is rock vs phantom?
    fcols = ["mean_freq", "dom_freq", "coda_energy_frac"]
    piv = d.pivot_table(index="sample_id", columns="arm", values=fcols)
    print("  Phantom vs Rock (paired, same sample):")
    n_identical = 0
    for sid in piv.index:
        pass
    # trace-level identity check
    print("\n  Per-feature mean +/- std by arm:")
    for arm in ("phantom", "rock"):
        da = d[d.arm == arm]
        print(f"    {arm:<8} " + "  ".join(f"{c}={da[c].mean():7.3f}" for c in fcols))

    print("\n  Paired delta (rock - phantom):")
    for c in fcols:
        if ("rock" in piv[c].columns) and ("phantom" in piv[c].columns):
            delta = (piv[c]["rock"] - piv[c]["phantom"]).dropna()
            frac_changed = (delta.abs() > 1e-6).mean()
            print(f"    {c:<16} mean {delta.mean():+8.3f}  |  {frac_changed*100:.0f}% of samples changed")

    # Headline: did rocks change the traces at all?
    print("\n  => If deltas are ~0, the phantom bug barely affected the features")
    print("     (full 80k re-run not worth it). If large, the 0.7083 baseline is invalid.")
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

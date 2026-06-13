#!/usr/bin/env python3
"""
Calibration round 2 — GEOMETRY/HETEROGENEITY search at pinned bulk velocities.

Round 1 (dzt_calib_poc.py) verdict: no material combo reaches the real coda
(target out-of-hull on 6/8 features); feature ranges across 150 material
combos were narrow -> coda is geometry-dominated. This round fixes bulk
velocities analytically and searches geometry:

  F1 rf_fouled   [0.50, 0.75]  fouled-layer rock fraction (skeleton breakdown;
                               matrix eps solved from CRIM to hold bulk 11.3)
  F2 frac_dim    [1.5, 3.0]    fractal dimension of the fines fractal_box
                               (Li-style discrete random medium texture)
  F3 rough_amp   [0.0, 0.08]   clean/fouled interface roughness (m)
  F4 trans_th    [0.0, 0.15]   fouling transition creeping into clean layer (m)
  F6 clean_phi   [0.15, 0.40]  clean-layer porosity (Benedetto: real loose
                               ballast is 39% voids, our packer gives 15%;
                               rock eps co-solved to hold bulk 3.45)

Pinned: clean bulk eps 3.45 and fouled bulk 11.3 (pit ID 11 interface picks),
rocks shared between layers (co-solved eps, sigma 0.001), subgrade 15/0.02,
geometry 0.50/0.29 m (pandoscope), H(f) system correction, real-dt resample.
Fines matrix = #soil_peplinski water content solved to the CRIM matrix eps
(field fouling signal is moisture - Benedetto), so dispersion comes for free.

Per LHS point, 5 packing seeds (templates) -> 30 x 5 = 150 sims.
Pre-registered success criteria: (a) per-feature hull coverage of the 6
OUT features, (b) best seed-mean RMS-z (<=2 ~ within cohort noise),
(c) envelope-peak arrival sanity 6.2/12.7 +/- 0.5 ns.

Stages:
    python scripts/experiments/dzt_calib_geo.py --templates
    python scripts/experiments/dzt_calib_geo.py --spike
    python scripts/experiments/dzt_calib_geo.py --generate
    python scripts/experiments/dzt_calib_geo.py --run
    python scripts/experiments/dzt_calib_geo.py --analyze
"""

import argparse
import importlib.util
import json
import random
import re
import subprocess
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

_spec = importlib.util.spec_from_file_location(
    "dzt_calib_poc", ROOT / "scripts" / "experiments" / "dzt_calib_poc.py")
poc = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(poc)

OUT_DIR = ROOT / "output" / "dzt_calib_geo"
SIM_DIR = Path("D:/gprMax/user_models/dzt_calib_geo")
TEMPLATE_SEEDS = [1234, 2001, 2002, 2003, 2004]

# pinned physics (sqrt-CRIM throughout)
SQRT_CLEAN_BULK = np.sqrt(3.45)    # pit ID 11 interface pick
SQRT_FOUL_BULK = np.sqrt(11.3)     # pit ID 11 interface pick
EPS_M_CAP = 35.0                   # max physical wet-fines matrix eps
SUBGRADE = (15.0, 0.02)
ROCK_SIGMA = 0.001

CLEAN_Y = (0.79, 1.29)             # clean ballast band in the template
FOUL_Y = (0.10, 0.79)              # fouled ballast band in the template (extended)
DOMAIN_X = 2.4

PARAM_SPACE = {
    "h_clean":   (0.40, 0.70, False),
    "h_foul":    (0.15, 0.45, False),
    "rf_fouled": (0.50, 0.75, False),
    "frac_dim":  (1.5, 3.0, False),
    "rough_amp": (0.0, 0.10, False),
    "trans_th":  (0.0, 0.20, False),
    "clean_phi": (0.15, 0.40, False),
}
N_LHS = 30
SEED = 77


# --------------------------------------------------------------- pinned solves
def rock_eps_for_clean(phi: float) -> float:
    """CRIM: (1-phi)*sqrt(eps_r) + phi*1 = sqrt(3.45)."""
    return float(((SQRT_CLEAN_BULK - phi) / (1.0 - phi)) ** 2)


def matrix_eps_for_fouled(rf: float, eps_rock: float) -> float:
    """CRIM: rf*sqrt(eps_rock) + (1-rf)*sqrt(eps_m) = sqrt(11.3)."""
    s = (SQRT_FOUL_BULK - rf * np.sqrt(eps_rock)) / (1.0 - rf)
    return float(min(s ** 2, EPS_M_CAP))


def peplinski_eps(theta: float, sand=0.5, clay=0.5, rho_b=1.5, rho_s=2.66) -> float:
    """Peplinski 1995 real permittivity (0.3-1.3 GHz band form)."""
    alpha = 0.65
    eps_s = (1.01 + 0.44 * rho_s) ** 2 - 0.062
    eps_fw = 80.1
    beta = 1.2748 - 0.519 * sand - 0.152 * clay
    inner = 1 + (rho_b / rho_s) * (eps_s ** alpha - 1) \
        + (theta ** beta) * (eps_fw ** alpha) - theta
    return 1.15 * inner ** (1 / alpha) - 0.68


def water_for_eps(eps_target: float) -> float:
    lo, hi = 0.001, 0.50
    for _ in range(60):
        mid = (lo + hi) / 2
        if peplinski_eps(mid) < eps_target:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


# ----------------------------------------------------------------- templates
TOML = """\
[sim]
title             = "calib geo template seed {seed}"
freq_hz           = 400e6
domain_x          = {domain_x}
antenna_clearance = 1.0
air_buffer        = 0.1
rx_spacing        = 0.0
seed              = {seed}
time_window       = 35e-9

[source]
waveform     = "ricker"
amplitude    = 1.0
polarization = "z"

[[layer]]
name = "subgrade"
thickness = 0.10
eps = 15.0
sigma = 0.02

[[layer]]
name = "fouled_ballast"
thickness = 0.69
packed = true
eps = 4.0
sigma = 0.001
matrix = "fouling"

[[layer]]
name = "ballast"
thickness = 0.50
packed = true
matrix = "free_space"
"""


def make_templates() -> None:
    SIM_DIR.mkdir(parents=True, exist_ok=True)
    gen = ROOT / "scripts" / "pipeline" / "generate_in_files.py"
    for seed in TEMPLATE_SEEDS:
        toml = SIM_DIR / f"tpl_{seed}.toml"
        toml.write_text(TOML.format(seed=seed, domain_x=DOMAIN_X), encoding="utf-8")
        res = subprocess.run(
            [sys.executable, str(gen), str(SIM_DIR / f"tpl_{seed}.in"),
             "--layers-file", str(toml)], capture_output=True, text=True)
        ok = (SIM_DIR / f"tpl_{seed}.in").exists()
        print(f"template seed {seed}: {'ok' if ok else 'FAIL'}")
        if not ok:
            print(res.stdout[-400:], res.stderr[-400:])


# ---------------------------------------------------- template .in dissection
TRI_RE = re.compile(
    r"^#triangle: ([\d.eE+-]+) ([\d.eE+-]+) [\d.eE+-]+ "
    r"([\d.eE+-]+) ([\d.eE+-]+) [\d.eE+-]+ "
    r"([\d.eE+-]+) ([\d.eE+-]+) [\d.eE+-]+ [\d.eE+-]+ (\w+)\s*$")


def parse_template(path: Path):
    """Split a template .in into: header lines (everything except geometry),
    box lines, and rock fans grouped by (material, apex vertex)."""
    header, boxes, fans = [], [], {}
    order = []
    for line in path.read_text(encoding="utf-8").splitlines():
        m = TRI_RE.match(line)
        if m:
            x1, y1, x2, y2, x3, y3, mat = m.groups()
            key = (mat, x1, y1)
            if key not in fans:
                fans[key] = {"lines": [], "area": 0.0, "mat": mat, "y_apex": float(y1)}
                order.append(key)
            a = abs((float(x2) - float(x1)) * (float(y3) - float(y1))
                    - (float(x3) - float(x1)) * (float(y2) - float(y1))) / 2
            fans[key]["lines"].append(line)
            fans[key]["area"] += a
        elif line.startswith("#box:"):
            boxes.append(line)
        elif line.startswith("#material:"):
            continue  # materials fully rewritten per candidate
        else:
            header.append(line)
    rock_fans = [fans[k] for k in order]
    return header, boxes, rock_fans


def thin_fans(fans, target_area, rng):
    """Randomly keep whole fans until their area is closest to target_area."""
    fans = fans[:]
    rng.shuffle(fans)
    kept, area = [], 0.0
    for f in fans:
        if area + f["area"] <= target_area + 1e-6:
            kept.append(f)
            area += f["area"]
    return kept, area


def build_candidate(template: Path, out_path: Path, p: dict, cand_seed: int) -> dict:
    header, boxes, fans = parse_template(template)
    
    # Dynamic layer boundary calculations (top of ballast fixed at 1.29 m)
    ballast_top_y = 1.29
    h_clean = p["h_clean"]
    h_foul = p["h_foul"]
    interface_y = ballast_top_y - h_clean
    subgrade_y = ballast_top_y - (h_clean + h_foul)

    # Classify rocks dynamically based on their y_apex coordinate
    clean = [f for f in fans if f["y_apex"] >= interface_y]
    foul = [f for f in fans if subgrade_y <= f["y_apex"] < interface_y]

    clean_area = DOMAIN_X * h_clean
    foul_area = DOMAIN_X * h_foul

    rng = random.Random(cand_seed)
    kept_clean, a_clean = thin_fans(clean, (1 - p["clean_phi"]) * clean_area, rng)
    kept_foul, a_foul = thin_fans(foul, p["rf_fouled"] * foul_area, rng)

    # solve eps from ACHIEVED fractions so the pinned bulks hold exactly
    # (the template tops out at rf~0.70 in the clean band: settling slack)
    rf_clean = a_clean / clean_area if clean_area > 0 else 0.0
    rf_foul = a_foul / foul_area if foul_area > 0 else 0.0
    eps_rock = rock_eps_for_clean(1.0 - rf_clean)
    eps_m = matrix_eps_for_fouled(rf_foul, eps_rock)
    theta = water_for_eps(eps_m)

    # transition material: CRIM midpoint between the two pinned bulks
    eps_mid = ((SQRT_CLEAN_BULK + SQRT_FOUL_BULK) / 2) ** 2
    t = p["trans_th"]

    lines = list(header)
    lines.append(f"#material: {SUBGRADE[0]} {SUBGRADE[1]} 1 0.0 subgrade")
    lines.append(f"#material: {eps_rock:.4f} {ROCK_SIGMA} 1 0.0 bal_rock")
    lines.append(f"#material: {eps_mid:.4f} 0.01 1 0.0 trans_mix")
    lines.append(f"#soil_peplinski: 0.5 0.5 1.5 2.66 "
                 f"{max(theta - 0.02, 0.001):.4f} {min(theta + 0.02, 0.50):.4f} fines")
    # geometry, paint order matters: subgrade, transition band, fines fractal
    # box (+ roughness), then rocks on top
    lines.append(f"#box: 0 0 0 {DOMAIN_X} {subgrade_y:.4f} 0.005 subgrade")
    if t >= 0.005:
        lines.append(f"#box: 0 {interface_y:.4f} 0 {DOMAIN_X} "
                     f"{interface_y + t:.4f} 0.005 trans_mix")
    lines.append(f"#fractal_box: 0 {subgrade_y:.4f} 0 {DOMAIN_X} {interface_y:.4f} 0.005 "
                 f"{p['frac_dim']:.3f} 1 1 1 20 fines fines_box {cand_seed}")
    if p["rough_amp"] >= 0.005:
        lo = interface_y - p["rough_amp"]
        hi = interface_y + p["rough_amp"]
        lines.append(f"#add_surface_roughness: 0 {interface_y:.4f} 0 {DOMAIN_X} "
                     f"{interface_y:.4f} 0.005 {p['frac_dim']:.3f} 1 1 "
                     f"{lo:.4f} {hi:.4f} fines_box {cand_seed}")
    for f in kept_foul:
        lines.extend(ln.replace(f["mat"], "bal_rock") for ln in f["lines"])
    for f in kept_clean:
        lines.extend(ln.replace(f["mat"], "bal_rock") for ln in f["lines"])
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return {"eps_rock": round(eps_rock, 3), "eps_m": round(eps_m, 2),
            "theta": round(theta, 3), "rf_clean_actual": round(a_clean / clean_area, 3),
            "rf_fouled_actual": round(a_foul / foul_area, 3),
            "eps_m_clamped": bool(eps_m >= EPS_M_CAP - 1e-9)}


# ----------------------------------------------------------------- LHS + run
def lhs(n, seed):
    rng = np.random.default_rng(seed)
    dims = len(PARAM_SPACE)
    u = (rng.permuted(np.tile(np.arange(n), (dims, 1)), axis=1).T
         + rng.random((n, dims))) / n
    cols = {k: lo + u[:, j] * (hi - lo)
            for j, (k, (lo, hi, _)) in enumerate(PARAM_SPACE.items())}
    df = pd.DataFrame(cols)
    df.insert(0, "cand", [f"g{i:03d}" for i in range(n)])
    return df


def generate() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    plan = lhs(N_LHS, SEED)
    rows = []
    for _, r in plan.iterrows():
        for si, seed in enumerate(TEMPLATE_SEEDS):
            name = f"{r.cand}_s{si}"
            meta = build_candidate(SIM_DIR / f"tpl_{seed}.in",
                                   SIM_DIR / f"{name}.in",
                                   dict(r), cand_seed=seed * 1000 + int(r.cand[1:]))
            rows.append({**dict(r), "sim": name, "tpl_seed": seed, **meta})
    pd.DataFrame(rows).to_csv(OUT_DIR / "geo_plan.csv", index=False)
    print(f"generated {len(rows)} .in files -> {SIM_DIR}")
    clamped = sum(r["eps_m_clamped"] for r in rows)
    print(f"eps_m clamped at {EPS_M_CAP} in {clamped}/{len(rows)} sims")


def run_batch(pattern="g*.in") -> None:
    todo = sorted(p for p in SIM_DIR.glob(pattern)
                  if not p.with_suffix(".out").exists())
    print(f"{len(todo)} sims to run")
    t0 = time.time()
    for i, f in enumerate(todo):
        res = subprocess.run([poc.GPRMAX_PY, "-m", "gprMax", str(f), "-n", "1"],
                             capture_output=True, text=True, cwd=str(SIM_DIR))
        ok = f.with_suffix(".out").exists()
        el = time.time() - t0
        print(f"[{i+1}/{len(todo)}] {f.stem} {'ok' if ok else 'FAIL'} "
              f"({el/60:.1f} min, ETA {el/(i+1)*(len(todo)-i-1)/60:.0f} min)", flush=True)
        if not ok:
            print(res.stderr[-600:])
    print("batch done")


# ------------------------------------------------------------------- analysis
def arrival_peaks(sig, dt):
    from scipy.signal import hilbert, find_peaks
    from src.signal_processing import dewow
    s = dewow(sig - sig.mean(), 50)
    pk = int(np.argmax(np.abs(s)))
    env = np.abs(hilbert(s / np.abs(s).max()))[pk:]
    peaks, props = find_peaks(env, prominence=0.005)
    prom = props.get("prominences", np.ones(len(peaks)))
    top = sorted(peaks[np.argsort(prom)[::-1][:4]] * dt * 1e9)
    return top


def analyze() -> None:
    tgt = json.loads((poc.OUT_DIR / "target_features.json").read_text())
    feats = list(tgt["features"].keys())
    t_vec = np.array([tgt["features"][k] for k in feats])
    s_vec = np.array([tgt["spread_mad"][k] for k in feats])

    plan = pd.read_csv(OUT_DIR / "geo_plan.csv")
    rows = []
    for _, r in plan.iterrows():
        out = SIM_DIR / f"{r.sim}.out"
        if not out.exists():
            continue
        ez, dt = poc.load_out(out)
        sig, dt_rs = poc.resample_to_real(ez, dt)
        sig = poc.apply_system_response(sig, dt_rs)
        fdict = poc.extract_fitness_feats(poc.prep_trace(sig), dt_rs, r.sim)
        if set(feats) - set(fdict):
            continue
        rec = dict(r)
        rec.update({f"f_{k}": fdict[k] for k in feats})
        rows.append(rec)
    df = pd.DataFrame(rows)
    df.to_csv(OUT_DIR / "geo_results_sims.csv", index=False)

    # aggregate over the 5 seeds per candidate
    fcols = [f"f_{k}" for k in feats]
    agg = df.groupby("cand").agg({**{c: "mean" for c in fcols},
                                  **{k: "first" for k in PARAM_SPACE}})
    z = (agg[fcols].to_numpy() - t_vec) / s_vec
    agg["fitness"] = np.sqrt((z ** 2).mean(axis=1))
    agg = agg.sort_values("fitness")
    agg.to_csv(OUT_DIR / "geo_results_agg.csv")

    print(f"analyzed {len(df)} sims -> {len(agg)} candidates (seed-mean)")
    print("\nTop 8 (seed-mean fitness; round-1 best with H was 6.46):")
    print(agg[list(PARAM_SPACE) + ["fitness"]].head(8).round(4).to_string())

    print("\nPre-registered hull check (sim cloud = ALL individual sims):")
    F = df[fcols].to_numpy()
    n_in = 0
    for j, k in enumerate(feats):
        lo, hi = F[:, j].min(), F[:, j].max()
        ok = lo <= t_vec[j] <= hi
        n_in += ok
        print(f"  {k:28s} target={t_vec[j]:+.4g}  sim=[{lo:+.4g}, {hi:+.4g}]  "
              f"{'in' if ok else 'OUT'}")
    print(f"  -> {n_in}/{len(feats)} features covered (round 1: 2/8)")

    from sklearn.ensemble import RandomForestRegressor
    X = agg[list(PARAM_SPACE)]
    rf = RandomForestRegressor(400, random_state=SEED).fit(X, agg["fitness"])
    imp = pd.Series(rf.feature_importances_, index=X.columns).sort_values(ascending=False)
    print("\nMisfit-surrogate importance:")
    print(imp.round(3).to_string())

    best = agg.index[0]
    sims = df[df.cand == best]
    print(f"\nBest candidate {best}: per-feature z (seed-mean), seed spread in ():")
    zb = (sims[fcols].mean().to_numpy() - t_vec) / s_vec
    sd = sims[fcols].std().to_numpy() / s_vec
    for k, zz, ss in zip(feats, zb, sd):
        print(f"  {k:28s} z={zz:+7.2f}  (seed sd {ss:.2f})")

    # arrival sanity on best candidate, first seed
    ez, dt = poc.load_out(SIM_DIR / f"{best}_s0.out")
    sig, dt_rs = poc.resample_to_real(ez, dt)
    print(f"\nArrival sanity {best}_s0 (expect ~6.2 and ~12.7 ns): "
          f"{[round(x,1) for x in arrival_peaks(sig, dt_rs)]}")


# ----------------------------------------------------------------------- main
def spike() -> None:
    """3 extreme candidates end-to-end before committing the LHS."""
    cases = [
        ("spike_lo", dict(h_clean=0.40, h_foul=0.15, rf_fouled=0.75, frac_dim=1.5,
                          rough_amp=0.0, trans_th=0.0, clean_phi=0.15)),
        ("spike_mid", dict(h_clean=0.55, h_foul=0.30, rf_fouled=0.60, frac_dim=2.2,
                           rough_amp=0.05, trans_th=0.10, clean_phi=0.28)),
        ("spike_hi", dict(h_clean=0.70, h_foul=0.45, rf_fouled=0.50, frac_dim=3.0,
                          rough_amp=0.10, trans_th=0.20, clean_phi=0.40)),
    ]
    tpl = SIM_DIR / f"tpl_{TEMPLATE_SEEDS[0]}.in"
    for name, p in cases:
        meta = build_candidate(tpl, SIM_DIR / f"{name}.in", p, cand_seed=999)
        print(f"{name}: {meta}")
    run_batch("spike_*.in")
    for name, _ in cases:
        out = SIM_DIR / f"{name}.out"
        if not out.exists():
            print(f"{name}: NO OUTPUT")
            continue
        ez, dt = poc.load_out(out)
        sig, dt_rs = poc.resample_to_real(ez, dt)
        sigc = poc.apply_system_response(sig, dt_rs)
        f = poc.extract_fitness_feats(poc.prep_trace(sigc), dt_rs, name)
        tgt = json.loads((poc.OUT_DIR / "target_features.json").read_text())
        z = [(f[k] - tgt["features"][k]) / tgt["spread_mad"][k] for k in f]
        print(f"{name}: RMS-z={np.sqrt(np.mean(np.array(z)**2)):.2f}  "
              f"arrivals={[round(x,1) for x in arrival_peaks(sig, dt_rs)]}")


def main():
    ap = argparse.ArgumentParser()
    for s in ["templates", "spike", "generate", "run", "analyze"]:
        ap.add_argument(f"--{s}", action="store_true")
    a = ap.parse_args()
    if a.templates:
        make_templates()
    elif a.spike:
        spike()
    elif a.generate:
        generate()
    elif a.run:
        run_batch()
    elif a.analyze:
        analyze()
    else:
        print("stages: --templates | --spike | --generate | --run | --analyze")


if __name__ == "__main__":
    main()

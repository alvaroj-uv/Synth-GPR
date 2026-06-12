#!/usr/bin/env python3
"""
Metaheuristic calibration POC: fit gprMax material parameters so the simulated
coda matches a real DZT block, anchored at a pandoscope pit.

DATASET RULE (user directive 2026-06-12): D:/Codigo/Data (raw DZTs) and
D:/Codigo/Data_Labled (112 matched traces + pandoscope) are DIFFERENT sets —
never mix. Everything here (target signal, geometry, FI, spread) comes from
Data_Labled only.

Anchor: pit ID 11 — FI = 27.0, clean ballast 0-0.50 m, fouled 0.50-0.79 m.

Design (per session decision):
  - Target = pit ID 11's own raw matched trace (df_GPR_match_filtrado),
    peak-normalized, dewowed.
  - Fitness = z-scored distance on scale-invariant v3 coda/att features,
    normalized by the robust spread across pits of similar FI (so "good
    fit" means "within the variability of same-class pits").
  - Forward model: deterministic layered scene (fixed seed packing) via the
    TOML layers mode; only material params vary across candidates.
  - Search: Latin hypercube (4 params) -> RF surrogate -> verify best.

Stages:
    python scripts/experiments/dzt_calib_poc.py --target     # build real target
    python scripts/experiments/dzt_calib_poc.py --generate   # LHS -> .in files
    python scripts/experiments/dzt_calib_poc.py --run        # run gprMax batch
    python scripts/experiments/dzt_calib_poc.py --analyze    # fitness + surrogate
"""

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

from src.constants import SC

# ---------------------------------------------------------------- anchor pit
LABELED_DIR = Path("D:/Codigo/Data_Labled")
MATCH_PKL = LABELED_DIR / "Señales_Brutas" / "df_GPR_match_filtrado.pkl"
PIT = {"ID": 11, "FI": 27.0, "clean_ballast_m": 0.50, "fouled_ballast_m": 0.29}
SPREAD_FI_BAND = 5.0          # pits within +/- this FI of the anchor set the spread

DT_REAL = 50.0e-9 / 511       # 50 ns window over 511 intervals (GSSI header)

OUT_DIR = ROOT / "output" / "dzt_calib_poc"
SIM_DIR = Path("D:/gprMax/user_models/dzt_calib_poc")
GPRMAX_PY = "C:/Users/barba/.conda/envs/gprMax/python.exe"

# ---------------------------------------------------------------- search space
# (lo, hi, log?) — fouled-ballast MATRIX and subgrade materials.
PARAM_SPACE = {
    "foul_eps":   (2.0, 12.0, False),
    "foul_sigma": (1e-4, 0.1, True),
    "sub_eps":    (5.0, 20.0, False),
    "sub_sigma":  (1e-3, 0.1, True),
}
N_LHS = 150
SEED = 42

# Fitness features: scale-invariant coda/att set (validated sensitive in the
# eps sweep). Final list is intersected with what the extractor produces.
FITNESS_FEATURES = [
    "coda_median_frequency",
    "coda_spectral_centroid",
    "coda_spectral_flatness",
    "att_env_decay_rate",
    "att_band_low_decay",
    "att_band_mid_decay",
    "att_band_high_decay",
    "att_centroid_slope_mhz_ns",
    "att_instfreq_mean_mhz",
]


# ------------------------------------------------------------------ real side
def load_labeled_traces():
    """All 112 matched raw traces + FI, from Data_Labled ONLY.

    Stored columns 0..510 hold the raw samples; column 0 is the -2^24
    instrument marker -> dropped."""
    match = pd.read_pickle(MATCH_PKL)
    pan = pd.read_pickle(LABELED_DIR / "Mediciones_FI" / "df_pandoscope_med.pkl")
    df = match.merge(pan[["ID", "FI_Estimado_Medio_JRO_Final"]], on="ID")
    samp_cols = [c for c in match.columns if isinstance(c, int)][1:]  # drop marker col 0
    sig = df[samp_cols].to_numpy(dtype=float)
    return df["ID"].to_numpy(), df["FI_Estimado_Medio_JRO_Final"].to_numpy(), sig


def prep_trace(tr: np.ndarray) -> np.ndarray:
    tr = tr - tr.mean()
    peak = np.abs(tr).max()
    return tr / peak if peak > 0 else tr


def extract_fitness_feats(signal: np.ndarray, dt: float, name: str) -> dict:
    from src.feature_extraction import extract_features_from_signal
    df = extract_features_from_signal(signal, dt=dt, signal_name=name,
                                      center_freq_hz=400e6, coda_seek_peak=True)
    row = df.iloc[0]
    return {k: float(row[k]) for k in FITNESS_FEATURES if k in df.columns}


def build_target() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    ids, fi, sig = load_labeled_traces()
    anchor = np.flatnonzero(ids == PIT["ID"])[0]
    target = prep_trace(sig[anchor])

    t0 = time.time()
    tgt_feats = extract_fitness_feats(target, DT_REAL, "target_ID11")
    print(f"target features ({time.time()-t0:.1f}s): {sorted(tgt_feats)}")

    # spread = robust variability across pits of similar FI (same class regime)
    band = np.flatnonzero(np.abs(fi - PIT["FI"]) <= SPREAD_FI_BAND)
    print(f"spread cohort: {len(band)} pits with FI in "
          f"[{PIT['FI']-SPREAD_FI_BAND}, {PIT['FI']+SPREAD_FI_BAND}]")
    rows = [extract_fitness_feats(prep_trace(sig[i]), DT_REAL, f"pit{ids[i]}")
            for i in band]
    spread = pd.DataFrame(rows)
    mad = (spread - spread.median()).abs().median() * 1.4826
    mad = mad.clip(lower=spread.std() * 0.1 + 1e-12)

    np.savez(OUT_DIR / "target.npz", target=target, dt=DT_REAL,
             cohort_ids=ids[band], cohort_fi=fi[band])
    payload = {
        "pit": PIT,
        "features": tgt_feats,
        "spread_mad": {k: float(mad[k]) for k in tgt_feats},
        "cohort_median": {k: float(spread[k].median()) for k in tgt_feats},
        "cohort_n": int(len(band)),
    }
    (OUT_DIR / "target_features.json").write_text(json.dumps(payload, indent=2))
    print(f"saved target (pit ID {PIT['ID']}, cohort n={len(band)}) -> {OUT_DIR}")
    for k in tgt_feats:
        print(f"  {k:28s} anchor={tgt_feats[k]:+.4g}  cohort_med={spread[k].median():+.4g}  mad={mad[k]:.3g}")


# ------------------------------------------------------------------- sim side
TOML_TEMPLATE = """\
[sim]
title             = "calib POC pit ID11 {name}"
freq_hz           = 400e6
domain_x          = 2.4
antenna_clearance = 0.4
air_buffer        = 0.1
rx_spacing        = 0.0
seed              = 1234
time_window       = 35e-9

[source]
waveform     = "ricker"
amplitude    = 1.0
polarization = "z"

[[layer]]
name = "subgrade"
thickness = 0.50
eps = {sub_eps}
sigma = {sub_sigma}

[[layer]]
name = "fouled_ballast"
thickness = {fouled_th}
packed = true
eps = {foul_eps}
sigma = {foul_sigma}
matrix = "fouling"

[[layer]]
name = "ballast"
thickness = {clean_th}
packed = true
matrix = "free_space"
"""


def lhs_samples(n: int, seed: int) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    dims = len(PARAM_SPACE)
    # Latin hypercube: stratified uniform per dim, shuffled independently
    u = (rng.permuted(np.tile(np.arange(n), (dims, 1)), axis=1).T + rng.random((n, dims))) / n
    cols = {}
    for j, (k, (lo, hi, log)) in enumerate(PARAM_SPACE.items()):
        if log:
            cols[k] = 10 ** (np.log10(lo) + u[:, j] * (np.log10(hi) - np.log10(lo)))
        else:
            cols[k] = lo + u[:, j] * (hi - lo)
    df = pd.DataFrame(cols)
    df.insert(0, "cand", [f"c{i:03d}" for i in range(n)])
    return df


def generate() -> None:
    SIM_DIR.mkdir(parents=True, exist_ok=True)
    plan = lhs_samples(N_LHS, SEED)
    plan.to_csv(OUT_DIR / "lhs_plan.csv", index=False)
    gen = ROOT / "scripts" / "pipeline" / "generate_in_files.py"
    ok = 0
    for _, r in plan.iterrows():
        toml_path = SIM_DIR / f"{r.cand}.toml"
        toml_path.write_text(TOML_TEMPLATE.format(
            name=r.cand,
            sub_eps=round(r.sub_eps, 4), sub_sigma=round(r.sub_sigma, 6),
            foul_eps=round(r.foul_eps, 4), foul_sigma=round(r.foul_sigma, 6),
            fouled_th=PIT["fouled_ballast_m"], clean_th=PIT["clean_ballast_m"],
        ), encoding="utf-8")
        res = subprocess.run(
            [sys.executable, str(gen), str(SIM_DIR / f"{r.cand}.in"),
             "--layers-file", str(toml_path)],
            capture_output=True, text=True)
        if res.returncode == 0 and (SIM_DIR / f"{r.cand}.in").exists():
            ok += 1
        else:
            print(f"[FAIL] {r.cand}: {res.stdout[-300:]}{res.stderr[-300:]}")
    print(f"generated {ok}/{len(plan)} .in files in {SIM_DIR}")


def run_batch() -> None:
    todo = sorted(p for p in SIM_DIR.glob("c*.in")
                  if not p.with_suffix(".out").exists())
    print(f"{len(todo)} sims to run")
    t0 = time.time()
    for i, f in enumerate(todo):
        res = subprocess.run([GPRMAX_PY, "-m", "gprMax", str(f), "-n", "1"],
                             capture_output=True, text=True, cwd=str(SIM_DIR))
        status = "ok" if f.with_suffix(".out").exists() else "FAIL"
        el = time.time() - t0
        eta = el / (i + 1) * (len(todo) - i - 1)
        print(f"[{i+1}/{len(todo)}] {f.stem} {status}  ({el/60:.1f} min in, ETA {eta/60:.0f} min)",
              flush=True)
        if status == "FAIL":
            print(res.stderr[-500:])
    print("batch done")


# ------------------------------------------------- system response (idea 2)
# If the acquisition chain is LTI, injecting the effective wavelet equals
# post-hoc convolution of the sim trace with the system impulse response, so
# no re-simulation is needed: H(f) = FFT(real direct pulse)/FFT(sim direct
# pulse), water-level regularized, band-tapered.
PULSE_PRE_NS, PULSE_POST_NS = 2.0, 4.0
H_BAND = (50e6, 1.5e9)
WATER_LEVEL = 0.05


def _windowed_pulse(sig: np.ndarray, dt: float):
    from scipy.signal.windows import tukey
    p = prep_trace(sig)
    pk = int(np.argmax(np.abs(p)))
    w0 = pk - int(PULSE_PRE_NS * 1e-9 / dt)
    w1 = pk + int(PULSE_POST_NS * 1e-9 / dt)
    if w0 < 0 or w1 > len(p):
        return None
    seg = p[w0:w1] * np.sign(p[pk])
    return seg * tukey(len(seg), 0.3)


def build_system_response() -> None:
    """--sysresp: estimate H(f) on the real time base and save it."""
    ids, fi, sig = load_labeled_traces()
    pulses = [w for tr in sig if (w := _windowed_pulse(tr, DT_REAL)) is not None]
    real_dp = np.median(np.array(pulses), axis=0)

    ez, dt = load_out(SIM_DIR / "smoke.in".replace(".in", ".out"))
    sim_rs, dt_rs = resample_to_real(ez, dt)
    sim_dp = _windowed_pulse(sim_rs, dt_rs)
    n = max(len(real_dp), len(sim_dp))
    nfft = 1 << (n - 1).bit_length() + 2
    freqs = np.fft.rfftfreq(nfft, DT_REAL)
    R = np.fft.rfft(real_dp, nfft)
    S = np.fft.rfft(sim_dp, nfft)
    Smag = np.abs(S)
    S_reg = np.where(Smag < WATER_LEVEL * Smag.max(),
                     S / np.maximum(Smag, 1e-30) * (WATER_LEVEL * Smag.max()), S)
    H = R / S_reg
    # smooth cosine taper to zero outside the trusted band
    lo, hi = H_BAND
    taper = np.ones_like(freqs)
    rise = (freqs >= lo / 2) & (freqs < lo)
    fall = (freqs > hi) & (freqs <= hi * 1.5)
    taper[freqs < lo / 2] = 0.0
    taper[rise] = 0.5 - 0.5 * np.cos(np.pi * (freqs[rise] - lo / 2) / (lo / 2))
    taper[fall] = 0.5 + 0.5 * np.cos(np.pi * (freqs[fall] - hi) / (hi / 2))
    taper[freqs > hi * 1.5] = 0.0
    H *= taper
    np.savez(OUT_DIR / "system_response.npz", freqs=freqs, H=H,
             real_dp=real_dp, sim_dp=sim_dp, n_pulses=len(pulses))
    print(f"H(f) built from {len(pulses)} real pulses + smoke sim pulse; "
          f"|H| peak={np.abs(H).max():.2f} at {freqs[np.argmax(np.abs(H))]/1e6:.0f} MHz "
          f"-> {OUT_DIR/'system_response.npz'}")


def apply_system_response(sig: np.ndarray, dt: float) -> np.ndarray:
    d = np.load(OUT_DIR / "system_response.npz")
    n = len(sig)
    H = np.interp(np.fft.rfftfreq(n, dt), d["freqs"], d["H"].real) + \
        1j * np.interp(np.fft.rfftfreq(n, dt), d["freqs"], d["H"].imag)
    out = np.fft.irfft(np.fft.rfft(sig) * H, n)
    return out


# ------------------------------------------------------------------- analysis
def load_out(path: Path):
    import h5py
    with h5py.File(path, "r") as f:
        dt = float(f.attrs["dt"])
        key = list(f["rxs"].keys())[0]
        ez = np.array(f["rxs"][key]["Ez"])
    return ez.astype(float), dt


def resample_to_real(ez: np.ndarray, dt: float):
    """Anti-aliased resample of a sim trace onto the real DZT time base.

    The real system records at dt=50/511 ns; comparing features computed on
    different bandwidths is meaningless (sim FDTD carries multi-GHz content
    the receiver can never see)."""
    from fractions import Fraction
    from scipy.signal import resample_poly
    r = Fraction(dt / DT_REAL).limit_denominator(500)
    sig = resample_poly(ez, up=r.numerator, down=r.denominator)
    dt_new = dt * r.denominator / r.numerator
    return sig, dt_new


def analyze() -> None:
    tgt = json.loads((OUT_DIR / "target_features.json").read_text())
    feats = list(tgt["features"].keys())
    t_vec = np.array([tgt["features"][k] for k in feats])
    s_vec = np.array([tgt["spread_mad"][k] for k in feats])
    has_H = (OUT_DIR / "system_response.npz").exists()

    plan = pd.read_csv(OUT_DIR / "lhs_plan.csv")
    results = {}
    for mode in (["raw", "syscorr"] if has_H else ["raw"]):
        rows = []
        for _, r in plan.iterrows():
            out = SIM_DIR / f"{r.cand}.out"
            if not out.exists():
                continue
            ez, dt = load_out(out)
            sig, dt_rs = resample_to_real(ez, dt)
            if mode == "syscorr":
                sig = apply_system_response(sig, dt_rs)
            fdict = extract_fitness_feats(prep_trace(sig), dt_rs, r.cand)
            if set(feats) - set(fdict):
                continue
            z = (np.array([fdict[k] for k in feats]) - t_vec) / s_vec
            rec = dict(r)
            rec.update({f"f_{k}": fdict[k] for k in feats})
            rec.update({f"z_{k}": float(zz) for k, zz in zip(feats, z)})
            rec["fitness"] = float(np.sqrt(np.mean(z ** 2)))   # RMS z-distance
            rows.append(rec)
        df = pd.DataFrame(rows).sort_values("fitness")
        df.to_csv(OUT_DIR / f"lhs_results_{mode}.csv", index=False)
        results[mode] = df

    from sklearn.ensemble import RandomForestRegressor
    for mode, df in results.items():
        print(f"\n{'='*72}\nMODE: {mode}  ({len(df)} candidates)")
        cols = ["cand", "foul_eps", "foul_sigma", "sub_eps", "sub_sigma", "fitness"]
        print("Top 8 (fitness = RMS z; ~1 means within same-FI cohort spread):")
        print(df[cols].head(8).round(4).to_string(index=False))

        X = df[list(PARAM_SPACE)].copy()
        for k, (_, _, log) in PARAM_SPACE.items():
            if log:
                X[k] = np.log10(X[k])
        rf = RandomForestRegressor(400, random_state=SEED).fit(X, df["fitness"])
        imp = pd.Series(rf.feature_importances_, index=X.columns)
        print("Misfit-surrogate importance:", dict(imp.round(3)))

        # --- idea 4a: identifiability — can features recover each param? ---
        F = df[[f"f_{k}" for k in feats]].to_numpy()
        print("Identifiability (OOB R2, features -> param; <0.3 = NOT constrained):")
        for k in PARAM_SPACE:
            y = X[k].to_numpy()
            r2 = RandomForestRegressor(400, oob_score=True, random_state=SEED,
                                       bootstrap=True).fit(F, y).oob_score_
            print(f"  {k:12s} OOB R2 = {r2:+.2f}")

        # --- idea 4b: is the real target inside the sim feature manifold? ---
        print("Real target vs sim feature range (OUT = unreachable physics):")
        for j, k in enumerate(feats):
            lo, hi = F[:, j].min(), F[:, j].max()
            tag = "in" if lo <= t_vec[j] <= hi else "OUT"
            print(f"  {k:28s} target={t_vec[j]:+.4g}  sim=[{lo:+.4g}, {hi:+.4g}]  {tag}")

        best = df.iloc[0]
        print("Best candidate per-feature z (|z|<~2 = inside cohort noise):")
        for k in feats:
            print(f"  {k:28s} sim={best[f'f_{k}']:+.4g}  target={tgt['features'][k]:+.4g}  z={best[f'z_{k}']:+.2f}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--target", action="store_true")
    ap.add_argument("--generate", action="store_true")
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--sysresp", action="store_true")
    ap.add_argument("--analyze", action="store_true")
    a = ap.parse_args()
    if a.target:
        build_target()
    elif a.generate:
        generate()
    elif a.run:
        run_batch()
    elif a.sysresp:
        build_system_response()
    elif a.analyze:
        analyze()
    else:
        print("stages: --target | --generate | --run | --sysresp | --analyze")


if __name__ == "__main__":
    main()

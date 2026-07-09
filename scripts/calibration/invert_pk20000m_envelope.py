#!/usr/bin/env python3
"""
Envelope-matching layer inversion for EFE PK 20 000 m (flat 3-layer model).

Reuses the proven patterns from ``calibrate_layers.py`` (subprocess gprMax,
Hilbert-envelope coda objective, per-trial cleanup) but targets the validated
v3 geometry: ballast / subgrade / formation with thicknesses FIXED from the
B-scan picks, inverting only the three permittivities. The forward model is a
flat homogeneous-layer proxy (no rocks) — deterministic between trials and
physically justified for an HF specimen where stones barely scatter.

Objective: maximize Pearson r between synthetic and real Hilbert envelopes in
the coda window (src.signal_processing.coda_envelope_correlation).

Forward model: 2-D TMz, Ez-polarised Ricker 420 MHz, domain 1.0 x 1.2559 m,
dx=3 mm, 22 ns window (~5 s/run on CPU).

Usage:
    # 1-D validation sweep on ballast eps:
    python scripts/calibration/invert_pk20000m_envelope.py --mode sweep \\
        --param eps_b --values 3,4,5,6,7
    # full coarse grid:
    python scripts/calibration/invert_pk20000m_envelope.py --mode grid
"""
import argparse
import itertools
import sys
import time
from pathlib import Path

import h5py
import numpy as np

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))
from src.gprmax_runner import run_gprmax  # noqa: E402
from src.physics import ballast_crim  # noqa: E402
from src.signal_processing import (  # noqa: E402
    coda_energy_ratio, coda_envelope_correlation,
)

# ── Paths ─────────────────────────────────────────────────────────────────────
WORK_DIR  = REPO / "experiments" / "2026-06-29" / "inversion"
EXCIT_FILE = REPO / "calibration" / "gssi_excitation.txt"   # real GSSI source
# RAW (NOT AGC): AGC's per-trace nonlinear gain destroys the coda envelope we
# match against — raw coda is coherent trace-to-trace (r~0.99), AGC is not.
REAL_H5   = Path(r"D:/Codigo/Data/efe_full.h5")
PK_M      = 20000.0
STACK_HALF = 50          # ± traces stacked (first-break aligned) for the target

# ── Fixed geometry (from v3 picks) ─────────────────────────────────────────────
DOM_X, DOM_Y, DZ = 1.0, 1.2559, 0.003
DX = 0.003
TIME_WINDOW = 22e-9
FREQ = 4.2e8

Y_FORM_TOP = 0.3000      # formation 0.0 .. 0.3
Y_SUB_TOP  = 0.6245      # subgrade  0.3 .. 0.6245   (thickness 0.3245)
Y_BAL_TOP  = 1.0559      # ballast   0.6245 .. 1.0559 (thickness 0.4314)
STANDOFF   = 0.05
SRC_Y      = Y_BAL_TOP + STANDOFF        # 1.1059
SRC_X      = DOM_X / 2
RX_X       = SRC_X + 0.03                 # bistatic 30 mm
SRC_Z      = DZ / 2

# Fixed conductivities (invert eps only, first pass)
SIG_BAL, SIG_SUB, SIG_FORM = 0.005, 0.05, 0.05

# Coda objective window (ns AFTER first break). Must start >=4 ns so the
# direct-wave tail (Ricker ~4-5 ns wide) is excluded — otherwise r is
# direct-wave-dominated and insensitive to the buried reflections.
CODA_LO, CODA_HI = 4.0, 18.0
CODA_MID = 11.0          # early/late split for the energy-ratio observable

# Two-term objective: envelope-shape r pins eps_eff; the late/early coda
# energy ratio pins attenuation (sigma, hence pore water) which shape-r is
# blind to (scale-invariant). Penalty weight on |log ratio mismatch|: the
# f-Sw ridge extremes differ by ~0.32 in log-ratio, mid-ridge by ~0.05, so
# w=1 turns the dry impostor's score from ~0.96 to ~0.63 while a true match
# loses <0.01.
AMP_WEIGHT = 1.0

# 2D->3D energy-ratio calibration: late arrivals decay differently under
# cylindrical (2D) vs spherical (3D) spreading, so a 2D synthetic's
# late/early ratio is biased vs a 3D (or real) target. Multiplicative factor
# measured ONCE on a clean reference model run in both dimensions (never on
# the truth — that would re-commit the inversion crime). Set by --ratio-cal.
RATIO_CAL = 1.0

# Defaults / grid axes
DEFAULTS = {"eps_b": 4.0, "eps_s": 12.0, "eps_f": 18.0}
GRID = {
    "eps_b": [3.0, 4.0, 5.0],
    "eps_s": [9.0, 12.0, 15.0],
    "eps_f": [14.0, 18.0, 22.0],
}

# ── CRIM parameterization of the ballast layer ────────────────────────────────
# Instead of a free eps_b, the ballast is a physical mix — see
# src.physics.ballast_crim (constants in constants.MC.CRIM_*). The inversion
# unknowns become f_fill (fouling axis, ~PVC/FI) and sw (moisture axis), both
# bounded 0..1, with sigma COUPLED to the same unknowns so amplitude decay
# constrains sw instead of being a free nuisance. Rationale: at 420 MHz the
# coda measures volume fractions / eps_eff only
# (experiments/2026-07-01/rock_shape_ab).


def write_flat_in(p: dict, in_path: Path) -> None:
    """Write a flat 3-layer 2-D .in file (Ez Ricker 420 MHz).

    Optional ``p['d_ballast']`` / ``p['d_subgrade']`` set layer thicknesses; the
    air/ballast SURFACE (and antenna standoff) stays fixed at Y_BAL_TOP and the
    interfaces move downward — so varying d_ballast sweeps the d–ε degeneracy
    partner of eps_b. Defaults reproduce the original pick geometry.
    """
    def f(v): return f"{v:.5f}"
    d_bal = float(p.get('d_ballast', Y_BAL_TOP - Y_SUB_TOP))   # default 0.4314
    d_sub = float(p.get('d_subgrade', Y_SUB_TOP - Y_FORM_TOP)) # default 0.3245
    y_bal_top  = Y_BAL_TOP                                      # surface, fixed
    y_bal_base = y_bal_top - d_bal
    y_sub_base = max(DX * 4, y_bal_base - d_sub)                # keep formation present
    lines = [
        "## PK20000m flat-layer inversion trial",
        f"#domain: {DOM_X} {DOM_Y} {DZ}",
        f"#dx_dy_dz: {DX} {DX} {DZ}",
        f"#time_window: {TIME_WINDOW:g}",
        "",
        f"#material: {f(p['eps_f'])} {p.get('sig_f', SIG_FORM)} 1.0 0.0 formation",
        f"#material: {f(p['eps_s'])} {p.get('sig_s', SIG_SUB)} 1.0 0.0 subgrade",
        f"#material: {f(p['eps_b'])} {p.get('sig_b', SIG_BAL)} 1.0 0.0 ballast",
        "",
        # source: ideal Ricker, OR the calibrated GSSI excitation (real antenna
        # ring-down baked in) when p['excitation'] is truthy.
        # bare filename (gprMax splits the line on ':' so a Windows drive letter
        # "D:" truncates the path — the excitation file is copied into WORK_DIR)
        (f"#excitation_file: {EXCIT_FILE.name}"
         if p.get("excitation") else f"#waveform: ricker 1 {FREQ:g} the_wave"),
        f"#hertzian_dipole: z {f(SRC_X)} {f(SRC_Y)} {f(SRC_Z)} "
        + ("gssi_420mhz" if p.get("excitation") else "the_wave"),
        f"#rx: {f(RX_X)} {f(SRC_Y)} {f(SRC_Z)}",
        "",
        f"#box: 0 0 0 {DOM_X} {DOM_Y} {DZ} free_space",
        f"#box: 0 0 0 {DOM_X} {f(y_sub_base)} {DZ} formation",
        f"#box: 0 {f(y_sub_base)} 0 {DOM_X} {f(y_bal_base)} {DZ} subgrade",
        f"#box: 0 {f(y_bal_base)} 0 {DOM_X} {f(y_bal_top)} {DZ} ballast",
        "",
        "#messages: n",
    ]
    in_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_flat_in_3d(p: dict, in_path: Path, width: float = 0.6) -> None:
    """3D version of write_flat_in: same layers, same Hertzian dipole + GSSI
    excitation, same dx — ONLY the dimensionality changes (spherical instead
    of cylindrical spreading). Used to generate out-of-family targets that
    break the 2D inversion crime and to calibrate the 2D->3D energy-ratio
    offset. Width 0.6 m keeps it ~17M cells (GPU-friendly)."""
    def f(v): return f"{v:.5f}"
    d_bal = float(p.get('d_ballast', Y_BAL_TOP - Y_SUB_TOP))
    d_sub = float(p.get('d_subgrade', Y_SUB_TOP - Y_FORM_TOP))
    y_bal_top  = Y_BAL_TOP
    y_bal_base = y_bal_top - d_bal
    y_sub_base = max(DX * 4, y_bal_base - d_sub)
    cx = cz = width / 2
    lines = [
        "## PK20000m flat-layer 3D target (spreading-honest twin of the 2D model)",
        f"#domain: {width} {DOM_Y} {width}",
        f"#dx_dy_dz: {DX} {DX} {DX}",
        f"#time_window: {TIME_WINDOW:g}",
        "",
        f"#material: {f(p['eps_f'])} {p.get('sig_f', SIG_FORM)} 1.0 0.0 formation",
        f"#material: {f(p['eps_s'])} {p.get('sig_s', SIG_SUB)} 1.0 0.0 subgrade",
        f"#material: {f(p['eps_b'])} {p.get('sig_b', SIG_BAL)} 1.0 0.0 ballast",
        "",
        (f"#excitation_file: {EXCIT_FILE.name}"
         if p.get("excitation") else f"#waveform: ricker 1 {FREQ:g} the_wave"),
        f"#hertzian_dipole: z {f(cx)} {f(SRC_Y)} {f(cz)} "
        + ("gssi_420mhz" if p.get("excitation") else "the_wave"),
        f"#rx: {f(cx + 0.03)} {f(SRC_Y)} {f(cz)}",
        "",
        f"#box: 0 0 0 {width} {DOM_Y} {width} free_space",
        f"#box: 0 0 0 {width} {f(y_sub_base)} {width} formation",
        f"#box: 0 {f(y_sub_base)} 0 {width} {f(y_bal_base)} {width} subgrade",
        f"#box: 0 {f(y_bal_base)} 0 {width} {f(y_bal_top)} {width} ballast",
        "",
        "#messages: n",
    ]
    in_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def read_ez(out_path: Path):
    with h5py.File(out_path, "r") as f:
        dt = float(f.attrs["dt"])
        ez = f["rxs/rx1/Ez"][:]
    return ez.astype(float), dt


def load_real():
    """First-break-aligned stack of ±STACK_HALF raw traces around PK_M.

    Block-regularization (cf. group's per-PK averaging) suppresses incoherent
    clutter while preserving the coherent layer reflections (raw coda is ~0.99
    coherent trace-to-trace).
    """
    from src.signal_processing import _first_break_sample
    with h5py.File(REAL_H5, "r") as f:
        dt = float(f.attrs["dt_ns"]) * 1e-9
        pk = f["pk_m"][:]
        idx = int(np.argmin(np.abs(pk - PK_M)))
        lo, hi = max(0, idx - STACK_HALF), idx + STACK_HALF
        block = f["traces"][lo:hi, :].astype(float)
    dt_ns = dt * 1e9
    ref = _first_break_sample(block[len(block) // 2], dt_ns)
    aligned = np.array([np.roll(b, ref - _first_break_sample(b, dt_ns)) for b in block])
    return aligned.mean(axis=0), dt


def evaluate(params: dict, real_sig, real_dt, tag: str,
             objective: str = "shape") -> tuple:
    """Run one forward model; return (score, r_shape, ratio).

    objective="shape":     score = coda envelope Pearson r (legacy).
    objective="shape+amp": score = r - AMP_WEIGHT * |log(ratio_syn/ratio_tgt)|
                           — adds the scale-free attenuation observable that
                           shape-r discards, separating iso-eps_eff (f, S_w)
                           impostors with different sigma.
    Returns (-1.0, -1.0, 0.0) on failure.
    """
    in_path = WORK_DIR / f"{tag}.in"
    try:
        write_flat_in(params, in_path)
        if not run_gprmax(in_path):
            return -1.0, -1.0, 0.0
        syn, syn_dt = read_ez(in_path.with_suffix(".out"))
        r = coda_envelope_correlation(syn, syn_dt, real_sig, real_dt,
                                      CODA_LO, CODA_HI)
        ratio = coda_energy_ratio(syn, syn_dt, CODA_LO, CODA_MID, CODA_HI)
        if objective == "shape+amp":
            ratio_tgt = coda_energy_ratio(real_sig, real_dt,
                                          CODA_LO, CODA_MID, CODA_HI)
            if ratio > 0 and ratio_tgt > 0:
                score = r - AMP_WEIGHT * abs(np.log(ratio * RATIO_CAL / ratio_tgt))
            else:
                score = -1.0
        else:
            score = r
        return score, r, ratio
    except Exception as exc:
        print(f"  [{tag}] ERROR: {exc}")
        return -1.0, -1.0, 0.0
    finally:
        for suf in (".in", ".out", ".vti"):
            p = in_path.with_suffix(suf)
            if p.exists():
                p.unlink()


def crim_params(f_fill: float, sw: float) -> dict:
    """Full forward-model parameter dict for a CRIM ballast trial."""
    eps_b, sig_b = ballast_crim(f_fill, sw)
    p = dict(DEFAULTS)
    p.update(eps_b=eps_b, sig_b=sig_b, excitation=True,
             f_fill=f_fill, sw=sw)
    return p


def make_synthetic_target(f_fill: float, sw: float, workdir: Path):
    """Forward-model a known (f_fill, sw) as the inversion target (inversion
    crime: same forward operator — measures best-case identifiability only)."""
    in_path = workdir / "synthetic_target.in"
    write_flat_in(crim_params(f_fill, sw), in_path)
    if not run_gprmax(in_path):
        raise RuntimeError("synthetic target forward model failed")
    sig, dt = read_ez(in_path.with_suffix(".out"))
    for suf in (".in", ".out", ".vti"):
        pth = in_path.with_suffix(suf)
        if pth.exists():
            pth.unlink()
    return sig, dt


def make_target_3d(f_fill: float, sw: float, workdir: Path):
    """3D flat-layer target for a known (f_fill, sw): out-of-family for the 2D
    engine (different spreading), breaking the strict inversion crime. The
    expensive .out is CACHED in workdir and reused across grid runs."""
    out_path = workdir / f"crim3d_target_f{f_fill:g}_sw{sw:g}.out"
    if not out_path.exists():
        in_path = out_path.with_suffix(".in")
        write_flat_in_3d(crim_params(f_fill, sw), in_path)
        print("  running 3D target (GPU, ~1-2 min) ...")
        if not run_gprmax(in_path, gpu=True):
            raise RuntimeError("3D target forward model failed")
    return read_ez(out_path)


def calibrate_ratio(workdir: Path) -> float:
    """2D->3D energy-ratio calibration on the CLEAN reference model (f=0, sw=0
    — far from any test truth). Returns ratio_3D_ref / ratio_2D_ref; the 2D
    synthetic ratios are multiplied by this to be comparable to 3D targets.
    The 3D reference .out is cached."""
    ref = crim_params(0.0, 0.0)
    # 2D reference
    in2d = workdir / "ratio_cal_2d.in"
    write_flat_in(ref, in2d)
    if not run_gprmax(in2d):
        raise RuntimeError("2D calibration reference failed")
    sig2, dt2 = read_ez(in2d.with_suffix(".out"))
    for suf in (".in", ".out", ".vti"):
        p = in2d.with_suffix(suf)
        if p.exists():
            p.unlink()
    # 3D reference (cached)
    out3d = workdir / "ratio_cal_3d.out"
    if not out3d.exists():
        in3d = out3d.with_suffix(".in")
        write_flat_in_3d(ref, in3d)
        print("  running 3D calibration reference (GPU, ~1-2 min) ...")
        if not run_gprmax(in3d, gpu=True):
            raise RuntimeError("3D calibration reference failed")
    sig3, dt3 = read_ez(out3d)
    r2 = coda_energy_ratio(sig2, dt2, CODA_LO, CODA_MID, CODA_HI)
    r3 = coda_energy_ratio(sig3, dt3, CODA_LO, CODA_MID, CODA_HI)
    print(f"  ratio calibration (clean ref): 2D={r2:.4f}  3D={r3:.4f}  "
          f"factor={r3/r2:.4f}")
    return r3 / r2


def add_noise(sig: np.ndarray, dt: float, snr_db: float, seed: int = 0):
    """Additive white Gaussian noise at snr_db relative to the coda RMS
    (4-18 ns after first break — the part of the trace the objective uses)."""
    from src.signal_processing import _first_break_sample
    dt_ns = dt * 1e9
    fb = _first_break_sample(sig, dt_ns)
    t = (np.arange(len(sig)) - fb) * dt_ns
    coda_rms = float(np.sqrt(np.mean(sig[(t >= CODA_LO) & (t <= CODA_HI)] ** 2)))
    sigma = coda_rms / (10 ** (snr_db / 20.0))
    rng = np.random.default_rng(seed)
    return sig + rng.normal(0.0, sigma, len(sig))


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--mode", choices=["sweep", "grid", "crim"], default="sweep")
    ap.add_argument("--param", default="eps_b", help="swept parameter (sweep mode)")
    ap.add_argument("--values", default="3,4,5,6,7", help="comma list (sweep mode)")
    ap.add_argument("--f-grid", default="0,0.2,0.4,0.6,0.8,1.0",
                    help="crim mode: fines fill fractions (fraction of void volume)")
    ap.add_argument("--sw-grid", default="0,0.25,0.5,0.75,1.0",
                    help="crim mode: fines-pack water saturations")
    ap.add_argument("--synthetic-target", default=None, metavar="F,SW",
                    help="invert a SYNTHETIC trace with known f_fill,sw instead of "
                         "the real PK trace (recovery / identifiability test)")
    ap.add_argument("--objective", choices=["shape", "shape+amp"], default="shape",
                    help="shape = envelope Pearson r only (legacy); shape+amp adds "
                         "the late/early coda energy-ratio attenuation term")
    ap.add_argument("--target-3d", default=None, metavar="F,SW",
                    help="like --synthetic-target but the target is generated by "
                         "the 3D flat-layer twin (breaks the 2D inversion crime; "
                         "cached .out reused)")
    ap.add_argument("--ratio-cal", action="store_true",
                    help="calibrate the 2D->3D energy-ratio offset on the clean "
                         "reference model before inverting (use with --target-3d)")
    ap.add_argument("--target-noise-db", type=float, default=None,
                    help="add white Gaussian noise to the target at this SNR (dB, "
                         "relative to coda RMS)")
    ap.add_argument("--noise-seed", type=int, default=0)
    ap.add_argument("--workdir", type=Path, default=None,
                    help="working/results directory (default: WORK_DIR)")
    args = ap.parse_args()

    global WORK_DIR
    if args.workdir is not None:
        WORK_DIR = args.workdir
    WORK_DIR.mkdir(parents=True, exist_ok=True)
    # gprMax needs the excitation file next to the deck (drive-letter caveat)
    excit_local = WORK_DIR / EXCIT_FILE.name
    if not excit_local.exists():
        excit_local.write_bytes(EXCIT_FILE.read_bytes())

    global RATIO_CAL
    if args.ratio_cal:
        RATIO_CAL = calibrate_ratio(WORK_DIR)

    if args.target_3d:
        f_t, sw_t = (float(v) for v in args.target_3d.split(","))
        eps_t, sig_t = ballast_crim(f_t, sw_t)
        print(f"3D target: f_fill={f_t:g} sw={sw_t:g} "
              f"(eps_b={eps_t:.3f} sig_b={sig_t:.4f}) …")
        real_sig, real_dt = make_target_3d(f_t, sw_t, WORK_DIR)
    elif args.synthetic_target:
        f_t, sw_t = (float(v) for v in args.synthetic_target.split(","))
        eps_t, sig_t = ballast_crim(f_t, sw_t)
        print(f"Synthetic target: f_fill={f_t:g} sw={sw_t:g} "
              f"(eps_b={eps_t:.3f} sig_b={sig_t:.4f}) …")
        real_sig, real_dt = make_synthetic_target(f_t, sw_t, WORK_DIR)
    else:
        print(f"Loading real trace at PK {PK_M:.0f} m …")
        real_sig, real_dt = load_real()

    if args.target_noise_db is not None:
        real_sig = add_noise(real_sig, real_dt, args.target_noise_db,
                             seed=args.noise_seed)
        print(f"Added target noise: SNR={args.target_noise_db:g} dB "
              f"(seed {args.noise_seed})")

    results = []
    t0 = time.time()

    if args.mode == "crim":
        f_vals  = [float(v) for v in args.f_grid.split(",")]
        sw_vals = [float(v) for v in args.sw_grid.split(",")]
        print(f"CRIM grid: f_fill in {f_vals} x sw in {sw_vals} "
              f"({len(f_vals)*len(sw_vals)} runs; objective={args.objective}; "
              f"eps_s/eps_f fixed at {DEFAULTS['eps_s']}/{DEFAULTS['eps_f']})\n")
        for i, (fv, swv) in enumerate(itertools.product(f_vals, sw_vals)):
            p = crim_params(fv, swv)
            score, r, ratio = evaluate(p, real_sig, real_dt, f"crim_{i:03d}",
                                       objective=args.objective)
            p.update(r_shape=r, ratio=ratio)
            results.append((p, score))
            print(f"  [{i+1:3d}] f={fv:4.2f} sw={swv:4.2f}  "
                  f"(eps_b={p['eps_b']:5.2f} sig_b={p['sig_b']:.4f})   "
                  f"score={score:+.4f}  (r={r:+.4f} ratio={ratio:.4f})")
    elif args.mode == "sweep":
        vals = [float(v) for v in args.values.split(",")]
        print(f"1-D sweep: {args.param} in {vals}  (others fixed: "
              + ", ".join(f"{k}={v}" for k, v in DEFAULTS.items() if k != args.param) + ")\n")
        for v in vals:
            p = dict(DEFAULTS); p[args.param] = v
            score, r, ratio = evaluate(p, real_sig, real_dt,
                                       f"sweep_{args.param}_{v:g}",
                                       objective=args.objective)
            p.update(r_shape=r, ratio=ratio)
            results.append((p, score))
            print(f"  {args.param}={v:5.2f}   score={score:+.4f}")
    else:
        combos = list(itertools.product(*GRID.values()))
        keys = list(GRID.keys())
        print(f"Coarse grid: {len(combos)} combos over {keys}\n")
        for i, combo in enumerate(combos):
            p = dict(zip(keys, combo))
            score, r, ratio = evaluate(p, real_sig, real_dt, f"grid_{i:03d}",
                                       objective=args.objective)
            p.update(r_shape=r, ratio=ratio)
            results.append((p, score))
            print(f"  [{i+1:3d}/{len(combos)}] "
                  + " ".join(f"{k}={p[k]:5.2f}" for k in keys) + f"   score={score:+.4f}")

    dt_tot = time.time() - t0
    best_p, best_r = max(results, key=lambda x: x[1])
    print(f"\n{'='*56}")
    extra = (f"  f_fill={best_p['f_fill']:.2f} sw={best_p['sw']:.2f} "
             f"sig_b={best_p['sig_b']:.4f}" if "f_fill" in best_p else "")
    print(f"Best: r={best_r:+.4f}   "
          + " ".join(f"{k}={best_p[k]:.2f}" for k in DEFAULTS) + extra)
    print(f"Ran {len(results)} forward models in {dt_tot:.0f} s "
          f"({dt_tot/max(1,len(results)):.1f} s/run)")

    # save results CSV
    suffix = "_amp" if args.objective == "shape+amp" else ""
    if args.target_3d:
        suffix += "_3d"
    if args.target_noise_db is not None:
        suffix += f"_n{args.target_noise_db:g}db"
    csv = WORK_DIR / f"results_{args.mode}{suffix}.csv"
    with open(csv, "w", encoding="utf-8") as fh:
        fh.write("f_fill,sw,sig_b,eps_b,eps_s,eps_f,score,r_shape,ratio\n")
        for p, s in results:
            fh.write(f"{p.get('f_fill', '')},{p.get('sw', '')},{p.get('sig_b', '')},"
                     f"{p['eps_b']},{p['eps_s']},{p['eps_f']},{s:.5f},"
                     f"{p.get('r_shape', '')},{p.get('ratio', '')}\n")
    print(f"Results -> {csv}")


if __name__ == "__main__":
    main()

"""
generate_test_fixtures.py — Synthetic test batch for the Synth-GPR pipeline.

Generates a small, fast, physics-plausible batch of fake A-scans in BOTH domains
so the pipeline code (assembler T5, comparison T6, harness, verifier T9) can be
developed and tested without running gprMax or touching real DZT data.

Ground truth is KNOWN and embedded, so tests can assert recovery:
  - air gap 0.50 m  -> surface reflection at ~3.3 ns after direct wave
  - ballast eps(frac_finos) via simplified CRIM -> base reflection timing
  - attenuation alpha increases with fouling -> envelope decay
  - spectral downshift with fouling -> centroid drop (the classification signal)
  - granular speckle coda -> raw-waveform correlation ~0 between seeds (by design)

Deliberate TRAPS included (the pipeline must handle these):
  - sim dt = 0.0311 ns (oversampled, like gprMax) vs real dt = 0.098 ns
  - real traces have hardware GAIN baked in (linear-in-time curve, like GSSI)
    -> stored in sidecar gain_curve.json; T7-style de-gaining must recover physics
  - real traces have measurement noise; sim traces are clean
  - real polarity is FLIPPED vs sim (Ez vs voltage convention)

Layout produced (under --out, default ./fixtures):
  sim/scene_{seed:04d}.out    gprMax-style HDF5: /rxs/rx1/Ez, attrs dt, iterations
  sim/scene_{seed:04d}.in     text file with ## CONFIG_* headers (assembler contract)
  real/trace_{i:04d}.npy      float array, gain baked in, dt=0.098ns
  real/real_labels.csv        trace_id, group (track segment), label, frac_finos_true
  real/gain_curve.json        the gain curve applied (for de-gain tests)
  ground_truth.json           every parameter used, per file (for asserts)
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import h5py
import numpy as np

C = 0.299792458  # m/ns

# ---------------- physics helpers (simplified but directionally correct) -------------

CLASSES = [  # (name, frac_finos range)
    ("CL", 0.00, 0.10), ("MC", 0.10, 0.25), ("MF", 0.25, 0.45),
    ("F", 0.45, 0.70), ("HF", 0.70, 1.00),
]


def label_from_frac(frac: float) -> str:
    for name, lo, hi in CLASSES:
        if lo <= frac < hi:
            return name
    return "HF"


def crim_eps(frac_finos: float, porosity: float = 0.40, moisture: float = 0.15) -> float:
    """Simplified CRIM: stone skeleton + voids filled bottom-up by fines/water/air."""
    v_stone = 1 - porosity
    v_filled = porosity * frac_finos          # fraction of voids occupied
    v_water = v_filled * moisture
    v_fines = v_filled - v_water
    v_air = porosity - v_filled
    sqrt_eps = (v_stone * np.sqrt(6.0) + v_fines * np.sqrt(6.5)
                + v_water * np.sqrt(81.0) + v_air * 1.0)
    return float(sqrt_eps ** 2)


def alpha_from_frac(frac: float) -> float:
    """Envelope decay rate (1/ns): grows with fouling (conduction + scattering)."""
    return 0.08 + 0.35 * frac


def centroid_hz_from_frac(frac: float) -> float:
    """Coda spectral centroid: downshifts with fouling (dispersive loss signature)."""
    return 400e6 - 170e6 * frac


def ricker(fc_hz: float, dt_ns: float, n: int = 161) -> np.ndarray:
    t = (np.arange(n) - n // 2) * dt_ns * 1e-9
    a = (np.pi * fc_hz) ** 2
    return (1 - 2 * a * t**2) * np.exp(-a * t**2)


def synth_ascan(frac_finos: float, seed: int, dt_ns: float, n_samples: int,
                h_air: float = 0.50, ballast_thick: float = 0.35,
                jitter_h: float = 0.0) -> dict:
    """One A-scan with direct wave, surface & base reflections, speckle coda."""
    rng = np.random.default_rng(seed)
    h = h_air + (rng.uniform(-jitter_h, jitter_h) if jitter_h else 0.0)
    eps = crim_eps(frac_finos)
    v_ballast = C / np.sqrt(eps)                     # m/ns
    t_direct = 1.0                                   # ns (arbitrary system delay)
    t_surface = t_direct + 2 * h / C                 # ~ +3.3 ns
    t_base = t_surface + 2 * ballast_thick / v_ballast

    t = np.arange(n_samples) * dt_ns
    tr = np.zeros(n_samples)
    fc = centroid_hz_from_frac(frac_finos)
    w_dir, w_sub = ricker(400e6, dt_ns), ricker(fc, dt_ns)

    def add(sig, t0, amp, wav):
        i0 = int(round(t0 / dt_ns))
        n = len(wav)
        a, b = max(0, i0 - n // 2), min(n_samples, i0 + n // 2 + 1)
        wa, wb = a - (i0 - n // 2), n - ((i0 + n // 2 + 1) - b)
        sig[a:b] += amp * wav[wa:wb]

    add(tr, t_direct, 1.00, w_dir)                   # direct wave (strongest)
    r_surf = (1 - np.sqrt(eps)) / (1 + np.sqrt(eps))
    add(tr, t_surface, 0.9 * abs(r_surf), w_dir)     # surface reflection
    add(tr, t_base, 0.25, w_sub)                     # ballast-base reflection

    # granular speckle coda: random scatterers filling the whole record
    # (multiple scattering fills the coda; truncating them would fake a decay
    #  unrelated to alpha — the fit must be governed by attenuation only)
    n_sc = 300
    t_sc = rng.uniform(t_surface + 0.5, t[-1] - 1.0, n_sc)
    a_sc = rng.normal(0, 0.045, n_sc)
    for ts, asc in zip(t_sc, a_sc):
        add(tr, ts, asc, w_sub)

    # bulk attenuation applied to everything after the surface
    alpha = alpha_from_frac(frac_finos)
    mask = t > t_surface
    tr[mask] *= np.exp(-alpha * (t[mask] - t_surface))

    return {"trace": tr, "eps": eps, "alpha": alpha, "t_surface": t_surface,
            "t_base": t_base, "h_air": h, "centroid_hz": fc}


# ---------------- writers ------------------------------------------------------------

IN_TEMPLATE = """#title: synthetic test fixture (NOT gprMax output)
#domain: 0.60 0.002 1.55
#dx_dy_dz: 0.002 0.002 0.002
#time_window: {tw:.1e}

## CONFIG_frac_finos: {frac:.4f}
## CONFIG_porosidad: 0.40
## CONFIG_humedad: 0.15
## CONFIG_fidelidad: barato_2D
## CONFIG_group_seed: {seed}
## CONFIG_h_aire: {h:.4f}
## CONFIG_label: {label}
## RESAMPLE_TO_DT: 9.8e-11
"""


def write_sim(outdir: Path, seed: int, frac: float, gt: dict) -> None:
    dt_ns, n = 0.0311, 1608                          # gprMax-like oversampling, ~50 ns
    r = synth_ascan(frac, seed, dt_ns, n)
    with h5py.File(outdir / f"scene_{seed:04d}.out", "w") as f:
        f.attrs["dt"] = dt_ns * 1e-9
        f.attrs["Iterations"] = n
        f.create_dataset("rxs/rx1/Ez", data=r["trace"])
    (outdir / f"scene_{seed:04d}.in").write_text(
        IN_TEMPLATE.format(tw=n * dt_ns * 1e-9, frac=frac, seed=seed,
                           h=r["h_air"], label=label_from_frac(frac)))
    gt[f"sim/scene_{seed:04d}"] = {k: v for k, v in r.items() if k != "trace"} | {
        "frac_finos": frac, "label": label_from_frac(frac), "dt_ns": dt_ns}


def write_real(outdir: Path, idx: int, seed: int, frac: float, group: str,
               gain_db_end: float, gt: dict, rows: list) -> None:
    dt_ns, n = 0.098, 512                            # real GSSI-like time base
    r = synth_ascan(frac, seed, dt_ns, n, jitter_h=0.04)
    tr = -r["trace"]                                 # TRAP: polarity flipped vs sim
    tr += np.random.default_rng(seed + 9999).normal(0, 0.004, n)   # noise
    gain_lin = 10 ** (np.linspace(0, gain_db_end, n) / 20)          # TRAP: baked gain
    np.save(outdir / f"trace_{idx:04d}.npy", tr * gain_lin)
    rows.append({"trace_id": f"trace_{idx:04d}", "group": group,
                 "label": label_from_frac(frac), "frac_finos_true": round(frac, 4)})
    gt[f"real/trace_{idx:04d}"] = {k: v for k, v in r.items() if k != "trace"} | {
        "frac_finos": frac, "label": label_from_frac(frac), "dt_ns": dt_ns,
        "group": group, "gain_db_end": gain_db_end, "polarity": -1}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="fixtures")
    ap.add_argument("--n-sim", type=int, default=20)
    ap.add_argument("--n-real", type=int, default=15)
    ap.add_argument("--gain-db", type=float, default=12.0,
                    help="end value of the baked linear gain ramp (dB); 0 = flat")
    args = ap.parse_args()

    root = Path(args.out)
    (root / "sim").mkdir(parents=True, exist_ok=True)
    (root / "real").mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(42)
    gt: dict = {}

    # sim: spread frac_finos across all classes; seed = group_id
    for seed in range(1, args.n_sim + 1):
        write_sim(root / "sim", seed, float(rng.uniform(0.0, 0.95)), gt)

    # real: 5 track segments (groups), each with a dominant condition
    rows: list = []
    segments = [("PK12+300", 0.05), ("PK12+800", 0.20), ("PK13+400", 0.40),
                ("PK14+100", 0.60), ("PK14+900", 0.85)]
    for i in range(args.n_real):
        seg, base = segments[i % len(segments)]
        frac = float(np.clip(base + rng.normal(0, 0.05), 0, 0.99))
        write_real(root / "real", i, 5000 + i, frac, seg, args.gain_db, gt, rows)

    import csv
    with open(root / "real" / "real_labels.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys())
        w.writeheader(); w.writerows(rows)
    (root / "real" / "gain_curve.json").write_text(json.dumps(
        {"type": "linear_db_ramp", "db_start": 0.0, "db_end": args.gain_db,
         "n_samples": 512, "note": "applied multiplicatively; de-gain must divide"}))
    (root / "ground_truth.json").write_text(json.dumps(gt, indent=1))
    print(f"OK: {args.n_sim} sim + {args.n_real} real -> {root}/ "
          f"(gain {args.gain_db} dB baked into real)")


if __name__ == "__main__":
    main()

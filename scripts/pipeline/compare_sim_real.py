"""Canonical sim<->real A-scan comparison — the single entry point.

Reads one synthetic gprMax .out and one real GSSI .dzt, computes the four
canonical metrics from src.sim_real_comparison, and writes a JSON report.
Replaces the ~44 ad-hoc compare_*/align_*/iterate_* root scripts, each of which
re-parsed DZT and re-windowed differently.

Rules (inherited from the module): explicit dt everywhere, envelope/spectrum
never raw-waveform on the coda, DZT only via src.dzt_io, amplitude-preserving
preprocess_physical.

Usage:
    python scripts/pipeline/compare_sim_real.py \
        --sim path/to/sim.out --real path/to/real.dzt --out report.json \
        [--real-trace N] [--band 150e6 800e6] [--alpha-window 4 18]
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import numpy as np  # noqa: E402

from src.data_loader import read_ascan  # noqa: E402
from src.dzt_io import read_dzt_traces  # noqa: E402
from src.sim_real_comparison import (  # noqa: E402
    direct_wave_correlation,
    envelope_alpha,
    spectral_evolution,
    spectral_distance,
)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--sim", required=True, help="Synthetic gprMax .out file.")
    ap.add_argument("--real", required=True, help="Real GSSI .dzt file.")
    ap.add_argument("--out", required=True, help="Output JSON report path.")
    ap.add_argument("--real-trace", type=int, default=None,
                    help="DZT trace index to compare (default: middle trace).")
    ap.add_argument("--band", type=float, nargs=2, default=None,
                    metavar=("F_LO_HZ", "F_HI_HZ"),
                    help="Antenna band applied to BOTH traces, e.g. 150e6 800e6.")
    ap.add_argument("--alpha-window", type=float, nargs=2, default=(4.0, 18.0),
                    metavar=("T_START_NS", "T_END_NS"),
                    help="Envelope-alpha fit window, ns after first break.")
    args = ap.parse_args()

    band = tuple(args.band) if args.band else None

    sim_d = read_ascan(args.sim)
    sim = np.asarray(sim_d["signal"], dtype=float)
    sim_dt = float(sim_d["dt"])

    traces, meta = read_dzt_traces(Path(args.real))
    if traces.shape[0] == 0:
        raise SystemExit(f"No traces read from {args.real}")
    idx = args.real_trace if args.real_trace is not None else traces.shape[0] // 2
    real = np.asarray(traces[idx], dtype=float)
    real_dt = float(meta["sample_interval_ns"]) * 1e-9

    a0, a1 = args.alpha_window
    report = {
        "sim_file": str(args.sim),
        "real_file": str(args.real),
        "real_trace_idx": int(idx),
        "sim_dt_ns": sim_dt * 1e9,
        "real_dt_ns": real_dt * 1e9,
        "band_hz": list(band) if band else None,
        "direct_wave_envelope_r": direct_wave_correlation(
            sim, sim_dt, real, real_dt, band=band),
        "envelope_alpha_sim_per_ns": envelope_alpha(
            sim, sim_dt, a0, a1, band=band),
        "envelope_alpha_real_per_ns": envelope_alpha(
            real, real_dt, a0, a1, band=band),
        "spectral_distance_hz": spectral_distance(
            sim, sim_dt, real, real_dt, band=band),
    }
    for name, sig, dt in [("sim", sim, sim_dt), ("real", real, real_dt)]:
        ev = spectral_evolution(sig, dt, band=band)
        report[f"spectral_evolution_{name}"] = {k: v.tolist() for k, v in ev.items()}

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(report, f, indent=2)

    # Console: the four scalar metrics (drop the bulky evolution arrays).
    summary = {k: v for k, v in report.items()
               if not k.startswith("spectral_evolution")}
    print(json.dumps(summary, indent=2))
    print(f"\nFull report -> {out_path}")


if __name__ == "__main__":
    main()

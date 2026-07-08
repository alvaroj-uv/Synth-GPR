"""Regenerate the golden feature fixtures for tests/test_golden_features.py.

Run deliberately, and ONLY with a justified reason:

    python tests/regenerate_golden.py --yes

Regenerating overwrites the frozen reference that the golden regression test
locks against. If you regenerate, the COMMIT MUST EXPLAIN WHY the 572-feature
outputs changed (e.g. an intentional feature-extraction change) — otherwise an
accidental feature-chain regression could silently rewrite its own baseline.

Writes:
  tests/fixtures/golden_traces.npz     frozen input traces (sim, real) + dt
  tests/fixtures/golden_features.json  extracted features for each trace
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from src.feature_extraction import extract_features_from_signal  # noqa: E402

FIXTURES = Path(__file__).parent / "fixtures"
DT_SIM = 0.0311e-9      # synthetic .out time base (dt from HDF5 attr)
DT_REAL = 0.1e-9        # real DZT/CSV time base
CENTER_FREQ_HZ = 400e6  # fixed so extraction is fully deterministic


def _synthetic_ascan(n, dt, seed, noise, reflections):
    """Deterministic Ricker direct pulse + delayed reflections + small noise."""
    rng = np.random.default_rng(seed)
    t = np.arange(n) * dt
    sig = np.zeros(n)
    f0 = 400e6
    for t0, amp in reflections:
        tau = t - t0
        arg = (np.pi * f0 * tau) ** 2
        sig += amp * (1.0 - 2.0 * arg) * np.exp(-arg)
    sig += noise * rng.standard_normal(n)
    return sig


def build_traces():
    # Synthetic .out-scale trace (clean-ish, sim time base).
    sim = _synthetic_ascan(
        644, DT_SIM, seed=20260704, noise=0.008,
        reflections=((3e-9, 1.0), (9e-9, -0.5), (14e-9, 0.25)),
    )
    # SUBSTITUTE for a real DZT trace: noisier, real time base (dt=0.1 ns,
    # n=511), more reflections. No real field trace is committable, so this is a
    # documented synthetic stand-in that still exercises the full 572-feature
    # chain on the real time base.
    real = _synthetic_ascan(
        511, DT_REAL, seed=19730401, noise=0.05,
        reflections=((3e-9, 1.0), (11e-9, -0.6), (20e-9, 0.3), (33e-9, -0.15)),
    )
    return {"sim": (sim, DT_SIM), "real": (real, DT_REAL)}


def features_of(sig, dt):
    df = extract_features_from_signal(sig, dt=dt, center_freq_hz=CENTER_FREQ_HZ)
    row = df.iloc[0].to_dict()
    out = {}
    for k, v in row.items():
        if k == "Signal":
            continue
        try:
            out[k] = float(v)     # skip string meta cols (meta_feature_version)
        except (TypeError, ValueError):
            continue
    return out


def main():
    ap = argparse.ArgumentParser(description="Regenerate golden feature fixtures.")
    ap.add_argument("--yes", action="store_true",
                    help="Confirm regeneration (required; justify in the commit).")
    args = ap.parse_args()
    if not args.yes:
        print(__doc__)
        raise SystemExit("Refusing to regenerate without --yes.")

    FIXTURES.mkdir(exist_ok=True)
    traces = build_traces()
    np.savez(
        FIXTURES / "golden_traces.npz",
        sim=traces["sim"][0], sim_dt=traces["sim"][1],
        real=traces["real"][0], real_dt=traces["real"][1],
    )
    golden = {name: features_of(sig, dt) for name, (sig, dt) in traces.items()}
    with open(FIXTURES / "golden_features.json", "w") as f:
        json.dump(golden, f, indent=1, sort_keys=True)

    counts = {k: len(v) for k, v in golden.items()}
    print(f"Wrote {FIXTURES / 'golden_traces.npz'}")
    print(f"Wrote {FIXTURES / 'golden_features.json'}  feature counts: {counts}")


if __name__ == "__main__":
    main()

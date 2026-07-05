#!/usr/bin/env python3
"""
Overnight 4-D gprMax inversion sweep for EFE PK 20 000 m (one raw trace).

Sweeps (eps_b, d_ballast, eps_s, eps_f) — the d_ballast axis maps the d–ε
degeneracy ridge that fixed-thickness grids cannot. Each combo is a real gprMax
FDTD run (~6 s); for each we record THREE objectives against the raw coda
[4,18] ns: envelope-Pearson r, W2 on the envelope, and W2 on the Softplus(b=6)
waveform. The Wasserstein objectives keep timing (envelope-r discards it) and
landed on the physical eps_b≈5.5 in the pilot.

Robust for unattended runs:
  * incremental CSV flush after every trial (partial results survive a crash)
  * RESUMABLE — re-running skips combos already in the CSV
  * progress + ETA logged every 50 trials
  * per-trial .in/.out/.vti cleanup (no disk blowup)

Usage:
    python scripts/calibration/invert_pk20000m_w2_grid.py            # full grid
    python scripts/calibration/invert_pk20000m_w2_grid.py --limit 3  # smoke test
"""
import argparse
import csv
import itertools
import sys
import time
from pathlib import Path

import h5py
import numpy as np

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "scripts" / "calibration"))
import invert_pk20000m_envelope as inv  # noqa: E402
from invert_pk20000m_envelope import write_flat_in, run_gprmax, read_ez  # noqa: E402
from src.signal_processing import (coda_envelope_correlation,  # noqa: E402
                                   coda_wasserstein_distance)

REAL_H5 = Path(r"D:/Codigo/Data/efe_full.h5")
PK_M    = 20000.0
OUT_CSV = inv.WORK_DIR / "w2_grid4d.csv"
LOG     = inv.WORK_DIR / "w2_grid4d.log"
CODA_LO, CODA_HI = 4.0, 18.0

# ── 4-D grid: fine on the (eps_b, d_ballast) degeneracy pair, coarse on deep ──
EPS_B = np.round(np.arange(3.0, 7.001, 0.2), 3)    # 21
D_BAL = np.round(np.arange(0.28, 0.5401, 0.02), 3) # 14
EPS_S = [9.0, 11.0, 13.0, 15.0]                     # 4
EPS_F = [16.0, 19.0, 22.0, 25.0]                    # 4
# → 21 * 14 * 4 * 4 = 4704 runs (~7.8 h at 6 s/run)


def load_one_trace():
    with h5py.File(REAL_H5, "r") as f:
        dt = float(f.attrs["dt_ns"]) * 1e-9
        pk = f["pk_m"][:]
        idx = int(np.argmin(np.abs(pk - PK_M)))
        return f["traces"][idx, :].astype(float), dt, float(pk[idx])


def _key(eb, db, es, ef):
    return f"{eb:.3f}_{db:.3f}_{es:.1f}_{ef:.1f}"


def _done_set():
    s = set()
    if OUT_CSV.exists():
        with open(OUT_CSV) as fh:
            r = csv.reader(fh)
            next(r, None)
            for row in r:
                if len(row) >= 4:
                    try:
                        s.add(_key(float(row[0]), float(row[1]), float(row[2]), float(row[3])))
                    except ValueError:
                        pass
    return s


def _log(msg):
    with open(LOG, "a", encoding="utf-8") as lg:
        lg.write(msg + "\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0, help="process at most N new combos (0 = all)")
    args = ap.parse_args()

    inv.WORK_DIR.mkdir(parents=True, exist_ok=True)
    real, dt, pk_actual = load_one_trace()
    done = _done_set()
    combos = list(itertools.product(EPS_B, D_BAL, EPS_S, EPS_F))
    total = len(combos)

    new_file = not OUT_CSV.exists()
    fh = open(OUT_CSV, "a", newline="", encoding="utf-8")
    w = csv.writer(fh)
    if new_file:
        w.writerow(["eps_b", "d_ballast", "eps_s", "eps_f", "env_r", "w2_env", "w2_sp6", "ok"])
        fh.flush()

    _log(f"\n=== start {time.ctime()}  PK={pk_actual:.0f}m  total={total}  already={len(done)}  limit={args.limit} ===")
    t0 = time.time()
    n_run = 0
    for i, (eb, db, es, ef) in enumerate(combos):
        if _key(eb, db, es, ef) in done:
            continue
        if args.limit and n_run >= args.limit:
            break
        p = dict(eps_b=float(eb), d_ballast=float(db), eps_s=float(es), eps_f=float(ef))
        inp = inv.WORK_DIR / f"g_{i:06d}.in"
        try:
            write_flat_in(p, inp)
            if run_gprmax(inp):
                syn, sdt = read_ez(inp.with_suffix(".out"))
                r   = coda_envelope_correlation(syn, sdt, real, dt, CODA_LO, CODA_HI)
                w2e = coda_wasserstein_distance(syn, sdt, real, dt, CODA_LO, CODA_HI, use_envelope=True)
                w2s = coda_wasserstein_distance(syn, sdt, real, dt, CODA_LO, CODA_HI, softplus_b=6.0)
                w.writerow([f"{eb:.3f}", f"{db:.3f}", f"{es:.1f}", f"{ef:.1f}",
                            f"{r:.5f}", f"{w2e:.5f}", f"{w2s:.5f}", 1])
            else:
                w.writerow([f"{eb:.3f}", f"{db:.3f}", f"{es:.1f}", f"{ef:.1f}", "nan", "nan", "nan", 0])
            fh.flush()
        except Exception as exc:  # noqa: BLE001
            _log(f"  ERROR combo {i} ({p}): {exc}")
            w.writerow([f"{eb:.3f}", f"{db:.3f}", f"{es:.1f}", f"{ef:.1f}", "nan", "nan", "nan", 0])
            fh.flush()
        finally:
            for suf in (".in", ".out", ".vti"):
                q = inp.with_suffix(suf)
                if q.exists():
                    q.unlink()
        n_run += 1
        if n_run % 50 == 0:
            el = time.time() - t0
            rate = n_run / el if el > 0 else 0
            remaining = total - len(done) - n_run
            eta_h = remaining / rate / 3600 if rate > 0 else 0
            _log(f"{time.ctime()}  done={len(done)+n_run}/{total}  rate={rate:.2f}/s  eta={eta_h:.1f}h")

    fh.close()
    _log(f"=== finished {time.ctime()}  ran={n_run}  elapsed={(time.time()-t0)/3600:.2f}h ===")
    print(f"Done: ran {n_run} new combos. CSV -> {OUT_CSV}")


if __name__ == "__main__":
    main()

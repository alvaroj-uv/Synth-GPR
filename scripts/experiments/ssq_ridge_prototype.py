#!/usr/bin/env python3
"""
PROTOTYPE: do ssqueezepy synchrosqueezed-CWT ridge features order ballast
permittivity more cleanly than the current att_* family?

Testbed: the mbubia rock-eps sweep (test_output/mbubia_eps{03,05,08,12,16}.out)
— identical geometry, only rock permittivity varies (3->16), so a good coda
feature should order the 5 traces monotonically (|Spearman rho| ~ 1 vs eps).

Decision rule (agreed): if ssq ridge features order the sweep more cleanly
than att_*, integrate an optional ssq_* block in Phase 3; otherwise skip the
dependency. NOTE: n=5 single-geometry traces — a signal check, NOT validation.
"""
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

from src.data_loader import read_ascan
from src.signal_processing import peak_relative_coda_gate
from src.feature_extraction import extract_features_from_signal

from scipy.stats import spearmanr
from ssqueezepy import ssq_cwt
from ssqueezepy.ridge_extraction import extract_ridges

EPS = [3, 5, 8, 12, 16]
FC = 400e6


def gated_coda(path):
    a = read_ascan(str(path), component="Ez")
    sig, dt = a["signal"].astype(float), float(a["dt"])
    mask, _ = peak_relative_coda_gate(sig, dt)
    seg = sig[mask]
    m = np.max(np.abs(seg))
    return (seg / m if m > 0 else seg), dt


def ssq_ridge_features(seg, dt):
    """Ridge + TF-concentration features from the synchrosqueezed CWT."""
    fs = 1.0 / dt
    Tx, Wx, ssq_freqs, scales = ssq_cwt(seg, fs=fs)
    aTx = np.abs(Tx)

    # keep the physically relevant band (50 MHz - 2 GHz) to stabilise ridges
    band = (ssq_freqs >= 50e6) & (ssq_freqs <= 2e9)
    aTx_b = aTx[band]
    freqs_b = ssq_freqs[band]

    t_ns = np.arange(seg.size) * dt * 1e9

    # 2 ridges on the band-limited synchrosqueezed plane
    ridge_idxs = extract_ridges(aTx_b, freqs_b, penalty=2.0, n_ridges=2, bw=4)
    r0 = ridge_idxs[:, 0]
    r1 = ridge_idxs[:, 1] if ridge_idxs.shape[1] > 1 else r0

    f0 = freqs_b[r0] / 1e6                       # ridge-0 frequency track (MHz)
    a0 = aTx_b[r0, np.arange(seg.size)]          # ridge-0 amplitude track
    a1 = aTx_b[r1, np.arange(seg.size)]

    # fit only where the ridge has meaningful amplitude
    good = a0 > 0.05 * np.max(a0)
    feats = {}
    if np.count_nonzero(good) >= 8:
        feats['ssq_ridge_freq_mean_mhz'] = float(np.mean(f0[good]))
        feats['ssq_ridge_freq_slope_mhz_ns'] = float(np.polyfit(t_ns[good], f0[good], 1)[0])
        feats['ssq_ridge_amp_decay'] = float(np.polyfit(
            t_ns[good], np.log(a0[good] / np.max(a0) + 1e-12), 1)[0])
    else:
        feats.update({'ssq_ridge_freq_mean_mhz': 0.0,
                      'ssq_ridge_freq_slope_mhz_ns': 0.0,
                      'ssq_ridge_amp_decay': 0.0})

    e0, e1 = float(np.sum(a0 ** 2)), float(np.sum(a1 ** 2))
    feats['ssq_ridge2_energy_ratio'] = e1 / e0 if e0 > 0 else 0.0

    # TF concentration: Renyi-like entropy of the normalized |Tx|^2 plane
    p = aTx_b ** 2
    s = p.sum()
    if s > 0:
        p = p / s
        feats['ssq_tf_entropy'] = float(-np.sum(p * np.log(p + 1e-15)))
        # fraction of energy on the per-time argmax bins (ridge sharpness)
        feats['ssq_tf_ridge_energy_frac'] = float(
            np.sum(np.max(p, axis=0)) / np.sum(p))
    else:
        feats['ssq_tf_entropy'] = 0.0
        feats['ssq_tf_ridge_energy_frac'] = 0.0
    return feats


def main():
    rows = []
    for e in EPS:
        p = ROOT / "test_output" / f"mbubia_eps{e:02d}.out"
        if not p.exists():
            print(f"[missing] {p}")
            return 1
        a = read_ascan(str(p), component="Ez")
        sig, dt = a["signal"].astype(float), float(a["dt"])

        # baseline: current extractor's att_* (+ two coda spectral refs)
        fd = extract_features_from_signal(sig, dt=dt, center_freq_hz=FC).iloc[0]
        row = {k: float(fd[k]) for k in fd.index if k.startswith('att_')}
        row['coda_median_frequency_mhz'] = float(fd['coda_median_frequency']) / 1e6
        row['coda_spectral_flatness'] = float(fd['coda_spectral_flatness'])

        # challenger: ssq ridge features on the same gated, normalized coda
        seg, dt2 = gated_coda(p)
        row.update(ssq_ridge_features(seg, dt2))
        row['eps'] = e
        rows.append(row)
        print(f"eps={e:>2} done ({len(row)-1} features)")

    import pandas as pd
    df = pd.DataFrame(rows).set_index('eps')

    print("\n=== |Spearman rho| vs eps (n=5; 1.0 = perfectly monotone) ===")
    res = []
    for c in df.columns:
        if df[c].nunique() <= 1:
            rho = 0.0
        else:
            rho = spearmanr(df.index.values, df[c].values).correlation
        fam = 'SSQ' if c.startswith('ssq_') else 'ATT/CODA'
        res.append((abs(rho), rho, fam, c))
    res.sort(reverse=True)
    print(f"{'|rho|':>6} {'rho':>6}  {'family':<9} feature")
    for arho, rho, fam, c in res:
        print(f"{arho:>6.2f} {rho:>+6.2f}  {fam:<9} {c}")

    fams = {}
    for arho, _, fam, _ in res:
        fams.setdefault(fam, []).append(arho)
    print("\n=== family summary (mean / max |rho|, n features) ===")
    for fam, v in fams.items():
        print(f"  {fam:<9} mean={np.mean(v):.2f}  max={np.max(v):.2f}  n={len(v)}")

    out = ROOT / "test_output" / "ssq_prototype_results.csv"
    df.to_csv(out)
    print(f"\nsaved -> {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

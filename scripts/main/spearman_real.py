#!/usr/bin/env python3
"""
DIAGNOSTIC 2: Spearman correlation of real FI vs each of the 572 features.

If no single feature correlates monotonically with FI (|rho| well above noise),
the real fouling signal is not captured by these features (or FI<->trace
coupling is broken). Shapovalov 2026 reported Hilbert-envelope r~0.96 with FI,
so the Hilbert features are the key comparison point.

Usage:
    python scripts/main/spearman_real.py
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

REAL_CSV = ROOT / "docs" / "input" / "feature_dataset_real.csv"
REPORT_PATH = ROOT / "output" / "spearman_real.txt"


def main():
    real = pd.read_csv(REAL_CSV)
    fi = real["FI"].values
    feat_cols = [c for c in real.columns if c not in ("ID", "FI", "FI_class")]

    rows = []
    for c in feat_cols:
        x = real[c].values
        if np.all(x == x[0]):  # constant feature
            rho, p = 0.0, 1.0
        else:
            rho, p = spearmanr(x, fi)
        rows.append((c, rho, p))
    d = pd.DataFrame(rows, columns=["feature", "rho", "p"]).dropna()
    d["absrho"] = d["rho"].abs()
    d = d.sort_values("absrho", ascending=False)

    # Significance with multiple-comparison context (572 tests)
    bonf = 0.05 / len(feat_cols)

    lines = []

    def log(m=""):
        print(m)
        lines.append(m)

    log("=" * 64)
    log("SPEARMAN — real FI vs each of 572 waveform features (n=101)")
    log("=" * 64)
    log(f"Bonferroni alpha = 0.05/{len(feat_cols)} = {bonf:.2e}")
    log(f"|rho| max = {d['absrho'].max():.3f}   median = {d['absrho'].median():.3f}")
    log(f"# features |rho|>0.3 : {(d['absrho'] > 0.3).sum()}")
    log(f"# features |rho|>0.5 : {(d['absrho'] > 0.5).sum()}")
    log(f"# features p<Bonferroni : {(d['p'] < bonf).sum()}")
    log()
    log("Top-25 features by |Spearman rho|:")
    log(f"  {'rho':>7}  {'p':>10}  feature")
    for _, r in d.head(25).iterrows():
        flag = " *" if r["p"] < bonf else ""
        log(f"  {r['rho']:>7.3f}  {r['p']:>10.2e}  {r['feature']}{flag}")
    log()

    # Spotlight Hilbert features (Shapovalov r~0.96 reference)
    hil = d[d["feature"].str.startswith("hilbert")].head(10)
    log("Hilbert-feature correlations (Shapovalov 2026 reported r~0.96):")
    for _, r in hil.iterrows():
        log(f"  {r['rho']:>7.3f}  {r['p']:>10.2e}  {r['feature']}")
    log()

    log("=" * 64)
    log("VERDICT")
    log("=" * 64)
    if d["absrho"].max() < 0.3:
        log("No feature exceeds |rho|=0.3 -> NO monotonic FI signal in features.")
        log("Fouling is not encoded in these real coda features (or ID<->FI")
        log("matching is broken). Next: verify trace<->FI alignment / FI quality.")
    elif (d["p"] < bonf).any():
        n = (d['p'] < bonf).sum()
        log(f"{n} feature(s) significantly correlate with FI (Bonferroni).")
        log(f"Strongest |rho|={d['absrho'].max():.3f}. Signal EXISTS but is weak;")
        log("classifier/scaling and class boundaries are the bottleneck, not data.")
    else:
        log("Some |rho|>0.3 but none survive multiple-comparison correction.")
        log("Signal is marginal at best; treat with caution.")

    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")
    print(f"\nReport saved -> {REPORT_PATH}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Extract Features from REAL GPR Traces (field validation set)

Applies the *exact same* 572-feature pipeline used for the synthetic dataset
(src.feature_extraction.extract_features) to the real, processed field traces
in docs/input, then merges with the real Fouling Index (FI) labels.

Input files (docs/input):
    - df_Signaux_traitees_S1.csv : processed/normalized A-scans (long format:
      Time, GPR, ID). Time is a SAMPLE INDEX (61..310), dt = 0.1 ns.
    - df_pandoscope_med.csv      : reference measurements with FI per ID.

Real acquisition: 400 MHz antenna, dt = 0.1 ns/sample == PC.DEFAULT_DT (1e-10),
so NO dt override is needed -- features are directly comparable to synthetic.

Placeholders: rows with FI == 0.4933 (== Prof_BC null) are NOT real
measurements and are excluded.

Output:
    docs/input/feature_dataset_real.csv
    Columns: [ID, FI, FI_class, <572 waveform features>]

Usage:
    python scripts/main/extract_features_real.py
"""

import sys
from pathlib import Path
import numpy as np
import pandas as pd

# Add project root to path
ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT))

import importlib.util

from src.feature_extraction import extract_features
from src.physics import classify_fouling_index
from src.constants import PC

# Shared coda-window rule, identical to the synthetic coda-aligned build
_spec = importlib.util.spec_from_file_location(
    "coda_build", Path(__file__).resolve().parent / "build_parquet_coda_aligned.py"
)
_coda_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_coda_mod)
coda_window = _coda_mod.coda_window

INPUT_DIR = ROOT / "docs" / "input"
SIGNALS_CSV = INPUT_DIR / "Señales_Tratadas" / "df_Signaux_traitees_S1.csv"
MED_CSV = INPUT_DIR / "Mediciones_FI" / "df_pandoscope_med.csv"
OUTPUT_CSV = INPUT_DIR / "feature_dataset_real.csv"

PLACEHOLDER_FI = 0.4933  # sentinel value for missing measurement


def load_wide_signals(signals_csv: Path) -> pd.DataFrame:
    """
    Convert the long-format processed traces (Time, GPR, ID) into the WIDE
    format expected by extract_features: one 'Time' column + one column per
    trace (named by ID), aligned on the shared sample-index axis.
    """
    long = pd.read_csv(signals_csv)
    # Pivot: index=Time (sample idx), columns=ID, values=GPR amplitude
    wide = long.pivot(index="Time", columns="ID", values="GPR")
    wide = wide.sort_index()

    # extract_features keys signals by column name; use the raw ID as the
    # column label so we can map features back to ID afterwards.
    wide.columns = [str(c) for c in wide.columns]
    wide = wide.reset_index().rename(columns={"Time": "Time"})
    return wide


def main():
    if not SIGNALS_CSV.exists():
        raise FileNotFoundError(f"Missing {SIGNALS_CSV}")
    if not MED_CSV.exists():
        raise FileNotFoundError(f"Missing {MED_CSV}")

    print(f"Loading processed traces: {SIGNALS_CSV.name}")
    wide = load_wide_signals(SIGNALS_CSV)
    n_traces = wide.shape[1] - 1
    print(f"  {n_traces} traces x {wide.shape[0]} samples (sample axis)")

    # The real _S1 traces ARE ALREADY the coda window (raw samples 61..310, i.e.
    # 250 samples starting at the direct-pulse peak). So we do NOT re-seek a peak
    # here (their dewowed max is an interior coda reflection, not the direct
    # pulse). We only dewow + peak-normalize, matching the amplitude/processing
    # the synthetic coda_window applies AFTER its cut. Result: identical 250-
    # sample time support and unit amplitude scale on both sides.
    print("Dewow + peak-normalize each real coda trace (no re-cut)...")
    id_cols = [c for c in wide.columns if c != "Time"]
    coda = {"Time": np.arange(wide.shape[0])}
    for c in id_cols:
        s = _coda_mod.dewow(wide[c].values, 50)
        m = np.max(np.abs(s))
        coda[c] = s / m if m > 0 else s
    wide = pd.DataFrame(coda)

    # Extract features using the IDENTICAL synthetic pipeline (dt defaults to
    # PC.DEFAULT_DT = 1e-10 = 0.1 ns, matching the 400 MHz acquisition).
    print("Extracting 572 waveform features (synthetic-identical pipeline)...")
    feats = extract_features(wide)
    # 'Signal' column holds the trace ID (as string)
    feats["ID"] = feats["Signal"].astype(int)
    feats = feats.drop(columns=["Signal"])

    # Merge with real FI labels
    med = pd.read_csv(MED_CSV)[["ID", "FI_Estimado_Medio_JRO_Final"]]
    med = med.rename(columns={"FI_Estimado_Medio_JRO_Final": "FI"})

    df = feats.merge(med, on="ID", how="inner")

    # Drop placeholder (non-measured) rows
    before = len(df)
    df = df[df["FI"].round(4) != PLACEHOLDER_FI].copy()
    print(f"  Dropped {before - len(df)} placeholder rows (FI=={PLACEHOLDER_FI})")

    # Label with the same Selig & Waters classification as synthetic
    df["FI_class"] = df["FI"].apply(classify_fouling_index)

    # Reorder: ID, FI, FI_class, then features
    feat_cols = [c for c in df.columns if c not in ("ID", "FI", "FI_class")]
    df = df[["ID", "FI", "FI_class"] + feat_cols].sort_values("ID").reset_index(drop=True)

    df.to_csv(OUTPUT_CSV, index=False)

    print("\n" + "=" * 60)
    print("Real Feature Extraction Complete!")
    print("=" * 60)
    print(f"Samples:   {len(df)}")
    print(f"Features:  {len(feat_cols)}")
    print(f"FI range:  {df['FI'].min():.2f} - {df['FI'].max():.2f}")
    print(f"Class dist:\n{df['FI_class'].value_counts().sort_index().to_string()}")
    print(f"Output:    {OUTPUT_CSV}")
    print("=" * 60)


if __name__ == "__main__":
    main()

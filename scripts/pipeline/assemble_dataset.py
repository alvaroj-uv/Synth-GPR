"""Assemble the unified features+metadata table the hypothesis harness consumes.

Walks a directory of synthetic gprMax .out files (and optionally real DZTs),
runs the CANONICAL chain on every trace — preprocess_physical (T2, explicit dt)
then extract_features (T1) — reads scene metadata from the sibling .in file via
the canonical ``## key: value`` header parser (src.file_reader), and writes one
Parquet table with the schema:

    <waveform features...> | label | domain | group | fidelity_level | meta_*

ANTI-CIRCULARITY (the core research constraint): eps / sigma / pvc and every
other scene parameter are emitted ONLY as ``meta_*`` columns, NEVER as features.
The waveform-feature columns are derived purely from the received signal, so a
model trained on them cannot cheat by reading the simulation inputs. A runtime
guard (and tests/test_assemble_dataset.py) assert no feature column name
contains eps|sigma|pvc|fi_.

  - domain: "sim" for .out, "real" for DZT traces.
  - group:  CONFIG_base_seed/actual_seed for sim (block-CV key so traces from
            one scene never split across train/test); a section id for real.
  - label:  fouling class. For sim — STRICT: Lab_Class only (LabWorker's Selig
            P4+P200 measurement of the built geometry), else None. Deliberately
            NOT FI_class (a pre-build sampling target, not ground truth) and NOT
            a pvc-derived estimate — a weaker guess dressed as ground truth is
            worse than a missing label. Scenes without a LabWorker pass are
            excluded from training by the harness, not silently mislabeled.
            For real — from the --real-labels CSV.
  - fidelity_level: CONFIG_fidelity_level if present (see T9), else "unknown".

Note: preprocess_physical (dewow+time-zero, NO normalization) is applied for
cross-domain consistency; the harness applies normalize_for_features across
domains. (Physical preprocessing can hurt synthetic-ONLY tasks — see memory
'Real Feature Pipeline' — but this table is for the sim->real setting.)

Usage:
    python scripts/pipeline/assemble_dataset.py --sim-dir DIR --out dataset.parquet
        [--real-dir DIR --real-labels labels.csv --real-stride 500]
        [--fidelity-default unknown]
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from src.data_loader import read_ascan  # noqa: E402
from src.dataset_io import save_dataset  # noqa: E402
from src.dzt_io import read_dzt_traces  # noqa: E402
from src.feature_extraction import extract_features_from_signal  # noqa: E402
from src.preprocessing import preprocess_physical  # noqa: E402
from src.file_reader import parse_metadata_file  # noqa: E402

RESERVED = {"label", "domain", "group", "fidelity_level", "Signal"}
_FORBIDDEN = ("eps", "sigma", "pvc", "fi_")


def feature_columns(columns):
    """Pure waveform-feature columns: everything that is not a reserved schema
    column and not a meta_* provenance/parameter column."""
    return [c for c in columns if c not in RESERVED and not str(c).startswith("meta_")]


def assert_no_circular_features(columns):
    bad = [c for c in feature_columns(columns)
           if any(tok in str(c).lower() for tok in _FORBIDDEN)]
    if bad:
        raise AssertionError(
            f"Circular feature columns leak scene params {sorted(bad)[:8]} — "
            f"eps/sigma/pvc/fi_* must be meta_* only.")


def _read_config(in_path: Path) -> dict:
    """Read the .in file's full ``## key: value`` metadata (position-independent,
    reads both bare keys like Lab_Class/FI_class/pvc AND CONFIG_-prefixed keys
    like CONFIG_base_seed/CONFIG_center_freq_hz — see src.file_reader for the
    single canonical parser this reuses, also used by the geometry parser, the
    A-scan visualizer, and the scene repository). Empty dict if the file is
    missing (mirrors the previous behaviour of this function).
    """
    if not in_path.exists():
        return {}
    return parse_metadata_file(in_path)


def _label_from_config(cfg):
    """Ground truth = Lab_Class only (LabWorker's measured Selig P4+P200
    classification of the built geometry). Deliberately no fallback to
    FI_class (a pre-build sampling TARGET, not ground truth) or a pvc-derived
    estimate: a weaker guess dressed as ground truth is worse than a missing
    label. Scenes without a LabWorker pass get label=None and are excluded
    from training by the harness, not silently mislabeled.
    """
    lab_class = cfg.get("Lab_Class")
    return str(lab_class) if lab_class is not None else None


def _group_from_config(cfg, fallback):
    for k in ("CONFIG_base_seed", "CONFIG_actual_seed", "CONFIG_group_seed",
             "group_seed", "base_seed", "actual_seed", "seed"):
        if k in cfg and cfg[k] not in (None, ""):
            return str(cfg[k])
    return fallback


def _row_from_out(out_path: Path, fidelity_default: str) -> dict:
    d = read_ascan(str(out_path))
    sig = np.asarray(d["signal"], dtype=float)
    dt = float(d["dt"])
    proc, _fb, _dt = preprocess_physical(sig, dt)

    cfg = _read_config(out_path.with_suffix(".in"))

    cf = cfg.get("CONFIG_center_freq_hz")
    feat = extract_features_from_signal(
        proc, dt=dt, center_freq_hz=(float(cf) if cf else None))
    row = {k: v for k, v in feat.iloc[0].to_dict().items() if k != "Signal"}

    row["domain"] = "sim"
    row["label"] = _label_from_config(cfg)
    row["group"] = _group_from_config(cfg, fallback=out_path.stem)
    row["fidelity_level"] = str(cfg.get("fidelity_level", fidelity_default))
    for k, v in cfg.items():                       # every scene param -> meta_*
        row[f"meta_{k}"] = v
    return row


def _rows_from_dzt(dzt_path: Path, labels: dict, stride: int,
                   fidelity_default: str):
    traces, meta = read_dzt_traces(dzt_path)
    real_dt = float(meta["sample_interval_ns"]) * 1e-9
    stem = dzt_path.stem
    label = labels.get(stem)
    rows = []
    for i in range(0, traces.shape[0], max(1, stride)):
        proc, _fb, _dt = preprocess_physical(np.asarray(traces[i], float), real_dt)
        feat = extract_features_from_signal(proc, dt=real_dt, center_freq_hz=400e6)
        row = {k: v for k, v in feat.iloc[0].to_dict().items() if k != "Signal"}
        row["domain"] = "real"
        row["label"] = label
        row["group"] = stem
        row["fidelity_level"] = fidelity_default
        row["meta_real_trace_idx"] = int(i)
        rows.append(row)
    return rows


def _load_labels(csv_path):
    if not csv_path:
        return {}
    df = pd.read_csv(csv_path)
    key = "file" if "file" in df.columns else df.columns[0]
    val = "label" if "label" in df.columns else df.columns[-1]
    return {Path(str(f)).stem: lab for f, lab in zip(df[key], df[val])}


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--sim-dir", type=Path, help="Directory of gprMax .out files.")
    ap.add_argument("--real-dir", type=Path, help="Directory of GSSI .dzt files.")
    ap.add_argument("--real-labels", type=Path, help="CSV mapping DZT stem -> label.")
    ap.add_argument("--real-stride", type=int, default=500,
                    help="Take every Nth real trace (default 500).")
    ap.add_argument("--fidelity-default", default="unknown")
    ap.add_argument("--out", type=Path, required=True, help="Output .parquet path.")
    args = ap.parse_args()

    rows = []
    if args.sim_dir:
        outs = sorted(Path(args.sim_dir).rglob("*.out"))
        print(f"[sim] {len(outs)} .out files under {args.sim_dir}")
        for i, p in enumerate(outs, 1):
            try:
                rows.append(_row_from_out(p, args.fidelity_default))
            except Exception as e:  # noqa: BLE001 — keep going, report the file
                print(f"  [skip] {p.name}: {type(e).__name__}: {e}")
            if i % 50 == 0:
                print(f"  ...{i}/{len(outs)}")

    if args.real_dir:
        labels = _load_labels(args.real_labels)
        dzts = sorted(Path(args.real_dir).rglob("*.[dD][zZ][tT]"))
        print(f"[real] {len(dzts)} DZT files, stride={args.real_stride}")
        for p in dzts:
            try:
                rows.extend(_rows_from_dzt(p, labels, args.real_stride,
                                           args.fidelity_default))
            except Exception as e:  # noqa: BLE001
                print(f"  [skip] {p.name}: {type(e).__name__}: {e}")

    if not rows:
        raise SystemExit("No rows assembled — check --sim-dir/--real-dir.")

    df = pd.DataFrame(rows)
    assert_no_circular_features(df.columns)

    # Column order: features..., then reserved schema, then meta_*.
    feats = feature_columns(df.columns)
    schema = ["label", "domain", "group", "fidelity_level"]
    metas = [c for c in df.columns if str(c).startswith("meta_")]
    df = df[feats + schema + metas]

    args.out.parent.mkdir(parents=True, exist_ok=True)
    save_dataset(df, args.out)
    print(f"\nWrote {args.out}: {len(df)} rows x {df.shape[1]} cols "
          f"({len(feats)} features, {len(metas)} meta). "
          f"domains={df['domain'].value_counts().to_dict()}")


if __name__ == "__main__":
    main()

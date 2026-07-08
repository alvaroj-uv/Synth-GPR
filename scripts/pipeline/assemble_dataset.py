"""Assemble the unified features+metadata table the hypothesis harness consumes.

Walks a directory of synthetic gprMax .out files (and optionally real DZTs),
runs the CANONICAL chain on every trace — preprocess_physical (T2, explicit dt)
then extract_features (T1) — reads scene metadata from the sibling .in
``## CONFIG_*`` headers, and writes one Parquet table with the schema:

    <waveform features...> | label | domain | group | fidelity_level | meta_*

ANTI-CIRCULARITY (the core research constraint): eps / sigma / pvc and every
other scene parameter are emitted ONLY as ``meta_*`` columns, NEVER as features.
The waveform-feature columns are derived purely from the received signal, so a
model trained on them cannot cheat by reading the simulation inputs. A runtime
guard (and tests/test_assemble_dataset.py) assert no feature column name
contains eps|sigma|pvc|fi_.

  - domain: "sim" for .out, "real" for DZT traces.
  - group:  CONFIG group/base/actual seed for sim (block-CV key so traces from
            one scene never split across train/test); a section id for real.
  - label:  fouling class — from CONFIG fi_class, else derived from pvc via
            physics.convert_pvc_to_fi -> classify_fouling_index; from the
            --real-labels CSV for real.
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
from src.dzt_io import read_dzt_traces  # noqa: E402
from src.feature_extraction import extract_features_from_signal  # noqa: E402
from src.preprocessing import preprocess_physical  # noqa: E402
from src.physics import convert_pvc_to_fi, classify_fouling_index  # noqa: E402

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
    """Robustly scan ALL '## CONFIG_key: value' lines, position-independent.

    file_reader.extract_config_from_in_file stops at the first non-'##' line, so
    it misses CONFIG headers written after a '#title'/'#domain' line (the common
    layout). This scans the whole header. Values are type-inferred.
    """
    cfg = {}
    if not in_path.exists():
        return cfg
    with open(in_path, encoding="utf-8", errors="replace") as f:
        for line in f:
            s = line.strip()
            if not s.startswith("## CONFIG_") or ":" not in s:
                continue
            key_part, value = s[2:].split(":", 1)          # drop leading '##'
            key = key_part.strip()[len("CONFIG_"):].lower()
            v = value.strip()
            if v.lower() == "true":
                cfg[key] = True
            elif v.lower() == "false":
                cfg[key] = False
            elif v.lstrip("-").isdigit():
                cfg[key] = int(v)
            else:
                try:
                    cfg[key] = float(v)
                except ValueError:
                    cfg[key] = v
    return cfg


def _label_from_config(cfg):
    if "fi_class" in cfg:
        return str(cfg["fi_class"])
    pvc = cfg.get("pvc_sampled", cfg.get("pvc"))
    if pvc is not None:
        try:
            return classify_fouling_index(convert_pvc_to_fi(float(pvc)))
        except (TypeError, ValueError):
            return None
    return None


def _group_from_config(cfg, fallback):
    for k in ("group_seed", "base_seed", "actual_seed", "seed"):
        if k in cfg and cfg[k] not in (None, ""):
            return str(cfg[k])
    return fallback


def _row_from_out(out_path: Path, fidelity_default: str) -> dict:
    d = read_ascan(str(out_path))
    sig = np.asarray(d["signal"], dtype=float)
    dt = float(d["dt"])
    proc, _fb, _dt = preprocess_physical(sig, dt)

    cfg = _read_config(out_path.with_suffix(".in"))

    cf = cfg.get("center_freq_hz")
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
    df.to_parquet(args.out, index=False)
    print(f"\nWrote {args.out}: {len(df)} rows x {df.shape[1]} cols "
          f"({len(feats)} features, {len(metas)} meta). "
          f"domains={df['domain'].value_counts().to_dict()}")


if __name__ == "__main__":
    main()

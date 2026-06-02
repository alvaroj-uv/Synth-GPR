#!/usr/bin/env python3
"""
Recalculate Lab_LDCP_FI_est IN-PLACE in existing .in files from their stored
Lab_LDCP_FH + porosity, using the Rojas-Vivanco 2025 quadratic
(src.physics.fi_from_fouling_height) instead of the old linear FH/1.5.

No re-simulation needed — only the header label is rewritten. The waveform .out
files are untouched. After this, rebuild the parquet to pick up the new values.

Safe by default: DRY-RUN (prints stats, writes nothing). Pass --apply to write.

Usage:
    python scripts/main/recalc_ldcp_fi_est.py --dir output/gpr_synth_dataset_80k
    python scripts/main/recalc_ldcp_fi_est.py --dir output/gpr_synth_dataset_80k --apply
"""

import sys
import re
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from src.physics import fi_from_fouling_height

FH_RE = re.compile(r"## Lab_LDCP_FH:\s*([-\d.]+)")
POR_RE = re.compile(r"## porosity:\s*([-\d.]+)")
EST_RE = re.compile(r"(## Lab_LDCP_FI_est:\s*)([-\d.]+)")


def recompute(in_path: Path, apply: bool):
    """Return (old, new) FI_est for one file, writing if apply=True. None if skip."""
    content = in_path.read_text(encoding="utf-8", errors="ignore")
    fh_m = FH_RE.search(content)
    if not fh_m:
        return None
    fh = float(fh_m.group(1))
    por_m = POR_RE.search(content)
    porosity = float(por_m.group(1)) if por_m else None

    new_val = round(fi_from_fouling_height(fh, porosity), 2)
    est_m = EST_RE.search(content)
    old_val = float(est_m.group(2)) if est_m else None

    if apply:
        if est_m:
            content = EST_RE.sub(rf"\g<1>{new_val}", content, count=1)
        else:
            # insert after Lab_LDCP_FH line
            content = re.sub(r"(## Lab_LDCP_FH:\s*[-\d.]+\n)",
                             rf"\1## Lab_LDCP_FI_est: {new_val}\n", content, count=1)
        in_path.write_text(content, encoding="utf-8")

    return old_val, new_val


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default="output/gpr_synth_dataset_80k")
    ap.add_argument("--apply", action="store_true", help="write changes (default: dry-run)")
    args = ap.parse_args()

    ins = sorted(Path(args.dir).rglob("*.in"))
    if not ins:
        print(f"No .in files in {args.dir}")
        sys.exit(1)

    print(f"{'APPLYING' if args.apply else 'DRY-RUN'} on {len(ins)} files in {args.dir}\n")

    n = changed = 0
    max_diff = 0.0
    examples = []
    for p in ins:
        r = recompute(p, args.apply)
        if r is None:
            continue
        old, new = r
        n += 1
        if old is None or abs(old - new) > 0.01:
            changed += 1
            if old is not None:
                max_diff = max(max_diff, abs(old - new))
            if len(examples) < 8:
                examples.append((p.name, old, new))

    print(f"Processed     : {n}")
    print(f"Changed       : {changed}")
    print(f"Max abs delta FI_est: {max_diff:.2f}")
    print("\nExamples (old -> new):")
    for name, old, new in examples:
        print(f"  {name}: {old} -> {new}")
    if not args.apply:
        print("\n(DRY-RUN — nothing written. Re-run with --apply to commit.)")
    else:
        print("\nDone. Rebuild the parquet to pick up the new Lab_LDCP_FI_est.")


if __name__ == "__main__":
    main()

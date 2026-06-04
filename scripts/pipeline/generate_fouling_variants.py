#!/usr/bin/env python3
"""
Generate fouling-height variants from existing .in files.

For each source .in file, produce one variant per PVC target:
  - Copy ALL content verbatim (rocks, domain, antenna, materials)
  - Add  ## cloned_from: <source>  header
  - Add  #messages: n              (suppress gprMax output)
  - Replace the fouling #box: y2 coordinate
  - Recompute Lab_FI / Lab_P4 / Lab_P200 / Lab_Class analytically
  - Name sequentially: s_5000.in, s_5001.in, ...

No rock reconstruction. No LabWorker. No Monte Carlo.

Usage:
    python scripts/pipeline/generate_fouling_variants.py [options]

    --source-dir   DIR   default: output/dataset_1k
    --output-dir   DIR   default: output/dataset_variants
    --start-id     N     first sequential ID  (default: 5000)
    -n N                 limit source files   (default: all)
    -j N                 parallel workers     (default: 4)
"""

import sys
import re
import argparse
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from src.physics import classify_fouling_index

# ── Config ───────────────────────────────────────────────────────────────────
PVC_TARGETS = [0.02, 0.12, 0.30, 0.50, 0.80]

# ── Header keys to rewrite ────────────────────────────────────────────────────
_UPDATE_KEYS = {"pvc", "FI_class", "Lab_FI", "Lab_P4", "Lab_P200", "Lab_Class"}

# ── Regexes ───────────────────────────────────────────────────────────────────
_HDR_RE = re.compile(r"^## ([^:]+):\s*(.*)")
_BOX_RE = re.compile(r"^#box:\s+", re.IGNORECASE)
_DOM_RE = re.compile(r"^#domain:\s+", re.IGNORECASE)
_MSG_RE = re.compile(r"^#messages:\s+", re.IGNORECASE)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _parse_meta(lines):
    meta = {}
    for line in lines:
        m = _HDR_RE.match(line.strip())
        if m:
            meta[m.group(1).strip()] = m.group(2).strip()
    return meta


def _domain_xz(lines):
    """Return (domain_x, dx) from #domain: x y z."""
    for line in lines:
        if _DOM_RE.match(line.strip()):
            toks = line.split()
            if len(toks) >= 4:
                return float(toks[1]), float(toks[3])
    return 2.248, 0.0132


def _compute_fi(h_foul, domain_x, H_ballast, lab_por):
    layer = domain_x * H_ballast * 1e6
    rock  = (1.0 - lab_por) * layer
    foul  = h_foul * domain_x * 1e6 * lab_por
    total = rock + foul
    if total <= 0:
        return 0.0, 0.0, 0.0, "C"
    P4   = foul / total * 100.0
    P200 = P4 * 0.30
    FI   = P4 + P200
    return round(FI, 4), round(P4, 4), round(P200, 4), classify_fouling_index(FI)


def _make_variant(lines, new_fouling_top, new_meta, source_name, new_id):
    """
    Build variant file lines:
      - Inject ## cloned_from and ## sample_id after opening banner
      - Inject #messages: n after #domain:
      - Update _UPDATE_KEYS header fields
      - Update fouling box y2
    """
    out = []
    cloned_injected  = False
    messages_injected = False
    box_replaced      = False

    for line in lines:
        stripped = line.strip()

        # Inject cloned_from + sample_id after first banner line
        if not cloned_injected and stripped.startswith("## ==="):
            out.append(line)
            out.append(f"## cloned_from: {source_name}\n")
            out.append(f"## sample_id: {new_id}\n")
            cloned_injected = True
            continue

        # Rewrite tracked header fields
        m = _HDR_RE.match(stripped)
        if m and m.group(1).strip() in _UPDATE_KEYS:
            out.append(f"## {m.group(1).strip()}: {new_meta[m.group(1).strip()]}\n")
            continue

        # Skip existing #messages: line (we will write our own)
        if _MSG_RE.match(stripped):
            continue

        # After #domain: inject #messages: n
        if not messages_injected and _DOM_RE.match(stripped):
            out.append(line)
            out.append("#messages: n\n")
            messages_injected = True
            continue

        # Replace fouling box y2
        if not box_replaced and _BOX_RE.match(stripped):
            toks = stripped.split()
            if len(toks) >= 8 and toks[7].startswith("bal_foul"):
                toks[5] = f"{new_fouling_top:.7f}"
                out.append(" ".join(toks) + "\n")
                box_replaced = True
                continue

        out.append(line)

    return out


# ── Worker ────────────────────────────────────────────────────────────────────

def _process(args):
    src_str, out_str, pvc_targets, src_idx, start_id = args
    src  = Path(src_str)
    odir = Path(out_str)

    try:
        with open(src, encoding="utf-8", errors="replace") as fh:
            lines = fh.readlines()
    except OSError:
        return src.name, 0, len(pvc_targets)

    meta              = _parse_meta(lines)
    domain_x, dx     = _domain_xz(lines)

    try:
        lab_por = float(meta.get("Lab_Porosity",    0.394))
        bal_bot = float(meta.get("ballast_bottom_y", 0.300))
        bal_top = float(meta.get("ballast_top_y",    0.796))
    except (ValueError, TypeError):
        return src.name, 0, len(pvc_targets)

    H_ballast = bal_top - bal_bot
    if H_ballast <= 0:
        return src.name, 0, len(pvc_targets)

    n_written = n_errors = 0

    for v_idx, pvc_frac in enumerate(pvc_targets):
        new_id = start_id + src_idx * len(pvc_targets) + v_idx
        try:
            h_foul   = max(pvc_frac * H_ballast, dx)
            h_foul   = min(h_foul, H_ballast)
            foul_top = bal_bot + h_foul

            FI, P4, P200, cls = _compute_fi(h_foul, domain_x, H_ballast, lab_por)

            new_meta = {
                "pvc"      : round(pvc_frac * 100, 4),
                "FI_class" : cls,
                "Lab_FI"   : FI,
                "Lab_P4"   : P4,
                "Lab_P200" : P200,
                "Lab_Class": cls,
            }

            variant_lines = _make_variant(lines, foul_top, new_meta, src.name, new_id)

            out_path = odir / f"s_{new_id:04d}.in"
            with open(out_path, "w", encoding="utf-8") as fh:
                fh.writelines(variant_lines)
            n_written += 1

        except Exception:
            n_errors += 1

    return src.name, n_written, n_errors


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-dir", default="output/dataset_1k")
    parser.add_argument("--output-dir", default="output/dataset_variants")
    parser.add_argument("--start-id",  type=int, default=5000)
    parser.add_argument("-n", "--max-files", type=int, default=None)
    parser.add_argument("-j", "--workers",   type=int, default=4)
    args = parser.parse_args()

    src_dir = Path(args.source_dir)
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    sources = sorted(f for f in src_dir.glob("s_*.in") if "_v" not in f.stem)
    if args.max_files:
        sources = sources[:args.max_files]

    n_src = len(sources)
    n_exp = n_src * len(PVC_TARGETS)
    id_end = args.start_id + n_exp - 1

    print(f"Source dir  : {src_dir}  ({n_src} files)")
    print(f"Output dir  : {out_dir}")
    print(f"PVC targets : {[f'{p*100:.0f}%' for p in PVC_TARGETS]}")
    print(f"Expected    : {n_exp} files  (s_{args.start_id:04d}.in … s_{id_end:04d}.in)")
    print(f"Workers     : {args.workers}")
    print()

    tasks = [
        (str(f), str(out_dir), PVC_TARGETS, idx, args.start_id)
        for idx, f in enumerate(sources)
    ]

    done = written = errors = 0
    with ProcessPoolExecutor(max_workers=args.workers) as ex:
        futs = {ex.submit(_process, t): t[0] for t in tasks}
        for fut in as_completed(futs):
            _, nw, ne = fut.result()
            done    += 1
            written += nw
            errors  += ne
            if done % 500 == 0 or done == n_src:
                print(f"  {done/n_src*100:5.1f}%  {done}/{n_src}  written={written}  errors={errors}")

    print()
    print(f"Done.  Written: {written}  Errors: {errors}")
    print(f"Output: {out_dir}")


if __name__ == "__main__":
    main()

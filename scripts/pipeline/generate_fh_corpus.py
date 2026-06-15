#!/usr/bin/env python3
"""Generate the FH-geometry fouling corpus (layers-mode, balanced classes).

Each sample is a two-sublayer ballast bed: a FOULED bottom (rocks in a fouling
matrix) + a CLEAN top (rocks in air), on formation + subgrade. The fouling
HEIGHT fraction (FH = fouled / total ballast) sets the Selig class via the
Rojas-Vivanco medium curve -- the SAME label definition as the real pandoscope
data (so synthetic and real labels mean the same thing).

Nuisance axes vary per sample (packing seed, layer thicknesses, subsurface and
fouling permittivity ~ a moisture proxy) so a waveform-only model learns
FH-robust coda features rather than memorising one geometry. Classes are
BALANCED (n per class); the real eval set keeps its natural distribution.

Outputs <out>/s_<id>.in (correct FI_class header via the geometry label) and
<out>/manifest.csv. Then: run_simulations.py for FDTD, build_parquet for
features, merge manifest labels, train, eval on real Site-1.

    python scripts/pipeline/generate_fh_corpus.py -o output/fh_corpus_v3 -n 500
"""
import argparse
import csv
import io
import sys
from contextlib import redirect_stdout
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from src.layer_spec import Layer
from src.layer_scene_builder import SceneParams, write_scene
from src.physics import fi_from_fouling_height, classify_fouling_index

CLASSES = ["C", "MC", "MF", "F", "HF"]
# FH% bands per class, derived from the medium-curve FI boundaries
# (FI=1->FH 0.8, FI=10->15.7, FI=20->34.0, FI=40->79.7). Edges nudged inward
# so the re-derived fi_class always equals the sampled target class.
FH_BANDS = {
    "C":  (0.0, 0.0),     # clean: no fouled sublayer
    "MC": (1.5, 15.5),
    "MF": (15.9, 33.8),
    "F":  (34.2, 79.4),
    "HF": (79.9, 98.0),
}
MIN_FOULED_M = 0.007  # below ~1 grid cell the fouled sublayer can't be resolved


def draw_sample(cls: str, rng: np.random.Generator) -> dict:
    lo, hi = FH_BANDS[cls]
    fh = 0.0 if cls == "C" else float(rng.uniform(lo, hi))
    return dict(
        fh=fh,
        H_ball=float(rng.uniform(0.30, 0.50)),    # ballast thickness
        H_sub=float(rng.uniform(0.15, 0.25)),     # subgrade thickness
        H_form=float(rng.uniform(0.08, 0.15)),    # formation thickness
        sub_eps=float(rng.uniform(7.0, 11.0)),    # subsurface eps (moisture proxy)
        form_eps=float(rng.uniform(9.0, 13.0)),
        foul_eps=float(rng.uniform(5.0, 7.5)),    # fouling matrix eps (dry->moist fines)
        foul_sig=float(rng.uniform(0.004, 0.012)),
    )


def build_layers(p: dict) -> list:
    """Bottom -> top: subgrade, formation, [fouled ballast], clean ballast."""
    layers = [
        Layer("subgrade", round(p["H_sub"], 3), eps=round(p["sub_eps"], 2), sigma=0.02),
        Layer("formation", round(p["H_form"], 3), eps=round(p["form_eps"], 2), sigma=0.03),
    ]
    fouled = p["H_ball"] * p["fh"] / 100.0
    clean = p["H_ball"] - fouled
    if fouled >= MIN_FOULED_M:
        layers.append(Layer("ballast_fouled", round(fouled, 3),
                            eps=round(p["foul_eps"], 2), sigma=round(p["foul_sig"], 4),
                            packed=True, rock_eps=4.0, rock_sigma=0.001,
                            matrix_name="fouling"))
    else:
        clean = p["H_ball"]
    layers.append(Layer("ballast_clean", round(clean, 3), eps=1.0, sigma=0.0,
                        packed=True, rock_eps=4.0, rock_sigma=0.001,
                        matrix_name="free_space"))
    return layers


def main() -> int:
    ap = argparse.ArgumentParser(description="Generate the balanced FH-geometry fouling corpus")
    ap.add_argument("-o", "--output", required=True, type=Path)
    ap.add_argument("-n", "--n-per-class", type=int, default=500)
    ap.add_argument("--start-id", type=int, default=10000)
    ap.add_argument("--seed", type=int, default=12345)
    ap.add_argument("--freq", type=float, default=400e6)
    ap.add_argument("--domain-x", type=float, default=1.0)
    args = ap.parse_args()

    out = args.output
    out.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(args.seed)

    manifest = []
    cid = args.start_id
    total = len(CLASSES) * args.n_per_class
    print(f"Generating {total} samples ({args.n_per_class}/class) -> {out}")
    for cls in CLASSES:
        for _ in range(args.n_per_class):
            p = draw_sample(cls, rng)
            layers = build_layers(p)
            pack_seed = int(rng.integers(1, 2**31 - 1))
            params = SceneParams(
                freq_hz=args.freq, domain_x=args.domain_x, rx_spacing=0.0,
                seed=pack_seed, rock_packing_algorithm="mbubia_ballast",
                title=f"fh_corpus {cls} FH={p['fh']:.1f}%",
            )
            fi = fi_from_fouling_height(p["fh"])
            fi_cls = classify_fouling_index(fi)
            out_in = out / f"s_{cid}.in"
            with redirect_stdout(io.StringIO()):           # silence per-scene packer/lab logs
                write_scene(layers, params, out_in)
            manifest.append(dict(
                id=cid, file=out_in.name, target_class=cls, fi_class=fi_cls,
                fh_pct=round(p["fh"], 2), fi=round(fi, 2), pack_seed=pack_seed,
                **{k: round(v, 4) for k, v in p.items() if k != "fh"},
            ))
            cid += 1
            if (cid - args.start_id) % 50 == 0:
                print(f"  {cid - args.start_id}/{total}")

    mism = sum(1 for m in manifest if m["target_class"] != m["fi_class"])
    with open(out / "manifest.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(manifest[0].keys()))
        w.writeheader()
        w.writerows(manifest)
    print(f"[OK] wrote {len(manifest)} .in + manifest.csv to {out}  "
          f"(target/fi_class mismatches: {mism})")
    return 0


if __name__ == "__main__":
    sys.exit(main())

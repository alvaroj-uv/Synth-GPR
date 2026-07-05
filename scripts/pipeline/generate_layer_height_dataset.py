#!/usr/bin/env python3
"""
Generate synthetic GPR training data with known layer heights.

Creates a grid of gprMax .in files with varying:
  - fouled ballast thickness  (0 – 40 cm)
  - clean ballast thickness   (25 – 70 cm)

Layer stack seen by the radar (top -> bottom):
  [air / antenna clearance]
  fouled_ballast   eps=8.0  sigma=0.05   (0 cm when PVC=0)
  clean_ballast    eps=3.45 sigma=0.0
  subgrade         eps=10.0 sigma=0.01   (fixed 50 cm)

Labels stored in metadata.csv:
  sample_id, fouled_m, clean_m, total_m
  where total_m = fouled_m + clean_m  (= Prof_BC analog in pandoscope)
        clean_m                       (= Prof_BS analog)

Coverage of real pandoscope data (n=112):
  Prof_BS range: 0.26 – 0.79 m  (clean layer depth)
  Prof_BC range: 0.38 – 1.08 m  (total ballast depth)

Usage:
    python scripts/pipeline/generate_layer_height_dataset.py
    python scripts/pipeline/generate_layer_height_dataset.py --out experiments/2026-06-29/layer_height_v1
    python scripts/pipeline/generate_layer_height_dataset.py --dry-run
"""

import argparse
import csv
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from src.layer_spec import Layer
from src.layer_scene_builder import SceneParams, write_scene


# ---------------------------------------------------------------------------
# Fixed simulation parameters (validated from DEFAULT_with_ballast.toml)
# ---------------------------------------------------------------------------
SCENE_PARAMS = SceneParams(
    freq_hz=420e6,
    domain_x=0.5,
    antenna_clearance=0.10,   # 10 cm standoff
    air_buffer=0.10,
    time_window=50e-9,        # 50 ns — matches real GSSI DZT window
    antenna_mode="bistatic",
    receiver_spacing=0.03,    # 30 mm TX/RX separation
    source_waveform="gaussian",
    source_amplitude=1.0,
    source_polarization="z",
    title="Layer-height dataset",
)

# Fixed subgrade below the ballast stack
SUBGRADE = Layer(name="subgrade", thickness=0.50, eps=10.0, sigma=0.01)

# Material properties — clean is fixed (Benedetto 2017)
EPS_CLEAN   = 3.45;  SIGMA_CLEAN   = 0.0
# Fouled eps is SAMPLED per-simulation: Uniform(4.0, 11.0)
#   4.0  ≈ barely fouled (FI ~5%)
#  11.0  ≈ highly fouled (pit ID11, FI ~47%, calibrated from DZT)
EPS_FOULED_MIN = 4.0
EPS_FOULED_MAX = 11.0
SIGMA_FOULED   = 0.05   # fixed conductivity (representative)

RNG = np.random.default_rng(seed=42)   # reproducible


def sample_eps_fouled() -> float:
    return float(RNG.uniform(EPS_FOULED_MIN, EPS_FOULED_MAX))


def make_layers(fouled_m: float, clean_m: float, eps_fouled: float) -> list[Layer]:
    """Build the layer stack (bottom -> top order for write_scene)."""
    layers = [SUBGRADE]
    layers.append(Layer(name="clean_ballast",  thickness=clean_m,
                        eps=EPS_CLEAN,  sigma=SIGMA_CLEAN))
    if fouled_m > 0.001:
        layers.append(Layer(name="fouled_ballast", thickness=fouled_m,
                            eps=eps_fouled, sigma=SIGMA_FOULED))
    return layers


def build_grid() -> list[tuple[float, float]]:
    """Regular grid: fouled × clean thicknesses covering the real data range."""
    fouled_levels = np.arange(0.00, 0.41, 0.05)   # 0,5,10,...,40 cm  (9 levels)
    clean_levels  = np.arange(0.25, 0.76, 0.05)   # 25,30,...,75 cm  (11 levels)
    return [(round(f, 3), round(c, 3))
            for f in fouled_levels
            for c in clean_levels]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="experiments/2026-06-29/layer_height_v1",
                    help="Output directory for .in files + metadata.csv")
    ap.add_argument("--dry-run", action="store_true",
                    help="Print what would be generated without writing files")
    args = ap.parse_args()

    out_dir = ROOT / args.out
    grid = build_grid()

    print(f"Layer-height dataset generator")
    print(f"  Samples      : {len(grid)}")
    print(f"  fouled range : 0 – 40 cm")
    print(f"  clean range  : 25 – 75 cm")
    print(f"  total range  : 25 – 115 cm  (real: 38 – 108 cm)")
    print(f"  Output dir   : {out_dir}")
    if args.dry_run:
        print("  [DRY RUN — no files written]")
    print()

    if not args.dry_run:
        out_dir.mkdir(parents=True, exist_ok=True)

    metadata = []

    for idx, (fouled_m, clean_m) in enumerate(grid):
        sample_id  = idx + 1
        total_m    = round(fouled_m + clean_m, 3)
        eps_fouled = round(sample_eps_fouled() if fouled_m > 0.001 else EPS_CLEAN, 3)
        in_name    = f"sample_{sample_id:04d}.in"
        in_path    = out_dir / in_name

        label = (f"fouled={fouled_m*100:.0f}cm(eps={eps_fouled:.1f})  "
                 f"clean={clean_m*100:.0f}cm  total={total_m*100:.0f}cm")

        if args.dry_run:
            print(f"  [{sample_id:3d}]  {in_name}  {label}")
        else:
            layers = make_layers(fouled_m, clean_m, eps_fouled)
            params = SceneParams(**{
                **SCENE_PARAMS.__dict__,
                "title": f"Layer-height #{sample_id:04d}  {label}",
            })
            try:
                write_scene(layers, params, in_path)
                print(f"  [{sample_id:3d}/{len(grid)}]  {in_name}  {label}")
            except Exception as e:
                print(f"  [{sample_id:3d}]  ERROR: {e}")
                continue

        metadata.append({
            "sample_id":  sample_id,
            "in_file":    in_name,
            "fouled_m":   fouled_m,
            "clean_m":    clean_m,
            "total_m":    total_m,
            "eps_fouled": eps_fouled,
        })

    # Write metadata.csv
    if not args.dry_run:
        meta_path = out_dir / "metadata.csv"
        fieldnames = ["sample_id", "in_file", "fouled_m", "clean_m", "total_m", "eps_fouled"]
        with open(meta_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(metadata)
        print(f"\nWrote {len(metadata)} entries to {meta_path}")

    print(f"\n--- Next step: run gprMax on all .in files ---")
    print(f"  cd {out_dir}")
    print(f"  for f in sample_*.in; do")
    print(f"      python -m gprMax \"$f\"")
    print(f"  done")
    print(f"\nOr in PowerShell:")
    print(f"  Get-ChildItem '{out_dir}\\sample_*.in' | ForEach-Object {{")
    print(f"      python -m gprMax $_.FullName")
    print(f"  }}")


if __name__ == "__main__":
    main()

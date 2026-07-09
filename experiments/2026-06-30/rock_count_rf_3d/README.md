# 3D rock-count RF (N=20, GSSI antenna, RCPGeneratorPacking spheres)

Extension of `../rock_count_rf/` and `../rock_count_rf_100/` (2D) to a real
3D geometry: granite spheres (eps=6.1) packed via `RCPGeneratorPacking`
(`rcpgen`, the C++ engine — exact target_phi, 0mm overlap) above a subgrade
box, GSSI 400MHz antenna (full physical model, not a simplified dipole),
generated via the project's proper TOML pipeline
(`scripts/pipeline/generate_3d_scene.py --config`, now with rich headers —
see main day README "sample_f050_s01" fix earlier).

## Key structural difference from 2D

**`RCPGeneratorPacking` computes rock count analytically from `target_phi`**
(N = phi*area / (pi*r_mean^2)), so count is **deterministic per fill level**
— all 4 seeds at a given `target_phi` produce the exact same rock count,
only different positions. This N=20 set therefore has only **5 distinct
target values** (91, 137, 182, 228, 273 rocks for phi=0.30/0.45/0.60/0.75/0.90),
not 20 independently-varying counts like the 2D `circlify` run had.

## Cost

~5-6 min/sample (11-16M cells, full GSSI antenna model) — N=20 took ~1h45m
total (not the estimated 2hrs, ran slightly faster than the single-sample
timing test suggested).

## Component: Ey, not Ez

The GSSI antenna model's dipole lies in a different orientation than the
simplified Hertzian dipole used in the 2D "layers" pipeline — its `.out`
files have `rxs/rx1/Ey`, no `Ez` at all. Confirmed non-trivial signal
(ringing envelope, peak ~4.4ns) when first checked.

## RF result — must use GroupKFold, not ordinary KFold

Because count is deterministic per fill level (only 5 distinct values, 4
near-duplicate seed-repeats each), an ordinary shuffled 5-fold CV leaks:
2-3 of a level's 4 repeats land in the training fold, so the model can
"memorize" that target value from near-identical siblings instead of
generalizing. Confirmed this empirically:

| CV method | R² |
|---|---|
| Ordinary KFold (shuffled, 2D-style) | **0.788** — looks great, but this is leakage from near-duplicate same-fill samples |
| **GroupKFold (grouped by fill level — the honest test)** | **0.000** (exactly, all 5 folds) |

**No real signal detected at N=20 in 3D**, once measured correctly (extrapolate to
an unseen density level, not interpolate between near-duplicates). This
isn't surprising: the 2D N=36 run also found nothing (R²≈-0.05) with a much
more favorable dataset structure (continuous per-seed count variation, no
group-leakage risk). N=20 with only 5 independent density levels is a much
harder, smaller-effective-N problem. Would need either far more distinct
fill levels (more independent targets) or a packer whose count varies
per-seed like circlify's did in 2D, to give the RF something to
generalize from.

## Files
- `sample3d_fNNN_sNN.{toml,in,out,vti}` x 20
- `generate_dataset_3d.py` — sweep driver (TOML-driven, uses
  `scripts/pipeline/generate_3d_scene.py --config`, not hand-rolled)
- `train_rf_3d.py` — feature extraction (Ey, raw) + RF + GroupKFold CV
- `generate_log_3d.txt` — full run log (rock counts, timings)

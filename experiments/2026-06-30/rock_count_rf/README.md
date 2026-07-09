# Rock-count RF feasibility check

**Goal:** test whether a RandomForestRegressor can predict the NUMBER OF
PACKED ROCKS from waveform features alone (this project's canonical
`extract_features()`, same extractor used for waveform-only fouling
classification).

## Bug found along the way

The project's default packer, `rock_packing_algorithm="pymunk_ballast"`
(resolves to `MbubiaPymunkSceneGenerator` in `layer_scene_builder.get_default_packer()`),
**silently ignores `rock_packing_target_fill` and `rock_radius_min`/`rock_radius_max`**.
`generate_rocks()` builds `BallastSimulation` with a hardcoded internal
grading curve (`get_clean_ballast_radii_distrib()`) and never reads its own
function args for those three params. Verified: two `.in` files generated
with `target_fill_ratio=0.4` vs `0.9` (same seed) are byte-identical
(`diff` = 0 lines). Switched to `rock_packing_algorithm="circlify"`, which
does respect `target_fill_ratio` (81 rocks @ fill=0.4 vs 111 @ fill=0.8,
same seed). See `project_mbubia_ballast_modeling`/`reference_packing_architecture`
memory for the full note.

## Dataset

36 samples: single ballast layer (rock=6.1 Brancadoro / matrix=3 Mbubia-Clean,
420 MHz), `rock_shape="circle"` (each rock = exactly one `#cylinder`, so
ground truth is `grep -c "#cylinder"` on the `.in` — no separate bookkeeping),
`target_fill` in {0.4,0.5,0.6,0.7,0.8,0.9} x 6 seeds. Actual rock count
achieved: 32-213 (mean 128.5, std 37.8) — a good spread, though not a clean
linear function of the requested `target_fill` (circlify trades off fewer/
larger vs more/smaller circles to hit an area target, so count and average
rock size are confounded here).

## Results

| Model | R² (5-fold CV) |
|---|---|
| RandomForestRegressor, 820 features | -0.054 ± 0.176 |
| RandomForestRegressor, top-10 features (by full-data importance) | -0.074 ± 0.678 |
| LinearRegression, `peak_max` only | -0.227 ± 0.350 |

| Simple metric vs rock count (no CV, just correlation) | r | p |
|---|---|---|
| Coda energy (5-12ns) | -0.010 | 0.955 |
| log(coda energy) | 0.005 | 0.978 |
| Coda peak amplitude | 0.363 | 0.030 |

**Conclusion: no robust signal at N=36.** Every cross-validated model (full
RF, reduced RF, single-feature linear) has R² ≤ 0, meaning none beats
predicting the mean on held-out folds. There's a marginal (p=0.03),
uncorrected, IN-SAMPLE correlation between coda peak amplitude and rock
count, but it doesn't survive 5-fold CV (test folds of ~7 samples have huge
variance at this N). Coda ENERGY has essentially zero correlation with count
— consistent with this session's earlier finding that rock count and average
rock size trade off in circlify's fill-targeting, and that per earlier
`rock_eps` tests, absolute dielectric contrast (not count) dominates coda
energy.

**This is a feasibility check, not a validated negative result.** N=36 is
small relative to 820 candidate features; a rock-count effect could be real
but too subtle to detect reliably without substantially more samples (100+)
and/or a packer that varies count independent of rock size (unlike circlify).

## Files
- `generate_dataset.py` — dataset generator (circlify, target_fill x seed sweep)
- `train_rf.py` — feature extraction + RF training + CV
- `sample_fNNN_sNN.{toml,in,out}` x 36
- `rf_feature_importances.csv`, `rf_results.txt` — full-feature RF output
- `generate_log.txt` — generation run log (rock counts per sample)

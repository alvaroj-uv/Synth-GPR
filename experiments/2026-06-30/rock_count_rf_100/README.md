# Rock-count RF feasibility check — N=100 follow-up

Follow-up to `../rock_count_rf/` (N=36, R^2 <= 0 for every model — no
detectable signal). Same method (single ballast layer, rock=6.1/matrix=3,
420 MHz, `circlify` packer, `rock_shape="circle"` for exact ground truth via
`#cylinder` counting, `extract_features()` — 820 features), scaled to
N=100: `target_fill` in {0.30, 0.45, 0.60, 0.75, 0.90} x 20 seeds each.

## Result: signal emerges at N=100

| Model | R² (5-fold CV) |
|---|---|
| RandomForestRegressor, 820 features, N=36 (prior run) | -0.054 ± 0.176 |
| **RandomForestRegressor, 820 features, N=100** | **0.264 ± 0.188** |
| LinearRegression, `coda_peak_max` only, N=100 | -0.118 ± 0.098 |

All 5 CV folds positive (0.047 to 0.594) — a modest but real, non-spurious
signal. MAE = 21.4 rocks on a 33-241 range (span 208), i.e. ~10.3% of range.

**The N=36 simple correlation didn't replicate:** `peak_max` vs rock count
was r=0.363/p=0.03 at N=36, but only r=0.113/p=0.26 at N=100 — confirms that
correlation was noise from the small sample, not a real univariate effect.
The real signal (R²=0.264) only shows up in the FULL multivariate RF, not any
single feature — it needs many features combined.

**Top features are dominated by the CODA, not the whole trace or the direct
pulse** (`coda_stft_energy_mid_mean`, `coda_grid_hilbert_imag_*`,
`coda_fb_energy_3`, `coda_stft_centroid_std`, ...) — consistent with this
project's established finding (`project_mbubia_ballast_modeling` memory)
that rock/scattering information lives in the coda, not the whole trace.

## Interpretation

- Rock count IS partially detectable from waveform features alone, but the
  effect is modest (R²~0.26, not >0.7) and needed N=100 (not N=36) to show up
  reliably — a real signal, previously masked by having too few samples
  relative to 820 candidate features.
- Confounding caveat (same as N=36): `circlify`'s `target_fill` trades off
  fewer/larger vs more/smaller circles to hit an area target, so rock COUNT
  and average rock SIZE are not independent in this dataset — the RF may be
  partially picking up on effective average rock size (which correlates with
  count here) rather than count per se. Untangling that would need a design
  where count varies independent of size (e.g. fixed radius, only fill grid
  spacing).
- N=100 is still modest for 820 features (p>>n regime) — R²=0.26 is a
  genuine feasibility signal, not something to treat as a tuned/validated
  model. A held-out test set (not just CV) and a larger N would be the next
  step if this line of work continues.

## Files
- `generate_dataset.py` — dataset generator (5 fills x 20 seeds)
- `train_rf.py` — feature extraction + RF training + CV + simple-correlation checks
- `sample_fNNN_sNN.{toml,in,out}` x 100
- `rf_feature_importances.csv`, `rf_results.txt`
- `generate_log.txt` — generation run log (rock counts per sample, all 100 succeeded)

## Follow-up: does `preprocess_signal()` help? NO — it hurts, here

Project convention (`feedback_real_feature_pipeline` memory,
`src/data_loader.py::load_batch_dataset`) says synthetic `.out` traces should
ALWAYS go through `preprocess_signal()` (dewow, time-gate direct-wave
removal, time-zero, 150-800MHz bandpass, peak-normalize) before
`extract_features()` — the original `train_rf.py` run above skipped this.
Re-ran with it applied (`train_rf_preprocessed.py`, direct-wave removal
params matched to this geometry: `center_freq_hz=420e6`, `air_gap_m=0.1`
i.e. our actual `antenna_clearance`):

| Pipeline | R² (5-fold CV) | MAE |
|---|---|---|
| Raw signal (no preprocessing) | **0.264 ± 0.188** | 21.4 rocks |
| `preprocess_signal()` applied | **-0.235 ± 0.244** (all 5 folds negative) | 28.2 rocks |

**Preprocessing made it noticeably worse, not better.** Reconciling with the
established convention: that rule exists specifically to fix a REAL-vs-
SYNTHETIC amplitude-scale mismatch (the RF trained on synthetic peak~1.0
collapses on unnormalized real traces at peak~0.02) — a problem that doesn't
exist here, since this is a synthetic-only regression with no real-data
transfer involved. Two candidate mechanisms for the regression:
1. Time-gate direct-wave removal (tuned via `air_gap_m`/`center_freq_hz` to
   estimate a gate) may be over-aggressive on this setup's short 12ns window,
   cutting into genuinely informative near-direct-wave signal, not just the
   direct pulse itself.
2. Peak-normalization discards absolute amplitude — but `peak_max`/
   `coda_peak_max` showed up among the raw-signal RF's more informative
   features, so removing that channel plausibly removes real signal for
   this specific target (rock count), even though it's the right call for
   real/synthetic domain-transfer tasks.

**Practical takeaway: "always preprocess_signal before extract_features" is
not a universal rule — it's specifically for closing the real/synthetic
amplitude gap.** For a synthetic-only feasibility check like this one, raw
signal was the better choice. Don't apply the real-data preprocessing
convention automatically without checking whether the *reason* for it (real
vs synthetic scale parity) actually applies to the task at hand.

## Files (preprocessing follow-up)
- `train_rf_preprocessed.py` — same pipeline with `preprocess_signal()` applied first
- `rf_feature_importances_preprocessed.csv`, `rf_results_preprocessed.txt`

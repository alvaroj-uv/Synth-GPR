# Historical baseline (pre-refactor) — reconstruction in progress

A previous iteration of this project reported a fouling-classification baseline
that is **not currently reproducible from code in this repository**: there is no
Random-Forest / XGBoost *training* pipeline in `src/` (only inference of a
pre-trained Rojas-Vivanco XGBoost via `src/vivanco_pipeline.py`). The number is
recorded here, with context, so it is not quoted in the README as if the code
behind it existed.

## The reported number
- **Balanced accuracy: 70.83%**
- Dataset: ~30k–50k synthetic samples (the two figures were quoted
  inconsistently across the old README).
- Model: Random Forest.
- Features: 572 waveform-only features (time-domain, Hilbert, frequency, STFT,
  grid), no metadata.

## Why it is not a live README claim
- No training script (`.fit` on RF/XGBoost for this task) exists in the repo.
- The sim→real gap work since then (`docs/REAL_SIM_GAP_ANALYSIS.md`, memory
  `project_sim2real_result`) showed a synthetic-trained waveform RF collapses to
  the majority class on real Site-1 traces — so the 70.83% *synthetic-only*
  figure does not transfer to field data and must not be advertised as project
  performance.

## Path back to a live baseline
The current repo rebuilds the pieces needed to re-establish (and honestly report)
a baseline:
- `scripts/pipeline/assemble_dataset.py` — unified features+metadata table with
  anti-circularity enforced.
- `src/sim_real_comparison.py` — canonical sim↔real metrics.
- a `hypothesis_harness.py` (to be provided) that consumes the assembled table.

When a training + evaluation pipeline lands and is verified end-to-end, its
number goes back into the README **with a link to the code that produces it**.

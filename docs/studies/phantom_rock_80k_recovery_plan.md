# 80k Dataset Phantom-Rock Recovery Plan

**Date:** 2026-06-02
**Status:** Bug CONFIRMED in the 80k dataset. Fix is in for future generation.
Recovery of the existing dataset is the open decision.

## Finding (verified, not assumed)

The 80k dataset — the one behind the **0.7083 balanced-accuracy baseline** — was
simulated with **phantom rocks**. Every ballast aggregate was silently dropped
from the FDTD grid.

- Rocks are angular `#triangle` with **thickness = 0.004 m**.
- Domain is 2-D, one z-cell thick: **dz = 0.0132 m**.
- thickness (0.004) < dz (0.0132) → the rock extrudes <1 cell in z, rounds to
  **zero z-cells**, never reaches the field-evaluation plane (z = dz/2 = 0.0066),
  and gprMax drops it.

**Proof:** took `s_30000.in` (1194 angular rocks), ran it with ballast εr = 5
and again with εr = 20 (a massive change). Traces were **byte-identical**
(max abs diff = 0.0). If the rocks existed, a 4× permittivity change would
drastically alter the coda. They don't. The traces contain only the layered
structure (subgrade / formation / fouling box) — no ballast skeleton.

(The gprMax dispersion warning that mentions `bal_rock` is computed from the
material *declaration*, not placement — it is NOT evidence the rocks exist.)

Same root cause as the cylinder phantom bug ([[feedback_rock_z_phantom]] in
memory) and the same family as the tx/rx-z bug: a z-extent smaller than dz is
silently dropped.

## What this means

- The waveform-only classifier (0.7083) learned from **rock-free** traces:
  layer reflections + the homogeneous fouling box only.
- Any prior conclusion that leaned on "ballast scattering" in the 80k features
  is suspect. The features are real, but the physics generating them was
  incomplete.
- The recent z-fixed hetero-fouling re-run showed rocks raise the coda-vs-FI
  slope ~5× (0.18 → 0.85) — so adding the real rocks materially changes the
  traces. The 80k corrected dataset will look meaningfully different.

## The fix (already done, for FUTURE generation)

`config.py __post_init__` now forces `rock_z_start=0, rock_z_end=domain_z`
whenever `(rock_z_end - rock_z_start) < dz`. Verified it propagates to BOTH
`#cylinder` and `#triangle` (angular) rocks: regenerated scenes now emit
thickness = 0.0132 (= dz). New generation is correct.

## Recovery plan — STAGED (do not burn days of FDTD on faith)

Re-running 80k FDTD A-scans is the expensive step (the reason the dataset exists
at all). Validate on a subset BEFORE committing to the full re-run.

### Stage 0 — Scope check (cheap, ~minutes)
- Confirm ALL 80k use thickness 0.004 (sampled 6, all did). Grep the full set
  for any `#triangle ... <thickness>` or `#cylinder` z2 ≥ dz to be sure there
  isn't a mixed-vintage subset already correct.
- Decide class balance / sample IDs for the validation subset.

### Stage 1 — Validation subset (~500–1000 samples, hours of GPU)
Pick a stratified subset across fouling classes + FI range.
1. **Regenerate** their `.in` with the fix — reuse the SAME geometry seeds so the
   only change is rock z-extent (rocks now present). `scripts/main/generate_in_files.py`.
   Better: load the existing packings via the rock library / `rock_source_file`
   so geometry is identical and only the z-extent differs — a clean A/B.
2. **Re-run** through gprMax. `scripts/main/run_simulations.py`.
3. **Re-extract** features. `scripts/main/extract_features.py`.
4. **Compare** phantom vs rock-present on the SAME samples:
   - How different are the traces / features? (quantify)
   - Re-train the waveform-only RF on the corrected subset
     (`train_rf_waveform_only.py`) — does balanced accuracy move vs 0.7083?
   - Do the corrected features separate classes better/worse?

### Stage 2 — Decision gate
- If corrected traces ≈ phantom traces in the features that matter → the bug,
  while real, barely affects the classifier; full re-run may not be worth it.
- If corrected traces differ materially AND change accuracy/separability →
  the 80k baseline is invalid; commit to the full re-run.

### Stage 3 — Full recovery (only if Stage 2 says so; days of GPU)
1. Regenerate all 80k `.in` with the fix (fast).
2. Re-run all 80k through gprMax (expensive — batch/queue).
3. Re-extract features → rebuild parquet (`build_parquet.py`).
4. Re-train + re-baseline. Update the 0.7083 number with an honest footnote that
   the original was rock-free.

## Honest notes
- Do NOT delete or overwrite the existing 80k `.out`/parquet until the corrected
  version is validated — keep the phantom set for the A/B comparison and as a
  record of what the 0.7083 baseline actually trained on.
- The bug fix changes physics for all future runs; any dataset mixing pre-fix and
  post-fix samples is inconsistent and must not be combined.

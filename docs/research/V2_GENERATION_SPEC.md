# V2 Generation Spec — 400 MHz Waveform-Only Dataset

**Date:** 2026-06-11
**Status:** DRAFT — validation subset not yet run
**Supersedes:** the 80k v1 generation (phantom rocks; see
[phantom-rock recovery plan](../studies/phantom_rock_80k_recovery_plan.md))

One spec, one regeneration. Every known defect and literature finding is folded
in here so the dataset is regenerated **once**. Do not start the full run until
the Stage-1 validation subset (below) has been evaluated.

---

## 1. Spec

| # | Parameter | v1 (80k) | **v2** | Why |
|---|-----------|----------|--------|-----|
| 1 | Rock z-extent | 0.004 m < dz → **rocks silently dropped** | `rock_z = [0, domain_z]` (fix in `config.py __post_init__`, verified for #triangle and #cylinder) | Phantom-rock bug: v1 traces contain no ballast skeleton (proof: ε 5→20 produced byte-identical traces) |
| 2 | domain_x @ 400 MHz | 1.0 m | **2.25 m** (≥ 1.5·λmax = 2.248 m) | Khosravi Largani et al. 2025 guideline; A/B/C experiment (2026-06-11, `scripts/experiments/domain_width_ab.py`) showed 21 features with \|d\| ≥ 0.8 concentrated in the late-coda Hilbert block — driven mostly by lateral scattering content. Narrow scenes under-represent the laterally continuous real track. |
| 3 | Antenna height | 0.25 m (n-layer: `clearance × 0.5`) | **0.50 m** above ballast surface | Matches field hardware (Mbubia 0.3 m, Shapovalov horns ~0.5 m). DELIBERATE deviation from the λmax/2 = 0.75 m far-field guideline: sim-to-real transfer beats a dipole-study rule. The `[GUIDELINE]` warning will still print — that is expected and accepted. |
| 4 | Direct-wave handling | None — features computed on raw trace incl. direct wave | **No-soil reference subtraction**: one air-only reference sim per (freq, domain, antenna) configuration; subtract from every trace before feature extraction | Khosravi Largani et al. 2025 method; removes the constant early-time component the classifier currently has to learn to ignore. One extra sim per config, not per scene. |
| 5 | dx | λmin/10 rule (already correct) | unchanged | Verified compliant in both generation paths |
| 6 | Peplinski materials | unchecked | Only within 300–1300 MHz band (validator now warns) | Peplinski et al. 1995 validity range; fine at 400 MHz, extrapolated at 1.5 GHz |
| 7 | Seeds / provenance | mixed | fresh seed series, `v2` tag in `## meta` header | Never mix pre-fix and post-fix samples (recovery-plan rule) |

Cost: item 2 ≈ 2.2× sim time per scene (seconds-scale 2D sims). Items 1, 3, 7
are free. Item 4 adds one sim per configuration.

## 2. Open decisions (resolve before Stage 1)

- **Ballast rock ε**: Li 2025 uses 4, Li 2023 measured 6 (Clark 2001 range
  3–26.9). Current code uses the value in `constants.py`. Decide and document
  in the materials doc (Tier-2 audit item — can ride along with v2).
- **Class balance / FI coverage** of the validation subset: stratify across
  CL/MC/MF/F/HF and the FI range, same as v1 so accuracies are comparable.

## 3. Staged plan (from the recovery plan, updated for v2)

1. **Stage 1 — validation subset (~500–1000 samples, hours).**
   Generate under this spec, run gprMax, extract features (with reference
   subtraction), retrain the waveform-only RF
   (`train_rf_waveform_only.py`), compare balanced accuracy and feature
   importances against the 0.7083 v1 baseline.
2. **Stage 2 — decision gate.** If separability/accuracy move materially →
   commit to the full 80k v2 run. If not → document that the defects, while
   real, do not affect the classifier, and continue on v1 with an honest
   footnote.
3. **Stage 3 — full run** (only if Stage 2 says so). Keep the v1 80k
   `.out`/parquet intact as the A/B record — do not delete or overwrite.

## 4. What v2 deliberately does NOT change

- 2D TMz simulation (3D is a separate research direction)
- Packing algorithm (Shang-Chu / hybrid — separate, already-decided track)
- Feature definitions (572-vector unchanged except the reference subtraction
  upstream, so v1/v2 feature comparisons stay meaningful)
- The waveform-only constraint: metadata stays out of the model

## 5. Cross-references

- [phantom_rock_80k_recovery_plan.md](../studies/phantom_rock_80k_recovery_plan.md) — bug proof + staged recovery logic
- [FDTD Medium Dimension Selection.md](../studies/FDTD%20Medium%20Dimension%20Selection.md) — Khosravi Largani 2025 guidelines
- [REF_Shapovalov2026_ideas.md](../studies/REF_Shapovalov2026_ideas.md) — field antenna height, indicator baselines
- [Li.md](../studies/Li.md) / [li_2.md](../studies/li_2.md) — ballast ε reconciliation (open)
- `scripts/experiments/domain_width_ab.py` + `test_output/domain_width_ab/summary.txt` — domain-width A/B/C evidence
- `src/physics.py::check_fdtd_guidelines` — the guideline warnings referenced above

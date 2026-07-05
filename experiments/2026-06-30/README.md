# 2026-06-30 — Dimension-agnostic packing: 2-D + 3-D create & test

**Goal:** Verify the unified `RCPGeneratorPacking` (algo `rcpgen`, real KD-physics
RCPGenerator C++ engine) produces valid gprMax geometry in **both** 2-D and 3-D
from the *same* `pack(bounds)` call — the bounds' `ndim` is the only thing that
changes.

## What was run
`test_2d_3d_packing.py` — packs, writes decks, renders, and runs
`gprMax --geometry-only` on each (the real validation: gprMax must rasterize
every primitive into a grid).

| Scene | Bounds | Result | Deck |
|-------|--------|--------|------|
| 2-D | `PackingBounds(0,0.5, 0.25,0.55)` → ndim 2 | 60 disks → `#cylinder` | `packing2d.in` |
| 3-D | `PackingBounds(0,0.3, 0,0.3, 0,0.3)` → ndim 3 | 131 spheres → `#sphere` | `packing3d.in` |

Both: ballast rocks = granite (ε=6.1), subgrade box (ε=8) below, 420 MHz Ricker
Hertzian dipole, `#geometry_view`.

## Result — both build ✅
- `packing2d.vti` (202 KB), `packing3d.vti` (4.2 MB) written by gprMax.
- Renders: `packing2d.png` (disks in ballast layer + subgrade), `packing3d.png`
  (3-D sphere scatter in the 0.15–0.45 m layer).

## Gotcha fixed
First run used `#time_window: 1e-9`, **shorter than the 420 MHz pulse**. gprMax's
dispersion check FFTs a *truncated* pulse → overestimates max frequency →
"Non-physical wave propagation … wavelength sampled by N cells" (surfaced as a
broken `'bool' has no attribute 'ID'` error formatter). Fix: realistic
`#time_window: 1.2e-8`. Time-window only feeds the dispersion analysis here;
`--geometry-only` skips time-stepping, so runtime is unaffected.

## Files
- `test_2d_3d_packing.py` — generator/test
- `packing2d.in` / `.vti` / `.png`
- `packing3d.in` / `.vti` / `.png`

---

## Run 2 — Two-layer rock packing with per-layer overrides

**Goal:** Demo + smoke-test the per-layer packing overrides added to
`src/layer_spec.py` / `src/layer_scene_builder.py` this session
(`rock_radius_min/max`, `rock_packing_algorithm`, `rock_packing_target_fill`,
`pymunk_settle_time` — each independently overridable per `[[layer]]`, falling
back to the `[sim]` scene default).

**Layer stack** (top → bottom): `fouled_rocks` (15 cm, eps=6.0 rock in
`fouling` matrix, radius 10–18 mm, scene-default `pymunk_ballast` packer) over
`clean_rocks` (20 cm, eps=6.0 rock in `free_space` matrix, radius 15–25 mm,
**per-layer override** to the `circlify` packer). 420 MHz Gaussian bistatic
30 mm, domain 0.5 × 0.55 m, dx=3mm, `#geometry_view` (type `n`) for `.vti`.

**Result:** generated via `scripts/pipeline/generate_gprmax_scenes.py` →
ran `python -m gprMax two_layer_rocks.in` in the `gprMax` conda env →
completed in 8.7s (749 geometry cmds, 7068 time steps). Confirmed in the
build log that `clean_rocks` correctly picked up its `circlify` override
(`[PACKER] layer 'clean_rocks' override (algo=circlify) -> CirclifyPacking`)
while `fouled_rocks` used the scene-default packer — per-layer overrides work
end-to-end through to a real gprMax run.

## Files (Run 2)
- `two_layer_rocks.toml` — TOML config
- `two_layer_rocks.in` — generated gprMax input deck
- `two_layer_rocks.out` — FDTD A-scan output (HDF5)
- `two_layer_rocks.vti` — geometry view for ParaView
- `two_layer_rocks.png` — quick-look render

---

## Run 3 — Three-layer trackbed: ballast(air) / subballast / subgrade

**Goal:** Standard 3-layer trackbed geometry using the project's validated SSOT
thicknesses (`src/constants.py` `PhysicalConstants`/`MaterialConstants`, same
values `src/config.py` `GeneratorConfig` uses for real dataset generation):
ballast 0.45 m (Selig & Waters 1994), subballast/`formation` 0.10 m (Selig &
Waters 1994), subgrade 0.20 m (PMC9003199). Note: `constants.py` also carries
an unused legacy `SUBGRADE_THICKNESS=0.50` not wired into the real generator —
used 0.20 m since that's what the validated dataset pipeline actually uses.

**Layer stack** (top → bottom): `ballast` (45 cm, packed rocks eps=4.0
granite/limestone — Tosti & Benedetto 2018 — voids = `free_space`/air, i.e.
clean dry ballast) → `formation` (10 cm flat, eps=10.0) → `subgrade` (20 cm
flat, eps=8.0 dry). 420 MHz Gaussian bistatic 30mm, domain 0.5 × 0.95 m,
dx=3mm, `time_window` auto-derived (28.3 ns), `#geometry_view` (type `n`).

**Result:** generated + ran `python -m gprMax three_layer_trackbed.in`
(gprMax conda env) — completed in 5.1s (1612 geometry cmds, 4003 time steps).

## Files (Run 3)
- `three_layer_trackbed.toml` — TOML config
- `three_layer_trackbed.in` — generated gprMax input deck
- `three_layer_trackbed.out` — FDTD A-scan output (HDF5)
- `three_layer_trackbed.vti` — geometry view for ParaView
- `three_layer_trackbed.png` — quick-look render

---

## Run 4 — Frequency sweep 100–2000 MHz: when do the 3 interfaces resolve?

Follow-up to Run 3 (which showed the formation/subgrade interface merges into
the ballast/formation reflection at 420 MHz). Swept the same geometry from
100 to 2000 MHz in 100 MHz steps (20 gprMax runs). **Result: both interfaces
become time-resolvable from ~1000–1200 MHz upward**, but the formation/
subgrade reflection is intrinsically weak (R≈0.056 vs R≈0.225) and needs
local/gain renormalization to see — a global-amplitude threshold misses it at
every frequency. See `freq_sweep/README.md` for full details and the gotcha.

## Files (Run 4)
- `freq_sweep/` — 20 × `{.toml,.in,.out}`, sweep driver, analysis script,
  comparison plot, full writeup

---

## Run 5 — 500 MHz, matrix eps=3, dz=2mm, 12ns window (amplitude/wavelet prep)

Parameter revision proposed in this session for future amplitude-based
inversion work (Xue 2021 ray-amplitude method — NOT implemented here, this
only prepares the forward-model trace):

| Parameter | Was (freq_sweep 100MHz) | Now | Reason |
|---|---|---|---|
| Frequency | 100 MHz | 500 MHz | Better interface resolution (lambda ~0.6m -> 0.12m in eps=4) |
| Matrix eps | 1 (pure free_space) | 3, sigma=1e-5 S/m | Voids carry residual moisture/fines even in "clean" ballast, not pure air. sigma sourced from Mbubia et al. 2024 (IOP J. Phys. Conf. Ser. 2887:012047) Table 1: "Clean" ballast state = eps[2.5-3.5]/sigma 1e-5 S/m — our eps=3 falls in that bucket. (Originally guessed sigma=0.002 unsourced; corrected same day.) |
| Domain dx/dz | 5mm (rock-packing cap) | 2mm | Explicit, finer than the auto-derived/capped value |
| Time window | 28.3 ns (auto-derived) | 12 ns | Explicit; focuses on near-surface ballast response |
| Objective | Geometry-only resolution test | Full FDTD amplitude + wavelet | Not `--geometry-only`; keeps the source wavelet for later amplitude-inversion work |

Same 3-layer geometry (ballast 0.45m/formation 0.10m/subgrade 0.20m) as Run
3/4. Ran in 4.5s. A-scan shows the direct pulse (~1.5-3ns) and a coda bump
around ~8ns (now visible since 8ns < 12ns window, unlike the Vivanco-pipeline
7ns-window finding in Run 4).

### Quantitative effect of the sigma=0.002 -> 1e-5 correction

Re-ran the sigma=0.002 (unsourced-guess) version to a scratch file and
diffed it sample-by-sample against the corrected sigma=1e-5 run (same
geometry/seed, matrix_sigma is the only thing that changed):

| Metric | Result |
|---|---|
| Peak amplitude | 766.01 -> 766.89 (+0.1%, ~unchanged) |
| Max abs difference (whole trace) | 4.05 (0.53% of peak) |
| Correlation, full trace | 0.99998 |
| **Coda energy (5-12ns, post direct wave)** | **428,671 -> 479,567 (+11.9%)** |
| Correlation, coda only | 0.9997 (shape preserved, magnitude shifts) |

**Interpretation:** dropping sigma 200x reduces ohmic loss in the matrix,
so ~12% more energy survives into the coda — consistent with less
attenuation. The effect on overall waveform SHAPE is small (both cases
already sat in a low-loss regime: loss tangent ~2.4% at sigma=0.002 vs
~0.01% at sigma=1e-5, and the matrix is only ~11.5% of the ballast layer's
area per LabWorker porosity), but the coda ENERGY difference (+11.9%) is
non-trivial for any amplitude-based analysis (e.g. Xue 2021), where
attenuation itself is the signal being measured — so getting sigma right
matters more for that use case than for waveform-shape/timing work.

## Files (Run 5)
- `three_layer_500mhz_eps3.toml` — TOML config (assumptions documented in the file header)
- `three_layer_500mhz_eps3.in` — generated gprMax input deck
- `three_layer_500mhz_eps3.out` — FDTD A-scan output (HDF5)
- `three_layer_500mhz_eps3.vti` — geometry view for ParaView
- `three_layer_500mhz_eps3.png` / `three_layer_500mhz_eps3_viz.png` — renders

### Side effect: the matrix eps=1->3 "fix" nearly killed the rocks' contribution

Raising matrix eps from 1 (pure air) to 3 (moist/fines voids) also SHRANK the
rock/matrix dielectric contrast that makes discrete rocks scatter at all —
R = (sqrt(rock_eps)-sqrt(matrix_eps))/(sqrt(rock_eps)+sqrt(matrix_eps)) drops
from 0.333 (matrix=1) to 0.072 (matrix=3), a **21.6x drop in power
reflectivity (R^2)**. Verified by comparing each packed-rock run against a
flat, CRIM area-weighted homogeneous ballast box (same effective eps/sigma,
no discrete rocks — `three_layer_500mhz_eps3_flat_check.toml` /
`three_layer_500mhz_matrix1_*_check.toml`):

| | OLD contrast (rock=4, matrix=1) | NEW contrast (rock=4, matrix=3) |
|---|---|---|
| R (rock/matrix reflection coeff.) | 0.333 | 0.072 |
| Coda correlation, rocks vs flat-equivalent | **0.097** (rocks fully dominate the coda shape) | **0.837** (rocks barely perturb it) |
| Coda energy ratio (rocks/flat) | 1.68x (+68%) | 1.27x (+27%) |

**Conclusion:** with the OLD matrix=1, discrete rock geometry was doing
essentially ALL the coda-shaping work (a flat layer looked nothing like it,
corr=0.097). With the physically-more-realistic matrix=3, a flat homogeneous
layer now reproduces the coda almost as well as the packed-rock model
(corr=0.837) — the rocks still add ~27% coda energy but no longer define a
distinctive scattering signature. This is a real tension: making the matrix
material more physically accurate (moisture/fines instead of pure air)
undercuts the entire reason to model discrete rocks in the first place. If
rock-scattering signatures matter for this line of work, either the rock eps
needs to go up (more mineral contrast) or this matrix correction needs
revisiting — using eps=3 uniformly may not be the right call for a matrix
that's meant to sit BETWEEN rocks specifically (vs. Mbubia's bulk/lumped
"Clean" eps, which was never meant to be a void-only value).

## Files (rock-contribution check)
- `three_layer_500mhz_eps3_flat_check.toml/.in/.out` — flat CRIM-equivalent (eps=3.885) counterpart to `three_layer_500mhz_eps3`
- `three_layer_500mhz_matrix1_rocks_check.toml/.in/.out` — packed-rock, matrix=1 (old baseline)
- `three_layer_500mhz_matrix1_flat_check.toml/.in/.out` — flat CRIM-equivalent (eps=3.655) counterpart to the matrix=1 baseline

### Fix: raise rock_eps to 6.1 (Brancadoro solid-mineral value), keep matrix_eps=3

Root cause: `BALLAST_ROCK_PROPS=(4.0, 0.001)` (Tosti & Benedetto 2018) is very
likely already an EFFECTIVE BULK value (rock+air CRIM-mixed), not solid
mineral permittivity — real dry granite/limestone runs higher. The project
already has a solid-mineral citation for exactly this: Brancadoro papers
(`docs/studies/brancadoro*.md`, [[ref_brancadoro]]) give rock aggregate
eps=6.1-6.5 for a 2D discrete-rock model, already used earlier the same day
in `two_layer_rocks.toml`. Raised rock_eps 4.0 -> 6.1 (matrix_eps=3.0
unchanged) and re-ran the packed-rock-vs-flat-equivalent comparison:

| Config | R | Power reflectivity | Coda corr (rocks vs flat) | Coda energy ratio |
|---|---|---|---|---|
| OLD (rock=4, matrix=1) | 0.333 | 11.1% | 0.097 | 1.68x |
| Collapsed (rock=4, matrix=3) | 0.072 | 0.52% | 0.837 | 1.27x |
| **Fixed (rock=6.1, matrix=3)** | **0.176** | **3.1%** | **0.208** | **1.70x** |

Coda correlation drops back to 0.208 (rocks dominate the coda shape again,
close to the old 0.097) and coda energy ratio (+70%) essentially matches the
old baseline (+68%) — discrete-rock scattering is restored while keeping the
physically-justified matrix eps=3 (moisture/fines, not pure air). **Adopt
rock_eps=6.1 (sigma=0.001, unchanged/reused) for any packed-ballast layer
that also uses matrix_eps=3** — `constants.MC.BALLAST_ROCK_PROPS` itself
still says 4.0/bulk-flavored and was NOT changed globally; this fix is
documented here per-TOML until/unless the SSOT default is revisited project-wide.

## Files (contrast-recovery check)
- `three_layer_500mhz_rock6p1_check.toml/.in/.out` — packed-rock, rock=6.1/matrix=3 (the fix)
- `three_layer_500mhz_rock6p1_flat_check.toml/.in/.out` — flat CRIM-equivalent (eps=5.7435) counterpart

### Follow-up: rock_eps=8 (Harajchi) goes even further than 6.1

Tested the other project-cited solid-rock value, Harajchi's stone eps=8
([[ref_harajchi]] / `docs/studies/haraj.md`), same method (packed vs flat
CRIM-equivalent, matrix_eps=3 unchanged):

| Config | R | Power reflectivity | Coda corr (rocks vs flat) | Coda energy ratio |
|---|---|---|---|---|
| OLD (rock=4, matrix=1) | 0.333 | 11.1% | 0.097 | 1.68x |
| Collapsed (rock=4, matrix=3) | 0.072 | 0.52% | 0.837 | 1.27x |
| rock=6.1 (Brancadoro), matrix=3 | 0.176 | 3.1% | 0.208 | 1.70x |
| **rock=8 (Harajchi), matrix=3** | **0.240** | **5.8%** | **0.053** | **2.10x** |

Surprising: rock=8 gives an even LOWER coda correlation (0.053) than the old
matrix=1 baseline (0.097) despite a SMALLER R (0.240 vs 0.333) — normal-
incidence Fresnel R (a single flat-interface estimate) doesn't fully capture
this. Higher absolute rock eps also slows the wave inside each rock (more
phase accumulated crossing it, i.e. rocks become "electrically larger"),
which appears to amplify multi-scattering complexity beyond what the R
contrast alone predicts. **Both rock=6.1 and rock=8 are valid literature
citations for solid ballast aggregate** (Brancadoro vs Harajchi respectively)
— they imply somewhat different lithology/porosity assumptions in their
source papers; this file currently uses 6.1 (see TOML header), 8 is
documented here as a stronger-contrast alternative, not yet adopted.

## Files (rock=8 follow-up)
- `three_layer_500mhz_rock8_check.toml/.in/.out` — packed-rock, rock=8/matrix=3
- `three_layer_500mhz_rock8_flat_check.toml/.in/.out` — flat CRIM-equivalent (eps=7.425) counterpart

### Visualizing the contrast: envelope comparison, packed rocks vs flat-equivalent

`plot_rock_contrast_envelopes.py` renders Hilbert envelopes (packed-rock
solid vs flat-CRIM-equivalent dashed) for all three configs above, side by
side: full trace (direct pulse dominates, both curves nearly overlap — same
reason coda-windowing is mandatory everywhere else in this project) and a
coda-only zoom (5-12ns, own local scale) where the shaded gap between the two
curves IS the rocks' distinctive contribution. Output:
`rock_contrast_envelope_comparison.png`.

Visually confirms the correlation numbers: rock=4/matrix=1 (old) shows one
big bump, phase-shifted between packed and flat (~7.4ns vs ~8.2ns) — low
correlation mostly from timing offset. rock=6.1/matrix=3 (adopted fix) adds
independent early ripples (5.5-8ns) on top of a similarly-shifted main peak.
rock=8/matrix=3 (alternative) is visibly the "noisiest" — several
rock-only oscillations (5.5-8.5ns) that the flat curve doesn't hint at at
all, before a large, also-shifted main peak — consistent with it having the
lowest coda correlation (0.053) of the three.

## Files (envelope visualization)
- `plot_rock_contrast_envelopes.py` — generator script
- `rock_contrast_envelope_comparison.png` — 3-config x 2-panel (full/coda-zoom) comparison

---

## Run 6 — Sanity check: overlay against one real EFE trace

Used the canonical `compare_synthetic_vs_real()` in
`scripts/visualization/unified_visualizer.py` (per
`feedback_unified_visualizer.md` — no ad-hoc script needed, this function
already existed) to overlay `three_layer_500mhz_eps3.out` (the corrected
rock=6.1/matrix=3 run) against the real EFE Puerto-Limache trace nearest
PK=20 km in `D:/Codigo/Data/efe_full.h5` (RAW, not AGC — per
`feedback_agc_breaks_matching.md`). Both direct-wave peak aligned, 12 ns
window (limited by the synthetic trace's short time_window).

**Result:**

| Metric | Value |
|---|---|
| Envelope correlation (Hilbert, -2 to 6ns around the aligned peak) | **0.954** |
| Raw signal correlation | -0.881 (polarity flipped) |
| Raw signal correlation, synthetic sign-flipped | **+0.881** |

Envelope shape matches very well (0.954). Raw-signal polarity is inverted
between synthetic and real (sim dips first/real rises first) — a consistent
sign flip, not noise (0.881 once corrected), which is exactly why the
project's established practice compares Hilbert envelopes rather than raw
signed amplitude for FI/fouling correlation work. This is only ONE real
trace at ONE PK with a short 12ns window — not a validated result, just a
quick single-scan sanity check.

## Files (Run 6)
- `efe_overlay_three_layer_500mhz_eps3.png` — 3-panel comparison (raw, peak-normalized, Hilbert envelope)
- `efe_overlay_three_layer_500mhz_eps3_flipped.png` — same, with `flip_synthetic=True`

### Added `flip_synthetic` param to `compare_synthetic_vs_real()`

The function had no way to apply the known sim/real polarity flip (see
`project_validated_420mhz_pipeline` memory) — panel 1 always plotted the
synthetic raw sign as-is. Added `flip_synthetic: bool = False` kwarg
(multiplies `syn_sig` by -1 right after loading; legend labels append
"flipped" when active) directly to
`scripts/visualization/unified_visualizer.py` per this project's convention
of extending the canonical visualizer rather than writing ad-hoc scripts.
With `flip_synthetic=True`, panels 1 and 2 now track each other closely
through the direct-wave pulse and first trough (both peak together at t=0,
both dip together ~t=1-1.2ns) — visually confirms the +0.881 flipped raw
correlation computed earlier.

### Follow-up: same geometry at 420 MHz (project's established reference frequency)

Same corrected rock/matrix eps (rock=6.1, matrix=3/sigma=1e-5), only
`freq_hz` changed 500e6 -> 420e6 (`three_layer_420mhz_eps3.toml`). 420 MHz is
the frequency the rest of the project already validates against (`DEFAULT.toml`:
"88.76% correlation with real data" at 420 MHz Gaussian bistatic 30mm).

| Metric | 500 MHz (Run 6) | 420 MHz |
|---|---|---|
| Envelope correlation | 0.954 | **0.979** |
| Raw signal correlation (flipped) | 0.881 | **0.946** |

Both metrics improve at 420 MHz — consistent with, and an independent
reconfirmation of, the project's existing 420 MHz preference, now also shown
to hold for this 3-layer packed-rock (rock=6.1/matrix=3) geometry, not just
the original single-homogeneous-layer validated pipeline. Still a single
trace/single PK sanity check, not a validated result.

## Files (420 MHz follow-up)
- `three_layer_420mhz_eps3.toml/.in/.out/.vti/.png` — same geometry as Run 5/6 at 420 MHz
- `efe_overlay_three_layer_420mhz_eps3_flipped.png` — 3-panel comparison vs EFE PK=20km

### Follow-up: rock_eps=10 — internal contrast keeps climbing, real-data match doesn't

Continued the rock_eps sweep (4 -> 6.1 -> 8 -> 10), matrix_eps=3 unchanged
each time. Same packed-vs-flat-CRIM-equivalent method as before, at 500MHz:

| Config | R | Power reflectivity | Coda corr (rocks vs flat) | Coda energy ratio |
|---|---|---|---|---|
| OLD (rock=4, matrix=1) | 0.333 | 11.1% | 0.097 | 1.68x |
| Collapsed (rock=4, matrix=3) | 0.072 | 0.52% | 0.837 | 1.27x |
| rock=6.1 (Brancadoro), matrix=3 | 0.176 | 3.1% | 0.208 | 1.70x |
| rock=8 (Harajchi), matrix=3 | 0.240 | 5.8% | 0.053 | 2.10x |
| **rock=10, matrix=3** | **0.292** | **8.5%** | **0.111** | **2.72x** |

Non-monotonic: rock=8 still has the LOWEST coda correlation (most
distinctive) of the four, not rock=10 — coda energy ratio, though, keeps
climbing monotonically (2.72x at rock=10).

**The decisive test — does more rock eps help against REAL data?** Re-ran the
420 MHz EFE-overlay comparison (`three_layer_420mhz_rock10.toml`, same PK=20km
trace) with rock_eps=10 instead of 6.1:

| Metric | rock=6.1 (420MHz) | rock=10 (420MHz) |
|---|---|---|
| Envelope correlation | 0.979 | 0.980 (tied, +0.001) |
| Raw signal correlation (flipped) | **0.946** | 0.937 (worse) |

**No — raising rock_eps further does NOT improve, and slightly worsens, the
match to real data**, despite higher internal rock/matrix contrast and coda
energy. rock_eps=6.1 (Brancadoro) is not just "good enough" but appears to
already be at or past the useful range for this purpose — internal
scattering-contrast metrics (coda correlation vs flat-equivalent, coda
energy) do NOT track real-data fit once rock_eps is high enough, so
optimizing them further is not a useful proxy. **Recommendation: keep
rock_eps=6.1, don't push higher.**

## Files (rock=10 follow-up)
- `three_layer_500mhz_rock10_check.toml/.in/.out` — packed-rock, rock=10/matrix=3
- `three_layer_500mhz_rock10_flat_check.toml/.in/.out` — flat CRIM-equivalent (eps=9.195) counterpart
- `three_layer_420mhz_rock10.toml/.in/.out` — rock=10 at 420MHz, EFE overlay check (no separate overlay PNG generated, correlation computed directly)

---

## Run 7 — New feature: `rock_invisible_fraction` (partial rock invisibility)

Requested: "make SOME rocks invisible" (not all — that degenerates to the
flat/no-rocks case already covered by the CRIM-equivalent comparisons above,
and `layer_spec.py` blocks rock_eps==matrix_eps outright as a builder
safeguard). Added a genuinely new per-layer TOML parameter:

**`rock_invisible_fraction`** (packed layers only, 0-1): each packed rock
independently has this probability of being stamped with the MATRIX material
instead of the rock material when emitted as `#triangle`/`#cylinder`
commands — geometrically present (still counted by LabWorker's
porosity/virtual-sieve analysis) but EM-inert (zero dielectric contrast).
Deterministic per `[sim].seed`.

**Implementation:**
- `src/layer_spec.py` — new `Layer.rock_invisible_fraction` field, TOML
  parsing + validation (packed-only, range [0,1]) in `_layer_from_table_obj`.
- `src/layer_scene_builder.py` — `_pack_layer_rocks()` gained `matrix_id` and
  `invisible_fraction` params; per-rock coin-flip via a seeded
  `np.random.default_rng` (separate RNG stream from the packer's own) decides
  `rock_id` vs `matrix_id` per triangle/cylinder. Logs
  `[PACKER] layer 'X' rock_invisible_fraction=Y -> N/M rocks stamped with matrix material`.
  Added the missing `import numpy as np` this module needed.

**Test:** `three_layer_420mhz_rock6p1_inv30.toml` — same best-so-far config
(rock=6.1, matrix=3, 420MHz) with `rock_invisible_fraction=0.3` (measured:
53/180 rocks, ~29%, stamped invisible — matches the requested fraction).

| Config | Envelope correlation | Raw correlation (flipped) |
|---|---|---|
| 100% rocks visible (rock=6.1 baseline) | 0.979 | 0.946 |
| **30% rocks invisible** | 0.9789 | 0.9470 |

Essentially no change (within single-trace noise) — a sparser effective
scatterer population doesn't measurably help or hurt the real-data fit
either. Consistent with the rock_eps=8/10 finding: once contrast is in a
reasonable range, further internal-population tweaks don't move the
real-data correlation.

## Files (Run 7)
- `three_layer_420mhz_rock6p1_inv30.toml/.in/.out` — 30% invisible-rock test

### Full sweep: 0% -> 100% invisible, re-evaluated against real EFE each step

`rock_invisible_sweep/run_invisible_sweep.py` swept `rock_invisible_fraction`
0.0 -> 1.0 in steps of 0.1 (11 runs, ~7.5-8.5s each), rock=6.1/matrix=3/420MHz
fixed, re-computing both correlation metrics against the same EFE PK=20km
trace at every step (`invisible_fraction_sweep_correlation.png`):

| frac | envelope corr | raw corr (flipped) |
|---|---|---|
| 0.0 | 0.9785 | 0.9458 |
| 0.1 | 0.9769 | 0.9443 |
| 0.2 | 0.9795 | 0.9482 |
| 0.3 | 0.9789 | 0.9470 |
| 0.4 | 0.9791 | 0.9468 |
| 0.5 | 0.9794 | 0.9479 |
| **0.6** | **0.9805** | 0.9526 |
| 0.7 | 0.9795 | 0.9513 |
| 0.8 | 0.9771 | 0.9517 |
| 0.9 | 0.9770 | **0.9536** |
| 1.0 | 0.9750 | 0.9513 |

**Envelope correlation is flat** across the whole range (0.975-0.981, no real
trend, peaks mildly at 0.6). **Raw-signal correlation trends upward** with
more invisible rocks — 0.946 at 0% rising to ~0.95-0.954 in the 0.6-0.9
range, a modest but consistent ~0.007-0.009 absolute improvement over the
fully-visible baseline, then flattens/dips slightly by 1.0 (fully flat,
zero-contrast layer). Best single point: 60-90% invisible, not 0% or 100%.

**Interpretation:** this is a small effect (within the same order as
single-trace noise seen elsewhere this session), but its direction is
informative — a somewhat SPARSER effective scatterer population matches the
real trace's raw waveform slightly better than either the fully-scattering
(0%) or fully-smooth (100%, no contrast) extremes. Possible explanation: our
rock=6.1 packed geometry's sharp multi-scattering wiggles are slightly more
jagged than the real coda's actual decay; thinning the rock population
smooths the synthetic response back toward the real trace without fully
flattening the physical rock geometry. Not large enough to justify adopting
a specific non-zero invisible_fraction as a new default — flagged here for
awareness, not as a recommendation.

## Files (invisible-fraction sweep)
- `rock_invisible_sweep/run_invisible_sweep.py` — sweep driver + correlation re-evaluation
- `rock_invisible_sweep/three_layer_420mhz_invNNN.{toml,in,out}` × 11 (0-100%)
- `rock_invisible_sweep/invisible_fraction_sweep_correlation.png` — correlation vs fraction plot
- `rock_invisible_sweep/sweep_log.txt` — run log

---

## Run 8 — New feature: `rock_shape` (circle vs polygon), tested against real EFE

Asked "what if rocks are cylinders [circles]?" All packed rocks in this
project have been angular triangulated polygons by default (the
`pymunk_ballast` packer's `generate_rocks()` always calls `self.polygonize()`
on its raw circle output). Added a way to keep them round instead.

**New per-layer TOML param `rock_shape`** ("polygon" default / "circle"):
- `src/layer_spec.py` — new `Layer.rock_shape` field + validation (packed-only,
  must be "polygon" or "circle").
- `src/layer_scene_builder.py` — `_pack_layer_rocks()` gained a `rock_shape`
  param; when `"circle"`, strips each packed `Rock`'s `.vertices` (set to
  `None`) right after packing, before geometry emission — `Rock.is_polygon`
  then reads False and the rock emits as a single `#cylinder` instead of N
  `#triangle` facets (same centre/radius either way, since polygonize()
  builds facets around the original circle). Logs
  `[PACKER] layer 'X' rock_shape=circle -> N rocks emitted as cylinders`.

**Test:** `three_layer_420mhz_circle_rocks.toml` — same best-so-far config
(rock=6.1, matrix=3, 420MHz) with `rock_shape="circle"` (confirmed: 163
`#cylinder`, 0 `#triangle` in the generated `.in`).

| Rock shape | Envelope correlation | Raw correlation (flipped) |
|---|---|---|
| Polygon (default, angular) | 0.9785 | 0.9458 |
| **Circle (cylinder)** | 0.9796 | 0.9464 |

Essentially tied (+0.001 / +0.0006) — rock cross-section shape doesn't
meaningfully affect the real-data fit at this frequency/resolution, unlike
rock_eps (which mattered a lot) or rock_invisible_fraction (small but real
effect). Geometric angularity is a second-order detail here; dielectric
contrast and effective scatterer density dominate.

## Files (Run 8)
- `three_layer_420mhz_circle_rocks.toml/.in/.out/.vti/.png` — circle-rocks test

### Follow-up: rock_shape="rip" (Li et al. 2023 Random Irregular Polygon, decoupled from RIPPacking)

Extended `rock_shape` with a 4th option, `"rip"`, implementing Li et al. 2023's
Random Irregular Polygon (8-12 vertices, +-25% radial roughness — see
`docs/studies/li_2.md`, this session's other paper-check). Extracted the
shape-generation logic (previously private to `rip_packing.RIPPacking._rip_polygon`)
into a standalone `rock_model.rip_polygon_vertices(cx, cy, r_mean, rng, ...)`
helper — `RIPPacking` now calls it too (refactored, no behavior change,
verified 20 rocks / 11-vertex polygon still produced standalone). This means
**any packer** (pymunk_ballast, circlify, rcpgen, ...) can now produce
Li-2023-style jagged polygon rocks via `rock_shape="rip"`, not just
`RIPPacking`'s own RSA placement — same pattern as `"circle"`/`"square"`.
Smoke-tested with `circlify` + `rock_shape="rip"`: 209 triangle facets, 0
cylinders, confirms the decoupling works. Not yet benchmarked against real
EFE data (unlike circle/square above).

### Follow-up: rock_shape="square"

Extended `rock_shape` to also accept `"square"` — replaces each packed rock's
vertices with a 4-corner square inscribed in the packer's original bounding
circle (same centre/radius as the polygon/circle variants). Same
implementation pattern in `layer_scene_builder.py` (`_pack_layer_rocks`) and
validation in `layer_spec.py`.

| Rock shape | Envelope correlation | Raw correlation (flipped) |
|---|---|---|
| Polygon (default, angular) | 0.9785 | 0.9458 |
| Circle (cylinder) | 0.9796 | 0.9464 |
| **Square** | 0.9787 | **0.9484** |

Square gives the best raw-signal correlation of the three (+0.0026 over
polygon), though still a small effect — envelope correlation stays
essentially tied across all three shapes (0.9785-0.9796). Consistent with
Run 8's conclusion: shape is a second-order effect next to rock_eps, though
this is a hint that sharper/flatter facets (square corners) might interact
with the real coda's reflection timing slightly differently than round or
irregular-angular shapes. Not enough signal to change the adopted default
(polygon, the packer's natural output) without more replication.

## Files (square-rocks follow-up)
- `three_layer_420mhz_square_rocks.toml/.in/.out/.vti/.png` — square-rocks test
- `rock_shape_comparison.png` — side-by-side geometry render, all three shapes (same rock positions/sizes, shape only)

### Waveform comparison between the three shapes

`plot_rock_shape_waveforms.py` overlays the three `.out` traces directly
(raw + Hilbert envelope, full trace and coda-only zoom) —
`rock_shape_waveform_comparison.png`.

**The direct-wave pulse (0-4ns) is IDENTICAL across all three shapes** (as
expected — surface/antenna coupling doesn't depend on ballast rock geometry).
The coda (>5ns) diverges: all three share a similar overall envelope (rise to
one big peak around 9-10ns) but with a clear TIME SHIFT — the main coda peak
arrives earliest with square rocks (~9.0ns), next with polygon (~9.3ns), and
latest with circle (~9.6ns), roughly a 0.6ns spread. Pairwise coda
correlation (raw signal, 5-12ns) confirms this ordering:

| Pair | r |
|---|---|
| Polygon vs Circle | 0.780 |
| Polygon vs Square | 0.819 |
| **Circle vs Square** | **0.350** |

Circle-vs-square (the two most different shapes, and the two extremes of the
timing shift) correlate the least; polygon sits geometrically and
temporally between them, correlating moderately with both. Plausible
mechanism: rock cross-section shape changes the effective scattering path
length/multiple-reflection timing within the packed layer (flat square faces
vs. round circles vs. irregular polygon facets each redirect/delay energy
differently), shifting when constructive interference peaks in the coda —
consistent with Run 8/8-square's finding that shape is a real, second-order
effect (small impact on real-data correlation, ~0.6ns of coda timing) next
to the first-order effect of rock_eps (dielectric contrast).

## Files (waveform comparison)
- `plot_rock_shape_waveforms.py` — generator script
- `rock_shape_waveform_comparison.png` — 4-panel (raw/envelope × full/coda-zoom) overlay

---

## Run 9 — Testing the "real signal shifted left" pulse-shape mismatch

The peak-normalised overlay panel (Run 6/420MHz follow-up) showed the real
trace's leading edge arriving earlier (relative to the shared peak) than the
synthetic Gaussian pulse, and its trailing edge decaying slower — i.e. the
real pulse is wider than the idealized Gaussian source, a genuine
pulse-SHAPE mismatch (not a timing offset, since both are peak-aligned by
construction).

**Test:** the project already has a pre-calibrated GSSI hardware excitation
(`calibration/gssi_excitation.txt`, built by `scripts/compute_gssi_excitation.py`
— a Wiener-filter correction `I_cal = I_g × H_correction` that bakes the real
antenna's measured impulse response into the source current, derived by
comparing a gprMax free-space run against the real DZT mean trace). Swapped
`[source] waveform=gaussian` for `excitation_file=gssi_excitation.txt` /
`excitation_waveform_id=gssi_420mhz` on the same rock=6.1/matrix=3/420MHz
geometry (`three_layer_420mhz_gssi_excitation.toml`; file must be copied into
the same directory as the `.in` and referenced by bare filename — gprMax's
`#excitation_file` splits on `:`, breaking Windows drive-letter paths).

**Result — big improvement:**

| Metric | Gaussian source (baseline) | GSSI-calibrated excitation |
|---|---|---|
| Envelope correlation | 0.979 | **0.9955** |
| Raw correlation (flipped) | 0.946 | **0.984** |
| Pre-peak (leading edge) raw corr | — | **0.9987** |
| Post-peak (trailing edge) raw corr | — | 0.950 |

Splitting the comparison at the peak confirms the diagnosis exactly: the
leading-edge mismatch is now (almost) fully resolved (0.9987) by using the
real calibrated wavelet instead of an idealized Gaussian — it was a SOURCE
WAVELET SHAPE problem, not a subsurface/geometry problem. A smaller
trailing-edge mismatch remains (0.950), now a better-isolated candidate for
genuine FDTD-domain effects (dispersion, scattering loss) rather than source
shape, worth investigating separately.

## Files (Run 9)
- `gssi_excitation.txt` — copy of `calibration/gssi_excitation.txt` (deck-local, bare-filename requirement)
- `three_layer_420mhz_gssi_excitation.toml/.in/.out` — GSSI-calibrated-excitation run
- `efe_overlay_gssi_excitation_flipped.png` — 3-panel comparison vs EFE PK=20km

---

## Run 10 — Rock-count RF feasibility check (see `rock_count_rf/README.md`)

Tested whether an RF can predict the NUMBER OF PACKED ROCKS from waveform
features alone. Found and worked around a real bug along the way: the
default `pymunk_ballast` packer silently ignores `target_fill_ratio` and
`rock_radius_min/max` (hardcoded internal grading curve) — switched to
`circlify`, which respects them. 36-sample dataset (target_fill x seed
sweep, actual count 32-213), full `extract_features()` (820 features) +
RandomForestRegressor, 5-fold CV.

**Result: no robust signal (R² ≤ 0 for every model tried)** — full RF
(-0.054), reduced 10-feature RF (-0.074), single-feature linear regression
on peak amplitude (-0.227). A marginal in-sample correlation (coda peak vs
count, r=0.363, p=0.03) doesn't survive cross-validation at this small N.
Feasibility check only, not a validated negative — N=36 is small relative to
820 candidate features. Full writeup, bug details, and all data in
`rock_count_rf/`.

### Follow-up: N=100 — the signal was real, just needed more samples

Re-ran the identical method (`rock_count_rf_100/`) with 5x more samples
(target_fill in {0.30,0.45,0.60,0.75,0.90} x 20 seeds = 100, all succeeded).
**R^2 jumped from -0.054 (N=36) to 0.264 ± 0.188 (N=100)** — all 5 CV folds
positive (0.047-0.594), MAE 21.4 rocks on a 33-241 range (~10.3%). The N=36
single-feature correlation (peak_max, r=0.363/p=0.03) did NOT replicate at
N=100 (r=0.113/p=0.26) — confirms it was noise; the real signal only appears
in the full multivariate RF. Top features are all CODA-domain
(`coda_stft_*`, `coda_grid_hilbert_*`), consistent with the project's
established "coda holds the subsurface signal" finding. Caveat: `circlify`'s
`target_fill` confounds rock count with average rock size, so the RF may be
partly detecting size rather than count specifically. Full writeup:
`rock_count_rf_100/README.md`.

**Follow-up: does the project's `preprocess_signal()` convention help here? No — it hurts.**
Project convention says synthetic traces should always go through
`preprocess_signal()` (dewow/time-gate/bandpass/peak-normalize) before
`extract_features()` — the runs above skipped it. Applying it (matched to
this geometry: 420MHz/0.1m air gap) DROPPED R² from 0.264±0.188 to
-0.235±0.244 (all 5 folds negative). That convention exists to fix a
real-vs-synthetic amplitude-scale mismatch, which isn't relevant for a
synthetic-only regression like this one — peak-normalizing away absolute
amplitude, and the time-gate's direct-wave removal, both plausibly discard
signal that was actually useful for predicting rock count. Lesson: that
preprocessing rule is task-specific (real/synthetic transfer), not a
blanket default. Full detail in `rock_count_rf_100/README.md`.

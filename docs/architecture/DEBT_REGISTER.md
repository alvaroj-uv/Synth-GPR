# Architecture Debt Register

**Created:** 2026-07-02 (full-repo audit; evidence = guard tests + pattern greps + memory-recorded issues)
**Rule:** update this file when a debt is paid or a new one is knowingly taken on. Severity is
about *consequence if ignored*, not code ugliness.

Recently paid (2026-07-02, for context): `ballast_crim` + CRIM constants moved to
`src/physics.py` / `constants.MC` (SSOT); voxelizer bit-parity + CRIM hull tests ported into
`tests/`; `eps_eff` linear-mixing mislabelled as CRIM renamed `eps_eff_linear`;
`src/gprmax_runner.py` extracted (env path + bare-name/cwd invocation conventions).

---

## Severity 1 — correctness-adjacent (can silently corrupt results)

### D1. Hardcoded dt fallbacks (the bug class that already burned us once)
`src/visualization/dashboard.py:59,61,66` falls back to `dt = 1e-10` (0.1 ns) when the time
vector is missing/short. The dt/frequency incident (see memory `feedback_dt_freq_bug`: all
frequency features mis-scaled 3.2× by a 0.1 ns default) came from exactly this pattern.
**Fix:** raise or return NaN instead of guessing; dt must come from file attrs. Effort: S.

### D2. Two live FI definitions (recorded, unfixed)
`convert_pvc_to_fi` (mass-based) caps FI at ~38.7 → the HF class is unreachable through that
path, while datasets use Selig P4+P200 (memory `feedback_two_fi_definitions`); real labels use a
third convention (pandoscope layer heights, `reference_real_labeling`). Also pending: mapping
classifier outputs to the Selig 5 states consumed by the Rojas-Vivanco 2026 indicator framework.
**Fix:** one FI module in `src/physics.py` with named conversions + tests; deprecate ambiguous
call sites. Effort: M. High scientific value.

### D3. Deck writing that bypasses `gpr_commands`
3 scripts hand-assemble `#material:`/`#box:` strings (`calibration/invert_pk20000m_envelope.py`,
`calibration/calibrate_layers.py`, `render_scenes_with_eps_gradient.py`), skipping
`MaterialCommand`'s eps ≥ 1 validation and the priority machinery.
**Fix:** build decks from `gpr_commands` (natural to do when the inversion forward model is
extracted to `src/`, see D10). Effort: S per script.

---

## Severity 2 — eroded boundaries (guards exist and are red)

### D4. I/O boundary regression: raw h5py in 25 scripts
`tests/test_io_boundary.py::test_no_raw_h5py_in_scripts` is FAILING (25 offenders vs 2
whitelisted). The Phase 1–3 consolidation (docs/architecture/IO_CONSOLIDATION_PLAN.md) eroded as
calibration/experiment scripts were added afterwards. A red guard means new offenders cost
nothing — the signal is dead until the list is drained.
**Fix:** route through `src.data_loader` (mostly mechanical `read_ascan`/`read_rx_traces`
substitutions); consciously whitelist genuine exceptions (e.g., DZT header diagnostics) so the
test is green and meaningful again. Effort: M (~1–2 days, mechanical).

### D5. Machine-specific paths scattered
gprMax env path now centralised in `src/gprmax_runner.py`, but 4 scripts still hardcode
`.conda/envs/gprMax` or `conda run -n gprMax` (`generate_3d_scene.py` docstring,
`verify_best.py`, `calibrate_layers.py`, `run_void_eps_sweep.py`); data paths like
`D:/Codigo/Data/efe_full.h5` are hardcoded in calibration scripts.
**Fix:** import `GPRMAX_PYTHON`/`run_gprmax` everywhere; a tiny `src/paths.py` (or env vars) for
data roots. Effort: S.

---

## Severity 3 — duplication / SSOT drift

### D6. Waveform scale factor 2592.59 in 5 scripts
The synthetic→A/D comparative scale (memory `project_waveform_scaling_result`) is pasted in 5
scripts (`check_gssi_reader*.py`, `read_dzt_header_raw_data.py`, `extract_calibration_from_dzt.py`,
`visualize_overlay_synthetic_vs_real.py`). If the GSSI V_ref ever arrives and the factor changes,
five copies must change. **Fix:** `constants.SC` entry. Effort: S.

### D7. First-break picking: 5 implementations
`signal_processing.py` holds `detect_first_break_coppens`, `detect_first_break_sta_lta`,
`detect_first_break` (dispatcher), and `_first_break_sample`; `unified_visualizer.py` duplicates
the latter as `_first_break_ns`. Different conventions = subtle alignment discrepancies between
plots and objectives. **Fix:** one public picker + one peak-relative helper; visualizer imports
it. Effort: S.

### D8. Material defaults duplicated outside `constants.MC`
`generate_3d_scene.py` `MATS_BASE` + `load_config` defaults hardcode eps/σ (5.1/10.0/6.1/7.5)
instead of referencing MC; note the *documented* duality MC.BALLAST_ROCK_PROPS=4.0 (Tosti bulk,
2D dataset pipeline) vs MC.CRIM_ROCK_EPS=6.1 (Brancadoro grains, packed-rock/inversion path) —
intentional, do not merge blindly. **Fix:** point script defaults at MC. Effort: S.

### D9. Two "frozen packing" mechanisms
2D: `rock_library` / `config.rock_source_file`; 3D: `--sphere-file` CSV (added because
rcpgenerator is non-deterministic even with a fixed seed — memory
`feedback_rcpgenerator_nondeterminism`). Same concept, two formats.
**Fix:** unify under rock_library when the 3D path stabilises. Effort: S–M.

---

## Severity 4 — structure / sprawl (slows work, hides bugs)

### D10. `invert_pk20000m_envelope.py` is a library wearing a script's clothes
Deck writers (2D+3D), CRIM wiring, objectives, ratio calibration, noise injection, target
caching, CLI, and mutated module globals (`WORK_DIR`, `RATIO_CAL`) in one file. Test scripts
already import it via `importlib` gymnastics — the tell.
**Fix:** split into `src/` (forward decks on `gpr_commands`, objectives, targets) *when the
second consumer (MCMC/multi-truth driver) exists*, so module seams follow real usage. Effort: M.

### D11. scripts/ sprawl: loose files at the root — IN PROGRESS (2026-07-02)
Low-risk first pass done: deleted 31 pure-scratch one-offs (alignment/flip/pad,
A-scan comparison, antenna spacing/height/mode clusters — all 2026-06-16, git-recoverable,
zero importers, outputs already in experiments/). Root now 24 files (was 55). Remaining:
scale-factor consolidation (D6), header probes, pipeline/ leaked sweeps, script_logging vs
logging_config, relocate utilities to tools/. See SCRIPTS_INVENTORY.md.

Original note:
### scripts/ sprawl: 55 loose files at the root
Dozens of one-shot session artifacts predating the experiments-folder rule (4× `scale_waveform*`,
3× `flip_*`, 2× `pad_*`, ~10× `compare_*`…). They inflate guard-test offender lists, shadow the
curated `pipeline/`/`visualization/`/`calibration/` entry points, and rot.
**Fix:** triage — archive to `experiments/<date>/` (their outputs mostly already live there) or
delete; keep the root to <10 curated tools. Effort: M (tedious, zero risk).

### D12. God modules — LARGELY PAID (2026-07-02)
- `signal_processing.py` (was 112 KB / 2635 lines, 44 defs) → **split into 6 focused modules**
  along its own documented sections: `preprocessing.py` (direct wave, SVD, pickers, gain,
  deconvolution, bandpass), `vivanco_pipeline.py` (Rojas-2025 replication + `predict_dzt_fouling`
  model application), `spectral_attributes.py` (FFT/STFT/instantaneous/MPM),
  `reflector_picking.py` (picks → depth → TOML), `bscan_processing.py` (ICA/WTMM, AGC, F-K,
  migration), `coda_objectives.py` (envelope r, energy ratio, W₂). `signal_processing.py` is now a
  **facade** re-exporting every previous name — zero importer changes needed. Verified: facade
  exposes all 45 HEAD names; AST undefined-name scan clean; signal tests 36/36.
- `unified_visualizer.py` 84 → 67 KB: `stitch_dzt_files` + `apply_agc_to_h5` moved to
  `src/dzt_io.py` (with the AGC-is-display-only warning baked into the docstring);
  `apply_vivanco_model_to_dzt`'s compute core moved to `src/vivanco_pipeline.predict_dzt_fouling`
  (visualizer keeps the plot + re-exports, CLI unchanged).
- `rock_packing.py`: broken strategies **quarantined** with RuntimeWarnings + docstring flags
  (FrontChainPacking, PhysicsPacking: hang >90 s; PymunkBallastPacking: silently ignores
  `target_fill_ratio`/radius args). Full split of the 104 KB packer zoo REMAINS OPEN — do it
  when a packer is next modified, one strategy file at a time.
**Remaining:** rock_packing split; opportunistic trimming of the visualizer's remaining
mixed panels. Effort: M (was L).

### D13. No packaging → 60 copies of `sys.path.insert`
Every script bootstraps the repo root by hand. **Fix:** minimal `pyproject.toml` +
`pip install -e .` in the working envs; delete the boilerplate opportunistically. Effort: S–M.

### D14. Test-suite hygiene
Full suite ≈ 11+ min (generation tests dominate) → nobody runs it, guards rot (D4). Pytest's
default basetemp is permission-broken on this machine (`pytest-of-barba` — use
`--basetemp`). `test_publication_figures.py` effectively excluded from routine runs.
**Six tests are red at committed HEAD** (verified 2026-07-02 in a clean worktree — NOT caused by
uncommitted work): the D4 h5py guard, `test_layer_spec.py::test_toml_file` +
`::test_full_config_toml`, `test_png_output.py::…test_render_flag_produces_png`,
`test_visualize_blueprint.py::…test_render_2d_geometry` +
`::test_parser_reads_triangle_material_after_thickness` (parser rejects 3-token
`#material: 8 0.02 subgrade` fixture lines — fixture/parser drift).
**Fix:** mark slow tests (`-m "not slow"` default), set basetemp in `pytest.ini`, repair/triage
the six red tests so the suite is green and red = regression again. Effort: S–M.

---

## Suggested order of attack

1. **D1 + D6 + D7** (one sitting, small, correctness + SSOT).
2. **D14 then D4** — make the suite runnable-fast and green, then drain the h5py offender list;
   the guards only pay rent when they're green.
3. **D2** next time labels/classifier work is touched (pairs with the Selig-state remap).
4. **D10 + D3** together when the MCMC/multi-truth phase starts.
5. **D11, D13** as background chores; **D12** opportunistically; **D5, D8, D9** whenever the
   owning file is next edited.

# Scripts Inventory

**Created:** 2026-07-02. Feeds debt **D11** (scripts/ sprawl) in DEBT_REGISTER.md.
93 `.py` under `scripts/`: **55 loose at root** + 17 `pipeline/` + 13 `visualization/` + 8 `calibration/`.

> **Progress (2026-07-02):** low-risk pass #1 done — groups A, B, C (31 scratch one-offs)
> DELETED. Root is now 24 files (was 55). Sections below retain the original analysis;
> groups A/B/C are historical.

Legend: **CANONICAL** (curated entry point, keep) · **KEEP** (still useful) ·
**ARCHIVE** (one-off; output already in an experiments/ folder → move there or drop) ·
**DELETE?** (superseded, no lasting value) · **SSOT** (hardcodes a duplicated constant/path).

---

## scripts/ (root) — 55 files, almost all dated 2026-06-16 (one session, 16 days old)

The root is a graveyard of one-off sim↔real matching experiments from the early calibration
phase. None are imported by `src/`. Superseded by: the canonical **unified_visualizer**
(comparison/overlay), the **validated 420 MHz pipeline** (alignment is baked in via the
GSSI-calibrated excitation), and the new `src/` modules. Grouped by intent:

### A. Waveform alignment / flip / pad (sim→real timeline) — ARCHIVE/DELETE?
`align_peaks_with_delay`, `apply_delay_and_flip`, `flip_polarity_and_align`,
`flip_polarity_peak_align`, `flip_synthetic_horizontally`, `flip_waveform_polarity`,
`pad_original_without_flip`, `pad_synthetic_to_match_real`, `match_synthetic_to_real_time_window`,
`match_synthetic_to_real_timeline`, `show_aligned_signals`, `compare_aligned_signals` (12)
→ The align/flip/pad question was settled; alignment now lives in the pipeline. Pure scratch.

### B. A-scan comparison one-offs — DELETE? (superseded by unified_visualizer)
`compare_ascan_files`, `compare_ballast_coda`, `compare_flipped_and_trimmed`,
`compare_flipped_then_padded`, `compare_normalized_ascan_files`, `compare_padded_and_flipped`,
`compare_raw_synthetic_vs_real`, `compare_waveform_shapes_matched_time`, `compare_waveforms`,
`compare_rocks`, `zoom_direct_wave`, `visualize_overlay_synthetic_vs_real` (12)
→ `unified_visualizer.py --overlay` / `compare_scans.py` replace all of these.

### C. Antenna spacing / height / mode experiments — DELETE? (antenna direction CLOSED)
`compare_all_antenna_spacings`, `compare_antenna_heights`, `modify_antenna_spacing`,
`optimize_rx_tx_configuration`, `optimize_tx_rx_spacing`, `test_antenna_heights`,
`test_antenna_modes` (7)
→ Antenna ruled out as the sim→real gap (memory: antenna_twin_conclusion); these are dead-branch.

### D. Waveform scaling (2592.59) — SSOT (debt D6), consolidate then DELETE
`scale_waveform`, `scale_waveform_binary`, `scale_waveform_correctly`, `scale_waveform_fast` (4)
→ Four variants of the same A/D-scale conversion; the factor belongs in `constants.SC`.

### E. GSSI / DZT reader diagnostics — mixed
- `compute_gssi_excitation` (2026-06-26) — **KEEP**: produces `calibration/gssi_excitation.txt`,
  the calibrated source the inversion + validated pipeline depend on. (Not imported, but it is
  the generator of a load-bearing artifact.)
- `check_gssi_reader`, `check_gssi_reader_final`, `read_dzt_header_raw_data`,
  `extract_calibration_from_dzt` — **SSOT (D6, 2592.59) + DELETE?**: header-format probes, the
  DZT format is now settled in `src/dzt_io.py`.

### F. Epsilon / frequency sweeps — ARCHIVE (results in experiments/)
`sweep_ballast_epsilon_50ns`, `sweep_epsilon_values`, `test_frequency_variants`,
`test_waveform_variants`, `plot_frequency_sweep` (5)

### G. Scene rendering — DELETE? (superseded by generate_gprmax_scenes / unified_visualizer)
`render_gprmax_scenes`, `render_scenes_with_eps_gradient`, `render_toml_scenes_with_eps_gradient`,
`create_freespace_scene_400mhz` (4). Note: `render_scenes_with_eps_gradient` hand-writes decks
(debt D3, bypasses gpr_commands).

### H. Dataset generation — DELETE? (superseded by pipeline/ generators)
`create_extended_synthetic_dataset`, `generate_and_organize_datasets` (2)

### I. Genuine utilities — KEEP (but relocate)
- `script_logging.py` — logging helper (0 importers now; `src/logging_config.py` is the real one
  → verify redundant, then DELETE).
- `convert_gprmax_snapshots.py` — snapshot→image converter, reusable utility → move to a `tools/`.
- `process_signal_vivanco_method.py` (22 KB) — **DELETE?**: the Vivanco method now lives in
  `src/vivanco_pipeline.py`; 1 stale importer to repoint.
- `visualize_dzt_sample_trace.py` (2026-06-26) — quick DZT trace viewer → fold into visualizer.

**Root verdict:** ~48 of 55 are one-offs (groups A–H). Recommended: keep `compute_gssi_excitation`,
`convert_gprmax_snapshots`; delete/relocate the rest. Their outputs already live in dated
`experiments/` folders, so deletion loses no record. Target: <8 files at root.

---

## scripts/pipeline/ — 17 files (mostly CANONICAL, some leaked one-offs)

**CANONICAL generators/trainers:**
`generate_3d_scene.py` (3D GSSI scene, --rock-shape/--sphere-file),
`generate_gprmax_scenes.py` (TOML→.in), `generate_layer_height_dataset.py`,
`extract_features.py`, `extract_features_layer_height.py`,
`train_layer_height_regressor.py`, `eval_layer_height_real.py`, `plot_virtual_sieve.py`,
`run_void_eps_sweep.py`, `generate_10layer_eps_sweep.py`.

**Leaked one-offs (ARCHIVE — belong in experiments/):**
`test_epsilon_sweep`, `test_moisture_sweep`, `test_rock_diameter_sweep`, `test_rock_spacing`,
`test_sigma_sweep_single_layer` (5 sweep scripts), `compare_rocks_final` (opens a hardcoded
`start_fresh_reduced.out`), `generate_rocks_model` (no docstring). These are session artifacts
that landed in pipeline/ instead of a dated folder.

## scripts/visualization/ — 13 files

**CANONICAL:** `unified_visualizer.py` (the one true visualizer — always extend this).
**KEEP (specialized plots):** `visualize_bscan`, `visualize_gprmax_ascans`, `compare_scans`,
`compare_vivanco_envelopes`, `plot_coda_energy_vs_fi`, `plot_fouling_classes`,
`plot_window_energy_features`, `visualize_checkpoint`, `antenna_mode_diagram`,
`antenna_radiation_pattern`, `visualize_antenna_signals`.
Some overlap with unified_visualizer's panels → candidates to fold in over time.

## scripts/calibration/ — 8 files (CANONICAL, active inversion work)

`invert_pk20000m_envelope.py` (the CRIM two-term inversion, active),
`invert_pk20000m_w2_grid.py` (overnight W₂ grid), `calibrate_layers.py` (optuna TPE),
`verify_best.py` (3D verification of top optuna trials), `reflector_depth_validation.py`,
`mpm_bscan_diagnostic.py`, `mpm_fi_correlation.py`.
Debt: `invert_pk20000m_envelope` + `calibrate_layers` hand-write decks (D3); several use raw
h5py (D4). Extract shared forward-model to `src/` when the MCMC phase lands (D10).

---

## Cross-cutting debts touching scripts/ (see DEBT_REGISTER.md)

- **D4** raw h5py: 10 root scripts (+ calibration) bypass `src.data_loader`.
- **D5** hardcoded paths: 21 root scripts hardcode `D:/Codigo/Data` real-data paths.
- **D6** the 2592.59 scale factor: 5 scripts (group D + E).
- **D3** deck strings bypass gpr_commands: `render_scenes_with_eps_gradient` + 2 calibration.
- **D13** every script hand-rolls `sys.path.insert` (no packaging).

## Recommended cleanup order (extends D11)

1. Delete groups A, B, C (31 pure-scratch scripts, 2026-06-16, outputs already in experiments/) —
   biggest sprawl reduction, zero risk (git-recoverable; nothing imports them).
2. Consolidate D (scale factor → constants.SC) and E header probes, then delete.
3. Move pipeline/ leaked sweeps + compare_rocks_final/generate_rocks_model to experiments/.
4. Verify `script_logging` vs `src/logging_config` redundancy; drop the loser.
5. Relocate `convert_gprmax_snapshots` (+ keep `compute_gssi_excitation`) to a `tools/` dir.

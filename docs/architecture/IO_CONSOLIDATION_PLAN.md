# File I/O Consolidation Plan

**Goal:** concentrate all file reading/writing behind specialized abstractions in
`src/`, so that scripts never touch raw file handles (`h5py.File`, `open()`,
`pd.read_parquet`, …). One module owns each file format; scripts call typed
readers/writers that return domain objects.

**Status:** plan only — no code changes yet. Phases are ordered by
risk-adjusted value (cheap + safe first, structural + risky later).

---

## 1. Current state (inventory)

### 1.1 What `src/` already provides
| Format | Canonical module | API (today) | Gap |
|---|---|---|---|
| `.out` (gprMax HDF5) | `src/data_loader.py` | `read_gprmax_hdf5()`, `read_ascan()`, `load_batch_dataset()` | 14 scripts bypass it with raw `h5py.File` |
| `.in` write | `src/file_writer.py` | `GPRMaxFileWriter.write_scene/write_to_file/save_scene_checkpoint` | ✅ already centralized |
| `.in` read (config) | `src/file_reader.py` | `extract_config_from_in_file()`, `extract_sources_from_in_file()`, `reconstruct_generator_config()`, `get_config_summary()` | only parses `## CONFIG_*` headers — not geometry |
| Scene collection | `src/repositories/filesystem_repository.py` | `FileSystemSceneRepository` (save / find / metadata CSV) | has its **own** `_extract_metadata_from_in_file` |
| Feature/dataset parquet | — | none | 16 scripts read/write parquet ad-hoc |

### 1.2 The `.in` reading problem — **five** parsers for one format
1. `src/file_reader.py` — `## CONFIG_*` headers → generator config.
2. `src/visualization/scene.py::parse_in_file` — 2D geometry (`#box/#cylinder/#triangle/#fractal_box`, tx/rx, `## meta` as JSON) → `SceneData`.
3. `scripts/visualization/render_3d_in_file.py::parse_3d_in_file` — 3D geometry (`#sphere`, `#box` w/ z, `antenna_like_GSSI`, `## meta`).
4. `scripts/visualization/visualize_ascan.py::read_header_meta` — `## key: val` metadata only.
5. `src/repositories/filesystem_repository.py::_extract_metadata_from_in_file` — metadata extraction for the repository index.

These disagree on dimensionality (2D vs 3D), metadata typing (raw str vs
JSON-decoded), and comment syntax (`##` vs `## CONFIG_`). This is redundancy #2
from the visualization cleanup.

### 1.3 Scattered I/O counts (scripts/)
- `h5py.File` direct: **14 files**
- `read_parquet`/`to_parquet`: **16 files**
- raw `open()`: 18 files · `json`: 1 · `np.save/load`: 1

---

## 2. Target architecture

Keep the existing module names (low churn — avoids touching 42 import sites).
Sharpen each module's responsibility so it is the **single** owner of its format.

```
src/
  data_loader.py     # THE .out reader  -> arrays / DataFrames / AScan
  file_reader.py     # THE .in reader   -> Scene{geometry, antennas, meta, config}
  file_writer.py     # THE .in writer   (already canonical)
  dataset_io.py      # NEW: THE feature/dataset parquet reader+writer
  repositories/      # scene-collection persistence (consumes file_reader)
  visualization/
    scene.py         # consumes file_reader's Scene; owns DRAWING only, not parsing
```

**Design rules (fitness functions):**
- A script must not import `h5py`, nor call `pd.read_parquet`/`to_parquet`, nor
  `open()` a `.in`/`.out`. It calls a `src` reader/writer instead.
- Each reader returns a **domain object** (e.g. `Scene`, `AScan`), not a raw
  handle or loose dict.
- Parsing logic lives in exactly one module per format; renderers/consumers
  receive the parsed object.

### 2.1 Unified `Scene` model (the keystone)
A single dataclass that supersedes `SceneData` (2D) and the 3D dict, carrying
full 3D coordinates so both the 2D projection and 3D views can consume it:

```
Scene:
  domain:   (x, y, z)
  boxes:    [Box(x1,y1,z1, x2,y2,z2, material)]
  spheres:  [Sphere(x,y,z, r, material)]
  cylinders/triangles: …
  tx:       Antenna(x,y,z)         rx: [Antenna(...)]
  meta:     dict      # JSON-decoded ## key: val (incl. CONFIG_*, Lab_*, PSD)
```

2D consumers read `(x1,y1)/(x2,y2)`; 3D consumers also read z. `meta` is the one
source of truth for config + lab metadata, so `file_reader.extract_config_*`
and the repository's extractor become thin views over `Scene.meta`.

---

## 3. Phased migration

### Phase 0 — Guardrails (no behavior change) · *low risk* — ✅ DONE
- `tests/test_io_consolidation.py`: characterization tests pinning
  `read_ascan` / `read_rx_traces` against the exact legacy raw-`h5py` patterns
  (synthetic, always-on) plus real-fixture byte-identity (`skipif` gitignored).
- Inventory table above is the reference.

### Phase 1 — `.out` reading sweep · *low risk, mechanical* — ✅ DONE
Migrated all 14 scripts off raw `h5py.File`:
- **Signal reads (12)** → `data_loader.read_ascan` (single Ez/component) or
  `read_rx_traces` (multi-component dominant-energy pick, `antenna_twin_ab`):
  `rock_vs_homog_rigorous`, `experiments/{antenna_twin_ab, ballast_eps_ab,
  hetero_fouling_ab, hetero_fouling_lib_ab, homog_debye_extreme,
  homog_debye_slope, peplinski_slope, phantom_recovery_stage1, waveform_ab}`,
  `visualization/{plot_coda_energy_vs_fi, plot_fouling_classes}`.
- **Writer (1)** → new `data_loader.write_rx_out` owns the `.out` HDF5 layout;
  `tools/generate_fake_output` now calls it. data_loader owns read **and** write.
- **Introspector (1)** → `analysis/analyze_dataset_structure` keeps raw `h5py`
  by design (it dumps HDF5 group/dataset structure); documented as the
  sanctioned exception in-file and here.

### Phase 2 — `.in` reading unification · *medium risk, highest dedup*
1. Define the unified `Scene` model + one `parse_in_file()` in `file_reader.py`
   (geometry 2D+3D, antennas, JSON-typed `meta`).
2. Re-point `scene.py` to consume `Scene` and keep **drawing only**
   (`draw_geometry`, `render_geometry_figure`).
3. Re-point `render_3d_in_file.py` to consume `Scene`; delete `parse_3d_in_file`.
4. Replace `visualize_ascan.read_header_meta` with `parse_in_file(...).meta`.
5. Make `file_reader.extract_config_from_in_file` and the repository's
   `_extract_metadata_from_in_file` thin views over `Scene.meta`.
6. Resolves visualization redundancy #2. Guard with Phase-0 characterization
   tests on real `.in` files (2D and 3D).

### Phase 3 — Dataset/parquet I/O · *higher risk, ML pipeline*
- Introduce `src/dataset_io.py`: `load_features()`, `save_dataset()`,
  `load_splits()` — one place for schema, dtypes, compression, column contracts.
- Migrate the 16 parquet scripts (pipeline `build_parquet*`, `train_rf*`;
  analysis `sim2real_*`, `domain_adapt`, `validate_real`; experiments).
- Highest value for reproducibility (enforces the 572-waveform-feature schema in
  one spot) but touches the training path — migrate read-only consumers first,
  then writers, with row-count/column/hash assertions.

### Phase 4 — Enforcement · *optional*
- A test that greps `scripts/` for `h5py.File` / `pd.read_parquet` / `open(*.in)`
  and fails, locking in the boundary so new scripts can't regress.

---

## 4. Risk & sequencing summary
| Phase | Touches | Risk | Value | Reversible? |
|---|---|---|---|---|
| 0 Guardrails | tests only | none | enables the rest | n/a |
| 1 `.out` sweep | 14 scripts | low | dedup + consistency | yes (per-script) |
| 2 `.in` unify | 5 parsers → 1 | medium | kills redundancy #2 | yes (git) |
| 3 dataset I/O | 16 scripts | higher | reproducibility | yes (read-first) |
| 4 enforcement | 1 test | none | prevents regression | yes |

**Recommended order:** 0 → 1 → 2 → 3 → 4. Phases 1 and 2 are independent and can
interleave; Phase 3 should wait until Phase 0 fixtures exist.

**Out of scope / already done:** `.in` **writing** is already centralized in
`GPRMaxFileWriter`; `.out` reading has a canonical home (`data_loader`) — Phase 1
is adoption, not new abstraction.

# Environment

## Python
- Python >= 3.10 (code uses modern type annotations). Install: `pip install -r requirements.txt`
- El intérprete/ejecutable de gprMax se resuelve vía variable de entorno
  `GPRMAX_PYTHON` (o `gprmax.ini`, ver `src/config.py::resolve_gprmax_python`);
  **nunca hardcodear rutas de máquina**.
- gprMax is NOT in requirements and NOT pip-installable here. Tests que lo
  requieren van marcados `@pytest.mark.gprmax` y skipean si no está instalado.
- Run tests: `pytest` (must be green at the end of every session).

## Repo discipline
- Constants ONLY in `src/constants.py`. Materials ONLY via `NAMED_MATERIALS`.
- Scene metadata ONLY as `## CONFIG_*` headers inside `.in` files.
- New pipeline code → `scripts/pipeline/`. NEVER add scripts to the repo root.
- Exploratory one-offs → don't commit, or move to `attic/` with a README note.

## Do not modify without explicit user approval
- `src/physics.py` (validated against literature)
- `src/layer_scene_builder.py` (painter's-algorithm ordering is load-bearing)
- `tests/fixtures/**` including `ground_truth.json` (validated physics; tests depend on it)
- Any real DZT data.

## Units & conventions (single source of truth)
- Distances: meters. Frequencies: Hz. Time: seconds in storage/HDF5, ns in analysis
  variables named `*_ns`.
- `dt` is ALWAYS explicit and read from the source: HDF5 attr `dt` for sim,
  DZT header for real. Never assume or default it.
- Polarity: sim Ez × (−1) to match GSSI voltage convention (post-processing step).
- Windowing/centering: slice the analysis window FIRST, subtract the mean AFTER.
  (Full-trace mean is a shared offset that creates phantom correlations.)

## Testing rules
- New module ⇒ tests in the same change. Physics assertions compare against
  `tests/fixtures/ground_truth.json`, not hardcoded numbers.
- Golden test (`tests/test_golden_features.py`) must pass before ending any session.
  Regenerating `golden_features.json` requires justification in the commit message.
- Prefer raising `ValueError` over emitting warnings for anything that would
  silently corrupt data (missing dt, asymmetric normalization, etc.).

## Commits
- One backlog task per commit/branch; message references the task: "T6: ...".
- Never commit: real DZT files, bulk `.out` outputs, `__pycache__`.

## Honesty
- Never claim in docs/README that something works without a test proving it.
- If a task can't be done as specified, stop and report — don't deliver a lookalike.

## Domain context (read before "optimizing" anything)
- An A-scan is a single GPR trace: amplitude vs. time. Setup: GSSI 400 MHz antenna,
  air-launched at 0.50 m over railway ballast.
- The ballast coda is SPECKLE (random realization of stone packing). Raw-waveform
  correlation over the coda is physically meaningless — the stable observables are
  smoothed envelope (→ attenuation/σ), coherent reflection timing (→ ε, thickness),
  and spectral content (→ fouling signature: centroid downshifts with fouling).
- Fouling classes come from the physical cause (fines fraction / ground truth),
  never from the ε the model could read. See docs/specs/ALGORITHM_SPECS.md.

## Documentos de trabajo
- Backlog de tareas: TODO_claude_code.md (trabajar en orden P0 → P1 → P2)
- Especificaciones de algoritmos: docs/specs/ALGORITHM_SPECS.md
  (leer OBLIGATORIAMENTE antes de implementar T6, T8 o T9)
- Fixtures de verdad conocida: tests/fixtures/ (batch sintético `sim/` + trazas
  reales `real/` con ground_truth.json; todo código nuevo del pipeline se prueba
  contra él — sanity-check con `python tests/validate_fixtures.py`)
- Contexto del proyecto: docs/NOTA_ESTADO_SynthGPR.md

## Reglas de validez (nunca violar)
1. Nunca splits aleatorios por traza — siempre GroupKFold por `group`
2. Nunca eps/sigma/pvc como features de ML (solo metadatos con prefijo `meta_`)
3. Nunca ganancia/normalización sobre datos de análisis de amplitud
4. Nunca correlación de forma de onda cruda sobre la coda (es speckle);
   métricas válidas: envolvente suavizada, timing, espectro
5. Recortar la ventana de análisis ANTES de restar la media (el orden inverso
   crea correlaciones fantasma por offset compartido)

# Development Guidelines

## Code Review Before Creating New Scripts
**Always ask if creating new folder**
**Always check existing code first** before writing new scripts or functions:
1. Search for similar functionality in existing files (use Grep/Glob)
2. Review existing implementations to understand patterns and conventions
3. Check if code can be reused, extended, or modified rather than recreated
4. Only write new scripts when existing code doesn't serve the purpose or when extending existing patterns

This prevents duplication and maintains consistency across the codebase.

## Experiment Folders

**Every simulation experiment must have its own timestamped folder.**

When starting a new experiment (new geometry, new sweep, new parameter test):
1. Create `experiments/YYYY-MM-DD/` using the current date
2. Copy the TOML config and generated `.in` file into the folder immediately
3. Write a `README.md` in the folder describing the goal, expected results, and file list
4. After the simulation completes, copy `.out`, `.vti`, and any plots into the folder

Format: `experiments/2026-06-28/` (year-month-day, zero-padded)
Multiple experiments on the same day share the same folder.

This creates a permanent, self-contained record of every experiment.

## Documentation Standards

- Keep documentation **accurate and up-to-date** with current code state
- Remove docs once they become stale or superseded by newer ones
- Use the **Documentation Index** (`docs/INDEX.md`) to find relevant guides
- Archive docs only if referenced elsewhere or kept for historical record
- Link to related docs instead of duplicating information

# Research Direction

## Core Novelty: Waveform-Only Features

**The key innovation of this project is predicting fouling class from GPR Ez waveform features alone** — without relying on metadata (material composition, density, moisture, etc.).

**Why this matters:**
- Metadata is derived from lab measurements or simulation inputs, making it unavailable in real-world GPR deployments
- Waveform features (572-dimensional: time-domain, Hilbert, frequency, STFT, grid) are extracted directly from the received signal
- The goal is to develop a classifier that works on field data where only the Ez A-scan is available

**Training approach:**
- Primary model: RF trained on **waveform features only** (no metadata)
- Baseline: 0.7083 balanced accuracy on 30k samples with 572 waveform features
- Metadata can be used for validation/analysis but **should not be features in the production model**

**When adding features or changing the pipeline:**
- Prioritize waveform feature engineering (signal processing, wavelets, time-frequency, statistical moments)
- Avoid adding metadata columns as features — they defeat the research goal
- If metadata is needed, use it for stratification, analysis, or post-hoc validation only
- Focus on improving the core 572 waveform features or developing new signal-based features

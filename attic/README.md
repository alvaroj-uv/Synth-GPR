# attic/ — archived, unmaintained history

Historical / pre-refactor material kept for reference. Not maintained, not
imported by any live code.

- `tests_verify/` — the old manual, print-and-eyeball `tests/verify/` scripts
  (T13). The one still-valid invariant was rescued to `tests/test_invariants.py`.

## Note on T10 (loose root scripts)

The backlog expected ~44 loose root-level exploration scripts
(`compare_*` / `align_*` / `iterate_*` / `check_*` / `analyze_*`) to be archived
here. The `refactor/voxel-crim-module-split` refactor had already removed them
from the repo root: the canonical sim↔real comparison now lives in
`src/sim_real_comparison.py` (T6) with the CLI
`scripts/pipeline/compare_sim_real.py`. The repo root is already clean (config
and docs only — the remaining root `*.toml`/`*.in` are gitignored scratch
scenes), so there was nothing tracked left to move.

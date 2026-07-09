# Archived: tests/verify/ (T13)

These 23 scripts were manual, print-and-eyeball verification scripts (no pytest
assertions), run by hand rather than in CI. Archived here because:

- Several reference APIs that drifted in the refactor (e.g.
  `WorkOrder(params=...)` in `verify_domain_consistency.py`) and no longer run.
- Some use machine-specific path hacks (`sys.path.append("d:/Codigo/...")`).
- One (`verify_void_filling.py`) imports a non-package path and exercises a
  packer (PoissonDisk) that isn't the production one.

The one still-valid, dependency-light invariant — the FI<->PVC physics
round-trip — was rescued as real pytest assertions in
`tests/test_invariants.py`, which also documents the mass-ratio saturation cap
that the old `verify_physics_math.py` `sys.exit(1)`'d on.

Not maintained; kept for history.

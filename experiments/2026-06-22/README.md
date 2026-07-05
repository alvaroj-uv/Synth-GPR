# 2026-06-22 — 2D ballast model explorations

Large batch of 2D parameter sweeps building the early simulation vocabulary.

**Experiments:**
- `start_fresh*` — iterative 2D ballast geometry refinements (layered, fouled, with rocks, high-eps/energy/deeper)
- `rocks_spacing_{35,50,60}` — rock spacing sensitivity
- `moisture_sigma_*` / `moisture_configs` — sigma sweep for moisture content effect
- `test_moisture_*` — finer moisture parameter scans (configs generated, many not simulated)
- `test_rocks_in_sand*`, `test_sand_*`, `test_stratified_ballast` — interface geometry tests
- `sweep_sigma_*` — sigma sweep configs (generated, not all simulated)
- `test_diameter_*` — rock diameter sensitivity configs
- `test_eps_*` — eps sensitivity configs

**Status:** Exploratory. The `moisture_sigma_*` results informed the 3D material model.

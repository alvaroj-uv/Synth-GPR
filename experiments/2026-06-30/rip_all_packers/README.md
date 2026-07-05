# RIP shape (Li et al. 2023) tested against every packer

Tests `rock_shape="rip"` (see today's other addition, decoupled from
`rip_packing.RIPPacking`'s own RSA placement) against every algorithm
reachable via `[sim] rock_packing_algorithm` in the layers-mode pipeline
(`src/layer_scene_builder.py get_packer()`). Same rock=6.1/matrix=3/420MHz
geometry as `rock_shape_comparison.png` (polygon/circle/square).

## Result: 14/16 work, 2 fail, quality varies a lot

| Algo | Status | Notes |
|---|---|---|
| pymunk_ballast, circlify, rip, rcp, rcpgen, shang_chu, hybris_shang, triangle, growth, wang, grid | OK | Dense, reasonable ballast-like packing |
| rsa | OK | Noticeably sparser — RSA saturates at lower density |
| poisson | OK (technically) | **Badly underfills** — only clusters in one corner, most of the layer stays empty matrix. Not usable as-is for this domain/params. |
| random | OK (technically) | Sparse/disorganized compared to the rest |
| front_chain | **FAIL (timeout)** | Hangs past 90s for this geometry |
| physics | **FAIL (timeout)** | Hangs past 90s for this geometry |

**Practical takeaway:** the RIP shape decoupling works everywhere it's
supposed to (confirms the design), but not every packing ALGORITHM is
actually usable for this ballast-layer geometry — `poisson`/`random` need
parameter tuning or aren't a good fit, `front_chain`/`physics` need
investigation into why they hang (possibly missing a convergence/attempt
cap for this bounds size, or a genuine bug). Recommended pairing for
production use remains `rock_packing_algorithm="pymunk_ballast"` (the
project default) or `"circlify"`.

## Files
- `generate_all.py` — driver (generates + renders each combo, with timeout handling)
- `rip_<algo>.{toml,in,png}` — one set per successful algo
- `rip_all_packers_grid.png` — 14-panel comparison grid
- `generate_all_log2.txt` — second-run log (front_chain/physics onward)

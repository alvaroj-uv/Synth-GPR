# Archived: redundant standalone packers (T11)

`rip_packing.py` (RIPPacking) and `rcp_packing.py` (RCPPacking) are pure-Python
2D packers that were only reachable through the `"rip"` / `"rcp"` registry
branches in `layer_scene_builder.get_packer` and `warehouses.ToolWarehouse` — no
test and no 3D path used them.

T11 consolidated the packers around the two that are **optimized via external
libraries**:
- `src/pymunk_packing.py` — `MbubiaPymunkSceneGenerator` (pymunk 2D physics),
  the 2D default.
- `src/rcpgenerator_packing.py` — `RCPGeneratorPacking` (external RCPGenerator /
  C++ ADAM packing), also the packer the **3D** generator uses directly
  (`scripts/pipeline/generate_3d_scene.py` → `rcpgenerator.Packing(Ndim=3)`).

`rock_packing.py` (RSA, circlify, triangle, shang_chu, hybris_shang, growth,
poisson, random, wang, grid) was left intact — several tests instantiate those
classes directly, and TOMLs still route them via config — so pruning the whole
registry to two would have broken the pipeline. Only the two truly-redundant
standalone files were archived here.

Not maintained; kept for history.

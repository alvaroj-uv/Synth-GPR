# Scripts and Packer Documentation

Purpose
-------
This document describes the role of the main scripts under scripts/ (pipeline and visualization)
and documents the packing API introduced to decouple geometry packing from the scene
builder and exporters.

Scripts overview
----------------
- scripts/pipeline/generate_in_files.py
  - CLI entry for dataset generation and single-sample generation.
  - Produces .in files by composing GeneratorConfig, DatasetGenerator and a writer.
  - Now uses SceneModel (pure-data) and delegates packing via an injected packer.

- scripts/visualization/
  - Utilities to render scenes and A-scans. These scripts expect exporter output
    (e.g. gprMax .in files or JSON scene descriptions) and provide rendering helpers.

Packer API (design)
-------------------
To avoid tight coupling between the builder and a specific physics packer, the
project uses a small packer protocol and a pure-data Placement DTO.

PackerProtocol (summary)
- Expected method: generate_rocks(bounds, random_seed=None)
- Returns: an iterable of Placement objects
- Implementations:
  - MbubiaPymunkSceneGenerator adapter (wraps the existing pymunk-based packer and
    translates results into Placement objects)
  - TestPacker (deterministic, used for unit tests)

Placement DTO (fields)
- id: int
- x: float
- y: float
- radius: float
- is_polygon: bool
- vertices: list[tuple]
- layer: Optional[int]
- material: Optional[str]
- metadata: dict

Example: using TestPacker in unit tests
--------------------------------------
from src.pymunk_packing import TestPacker, PackingBounds
from src.layer_scene_builder import build_scene_commands

packer = TestPacker()
bounds = PackingBounds(x_min=0.0, x_max=1.0, y_min=0.0, y_max=0.2)
placements = list(packer.generate_rocks(bounds, random_seed=42))
# Inject packer into builder to render deterministic geometry
# build_scene_commands(..., packer=packer)

Injecting packer into the builder
--------------------------------
The builder functions accept an optional `packer` argument (PackerProtocol). Pass
an instance (TestPacker or MbubiaPymunkSceneGenerator) when calling build_scene_commands
or when reconstructing rock positions for LabWorker.

Exporter note
-------------
Exporters should operate on pure-data SceneModel/scene-checkpoint representations
and consume Placement objects for any target/rock geometry. The JSON exporter
included with the refactor serializes SceneModel dataclasses directly.

Recommended workflow for contributors
-------------------------------------
1. Use parse_toml() (src.scene_model) to build a SceneModel instance from a TOML file.
2. Call build_scene_from_model(scene) to get a conservative pure-data representation.
3. If packed layers are required, inject TestPacker (for tests) or get_default_packer().
4. Use Exporter implementations to serialize the pure-data scene to the target format.

Contact
-------
For questions about the packer adapter or to add support for other backend packers,
please update src/pymunk_packing.py and add an adapter that yields Placement objects.
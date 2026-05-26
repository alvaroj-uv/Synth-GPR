## Plan: Generate 5000 Angular Rocks 400MHz .in Files

TL;DR: Use the existing dataset generator pipeline and add a small reusable script that forces 400 MHz center frequency, angular rocks, and five fouling classes with 1000 samples each.

**Steps**
1. Create a new script in `scripts/main/` named `generate_angular_rocks_400MHz.py`.
2. In that script, import `GeneratorConfig` and `DatasetGenerator` from `src.config` and `src.dataset_generator`.
3. Build a base config using `GeneratorConfig.create_physically_perfect(4e8, ...)` with `granular_mode=True` and `angular_rocks=True`.
4. Loop through the five fouling classes `['CL', 'MC', 'MF', 'F', 'HF']` and generate 1000 samples per class, using `DatasetGenerator.generate_samples(output_dir, n_samples=1000, start_id=current_id)`.
5. Keep a running `current_id` offset so all sample IDs are unique and produce 5000 total `.in` files.
6. Save the generated files into a dedicated output folder such as `output/angular_rocks_400MHz_5class`.

**Verification**
1. Confirm `output/angular_rocks_400MHz_5class` contains 5000 `.in` files.
2. Confirm metadata CSV in that output folder has 5000 rows and `center_freq` values of `4e8`.
3. Open one generated `.in` file and verify the `angular_rocks` geometry path is used by eyeballing the file or using `scripts/tools/visualization/visualize_gprmax_blueprint.py` on a sample.

**Decisions**
- Use a dedicated script rather than only CLI flags, because `generate_dataset.py` does not currently expose `angular_rocks` through its INI loader.
- Target labels as the repository’s five fouling classes: `CL`, `MC`, `MF`, `F`, and `HF`.

**Further considerations**
1. If you want `moisture_max` or ballast thickness customized, the script can expose these as command-line options.
2. If you want a repeatable run with exact sample IDs, use a fixed `base_seed` and sequential `start_id`.

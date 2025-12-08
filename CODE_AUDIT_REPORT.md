# Code Audit Report

Generated on: 2025-12-08 13:33:01.442354


## Summary
- Total Files: 71
- Active Core: 22
- Standalone/Tools: 47
- **Candidates for Legacy**: 2

## Active Core
- create_feature_dataset.py
- generate_balanced_dataset.py
- scripts\main\create_feature_dataset.py
- src\config.py
- src\dataset_generator.py
- src\data_loader.py
- src\feature_extraction.py
- src\file_writer.py
- src\gpr_commands.py
- src\physics.py
- src\production_line.py
- src\quality_log.py
- src\recipes.py
- src\rock_packing.py
- src\scene_descriptor.py
- src\signal_processing.py
- src\warehouses.py
- src\warehouse_keeper.py
- src\worker.py
- src\workers.py
- src\work_order.py
- visualization\plot_utils.py

## Standalone / Tools / Tests
- ml\train_model.py
- scripts\__init__.py
- scripts\main\batch_extract_features.py
- scripts\main\consolidate_dataset.py
- scripts\main\extract_features.py
- scripts\main\generate_dataset.py
- scripts\main\run_simulations.py
- scripts\tools\audit_codebase.py
- scripts\tools\cleanup_root.py
- scripts\tools\migrate_candidates.py
- scripts\tools\regression_check.py
- scripts\tools\data_management\merge_datasets.py
- scripts\tools\data_management\update_hdf5_titles.py
- scripts\tools\data_management\validate_dataset.py
- scripts\tools\generation\generate_dummy_hdf5.py
- scripts\tools\generation\generate_master_pattern.py
- scripts\tools\research\analyze_selected_pdfs.py
- scripts\tools\tests\analyze_randomization_effect.py
- scripts\tools\tests\compare_domain_randomization.py
- scripts\tools\tests\compare_signals.py
- scripts\tools\tests\generate_randomized.py
- scripts\tools\tests\test_data_generator.py
- scripts\tools\tests\test_domain_randomization.py
- scripts\tools\visualization\read_gprmax_output.py
- scripts\tools\visualization\visualize_gprmax_blueprint.py
- tests\test_antenna_snippet.py
- tests\test_dataset_gen.py
- tests\test_decoupling.py
- tests\test_foreman.py
- tests\test_generation.py
- tests\test_production.py
- tests\test_ssot.py
- tests\test_wang_tiles.py
- tests\test_workers.py
- tests\verify_400mhz.py
- tests\verify_all_workers_read.py
- tests\verify_domain_consistency.py
- tests\verify_domain_restrictions.py
- tests\verify_fail_fast.py
- tests\verify_physics_math.py
- tests\verify_refactor.py
- tests\verify_resilience.py
- tests\verify_rock_dataframe.py
- tests\verify_workorder_refactor.py
- visualization\batch_visualize.py
- visualization\visualize_single_signal.py
- visualization\__init__.py

## Candidates for Legacy (To Move)
- ml\__init__.py
- src\__init__.py

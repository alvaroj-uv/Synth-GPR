"""
API Migration Summary for DatasetGenerator
===========================================

Old API (BallastScenarioGenerator):
-----------------------------------
gen.generate_dataset(out_dir, n_samples, csv_name, start_id)
Returns: pandas DataFrame

New API (DatasetGenerator):
----------------------------
gen.generate_samples(output_dir, n_samples, start_id)
Returns: List[str] (file paths)

Notes:
- Metadata CSV is always named 'metadata.csv'
- csv_name parameter removed (no longer configurable)
- Parameter renamed: out_dir -> output_dir

Migration:
1. Replace generate_dataset() -> generate_samples()
2. Replace out_dir= -> output_dir=
3. Remove csv_name= parameter
4. Update return value handling (DataFrame -> List[str])
"""

Pipeline Run Scripts
====================

This directory contains auto-generated scripts to run the remaining pipeline steps.

Usage:
------

1. Run gprMax simulations:
   ./run_gprmax.sh
   
   With options:
   ./run_gprmax.sh -p 4        # Use 4 parallel processes
   ./run_gprmax.sh -f          # Force re-run existing files

2. Extract features:
   ./extract_features.sh

3. Create blueprints:
   ./create_blueprints.sh
   
   With options:
   ./create_blueprints.sh -f   # Force re-create existing blueprints
   ./create_blueprints.sh -s   # Show blueprints after creation

Run all remaining steps:
------------------------
./run_gprmax.sh -p 4 && ./extract_features.sh && ./create_blueprints.sh

Directory: /Users/alvarojeria/Codigo/Synth-GPR/output/pipeline_run/20251210_142323
Generated: Wed Dec 10 14:30:46 -03 2025

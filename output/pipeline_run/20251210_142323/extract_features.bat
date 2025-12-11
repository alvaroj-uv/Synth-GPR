@echo off
set PYTHON_EXE="/opt/miniconda3/envs/gprMax/bin/python"
set SCRIPT="/Users/alvarojeria/Codigo/Synth-GPR/create_feature_dataset.py"
echo [BATCH] Extracting Features...
echo Input: %CD%
%PYTHON_EXE% %SCRIPT% "%CD%"
echo [BATCH] Extraction Complete.

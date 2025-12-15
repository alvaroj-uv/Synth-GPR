@echo off
set PYTHON_EXE="C:\Users\barba\.conda\envs\gprMax\python.exe"
set SCRIPT="D:\Codigo\Synth-GPR\Synth-GPR\scripts\main\create_feature_dataset.py"
echo [BATCH] Extracting Features...
echo Input: %CD%
%PYTHON_EXE% %SCRIPT% "%CD%" --metadata metadata.csv
echo [BATCH] Extraction Complete.

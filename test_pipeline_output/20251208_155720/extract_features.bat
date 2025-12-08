@echo off
set PYTHON_EXE="c:\Users\barba\.conda\envs\gprMax\python.exe"
set SCRIPT="D:\Codigo\Synth-GPR\create_feature_dataset.py"
echo [BATCH] Extracting Features...
echo Input: %CD%
%PYTHON_EXE% %SCRIPT% "%CD%"
echo [BATCH] Extraction Complete.

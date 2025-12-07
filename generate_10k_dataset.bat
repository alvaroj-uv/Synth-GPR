@echo off
REM ============================================================
REM Synth-GPR Production Pipeline: 400MHz 10k Dataset
REM ============================================================
echo.
echo ============================================================
echo SYNTH-GPR PRODUCTION RUN: 10,000 SCENARIOS
echo ============================================================
echo.
echo Configuration: 400MHz_production.ini
echo Output Folder: d:\Codigo\Synth-Data\400MHz_Production
echo Target Files:  10,000 (2,500 base samples x 4 variants)
echo.

REM Activate conda environment
call C:\ProgramData\miniconda3\Scripts\activate.bat C:\ProgramData\miniconda3
call conda activate gprMax
cd /d d:\Codigo\Synth-GPR

echo.
echo [1/4] Generating Dataset...
echo ============================================================
python scripts\main\generate_dataset.py 400MHz_production.ini
if %ERRORLEVEL% NEQ 0 goto :error

echo.
echo [2/4] Running Simulations (GPU)...
echo ============================================================
echo Check GPRMAX GPU usage in another window if needed.
python scripts\main\run_simulations.py 400MHz_production.ini
if %ERRORLEVEL% NEQ 0 goto :error

echo.
echo [3/4] Validating Dataset...
echo ============================================================
python scripts\tools\data_management\validate_dataset.py d:\Codigo\Synth-Data\400MHz_Production
if %ERRORLEVEL% NEQ 0 goto :error

echo.
echo [4/4] Extracting Features...
echo ============================================================
python scripts\main\batch_extract_features.py ^
    --input_dir d:\Codigo\Synth-Data\400MHz_Production ^
    --output_csv d:\Codigo\Synth-Data\400MHz_Production\features_400MHz_10k.csv

echo.
echo ============================================================
echo PRODUCTION RUN COMPLETE!
echo Data saved to: d:\Codigo\Synth-Data\400MHz_Production
echo Features saved to: d:\Codigo\Synth-Data\400MHz_Production\features_400MHz_10k.csv
echo ============================================================
pause
exit /b 0

:error
echo.
echo [ERROR] Pipeline failed!
pause
exit /b 1

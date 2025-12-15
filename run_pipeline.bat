@echo off
setlocal EnableDelayedExpansion

echo ========================================================
echo GPR Data Pipeline - Windows Execution
echo ========================================================

:: Try to activate conda environment
echo Activating gprMax environment...
call conda activate gprMax 2>NUL
if %errorlevel% neq 0 (
    echo [WARN] 'conda' command not found in PATH.
    echo Trying C:\ProgramData\miniconda3\Scripts\activate.bat...
    if exist "C:\ProgramData\miniconda3\Scripts\activate.bat" (
        call "C:\ProgramData\miniconda3\Scripts\activate.bat" gprMax
    ) else (
         echo [ERROR] Could not find activate.bat in C:\ProgramData\miniconda3\Scripts
         echo Assuming python is in PATH...
    )
)

:: Default configuration
set NUM_SAMPLES=2
set OUTPUT_BASE=output\balanced_dataset

:: Set PYTHONPATH to project root (directory of this script)
set PYTHONPATH=%~dp0
echo PYTHONPATH set to: %PYTHONPATH%

:: Allow overriding NUM_SAMPLES via argument
if "%~1" neq "" set NUM_SAMPLES=%~1

echo Configuration:
echo   Samples per class: %NUM_SAMPLES%
echo   Output base:       %OUTPUT_BASE%
echo.

echo [Step 1] Generating .in files...
python scripts\main\generate_balanced_dataset.py --count %NUM_SAMPLES%
if %ERRORLEVEL% neq 0 (
    echo Error generating dataset.
    pause
    exit /b %ERRORLEVEL%
)

:: Find the latest created directory in the output base
set "LATEST_DIR="
if exist "%OUTPUT_BASE%" (
    for /f "delims=" %%I in ('dir "%OUTPUT_BASE%" /b /ad /o-d') do (
        set "LATEST_DIR=%OUTPUT_BASE%\%%I"
        goto :FoundDir
    )
)

:FoundDir
if not defined LATEST_DIR (
    echo Error: Could not find the generated output directory in %OUTPUT_BASE%.
    pause
    exit /b 1
)

echo.
echo [Pipeline] Using run directory: %LATEST_DIR%
pushd "%LATEST_DIR%"

echo.
echo [Step 2] Running Simulations...
if exist run_simulations.bat (
    call run_simulations.bat
) else (
    echo Error: run_simulations.bat not found in %CD%
)

echo.
echo [Step 3] Extracting Features...
if exist extract_features.bat (
    call extract_features.bat
) else (
    echo Error: extract_features.bat not found in %CD%
)

echo.
echo [Step 4] Visualizing Blueprints...
if exist visualize_blueprints.bat (
    call visualize_blueprints.bat
) else (
    echo Error: visualize_blueprints.bat not found in %CD%
)

popd

echo.
echo ========================================================
echo Pipeline Complete!
echo Outputs are in: %LATEST_DIR%
echo ========================================================
pause

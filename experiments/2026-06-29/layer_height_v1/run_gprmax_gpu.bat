@echo off
setlocal enabledelayedexpansion

:: ============================================================
:: Run all layer-height gprMax simulations on GPU
:: Conda env: gprMax  |  Miniconda: C:\Users\barba\miniconda3
:: ============================================================

set CONDA_ROOT=C:\Users\barba\miniconda3
set CONDA_ENV=gprMax
set SIM_DIR=%~dp0
set LOG_FILE=%SIM_DIR%run_log.txt

echo ============================================================ > "%LOG_FILE%"
echo Layer-height dataset - gprMax GPU batch run >> "%LOG_FILE%"
echo Started: %date% %time% >> "%LOG_FILE%"
echo ============================================================ >> "%LOG_FILE%"

:: Activate conda environment
call "%CONDA_ROOT%\Scripts\activate.bat" "%CONDA_ENV%"
if errorlevel 1 (
    echo ERROR: Could not activate conda env "%CONDA_ENV%"
    exit /b 1
)

:: Count total .in files
set TOTAL=0
for %%f in ("%SIM_DIR%sample_*.in") do set /a TOTAL+=1
echo Running %TOTAL% simulations on GPU...
echo Running %TOTAL% simulations on GPU... >> "%LOG_FILE%"

:: Run each simulation
set COUNT=0
for %%f in ("%SIM_DIR%sample_*.in") do (
    set /a COUNT+=1
    echo [!COUNT!/%TOTAL%] %%~nxf
    echo [!COUNT!/%TOTAL%] %%~nxf >> "%LOG_FILE%"
    python -m gprMax "%%f" -gpu >> "%LOG_FILE%" 2>&1
    if errorlevel 1 (
        echo   WARNING: %%~nxf returned error >> "%LOG_FILE%"
    )
)

echo ============================================================ >> "%LOG_FILE%"
echo Finished: %date% %time% >> "%LOG_FILE%"
echo ============================================================ >> "%LOG_FILE%"

echo.
echo Done. %COUNT% simulations completed.
echo Log saved to: %LOG_FILE%
pause

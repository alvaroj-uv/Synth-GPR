@echo off
setlocal

:: ============================================================
:: Geometry-only run — experiment 2026-06-29
:: Generates .vti geometry file without running FDTD
:: Conda env: gprMax  |  Miniconda: C:\Users\barba\miniconda3
:: ============================================================

set CONDA_ROOT=C:\Users\barba\miniconda3
set CONDA_ENV=gprMax
set IN_FILE=%~dp0from_picks_pk20000m.in
set LOG_FILE=%~dp0run_geometry_log.txt

echo ============================================================ > "%LOG_FILE%"
echo EFE picks model - geometry-only run >> "%LOG_FILE%"
echo Started: %date% %time% >> "%LOG_FILE%"
echo File: %IN_FILE% >> "%LOG_FILE%"
echo ============================================================ >> "%LOG_FILE%"

call "%CONDA_ROOT%\Scripts\activate.bat" "%CONDA_ENV%"
if errorlevel 1 (
    echo ERROR: Could not activate conda env "%CONDA_ENV%"
    exit /b 1
)

echo Running geometry-only...
python -m gprMax "%IN_FILE%" --geometry-only >> "%LOG_FILE%" 2>&1

echo ============================================================ >> "%LOG_FILE%"
echo Finished: %date% %time% >> "%LOG_FILE%"
echo ============================================================ >> "%LOG_FILE%"

echo Done. Log: %LOG_FILE%
pause

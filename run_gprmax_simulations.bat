@echo off
setlocal enabledelayedexpansion

REM Activate gprMax conda environment and run simulations
echo Activating gprMax conda environment...
call C:\Users\barba\miniconda3\Scripts\activate.bat gprMax

if errorlevel 1 (
    echo [ERR] Failed to activate gprMax environment
    exit /b 1
)

echo.
echo ======================================================================
echo Running BALLAST simulation (50 ns window)
echo ======================================================================
cd /d d:\Codigo\Synth-GPR
python -m gprMax output_test/ballast_50ns.in
if errorlevel 1 (
    echo [ERR] Ballast simulation failed
) else (
    echo [OK] Ballast simulation completed
)

echo.
echo ======================================================================
echo Running ROCKS simulation (50 ns window)
echo ======================================================================
python -m gprMax output_test/rocks_50ns.in
if errorlevel 1 (
    echo [ERR] Rocks simulation failed
) else (
    echo [OK] Rocks simulation completed
)

echo.
echo ======================================================================
echo Done
echo ======================================================================
pause

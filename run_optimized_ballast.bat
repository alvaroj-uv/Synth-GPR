@echo off
setlocal enabledelayedexpansion

REM Run optimized ballast simulation (eps=5.1)
echo Activating gprMax conda environment...
call C:\Users\barba\miniconda3\Scripts\activate.bat gprMax

if errorlevel 1 (
    echo [ERR] Failed to activate gprMax environment
    exit /b 1
)

echo.
echo ======================================================================
echo Running OPTIMIZED BALLAST simulation (eps=5.1, 50 ns window)
echo ======================================================================
cd /d d:\Codigo\Synth-GPR
python -m gprMax output_test/ballast_eps51_optimized.in
if errorlevel 1 (
    echo [ERR] Optimized ballast simulation failed
) else (
    echo [OK] Optimized ballast simulation completed
)

echo.
echo ======================================================================
echo Done
echo ======================================================================
pause

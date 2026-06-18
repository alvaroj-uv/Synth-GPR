@echo off
REM ============================================================
REM Run gprMax simulation on ballast_eps51_antenna_30cm.in
REM ============================================================

setlocal enabledelayedexpansion

REM Set directory and file paths
cd /d "d:\Codigo\Synth-GPR"

set IN_FILE=output_test\ballast_eps51_antenna_30cm.in
set OUT_FILE=output_test\ballast_eps51_antenna_30cm.out

echo ============================================================
echo gprMax Simulation: 30cm Antenna Height + Clean Ballast
echo ============================================================
echo.
echo Input file:  %IN_FILE%
echo Output file: %OUT_FILE%
echo.

REM Check if input file exists
if not exist "%IN_FILE%" (
    echo ERROR: Input file not found: %IN_FILE%
    exit /b 1
)

echo [START] Running gprMax...
echo.

REM Try to run gprMax
REM Option 1: gprmax command in PATH
gprmax "%IN_FILE%" -o "%OUT_FILE%" 2>nul
if !errorlevel! equ 0 (
    echo [OK] Simulation completed successfully
    echo.
    if exist "%OUT_FILE%" (
        echo Output file created: %OUT_FILE%
        for %%F in ("%OUT_FILE%") do echo File size: %%~zF bytes
    )
    exit /b 0
)

REM Option 2: Python module via miniconda
echo Trying Python module approach...
C:\Users\barba\miniconda3\python.exe -m gprmax "%IN_FILE%" -o "%OUT_FILE%"
if !errorlevel! equ 0 (
    echo [OK] Simulation completed successfully
    echo.
    if exist "%OUT_FILE%" (
        echo Output file created: %OUT_FILE%
        for %%F in ("%OUT_FILE%") do echo File size: %%~zF bytes
    )
    exit /b 0
)

REM If both fail, show error
echo.
echo ERROR: gprMax execution failed
echo.
echo Please ensure gprMax is installed:
echo   - Install via: pip install gprmax
echo   - Or: conda install -c gprmax gprmax
echo.
exit /b 1

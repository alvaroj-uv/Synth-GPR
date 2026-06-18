@echo off
REM Install gprMax from D:\gprMax source and run simulation

cd /d "d:\Codigo\Synth-GPR"

echo.
echo ============================================================
echo Activating gprMax environment
echo ============================================================
echo.

REM Activate conda environment
call C:\Users\barba\miniconda3\Scripts\activate.bat gprMax
if %errorlevel% neq 0 (
    echo ERROR: Could not activate gprMax environment
    exit /b 1
)

echo [OK] gprMax environment activated
echo.

REM Install gprMax in editable mode
echo ============================================================
echo Installing gprMax from source
echo ============================================================
echo.

pip install -e D:\gprMax
if %errorlevel% neq 0 (
    echo ERROR: Could not install gprMax
    exit /b 1
)

echo [OK] gprMax installed
echo.
echo ============================================================
echo Running gprMax simulation
echo ============================================================
echo.

set IN_FILE=start_fresh.in
set OUT_FILE=start_fresh.out

if not exist "%IN_FILE%" (
    echo ERROR: %IN_FILE% not found
    exit /b 1
)

echo Input:  %IN_FILE%
echo Output: %OUT_FILE%
echo.

REM Run gprMax via Python module
python -m gprmax "%IN_FILE%" -o "%OUT_FILE%"

if %errorlevel% equ 0 (
    echo.
    echo ============================================================
    echo [OK] Simulation complete!
    echo ============================================================
    echo Output file: %OUT_FILE%
    if exist "%OUT_FILE%" (
        for %%F in ("%OUT_FILE%") do echo File size: %%~zF bytes
    )
    exit /b 0
) else (
    echo.
    echo ERROR: gprMax simulation failed
    exit /b 1
)

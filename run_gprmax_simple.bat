@echo off
REM Activate gprMax environment and run simulation

cd /d "d:\Codigo\Synth-GPR"

echo.
echo ============================================================
echo Activating gprMax environment
echo ============================================================
echo.

call C:\Users\barba\miniconda3\Scripts\activate.bat gprMax
if %errorlevel% neq 0 (
    echo ERROR: Could not activate gprMax environment
    exit /b 1
)

echo [OK] gprMax environment activated
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

python -m gprMax "%IN_FILE%"

if %errorlevel% equ 0 (
    echo.
    echo ============================================================
    echo [OK] Simulation complete!
    echo ============================================================
    if exist "%OUT_FILE%" (
        for %%F in ("%OUT_FILE%") do echo Output: %OUT_FILE% (%%~zF bytes^)
    )
) else (
    echo ERROR: gprMax simulation failed
)

exit /b %errorlevel%

@echo off
REM Activate gprMax environment and run fouled ballast epsilon sweep

cd /d "d:\Codigo\Synth-GPR"

echo.
echo ============================================================
echo Fouled Ballast Epsilon Sweep (eps 5.5-9.5)
echo ============================================================
echo.

call C:\Users\barba\miniconda3\Scripts\activate.bat gprMax
if %errorlevel% neq 0 (
    echo ERROR: Could not activate gprMax environment
    exit /b 1
)

echo [OK] gprMax environment activated
echo.

setlocal enabledelayedexpansion

set toml_dir=epsilon_sweep_fouled

for %%f in (%toml_dir%\*.toml) do (
    echo ============================================================
    echo Generating .in from %%~nf
    echo ============================================================
    python scripts/pipeline/generate_in_files.py "%%f" -o "%toml_dir%\%%~nf.in"
    if !errorlevel! neq 0 (
        echo ERROR: Could not generate .in for %%~nf
        continue
    )
)

echo.
echo ============================================================
echo Running simulations
echo ============================================================
echo.

for %%f in (%toml_dir%\*.in) do (
    echo.
    echo [RUN] %%~nf
    python -m gprMax "%%f"
    if !errorlevel! equ 0 (
        echo [OK] %%~nf simulation complete
    ) else (
        echo [FAIL] %%~nf simulation failed
    )
)

echo.
echo ============================================================
echo All simulations complete!
echo ============================================================
echo.

exit /b 0

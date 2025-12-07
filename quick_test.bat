@echo off
REM ============================================================
REM Quick Test - Minimal Pipeline
REM Runs a fast test of core functionality
REM ============================================================

echo ============================================================
echo QUICK PIPELINE TEST
echo ============================================================
echo.

call C:\ProgramData\miniconda3\Scripts\activate.bat C:\ProgramData\miniconda3
call conda activate gprMax

cd d:\Codigo\Synth-GPR

echo Cleaning up old test data...
if exist "d:\Codigo\Synth-Data\Tests\QuickTest\s_50000.in" (
    del /q "d:\Codigo\Synth-Data\Tests\QuickTest\s_*.*"
    echo   Removed old test files
)
echo.

echo [1/3] Generating 1 sample...
echo Using config: config_quick_test.ini
python scripts\main\generate_dataset.py config_quick_test.ini

if %ERRORLEVEL% NEQ 0 (
    echo [FAILED] Generation failed!
    exit /b 1
)

echo [2/3] Running simulation...
python -m gprMax d:\Codigo\Synth-Data\Tests\QuickTest\s_50000.in -n 1

if %ERRORLEVEL% NEQ 0 (
    echo [FAILED] Simulation failed!
    exit /b 1
)

echo [3/3] Creating blueprint...
python scripts\tools\visualization\visualize_gprmax_blueprint.py ^
    d:\Codigo\Synth-Data\Tests\QuickTest\s_50000.in ^
    -o d:\Codigo\Synth-Data\Tests\QuickTest\quick_test.png ^
    --no-show

if %ERRORLEVEL% NEQ 0 (
    echo [FAILED] Blueprint failed!
    exit /b 1
)

echo.
echo ============================================================
echo QUICK TEST PASSED!
echo ============================================================
echo Output: d:\Codigo\Synth-Data\Tests\QuickTest\quick_test.png
pause


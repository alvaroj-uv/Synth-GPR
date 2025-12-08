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
set PYTHON_EXE=c:\Users\barba\.conda\envs\gprMax\python.exe

echo Cleaning up old test data...
if exist "d:\Codigo\Synth-Data\Tests\QuickTest\s_50000.in" (
    del /q "d:\Codigo\Synth-Data\Tests\QuickTest\s_*.*"
    echo   Removed old test files
)
echo.

echo [1/3] Generating 1 sample...
echo Using config: config_quick_test.ini
%PYTHON_EXE% scripts\main\generate_dataset.py config_quick_test.ini

if %ERRORLEVEL% NEQ 0 (
    echo [FAILED] Generation failed!
    exit /b 1
)

echo [2/3] Running simulations for all .in files...
for %%f in (d:\Codigo\Synth-Data\Tests\QuickTest\*.in) do (
    echo   Simulating: %%~nxf
    %PYTHON_EXE% -m gprMax "%%f" -n 1
    if %ERRORLEVEL% NEQ 0 (
        echo   [WARN] Simulation failed for %%~nxf
    )
)

if %ERRORLEVEL% NEQ 0 (
    echo [FAILED] Simulation failed!
    exit /b 1
)

echo [3/3] Creating blueprints for all .in files...
for %%f in (d:\Codigo\Synth-Data\Tests\QuickTest\*.in) do (
    echo   Processing: %%~nxf
    %PYTHON_EXE% scripts\tools\visualization\visualize_gprmax_blueprint.py ^
        "%%f" ^
        -o "d:\Codigo\Synth-Data\Tests\QuickTest\%%~nf_blueprint.png" ^
        --no-show
    if %ERRORLEVEL% NEQ 0 (
        echo   [WARN] Blueprint failed for %%~nxf
    )
)

if %ERRORLEVEL% NEQ 0 (
    echo [FAILED] Blueprint generation had errors!
    exit /b 1
)

echo.
echo ============================================================
echo QUICK TEST PASSED!
echo ============================================================
echo Output images: d:\Codigo\Synth-Data\Tests\QuickTest\*_blueprint.png
pause

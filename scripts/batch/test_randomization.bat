@echo off
REM ============================================================
REM Domain Randomization Test Pipeline
REM Tests randomization ON vs OFF
REM ============================================================

echo ============================================================
echo DOMAIN RANDOMIZATION TEST PIPELINE
echo ============================================================
echo.

call C:\ProgramData\miniconda3\Scripts\activate.bat C:\ProgramData\miniconda3
call conda activate gprMax

cd d:\Codigo\Synth-GPR
set PYTHON_EXE=c:\Users\barba\.conda\envs\gprMax\python.exe

echo Running comprehensive domain randomization test...
echo This will:
echo   1. Generate baseline sample (randomization OFF)
echo   2. Generate randomized sample (randomization ON)
echo   3. Run gprMax simulations on both
echo   4. Create blueprints for comparison
echo   5. Compare signals
echo.

%PYTHON_EXE% scripts\tools\tests\compare_domain_randomization.py

if %ERRORLEVEL% NEQ 0 (
    echo [FAILED] Domain randomization test failed!
    exit /b 1
)

echo.
echo ============================================================
echo DOMAIN RANDOMIZATION TEST COMPLETE!
echo ============================================================
echo.
echo Results:
echo   Baseline:    d:\Codigo\Synth-Data\ComparisonTest\baseline_blueprint.png
echo   Randomized:  d:\Codigo\Synth-Data\ComparisonTest\randomized_blueprint.png
echo.
pause

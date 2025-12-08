@echo off
REM ============================================================
REM Test Pipeline Creation
REM Generates a small batch of data to verify the .in generation logic
REM ============================================================

set "PROJECT_ROOT=%~dp0..\.."
set "OUTPUT_DIR=%PROJECT_ROOT%\test_pipeline_output"
set "PYTHON_EXE=c:\Users\barba\.conda\envs\gprMax\python.exe"

echo ============================================================
echo [TEST] Starting Pipeline Generation Test
echo Project Root: %PROJECT_ROOT%
echo Output Dir:   %OUTPUT_DIR%
echo ============================================================

REM 1. Cleanup
if exist "%OUTPUT_DIR%" (
    echo [CLEAN] Removing previous test output...
    rmdir /s /q "%OUTPUT_DIR%"
)

REM 2. Run Generation (using the root script)
echo.
echo [RUN] Generating 2 samples per class...
cd /d "%PROJECT_ROOT%"
%PYTHON_EXE% generate_balanced_dataset.py -n 2 -o "%OUTPUT_DIR%"

if %ERRORLEVEL% NEQ 0 (
    echo [FAIL] Python script execution failed!
    exit /b 1
)

REM 3. Navigate to the generated timestamped folder
REM Since we don't know the exact timestamp, we grab the last created folder
for /f "delims=" %%D in ('dir "%OUTPUT_DIR%" /b /ad /o-n') do (
    set "LATEST_DIR=%OUTPUT_DIR%\%%D"
    goto :FoundDir
)

:FoundDir
echo.
echo [CHECK] Verifying content in: %LATEST_DIR%

set "PASS=1"

if exist "%LATEST_DIR%\metadata.csv" (
    echo   [OK] Found metadata.csv
) else (
    echo   [FAIL] Missing metadata.csv
    set "PASS=0"
)

if exist "%LATEST_DIR%\run_simulations.bat" (
    echo   [OK] Found run_simulations.bat
) else (
    echo   [FAIL] Missing run_simulations.bat
    set "PASS=0"
)

if exist "%LATEST_DIR%\extract_features.bat" (
    echo   [OK] Found extract_features.bat
) else (
    echo   [FAIL] Missing extract_features.bat
    set "PASS=0"
)

if exist "%LATEST_DIR%\visualize_blueprints.bat" (
    echo   [OK] Found visualize_blueprints.bat
) else (
    echo   [FAIL] Missing visualize_blueprints.bat
    set "PASS=0"
)

REM Check for at least one .in file
if exist "%LATEST_DIR%\*.in" (
    echo   [OK] Found .in files
) else (
    echo   [FAIL] No .in files generated
    set "PASS=0"
)

echo.
echo ============================================================
if "%PASS%"=="1" (
    echo [SUCCESS] Pipeline generation test passed!
    exit /b 0
) else (
    echo [FAILED] Some checks failed.
    exit /b 1
)

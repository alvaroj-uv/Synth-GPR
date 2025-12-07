@echo off
REM ============================================================
REM Synth-GPR Testing Pipeline
REM Tests all major scripts in the workflow
REM ============================================================

echo ============================================================
echo SYNTH-GPR TESTING PIPELINE
echo ============================================================
echo.

REM Activate conda environment
call C:\ProgramData\miniconda3\Scripts\activate.bat C:\ProgramData\miniconda3
call conda activate gprMax

REM Change to project directory (for INI file detection)
cd d:\Codigo\Synth-GPR

REM Set test output directory
set TEST_DIR=d:\Codigo\Synth-Data\Tests\PipelineTest
set CONFIG_DIR=d:\Codigo\Synth-GPR

echo Test Directory: %TEST_DIR%
echo Config Directory: %CONFIG_DIR%
echo.

REM ============================================================
REM CLEANUP: Remove old test data to prevent duplicates
REM ============================================================
echo Cleaning up old test data...
if exist "%TEST_DIR%\Generation" (
    rmdir /s /q "%TEST_DIR%\Generation"
    echo   Removed old Generation folder
)
REM Also clean up RandomizationTest to avoid confusion
if exist "d:\Codigo\Synth-Data\Tests\RandomizationTest" (
    rmdir /s /q "d:\Codigo\Synth-Data\Tests\RandomizationTest"
    echo   Removed old RandomizationTest folder
)
REM Remove any lingering PNGs
del /q "%TEST_DIR%\*.png" 2>nul

mkdir "%TEST_DIR%\Generation" 2>nul
echo   Test directory ready
echo.

REM ============================================================
REM TEST 1: Dataset Generation
REM ============================================================
echo [1/4] Testing Dataset Generation...
echo ============================================================
echo Using config: config_pipeline_test.ini

python scripts\main\generate_dataset.py config_pipeline_test.ini

if %ERRORLEVEL% NEQ 0 (
    echo [FAILED] Dataset generation failed!
    exit /b 1
)
echo [OK] Dataset generation successful
echo.

REM ============================================================
REM TEST 2: Batch Simulations
REM ============================================================
echo [2/4] Testing Batch Simulations...
echo ============================================================

python scripts\main\run_simulations.py ^
    %TEST_DIR%\Generation ^
    -j 4

if %ERRORLEVEL% NEQ 0 (
    echo [FAILED] Batch simulations failed!
    exit /b 1
)
echo [OK] Batch simulations successful
echo.

REM (Blueprint Visualization skipped as requested)

REM ============================================================
REM TEST 3: Dataset Validation
REM ============================================================
echo [3/4] Testing Dataset Validation...
echo ============================================================

python scripts\tools\data_management\validate_dataset.py ^
    %TEST_DIR%\Generation

if %ERRORLEVEL% NEQ 0 (
    echo [FAILED] Dataset validation failed!
    exit /b 1
)
echo [OK] Dataset validation successful
echo.

REM ============================================================
REM TEST 4: Feature Extraction (Final Step)
REM ============================================================
echo [4/4] Testing Feature Extraction...
echo ============================================================

python scripts\main\batch_extract_features.py ^
    --input_dir %TEST_DIR%\Generation ^
    --output_csv %TEST_DIR%\features_test.csv

if %ERRORLEVEL% NEQ 0 (
    echo [FAILED] Feature extraction failed!
    exit /b 1
)
echo [OK] Feature extraction successful
echo.

REM ============================================================
REM SUMMARY
REM ============================================================
echo ============================================================
echo ALL TESTS PASSED!
echo ============================================================
echo.
echo Test Results Summary:
echo   [OK] Dataset Generation
echo   [OK] Batch Simulations
echo   [OK] Dataset Validation
echo   [OK] Feature Extraction
echo.
echo Output Directory: %TEST_DIR%
echo.
echo ============================================================
REM pause

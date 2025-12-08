@echo off
REM ============================================================
REM Test Environment Setup and Cleanup
REM Creates organized test folder structure and cleans old tests
REM ============================================================

echo ============================================================
echo TEST ENVIRONMENT SETUP
echo ============================================================
echo.

REM Define test directories
set BASE_TEST_DIR=d:\Codigo\Synth-Data\Tests
set PIPELINE_TEST=%BASE_TEST_DIR%\PipelineTest
set QUICK_TEST=%BASE_TEST_DIR%\QuickTest
set RANDOMIZATION_TEST=%BASE_TEST_DIR%\RandomizationTest
set VALIDATION_TEST=%BASE_TEST_DIR%\ValidationTest

echo Cleaning up old test directories...
echo.

REM Clean up old test directories
if exist "d:\Codigo\Synth-Data\PipelineTest" (
    echo Removing old PipelineTest...
    rmdir /s /q "d:\Codigo\Synth-Data\PipelineTest"
)

if exist "d:\Codigo\Synth-Data\QuickTest" (
    echo Removing old QuickTest...
    rmdir /s /q "d:\Codigo\Synth-Data\QuickTest"
)

if exist "d:\Codigo\Synth-Data\ComparisonTest" (
    echo Removing old ComparisonTest...
    rmdir /s /q "d:\Codigo\Synth-Data\ComparisonTest"
)

if exist "d:\Codigo\Synth-Data\DomainRandTest" (
    echo Removing old DomainRandTest...
    rmdir /s /q "d:\Codigo\Synth-Data\DomainRandTest"
)

if exist "d:\Codigo\Synth-Data\VoidFillingTest" (
    echo Removing old VoidFillingTest...
    rmdir /s /q "d:\Codigo\Synth-Data\VoidFillingTest"
)

if exist "d:\Codigo\Synth-Data\LayeredTest" (
    echo Removing old LayeredTest...
    rmdir /s /q "d:\Codigo\Synth-Data\LayeredTest"
)

echo.
echo Creating new organized test structure...
echo.

REM Create new test directory structure
mkdir "%BASE_TEST_DIR%" 2>nul
mkdir "%PIPELINE_TEST%" 2>nul
mkdir "%QUICK_TEST%" 2>nul
mkdir "%RANDOMIZATION_TEST%" 2>nul
mkdir "%RANDOMIZATION_TEST%\Baseline" 2>nul
mkdir "%RANDOMIZATION_TEST%\Randomized" 2>nul
mkdir "%VALIDATION_TEST%" 2>nul

echo Test directory structure created:
echo   %BASE_TEST_DIR%
echo   ├── PipelineTest\
echo   ├── QuickTest\
echo   ├── RandomizationTest\
echo   │   ├── Baseline\
echo   │   └── Randomized\
echo   └── ValidationTest\
echo.

REM Create README files for each test directory
echo Creating README files...

REM Pipeline Test README
echo # Pipeline Test Directory > "%PIPELINE_TEST%\README.txt"
echo. >> "%PIPELINE_TEST%\README.txt"
echo This directory contains outputs from the full pipeline test. >> "%PIPELINE_TEST%\README.txt"
echo. >> "%PIPELINE_TEST%\README.txt"
echo Contents: >> "%PIPELINE_TEST%\README.txt"
echo - Generated .in files >> "%PIPELINE_TEST%\README.txt"
echo - Simulation .out files >> "%PIPELINE_TEST%\README.txt"
echo - Blueprint images >> "%PIPELINE_TEST%\README.txt"
echo - Feature extraction CSV >> "%PIPELINE_TEST%\README.txt"
echo. >> "%PIPELINE_TEST%\README.txt"
echo Run: test_pipeline.bat >> "%PIPELINE_TEST%\README.txt"

REM Quick Test README
echo # Quick Test Directory > "%QUICK_TEST%\README.txt"
echo. >> "%QUICK_TEST%\README.txt"
echo This directory contains outputs from quick validation tests. >> "%QUICK_TEST%\README.txt"
echo. >> "%QUICK_TEST%\README.txt"
echo Contents: >> "%QUICK_TEST%\README.txt"
echo - Single test sample >> "%QUICK_TEST%\README.txt"
echo - Quick validation blueprint >> "%QUICK_TEST%\README.txt"
echo. >> "%QUICK_TEST%\README.txt"
echo Run: quick_test.bat >> "%QUICK_TEST%\README.txt"

REM Randomization Test README
echo # Domain Randomization Test Directory > "%RANDOMIZATION_TEST%\README.txt"
echo. >> "%RANDOMIZATION_TEST%\README.txt"
echo This directory contains domain randomization comparison tests. >> "%RANDOMIZATION_TEST%\README.txt"
echo. >> "%RANDOMIZATION_TEST%\README.txt"
echo Contents: >> "%RANDOMIZATION_TEST%\README.txt"
echo - Baseline\ : Samples with randomization OFF >> "%RANDOMIZATION_TEST%\README.txt"
echo - Randomized\ : Samples with randomization ON >> "%RANDOMIZATION_TEST%\README.txt"
echo - Comparison blueprints >> "%RANDOMIZATION_TEST%\README.txt"
echo - Signal analysis >> "%RANDOMIZATION_TEST%\README.txt"
echo. >> "%RANDOMIZATION_TEST%\README.txt"
echo Run: test_randomization.bat >> "%RANDOMIZATION_TEST%\README.txt"

REM Validation Test README
echo # Validation Test Directory > "%VALIDATION_TEST%\README.txt"
echo. >> "%VALIDATION_TEST%\README.txt"
echo This directory is for dataset validation and quality checks. >> "%VALIDATION_TEST%\README.txt"
echo. >> "%VALIDATION_TEST%\README.txt"
echo Contents: >> "%VALIDATION_TEST%\README.txt"
echo - Validation reports >> "%VALIDATION_TEST%\README.txt"
echo - Quality check results >> "%VALIDATION_TEST%\README.txt"

echo.
echo ============================================================
echo TEST ENVIRONMENT READY!
echo ============================================================
echo.
echo Base directory: %BASE_TEST_DIR%
echo.
echo Available test scripts:
echo   test_pipeline.bat      - Full pipeline test
echo   quick_test.bat         - Quick validation
echo   test_randomization.bat - Domain randomization test
echo.
echo ============================================================
pause

@echo off
REM ============================================================
REM Validation Check Script
REM Validates test outputs and checks for completeness
REM ============================================================

echo ============================================================
echo TEST VALIDATION CHECK
echo ============================================================
echo.

set BASE_TEST_DIR=d:\Codigo\Synth-Data\Tests
set PASS_COUNT=0
set FAIL_COUNT=0

echo Checking test outputs...
echo.

REM ============================================================
REM Check Pipeline Test
REM ============================================================
echo [1] Pipeline Test Validation
echo ------------------------------------------------------------

if exist "%BASE_TEST_DIR%\PipelineTest\s_40000.in" (
    echo   [OK] Input file generated
    set /a PASS_COUNT+=1
) else (
    echo   [FAIL] Input file missing
    set /a FAIL_COUNT+=1
)

if exist "%BASE_TEST_DIR%\PipelineTest\s_40000.out" (
    echo   [OK] Simulation output exists
    set /a PASS_COUNT+=1
) else (
    echo   [FAIL] Simulation output missing
    set /a FAIL_COUNT+=1
)

if exist "%BASE_TEST_DIR%\PipelineTest\test_blueprint.png" (
    echo   [OK] Blueprint generated
    set /a PASS_COUNT+=1
) else (
    echo   [FAIL] Blueprint missing
    set /a FAIL_COUNT+=1
)

if exist "%BASE_TEST_DIR%\PipelineTest\features_test.csv" (
    echo   [OK] Features extracted
    set /a PASS_COUNT+=1
) else (
    echo   [FAIL] Features CSV missing
    set /a FAIL_COUNT+=1
)

echo.

REM ============================================================
REM Check Quick Test
REM ============================================================
echo [2] Quick Test Validation
echo ------------------------------------------------------------

if exist "%BASE_TEST_DIR%\QuickTest\s_50000.in" (
    echo   [OK] Quick test input generated
    set /a PASS_COUNT+=1
) else (
    echo   [FAIL] Quick test input missing
    set /a FAIL_COUNT+=1
)

if exist "%BASE_TEST_DIR%\QuickTest\quick_test.png" (
    echo   [OK] Quick test blueprint generated
    set /a PASS_COUNT+=1
) else (
    echo   [FAIL] Quick test blueprint missing
    set /a FAIL_COUNT+=1
)

echo.

REM ============================================================
REM Check Randomization Test
REM ============================================================
echo [3] Randomization Test Validation
echo ------------------------------------------------------------

if exist "%BASE_TEST_DIR%\RandomizationTest\Baseline\s_30000.in" (
    echo   [OK] Baseline sample generated
    set /a PASS_COUNT+=1
) else (
    echo   [FAIL] Baseline sample missing
    set /a FAIL_COUNT+=1
)

if exist "%BASE_TEST_DIR%\RandomizationTest\Randomized\s_30000.in" (
    echo   [OK] Randomized sample generated
    set /a PASS_COUNT+=1
) else (
    echo   [FAIL] Randomized sample missing
    set /a FAIL_COUNT+=1
)

if exist "%BASE_TEST_DIR%\RandomizationTest\baseline_blueprint.png" (
    echo   [OK] Baseline blueprint exists
    set /a PASS_COUNT+=1
) else (
    echo   [FAIL] Baseline blueprint missing
    set /a FAIL_COUNT+=1
)

if exist "%BASE_TEST_DIR%\RandomizationTest\randomized_blueprint.png" (
    echo   [OK] Randomized blueprint exists
    set /a PASS_COUNT+=1
) else (
    echo   [FAIL] Randomized blueprint missing
    set /a FAIL_COUNT+=1
)

if exist "%BASE_TEST_DIR%\RandomizationTest\signal_comparison.png" (
    echo   [OK] Signal comparison generated
    set /a PASS_COUNT+=1
) else (
    echo   [FAIL] Signal comparison missing
    set /a FAIL_COUNT+=1
)

echo.

REM ============================================================
REM Summary
REM ============================================================
echo ============================================================
echo VALIDATION SUMMARY
echo ============================================================
echo.
echo Passed: %PASS_COUNT%
echo Failed: %FAIL_COUNT%
echo.

if %FAIL_COUNT% EQU 0 (
    echo [SUCCESS] All validation checks passed!
    echo.
    exit /b 0
) else (
    echo [WARNING] Some validation checks failed.
    echo Please review the output above.
    echo.
    exit /b 1
)

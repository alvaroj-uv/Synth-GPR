@echo off
REM ============================================================
REM Clean All Test Data
REM Removes all test outputs to ensure fresh runs
REM ============================================================

echo ============================================================
echo CLEANING ALL TEST DATA
echo ============================================================
echo.

set BASE_TEST_DIR=d:\Codigo\Synth-Data\Tests

echo Removing test outputs...

if exist "%BASE_TEST_DIR%\PipelineTest\Generation" (
    rmdir /s /q "%BASE_TEST_DIR%\PipelineTest\Generation"
    echo   [OK] Cleaned PipelineTest/Generation
)

if exist "%BASE_TEST_DIR%\PipelineTest\*.csv" (
    del /q "%BASE_TEST_DIR%\PipelineTest\*.csv"
    echo   [OK] Cleaned PipelineTest CSV files
)

if exist "%BASE_TEST_DIR%\PipelineTest\*.png" (
    del /q "%BASE_TEST_DIR%\PipelineTest\*.png"
    echo   [OK] Cleaned PipelineTest images
)

if exist "%BASE_TEST_DIR%\QuickTest\s_*.*" (
    del /q "%BASE_TEST_DIR%\QuickTest\s_*.*"
    echo   [OK] Cleaned QuickTest files
)

if exist "%BASE_TEST_DIR%\QuickTest\*.png" (
    del /q "%BASE_TEST_DIR%\QuickTest\*.png"
    echo   [OK] Cleaned QuickTest images
)

if exist "%BASE_TEST_DIR%\RandomizationTest\Baseline" (
    rmdir /s /q "%BASE_TEST_DIR%\RandomizationTest\Baseline"
    echo   [OK] Cleaned RandomizationTest/Baseline
)

if exist "%BASE_TEST_DIR%\RandomizationTest\Randomized" (
    rmdir /s /q "%BASE_TEST_DIR%\RandomizationTest\Randomized"
    echo   [OK] Cleaned RandomizationTest/Randomized
)

if exist "%BASE_TEST_DIR%\RandomizationTest\*.png" (
    del /q "%BASE_TEST_DIR%\RandomizationTest\*.png"
    echo   [OK] Cleaned RandomizationTest images
)

echo.
echo ============================================================
echo CLEANUP COMPLETE!
echo ============================================================
echo.
echo All test data has been removed.
echo Run your test scripts to generate fresh data.
echo.
pause

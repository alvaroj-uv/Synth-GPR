@echo off
REM ============================================================================
REM Synth-GPR: Generate 10,000 .in files and run gprMax simulations
REM ============================================================================
REM 
REM This script:
REM 1. Generates 10,000 .in files (2,000 samples per FI class)
REM 2. Runs gprMax simulations on all .in files in parallel
REM 3. Outputs .out files in the same directory
REM
REM Usage: double-click or run from command line
REM        generate_10k_dataset.bat
REM
REM Requirements:
REM - Anaconda/Miniconda with gprMax environment
REM - Synth-GPR code in current directory
REM ============================================================================

echo.
echo ============================================================================
echo  Synth-GPR Full Dataset Generation (10,000 samples)
echo ============================================================================
echo.

REM Configuration
set OUTPUT_DIR=D:\Codigo\Synth-Data\dataset_10k
set CONDA_ENV=gprMax
set START_ID=0
set SAMPLES_PER_CLASS=2000

REM ============================================================================
REM STEP 1: Generate .in Files
REM ============================================================================

echo [STEP 1/2] Generating 10,000 .in files...
echo Output Directory: %OUTPUT_DIR%
echo Samples per class: %SAMPLES_PER_CLASS% x 5 classes = 10,000 total
echo.

REM Activate conda environment
call conda activate %CONDA_ENV%
if errorlevel 1 (
    echo ERROR: Failed to activate conda environment '%CONDA_ENV%'
    echo Please check that the environment exists: conda env list
    pause
    exit /b 1
)

REM Generate dataset
python scripts\main\generate_dataset.py %OUTPUT_DIR% ^
    --labels C MC MF F HF ^
    -n %SAMPLES_PER_CLASS% ^
    --start_id %START_ID% ^
    --moisture_max 0.15

if errorlevel 1 (
    echo ERROR: Dataset generation failed!
    pause
    exit /b 1
)

echo.
echo ✓ .in files generated successfully
echo.

REM ============================================================================
REM STEP 2: Run gprMax Simulations
REM ============================================================================

echo [STEP 2/2] Running gprMax simulations...
echo This may take several hours for 10,000 files.
echo.

REM Save original directory
set ORIGINAL_DIR=%CD%

REM Change to output directory
cd /d %OUTPUT_DIR%

REM Count .in files
set FILE_COUNT=0
for %%f in (*.in) do set /a FILE_COUNT+=1
echo Found %FILE_COUNT% .in files to simulate
echo.

REM Ask user for GPU acceleration
set /p USE_GPU="Use GPU acceleration? (y/n): "
set GPU_FLAG=
if /i "%USE_GPU%"=="y" set GPU_FLAG=--gpu

REM Ask user for number of parallel processes
set /p NUM_PROCESSES="Number of parallel processes (1-8, recommended 4): "
if "%NUM_PROCESSES%"=="" set NUM_PROCESSES=4

echo.
echo Starting simulations with %NUM_PROCESSES% parallel processes %GPU_FLAG%...
echo Press Ctrl+C to abort if needed.
echo.
timeout /t 3

REM Run gprMax on all .in files in parallel
set COUNTER=0
for %%f in (*.in) do (
    set /a COUNTER+=1
    echo [!COUNTER!/%FILE_COUNT%] Queuing %%f...
    
    REM Run in background with parallel flag
    start /min python -m gprMax "%%f" -n %NUM_PROCESSES% %GPU_FLAG%
    
    REM Small delay to avoid overwhelming system startup
    if !COUNTER! LEQ 10 timeout /t 2 /nobreak >nul
)

echo.
echo ✓ All simulations queued
echo Monitor progress: Check .out files appearing in %OUTPUT_DIR%
echo.

REM Wait for simulations to complete
echo Waiting for all gprMax processes to finish...
echo (This may take hours - check Task Manager for progress)
echo.

:wait_loop
tasklist | find /i "python.exe" >nul
if errorlevel 1 goto simulations_done
REM Show progress
for /f %%A in ('dir /b *.out 2^>nul ^| find /c /v ""') do set CURRENT_OUT=%%A
echo Progress: !CURRENT_OUT! / %FILE_COUNT% .out files completed
timeout /t 30 /nobreak >nul
goto wait_loop

:simulations_done
echo.
echo ✓ All simulations completed
echo.

REM ============================================================================
REM Verification
REM ============================================================================

echo Verifying output files...
set OUT_COUNT=0
for %%f in (*.out) do set /a OUT_COUNT+=1
echo Generated .out files: %OUT_COUNT% / %FILE_COUNT%
echo.

if %OUT_COUNT% LSS %FILE_COUNT% (
    set /a MISSING=%FILE_COUNT%-%OUT_COUNT%
    echo WARNING: %MISSING% simulations may have failed.
    echo Check for .in files without corresponding .out files.
    echo.
    echo Creating missing_files.txt with list of missing .out files...
    
    for %%f in (*.in) do (
        set BASENAME=%%~nf
        if not exist "!BASENAME!.out" echo %%f >> missing_files.txt
    )
    
    if exist missing_files.txt (
        echo ✓ See missing_files.txt for list of failed simulations
    )
)

REM Return to original directory
cd /d %ORIGINAL_DIR%

REM ============================================================================
REM Summary
REM ============================================================================

echo.
echo ============================================================================
echo  Dataset Generation Complete
echo ============================================================================
echo.
echo Output Directory: %OUTPUT_DIR%
echo .in files:  %FILE_COUNT%
echo .out files: %OUT_COUNT%
echo.
echo Next steps:
echo   1. Verify all .out files generated successfully
echo   2. Extract features:
echo      python scripts\main\extract_features.py %OUTPUT_DIR%
echo   3. Result: %OUTPUT_DIR%\feature_dataset.csv
echo.
echo ============================================================================

pause

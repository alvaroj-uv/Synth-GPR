@echo off
echo ==========================================
echo Synth-GPR Pipeline Verification
echo ==========================================

REM Try to activate conda environment
echo Activating gprMax environment...
call conda activate gprMax 2>NUL
if %errorlevel% neq 0 (
    echo [WARN] Could not run 'conda activate gprMax'.
    echo Assuming python is already in PATH with correct dependencies.
)

set OUT_DIR=d:\Codigo\Synth-Data\TestRunV2
if not exist "%OUT_DIR%" mkdir "%OUT_DIR%"

echo.
echo [1/3] Generating Data...
python scripts/main/generate_dataset.py "%OUT_DIR%" --labels CL -n 1 --start_id 5000
if %errorlevel% neq 0 goto :error

echo.
echo [2/3] Simulating...
python -m gprMax "%OUT_DIR%\s_5000.in" -n 1
if %errorlevel% neq 0 goto :error

echo.
echo [3/3] Generating Blueprint...
python scripts/tools/visualization/visualize_gprmax_blueprint.py "%OUT_DIR%\s_5000.in" -o "%OUT_DIR%\blueprint_s5000.png" --no-show
if %errorlevel% neq 0 goto :error

echo.
echo [SUCCESS] Pipeline complete.
echo Please check the blueprint at: %OUT_DIR%\blueprint_s5000.png
goto :end

:error
echo.
echo [ERROR] Pipeline failed. See output above.
pause
exit /b 1

:end
pause

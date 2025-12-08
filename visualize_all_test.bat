@echo off
REM Visualize all .in files in test directory

setlocal enabledelayedexpansion

set TEST_DIR=d:\Codigo\Synth-Data\Tests\PipelineTest\Generation

echo Visualizing all .in files in %TEST_DIR%
echo.

call conda activate gprMax

set COUNT=0
for %%f in ("%TEST_DIR%\*.in") do (
    set /a COUNT+=1
    echo [!COUNT!] Visualizing %%~nxf...
    python scripts\tools\visualization\visualize_gprmax_blueprint.py "%%f" -o "%%~dpnf.png" --no-show
    
    if errorlevel 1 (
        echo   ERROR: Failed to visualize %%~nxf
    ) else (
        echo   ✓ Created %%~nf.png (Combined Blueprint + Signal if .out exists)
    )
    echo.
)

echo.
echo Visualization complete! Created !COUNT! blueprints.
echo Output: %TEST_DIR%\*.png
pause

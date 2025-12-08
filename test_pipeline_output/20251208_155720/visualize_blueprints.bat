@echo off
set PYTHON_EXE="c:\Users\barba\.conda\envs\gprMax\python.exe"
set SCRIPT="D:\Codigo\Synth-GPR\scripts\tools\visualization\visualize_gprmax_blueprint.py"
echo [BATCH] Visualizing Blueprints...
for %%f in (*.in) do (
    echo   Processing: %%~nxf
    %PYTHON_EXE% %SCRIPT% "%%f" -o "%%~nf_blueprint.png" --no-show
)
echo [BATCH] Visualization Complete.

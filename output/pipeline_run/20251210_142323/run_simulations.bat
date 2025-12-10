@echo off
set PYTHON_EXE="/opt/miniconda3/envs/gprMax/bin/python"
echo [BATCH] Running Simulations...
for %%f in (*.in) do (
    if not exist "%%~nf.out" (
        echo Running %%f
        %PYTHON_EXE% -m gprMax %%f -n 1
    ) else (
        echo Skipping %%f (Already exists)
    )
)
echo [BATCH] Simulations Complete.
